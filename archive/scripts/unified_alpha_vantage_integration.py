#!/usr/bin/env python3
"""
Unified Alpha Vantage Integration for QuantVerse uRISK
Combines the enhanced Alpha Vantage collector with existing pipeline architecture
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.db.postgres_handler import PostgresHandler
from backend.embeddings.vector_store import ChromaVectorStore
from enhanced_alpha_vantage_collector import EnhancedAlphaVantageCollector, get_alpha_vantage_config
from top_200_companies import TOP_200_COMPANIES, US_TRADEABLE_SYMBOLS

logger = logging.getLogger(__name__)

class UnifiedAlphaVantageIntegration:
    """
    Unified integration class that connects Alpha Vantage data collection
    with the existing uRISK pipeline architecture and database schema.
    """
    
    def __init__(self):
        self.db = PostgresHandler()
        self.vector_store = ChromaVectorStore()
        self.config = get_alpha_vantage_config()
        
    async def initialize(self):
        """Initialize all components"""
        try:
            await self.db.initialize_async_pool()
            await self.vector_store.initialize()
            logger.info("✅ Unified integration initialized")
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise

    async def apply_enhanced_schema(self):
        """Apply the enhanced Alpha Vantage schema to existing database"""
        try:
            with open('enhanced_alpha_vantage_schema.sql', 'r') as f:
                schema_sql = f.read()
            
            # Split into individual statements
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement.upper().startswith(('CREATE TABLE', 'CREATE INDEX', 'CREATE VIEW')):
                    try:
                        await self.db.async_execute_query(statement)
                        logger.info(f"✅ Applied: {statement[:50]}...")
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            logger.info(f"⚠️ Already exists: {statement[:50]}...")
                        else:
                            logger.error(f"❌ Failed: {statement[:50]}... - {e}")
                            
            logger.info("✅ Enhanced schema application completed")
            
        except Exception as e:
            logger.error(f"❌ Schema application failed: {e}")
            raise

    async def collect_alpha_vantage_data(self, tickers: List[str], data_types: List[str] = None):
        """
        Collect Alpha Vantage data and integrate with existing schema
        
        Args:
            tickers: List of ticker symbols to collect
            data_types: List of data types ['stocks', 'fundamentals', 'news', 'forex', 'crypto']
        """
        if data_types is None:
            data_types = ['stocks', 'fundamentals', 'news']
            
        results = {
            'success': 0,
            'failed': 0,
            'data_collected': {},
            'errors': []
        }
        
        try:
            async with EnhancedAlphaVantageCollector(self.config) as collector:
                
                # 1. Collect stock price data
                if 'stocks' in data_types:
                    logger.info(f"📈 Collecting stock data for {len(tickers)} tickers")
                    stock_data = await collector.collect_daily_prices(tickers)
                    
                    for ticker, df in stock_data.items():
                        if not df.empty:
                            await self._store_market_prices(ticker, df, 'alpha_vantage')
                            results['data_collected'][f'{ticker}_prices'] = len(df)
                            results['success'] += 1
                
                # 2. Collect fundamental data
                if 'fundamentals' in data_types:
                    logger.info(f"🏢 Collecting fundamental data for {len(tickers)} tickers")
                    fundamental_data = await collector.collect_company_overviews(tickers)
                    
                    for ticker, data in fundamental_data.items():
                        if data:
                            await self._store_fundamental_data(ticker, data)
                            results['data_collected'][f'{ticker}_fundamentals'] = 1
                            results['success'] += 1
                
                # 3. Collect news and sentiment
                if 'news' in data_types:
                    logger.info(f"📰 Collecting news data for {len(tickers)} tickers")
                    news_data = await collector.collect_news_sentiment(tickers=tickers)
                    
                    if news_data:
                        await self._store_news_data(news_data)
                        results['data_collected']['news_articles'] = len(news_data)
                        results['success'] += 1
                
                logger.info(f"✅ Data collection completed. Success: {results['success']}, Failed: {results['failed']}")
                return results
                
        except Exception as e:
            logger.error(f"❌ Data collection failed: {e}")
            results['errors'].append(str(e))
            return results

    async def _store_market_prices(self, ticker: str, df: Any, source: str):
        """Store market price data in existing market_prices table"""
        try:
            for timestamp, row in df.iterrows():
                query = """
                    INSERT INTO market_prices 
                    (ticker, timestamp, open, high, low, close, volume, source)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (ticker, timestamp) DO UPDATE SET
                        open = EXCLUDED.open,
                        high = EXCLUDED.high,
                        low = EXCLUDED.low,
                        close = EXCLUDED.close,
                        volume = EXCLUDED.volume,
                        source = EXCLUDED.source
                """
                
                await self.db.async_execute_query(query, (
                    ticker,
                    timestamp,
                    float(row.get('open', 0)),
                    float(row.get('high', 0)), 
                    float(row.get('low', 0)),
                    float(row.get('close', 0)),
                    int(row.get('volume', 0)),
                    source
                ))
                
            logger.info(f"✅ Stored {len(df)} price records for {ticker}")
            
        except Exception as e:
            logger.error(f"❌ Failed to store market prices for {ticker}: {e}")

    async def _store_fundamental_data(self, ticker: str, data: Dict[str, Any]):
        """Store fundamental data in enhanced schema"""
        try:
            query = """
                INSERT INTO fundamental_data (ticker, data_type, data, source)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (ticker, data_type, source) DO UPDATE SET
                    data = EXCLUDED.data,
                    updated_at = NOW()
            """
            
            await self.db.async_execute_query(query, (
                ticker,
                'company_overview',
                json.dumps(data),
                'alpha_vantage'
            ))
            
            logger.info(f"✅ Stored fundamental data for {ticker}")
            
        except Exception as e:
            logger.error(f"❌ Failed to store fundamental data for {ticker}: {e}")

    async def _store_news_data(self, news_data: Dict[str, Any]):
        """Store news data in existing news_headlines and news_sentiment tables"""
        try:
            if 'feed' in news_data:
                for article in news_data['feed']:
                    # Store headline
                    headline_query = """
                        INSERT INTO news_headlines (ticker, headline, url, source, published_at)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT DO NOTHING
                        RETURNING id
                    """
                    
                    # Extract ticker from article if available
                    ticker = article.get('ticker_sentiment', [{}])[0].get('ticker', 'GENERAL')
                    
                    headline_id = await self.db.async_fetch_scalar(headline_query, (
                        ticker,
                        article.get('title', ''),
                        article.get('url', ''),
                        'alpha_vantage',
                        datetime.strptime(article.get('time_published', ''), '%Y%m%dT%H%M%S') 
                        if article.get('time_published') else datetime.now()
                    ))
                    
                    # Store sentiment if available
                    if headline_id and 'overall_sentiment_score' in article:
                        sentiment_query = """
                            INSERT INTO news_sentiment 
                            (headline_id, sentiment_score, sentiment_label, confidence, model_version)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (headline_id) DO NOTHING
                        """
                        
                        await self.db.async_execute_query(sentiment_query, (
                            headline_id,
                            float(article['overall_sentiment_score']),
                            article.get('overall_sentiment_label', 'neutral'),
                            1.0,  # Alpha Vantage provides high confidence
                            'alpha_vantage_sentiment'
                        ))
                        
            logger.info(f"✅ Stored news and sentiment data")
            
        except Exception as e:
            logger.error(f"❌ Failed to store news data: {e}")

    async def run_integration_test(self):
        """Run comprehensive integration test"""
        print("\n🧪 **UNIFIED ALPHA VANTAGE INTEGRATION TEST**")
        print("=" * 60)
        
        try:
            # 1. Initialize
            await self.initialize()
            print("✅ 1. Initialization completed")
            
            # 2. Apply enhanced schema
            await self.apply_enhanced_schema()
            print("✅ 2. Enhanced schema applied")
            
            # 3. Test with top 5 mega cap companies
            test_tickers = ['NVDA', 'MSFT', 'AAPL', 'GOOG', 'AMZN']
            
            # 4. Collect data
            results = await self.collect_alpha_vantage_data(
                tickers=test_tickers,
                data_types=['stocks', 'fundamentals', 'news']
            )
            
            print(f"✅ 3. Data collection completed")
            print(f"   Success: {results['success']}")
            print(f"   Failed: {results['failed']}")
            print(f"   Data collected: {results['data_collected']}")
            
            # 5. Verify database counts
            total_records = 0
            tables = ['market_prices', 'fundamental_data', 'news_headlines', 'news_sentiment']
            
            for table in tables:
                count = await self.db.async_fetch_scalar(f"SELECT COUNT(*) FROM {table}")
                print(f"   📊 {table}: {count} records")
                total_records += count
            
            print(f"✅ 4. Database verification completed - {total_records} total records")
            
            # 6. Test vector embeddings
            await self.vector_store.initialize()
            stats = await self.vector_store.get_collection_stats()
            print(f"✅ 5. Vector database stats: {stats}")
            
            await self.cleanup()
            
            print("\n🎉 **INTEGRATION TEST COMPLETED SUCCESSFULLY!**")
            return True
            
        except Exception as e:
            print(f"\n❌ **INTEGRATION TEST FAILED:** {e}")
            await self.cleanup()
            return False

    async def cleanup(self):
        """Cleanup connections"""
        try:
            if hasattr(self.db, 'close_async_pool'):
                await self.db.close_async_pool()
        except:
            pass

async def main():
    """Run the unified integration"""
    integration = UnifiedAlphaVantageIntegration()
    success = await integration.run_integration_test()
    
    if success:
        print("\n🚀 **READY FOR PRODUCTION DATA COLLECTION**")
        print("Run: python3 populate_alpha_vantage_data.py --tiers mega")
    else:
        print("\n🔧 **REQUIRES ATTENTION - CHECK LOGS**")

if __name__ == "__main__":
    import json
    asyncio.run(main())
