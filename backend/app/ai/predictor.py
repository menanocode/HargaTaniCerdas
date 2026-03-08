"""
AI Price Predictor
Model prediksi harga bahan pokok menggunakan Facebook Prophet
dengan regressor tambahan (cuaca, sentimen, inflasi).
"""

import logging
import pandas as pd
import numpy as np
from datetime import date, timedelta
from typing import Optional, Any
from sqlalchemy.orm import Session
from prophet import Prophet

from app.models import Price, Weather, NewsSentiment, MacroEconomic, Prediction

logger = logging.getLogger(__name__)


def get_price_history(
    db: Session, 
    commodity: str, 
    days: int = 90,
    kode_provinsi: Optional[str] = None,
    kode_kab_kota: Optional[str] = None
) -> pd.DataFrame:
    """Get price history for a commodity as a DataFrame."""
    start_date = date.today() - timedelta(days=days)

    query = db.query(Price).filter(Price.commodity == commodity, Price.date >= start_date)
    if kode_provinsi:
        query = query.filter(Price.kode_provinsi == kode_provinsi)
    if kode_kab_kota:
        query = query.filter(Price.kode_kab_kota == kode_kab_kota)
        
    prices = query.order_by(Price.date).all()

    if not prices:
        return pd.DataFrame()

    data = [{"ds": p.date, "y": p.price} for p in prices]
    df = pd.DataFrame(data)
    df["ds"] = pd.to_datetime(df["ds"])
    return df


def get_weather_features(db: Session, days: int = 90) -> pd.DataFrame:
    """Get weather data as a DataFrame for use as regressor."""
    start_date = date.today() - timedelta(days=days)

    weather = (
        db.query(Weather)
        .filter(Weather.date >= start_date)
        .order_by(Weather.date)
        .all()
    )

    if not weather:
        return pd.DataFrame()

    data = [
        {
            "ds": w.date,
            "temperature": w.temperature or 0,
            "humidity": w.humidity or 0,
        }
        for w in weather
    ]
    df = pd.DataFrame(data)
    df["ds"] = pd.to_datetime(df["ds"])
    return df


def get_sentiment_features(db: Session, commodity: str, days: int = 90) -> pd.DataFrame:
    """Get aggregated daily sentiment scores as a DataFrame."""
    start_date = date.today() - timedelta(days=days)

    query = db.query(NewsSentiment).filter(NewsSentiment.date >= start_date)

    # Filter by commodity if possible, otherwise use all food-related news
    commodity_news = query.filter(NewsSentiment.related_commodity == commodity).all()
    if not commodity_news:
        commodity_news = query.all()

    if not commodity_news:
        return pd.DataFrame()

    # Aggregate by date
    daily_sentiment = {}
    for n in commodity_news:
        d = n.date
        if d not in daily_sentiment:
            daily_sentiment[d] = []
        if n.sentiment_score is not None:
            daily_sentiment[d].append(n.sentiment_score)

    data = [
        {"ds": d, "sentiment": np.mean(scores) if scores else 0}
        for d, scores in daily_sentiment.items()
    ]
    df = pd.DataFrame(data)
    if not df.empty:
        df["ds"] = pd.to_datetime(df["ds"])
    return df


def get_inflation_feature(db: Session) -> float:
    """Get latest inflation value as a static feature."""
    latest = (
        db.query(MacroEconomic)
        .filter(MacroEconomic.indicator == "inflasi")
        .order_by(MacroEconomic.date.desc())
        .first()
    )
    return latest.value if latest else 0.0


