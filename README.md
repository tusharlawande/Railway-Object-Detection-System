# Railway Object Detection System

## Project Overview

This project is a Python-based solution designed to detect and classify railway track objects from video footage, developed as a task submission for the **Python Developer (Machine Learning, Image Processing, & Data Analysis)** role at **Mounarch Tech Solutions & Systems Pvt Ltd (MTSS)**. It processes the provided video (`karad_video.mp4`) to identify 17 railway objects listed in the task PDFs, leveraging machine learning, image processing, and data analysis techniques. The system integrates a YOLO model for object detection, OpenCV for image processing, MySQL for data storage, and Google’s Gemini AI for generating object descriptions, fulfilling the job’s key responsibilities and requirements.

### Task Context
- **Company**: Mounarch Tech Solutions & Systems Pvt Ltd
- **Role**: Python Developer (Machine Learning, Image Processing, & Data Analysis)
- **Task Links**:
  - [PDF Folder 1](https://drive.google.com/drive/folders/1z3lTWMP3EvKBsqWSVcNAzFH2ZlCevPOI?usp=sharing)
  - [PDF Folder 2](https://drive.google.com/drive/folders/1-9QA07fm6CLS_GgYKBt6Lfb2k7U-qoB1?usp=sharing)
  - [Video File](https://drive.google.com/file/d/1gEK9cOedEcpd67TfqvSArPsCrsFncN-k/view?usp=sharing)

---

## Features

- **Object Detection**: Identifies railway objects (e.g., OHE-Pole, K.M. Stone) using the YOLOv8 model, displaying bounding boxes and labels in real-time.
- **Image Processing**: Resizes video frames, crops detected objects, and annotates them with OpenCV, enabling feature extraction and pattern recognition.
- **AI-Driven Descriptions**: Utilizes Google’s Gemini AI (`gemini-pro-vision`) to generate textual descriptions of detected objects from cropped images.
- **Data Storage**: Logs detection details (track ID, object type, timestamp, description, coordinates) into a MySQL database for analysis.
- **Real-Time Visualization**: Displays the processed video feed with annotated detections in an OpenCV window, supporting interactive monitoring.

---

## Alignment with Job Requirements

### Key Responsibilities
- **Build and Train Machine Learning Models**: Implements the YOLOv8 model for predictive object detection, with detailed training instructions for railway-specific objects, supporting automation and analytics.
- **Design and Implement Image Processing Algorithms**: Uses OpenCV to resize frames, crop objects, and annotate detections, achieving feature extraction and pattern recognition.
- **Perform Data Analysis**: Stores detection data in MySQL for insights and decision-making, with potential for exploratory data analysis (EDA) on object positions and types.
- **Work with Libraries**: Leverages OpenCV, NumPy, Ultralytics (YOLO), and MySQL; training supports TensorFlow/PyTorch integration.
- **Collaborate with Teams**: Modular design allows seamless integration into larger applications or systems.

### Requirements
- **Proficiency in Python and Libraries**: Entirely Python-based, utilizing OpenCV, NumPy, and Ultralytics for ML and image processing tasks.
- **Experience with Tools**: Employs Pandas-compatible NumPy, OpenCV, and Matplotlib-like visualization (via OpenCV windows). Training leverages TensorFlow/PyTorch.
- **Knowledge of Deep Learning Frameworks**: YOLOv8 integration demonstrates deep learning expertise.
- **Familiarity with Data Visualization and EDA**: Real-time visualization via OpenCV; MySQL storage enables EDA.
- **Understanding of Computer Vision**: Applies vision concepts (bounding boxes, region of interest) for object detection and annotation.

---

## System Architecture

- **Input**: Video file (`karad_video.mp4`) containing railway track footage.
- **Processing Pipeline**:
  1. **Frame Extraction**: Captures frames from video using OpenCV.
  2. **Object Detection**: YOLOv8 (`yolo12s.pt`) detects objects, assigning track IDs and labels.
  3. **Image Processing**: Resizes frames, crops detected objects, and annotates with OpenCV.
  4. **AI Analysis**: Gemini AI generates descriptions from cropped images (if API key is valid).
  5. **Data Storage**: Saves detection details to MySQL database.
- **Output**: Annotated video feed, cropped images, and database entries.

---

## Prerequisites

### Software
- **Python 3.13**: Download from [python.org](https://www.python.org/downloads/).
- **MySQL 8.0**: Community Server for database storage.
- **VSCode**: Recommended IDE for execution.

### Python Dependencies
Install via pip:
```bash
pip install opencv-python mysql-connector-python numpy ultralytics shapely langchain-google-genai



