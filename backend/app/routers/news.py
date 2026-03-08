"""
News Router — /api/news
Menampilkan berita ekonomi + skor sentimen dari database.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.database import get_db
from app.models import NewsSentiment
from app.schemas import NewsSentimentOut

router = APIRouter(prefix="/api", tags=["news"])


@router.get("/news", response_model=list[NewsSentimentOut])
async def get_news(
    days: int = Query(7, description="Jumlah hari ke belakang", ge=1, le=30),
    commodity: str = Query(None, description="Filter berdasarkan komoditas"),
    db: Session = Depends(get_db),
):
    """Ambil berita ekonomi dengan skor sentimen."""
    query = db.query(NewsSentiment)

    if commodity:
        query = query.filter(NewsSentiment.related_commodity == commodity)

    news = query.order_by(NewsSentiment.date.desc()).limit(50).all()
    return [NewsSentimentOut.model_validate(n) for n in news]
