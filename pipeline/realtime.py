import cv2
import time
import requests
import numpy as np
import threading
from picamera2 import Picamera2
from datetime import datetime, timezone
from detection.detector import PotholeDetector
from detection.gps_parser import GPSParser
from api.config import get_settings
from api.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


class RealtimePipeline:
    def __init__(self, api_url: str = None, save_video: bool = True):
        self.detector = PotholeDetector(
            model_path=settings.model_path,
            confidence_threshold=settings.confidence_threshold
        )
        self.gps = GPSParser(
            port=settings.gps_port,
            baudrate=settings.gps_baudrate
        )
        self.api_url = api_url or "https://cv-pothole-mapper.onrender.com/api"
        self.frame_skip = settings.frame_skip
        self.save_video = save_video
        self._running = False
        self._last_detections = []
        self._detection_lock = threading.Lock()
        self._inference_frame = None
        self._inference_lock = threading.Lock()
        logger.info("Realtime pipeline initialized")

    def post_pothole(self, lat: float, lon: float, confidence: float):
        try:
            response = requests.post(
                f"{self.api_url}/potholes",
                json={
                    "latitude": lat,
                    "longitude": lon,
                    "confidence": confidence,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"Logged pothole at ({lat:.6f}, {lon:.6f}) confidence={confidence}")
            else:
                logger.error(f"Failed to log pothole: {response.status_code}")
        except Exception as e:
            logger.error(f"API error: {e}")

    def draw_detections(self, frame: np.ndarray, detections: list) -> np.ndarray:
        for detection in detections:
            bbox = detection["bbox"]
            confidence = detection["confidence"]
            x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"Pothole {confidence:.0%}"
            cv2.putText(
                frame, label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (0, 255, 0), 2
            )
        return frame

    def _inference_worker(self):
        while self._running:
            frame = None
            with self._inference_lock:
                if self._inference_frame is not None:
                    frame = self._inference_frame.copy()
                    self._inference_frame = None

            if frame is not None:
                # YOLO expects RGB — frame is already RGB from picamera2
                detections = self.detector.detect(frame)
                with self._detection_lock:
                    self._last_detections = detections

                if detections:
                    lat, lon = self.gps.get_coordinates()
                    if lat and lon:
                        for detection in detections:
                            self.post_pothole(lat, lon, detection["confidence"])
                    else:
                        logger.warning("Pothole detected but no GPS fix yet")
            else:
                time.sleep(0.01)

    def run(self):
        logger.info("Starting realtime pipeline — press Ctrl+C to stop")

        self.gps.start()
        logger.info("GPS parser started")

        logger.info("Waiting for GPS fix...")
        timeout = 30
        elapsed = 0
        while not self.gps.has_fix() and elapsed < timeout:
            time.sleep(1)
            elapsed += 1

        if not self.gps.has_fix():
            logger.warning("No GPS fix after 30s — will retry during pipeline")
        else:
            lat, lon = self.gps.get_coordinates()
            logger.info(f"GPS fix acquired: ({lat:.6f}, {lon:.6f})")

        # Use RGB888 so YOLO gets correct colors
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(
            main={"size": (1280, 720), "format": "RGB888"}
        )
        picam2.configure(config)
        picam2.start()
        time.sleep(2)

        # Measure actual FPS
        logger.info("Measuring camera FPS...")
        fps_frames = []
        for _ in range(30):
            t = time.time()
            picam2.capture_array()
            fps_frames.append(time.time() - t)
        actual_fps = 1.0 / (sum(fps_frames) / len(fps_frames))
        logger.info(f"Camera FPS: {actual_fps:.1f}")

        video_writer = None
        video_path = None
        if self.save_video:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_path = f"/home/pi/drive_{timestamp}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            # Use actual FPS so video plays at correct speed
            video_writer = cv2.VideoWriter(video_path, fourcc, actual_fps, (1280, 720))
            logger.info(f"Recording video at {actual_fps:.1f}fps to {video_path}")

        self._running = True
        inference_thread = threading.Thread(target=self._inference_worker, daemon=True)
        inference_thread.start()

        logger.info("Camera started — detecting potholes...")
        frame_count = 0

        try:
            while self._running:
                # RGB frame from picamera2
                frame = picam2.capture_array()

                if frame_count % self.frame_skip == 0:
                    with self._inference_lock:
                        self._inference_frame = frame.copy()

                if video_writer:
                    with self._detection_lock:
                        current_detections = self._last_detections.copy()

                    # Convert RGB to BGR for OpenCV video writer
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    annotated = self.draw_detections(frame_bgr, current_detections)
                    video_writer.write(annotated)

                frame_count += 1

        except KeyboardInterrupt:
            logger.info("Pipeline stopped by user")
        finally:
            self._running = False
            picam2.stop()
            self.gps.stop()
            if video_writer:
                video_writer.release()
                logger.info(f"Video saved to {video_path}")
            logger.info(f"Pipeline complete — {len(self._last_detections)} final detections")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run realtime pothole detection pipeline")
    parser.add_argument("--api", default="https://cv-pothole-mapper.onrender.com/api", help="API URL")
    parser.add_argument("--no-video", action="store_true", help="Disable video recording")
    args = parser.parse_args()

    pipeline = RealtimePipeline(api_url=args.api, save_video=not args.no_video)
    pipeline.run()