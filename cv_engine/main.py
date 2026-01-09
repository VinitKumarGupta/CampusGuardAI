import os
import cv2
import sys

sys.path.append(os.getcwd())

from cv_engine import config
from cv_engine.modules.detector import Detector

def main():
    if not os.path.exists(config.VIDEO_PATH):
        print(f"ERROR: Video not found at {config.VIDEO_PATH}")
        return

    cap = cv2.VideoCapture(config.VIDEO_PATH)
    
    width, height = config.PROCESS_RES
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    output_path = config.OUTPUT_PATH
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    out = cv2.VideoWriter(output_path, fourcc, config.TARGET_FPS, (width, height))
    
    print(f"CampusGuard Running...")
    print(f"Press 'q' in the window to stop.")

    # 3. Initialize Detector
    detector = Detector()

    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("End of video reached.")
            break

        frame = cv2.resize(frame, config.PROCESS_RES)
        
        # Process Frame (Detection + Speed + Drawing)
        # We pass frame_count so speed estimator can calculate time delta
        processed_frame = detector.process_frame(frame, frame_count)
        
        # Show the output window
        cv2.imshow("CampusGuard AI - Monitor", processed_frame)
        out.write(processed_frame)
        
        frame_count += 1

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 7. Cleanup
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("--- PROCESS COMPLETED ---")

if __name__ == "__main__":
    main()