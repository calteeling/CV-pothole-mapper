from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db, Pothole
from api.schemas import PotholeCreate, PotholeResponse
from api.config import get_settings
from api.logger import get_logger
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()
settings = get_settings()
logger = get_logger(__name__)


@router.post("/potholes", response_model=PotholeResponse)
def log_pothole(pothole: PotholeCreate, db: Session = Depends(get_db)):
    db_pothole = Pothole(
        latitude=pothole.latitude,
        longitude=pothole.longitude,
        confidence=pothole.confidence,
        timestamp=pothole.timestamp or datetime.utcnow()
    )
    db.add(db_pothole)
    db.commit()
    db.refresh(db_pothole)
    logger.info(f"Logged pothole at ({pothole.latitude}, {pothole.longitude}) confidence={pothole.confidence}")
    return db_pothole


@router.get("/potholes", response_model=list[PotholeResponse])
def get_potholes(db: Session = Depends(get_db)):
    potholes = db.query(Pothole).all()
    logger.info(f"Returning {len(potholes)} potholes")
    return potholes


@router.delete("/potholes")
def clear_potholes(db: Session = Depends(get_db)):
    db.query(Pothole).delete()
    db.commit()
    logger.info("Cleared all potholes")
    return {"message": "All potholes cleared"}

@router.delete("/potholes/{pothole_id}")
def delete_pothole(pothole_id: int, db: Session = Depends(get_db)):
    pothole = db.query(Pothole).filter(Pothole.id == pothole_id).first()
    if not pothole:
        raise HTTPException(status_code=404, detail="Pothole not found")
    db.delete(pothole)
    db.commit()
    logger.info(f"Deleted pothole {pothole_id}")
    return {"message": f"Deleted pothole {pothole_id}"}