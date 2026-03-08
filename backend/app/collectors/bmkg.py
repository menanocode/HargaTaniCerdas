"""
BMKG Weather Data Collector
Mengambil data nowcast cuaca dari BMKG API Lokal.
Endpoint: GET http://127.0.0.1:8500/bmkg/nowcast
"""

import httpx
import logging
from datetime import date, datetime
from typing import Optional, Any
from email.utils import parsedate_to_datetime
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Weather

logger = logging.getLogger(__name__)
settings = get_settings()


async def fetch_bmkg_weather(adm4: Optional[str] = None) -> dict[str, Any]:
    """
    Fetch nowcast weather data from local BMKG API.

    Returns:
        Raw JSON response from BMKG nowcast API
    """
    url = f"{settings.BMKG_API_URL}/bmkg/nowcast"
    logger.info(f"Fetching BMKG nowcast: {url}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        logger.info(f"BMKG nowcast response received: {len(data.get('nowcast', []))} items")
        return data
    return {}  # fallback


def parse_and_store_weather(db: Session, raw_data: dict[str, Any]) -> list[Weather]:
    """
    Parse BMKG nowcast response and store weather data in database.

    Nowcast format:
    {
      "nowcast": [
        {
          "rss": {
            "title": "Hujan Lebat disertai Petir di Sulawesi Tenggara",
            "description": "...",
            "pubDate": "Sun, 08 Mar 2026 01:40:00 +0800",
            ...
          }
        },
        ...
      ]
    }
    """
    stored_records = []

    nowcast_list = raw_data.get("nowcast", [])
    if not isinstance(nowcast_list, list):
        logger.warning("BMKG nowcast: 'nowcast' field is not a list")
        return []

    # Group by date to avoid duplicate entries per day
    daily_data: dict[date, list[dict[str, str]]] = {}

    for item in nowcast_list:
        if not isinstance(item, dict):
            continue

        rss = item.get("rss", {})
        if not isinstance(rss, dict):
            continue

        title = rss.get("title", "")
        description = rss.get("description", "")
        pub_date_str = rss.get("pubDate", "")

        if not title and not description:
            continue

        # Parse date from pubDate (RFC 2822 format)
        fc_date = date.today()
        if pub_date_str:
            try:
                dt = parsedate_to_datetime(pub_date_str)
                fc_date = dt.date()
            except (ValueError, TypeError):
                try:
                    # Fallback: try ISO format
                    dt = datetime.fromisoformat(pub_date_str)
                    fc_date = dt.date()
                except (ValueError, TypeError):
                    pass

        # Extract region from title (e.g., "Hujan Lebat disertai Petir di Sulawesi Tenggara")
        region = "Indonesia"
        if " di " in title:
            region = title.split(" di ", 1)[1].strip()

        # Extract weather description from title
        weather_desc = title
        if " di " in title:
            weather_desc = title.split(" di ", 1)[0].strip()

        if fc_date not in daily_data:
            daily_data[fc_date] = []

        daily_data[fc_date].append({
            "region": region,
            "weather_desc": weather_desc,
            "description": description,
        })

    # Store one record per date (aggregate descriptions)
    for fc_date, entries in daily_data.items():
        # Combine all weather descriptions for this date
        all_descs = list(set(entry["weather_desc"] for entry in entries if entry["weather_desc"]))
        combined_desc = "; ".join(all_descs[:5])  # Limit to 5 descriptions

        # Use the most common region, or combine
        regions = [entry["region"] for entry in entries if entry["region"]]
        region = regions[0] if regions else "Indonesia"

        # Check for existing record
        existing = (
            db.query(Weather)
            .filter(Weather.date == fc_date)
            .first()
        )

        if existing:
            existing.weather_desc = combined_desc[:200]
            existing.region = region
            stored_records.append(existing)
        else:
            record = Weather(
                region=region,
                adm4_code=settings.BMKG_ADM4,
                temperature=None,  # Nowcast doesn't provide numerical data
                humidity=None,
                wind_speed=None,
                weather_desc=combined_desc[:200],
                cloud_cover=None,
                date=fc_date,
            )
            db.add(record)
            stored_records.append(record)

    db.commit()
    logger.info(f"Stored {len(stored_records)} BMKG weather records")
    return stored_records


async def collect_bmkg_weather(db: Session) -> list[Weather]:
    """Full pipeline: fetch from BMKG API and store in database."""
    try:
        raw_data = await fetch_bmkg_weather()
        return parse_and_store_weather(db, raw_data)
    except httpx.HTTPError as e:
        logger.error(f"BMKG HTTP error: {e}")
        return []
    except Exception as e:
        logger.error(f"BMKG collection error: {e}")
        return []
