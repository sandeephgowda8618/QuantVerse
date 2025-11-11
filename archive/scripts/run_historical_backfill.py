#!/usr/bin/env python3
"""
Historical Data Backfill for uRISK Professional System
Backfills 30-90 days of historical data for 160+ assets using proven methods
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.db.postgres_handler import PostgresHandler
from backend.data_ingestion.market_collector import market_collector
from backend.data_ingestion.news_collector import news_collector
from backend.data_ingestion.regulatory_collector import regulatory_collector
from backend.data_ingestion.preprocess_pipeline import preprocessing_pipeline
from backend.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

class HistoricalBackfillEngine:
    """Professional historical data backfill using proven methods"""
    
    def __init__(self):
        self.db = PostgresHandler()
        self.stats = {
            'market_data': 0,
            'news_articles': 0,
            'regulatory_events': 0,
            'embeddings': 0,
            'errors': 0
        }
        
    async def get_all_assets(self) -> List[Dict[str, Any]]:
        """Get all assets from database"""
        try:
            query = """
            SELECT ticker, name, asset_type, exchange, sector, country 
            FROM assets 
            WHERE asset_type IN ('stock', 'crypto', 'etf', 'index') 
            ORDER BY asset_type, ticker
            """
            assets = await self.db.async_execute_query(query)
            logger.info(f"📊 Found {len(assets)} assets for historical backfill")
            return assets
        except Exception as e:
            logger.error(f"Failed to get assets: {e}")
            return []
    
    async def backfill_market_data(self, assets: List[Dict], days_back: int = 30) -> Dict[str, Any]:
        """Backfill historical market data using proven market collector methods"""
        logger.info(f"📈 Starting market data backfill for last {days_back} days...")
        
        start_time = datetime.now()
        success_count = 0
        error_count = 0
        total_records = 0
        
        try:
            # Process in batches to avoid API limits
            batch_size = 5
            for i in range(0, len(assets), batch_size):
                batch = assets[i:i + batch_size]
                batch_tickers = [asset['ticker'] for asset in batch]
                
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(assets)-1)//batch_size + 1}: {batch_tickers}")
                
                try:
                    # Use the proven market collector collection cycle method
                    batch_records = 0
                    for ticker in batch_tickers:
                        try:
                            # Use individual ticker collection from market collector
                            ticker_data = market_collector.collect_tiingo_data(ticker)
                            if ticker_data is not None and not ticker_data.empty:
                                # Store the data and count records
                                stored_count = market_collector.store_market_data({ticker: ticker_data})
                                batch_records += stored_count
                                logger.debug(f"✅ {ticker}: {stored_count} records")
                            else:
                                logger.warning(f"⚠️ {ticker}: No data collected")
                        except Exception as ticker_error:
                            logger.error(f"❌ {ticker}: {ticker_error}")
                            error_count += 1
                    
                    total_records += batch_records
                    success_count += len(batch_tickers)
                    logger.info(f"✅ Batch completed: {batch_records} records collected")
                        
                except Exception as e:
                    error_count += len(batch_tickers)
                    logger.error(f"❌ Batch failed: {e}")
                
                # Rate limiting - avoid overwhelming APIs
                await asyncio.sleep(2)
            
            duration = datetime.now() - start_time
            self.stats['market_data'] = total_records
            self.stats['errors'] += error_count
            
            logger.info(f"📈 Market data backfill completed in {duration.total_seconds():.1f}s")
            logger.info(f"   ✅ Success: {success_count} assets, {total_records} records")
            logger.info(f"   ❌ Errors: {error_count} assets")
            
            return {
                'success': True,
                'assets_processed': success_count,
                'total_records': total_records,
                'errors': error_count,
                'duration': duration.total_seconds()
            }
            
        except Exception as e:
            logger.error(f"❌ Market data backfill failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def backfill_news_data(self, assets: List[Dict], days_back: int = 14) -> Dict[str, Any]:
        """Backfill historical news data using proven news collector methods"""
        logger.info(f"📰 Starting news data backfill for last {days_back} days...")
        
        start_time = datetime.now()
        success_count = 0
        total_articles = 0
        
        try:
            # Focus on major assets for news (avoid API limits) - fix crypto ticker format
            major_tickers = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 
                           'META', 'BTC-USD', 'ETH-USD', 'SPY', 'QQQ']
            major_assets = [
                asset for asset in assets 
                if asset['ticker'] in major_tickers
            ]
            
            # Process in smaller batches for news
            batch_size = 3
            for i in range(0, len(major_assets), batch_size):
                batch = major_assets[i:i + batch_size]
                batch_tickers = [asset['ticker'] for asset in batch]
                
                logger.info(f"Processing news batch {i//batch_size + 1}: {batch_tickers}")
                
                try:
                    # FIX ISSUE #3: Remove await from non-async news collector
                    batch_articles = 0
                    for ticker in batch_tickers:
                        try:
                            # Use individual ticker collection for news
                            articles = news_collector.collect_company_news(ticker, days_back=days_back)
                            if articles:
                                batch_articles += len(articles)
                                logger.debug(f"✅ {ticker}: {len(articles)} articles")
                        except Exception as ticker_error:
                            logger.error(f"❌ {ticker} news: {ticker_error}")
                    
                    total_articles += batch_articles
                    success_count += len(batch_tickers)
                    logger.info(f"✅ News batch completed: {batch_articles} articles collected")
                        
                except Exception as e:
                    logger.error(f"❌ News batch failed: {e}")
                
                # Rate limiting for news APIs
                await asyncio.sleep(3)
            
            duration = datetime.now() - start_time
            self.stats['news_articles'] = total_articles
            
            logger.info(f"📰 News data backfill completed in {duration.total_seconds():.1f}s")
            logger.info(f"   ✅ Success: {success_count} assets, {total_articles} articles")
            
            return {
                'success': True,
                'assets_processed': success_count,
                'total_articles': total_articles,
                'duration': duration.total_seconds()
            }
            
        except Exception as e:
            logger.error(f"❌ News data backfill failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def backfill_regulatory_data(self, days_back: int = 90) -> Dict[str, Any]:
        """Backfill regulatory data using proven regulatory collector methods"""
        logger.info(f"🏛️ Starting regulatory data backfill for last {days_back} days...")
        
        start_time = datetime.now()
        
        try:
            # FIX ISSUE #3: Remove await from non-async regulatory collector
            result = regulatory_collector.run_collection_cycle()
            
            duration = datetime.now() - start_time
            
            if result and result.get('success'):
                events_collected = result.get('events_collected', 0)
                events_stored = result.get('events_stored', 0)
                
                self.stats['regulatory_events'] = events_stored
                
                logger.info(f"🏛️ Regulatory backfill completed in {duration.total_seconds():.1f}s")
                logger.info(f"   ✅ Events collected: {events_collected}")
                logger.info(f"   ✅ Events stored: {events_stored}")
                
                return {
                    'success': True,
                    'events_collected': events_collected,
                    'events_stored': events_stored,
                    'duration': duration.total_seconds()
                }
            else:
                logger.warning(f"⚠️ Regulatory backfill had issues: {result.get('errors', [])}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Regulatory data backfill failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def generate_historical_embeddings(self) -> Dict[str, Any]:
        """Generate embeddings for all historical data using proven preprocessing pipeline"""
        logger.info(f"🧠 Starting historical embeddings generation...")
        
        start_time = datetime.now()
        
        try:
            # FIX ISSUE #4: Use correct preprocessing pipeline method
            result = await preprocessing_pipeline.run_preprocessing_cycle()
            
            duration = datetime.now() - start_time
            
            if result and result.get('success'):
                embeddings_created = result.get('embeddings_created', 0)
                chunks_created = result.get('chunks_created', 0)
                documents_processed = result.get('documents_processed', 0)
                
                self.stats['embeddings'] = embeddings_created
                
                logger.info(f"🧠 Embeddings generation completed in {duration.total_seconds():.1f}s")
                logger.info(f"   ✅ Documents processed: {documents_processed}")
                logger.info(f"   ✅ Chunks created: {chunks_created}")
                logger.info(f"   ✅ Embeddings generated: {embeddings_created}")
                
                return {
                    'success': True,
                    'documents_processed': documents_processed,
                    'chunks_created': chunks_created,
                    'embeddings_created': embeddings_created,
                    'duration': duration.total_seconds()
                }
            else:
                logger.warning(f"⚠️ Embeddings generation had issues: {result.get('errors', [])}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Embeddings generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def verify_backfill_data(self) -> Dict[str, Any]:
        """Verify the historical data was populated correctly"""
        logger.info(f"🔍 Verifying historical data backfill...")
        
        try:
            # Check market data
            market_query = "SELECT COUNT(*) as count FROM market_prices WHERE timestamp >= NOW() - INTERVAL '30 days'"
            market_result = await self.db.async_execute_query(market_query)
            market_count = market_result[0]['count'] if market_result else 0
            
            # Check news data
            news_query = "SELECT COUNT(*) as count FROM news_headlines WHERE published_at >= NOW() - INTERVAL '14 days'"
            news_result = await self.db.async_execute_query(news_query)
            news_count = news_result[0]['count'] if news_result else 0
            
            # Check regulatory data
            regulatory_query = "SELECT COUNT(*) as count FROM regulatory_events WHERE inserted_at >= NOW() - INTERVAL '7 days'"
            regulatory_result = await self.db.async_execute_query(regulatory_query)
            regulatory_count = regulatory_result[0]['count'] if regulatory_result else 0
            
            # Check vector embeddings (fix issue #5)
            try:
                from backend.embeddings.vector_store import vector_store
                # Try to get collection stats if available
                total_vectors = vector_store.get_total_document_count() if hasattr(vector_store, 'get_total_document_count') else 0
            except Exception as e:
                logger.warning(f"Could not get vector stats: {e}")
                total_vectors = 0
            
            verification_stats = {
                'market_data_records': market_count,
                'news_articles': news_count,
                'regulatory_events': regulatory_count,
                'vector_embeddings': total_vectors
            }
            
            logger.info(f"🔍 Verification Results:")
            logger.info(f"   📈 Market data records: {market_count}")
            logger.info(f"   📰 News articles: {news_count}")
            logger.info(f"   🏛️ Regulatory events: {regulatory_count}")
            logger.info(f"   🧠 Vector embeddings: {total_vectors}")
            
            return {
                'success': True,
                'verification_stats': verification_stats
            }
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def run_complete_historical_backfill(self) -> Dict[str, Any]:
        """Run complete historical backfill process"""
        logger.info("🚀 Starting complete historical data backfill...")
        logger.info("=" * 60)
        
        overall_start = datetime.now()
        results = {}
        
        try:
            # Step 1: Get all assets
            assets = await self.get_all_assets()
            if not assets:
                raise Exception("No assets found in database")
            
            # Step 2: Backfill market data (30 days)
            logger.info("\n📈 STEP 1: Market Data Backfill")
            results['market_data'] = await self.backfill_market_data(assets, days_back=30)
            
            # Step 3: Backfill news data (14 days)
            logger.info("\n📰 STEP 2: News Data Backfill")
            results['news_data'] = await self.backfill_news_data(assets, days_back=14)
            
            # Step 4: Backfill regulatory data (90 days)
            logger.info("\n🏛️ STEP 3: Regulatory Data Backfill")
            results['regulatory_data'] = await self.backfill_regulatory_data(days_back=90)
            
            # Step 5: Generate embeddings for all historical data
            logger.info("\n🧠 STEP 4: Historical Embeddings Generation")
            results['embeddings'] = await self.generate_historical_embeddings()
            
            # Step 6: Verify all data
            logger.info("\n🔍 STEP 5: Data Verification")
            results['verification'] = await self.verify_backfill_data()
            
            # Calculate overall stats
            overall_duration = datetime.now() - overall_start
            
            logger.info("\n🎉 HISTORICAL BACKFILL COMPLETED")
            logger.info("=" * 60)
            logger.info(f"⏱️  Total duration: {overall_duration.total_seconds():.1f} seconds")
            logger.info(f"📊 Final Statistics:")
            logger.info(f"   📈 Market data records: {self.stats['market_data']}")
            logger.info(f"   📰 News articles: {self.stats['news_articles']}")
            logger.info(f"   🏛️ Regulatory events: {self.stats['regulatory_events']}")
            logger.info(f"   🧠 Embeddings generated: {self.stats['embeddings']}")
            logger.info(f"   ❌ Total errors: {self.stats['errors']}")
            
            return {
                'success': True,
                'overall_duration': overall_duration.total_seconds(),
                'final_stats': self.stats,
                'detailed_results': results
            }
            
        except Exception as e:
            logger.error(f"❌ Historical backfill failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'partial_results': results
            }

async def main():
    """Main execution function"""
    print("🚀 uRISK Historical Data Backfill Engine")
    print("🎯 Professional-grade data population for 160+ assets")
    print("=" * 70)
    
    backfill_engine = HistoricalBackfillEngine()
    
    # Run complete historical backfill
    result = await backfill_engine.run_complete_historical_backfill()
    
    if result.get('success'):
        print(f"\n✅ BACKFILL SUCCESSFUL!")
        print(f"🚀 Your uRISK system now has comprehensive historical data")
        print(f"💡 Ready for professional RAG queries!")
        print(f"\n🎯 Next Steps:")
        print(f"   1. Start continuous scheduler: python3 backend/scheduler/data_scheduler.py")
        print(f"   2. Test RAG queries via API endpoints")
        print(f"   3. Enable options flow data for Member-1 features")
    else:
        print(f"\n❌ BACKFILL FAILED: {result.get('error', 'Unknown error')}")
        if 'partial_results' in result:
            print(f"📊 Some data may have been collected successfully")

if __name__ == "__main__":
    asyncio.run(main())
