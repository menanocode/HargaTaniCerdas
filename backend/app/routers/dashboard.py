"""
Dashboard Router — /api/dashboard
Aggregated data endpoint untuk frontend dashboard.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from app.database import get_db
from app.models import Price, Weather, NewsSentiment, MacroEconomic, Prediction
from app.schemas import (
    DashboardOut,
    CommoditySummary,
    WeatherOut,
    NewsSentimentOut,
    MacroEconomicOut,
)

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardOut)
async def get_dashboard(
    tanggal: str = Query(None, description="Tanggal spesifik yyyy-mm-dd"),
    kode_provinsi: str = Query(None, description="Kode Provinsi"),
    kode_kab_kota: str = Query(None, description="Kode Kab/Kota"),
    db: Session = Depends(get_db)
):
    """
    Aggregated dashboard data:
    - Semua komoditas dengan harga terbaru + prediksi
    - Cuaca terbaru
    - Berita terbaru
    - Data makro ekonomi terbaru
    """
    # Get all unique commodities
    query_cmd = db.query(Price.commodity).distinct()
    if kode_provinsi:
        query_cmd = query_cmd.filter(Price.kode_provinsi == kode_provinsi)
    if kode_kab_kota:
        query_cmd = query_cmd.filter(Price.kode_kab_kota == kode_kab_kota)
        
    commodity_names = query_cmd.order_by(Price.commodity).all()
    commodity_names = [c[0] for c in commodity_names]

    # Build commodity summaries
    commodities = []
    change_percents = []

    for name in commodity_names:
        # Latest price
        price_query = db.query(Price).filter(Price.commodity == name)
        if kode_provinsi:
            price_query = price_query.filter(Price.kode_provinsi == kode_provinsi)
        if kode_kab_kota:
            price_query = price_query.filter(Price.kode_kab_kota == kode_kab_kota)
        if tanggal:
            try:
                target_date = date.fromisoformat(tanggal[:10])
                price_query = price_query.filter(Price.date == target_date)
            except (ValueError, TypeError):
                pass
            
        latest_price = price_query.order_by(Price.date.desc()).first()

        # Latest prediction
        latest_pred = (
            db.query(Prediction)
            .filter(Prediction.commodity == name)
            .order_by(Prediction.prediction_date.desc())
            .first()
        )

        summary = CommoditySummary(
            commodity=name,
            latest_price=latest_price.price if latest_price else None,
            previous_price=latest_price.previous_price if latest_price else None,
            change_percent=latest_price.change_percent if latest_price else None,
            trend=latest_pred.trend if latest_pred else None,
            predicted_price=latest_pred.predicted_price if latest_pred else None,
        )
        commodities.append(summary)

        if latest_price and latest_price.change_percent is not None:
            change_percents.append(latest_price.change_percent)

    # Latest weather
    latest_weather = (
        db.query(Weather)
        .order_by(Weather.date.desc())
        .first()
    )

    # Latest news (always show latest 10, regardless of exact date since the API might have returned older news)
    latest_news = (
        db.query(NewsSentiment)
        .order_by(NewsSentiment.date.desc())
        .limit(10)
        .all()
    )

    # Latest macro data
    latest_macro = (
        db.query(MacroEconomic)
        .order_by(MacroEconomic.date.desc())
        .limit(5)
        .all()
    )

    avg_change = sum(change_percents) / len(change_percents) if change_percents else None

    return DashboardOut(
        commodities=commodities,
        latest_weather=WeatherOut.model_validate(latest_weather) if latest_weather else None,
        latest_news=[NewsSentimentOut.model_validate(n) for n in latest_news],
        latest_macro=[MacroEconomicOut.model_validate(m) for m in latest_macro],
        total_commodities=len(commodity_names),
        avg_change_percent=round(avg_change, 2) if avg_change is not None else None,
    )
