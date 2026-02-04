"""
Caskada flow for daily market metrics and leaderboards computation.
"""
import asyncio
from caskada import Node, Flow, Memory
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd  
import logging

from core.database import get_database

logger = logging.getLogger(__name__)

# --- Node 1: Load Instruments ---
class LoadInstruments(Node):
    async def prep(self, memory):
        return memory
    
    async def exec(self, memory):
        db = get_database()
        cursor = db.instruments.find({"active": True}, {"_id": 1, "symbol": 1, "name": 1}).limit(5000)
        instruments = await cursor.to_list(length=None)
        
        memory.instruments = [
            {"instrumentId": x["_id"], "symbol": x["symbol"], "name": x["name"]}
            for x in instruments
        ]
        logger.info(f"Loaded {len(memory.instruments)} active instruments.")
        return memory.instruments

    async def post(self, memory, prep_res, exec_res):
        return memory

# --- Node 2: Fan-out per Instrument ---
class FanOutInstruments(Node):
    async def prep(self, memory):
        return memory
    
    async def exec(self, memory):
        return memory.instruments
    
    async def post(self, memory, prep_res, exec_res):
        memory.batches_nb = len(exec_res)
        for count, instrument in enumerate(exec_res):
            logger.info(f"Fant out for {instrument['symbol']}")
            self.trigger("default", instrument)

