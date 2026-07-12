import os
import urllib.request
import cv2
from detection.detector import PotholeDetector

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Download a sample image to test with
url = "https://ultralytics.com/images/bus.jpg"
urllib.request.urlretrieve(url, "data/test_image.jpg")

# Load image
frame = cv2.imread("data/test_image.jpg")

# Run detector
detector = PotholeDetector()
detections = detector.detect(frame)

print(f"Found {len(detections)} pothole(s)")
for d in detections:
    print(f"  Confidence: {d['confidence']} | BBox: {d['bbox']}")