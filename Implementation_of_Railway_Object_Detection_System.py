import cv2
import os
import base64
import threading
import mysql.connector
import numpy as np
from ultralytics.solutions.solutions import BaseSolution
from ultralytics.utils.plotting import Annotator, colors
from datetime import datetime
from shapely.geometry import LineString

# Suppress TqdmWarning
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="tqdm")

# Attempt Gemini AI imports
try:
    from langchain_core.messages import HumanMessage
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Gemini AI dependencies not found. Running without AI descriptions.")

# Configuration
GOOGLE_API_KEY = "........................"  # Updated with your new key
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": ".....................",
    "database": "railway_data"
}

VIDEO_PATH = r"C:\Users\win10\OneDrive\Desktop\py_1\karad_video.mp4"
MODEL_PATH = r"C:\Users\win10\OneDrive\Desktop\py_1\yolo12s.pt"
REGION_POINTS = [(0, 200), (640, 200)]
FRAME_SIZE = (640, 360)

# Database Initialization
def initialize_database():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS railway_data")
        cursor.close()
        conn.close()

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS railway_objects (
            id INT AUTO_INCREMENT PRIMARY KEY,
            track_id INT,
            object_type VARCHAR(255),
            date_time DATETIME,
            description VARCHAR(255),
            location_x INT,
            location_y INT
        )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database and table are ready!")
    except Exception as e:
        print(f"❌ Database Initialization Error: {e}")

# Database Insertion
def insert_into_database(track_id, object_type, timestamp, description, x, y):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = """
        INSERT INTO railway_objects (track_id, object_type, date_time, description, location_x, location_y)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (track_id, object_type, timestamp, description, x, y)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Data inserted for Track ID: {track_id} - {object_type}")
    except Exception as e:
        print(f"❌ Database Insert Error: {e}")

# Railway Object Detector Class
class RailwayObjectDetector(BaseSolution):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initialize_region()
        self.trkd_ids = []
        self.trk_pos = {}
        self.saved_ids = set()
        if GEMINI_AVAILABLE:
            try:
                self.gemini_model = ChatGoogleGenerativeAI(model="gemini-pro-vision")
                print("✅ Gemini AI initialized.")
            except Exception as e:
                print(f"❌ Failed to initialize Gemini AI: {e}. Proceeding without AI.")
                self.gemini_model = None
        else:
            self.gemini_model = None
        os.makedirs("railway_crops", exist_ok=True)

    def analyze_and_save_response(self, image_path, track_id, object_type, timestamp, x, y):
        if not GEMINI_AVAILABLE or not self.gemini_model:
            description = "AI analysis disabled"
            insert_into_database(track_id, object_type, timestamp, description, x, y)
            return
        try:
            with open(image_path, "rb") as img_file:
                base64_image = base64.b64encode(img_file.read()).decode("utf-8")
            message = HumanMessage(
                content=[
                    {"type": "text", "text": "Provide a brief description of the railway object in the image."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}, "description": "Detected railway object"}
                ]
            )
            response = self.gemini_model.invoke([message])
            description = response.content.strip() if response.content else "No description available"
            insert_into_database(track_id, object_type, timestamp, description, x, y)
        except Exception as e:
            print(f"❌ Error invoking Gemini AI: {e}")
            description = "Error in AI analysis"
            insert_into_database(track_id, object_type, timestamp, description, x, y)

    def detect_objects(self, im0):
        try:
            self.annotator = Annotator(im0, line_width=self.line_width)
            self.extract_tracks(im0)
            self.annotator.draw_region(reg_pts=self.region, color=(0, 255, 0), thickness=self.line_width * 2)
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            for box, track_id, cls in zip(self.boxes, self.track_ids, self.clss):
                object_type = self.model.names[int(cls)]
                x1, y1, x2, y2 = map(int, box)
                center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                self.trk_pos[track_id] = (center_x, center_y)

                if LineString([(x1, y1), (x2, y2)]).intersects(LineString(self.region)) and track_id not in self.trkd_ids:
                    self.trkd_ids.append(track_id)

                label = f"ID: {track_id} | {object_type}"
                self.annotator.box_label(box, label=label, color=colors(track_id, True))

                if track_id not in self.saved_ids:
                    cropped_image = im0[y1:y2, x1:x2]
                    if cropped_image.size != 0:
                        image_filename = f"railway_crops/{track_id}_{object_type}.jpg"
                        cv2.imwrite(image_filename, cropped_image)
                        print(f"📷 Saved image: {image_filename}")
                        threading.Thread(
                            target=self.analyze_and_save_response,
                            args=(image_filename, track_id, object_type, current_time, center_x, center_y),
                            daemon=True
                        ).start()
                        self.saved_ids.add(track_id)

            self.display_output(im0)
            return im0
        except Exception as e:
            print(f"❌ Error in detect_objects: {e}")
            return im0

# Mouse Callback
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        print(f"Mouse Position: x={x}, y={y}")

# Main Function
def main():
    print("Starting railway object detection...")
    initialize_database()

    if not os.path.exists(VIDEO_PATH):
        print(f"❌ Video file '{VIDEO_PATH}' not found!")
        return

    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model file '{MODEL_PATH}' not found! Please provide a trained YOLO model.")
        return

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"❌ Failed to open video file '{VIDEO_PATH}'!")
        return

    try:
        detector = RailwayObjectDetector(region=REGION_POINTS, model=MODEL_PATH, line_width=2)
    except Exception as e:
        print(f"❌ Failed to initialize detector: {e}")
        cap.release()
        return

    cv2.namedWindow("Railway Object Detection")
    cv2.setMouseCallback("Railway Object Detection", mouse_callback)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ End of video or error reading frame.")
            break

        frame = cv2.resize(frame, FRAME_SIZE)
        result = detector.detect_objects(frame)
        cv2.imshow("Railway Object Detection", result)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("✅ User terminated the program.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