def predict_prices(
    db: Session,
    commodity: str,
    days: int = 7,
    history_days: int = 90,
    kode_provinsi: Optional[str] = None,
    kode_kab_kota: Optional[str] = None
) -> list[dict[str, Any]]:
    """
    Predict future prices using Facebook Prophet.

    Args:
        db: Database session
        commodity: Commodity name (e.g., 'beras', 'telur ayam')
        days: Number of days to predict into the future
        history_days: Days of historical data to use for training

    Returns:
        List of prediction dictionaries with date, price, trend, change_percent
    """
    # Get historical price data
    df_prices = get_price_history(db, commodity, history_days, kode_provinsi, kode_kab_kota)

    if df_prices.empty or len(df_prices) < 3:
        logger.warning(f"Not enough price data for {commodity} ({len(df_prices)} records). Need >= 3.")
        # Return simple prediction based on last known price
        return _fallback_prediction(db, commodity, days, kode_provinsi, kode_kab_kota)

    # Initialize Prophet model
    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=False if len(df_prices) < 365 else True,
        changepoint_prior_scale=0.05,
        seasonality_mode="multiplicative",
    )

    # Try to add regressors if data available
    has_weather = False
    has_sentiment = False

    df_weather = get_weather_features(db, history_days)
    df_sentiment = get_sentiment_features(db, commodity, history_days)

    if not df_weather.empty and len(df_weather) > 5:
        df_prices = df_prices.merge(df_weather[["ds", "temperature"]], on="ds", how="left")
        df_prices["temperature"] = df_prices["temperature"].fillna(df_prices["temperature"].mean())
        model.add_regressor("temperature")
        has_weather = True

    if not df_sentiment.empty and len(df_sentiment) > 3:
        df_prices = df_prices.merge(df_sentiment[["ds", "sentiment"]], on="ds", how="left")
        df_prices["sentiment"] = df_prices["sentiment"].fillna(0)
        model.add_regressor("sentiment")
        has_sentiment = True

    # Fit model
    try:
        model.fit(df_prices)
    except Exception as e:
        logger.error(f"Prophet model fit error for {commodity}: {e}")
        return _fallback_prediction(db, commodity, days, kode_provinsi, kode_kab_kota)

    # Make future dataframe
    future = model.make_future_dataframe(periods=days)

    # Add regressor values for future dates
    if has_weather:
        avg_temp = df_prices["temperature"].mean()
        if "temperature" not in future.columns:
            future["temperature"] = avg_temp
        future["temperature"] = future["temperature"].fillna(avg_temp)

    if has_sentiment:
        avg_sent = df_prices["sentiment"].mean() if "sentiment" in df_prices.columns else 0
        if "sentiment" not in future.columns:
            future["sentiment"] = avg_sent
        future["sentiment"] = future["sentiment"].fillna(avg_sent)

    # Predict
    forecast = model.predict(future)

    # Extract predictions for future dates only
    today = pd.Timestamp(date.today())
    future_forecast = forecast[forecast["ds"] > today].tail(days)

    # Get current price for trend calculation
    current_price = df_prices["y"].iloc[-1] if not df_prices.empty else 0

    predictions = []
    for _, row in future_forecast.iterrows():
        predicted = max(0, row["yhat"])  # Price can't be negative
        change_pct = ((float(predicted) - float(current_price)) / float(current_price) * 100) if current_price > 0 else 0.0

        if change_pct > 1:
            trend = "naik"
        elif change_pct < -1:
            trend = "turun"
        else:
            trend = "stabil"

        predictions.append({
            "commodity": commodity,
            "current_price": current_price,
            "predicted_price": round(float(predicted), 2),
            "trend": trend,
            "change_percent": round(float(change_pct), 2),
            "confidence": round(float(max(0, min(100, 100 - abs(row.get("yhat_upper", predicted) - row.get("yhat_lower", predicted)) / max(predicted, 1) * 100))), 1),
            "prediction_date": row["ds"].date(),
            "model_version": "prophet_v1",
        })

    return predictions


def _fallback_prediction(
    db: Session, 
    commodity: str, 
    days: int,
    kode_provinsi: Optional[str] = None,
    kode_kab_kota: Optional[str] = None
) -> list[dict[str, Any]]:
    """
    Fallback prediction when not enough historical data.
    Uses simple moving average or last known price.
    """
    query = db.query(Price).filter(Price.commodity == commodity)
    if kode_provinsi:
        query = query.filter(Price.kode_provinsi == kode_provinsi)
    if kode_kab_kota:
        query = query.filter(Price.kode_kab_kota == kode_kab_kota)
        
    latest = query.order_by(Price.date.desc()).first()

    if not latest:
        return []

    current_price = latest.price
    predictions = []

    for i in range(1, days + 1):
        pred_date = date.today() + timedelta(days=i)
        # Simple random walk with small drift
        variation = np.random.uniform(-0.5, 0.5)  # ±0.5% daily
        predicted = current_price * (1 + variation / 100)
        change_pct = ((predicted - current_price) / current_price * 100) if current_price > 0 else 0

        predictions.append({
            "commodity": commodity,
            "current_price": current_price,
            "predicted_price": round(predicted, 2),
            "trend": "naik" if change_pct > 0.5 else ("turun" if change_pct < -0.5 else "stabil"),
            "change_percent": round(change_pct, 2),
            "confidence": 30.0,  # Low confidence for fallback
            "prediction_date": pred_date,
            "model_version": "fallback_v1",
        })

    return predictions


def store_predictions(db: Session, predictions: list[dict]) -> list[Prediction]:
    """Store prediction results in database."""
    stored = []
    for pred in predictions:
        existing = (
            db.query(Prediction)
            .filter(
                Prediction.commodity == pred["commodity"],
                Prediction.prediction_date == pred["prediction_date"],
            )
            .first()
        )

        if existing:
            existing.predicted_price = pred["predicted_price"]
            existing.trend = pred["trend"]
            existing.change_percent = pred["change_percent"]
            existing.confidence = pred["confidence"]
            existing.current_price = pred["current_price"]
            existing.model_version = pred["model_version"]
            stored.append(existing)
        else:
            record = Prediction(
                commodity=pred["commodity"],
                current_price=pred["current_price"],
                predicted_price=pred["predicted_price"],
                trend=pred["trend"],
                change_percent=pred["change_percent"],
                confidence=pred["confidence"],
                prediction_date=pred["prediction_date"],
                model_version=pred["model_version"],
            )
            db.add(record)
            stored.append(record)

    db.commit()
    logger.info(f"Stored {len(stored)} predictions for {predictions[0]['commodity'] if predictions else 'unknown'}")
    return stored