# --- Node 3: Fetch Daily Bars (Yahoo Finance) ---
class FetchDailyBarsAndComputeMetrics(Node):
    async def prep(self, instrument):
        return instrument
        
    async def exec(self, instrument):
        symbol = instrument["symbol"]
        instrumentId = instrument["instrumentId"]
        db = get_database()
        
        # Check existing data in database (limit to 300 most recent bars)
        existing_bars_cursor = db.daily_bars.find(
            {"instrumentId": instrumentId}
        ).sort("date", -1).limit(300)
        existing_bars = await existing_bars_cursor.to_list(length=None)
        
        # Determine if we need to fetch new data
        need_fetch = False
        fetch_period = "1y"  # Default: fetch 1 year for 52w window
        
        if not existing_bars:
            # No data in DB, fetch full period
            logger.info(f"No existing data for {symbol}, fetching full 1y period")
            need_fetch = True
        else:
            # Check if we have enough data and if it's recent
            most_recent_date = max(bar["date"] for bar in existing_bars)
            most_recent_dt = datetime.strptime(most_recent_date, "%Y-%m-%d")
            today = datetime.utcnow()
            days_old = (today - most_recent_dt).days
            
            if days_old > 1:
                # Data is outdated, fetch recent data only
                logger.info(f"Data for {symbol} is {days_old} days old, fetching updates since {most_recent_date}")
                need_fetch = True
                fetch_period = f"{min(days_old + 5, 30)}d"  # Fetch with small buffer, max 30d
            elif len(existing_bars) < 252:
                # Not enough historical data for 52w window
                logger.info(f"Insufficient data for {symbol} ({len(existing_bars)} bars), fetching full 1y period")
                need_fetch = True
            else:
                logger.info(f"Using existing data for {symbol} ({len(existing_bars)} bars, most recent: {most_recent_date})")
        
        # Fetch new data if needed
        if need_fetch:
            logger.info(f"Fetching daily bars for {symbol} (period: {fetch_period})")
            bars = yf.download(symbol, period=fetch_period, interval="1d", auto_adjust=False, prepost=False)
            # Si MultiIndex, sélectionne le bon niveau
            if isinstance(bars.columns, pd.MultiIndex):
                bars = bars.xs(symbol, axis=1, level=1)
            bars = bars.reset_index()

            daily_bars = []
            for _, row in bars.iterrows():
                date_val = row["Date"]
                if hasattr(date_val, 'date'):
                    date_str = date_val.date().isoformat()
                else:
                    date_str = str(date_val)
                bar = {
                    "instrumentId": instrumentId,
                    "date": date_str,
                    "open": float(row["Open"].iloc[0]) if hasattr(row["Open"], "iloc") else float(row["Open"]),
                    "high": float(row["High"].iloc[0]) if hasattr(row["High"], "iloc") else float(row["High"]),
                    "low": float(row["Low"].iloc[0]) if hasattr(row["Low"], "iloc") else float(row["Low"]),
                    "close": float(row["Close"].iloc[0]) if hasattr(row["Close"], "iloc") else float(row["Close"]),
                    "volume": int(row["Volume"].iloc[0]) if hasattr(row["Volume"], "iloc") else int(row["Volume"]),
                }
                daily_bars.append(bar)

            # Store daily bars in DB
            for bar in daily_bars:
                db.daily_bars.update_one(
                    {"instrumentId": bar["instrumentId"], "date": bar["date"]},
                    {"$set": bar}, upsert=True
                )
            
            if daily_bars:
                logger.info(f"Stored {len(daily_bars)} new/updated bars for {symbol}")
            
            # Reload all bars from DB for metrics computation (limit to 300 most recent)
            existing_bars_cursor = db.daily_bars.find(
                {"instrumentId": instrumentId}
            ).sort("date", -1).limit(300)
            existing_bars = await existing_bars_cursor.to_list(length=None)
        
        # Use existing data for metrics computation
        daily_bars = existing_bars
        
        # Skip instrument if no data available
        if not daily_bars:
            logger.warning(f"No data available for {symbol}, skipping metrics computation")
            return instrument

        #compute metrics
        bars = sorted(daily_bars, key=lambda x: x["date"])
        today = bars[-1]["date"]
        logger.info(f"Compute metrics for instr {instrument['symbol']} at date {today}")
        def window_bars(n):
            return bars[-n:] if len(bars) >= n else bars
        def high(bars):
            return max(x["high"] for x in bars)
        def low(bars):
            return min(x["low"] for x in bars)
        last_price = bars[-1]["close"]
        volume = bars[-1]["volume"]
        metrics = {
            "instrumentId": instrumentId,
            "symbol": instrument["symbol"],
            "date": today,
            "last_price": last_price,
            "volume": volume,
            "computedAt": datetime.utcnow().isoformat() + "Z"
        }
        for n, label in [(5, "5d"), (21, "1M"), (42, "2M"), (63, "3M"), (126, "6M"), (252, "52w")]:
            wbars = window_bars(n)
            if len(wbars) < 1:
                continue
            h = high(wbars)
            l = low(wbars)
            metrics[f"high_{label}"] = h
            metrics[f"low_{label}"] = l
            # Change from low (for gainers) - positive = stock went up from lowest point
            metrics[f"change_from_low_{label}"] = last_price - l
            metrics[f"change_pct_from_low_{label}"] = ((last_price - l) / l * 100) if l else None
            # Change from high (for losers) - negative = stock went down from highest point
            metrics[f"change_from_high_{label}"] = last_price - h
            metrics[f"change_pct_from_high_{label}"] = ((last_price - h) / h * 100) if h else None

        #compute MA 50, 100, 200 and EMA20
        df = pd.DataFrame(bars)
        df["close"] = df["close"].astype(float)

        df["ma50"] = df["close"].rolling(window=50).mean()
        df["ma100"] = df["close"].rolling(window=100).mean()
        df["ma200"] = df["close"].rolling(window=200).mean()
        df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()

        last_row = df.iloc[-1]

        metrics["ma50"] = float(last_row["ma50"])
        metrics["ma100"] = float(last_row["ma100"])
        metrics["ma200"] = float(last_row["ma200"])
        metrics["ema20"] = float(last_row["ema20"])

        metrics["stacked_ma_trend"] = bool(
            last_row["ma200"] < last_row["ma100"] < last_row["ma50"] < last_row["ema20"] < last_price
        )
        
        #store interval metrics
        db.daily_metrics.update_one(
                {"instrumentId": metrics["instrumentId"], "date": metrics["date"]},
                {"$set": metrics}, upsert=True
            )
        
        return instrument
    
