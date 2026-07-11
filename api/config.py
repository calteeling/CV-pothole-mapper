from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API
    app_name: str = "Pothole Mapper API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./potholes.db"

    # Model
    model_path: str = "models/best.pt"
    confidence_threshold: float = 0.25

    # GPS
    gps_port: str = "/dev/ttyACM0"
    gps_baudrate: int = 9600

    # Pipeline
    frame_skip: int = 5

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()