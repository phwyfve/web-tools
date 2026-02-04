from urllib3 import request
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from cmd_trading.seed_instruments import seed_instruments
from cmd_trading.flow_stock_metrics import seed_instrument_prices, seed_leaderboards_only
from core.database import get_database
from datetime import datetime, timedelta
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

def serialize_mongo_doc(doc):
    """Convert MongoDB document to JSON-serializable dict"""
    if isinstance(doc, list):
        return [serialize_mongo_doc(item) for item in doc]
    if isinstance(doc, dict):
        return {k: serialize_mongo_doc(v) for k, v in doc.items()}
    if isinstance(doc, ObjectId):
        return str(doc)
    return doc

router = APIRouter()

PERIOD_MAP = {
    "5d": 5,
    "1M": 21,
    "2M": 42,
    "3M": 63,
    "6M": 126,
    "52w": 252,
}

@router.post("/trading/named_query")
async def query_trading_data(request: Request):
    params = await request.json()
    db = get_database()
    named_query = params.get("named_query")
    start = params.get("start", 0)
    limit = params.get("limit", 20)
    
    if named_query == "moving_average_correct_order":
        # Get most recent date from daily_metrics
        latest_metric = await db.daily_metrics.find_one({}, sort=[("date", -1)])
        if not latest_metric:
            return {"result": {"items": [], "total": 0, "start": start, "limit": limit}}
        
        latest_date = latest_metric["date"]
        logger.info(f"[NAMED_QUERY] Fetching stacked_ma_trend stocks for date: {latest_date}")
        
        # Find all stocks with stacked_ma_trend = true
        pipeline = [
            {
                "$match": {
                    "date": latest_date,
                    "stacked_ma_trend": True
                }
            },
            {
                "$lookup": {
                    "from": "instruments",
                    "localField": "instrumentId",
                    "foreignField": "_id",
                    "as": "instrument"
                }
            },
            {
                "$unwind": "$instrument"
            },
            {
                "$project": {
                    "instrumentId": 1,
                    "symbol": 1,
                    "date": 1,
                    "last_price": 1,
                    "volume": 1,
                    "ma50": 1,
                    "ma100": 1,
                    "ma200": 1,
                    "ema20": 1,
                    "change_pct_from_low_5d": 1,
                    "name": "$instrument.name"
                }
            },
            {
                "$sort": {"change_pct_from_low_5d": -1}  # Sort by 5d performance descending (best first)
            }
        ]
        
        cursor = db.daily_metrics.aggregate(pipeline)
        all_stocks = await cursor.to_list(length=None)
        
        total = len(all_stocks)
        paginated_stocks = all_stocks[start:start + limit]
        
        logger.info(f"[NAMED_QUERY] Found {total} stocks with stacked MA trend, returning {len(paginated_stocks)} (from {start})")
        
        result = {
            "items": serialize_mongo_doc(paginated_stocks),
            "total": total,
            "start": start,
            "limit": limit,
            "date": latest_date
        }
        
        return {"result": result}
    
    return {"error": "Unknown named_query"}

@router.post("/trading/data")
async def get_trading_data(request: Request):
    params = await request.json()
    db = get_database()
    data_type = params.get("data_type")  # 'stock' ou 'leaderboard'
    period = params.get("period")        # '5d', '1M', '2M', '3M', '6M', '52w', etc.
    date = params.get("date")            # optionnel, date de fin
    symbol = params.get("symbol")        # optionnel
    leaderboard_type = params.get("leaderboard_type")  # 'high', 'low', 'volume' pour leaderboard
    start = params.get("start", 0)       # index de début pour pagination
    limit = params.get("limit", 20)      # nombre d'items par page
    result = None

    logger.info(f"[TRADING_DATA] data_type={data_type}, period={period}, date={date}, symbol={symbol}, leaderboard_type={leaderboard_type}, start={start}, limit={limit}")

    if data_type == "stock":
        q = {}
        if symbol:
            q["symbol"] = symbol
        stocks = await db.instruments.find(q).to_list(length=None)
        for stock in stocks:
            bars_query = {"instrumentId": stock["_id"]}
            metrics_query = {"instrumentId": stock["_id"]}
            # Filtrage par période sur daily_bars et metrics
            if period in PERIOD_MAP:
                n_days = PERIOD_MAP[period]
                end_date = date or datetime.utcnow().strftime("%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                start_dt = end_dt - timedelta(days=n_days-1)
                bars_query["date"] = {"$gte": start_dt.strftime("%Y-%m-%d"), "$lte": end_dt.strftime("%Y-%m-%d")}
                metrics_query["date"] = {"$gte": start_dt.strftime("%Y-%m-%d"), "$lte": end_dt.strftime("%Y-%m-%d")}
            elif date:
                bars_query["date"] = date
                metrics_query["date"] = date
            stock["daily_bars"] = await db.daily_bars.find(bars_query).to_list(length=None)
            stock["metrics"] = await db.daily_metrics.find(metrics_query).to_list(length=None)
        result = serialize_mongo_doc(stocks)
    elif data_type == "leaderboard":
        q = {}
        if period:
            q["period"] = period
        if date:
            q["date"] = date
        if leaderboard_type:
            q["type"] = leaderboard_type
        
        logger.info(f"[LEADERBOARD] MongoDB query: {q}")
        
        # Use aggregation pipeline to paginate directly in MongoDB
        # 1. Match by period/date/type
        # 2. Filter only leaderboards with items
        # 3. Sort by date descending
        # 4. Limit to 1 (most recent)
        # 5. Add total count of items
        # 6. Slice the items array for pagination
        pipeline = [
            {"$match": q},
            {"$match": {"items": {"$exists": True, "$ne": []}}},
            {"$sort": {"date": -1}},
            {"$limit": 1},
            {"$project": {
                "date": 1,
                "period": 1,
                "type": 1,
                "generatedAt": 1,
                "total": {"$size": "$items"},
                "items": {"$slice": ["$items", start, limit]}
            }}
        ]
        
        cursor = db.leaderboards.aggregate(pipeline)
        leaderboards = await cursor.to_list(length=None)
        
        if leaderboards:
            leaderboard = leaderboards[0]
            logger.info(f"[LEADERBOARD] Returning {len(leaderboard['items'])} items (from {start}) out of {leaderboard['total']} total for date {leaderboard['date']}")
            
            result = serialize_mongo_doc({
                **leaderboard,
                'start': start,
                'limit': limit
            })
        else:
            logger.info(f"[LEADERBOARD] No leaderboard with items found")
            result = {"items": [], "total": 0, "start": start, "limit": limit}
    else:
        return {"error": "Invalid type. Use 'stock' or 'leaderboard'."}
    return {"result": result}

#### Seeding Endpoints ####
@router.post("/admin/seed/instruments")
async def seed_instruments_route():
    await seed_instruments()
    return {"status": "ok"}

@router.post("/admin/seed/daily_prices")
async def seed_daily_prices_route():
    await seed_instrument_prices()
    return {"status": "ok"}

@router.post("/admin/seed/leaderboards")
async def seed_leaderboards_route():
    await seed_leaderboards_only()
    return {"status": "ok"}


