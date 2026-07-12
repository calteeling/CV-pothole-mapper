# Computer Vision Pothole Mapper

A real-time computer vision system that detects road potholes from a live camera feed, geotags each detection using a GPS module, and plots them on an interactive public map updated in real time.

**[View Live Map](https://cv-pothole-mapper.onrender.com)**

---

## Demo

> Drive around Charlotte → Pi detects potholes → markers appear on the live map within seconds

*Demo video coming soon*

---

## How It Works

1. A Raspberry Pi 5 mounted in a vehicle runs YOLOv8 nano inference on frames captured by a Pi Camera Module 3
2. A Stratux VK-162 USB GPS dongle provides real-time coordinates at 5Hz
3. When a pothole is detected above the confidence threshold, the Pi immediately POSTs the GPS coordinate and confidence score to a FastAPI backend over a phone hotspot
4. The FastAPI server logs the detection to a PostgreSQL database hosted on Supabase
5. A Leaflet.js map auto-refreshes every 5 seconds to display new detections as color-coded markers

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Detection | YOLOv8 nano, OpenCV, ultralytics |
| Hardware | Raspberry Pi 5 4GB, Pi Camera Module 3 Wide, Stratux VK-162 GPS |
| Backend | Python, FastAPI, SQLAlchemy, PostgreSQL |
| Database | Supabase (free tier, no expiration) |
| Frontend | Leaflet.js, OpenStreetMap |
| Deployment | Render |

---

## Project Structure

```
CV-pothole-mapper/
├── detection/
│   ├── detector.py          # YOLOv8 inference wrapper
│   ├── video_processor.py   # Frame extraction from video files
│   └── gps_parser.py        # Real-time NMEA GPS parsing via pyserial
├── api/
│   ├── main.py              # FastAPI app entry point
│   ├── routes.py            # API endpoint definitions
│   ├── database.py          # SQLAlchemy models and DB connection
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── config.py            # Centralized settings via pydantic-settings
│   └── logger.py            # Structured logging
├── pipeline/
│   ├── offline.py           # Post-processing pipeline for video files
│   └── realtime.py          # Live inference pipeline for Raspberry Pi
├── frontend/
│   ├── index.html           # Map UI
│   └── map.js               # Leaflet.js map logic and auto-refresh
├── scripts/
│   └── seed_data.py         # Seed realistic Charlotte pothole data
└── tests/
    ├── test_detector.py
    ├── test_video_processor.py
    └── test_gps_parser.py
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/potholes` | Returns all detections as GeoJSON |
| POST | `/api/potholes` | Log a new pothole detection |
| DELETE | `/api/potholes` | Clear all detections |

Swagger UI available at `/docs`

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

# Configure environment
cp .env.example .env
# Edit .env and set DATABASE_URL to your PostgreSQL connection string

# Run the server
uvicorn api.main:app --reload
```

Open `http://localhost:8000` — model weights download automatically on first run.

---

## Running the Pipeline

**Offline — process a video file:**
```bash
python -m pipeline.offline path/to/dashcam.mp4 --lat 35.2271 --lon -80.8431 --api http://localhost:8000/api
```

**Real-time — live inference on Raspberry Pi:**
```bash
python -m pipeline.realtime
```

---

## Model Weights

Weights are downloaded automatically from HuggingFace on first run and are not committed to this repo.

Model: `keremberke/yolov8n-pothole-segmentation`
Performance: 99.5% mAP@50, 84.9% Precision, 100% Recall

---

## Scope

Designed and optimized for city and suburban driving under 45mph — the speed range where road potholes are most common and where YOLOv8 detection is most reliable given motion blur constraints.

---

## License

CC BY 4.0 — model weights courtesy of [keremberke](https://huggingface.co/keremberke) on Hugging Face