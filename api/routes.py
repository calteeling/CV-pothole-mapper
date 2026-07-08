from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.database import get_db, Pothole
from api.schemas import PotholeCreate, PotholeResponse
from datetime import datetime

router = APIRouter()


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
    return db_pothole


@router.get("/potholes", response_model=list[PotholeResponse])
def get_potholes(db: Session = Depends(get_db)):
    return db.query(Pothole).all()


@router.delete("/potholes")
def clear_potholes(db: Session = Depends(get_db)):
    db.query(Pothole).delete()
    db.commit()
    return {"message": "All potholes cleared"}