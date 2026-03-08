"""
Weather Router — /api/weather
Menampilkan data cuaca dari database.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.database import get_db
from app.models import Weather
from app.schemas import WeatherOut

router = APIRouter(prefix="/api", tags=["weather"])


@router.get("/weather", response_model=list[WeatherOut])
async def get_weather(
    days: int = Query(7, description="Jumlah hari ke belakang", ge=1, le=30),
    db: Session = Depends(get_db),
):
    """Ambil data cuaca terkini."""
    start_date = date.today() - timedelta(days=days)

    weather = (
        db.query(Weather)
        .filter(Weather.date >= start_date)
        .order_by(Weather.date.desc())
        .all()
    )
    return [WeatherOut.model_validate(w) for w in weather]


@router.get("/weather/latest", response_model=WeatherOut | None)
async def get_latest_weather(db: Session = Depends(get_db)):
    """Ambil data cuaca terbaru."""
    weather = (
        db.query(Weather)
        .order_by(Weather.date.desc())
        .first()
    )
    return WeatherOut.model_validate(weather) if weather else None
