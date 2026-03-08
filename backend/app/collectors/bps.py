"""
BPS (Badan Pusat Statistik) Data Collector
Mengambil data inflasi dan indikator makro ekonomi dari BPS Web API.
Endpoint: https://webapi.bps.go.id/v1/api/list
"""

import httpx
import logging
from datetime import date
from typing import Any
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import MacroEconomic

logger = logging.getLogger(__name__)
settings = get_settings()

BPS_API_BASE = "https://webapi.bps.go.id/v1/api/list"


async def fetch_bps_inflation(domain: str = "0000") -> dict[str, Any]:
    """
    Fetch inflation data from BPS Web API.

    Args:
        domain: BPS domain code. "0000" = national level.
                Use 2-digit province code (e.g., "33" for Jawa Tengah)
                or 4-digit regency code for regional data.

    Returns:
        Raw JSON response
    """
    # BPS API for strategic indicators (inflasi = var 3)
    # model=statictable or model=data
    params = {
        "model": "data",
        "domain": domain,
        "var": "3",  # Variable for inflation/IHK
        "key": settings.BPS_API_KEY,
    }

    logger.info(f"Fetching BPS inflation data for domain={domain}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(BPS_API_BASE, params=params)
        response.raise_for_status()
        data = response.json()
        logger.info(f"BPS response received: status={data.get('status', 'unknown')}")
        return data
    return {}  # fallback


async def fetch_bps_strategic_indicator() -> dict[str, Any]:
    """
    Fetch strategic indicators (inflasi, IHK) from BPS.
    Uses the pressrelease/statictable model.
    """
    params = {
        "model": "pressrelease",
        "domain": "0000",
        "keyword": "inflasi",
        "key": settings.BPS_API_KEY,
        "page": "1",
    }

    logger.info("Fetching BPS strategic indicators (inflasi)")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(BPS_API_BASE, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    return {}  # fallback


def parse_and_store_inflation(db: Session, raw_data: dict[str, Any]) -> list[MacroEconomic]:
    """
    Parse BPS API response and store inflation/macro data in database.
    """
    stored = []
    today = date.today()

    # BPS API response structure varies by model
    # Common: { "status": "OK", "data-availability": "available", "data": [...] }
    data_list = []

    if isinstance(raw_data, dict):
        status = raw_data.get("status", "")
        availability = raw_data.get("data-availability", "")

        if availability == "available" or status == "OK":
            # Try different response structures
            for key in ["data", "datacontent", "vervar", "turvar"]:
                candidate = raw_data.get(key)
                if isinstance(candidate, list):
                    data_list = candidate
                    break
                elif isinstance(candidate, dict):
                    # datacontent is often a dict of {key: value}
                    for k, v in candidate.items():
                        try:
                            val = float(v)
                            data_list.append({"key": k, "value": val})
                        except (ValueError, TypeError):
                            continue
                    break

        # Also try to extract period/variable info
        var_info = raw_data.get("var", [])
        turvar_info = raw_data.get("turvar", [])
        vervar_info = raw_data.get("vervar", [])

        # Map turvar IDs to period labels
        period_map = {}
        if isinstance(turvar_info, list):
            for item in turvar_info:
                if isinstance(item, dict):
                    tid = str(item.get("val", item.get("id", "")))
                    tlabel = str(item.get("label", item.get("name", tid)))
                    period_map[tid] = tlabel

        # If datacontent is a dict mapping composite keys to values
        datacontent = raw_data.get("datacontent", {})
        if isinstance(datacontent, dict) and datacontent:
            for composite_key, value in datacontent.items():
                try:
                    val = float(value)
                except (ValueError, TypeError):
                    continue

                # composite_key format is usually "varID_turvarID"
                parts = str(composite_key).split("_") if "_" in str(composite_key) else [composite_key]
                period = period_map.get(parts[-1], str(composite_key)) if len(parts) > 1 else str(composite_key)

                existing = (
                    db.query(MacroEconomic)
                    .filter(
                        MacroEconomic.indicator == "inflasi",
                        MacroEconomic.period == period,
                    )
                    .first()
                )

                if existing:
                    existing.value = val
                    existing.date = today
                    stored.append(existing)
                else:
                    record = MacroEconomic(
                        indicator="inflasi",
                        value=val,
                        period=period,
                        source="BPS",
                        date=today,
                    )
                    db.add(record)
                    stored.append(record)

    # If we got a simple data list
    for item in data_list:
        if not isinstance(item, dict):
            continue

        value = None
        for field in ["value", "nilai", "data_content", "val"]:
            if field in item:
                try:
                    value = float(item[field])
                    break
                except (ValueError, TypeError):
                    continue

        if value is None:
            if "value" in item:
                try:
                    value = float(item["value"])
                except (ValueError, TypeError):
                    continue
            else:
                continue

        indicator = "inflasi"
        period = item.get("label", item.get("period", item.get("tahun", str(today.year))))

        existing = (
            db.query(MacroEconomic)
            .filter(
                MacroEconomic.indicator == indicator,
                MacroEconomic.period == str(period),
            )
            .first()
        )

        if existing:
            existing.value = value
            existing.date = today
            stored.append(existing)
        else:
            record = MacroEconomic(
                indicator=indicator,
                value=value,
                period=str(period),
                source="BPS",
                date=today,
            )
            db.add(record)
            stored.append(record)

    db.commit()
    logger.info(f"Stored {len(stored)} BPS macro economic records")
    return stored


async def collect_bps_data(db: Session) -> list[MacroEconomic]:
    """Full pipeline: fetch from BPS API and store in database."""
    try:
        raw_data = await fetch_bps_inflation()
        return parse_and_store_inflation(db, raw_data)
    except httpx.HTTPError as e:
        logger.error(f"BPS HTTP error: {e}")
        return []
    except Exception as e:
        logger.error(f"BPS collection error: {e}")
        return []
