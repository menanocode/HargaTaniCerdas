"""
Prices Router — /api/prices
Menampilkan data harga historis dari database.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from app.database import get_db
from app.models import Price
from app.schemas import PriceOut, PriceHistoryOut

router = APIRouter(prefix="/api", tags=["prices"])


@router.get("/prices", response_model=PriceHistoryOut)
async def get_price_history(
    commodity: str = Query("beras", description="Nama komoditas"),
    days: int = Query(30, description="Jumlah hari ke belakang", ge=1, le=365),
    kode_provinsi: str = Query(None, description="Kode Provinsi"),
    kode_kab_kota: str = Query(None, description="Kode Kab/Kota"),
    db: Session = Depends(get_db),
):
    """
    Ambil harga historis untuk satu komoditas.

    - **commodity**: Nama komoditas
    - **days**: Jumlah hari ke belakang (default 30)
    """
    start_date = date.today() - timedelta(days=days)

    query = db.query(Price).filter(Price.commodity == commodity, Price.date >= start_date)
    if kode_provinsi:
        query = query.filter(Price.kode_provinsi == kode_provinsi)
    if kode_kab_kota:
        query = query.filter(Price.kode_kab_kota == kode_kab_kota)
        
    prices = query.order_by(Price.date).all()

    price_values = [p.price for p in prices] if prices else [0]

    return PriceHistoryOut(
        commodity=commodity,
        prices=[PriceOut.model_validate(p) for p in prices],
        avg_price=sum(price_values) / len(price_values),
        min_price=min(price_values),
        max_price=max(price_values),
    )


@router.get("/commodities", response_model=list[str])
async def get_commodities(db: Session = Depends(get_db)):
    """Ambil daftar semua komoditas yang tersedia di database."""
    commodities = (
        db.query(Price.commodity)
        .distinct()
        .order_by(Price.commodity)
        .all()
    )
    return [c[0] for c in commodities]
