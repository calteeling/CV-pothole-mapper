import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from huggingface_hub import hf_hub_download
from api.config import get_settings
from api.logger import get_logger
from api.routes import router
from api.database import init_db

settings = get_settings()
logger = get_logger(__name__)


def download_model():
    model_path = settings.model_path
    if not os.path.exists(model_path):
        os.makedirs("models", exist_ok=True)
        logger.info("Downloading model weights...")
        hf_hub_download(
            repo_id="keremberke/yolov8n-pothole-segmentation",
            filename="best.pt",
            local_dir="models/"
        )
        logger.info("Model weights downloaded successfully")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api")
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

    download_model()
    init_db()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    return app


app = create_app()