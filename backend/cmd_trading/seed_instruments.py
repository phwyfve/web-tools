import asyncio
import requests
from datetime import datetime, timezone
from typing import List, Dict
from pymongo import ASCENDING

from core.database import get_database

# Logger setup
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -----------------------------
# Config
# -----------------------------
NASDAQ_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
OTHER_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# -----------------------------
# Helpers
# -----------------------------
def utc_now():
    return datetime.now(timezone.utc)


def fetch_text(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text


def parse_pipe_file(text: str) -> List[Dict[str, str]]:
    lines = text.strip().splitlines()
    header = lines[0].split("|")
    records = []

    for line in lines[1:]:
        if line.startswith("File Creation Time"):
            continue

        values = line.split("|")
        if len(values) != len(header):
            continue

        records.append(dict(zip(header, values)))

    return records


def exchange_code_from_otherlisted(code: str) -> str:
    return {
        "N": "XNAS",
        "A": "XASE",
        "P": "XASE",
        "Z": "XNAS",
        "V": "XNYS"
    }.get(code, "UNKNOWN")


# -----------------------------
# Fetch from WEB
# -----------------------------
def parse_nasdaq_symbol(row: dict) -> str | None:
    return row.get("Symbol")


def parse_otherlisted_symbol(row: dict) -> str | None:
    return row.get("ACT Symbol")


def is_special_security_name(name: str | None) -> bool:
    if not name:
        return False
    lowered = name.lower()
    keywords = ["warrant", "unit", "right", "rights"]
    return any(k in lowered for k in keywords)

def fetch_instruments_from_web() -> list[dict]:
    instruments = []
    allowed_exchanges = {"XNAS", "XNYS"}

    # ---- NASDAQ LISTED ----
    nasdaq_rows = parse_pipe_file(fetch_text(NASDAQ_LISTED_URL))
    for row in nasdaq_rows:
        if row.get("Test Issue") == "Y":
            continue
        if row.get("ETF") == "Y":
            continue
        if row.get("Financial Status") != "N":
            continue

        symbol = parse_nasdaq_symbol(row)
        if not symbol:
            continue

        if is_special_security_name(row.get("Security Name")):
            continue

        instruments.append({
            "_id": f"XNAS:{symbol}",
            "symbol": symbol,
            "exchange": "XNAS",
            "name": row.get("Security Name"),
            "type": "etf" if row.get("ETF") == "Y" else "equity",
            "active": row.get("Financial Status") != "D",
        })

    # ---- OTHER LISTED (NYSE / AMEX / ARCA) ----
    other_rows = parse_pipe_file(fetch_text(OTHER_LISTED_URL))
    for row in other_rows:
        if row.get("Test Issue") == "Y":
            continue
        if row.get("ETF") == "Y":
            continue
        if row.get("Financial Status") != "N":
            continue

        symbol = parse_otherlisted_symbol(row)
        if not symbol:
            continue

        if is_special_security_name(row.get("Security Name")):
            continue

        exchange = exchange_code_from_otherlisted(row.get("Exchange"))
        if exchange not in allowed_exchanges:
            continue

        instruments.append({
            "_id": f"{exchange}:{symbol}",
            "symbol": symbol,
            "exchange": exchange,
            "name": row.get("Security Name"),
            "type": "etf" if row.get("ETF") == "Y" else "equity",
            "active": row.get("Financial Status") != "D",
        })

    return instruments


# -----------------------------
# Save to Mongo (USING YOUR GLOBAL DB)
# -----------------------------
async def save_instruments(instruments: List[Dict], simulate: bool = False):
    if simulate:
        logger.info(f"[SIMU] would upsert {len(instruments)} instruments")
        logger.info("[SIMU] no database changes performed")
        return

    db = get_database()
    collection = db.instruments
    now = utc_now()
    allowed_exchanges = ["XNAS", "XNYS"]

    # indexes (safe, idempotent)
    await collection.create_index(
        [("symbol", ASCENDING), ("exchange", ASCENDING)],
        unique=True
    )
    await collection.create_index("active")

    ops = [
        collection.update_one(
            {"_id": inst["_id"]},
            {
                "$set": {
                    "symbol": inst["symbol"],
                    "exchange": inst["exchange"],
                    "name": inst["name"],
                    "type": inst["type"],
                    "active": inst["active"],
                    "updatedAt": now,
                },
                "$setOnInsert": {
                    "_id": inst["_id"],
                    "createdAt": now,
                },
            },
            upsert=True
        )
        for inst in instruments
    ]

    results = await asyncio.gather(*ops)

    # Remove any existing instruments outside NASDAQ/NYSE or ETFs
    await collection.delete_many({
        "$or": [
            {"exchange": {"$nin": allowed_exchanges}},
            {"type": "etf"}
        ]
    })

    logger.info(f"[OK] upserted: {sum(1 for r in results if r.upserted_id)}")
    logger.info(f"[OK] modified: {sum(1 for r in results if r.modified_count)}")
    logger.info(f"[OK] total instruments: {await collection.count_documents({})}")


# -----------------------------
# Entry point (script / CLI)
# -----------------------------
async def seed_instruments(simulate: bool = False):

    logger.info("Fetching instruments from NASDAQ Trader...")
    instruments = fetch_instruments_from_web()
    logger.info(f"Fetched {len(instruments)} instruments")

    if simulate:
        logger.info("[SIMU] Saving instruments to Mongo...")
    else:
        logger.info("Saving instruments to Mongo...")
    await save_instruments(instruments, simulate=simulate)


if __name__ == "__main__":
    import os
    import argparse

    parser = argparse.ArgumentParser(description="Seed instruments from NASDAQ Trader")
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Simulate only (no DB writes)"
    )
    args = parser.parse_args()

    env_simulate = os.getenv("SIMULATE", "0") in {"1", "true", "TRUE", "yes", "YES"}
    simulate_flag = args.simulate or env_simulate
    asyncio.run(seed_instruments(simulate=simulate_flag))
