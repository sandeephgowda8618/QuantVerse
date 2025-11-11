#!/usr/bin/env python3
"""
Alpha Vantage High-Impact Ticker Pipeline - Temporary Add-on
Focused data collection for 35 curated high-impact assets across sectors

This is a TEMPORARY pipeline component designed to be easily detached.
It collects fundamental data and light technical indicators for a balanced
portfolio of high-impact assets across multiple sectors and market regimes.

Usage:
    python run_high_impact_pipeline.py                    # Full collection
    python run_high_impact_pipeline.py --max-tickers 10  # Test with 10 tickers
    python run_high_impact_pipeline.py --sector tech     # Only tech stocks
    python run_high_impact_pipeline.py --resume          # Resume from checkpoint
"""

import asyncio
import argparse
import sys
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Add backend to Python path
sys.path.append(str(Path(__file__).parent / 'backend'))

from backend.config.settings import settings
from backend.data_ingestion.alpha_fetcher import AlphaFetcher
from backend.data_ingestion.alpha_normalizer import AlphaNormalizer
from backend.data_ingestion.alpha_writer import AlphaWriter
from backend.db.postgres_handler import PostgresHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'high_impact_ingestion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class HighImpactPipelineManager:
    """
    Temporary pipeline manager for high-impact tickers
    
    This component is designed to be easily detached from the main pipeline
    when no longer needed. It focuses on fundamental data and key technical
    indicators for a curated set of market-moving assets.
    """
    
    def __init__(self):
        self.session_id = f"high_impact_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.fetcher = AlphaFetcher()
        self.normalizer = AlphaNormalizer()
        self.writer = AlphaWriter()
        self.db = PostgresHandler()
        
        # High-impact ticker universe (35 assets)
        self.high_impact_tickers = {
            # US Tech Giants (9) - NVDA commented out due to sufficient data
            'tech': [
                {'ticker': 'AMZN', 'name': 'Amazon.com', 'priority': 100},
                {'ticker': 'GOOGL', 'name': 'Alphabet Class A', 'priority': 98},
                {'ticker': 'META', 'name': 'Meta Platforms', 'priority': 98},
                {'ticker': 'TSLA', 'name': 'Tesla', 'priority': 97},
                {'ticker': 'AMD', 'name': 'Advanced Micro Devices', 'priority': 95},
                {'ticker': 'AVGO', 'name': 'Broadcom', 'priority': 95},
                {'ticker': 'NFLX', 'name': 'Netflix', 'priority': 94},
                {'ticker': 'AAPL', 'name': 'Apple Inc', 'priority': 100},
                {'ticker': 'MSFT', 'name': 'Microsoft Corp', 'priority': 100},
                # {'ticker': 'NVDA', 'name': 'NVIDIA Corp', 'priority': 100}  # Commented out - sufficient data already ingested
            ],
            
            # Banks & Finance (5)
            'finance': [
                {'ticker': 'JPM', 'name': 'JPMorgan Chase', 'priority': 100},
                {'ticker': 'BAC', 'name': 'Bank of America', 'priority': 95},
                {'ticker': 'GS', 'name': 'Goldman Sachs', 'priority': 92},
                {'ticker': 'WFC', 'name': 'Wells Fargo', 'priority': 90},
                {'ticker': 'MS', 'name': 'Morgan Stanley', 'priority': 90}
            ],
            
            # Energy & Commodities (3)
            'energy': [
                {'ticker': 'XOM', 'name': 'Exxon Mobil', 'priority': 96},
                {'ticker': 'CVX', 'name': 'Chevron', 'priority': 94},
                {'ticker': 'COP', 'name': 'ConocoPhillips', 'priority': 90}
            ],
            
            # Industrials & Defense (4)
            'industrials': [
                {'ticker': 'BA', 'name': 'Boeing', 'priority': 90},
                {'ticker': 'LMT', 'name': 'Lockheed Martin', 'priority': 88},
                {'ticker': 'CAT', 'name': 'Caterpillar', 'priority': 88},
                {'ticker': 'GE', 'name': 'General Electric', 'priority': 87}
            ],
            
            # Retail & Consumer (5)
            'retail': [
                {'ticker': 'WMT', 'name': 'Walmart', 'priority': 90},
                {'ticker': 'COST', 'name': 'Costco', 'priority': 89},
                {'ticker': 'MCD', 'name': 'McDonalds', 'priority': 88},
                {'ticker': 'HD', 'name': 'Home Depot', 'priority': 87},
                {'ticker': 'SBUX', 'name': 'Starbucks', 'priority': 85}
            ],
            
            # Healthcare & Pharma (3)
            'healthcare': [
                {'ticker': 'JNJ', 'name': 'Johnson & Johnson', 'priority': 90},
                {'ticker': 'PFE', 'name': 'Pfizer', 'priority': 88},
                {'ticker': 'MRK', 'name': 'Merck', 'priority': 88}
            ],
            
            # ETFs (3)
            'etfs': [
                {'ticker': 'SPY', 'name': 'SPDR S&P 500 ETF', 'priority': 95},
                {'ticker': 'QQQ', 'name': 'Invesco QQQ ETF', 'priority': 95},
                {'ticker': 'IWM', 'name': 'Russell 2000 ETF', 'priority': 90}
            ],
            
            # Crypto (2)
            'crypto': [
                {'ticker': 'BTC-USD', 'name': 'Bitcoin', 'priority': 100},
                {'ticker': 'ETH-USD', 'name': 'Ethereum', 'priority': 100}
            ]
        }
        
        # High-value, low-cost endpoints (8 endpoints per ticker)
        self.target_endpoints = [
            # Fundamental Data (6 endpoints)
            'OVERVIEW',           # Company overview & key metrics
            'EARNINGS',          # Quarterly earnings data
            'INCOME_STATEMENT',  # Annual income statements
            'BALANCE_SHEET',     # Annual balance sheets
            'CASH_FLOW',         # Annual cash flow statements
            'SHARES_OUTSTANDING', # Share count data
            
            # Technical Indicators (2 endpoints)
            'RSI',               # Relative Strength Index
            'EMA'                # Exponential Moving Average
        ]
        
        self.stats = {
            'session_id': self.session_id,
            'total_tickers_processed': 0,
            'total_records_inserted': 0,
            'total_api_calls': 0,
            'total_errors': 0,
            'successful_tickers': [],
            'failed_tickers': [],
            'start_time': datetime.now(),
            'sector_stats': {}
        }

    def get_all_tickers(self, sector_filter: Optional[str] = None) -> List[Dict]:
        """Get all tickers or filter by sector"""
        all_tickers = []
        
        if sector_filter:
            if sector_filter in self.high_impact_tickers:
                return self.high_impact_tickers[sector_filter]
            else:
                logger.error(f"❌ Invalid sector: {sector_filter}")
                return []
        
        # Return all tickers from all sectors
        for sector, tickers in self.high_impact_tickers.items():
            for ticker_info in tickers:
                ticker_info['sector'] = sector
                all_tickers.append(ticker_info)
        
        # Sort by priority (highest first)
        all_tickers.sort(key=lambda x: x['priority'], reverse=True)
        return all_tickers

    async def process_ticker(self, ticker_info: Dict) -> Dict:
        """Process a single ticker through all endpoints"""
        ticker = ticker_info['ticker']
        name = ticker_info['name']
        sector = ticker_info.get('sector', 'unknown')
        
        logger.info(f"🎯 Processing {ticker} ({name}) - {sector.upper()}")
        
        ticker_stats = {
            'ticker': ticker,
            'name': name,
            'sector': sector,
            'records': 0,
            'successful_endpoints': 0,
            'failed_endpoints': 0,
            'errors': []
        }
        
        start_time = datetime.now()
        
        for endpoint in self.target_endpoints:
            try:
                logger.info(f"📊 {ticker} - Fetching {endpoint}...")
                
                # Fetch data from Alpha Vantage
                success, response_data, error = await self.fetcher.fetch_endpoint(endpoint, ticker)
                
                if success and response_data and 'Error Message' not in str(response_data):
                    # Normalize and process data
                    normalized_records = self.normalizer.normalize_endpoint_data(
                        endpoint, response_data, ticker
                    )
                    
                    if normalized_records:
                        # Write to database (use 1 as epoch since this is a single batch)
                        records_count = await self.writer.write_to_postgres(
                            ticker, endpoint, normalized_records, response_data, 
                            1, self.session_id
                        )
                        
                        ticker_stats['records'] += records_count
                        ticker_stats['successful_endpoints'] += 1
                        
                        logger.info(f"✅ {ticker} - {endpoint}: {records_count} records")
                    else:
                        ticker_stats['failed_endpoints'] += 1
                        logger.warning(f"⚠️ {ticker} - {endpoint}: No data returned")
                else:
                    ticker_stats['failed_endpoints'] += 1
                    error_msg = f"API error or rate limit for {endpoint}"
                    ticker_stats['errors'].append(error_msg)
                    logger.warning(f"⚠️ {ticker} - {endpoint}: {error_msg}")
                
                self.stats['total_api_calls'] += 1
                
                # Small delay between endpoints
                await asyncio.sleep(1)
                
            except Exception as e:
                ticker_stats['failed_endpoints'] += 1
                error_msg = f"{endpoint}: {str(e)}"
                ticker_stats['errors'].append(error_msg)
                logger.error(f"❌ {ticker} - {endpoint}: {str(e)}")
                self.stats['total_errors'] += 1
        
        duration = (datetime.now() - start_time).total_seconds()
        ticker_stats['duration'] = duration
        
        # Update sector stats
        if sector not in self.stats['sector_stats']:
            self.stats['sector_stats'][sector] = {
                'tickers_processed': 0,
                'total_records': 0,
                'successful_tickers': 0
            }
        
        self.stats['sector_stats'][sector]['tickers_processed'] += 1
        self.stats['sector_stats'][sector]['total_records'] += ticker_stats['records']
        
        if ticker_stats['successful_endpoints'] > 0:
            self.stats['successful_tickers'].append(ticker)
            self.stats['sector_stats'][sector]['successful_tickers'] += 1
        else:
            self.stats['failed_tickers'].append(ticker)
        
        self.stats['total_tickers_processed'] += 1
        self.stats['total_records_inserted'] += ticker_stats['records']
        
        logger.info(f"✅ {ticker} Complete: {ticker_stats['records']} records in {duration:.1f}s")
        
        return ticker_stats

    async def run_high_impact_ingestion(self, 
                                      sector_filter: Optional[str] = None,
                                      max_tickers: Optional[int] = None) -> Dict:
        """Run the complete high-impact ticker ingestion"""
        
        logger.info("🚀 Starting High-Impact Ticker Ingestion Pipeline")
        logger.info(f"📊 Session ID: {self.session_id}")
        
        # Get ticker list
        tickers = self.get_all_tickers(sector_filter)
        
        if max_tickers:
            tickers = tickers[:max_tickers]
            
        logger.info(f"🎯 Processing {len(tickers)} high-impact tickers")
        if sector_filter:
            logger.info(f"🔍 Sector filter: {sector_filter.upper()}")
        
        # Log ticker breakdown by sector
        sector_counts = {}
        for ticker_info in tickers:
            sector = ticker_info.get('sector', 'unknown')
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        logger.info("📈 Sector breakdown:")
        for sector, count in sector_counts.items():
            logger.info(f"   {sector.upper()}: {count} tickers")
        
        # Process each ticker
        ticker_results = []
        
        for i, ticker_info in enumerate(tickers, 1):
            logger.info(f"🔄 [{i}/{len(tickers)}] Starting {ticker_info['ticker']}")
            
            try:
                result = await self.process_ticker(ticker_info)
                ticker_results.append(result)
                
                # Progress update
                progress = (i / len(tickers)) * 100
                logger.info(f"📊 Progress: {progress:.1f}% ({i}/{len(tickers)})")
                
            except KeyboardInterrupt:
                logger.warning("⚠️ Pipeline interrupted by user")
                break
            except Exception as e:
                logger.error(f"💥 Fatal error processing {ticker_info['ticker']}: {str(e)}")
                continue
        
        # Calculate final statistics
        duration = (datetime.now() - self.stats['start_time']).total_seconds()
        self.stats['duration_seconds'] = duration
        self.stats['ingestion_rate_per_second'] = (
            self.stats['total_records_inserted'] / duration if duration > 0 else 0
        )
        self.stats['ticker_results'] = ticker_results
        
        return self.stats

    async def create_assets_table_entries(self):
        """Create/update assets table with high-impact tickers"""
        logger.info("📋 Creating assets table entries...")
        
        sql_statements = []
        
        for sector, tickers in self.high_impact_tickers.items():
            for ticker_info in tickers:
                ticker = ticker_info['ticker']
                name = ticker_info['name']
                priority = ticker_info['priority']
                
                # Determine asset type and exchange
                if '-USD' in ticker:
                    asset_type = 'crypto'
                    exchange = 'COINBASE'
                elif ticker in ['SPY', 'QQQ', 'IWM']:
                    asset_type = 'etf'
                    exchange = 'NYSE' if ticker in ['SPY', 'IWM'] else 'NASDAQ'
                else:
                    asset_type = 'stock'
                    exchange = 'NASDAQ' if ticker in ['AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'META', 'TSLA', 'AMD', 'AVGO', 'NFLX', 'COST', 'SBUX'] else 'NYSE'
                
                sql_statements.append(
                    f"('{ticker}', '{name}', '{asset_type}', '{exchange}', {priority})"
                )
        
        # Create the full INSERT statement
        insert_sql = f"""
        INSERT INTO assets (ticker, name, asset_type, exchange, priority_score)
        VALUES {', '.join(sql_statements)}
        ON CONFLICT (ticker) DO UPDATE SET
            name = EXCLUDED.name,
            asset_type = EXCLUDED.asset_type,
            exchange = EXCLUDED.exchange,
            priority_score = EXCLUDED.priority_score;
        """
        
        try:
            await self.db.async_execute_insert(insert_sql)
            logger.info(f"✅ Updated assets table with {len(sql_statements)} high-impact tickers")
        except Exception as e:
            logger.error(f"❌ Failed to update assets table: {str(e)}")

def print_completion_summary(stats: Dict):
    """Print a detailed completion summary"""
    print("\n" + "=" * 80)
    print("🎉 HIGH-IMPACT TICKER INGESTION COMPLETED!")
    print("=" * 80)
    print(f"📊 Session ID: {stats['session_id']}")
    print(f"📈 Total Records: {stats['total_records_inserted']:,}")
    print(f"🎯 Total Tickers: {stats['total_tickers_processed']}")
    print(f"✅ Successful: {len(stats['successful_tickers'])}")
    print(f"❌ Failed: {len(stats['failed_tickers'])}")
    print(f"⏱️ Duration: {stats['duration_seconds']:.1f} seconds")
    print(f"📈 Rate: {stats['ingestion_rate_per_second']:.2f} records/second")
    print(f"🔄 API Calls: {stats['total_api_calls']:,}")
    print(f"❌ Errors: {stats['total_errors']}")
    
    # Sector breakdown
    if stats['sector_stats']:
        print("\n📊 SECTOR PERFORMANCE:")
        for sector, sector_stats in stats['sector_stats'].items():
            success_rate = (sector_stats['successful_tickers'] / sector_stats['tickers_processed'] * 100) if sector_stats['tickers_processed'] > 0 else 0
            print(f"   {sector.upper()}: {sector_stats['total_records']:,} records ({success_rate:.1f}% success)")
    
    # Top performers
    if stats.get('ticker_results'):
        print("\n🏆 TOP PERFORMING TICKERS:")
        top_tickers = sorted(stats['ticker_results'], key=lambda x: x['records'], reverse=True)[:10]
        for i, result in enumerate(top_tickers, 1):
            print(f"   {i}. {result['ticker']}: {result['records']:,} records ({result['sector']})")
    
    if stats['failed_tickers']:
        print(f"\n⚠️ FAILED TICKERS: {', '.join(stats['failed_tickers'])}")
    
    print("=" * 80)

async def main():
    """Main execution function for high-impact ticker pipeline"""
    parser = argparse.ArgumentParser(
        description="High-Impact Ticker Pipeline - Temporary Add-on",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--sector',
        choices=['tech', 'finance', 'energy', 'industrials', 'retail', 'healthcare', 'etfs', 'crypto'],
        help='Process only specific sector'
    )
    
    parser.add_argument(
        '--max-tickers',
        type=int,
        help='Maximum number of tickers to process (for testing)'
    )
    
    parser.add_argument(
        '--setup-assets',
        action='store_true',
        help='Create/update assets table entries and exit'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be processed without running'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print("=" * 80)
    print("🚀 Alpha Vantage High-Impact Ticker Pipeline")
    print("   Temporary add-on for curated asset collection")
    print("   35 tickers × 8 endpoints = ~280 API calls")
    print("=" * 80)
    
    # Initialize pipeline manager
    manager = HighImpactPipelineManager()
    
    try:
        # Setup assets table if requested
        if args.setup_assets:
            await manager.create_assets_table_entries()
            print("✅ Assets table updated successfully")
            return
        
        # Dry run
        if args.dry_run:
            tickers = manager.get_all_tickers(args.sector)
            if args.max_tickers:
                tickers = tickers[:args.max_tickers]
            
            print(f"📊 Would process {len(tickers)} tickers:")
            for ticker_info in tickers:
                print(f"   {ticker_info['ticker']} ({ticker_info['name']}) - {ticker_info.get('sector', 'unknown')}")
            
            print(f"🔄 Total API calls needed: {len(tickers) * len(manager.target_endpoints)}")
            return
        
        # Run the ingestion
        final_stats = await manager.run_high_impact_ingestion(
            sector_filter=args.sector,
            max_tickers=args.max_tickers
        )
        
        # Print completion summary
        print_completion_summary(final_stats)
        
        logger.info("🎉 High-impact ingestion completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ High-impact ingestion interrupted by user")
        
    except Exception as e:
        print(f"\n❌ High-impact ingestion failed: {str(e)}")
        logger.error(f"💥 Fatal error: {str(e)}")
        sys.exit(1)
    
    finally:
        # Clean up resources
        if hasattr(manager, 'fetcher') and hasattr(manager.fetcher, 'close_session'):
            await manager.fetcher.close_session()
        
        if hasattr(manager, 'db') and hasattr(manager.db, 'close_async_pool'):
            await manager.db.close_async_pool()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Pipeline interrupted")
        sys.exit(1)
