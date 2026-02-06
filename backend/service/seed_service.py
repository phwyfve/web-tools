"""
Seed service for trading data.
- On startup: seed instruments if empty
- Daily: seed daily prices + leaderboards
- Hourly: cleanup if daily seed not due
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from core.config import settings
from core.database import get_database
from cmd_trading.seed_instruments import seed_instruments
from cmd_trading.flow_stock_metrics import seed_instrument_prices, seed_leaderboards_only
from service.cleanup_service import run_single_cleanup

logger = logging.getLogger("seed_service")

_seed_lock = asyncio.Lock()


def _utc_today_str() -> str:
    return datetime.now(timezone.utc).date().isoformat()


async def _get_job_state(job_name: str) -> Optional[dict]:
    db = get_database()
    return await db.job_runs.find_one({"_id": job_name})


async def _set_job_state(job_name: str, last_run_date: str) -> None:
    db = get_database()
    await db.job_runs.update_one(
        {"_id": job_name},
        {"$set": {"last_run_date": last_run_date, "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )


async def ensure_instruments_seeded() -> bool:
    """
    Ensure instruments collection is not empty.
    Returns True if seeding was performed.
    """
    db = get_database()
    count = await db.instruments.count_documents({})
    if count > 0:
        logger.info("✅ Instruments already seeded (%s)", count)
        return False

    logger.info("🌱 No instruments found. Seeding instruments...")
    await seed_instruments()
    return True


async def run_daily_seed_if_due() -> bool:
    """
    Run daily seed if not done today.
    Returns True if daily seed ran.
    """
    today = _utc_today_str()
    state = await _get_job_state("daily_trading_seed")
    last_run_date = state.get("last_run_date") if state else None

    if last_run_date == today:
        logger.info("⏭️ Daily seed already ran today (%s)", today)
        return False

    logger.info("📈 Running daily trading seed for %s", today)
    await seed_instrument_prices()
    await seed_leaderboards_only()
    await _set_job_state("daily_trading_seed", today)
    logger.info("✅ Daily trading seed completed for %s", today)
    return True


def start_seed_scheduler():
    """
    Create and return a background task for seeding + cleanup scheduling.
    """
    interval_minutes = getattr(settings, "seed_check_interval_minutes", 60)
    logger.info("🕐 Creating seed scheduler: check every %s minutes", interval_minutes)

    async def seed_loop():
        await asyncio.sleep(10)  # short delay after startup

        while True:
            try:
                async with _seed_lock:
                    seeded_instruments = await ensure_instruments_seeded()
                    ran_daily_seed = await run_daily_seed_if_due()

                    # If no daily seed was needed, do cleanup
                    #if not ran_daily_seed and not seeded_instruments:
                        #await run_single_cleanup()

                await asyncio.sleep(interval_minutes * 60)

            except asyncio.CancelledError:
                logger.info("🛑 Seed scheduler cancelled")
                break
            except Exception as exc:
                logger.error("❌ Seed scheduler error: %s", exc)
                await asyncio.sleep(300)

    return asyncio.create_task(seed_loop())
