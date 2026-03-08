from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional, List


# ── Price Schemas ──────────────────────────────────────────────

class PriceOut(BaseModel):
    id: int
    commodity: str
    price: float
    previous_price: Optional[float] = None
    change_percent: Optional[float] = None
    unit: str = "Rp/kg"
    region: Optional[str] = None
    date: date

    class Config:
        from_attributes = True


class PriceHistoryOut(BaseModel):
    commodity: str
    prices: List[PriceOut]
    avg_price: float
    min_price: float
    max_price: float


# ── Weather Schemas ────────────────────────────────────────────

class WeatherOut(BaseModel):
    id: int
    region: Optional[str] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    weather_desc: Optional[str] = None
    date: date

    class Config:
        from_attributes = True


# ── News Schemas ───────────────────────────────────────────────

class NewsSentimentOut(BaseModel):
    id: int
    title: str
    url: Optional[str] = None
    source: str = "CNN Indonesia"
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    related_commodity: Optional[str] = None
    date: date

    class Config:
        from_attributes = True


# ── Macro Economic Schemas ─────────────────────────────────────

class MacroEconomicOut(BaseModel):
    id: int
    indicator: str
    value: float
    period: Optional[str] = None
    source: str = "BPS"
    date: date

    class Config:
        from_attributes = True


# ── Prediction Schemas ─────────────────────────────────────────

class PredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: int
    commodity: str
    current_price: Optional[float] = None
    predicted_price: float
    trend: str
    change_percent: Optional[float] = None
    confidence: Optional[float] = None
    prediction_date: date
    model_version: str = "prophet_v1"


class PredictionRequest(BaseModel):
    commodity: str = "beras"
    days: int = 7
    kode_provinsi: Optional[str] = None
    kode_kab_kota: Optional[str] = None


# ── Dashboard Schemas ──────────────────────────────────────────

class CommoditySummary(BaseModel):
    commodity: str
    latest_price: Optional[float] = None
    previous_price: Optional[float] = None
    change_percent: Optional[float] = None
    trend: Optional[str] = None
    predicted_price: Optional[float] = None


class DashboardOut(BaseModel):
    commodities: List[CommoditySummary]
    latest_weather: Optional[WeatherOut] = None
    latest_news: List[NewsSentimentOut] = []
    latest_macro: List[MacroEconomicOut] = []
    total_commodities: int = 0
    avg_change_percent: Optional[float] = None
