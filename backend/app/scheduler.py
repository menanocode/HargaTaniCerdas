"""
Scheduler — Background tasks untuk pengumpulan data berkala.
Menggunakan APScheduler untuk menjalankan data collectors secara terjadwal.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.database import SessionLocal
from app.collectors.sp2kp import collect_sp2kp_prices
from app.collectors.bmkg import collect_bmkg_weather
from app.collectors.news import collect_news_sentiments
from app.collectors.bps import collect_bps_data

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def run_all_collectors():
    """Run all data collectors sequentially."""
    db = SessionLocal()
    try:
        logger.info("=== Starting scheduled data collection ===")

        logger.info("[1/4] Collecting SP2KP prices...")
        prices = await collect_sp2kp_prices(db)
        logger.info(f"SP2KP: {len(prices)} records")

        logger.info("[2/4] Collecting BMKG weather...")
        weather = await collect_bmkg_weather(db)
        logger.info(f"BMKG: {len(weather)} records")

        logger.info("[3/4] Collecting news sentiments...")
        news = await collect_news_sentiments(db)
        logger.info(f"News: {len(news)} records")

        logger.info("[4/4] Collecting BPS macro data...")
        macro = await collect_bps_data(db)
        logger.info(f"BPS: {len(macro)} records")

        logger.info("=== Data collection complete ===")

    except Exception as e:
        logger.error(f"Scheduled collection error: {e}")
    finally:
        db.close()


def setup_scheduler():
    """Configure and start the scheduler."""

    # Collect data every 6 hours
    scheduler.add_job(
        run_all_collectors,
        trigger=IntervalTrigger(hours=6),
        id="collect_all_data",
        name="Collect all data from SP2KP, BMKG, CNN, BPS",
        replace_existing=True,
    )

    # Also collect SP2KP prices daily at 08:00 WIB (01:00 UTC)
    scheduler.add_job(
        _collect_sp2kp_only,
        trigger=CronTrigger(hour=1, minute=0),  # 08:00 WIB
        id="daily_sp2kp",
        name="Daily SP2KP price collection",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with periodic data collection jobs")


async def _collect_sp2kp_only():
    """Collect SP2KP price data only."""
    db = SessionLocal()
    try:
        await collect_sp2kp_prices(db)
    except Exception as e:
        logger.error(f"SP2KP daily collection error: {e}")
    finally:
        db.close()
