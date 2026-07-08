from pydantic import BaseModel
from datetime import datetime


class PotholeCreate(BaseModel):
    latitude: float
    longitude: float
    confidence: float
    timestamp: datetime = None


class PotholeResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    confidence: float
    timestamp: datetime

    class Config:
        from_attributes = True