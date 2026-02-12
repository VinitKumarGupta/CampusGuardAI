# CampusGuard AI: Automated Traffic Monitoring and Enforcement System

## 1. Abstract

CampusGuard AI is a computer vision-based framework designed to automate traffic management within restricted campus environments. Leveraging existing CCTV infrastructure, the system performs real-time vehicle tracking, speed estimation, and violation detection (specifically speeding and passenger limit violations). The architecture couples a high-performance computer vision engine with a Django-based administrative dashboard, facilitating data logging, automated SMS alerts via Twilio, and a driver behavior gamification system.

## 2. Introduction

Traffic enforcement on large university campuses often relies on manual monitoring, which is resource-intensive and prone to human error. CampusGuard AI addresses this by providing a non-intrusive, automated monitoring solution. The system is engineered to handle non-standard camera angles (side-view perspective) using geometric calibration, enabling accurate speed estimation without the need for specialized hardware like radar guns or inductive loops.

## 3. System Architecture

The software is divided into two decoupled subsystems: the **Computer Vision Engine (`cv_engine`)** for real-time inference and the **Backend Dashboard (`backend_dashboard`)** for data visualization and management.

### 3.1 Computer Vision Engine

The core processing pipeline utilizes **YOLOv8** for object detection and **ByteTrack** for persistent object tracking.

* **Speed Estimation:** Utilizes a dual-line intersection algorithm based on vector cross-products to calculate velocity across a calibrated zone.
* **Violation Logic:**
* **Speeding:** Compares calculated velocity against a defined threshold (e.g., 30 km/h).
* **Triple Riding:** Implements spatial containment logic to count passengers on two-wheelers.


* **ANPR (Automatic Number Plate Recognition):** Integration of a custom YOLOv8 model for license plate detection followed by **EasyOCR** for text extraction.

### 3.2 Administrative Dashboard

A Django-based web application that serves as the interface for security personnel.

* **Violation Review:** Displays captured snapshots of infractions.
* **Gamification Module:** Calculates "Risk Scores" and "Safe Miles Credits" to incentivize compliant driving behavior.
* **Alert System:** Integrated Twilio API for sending real-time SMS notifications to registered vehicle owners.

## 4. Methodology

### 4.1 Speed Estimation Algorithm

Unlike overhead cameras that use simple vertical displacement, this system accommodates diagonal road geometries.

* **Calibration:** Two reference lines ( and ) are defined in the image plane.
* **Logic:** The system computes the cross-product of the vehicle's centroid vector relative to the reference lines. A sign change in the cross-product indicates a crossing event.
* **Velocity ():** Calculated as , where  is the real-world distance (calibrated to 4.9 meters) and  is the frame delta derived from the video framerate (30 FPS).

### 4.2 Passenger Counting (Triple Riding Detection)

To identify "triple riding" on two-wheelers, the system employs a bounding-box containment strategy:

1. Detect all instances of class `Person` and class `Motorcycle`.
2. Calculate the centroid of each `Person`.
3. Determine if the centroid lies strictly within the bounding box of a `Motorcycle`.
4. If the count of associated persons exceeds the legal limit (2), a violation is flagged.

### 4.3 Optical Character Recognition (OCR)

The `PlateReader` module executes a two-stage inference:

1. **Detection:** A custom trained YOLOv8 model (`best.pt`) localizes the license plate.
2. **Recognition:** The region of interest (ROI) is cropped, upscaled, and processed by EasyOCR to extract the alphanumeric string, filtered against standard Indian license plate patterns (Regex).

## 5. Implementation Details

### Technology Stack

* **Language:** Python 3.x
* **Computer Vision:** OpenCV, Ultralytics YOLOv8, EasyOCR, NumPy
* **Web Framework:** Django 5.2
* **Database:** SQLite (Development), adaptable to PostgreSQL
* **Notifications:** Twilio REST API

### Key Modules

* `cv_engine/modules/speed_estimator.py`: Implements the mathematical logic for vector-based line crossing.
* `cv_engine/modules/plate_reader.py`: Handles the OCR pipeline and regex validation.
* `backend_dashboard/dashboard/utils.py`: Contains the logic for the "Safe Miles" gamification program and risk scoring.

## 6. Installation and Usage

### Prerequisites

* Python 3.10+
* NVIDIA GPU with CUDA support (Recommended for real-time inference)

### Setup

1. **Clone the Repository:**
```bash
git clone https://github.com/vinitkumargupta/campusguardai.git
cd campusguardai
```


2. **Install Dependencies:**
```bash
pip install -r requirements.txt
```


3. **Calibration:**
Execute the calibration script to define the speed trap lines on the input video.
```bash
python get_line_coords.py
```


Update `cv_engine/config.py` with the generated coordinates.


4. **Run the CV Engine:**
```bash
python cv_engine/main.py
```


5. **Launch the Dashboard:**
```bash
cd backend_dashboard
python manage.py runserver
```



## 7. Results and Features

* **Real-time Visualization:** Annotates video feed with bounding boxes, vehicle IDs, estimated speeds, and passenger counts.
* **Automated Logging:** JSON-based logging of all vehicle entries with timestamps and metadata.
* **Evidence Archival:** Automatically saves high-resolution snapshots of detected violations.
* **SMS Alerts:** Capable of sending immediate notifications to vehicle owners via Twilio upon violation detection.

## 8. Future Scope

* **Helmet Detection:** Integration of a secondary classifier to detect helmet usage on two-wheeler riders.
* **Night Mode:** Optimization of OCR and detection models for low-light conditions.
* **Centralized Database:** Migration from JSON logs/SQLite to a unified PostgreSQL database for scalability.
