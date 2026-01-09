import cv2
import re
import os
import easyocr
from ultralytics import YOLO

class PlateReader:
    def __init__(self):
        # Load your CUSTOM trained plate detector
        model_path = "best.pt"

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Plate detector model not found at {model_path}"
            )

        print(f"Loading Plate Detector from {model_path}...")
        self.plate_model = YOLO(model_path)

        print("Loading EasyOCR...")
        self.ocr = easyocr.Reader(
            ['en'],
            gpu=True  # you have CUDA + torch, so use GPU
        )

        # Indian plate pattern (strict but realistic)
        self.plate_regex = re.compile(
            r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{3,4}$'
        )

    def read_plate(self, frame):
        """
        Runs plate detection on FULL FRAME.
        Returns first valid plate text found, else 'Unreadable'.
        """

        results = self.plate_model(frame, conf=0.3, verbose=False)

        if not results or results[0].boxes is None:
            return "Unreadable"

        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Safe crop
            h, w, _ = frame.shape
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            plate_crop = frame[y1:y2, x1:x2]
            if plate_crop.size == 0:
                continue

            # Upscale for OCR
            plate_crop = cv2.resize(
                plate_crop,
                None,
                fx=2.0,
                fy=2.0,
                interpolation=cv2.INTER_CUBIC
            )
            
            # cv2.imshow("OCR INPUT - Plate Crop", plate_crop)
            # cv2.waitKey(1)

            # OCR
            ocr_results = self.ocr.readtext(
                plate_crop,
                detail=0,
                allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            )

            if not ocr_results:
                continue

            raw_text = "".join(ocr_results)
            clean_text = re.sub(r'[^A-Z0-9]', '', raw_text.upper())

            # Remove country prefix if merged
            if clean_text.startswith("IND"):
                clean_text = clean_text[3:]

            # Validate
            if self.plate_regex.match(clean_text):
                return clean_text

        return "Unreadable"
