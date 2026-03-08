from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Price(Base):
    """Harga bahan pokok harian dari SP2KP."""
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    commodity = Column(String(100), nullable=False, index=True)
    price = Column(Float, nullable=False)
    previous_price = Column(Float, nullable=True)
    change_percent = Column(Float, nullable=True)
    unit = Column(String(20), default="Rp/kg")
    region = Column(String(100), nullable=True)
    kode_provinsi = Column(String(10), nullable=True)
    kode_kab_kota = Column(String(10), nullable=True)
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Price {self.commodity} Rp{self.price} on {self.date}>"


class Weather(Base):
    """Data cuaca harian dari BMKG."""
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, autoincrement=True)
    region = Column(String(100), nullable=True)
    adm4_code = Column(String(20), nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    weather_desc = Column(String(200), nullable=True)
    cloud_cover = Column(Float, nullable=True)
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Weather {self.region} {self.temperature}°C on {self.date}>"


class NewsSentiment(Base):
    """Sentimen berita ekonomi dari CNN Indonesia."""
    __tablename__ = "news_sentiments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    url = Column(String(500), nullable=True)
    source = Column(String(100), default="Berita Lokal")
    content_snippet = Column(Text, nullable=True)
    sentiment_score = Column(Float, nullable=True)  # -1 (negatif) to +1 (positif)
    sentiment_label = Column(String(20), nullable=True)  # positif/negatif/netral
    related_commodity = Column(String(100), nullable=True)
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<News '{self.title[:30]}' sentiment={self.sentiment_score}>"


class MacroEconomic(Base):
    """Data makro ekonomi dari BPS (inflasi, dll)."""
    __tablename__ = "macro_economics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    indicator = Column(String(100), nullable=False)  # inflasi, ihk
    value = Column(Float, nullable=False)
    period = Column(String(50), nullable=True)  # 2026-01, 2026-02
    source = Column(String(100), default="BPS")
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<MacroEconomic {self.indicator}={self.value} {self.period}>"


class Prediction(Base):
    """Hasil prediksi AI."""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    commodity = Column(String(100), nullable=False, index=True)
    current_price = Column(Float, nullable=True)
    predicted_price = Column(Float, nullable=False)
    trend = Column(String(20), nullable=False)  # naik/turun/stabil
    change_percent = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    prediction_date = Column(Date, nullable=False)  # tanggal prediksi untuk
    model_version = Column(String(50), default="prophet_v1")
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Prediction {self.commodity} {self.trend} {self.change_percent}%>"
