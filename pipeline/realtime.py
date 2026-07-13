import cv2
import time
import requests
import numpy as np
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
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
        except requests.exceptions.ConnectionError:
            logger.error("Could not connect to API — check hotspot connection")
        except requests.exceptions.Timeout:
            logger.error("API request timed out")

    def draw_detections(self, frame: np.ndarray, detections: list) -> np.ndarray:
        for detection in detections:
            bbox = detection["bbox"]
            confidence = detection["confidence"]
            x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            label = f"Pothole {confidence:.0%}"
            cv2.putText(
                frame, label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (0, 0, 255), 2
            )
        return frame

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

        picam2 = Picamera2()
        config = picam2.create_preview_configuration(
            main={"size": (1280, 720), "format": "RGB888"}
        )
        picam2.configure(config)
        picam2.start()
        time.sleep(2)

        # Set up video writer
        video_writer = None
        if self.save_video:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_path = f"/home/pi/drive_{timestamp}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(video_path, fourcc, 10, (1280, 720))
            logger.info(f"Recording video to {video_path}")

        logger.info("Camera started — detecting potholes...")
        self._running = True
        frame_count = 0
        total_detections = 0

        try:
            while self._running:
                frame = picam2.capture_array()

                detections = []
                if frame_count % self.frame_skip == 0:
                    detections = self.detector.detect(frame)

                    if detections:
                        lat, lon = self.gps.get_coordinates()
                        if lat and lon:
                            for detection in detections:
                                self.post_pothole(lat, lon, detection["confidence"])
                                total_detections += 1
                        else:
                            logger.warning("Pothole detected but no GPS fix yet")

                # Draw boxes on frame and save to video
                if video_writer:
                    annotated = self.draw_detections(frame.copy(), detections)
                    annotated_bgr = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)
                    video_writer.write(annotated_bgr)

                frame_count += 1

        except KeyboardInterrupt:
            logger.info("Pipeline stopped by user")
        finally:
            picam2.stop()
            self.gps.stop()
            if video_writer:
                video_writer.release()
                logger.info(f"Video saved to {video_path}")
            logger.info(f"Pipeline complete — {total_detections} potholes detected")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run realtime pothole detection pipeline")
    parser.add_argument("--api", default="https://cv-pothole-mapper.onrender.com/api", help="API URL")
    parser.add_argument("--no-video", action="store_true", help="Disable video recording")
    args = parser.parse_args()

    pipeline = RealtimePipeline(api_url=args.api, save_video=not args.no_video)
    pipeline.run()