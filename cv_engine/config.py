import os

# ==============================================================================
# 1. FILE PATHS & DIRECTORIES
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Input Video Path
VIDEO_PATH = os.path.join(BASE_DIR, "media", "input", "Safetronics-Demo-Video.mp4")

# Output Directories
OUTPUT_PATH = os.path.join(BASE_DIR, "media", "output", "frames", "processed_output.mp4")
OUTPUT_LOGS_DIR = os.path.join(BASE_DIR, "media", "output", "vehicle_log.json")
OUTPUT_VIOLATIONS_DIR = os.path.join(BASE_DIR, "media", "output", "violations")

os.makedirs(OUTPUT_VIOLATIONS_DIR, exist_ok=True)

# ==============================================================================
# 2. SYSTEM SETTINGS
# ==============================================================================
PROCESS_RES = (1280, 720) 
TARGET_FPS = 30  

# ==============================================================================
# 3. YOLO MODEL SETTINGS
# ==============================================================================
MODEL_PATH = "yolov8n.pt" 
# COCO IDs
# 0 = person, 1 = bicycle, 2 = car, 3 = motorcycle
VEHICLE_CLASSES = [1, 2, 3]
PERSON_CLASS = 0
CONF_THRESHOLD = 0.3        # Confidence Threshold

# ==============================================================================
# 4. SPEED ESTIMATION SETTINGS
# ==============================================================================
REAL_DISTANCE_METERS = 4.9
SPEED_LIMIT = 30 # km/h
SPEED_CORRECTION = {
    1: 1.0,    # Bicycle
    2: 0.6,    # Car
    3: 1.0     # Motorcycle
}

# Coordinates: [(Start_X, Start_Y), (End_X, End_Y)]
LINE_A = [(1, 468), (373, 373)]     # Original was: [(3, 471), (372, 370)]
LINE_B = [(125, 546), (576, 411)]