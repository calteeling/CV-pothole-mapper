import cv2
from api.config import get_settings
from api.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


class VideoProcessor:
    def __init__(self, frame_skip: int = None):
        self.frame_skip = frame_skip or settings.frame_skip

    def extract_frames(self, video_path: str):
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            return

        frame_count = 0
        extracted = 0

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            if frame_count % self.frame_skip == 0:
                yield frame
                extracted += 1

            frame_count += 1

        cap.release()
        logger.info(f"Extracted {extracted} frames from {video_path} ({frame_count} total)")

    def get_video_fps(self, video_path: str) -> float:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        return fps

    def get_frame_count(self, video_path: str) -> int:
        cap = cv2.VideoCapture(video_path)
        count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        return count