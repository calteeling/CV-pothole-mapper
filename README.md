# CV Pothole Mapper

A real-time computer vision system that detects road potholes from a live camera feed, geotags each detection using a GPS module, and plots them on an interactive public map.

**[Live Map](https://cv-pothole-mapper.onrender.com)**

---

## How It Works

1. A Raspberry Pi 5 mounted in a vehicle runs YOLOv8 nano inference on frames from a Pi Camera Module 3
2. A VK-162 USB GPS dongle provides real-time coordinates at 5Hz
3. When a pothole is detected, the Pi immediately POSTs the GPS coordinate and confidence score to a FastAPI backend over a phone hotspot
4. The FastAPI server logs the detection to a PostgreSQL database (Supabase)
5. A Leaflet.js map auto-refreshes every 5 seconds to display new detections as markers

---

## Tech Stack

**Hardware**
- Raspberry Pi 5 4GB
- Raspberry Pi Camera Module 3 Wide
- Stratux VK-162 USB GPS Dongle

**Backend**
- Python, FastAPI, SQLAlchemy
- PostgreSQL (Supabase)
- Deployed on Render

**Detection**
- YOLOv8 nano (ultralytics)
- Pretrained pothole segmentation weights

**Frontend**
- Leaflet.js interactive map
- OpenStreetMap tiles
- Auto-refreshes every 5 seconds

---

## Project Structure

CV-pothole-mapper/
├── detection/
│   ├── detector.py        # YOLOv8 inference wrapper
│   ├── video_processor.py # Frame extraction from video
│   └── gps_parser.py      # NMEA GPS parsing via pyserial
├── api/
│   ├── main.py            # FastAPI app entry point
│   ├── routes.py          # API endpoints
│   ├── database.py        # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── config.py          # Centralized settings
│   └── logger.py          # Structured logging
├── pipeline/
│   ├── offline.py         # Post-processing pipeline
│   └── realtime.py        # Live Pi inference pipeline
├── frontend/
│   ├── index.html         # Map UI
│   └── map.js             # Leaflet.js map logic
└── tests/
├── test_detector.py
├── test_video_processor.py
└── test_gps_parser.py

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/potholes` | Returns all detections as GeoJSON |
| POST | `/api/potholes` | Log a new pothole detection |
| DELETE | `/api/potholes` | Clear all detections |

---

## Local Setup

```bash
# Clone the repo
git clone https://github.com/calteeling/CV-pothole-mapper.git
cd CV-pothole-mapper

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your DATABASE_URL

# Run the server
uvicorn api.main:app --reload
```

The app will be available at `http://localhost:8000`

---

## Running the Pipeline

**Offline (video file):**
```bash
python -m pipeline.offline path/to/video.mp4 --lat 35.2271 --lon -80.8431
```

**Real-time (Raspberry Pi):**
```bash
python -m pipeline.realtime
```

---

## Model Weights

Model weights are not included in this repo due to file size. They are automatically downloaded from HuggingFace on first run:

`keremberke/yolov8n-pothole-segmentation` — 99.5% mAP@50

---

## Scope

Optimized for city driving under 45mph where potholes are most common and detection is most reliable.