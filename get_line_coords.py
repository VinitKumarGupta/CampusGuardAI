import cv2
import os

# PATH to your reference image (The one with yellow lines)
IMAGE_PATH = "cv_engine/media/input/reference_lines.png"

points = []

def click_event(event, x, y, flags, params):
    global points, frame
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        
        # Visual Feedback (Red dot on click)
        cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
        cv2.putText(frame, f"P{len(points)}", (x, y-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Draw line if we have a pair (Green line for confirmation)
        if len(points) == 2:
            cv2.line(frame, points[0], points[1], (0, 255, 0), 2)
        elif len(points) == 4:
            cv2.line(frame, points[2], points[3], (0, 255, 0), 2)
            print("\nCOMPLETED! Copy these values:")
            print(f"LINE_A = {points[0]}, {points[1]}  # Top Line (Start, End)")
            print(f"LINE_B = {points[2]}, {points[3]}  # Bottom Line (Start, End)")
            
        cv2.imshow('Calibration - Image', frame)

# Check if file exists
if not os.path.exists(IMAGE_PATH):
    print(f"Error: File not found at {IMAGE_PATH}")
    print("Please make sure you saved the screenshot there.")
    exit()

# Load Image
frame = cv2.imread(IMAGE_PATH)

if frame is None:
    print("Error: Could not load image. Check file format.")
    exit()

# CRITICAL: Resize to match the video processing resolution
frame = cv2.resize(frame, (1280, 720))

cv2.imshow('Calibration - Image', frame)
cv2.setMouseCallback('Calibration - Image', click_event)

print("--- INSTRUCTIONS ---")
print("1. Click LEFT end of the TOP yellow line.")
print("2. Click RIGHT end of the TOP yellow line.")
print("3. Click LEFT end of the BOTTOM yellow line.")
print("4. Click RIGHT end of the BOTTOM yellow line.")
print("--------------------")

cv2.waitKey(0)
cv2.destroyAllWindows()