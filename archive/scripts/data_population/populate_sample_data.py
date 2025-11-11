#!/usr/bin/env python3
"""
Quick Sample Data Population for Testing
Populates minimal sample data to test all API endpoints immediately
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import random

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.db.postgres_handler import PostgresHandler

async def populate_sample_data():
    """Populate sample data for immediate API testing"""
    db = PostgresHandler()
    
    print("🌟 Populating sample data for API testing...")
    
    try:
        # Sample news headlines
        headlines_data = [
            ("AAPL", "Apple Reports Strong Q4 Earnings", "Reuters", datetime.now() - timedelta(hours=2)),
            ("AAPL", "Apple Stock Rises on New iPhone Sales", "Bloomberg", datetime.now() - timedelta(hours=5)),
            ("TSLA", "Tesla Announces New Gigafactory", "CNBC", datetime.now() - timedelta(hours=3)),
            ("BTC", "Bitcoin Reaches New All-Time High", "CoinDesk", datetime.now() - timedelta(hours=1)),
            ("NVDA", "NVIDIA AI Chip Demand Surges", "TechCrunch", datetime.now() - timedelta(hours=4)),
        ]
        
        for ticker, headline, source, published_at in headlines_data:
            await db.async_execute_query("""
                INSERT INTO news_headlines (ticker, headline, source, published_at)
                VALUES ($1, $2, $3, $4)
            """, (ticker, headline, source, published_at))
        
        print(f"✅ Inserted {len(headlines_data)} news headlines")
        
        # Sample sentiment scores
        sentiment_data = [
            (1, 0.8, datetime.now() - timedelta(hours=2)),
            (2, 0.6, datetime.now() - timedelta(hours=5)),
            (3, 0.7, datetime.now() - timedelta(hours=3)),
            (4, 0.9, datetime.now() - timedelta(hours=1)),
            (5, 0.5, datetime.now() - timedelta(hours=4)),
        ]
        
        for headline_id, sentiment_score, timestamp in sentiment_data:
            await db.async_execute_query("""
                INSERT INTO news_sentiment (headline_id, sentiment_score, timestamp)
                VALUES ($1, $2, $3)
            """, (headline_id, sentiment_score, timestamp))
        
        print(f"✅ Inserted {len(sentiment_data)} sentiment scores")
        
        # Sample regulatory events
        regulatory_data = [
            ("AAPL", "SEC Files Investigation", "SEC", datetime.now() - timedelta(days=1)),
            ("TSLA", "DOT Safety Review", "DOT", datetime.now() - timedelta(days=2)),
            ("BTC", "Treasury Crypto Guidelines", "Treasury", datetime.now() - timedelta(hours=12)),
        ]
        
        for ticker, title, source, published_at in regulatory_data:
            await db.async_execute_query("""
                INSERT INTO regulatory_events (ticker, title, source, published_at)
                VALUES ($1, $2, $3, $4)
            """, (ticker, title, source, published_at))
        
        print(f"✅ Inserted {len(regulatory_data)} regulatory events")
        
        # Sample anomalies
        anomaly_data = [
            ("AAPL", "price_jump", "high", 0.85, "Unusual 5% price increase in 10 minutes", datetime.now() - timedelta(hours=3)),
            ("TSLA", "volume_spike", "medium", 0.72, "Trading volume 3x above average", datetime.now() - timedelta(hours=6)),
            ("BTC", "volatility", "high", 0.91, "Extreme volatility detected", datetime.now() - timedelta(hours=1)),
            ("NVDA", "price_drop", "medium", 0.68, "Significant price drop detected", datetime.now() - timedelta(hours=2)),
        ]
        
        for ticker, metric, severity, anomaly_score, explanation, timestamp in anomaly_data:
            await db.async_execute_query("""
                INSERT INTO anomalies (ticker, metric, severity, anomaly_score, explanation, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, (ticker, metric, severity, anomaly_score, explanation, timestamp))
        
        print(f"✅ Inserted {len(anomaly_data)} anomalies")
        
        # Sample infrastructure status (using actual table structure)
        infra_data = [
            ("market_data_api", "healthy", "All market data feeds operational", "internal", "low", "SYSTEM"),
            ("news_api", "healthy", "News collection running normally", "internal", "low", "SYSTEM"),
            ("database", "healthy", "PostgreSQL performance optimal", "internal", "low", "SYSTEM"),
            ("vector_store", "warning", "ChromaDB latency slightly elevated", "internal", "medium", "SYSTEM"),
        ]
        
        for service_name, status, description, source, severity, ticker in infra_data:
            await db.async_execute_query("""
                INSERT INTO infrastructure_status (service_name, status, description, source, severity, ticker, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, (service_name, status, description, source, severity, ticker, datetime.now()))
        
        print(f"✅ Inserted {len(infra_data)} infrastructure statuses")
        
        print("\n🎉 Sample data population completed!")
        print("🧪 All API endpoints should now return data for testing")
        
    except Exception as e:
        print(f"❌ Sample data population failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(populate_sample_data())
