"""
SP2KP Data Collector
Mengambil data harga bahan pokok dari SP2KP API Lokal.
Endpoint: POST {SP2KP_BASE_URL}/get-price-comparison
"""

import httpx
import logging
from datetime import date, timedelta
from typing import Optional, Any
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Price

logger = logging.getLogger(__name__)
settings = get_settings()


async def fetch_sp2kp_prices(
    tanggal: Optional[str] = None,
    tanggal_pembanding: Optional[str] = None,
    kode_provinsi: Optional[str] = None,
    kode_kab_kota: Optional[str] = None,
) -> dict[str, Any]:
    """
    Fetch price comparison data from SP2KP local API.

    Args:
        tanggal: Target date (YYYY-MM-DD), defaults to today
        tanggal_pembanding: Comparison date, defaults to 5 days ago
        kode_provinsi: Province code, defaults from config
        kode_kab_kota: City/regency code, defaults from config

    Returns:
        Raw JSON response from SP2KP API
    """
    if tanggal is None:
        tanggal = (date.today() - timedelta(days=2)).isoformat()
    if tanggal_pembanding is None:
        tanggal_pembanding = "2026-03-02"
    if kode_provinsi is None:
        kode_provinsi = settings.SP2KP_KODE_PROVINSI
    if kode_kab_kota is None:
        kode_kab_kota = settings.SP2KP_KODE_KAB_KOTA

    payload = {
        "tanggal": tanggal,
        "tanggal_pembanding": tanggal_pembanding,
        "kode_provinsi": kode_provinsi,
        "kode_kab_kota": kode_kab_kota,
    }

    url = f"{settings.SP2KP_BASE_URL}/get-price-comparison"
    logger.info(f"Fetching SP2KP prices: {url} with payload {payload}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        for attempt in range(3):
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                logger.info(f"SP2KP response received: {len(str(data))} chars")
                return data
            except httpx.TimeoutException:
                logger.warning(f"SP2KP timeout attempt {attempt+1}/3")
                if attempt == 2:
                    raise
            except httpx.HTTPError:
                raise
    return {}  # fallback (should not reach here)


def parse_and_store_sp2kp(
    db: Session, 
    raw_data: dict[str, Any], 
    tanggal: Optional[str] = None,
    kode_provinsi: Optional[str] = None,
    kode_kab_kota: Optional[str] = None,
) -> list[Price]:
    """
    Parse SP2KP response and store prices in database.

    The SP2KP API returns commodity price data. We parse the response
    and create Price records for each commodity found.
    """
    if tanggal is None:
        tanggal = date.today().isoformat()

    default_target_date = date.fromisoformat(tanggal)
    stored_prices = []

    # Try to parse different response structures
    # The SP2KP API may return data in various formats
    items = []

    if isinstance(raw_data, dict):
        # Try common response keys
        for key in ["data", "items", "hasil", "result", "commodities"]:
            if key in raw_data:
                candidate = raw_data[key]
                if isinstance(candidate, list):
                    items = candidate
                    break
                elif isinstance(candidate, dict):
                    # Maybe nested further
                    for subkey in ["items", "data", "list"]:
                        if subkey in candidate and isinstance(candidate[subkey], list):
                            items = candidate[subkey]
                            break
                    if items:
                        break
        # If no known key found, try the root dict values
        if not items and raw_data:
            # Check if root has commodity-like fields
            first_val = next(iter(raw_data.values()), None)
            if isinstance(first_val, list):
                items = first_val
    elif isinstance(raw_data, list):
        items = raw_data

    for item in items:
        if not isinstance(item, dict):
            continue

        # Extract commodity name (try multiple field names)
        commodity = None
        for field in ["variant_nama", "nama_komoditas", "komoditas", "commodity", "nama", "name", "item"]:
            if field in item:
                commodity = str(item[field]).strip()
                break

        if not commodity:
            continue

        # Extract previous price
        prev_price = None
        for field in ["harga_pembanding", "harga_sebelumnya", "previous_price", "harga_lama"]:
            if field in item:
                try:
                    raw_val = item[field]
                    prev_price = float(raw_val) if raw_val is not None else None
                    break
                except (ValueError, TypeError):
                    continue

        # Extract price (try multiple field names)
        price = None
        for field in ["harga", "price", "harga_sekarang", "harga_terkini", "nilai"]:
            if field in item:
                try:
                    raw_val = item[field]
                    temp_price = float(raw_val) if raw_val is not None else 0.0
                    if temp_price > 0:
                        price = temp_price
                        break
                except (ValueError, TypeError):
                    continue

        # Handle zero-price issues from SP2KP gracefully
        if price is None or price <= 0:
            if prev_price is not None and prev_price > 0:
                price = prev_price
            else:
                continue

        # Calculate change percent
        change_pct = None
        for field in ["persen_perubahan", "persentase", "change_percent", "perubahan", "persen"]:
            if field in item:
                try:
                    pct = float(item[field])
                    if pct != -100:  # Ignore faulty -100% when price was 0
                        change_pct = pct
                    break
                except (ValueError, TypeError):
                    continue

        if change_pct is None and prev_price is not None and prev_price > 0 and price is not None:
            change_pct = ((float(price) - float(prev_price)) / float(prev_price)) * 100
        elif change_pct is None:
            change_pct = 0.0

        # Extract unit
        unit = "Rp/kg"
        for field in ["satuan_display", "satuan", "unit"]:
            if field in item:
                unit = str(item[field])
                # Ensure it has Rp/ prefix if it's just kg/lt
                if unit.lower() in ["kg", "lt", "liter", "g"]:
                    unit = f"Rp/{unit}"
                break
                
        # Extract specific date if available
        item_date = default_target_date
        if "tanggal" in item and item["tanggal"]:
            try:
                item_date = date.fromisoformat(item["tanggal"][:10])
            except (ValueError, TypeError):
                pass

        # Check for duplicate (include region codes to avoid cross-region conflicts)
        dup_query = db.query(Price).filter(
            Price.commodity == commodity,
            Price.date == item_date,
            Price.kode_provinsi == (kode_provinsi or settings.SP2KP_KODE_PROVINSI),
            Price.kode_kab_kota == (kode_kab_kota or settings.SP2KP_KODE_KAB_KOTA),
        )
        existing = dup_query.first()
        if existing:
            # Update existing record
            existing.price = price
            existing.previous_price = prev_price
            existing.change_percent = change_pct
            existing.unit = unit
            stored_prices.append(existing)
        else:
            price_record = Price(
                commodity=commodity,
                price=price,
                previous_price=prev_price,
                change_percent=change_pct,
                unit=unit,
                region=f"Prov {kode_provinsi or settings.SP2KP_KODE_PROVINSI} Kab {kode_kab_kota or settings.SP2KP_KODE_KAB_KOTA}",
                kode_provinsi=kode_provinsi or settings.SP2KP_KODE_PROVINSI,
                kode_kab_kota=kode_kab_kota or settings.SP2KP_KODE_KAB_KOTA,
                date=item_date,
            )
            db.add(price_record)
            stored_prices.append(price_record)

    db.commit()
    logger.info(f"Stored {len(stored_prices)} SP2KP price records for {default_target_date}")
    return stored_prices


async def collect_sp2kp_prices(
    db: Session, 
    tanggal: Optional[str] = None,
    tanggal_pembanding: Optional[str] = None,
    kode_provinsi: Optional[str] = None,
    kode_kab_kota: Optional[str] = None,
) -> list[Price]:
    """
    Full pipeline: fetch from SP2KP API and store in database.
    """
    try:
        raw_data = await fetch_sp2kp_prices(
            tanggal=tanggal, 
            tanggal_pembanding=tanggal_pembanding,
            kode_provinsi=kode_provinsi, 
            kode_kab_kota=kode_kab_kota
        )
        return parse_and_store_sp2kp(
            db, 
            raw_data, 
            tanggal=tanggal,
            kode_provinsi=kode_provinsi, 
            kode_kab_kota=kode_kab_kota
        )
    except httpx.HTTPError as e:
        logger.error(f"SP2KP HTTP error: {e}")
        return []
    except Exception as e:
        logger.error(f"SP2KP collection error: {e}")
        return []
