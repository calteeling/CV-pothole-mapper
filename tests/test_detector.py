from detection.detector import PotholeDetector
import urllib.request
import cv2

# Download a sample pothole image to test with
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