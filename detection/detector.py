from ultralytics import YOLO
import numpy as np


class PotholeDetector:
    def __init__(self, model_path: str = "models/best.pt", confidence_threshold: float = 0.25):
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold

    def detect(self, frame: np.ndarray) -> list[dict]:
        results = self.model.predict(frame, conf=self.confidence_threshold, verbose=False)
        detections = []

        for result in results:
            for box in result.boxes:
                confidence = float(box.conf)
                detections.append({
                    "confidence": round(confidence, 3),
                    "bbox": box.xyxy[0].tolist(),
                    "label": "pothole"
                })

        return detections