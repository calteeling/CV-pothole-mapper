import requests
import argparse
from datetime import datetime, timezone
from detection.detector import PotholeDetector
from detection.video_processor import VideoProcessor
from api.config import get_settings
from api.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


class OfflinePipeline:
    def __init__(self, api_url: str = None):
        self.detector = PotholeDetector(
            model_path=settings.model_path,
            confidence_threshold=settings.confidence_threshold
        )
        self.processor = VideoProcessor(frame_skip=settings.frame_skip)
        self.api_url = api_url or "http://localhost:8000/api"
        logger.info("Offline pipeline initialized")

    def post_pothole(self, lat: float, lon: float, confidence: float):
        try:
            response = requests.post(
                f"{self.api_url}/potholes",
                json={
                    "latitude": lat,
                    "longitude": lon,
                    "confidence": confidence,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            if response.status_code == 200:
                logger.info(f"Logged pothole at ({lat}, {lon}) confidence={confidence}")
            else:
                logger.error(f"Failed to log pothole: {response.status_code}")
        except requests.exceptions.ConnectionError:
            logger.error("Could not connect to API — is the server running?")

    def run(self, video_path: str, lat: float = None, lon: float = None):
        logger.info(f"Starting offline pipeline on {video_path}")

        total_detections = 0

        for i, frame in enumerate(self.processor.extract_frames(video_path)):
            detections = self.detector.detect(frame)

            if detections:
                for detection in detections:
                    # Use provided coordinates or default to Charlotte center
                    frame_lat = lat or 35.2271
                    frame_lon = lon or -80.8431

                    self.post_pothole(
                        lat=frame_lat,
                        lon=frame_lon,
                        confidence=detection["confidence"]
                    )
                    total_detections += 1

        logger.info(f"Pipeline complete — {total_detections} potholes detected")
        return total_detections


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run offline pothole detection pipeline")
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("--lat", type=float, default=35.2271, help="Latitude")
    parser.add_argument("--lon", type=float, default=-80.8431, help="Longitude")
    parser.add_argument("--api", default="http://localhost:8000/api", help="API URL")
    args = parser.parse_args()

    pipeline = OfflinePipeline(api_url=args.api)
    pipeline.run(args.video, lat=args.lat, lon=args.lon)