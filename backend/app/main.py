"""
HargaTaniCerdas Backend — Main Application
FastAPI application untuk Sistem Prediksi Harga Bahan Pokok.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import init_db, get_db, SessionLocal
from app.scheduler import setup_scheduler, run_all_collectors
from app.routers import predict, prices, weather, news, dashboard
from app.collectors.sp2kp import collect_sp2kp_prices
from app.collectors.bmkg import collect_bmkg_weather
from app.collectors.news import collect_news_sentiments
from app.collectors.bps import collect_bps_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events."""
    # Startup
    logger.info("🚀 Starting HargaTaniCerdas Backend...")
    init_db()
    logger.info("✅ Database tables created")
    setup_scheduler()
    logger.info("✅ Scheduler started")
    yield
    # Shutdown
    logger.info("🛑 Shutting down HargaTaniCerdas Backend...")


app = FastAPI(
    title="HargaTaniCerdas API",
    description="Sistem Prediksi Harga Bahan Pokok — API Backend",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(predict.router)
app.include_router(prices.router)
app.include_router(weather.router)
app.include_router(news.router)
app.include_router(dashboard.router)


@app.get("/", tags=["root"])
async def root():
    """Health check and API info."""
    return {
        "app": "HargaTaniCerdas API",
        "version": "1.0.0",
        "description": "Sistem Prediksi Harga Bahan Pokok",
        "docs": "/docs",
        "endpoints": {
            "dashboard": "/api/dashboard",
            "predict": "/api/predict?commodity=beras&days=7",
            "prices": "/api/prices?commodity=beras&days=30",
            "commodities": "/api/commodities",
            "weather": "/api/weather",
            "news": "/api/news",
        },
    }


@app.post("/api/collect", tags=["data-collection"])
async def trigger_data_collection(
    tanggal: str = Query(None, description="Tanggal Utama (YYYY-MM-DD)"),
    tanggal_pembanding: str = Query(None, description="Tanggal Pembanding (YYYY-MM-DD)"),
    kode_provinsi: str = Query(None, description="Kode Provinsi"),
    kode_kab_kota: str = Query(None, description="Kode Kab/Kota"),
    db: Session = Depends(get_db)
):
    """
    Trigger manual data collection dari semua sumber.
    Berguna untuk pengumpulan data awal atau refresh.
    """
    results = {}

    try:
        sp2kp = await collect_sp2kp_prices(db, tanggal=tanggal, tanggal_pembanding=tanggal_pembanding, kode_provinsi=kode_provinsi, kode_kab_kota=kode_kab_kota)
        results["sp2kp"] = f"{len(sp2kp)} records"
    except Exception as e:
        results["sp2kp"] = f"error: {str(e)}"

    try:
        bmkg = await collect_bmkg_weather(db)
        results["bmkg"] = f"{len(bmkg)} records"
    except Exception as e:
        results["bmkg"] = f"error: {str(e)}"

    try:
        cnn = await collect_news_sentiments(db, "ekonomi Indonesia")
        results["news"] = f"{len(cnn)} records"
    except Exception as e:
        results["news"] = f"error: {str(e)}"

    try:
        bps = await collect_bps_data(db)
        results["bps"] = f"{len(bps)} records"
    except Exception as e:
        results["bps"] = f"error: {str(e)}"

    return {"status": "completed", "results": results}


@app.post("/api/collect/sp2kp", tags=["data-collection"])
async def trigger_sp2kp_collection(
    tanggal: str = Query(None, description="Tanggal Utama (YYYY-MM-DD)"),
    tanggal_pembanding: str = Query(None, description="Tanggal Pembanding (YYYY-MM-DD)"),
    kode_provinsi: str = Query(None, description="Kode Provinsi"),
    kode_kab_kota: str = Query(None, description="Kode Kab/Kota"),
    db: Session = Depends(get_db)
):
    """Trigger manual SP2KP data collection only."""
    try:
        prices = await collect_sp2kp_prices(db, tanggal=tanggal, tanggal_pembanding=tanggal_pembanding, kode_provinsi=kode_provinsi, kode_kab_kota=kode_kab_kota)
        return {"status": "ok", "records": len(prices)}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.post("/api/collect/bmkg", tags=["data-collection"])
async def trigger_bmkg_collection(db: Session = Depends(get_db)):
    """Trigger manual BMKG weather collection only."""
    try:
        weather = await collect_bmkg_weather(db)
        return {"status": "ok", "records": len(weather)}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.post("/api/collect/news", tags=["data-collection"])
async def trigger_news_collection(
    query: str = Query("ekonomi Indonesia", description="Keyword untuk mencari berita (contoh: harga beras)"),
    db: Session = Depends(get_db)
):
    """Trigger manual news collection only."""
    try:
        news = await collect_news_sentiments(db, query)
        return {"status": "ok", "records": len(news)}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.post("/api/collect/bps", tags=["data-collection"])
async def trigger_bps_collection(db: Session = Depends(get_db)):
    """Trigger manual BPS data collection only."""
    try:
        macro = await collect_bps_data(db)
        return {"status": "ok", "records": len(macro)}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
