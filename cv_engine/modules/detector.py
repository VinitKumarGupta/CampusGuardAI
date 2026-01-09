import cv2
import numpy as np
from ultralytics import YOLO
from cv_engine import config
from cv_engine.modules.speed_estimator import SpeedEstimator
from cv_engine.modules.vehicle_logger import VehicleLogger
from cv_engine.modules.plate_reader import PlateReader

class Detector:
    def __init__(self):
        print(f"Loading YOLO model from {config.MODEL_PATH}...")
        self.model = YOLO(config.MODEL_PATH)
        
        self.speed_estimator = SpeedEstimator()
        self.logger = VehicleLogger()
        self.plate_reader = PlateReader()
        self.vehicle_plate_cache = {}  

        self.vehicle_max_passengers = {}
        
        # Colors
        self.COLOR_LINE = (255, 0, 0)
        self.COLOR_BOX = (0, 255, 0)
        self.SPEED_TRAP = (0, 0, 255)
        
    def _get_passengers(self, bike_box, all_persons):
        passenger_count = 0
        bx1, by1, bx2, by2 = map(int, bike_box)
        for p_box in all_persons:
            px1, py1, px2, py2 = map(int, p_box)
            p_center_x = int((px1 + px2) / 2)
            p_center_y = int((py1 + py2) / 2)
            if (bx1 < p_center_x < bx2) and (by1 < p_center_y < by2):
                passenger_count += 1
        return passenger_count
        
    def process_frame(self, frame, frame_num):
        raw_frame = frame.copy()    # Needed for OCR
        
        results = self.model.track(frame, persist=True, verbose=False, conf=config.CONF_THRESHOLD)
        
        # --- STATIC VISUALS ---
        overlay = frame.copy()
        speed_zone = [config.LINE_A[0], config.LINE_A[1], config.LINE_B[1], config.LINE_B[0]]
        cv2.fillPoly(overlay, [np.array(speed_zone, dtype=np.int32)], color=self.SPEED_TRAP)
        frame = cv2.addWeighted(overlay, 0.25, frame, 0.75, 0)
        
        cv2.line(frame, config.LINE_A[0], config.LINE_A[1], self.COLOR_LINE, 1)
        cv2.line(frame, config.LINE_B[0], config.LINE_B[1], self.COLOR_LINE, 1)
        cv2.putText(frame, "LINE A", config.LINE_A[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_LINE, 2)
        cv2.putText(frame, "LINE B", config.LINE_B[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_LINE, 2)

        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            class_ids = results[0].boxes.cls.cpu().numpy().astype(int)
            track_ids = results[0].boxes.id.cpu().numpy().astype(int)

            person_boxes = [boxes[i] for i, cls in enumerate(class_ids) if cls == config.PERSON_CLASS]

            for i, (box, cls_id, track_id) in enumerate(zip(boxes, class_ids, track_ids)):
                if cls_id not in config.VEHICLE_CLASSES:
                    continue

                x1, y1, x2, y2 = map(int, box)
                cx = int((x1 + x2) / 2)
                tracking_point = (cx, y2)
                
                # --- SPEED ---
                raw_speed = self.speed_estimator.estimate_speed(
                    vehicle_id=track_id, 
                    track_point=tracking_point, 
                    current_frame_num=frame_num, 
                    fps=config.TARGET_FPS
                )
                
                speed = None
                if raw_speed is not None:
                    factor = config.SPEED_CORRECTION.get(cls_id, 1.0) 
                    speed = int(raw_speed * factor)

                # --- PASSENGERS ---
                is_two_wheeler = (cls_id == 1 or cls_id == 3)
                final_pax_count = 0
                box_color = self.COLOR_BOX

                if is_two_wheeler:
                    current_pax = self._get_passengers(box, person_boxes)
                    prev_max = self.vehicle_max_passengers.get(track_id, 0)
                    final_pax_count = max(prev_max, current_pax)
                    self.vehicle_max_passengers[track_id] = final_pax_count

                # --- LOGGING ---
                violation_list = []
                if speed and speed > config.SPEED_LIMIT:
                    violation_list.append("Speeding")
                if is_two_wheeler and final_pax_count > 2:
                    violation_list.append("Triple Riding")

                if speed is not None:
                    log_pax = final_pax_count if is_two_wheeler else "N/A"
                    
                    # --- OCR LOGIC ---
                    detected_plate = "Unreadable"
                    
                    # Running OCR if the vehicle is big enough (width > 80px)
                    # (saves speed and prevents false positives on tiny distant cars)
                    box_w = x2 - x1
                    if track_id not in self.vehicle_plate_cache:
                        if box_w > 80:
                            plate = self.plate_reader.read_plate(frame)
                            if plate != "Unreadable":
                                self.vehicle_plate_cache[track_id] = plate
                                detected_plate = plate
                    else:
                        detected_plate = self.vehicle_plate_cache[track_id]


                    # Log the vehicle (Bike or Car - we read plates for both now!)
                    self.logger.log_vehicle(
                        frame=raw_frame,
                        box=box,
                        track_id=track_id,
                        class_name=self.model.names[cls_id],
                        speed=speed,
                        pax_count=log_pax,
                        violations=violation_list,
                        is_two_wheeler=is_two_wheeler,
                        plate_text=detected_plate
                    )

                # --- VISUALIZATION ---
                violation_text = ""
                if len(violation_list) > 0:
                    box_color = (0, 0, 255)
                    violation_text = " + ".join(violation_list).upper()
                    if "SPEEDING" in violation_text: violation_text = "SPEEDING!" 

                cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)

                class_name = self.model.names[cls_id].upper()[:4] 
                label_parts = [f"{class_name}-{track_id}"]
                if speed: label_parts.append(f"{speed}km/h")
                if is_two_wheeler and final_pax_count > 0: label_parts.append(f"Pax:{final_pax_count}")
                
                label = " | ".join(label_parts)
                (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(frame, (x1, y1 - 20), (x1 + w, y1), box_color, -1)
                cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)

                if violation_text:
                    cv2.putText(frame, violation_text, (x1, y1 - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                cv2.circle(frame, tracking_point, 4, (0, 255, 255), -1)

        return frame