"""
Historical Data Backfill Pipeline for uRISK
Backfills 30-90 days of historical data for all assets to improve RAG accuracy and ML model performance.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.postgres_handler import db
from backend.data_ingestion.market_collector import MarketDataCollector
from backend.data_ingestion.news_collector import NewsCollector
from backend.data_ingestion.regulatory_collector import RegulatoryCollector
from backend.data_ingestion.preprocess_pipeline import PreprocessingPipeline
from backend.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

class HistoricalBackfillPipeline:
    """Backfills historical data for comprehensive RAG and ML training."""
    
    def __init__(self, days_back: int = 90):
        self.days_back = days_back
        self.market_collector = MarketDataCollector()
        self.news_collector = NewsCollector()
        self.regulatory_collector = RegulatoryCollector()
        self.preprocessor = PreprocessingPipeline()
        
    async def get_all_assets(self) -> List[Dict[str, Any]]:
        """Get all assets from the database."""
        query = """
            SELECT ticker, name, asset_type, exchange, sector, country
            FROM assets
            ORDER BY asset_type, ticker
        """
        return await db.fetch_all(query)
    
    async def backfill_market_prices(self, assets: List[Dict[str, Any]]) -> Dict[str, int]:
        """Backfill historical market prices for all assets."""
        logger.info(f"🏦 Starting historical market price backfill for {len(assets)} assets...")
        
        results = {"success": 0, "failed": 0, "total_records": 0}
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.days_back)
        
        for asset in assets:
            ticker = asset['ticker']
            asset_type = asset['asset_type']
            
            try:
                logger.info(f"📈 Backfilling {ticker} ({asset_type}) from {start_date.date()} to {end_date.date()}")
                
                # Get historical data based on asset type
                if asset_type == 'crypto':
                    # Use CoinGecko for crypto historical data
                    historical_data = await self._fetch_crypto_historical(ticker, start_date, end_date)
                else:
                    # Use yfinance/Tiingo for stocks, indices, etc.
                    historical_data = await self._fetch_stock_historical(ticker, start_date, end_date)
                
                if historical_data:
                    # Store in database
                    stored_count = await self._store_historical_prices(ticker, historical_data)
                    results["total_records"] += stored_count
                    results["success"] += 1
                    logger.info(f"✅ {ticker}: {stored_count} historical records stored")
                else:
                    results["failed"] += 1
                    logger.warning(f"⚠️ {ticker}: No historical data available")
                    
            except Exception as e:
                results["failed"] += 1
                logger.error(f"❌ {ticker}: Historical backfill failed - {e}")
        
        logger.info(f"🏦 Market price backfill completed: {results['success']} success, {results['failed']} failed, {results['total_records']} total records")
        return results
    
    async def _fetch_stock_historical(self, ticker: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch historical stock data using yfinance."""
        try:
            import yfinance as yf
            
            # Download historical data
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date, interval="1d")
            
            if hist.empty:
                return []
            
            # Convert to list of dicts
            historical_data = []
            for date, row in hist.iterrows():
                historical_data.append({
                    'timestamp': date.tz_localize(None) if date.tz else date,
                    'open': float(row['Open']) if pd.notna(row['Open']) else None,
                    'high': float(row['High']) if pd.notna(row['High']) else None,
                    'low': float(row['Low']) if pd.notna(row['Low']) else None,
                    'close': float(row['Close']) if pd.notna(row['Close']) else None,
                    'volume': int(row['Volume']) if pd.notna(row['Volume']) else 0,
                    'source': 'yfinance_historical'
                })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Failed to fetch historical data for {ticker}: {e}")
            return []
    
    async def _fetch_crypto_historical(self, ticker: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch historical crypto data."""
        try:
            # Extract crypto symbol from ticker (e.g., 'BTC-USD' -> 'bitcoin')
            crypto_map = {
                'BTC-USD': 'bitcoin',
                'ETH-USD': 'ethereum',
                'ADA-USD': 'cardano',
                'SOL-USD': 'solana',
                'DOT-USD': 'polkadot',
                'BNB-USD': 'binancecoin',
                'XRP-USD': 'ripple',
                'DOGE-USD': 'dogecoin',
                'MATIC-USD': 'matic-network',
                'AVAX-USD': 'avalanche-2',
                'LINK-USD': 'chainlink',
                'UNI-USD': 'uniswap'
            }
            
            if ticker not in crypto_map:
                # Fallback to yfinance for crypto
                return await self._fetch_stock_historical(ticker, start_date, end_date)
            
            coin_id = crypto_map[ticker]
            
            # Use CoinGecko API for historical crypto data
            import requests
            
            # Convert dates to timestamps
            start_timestamp = int(start_date.timestamp())
            end_timestamp = int(end_date.timestamp())
            
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
            params = {
                'vs_currency': 'usd',
                'from': start_timestamp,
                'to': end_timestamp
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code != 200:
                return await self._fetch_stock_historical(ticker, start_date, end_date)
            
            data = response.json()
            
            # Process price data
            historical_data = []
            prices = data.get('prices', [])
            volumes = data.get('total_volumes', [])
            
            for i, (timestamp_ms, price) in enumerate(prices):
                volume = volumes[i][1] if i < len(volumes) else 0
                
                historical_data.append({
                    'timestamp': datetime.fromtimestamp(timestamp_ms / 1000),
                    'open': float(price),
                    'high': float(price),
                    'low': float(price),
                    'close': float(price),
                    'volume': int(volume),
                    'source': 'coingecko_historical'
                })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Failed to fetch crypto historical data for {ticker}: {e}")
            # Fallback to yfinance
            return await self._fetch_stock_historical(ticker, start_date, end_date)
    
    async def _store_historical_prices(self, ticker: str, historical_data: List[Dict]) -> int:
        """Store historical price data in database."""
        if not historical_data:
            return 0
        
        # Prepare data for bulk insert
        columns = ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'source']
        data = []
        
        for record in historical_data:
            data.append((
                ticker,
                record['timestamp'],
                record['open'],
                record['high'],
                record['low'],
                record['close'],
                record['volume'],
                record['source']
            ))
        
        # Use bulk upsert to avoid duplicates
        return db.bulk_upsert(
            table='market_prices',
            columns=columns,
            data=data,
            conflict_columns=['ticker', 'timestamp'],
            update_columns=['open', 'high', 'low', 'close', 'volume', 'source']
        )
    
    async def backfill_news_data(self, assets: List[Dict[str, Any]]) -> Dict[str, int]:
        """Backfill historical news data for major assets."""
        logger.info(f"📰 Starting historical news backfill...")
        
        results = {"success": 0, "failed": 0, "total_articles": 0}
        
        # Focus on major assets for news backfill (to avoid API limits)
        major_assets = [
            asset for asset in assets 
            if asset['ticker'] in [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META',
                'BTC-USD', 'ETH-USD', 'SPY', 'QQQ', 
                'RELIANCE.NS', 'TCS.NS', 'INFY.NS'
            ]
        ]
        
        for asset in major_assets:
            ticker = asset['ticker']
            try:
                logger.info(f"📰 Backfilling news for {ticker}")
                
                # Use news collector to get historical articles
                articles = await self._fetch_historical_news(ticker, days_back=14)
                
                if articles:
                    stored_count = len(articles)
                    results["total_articles"] += stored_count
                    results["success"] += 1
                    logger.info(f"✅ {ticker}: {stored_count} historical articles stored")
                else:
                    results["failed"] += 1
                    logger.warning(f"⚠️ {ticker}: No historical news available")
                    
            except Exception as e:
                results["failed"] += 1
                logger.error(f"❌ {ticker}: News backfill failed - {e}")
        
        logger.info(f"📰 News backfill completed: {results['success']} success, {results['failed']} failed, {results['total_articles']} total articles")
        return results
    
    async def _fetch_historical_news(self, ticker: str, days_back: int = 14) -> List[Dict]:
        """Fetch historical news for a ticker."""
        try:
            # Use the existing news collector
            articles = await self.news_collector.collect_company_news(ticker)
            return articles
        except Exception as e:
            logger.error(f"Failed to fetch historical news for {ticker}: {e}")
            return []
    
    async def backfill_regulatory_data(self) -> Dict[str, int]:
        """Backfill regulatory events for the past 90 days."""
        logger.info("🏛️ Starting regulatory data backfill...")
        
        try:
            # Use existing regulatory collector
            regulatory_results = await self.regulatory_collector.collect_all_regulatory_data()
            
            logger.info(f"✅ Regulatory backfill completed: {regulatory_results.get('total_collected', 0)} events")
            return {"success": 1, "total_events": regulatory_results.get('total_collected', 0)}
            
        except Exception as e:
            logger.error(f"❌ Regulatory backfill failed: {e}")
            return {"success": 0, "total_events": 0}
    
    async def generate_embeddings(self) -> Dict[str, int]:
        """Generate embeddings for all historical data."""
        logger.info("🧠 Starting historical embedding generation...")
        
        try:
            # Use preprocessing pipeline to generate embeddings
            embedding_results = await self.preprocessor.process_all_data()
            
            total_embeddings = embedding_results.get('embeddings_created', 0)
            logger.info(f"✅ Historical embedding generation completed: {total_embeddings} embeddings")
            
            return {"success": 1, "total_embeddings": total_embeddings}
            
        except Exception as e:
            logger.error(f"❌ Historical embedding generation failed: {e}")
            return {"success": 0, "total_embeddings": 0}
    
    async def run_complete_backfill(self) -> Dict[str, Any]:
        """Run the complete historical backfill pipeline."""
        start_time = datetime.now()
        logger.info(f"🚀 Starting comprehensive historical backfill ({self.days_back} days)")
        
        # Get all assets
        assets = await self.get_all_assets()
        logger.info(f"📊 Found {len(assets)} assets to backfill")
        
        results = {
            "start_time": start_time.isoformat(),
            "assets_count": len(assets),
            "days_back": self.days_back
        }
        
        # Step 1: Backfill market prices
        market_results = await self.backfill_market_prices(assets)
        results["market_prices"] = market_results
        
        # Step 2: Backfill news data
        news_results = await self.backfill_news_data(assets)
        results["news"] = news_results
        
        # Step 3: Backfill regulatory data
        regulatory_results = await self.backfill_regulatory_data()
        results["regulatory"] = regulatory_results
        
        # Step 4: Generate embeddings
        embedding_results = await self.generate_embeddings()
        results["embeddings"] = embedding_results
        
        # Calculate totals
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        results.update({
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "total_market_records": market_results.get("total_records", 0),
            "total_news_articles": news_results.get("total_articles", 0),
            "total_regulatory_events": regulatory_results.get("total_events", 0),
            "total_embeddings": embedding_results.get("total_embeddings", 0)
        })
        
        logger.info("=" * 60)
        logger.info("HISTORICAL BACKFILL COMPLETED")
        logger.info("=" * 60)
        logger.info(f"⏱️  Duration: {duration:.1f} seconds")
        logger.info(f"📊 Assets processed: {len(assets)}")
        logger.info(f"📈 Market records: {results['total_market_records']}")
        logger.info(f"📰 News articles: {results['total_news_articles']}")
        logger.info(f"🏛️ Regulatory events: {results['total_regulatory_events']}")
        logger.info(f"🧠 Embeddings generated: {results['total_embeddings']}")
        
        return results

async def main():
    """Main entry point for historical backfill."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Historical data backfill for uRISK')
    parser.add_argument('--days', type=int, default=90, help='Number of days to backfill (default: 90)')
    parser.add_argument('--market-only', action='store_true', help='Only backfill market data')
    parser.add_argument('--news-only', action='store_true', help='Only backfill news data')
    parser.add_argument('--embeddings-only', action='store_true', help='Only generate embeddings')
    
    args = parser.parse_args()
    
    # Initialize backfill pipeline
    backfill = HistoricalBackfillPipeline(days_back=args.days)
    
    if args.market_only:
        assets = await backfill.get_all_assets()
        results = await backfill.backfill_market_prices(assets)
        logger.info(f"Market-only backfill completed: {results}")
    elif args.news_only:
        assets = await backfill.get_all_assets()
        results = await backfill.backfill_news_data(assets)
        logger.info(f"News-only backfill completed: {results}")
    elif args.embeddings_only:
        results = await backfill.generate_embeddings()
        logger.info(f"Embeddings-only generation completed: {results}")
    else:
        # Run complete backfill
        results = await backfill.run_complete_backfill()
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
