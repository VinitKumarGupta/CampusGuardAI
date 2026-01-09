import cv2
import os
import json
from datetime import datetime
from cv_engine import config

class VehicleLogger:
    def __init__(self):
        self.logged_ids = set()
        
        # JSON Database
        self.json_db_path = config.OUTPUT_LOGS_DIR
        
        if not os.path.exists(self.json_db_path):
            with open(self.json_db_path, 'w') as f:
                json.dump([], f)

    def log_vehicle(self, frame, box, track_id, class_name, speed, pax_count, violations, is_two_wheeler, plate_text="N/A"):
        """
        Logs metadata for ALL vehicles.
        Saves snapshot ONLY if there are violations.
        """
        # Idempotency Check
        if track_id in self.logged_ids:
            return
        
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = "N/A"  # Default if no violation

        # --- SNAPSHOT LOGIC (Violations Only) ---
        if len(violations) > 0:
            x1, y1, x2, y2 = map(int, box)
            h, w, _ = frame.shape
            
            # Base Padding
            pad_x = 20
            pad_y = 20
            
            # --- CROP ADJUSTMENT ---
            # If Two-Wheeler: Expand TOP crop significantly to catch passenger heads
            if is_two_wheeler:
                box_height = y2 - y1
                extra_head_room = int(box_height * 0.4) # Add 40% height to top
                y1 = max(0, y1 - extra_head_room)
                y2 = min(h, y2 + pad_y) # Normal bottom padding
            else:
                # Normal Car Padding
                y1 = max(0, y1 - pad_y)
                y2 = min(h, y2 + pad_y)

            x1 = max(0, x1 - pad_x)
            x2 = min(w, x2 + pad_x)
            
            vehicle_crop = frame[y1:y2, x1:x2]
            
            # Save Image
            if vehicle_crop.size > 0:
                image_filename = f"v_{track_id}_{timestamp_str}.jpg"
                filepath = os.path.join(config.OUTPUT_VIOLATIONS_DIR, image_filename)
                cv2.imwrite(filepath, vehicle_crop)
                print(f" VIOLATION SAVED: ID {track_id} | {class_name} | {violations}")

        # --- JSON LOGGING (For Every Vehicle) ---
        record = {
            "entry_id": f"{track_id}_{timestamp_str}",
            "track_id": int(track_id),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "class": class_name,
            "speed_kmh": speed,
            "passengers": pax_count,
            "violations": violations,
            "is_violation": len(violations) > 0,
            "image_path": image_filename, # "N/A" for normal vehicles
            "plate_number": plate_text
        }
        
        self._append_to_json(record)
        self.logged_ids.add(track_id)

    def _append_to_json(self, record):
        try:
            with open(self.json_db_path, 'r+') as f:
                data = json.load(f)
                data.append(record)
                f.seek(0)
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error logging JSON: {e}")