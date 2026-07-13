import cv2
import time
import requests
import numpy as np
from picamera2 import Picamera2
from datetime import datetime, timezone
from detection.detector import PotholeDetector
from detection.gps_parser import GPSParser
from api.config import get_settings
from api.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


class RealtimePipeline:
    def __init__(self, api_url: str = None):
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

        logger.info("Camera started — detecting potholes...")
        self._running = True
        frame_count = 0
        total_detections = 0

        try:
            while self._running:
                frame = picam2.capture_array()

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

                frame_count += 1

        except KeyboardInterrupt:
            logger.info("Pipeline stopped by user")
        finally:
            picam2.stop()
            self.gps.stop()
            logger.info(f"Pipeline complete — {total_detections} potholes detected")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run realtime pothole detection pipeline")
    parser.add_argument("--api", default="https://cv-pothole-mapper.onrender.com/api", help="API URL")
    args = parser.parse_args()

    pipeline = RealtimePipeline(api_url=args.api)
    pipeline.run()