# --- Node 4: Compute Leaderboards ---
class ComputeLeaderboards(Node):
    async def prep(self, memory):
        return memory
    
    async def exec(self, memory):

        memory.batches_nb -= 1
        if(memory.batches_nb > 0):
            logger.info(f"Waiting for other batches to complete. Remaining: {memory.batches_nb}")
            return memory
        
        logger.info("All instrument metrics computed. Computing leaderboards...")

        db = get_database()
        today = memory.execution_date
        periods = [("5d", 5), ("1M", 21), ("2M", 42), ("3M", 63), ("6M", 126), ("52w", 252)]
        # Génère la liste des dates à tester : today, today-1, today-2
        date_format = "%Y-%m-%d"
        today_dt = datetime.strptime(today, date_format)
        date_tries = [
            (today_dt - timedelta(days=delta)).strftime(date_format)
            for delta in range(4)
        ]
        logger.info(f"Computing leaderboards for dates: {date_tries}")
        for label, _ in periods:
            for typ, sort_dir in [("high", -1), ("low", 1)]:
                # For gainers (high), use change_pct_from_low (positive values)
                # For losers (low), use change_pct_from_high (negative values)
                key = f"change_pct_from_low_{label}" if typ == "high" else f"change_pct_from_high_{label}"
                metrics = []
                for date_try in date_tries:
                    logger.info(f"try get metrics date  {label} {date_try} for type {typ}")
                    q = {key: {"$ne": None}, "date": date_try}
                    sort = [(key, sort_dir)]
                    cursor = db.daily_metrics.find(q).sort(sort).limit(3600)
                    metrics = await cursor.to_list(length=None)
                    if metrics:
                        break
                items = []
                for rank, m in enumerate(metrics, 1):
                    items.append({
                        "instrumentId": m["instrumentId"],
                        "symbol": m.get("symbol", ""),
                        "change_pct": m[key],
                        "last_price": m.get("last_price", 0),
                        "volume": m.get("volume", 0),
                        "rank": rank
                    })
                board = {
                    "date": date_try,
                    "period": label,
                    "type": typ,
                    "generatedAt": datetime.utcnow().isoformat() + "Z",
                    "items": items
                }
                db.leaderboards.update_one(
                    {"date": date_try, "period": label, "type": typ},
                    {"$set": board}, upsert=True
                )
            # Ajout du leaderboard market movers (volume)
            for date_try in date_tries:
                q = {"date": date_try, "volume": {"$ne": None}}
                sort = [("volume", -1)]
                cursor = db.daily_metrics.find(q).sort(sort).limit(3600)
                metrics = await cursor.to_list(length=None)
                if metrics:
                    items = []
                    for rank, m in enumerate(metrics, 1):
                        items.append({
                            "instrumentId": m["instrumentId"],
                            "symbol": m.get("symbol", ""),
                            "volume": m["volume"],
                            "last_price": m.get("last_price", 0),
                            "rank": rank
                        })
                    board = {
                        "date": date_try,
                        "period": "market_movers",
                        "type": "volume",
                        "generatedAt": datetime.utcnow().isoformat() + "Z",
                        "items": items
                    }
                    db.leaderboards.update_one(
                        {"date": date_try, "period": "market_movers", "type": "volume"},
                        {"$set": board}, upsert=True
                    )
        logger.info(f"Leaderboards computed for {today} (or previous 2 days if needed).")
        return memory
    

# --- Flow Definition ---
def create_flow():
    load = LoadInstruments()
    fan = FanOutInstruments()
    metrics = FetchDailyBarsAndComputeMetrics()
    boards = ComputeLeaderboards()
    load >> fan >> metrics >> boards
    return Flow(start=load, options={"max_visits": 10000})

# --- Example Entrypoint ---
async def seed_instrument_prices():
    memory = Memory({"execution_date":  datetime.utcnow().strftime("%Y-%m-%d")})
    flow = create_flow()
    await flow.run(memory)

# --- Example Entrypoint ---
async def seed_leaderboards_only():
    memory = Memory({"execution_date":  datetime.utcnow().strftime("%Y-%m-%d")})
    load = LoadInstruments()
    boards = ComputeLeaderboards()
    load >> boards
    flow = Flow(start=load)
    memory.batches_nb = 0
    await flow.run(memory)

if __name__ == "__main__":
    asyncio.run(seed_instrument_prices())