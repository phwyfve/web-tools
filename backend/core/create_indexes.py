"""
Create MongoDB indexes for better performance on leaderboard queries.
"""
import asyncio
from .database import get_database

async def create_indexes():
    db = get_database()
    
    print("Creating indexes on daily_metrics collection...")
    
    # Index for leaderboard queries (date + period fields)
    periods = ["5d", "1M", "2M", "3M", "6M", "52w"]
    
    for period in periods:
        # Index for gainers (change_pct_from_low)
        await db.daily_metrics.create_index([
            ("date", 1),
            (f"change_pct_from_low_{period}", -1)
        ], name=f"leaderboard_gainers_{period}")
        
        # Index for losers (change_pct_from_high)
        await db.daily_metrics.create_index([
            ("date", 1),
            (f"change_pct_from_high_{period}", 1)
        ], name=f"leaderboard_losers_{period}")
    
    # Index for market movers (volume)
    await db.daily_metrics.create_index([
        ("date", 1),
        ("volume", -1)
    ], name="leaderboard_volume")
    
    # Index for daily_bars queries
    await db.daily_bars.create_index([
        ("instrumentId", 1),
        ("date", 1)
    ], name="bars_by_instrument_date")
    
    # Index for leaderboards queries
    await db.leaderboards.create_index([
        ("period", 1),
        ("type", 1),
        ("date", -1)
    ], name="leaderboard_lookup")
    
    print("✓ All indexes created successfully!")
    print("\nIndexes on daily_metrics:")
    indexes = await db.daily_metrics.list_indexes().to_list(length=None)
    for idx in indexes:
        print(f"  - {idx['name']}")

if __name__ == "__main__":
    asyncio.run(create_indexes())
