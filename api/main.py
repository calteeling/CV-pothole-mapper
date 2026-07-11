from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.config import get_settings
from api.logger import get_logger
from api.routes import router
from api.database import init_db

settings = get_settings()
logger = get_logger(__name__)


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

    init_db()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    return app


app = create_app()