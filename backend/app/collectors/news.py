"""
Local News Collector + Sentiment Analysis
Mengambil berita ekonomi dari Local API
dan melakukan analisis sentimen menggunakan VADER.
"""

import httpx
import logging
import re
from datetime import date, datetime
from sqlalchemy.orm import Session
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from app.models import NewsSentiment
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Commodities keyword mapping (Indonesian)
COMMODITY_KEYWORDS = {
    "beras": ["beras", "padi", "gabah", "rice"],
    "minyak goreng": ["minyak goreng", "minyak sawit", "kelapa sawit", "cpo"],
    "telur ayam": ["telur", "egg"],
    "daging ayam": ["daging ayam", "ayam broiler", "ayam potong"],
    "daging sapi": ["daging sapi", "sapi", "beef"],
    "cabai merah": ["cabai", "cabe", "chili"],
    "bawang merah": ["bawang merah", "shallot"],
    "bawang putih": ["bawang putih", "garlic"],
    "gula pasir": ["gula", "sugar"],
    "jagung": ["jagung", "corn"],
    "kedelai": ["kedelai", "soybean"],
}

# General food/economic keywords
FOOD_PRICE_KEYWORDS = [
    "harga pangan", "bahan pokok", "sembako", "inflasi",
    "kenaikan harga", "penurunan harga", "stok pangan",
    "impor", "ekspor", "produksi", "pasokan", "distribusi",
    "kebutuhan pokok", "harga komoditas", "pasar", "petani",
]

analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> tuple[float, str]:
    """
    Analyze sentiment of Indonesian text using VADER.
    Returns (score, label) where score is -1 to +1.
    """
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        label = "positif"
    elif compound <= -0.05:
        label = "negatif"
    else:
        label = "netral"

    return compound, label


def find_related_commodity(text: str) -> str | None:
    """Match text to a specific commodity based on keywords."""
    text_lower = text.lower()
    for commodity, keywords in COMMODITY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return commodity
    return None


def is_food_price_related(text: str) -> bool:
    """Check if text is related to food prices or economics."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in FOOD_PRICE_KEYWORDS)


async def fetch_local_news(query: str = "ekonomi Indonesia") -> list[dict]:
    """
    Fetch economic news from Local API.
    Returns list of news items.
    """
    url = f"{settings.LOCAL_NEWS_API_URL}/everything?q={query}&language=id"
    logger.info(f"Fetching Local news from {url}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    # API response structure: { "articles": [ { "title": "...", "url": "...", "description": "...", "publishedAt": "..." } ], ... }
    posts = data.get("articles", [])

    logger.info(f"Fetched {len(posts)} news items from Local API with query: {query}")
    return posts


def parse_and_store_news(db: Session, posts: list[dict]) -> list[NewsSentiment]:
    """
    Parse news items, analyze sentiment, and store in database.
    Only stores news related to food prices, commodities, or economics.
    """
    stored = []

    for post in posts:
        if not isinstance(post, dict):
            continue

        title = post.get("title", "")
        link = post.get("url", "")
        description = post.get("description", "")
        
        if not title:
            continue

        published_at_str = post.get("publishedAt", "")
        try:
            if published_at_str:
                news_date = datetime.fromisoformat(published_at_str.replace("Z", "+00:00")).date()
            else:
                news_date = date.today()
        except Exception:
            news_date = date.today()

        # Combine title + description for analysis
        full_text = f"{title} {description}"

        # Only process food/commodity/economic related news
        commodity = find_related_commodity(full_text)
        if not commodity and not is_food_price_related(full_text):
            continue

        # Analyze sentiment
        score, label = analyze_sentiment(full_text)

        # Check for duplicate by title + date
        existing = (
            db.query(NewsSentiment)
            .filter(NewsSentiment.title == title, NewsSentiment.date == news_date)
            .first()
        )

        if existing:
            existing.sentiment_score = score
            existing.sentiment_label = label
            existing.related_commodity = commodity
            stored.append(existing)
        else:
            source_name = post.get("source", {}).get("name", "Berita Lokal") if isinstance(post.get("source"), dict) else "Berita Lokal"
            record = NewsSentiment(
                title=title,
                url=link,
                source=source_name,
                content_snippet=description[:500] if description else None,
                sentiment_score=score,
                sentiment_label=label,
                related_commodity=commodity,
                date=news_date,
            )
            db.add(record)
            stored.append(record)

    db.commit()
    logger.info(f"Stored {len(stored)} news sentiment records")
    return stored


async def collect_news_sentiments(db: Session, query: str = "ekonomi Indonesia") -> list[NewsSentiment]:
    """Full pipeline: fetch news, analyze sentiment, and store."""
    try:
        posts = await fetch_local_news(query)
        return parse_and_store_news(db, posts)
    except httpx.HTTPError as e:
        logger.error(f"Local API HTTP error: {e}")
        return []
    except Exception as e:
        logger.error(f"News collection error: {e}")
        return []
