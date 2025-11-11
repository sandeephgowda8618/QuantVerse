#!/usr/bin/env python3
"""
Focused Alpha Vantage Data Ingestion Pipeline
Uses only essential endpoints to work within free tier API limits
"""

import asyncio
import sys
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

# Add backend to Python path
sys.path.append(str(Path(__file__).parent / 'backend'))

from backend.config.settings import settings
from backend.data_ingestion.alpha_fetcher import AlphaFetcher
from backend.data_ingestion.alpha_writer import AlphaWriter
from backend.db.postgres_handler import PostgresHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'focused_ingestion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Essential endpoints that work with free tier
ESSENTIAL_ENDPOINTS = [
    'GLOBAL_QUOTE',      # Real-time quotes
    'OVERVIEW',          # Company fundamentals
    'EARNINGS',          # Earnings data
    'TIME_SERIES_DAILY', # Daily prices (compact)
]

# Key companies for focused ingestion
KEY_COMPANIES = [
    {'ticker': 'AAPL', 'name': 'Apple Inc'},
    {'ticker': 'MSFT', 'name': 'Microsoft Corporation'},
    {'ticker': 'GOOGL', 'name': 'Alphabet Inc'},
    {'ticker': 'AMZN', 'name': 'Amazon.com Inc'},
    {'ticker': 'TSLA', 'name': 'Tesla Inc'},
    {'ticker': 'NVDA', 'name': 'NVIDIA Corporation'},
    {'ticker': 'META', 'name': 'Meta Platforms Inc'},
    {'ticker': 'NFLX', 'name': 'Netflix Inc'},
]

class FocusedIngestionManager:
    def __init__(self):
        self.db = PostgresHandler()
        self.fetcher = AlphaFetcher()
        self.writer = AlphaWriter()
        self.session_id = f"focused_ingestion_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    async def run_focused_ingestion(self):
        """Run focused ingestion with essential endpoints only"""
        logger.info(f"🚀 Starting Focused Alpha Vantage Ingestion: {self.session_id}")
        logger.info(f"📊 Companies: {len(KEY_COMPANIES)}")
        logger.info(f"🔗 Endpoints per company: {len(ESSENTIAL_ENDPOINTS)}")
        
        stats = {
            'session_id': self.session_id,
            'start_time': datetime.now(),
            'total_records': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'companies_processed': 0,
            'endpoints_processed': 0
        }
        
        try:
            for i, company in enumerate(KEY_COMPANIES, 1):
                ticker = company['ticker']
                name = company['name']
                
                logger.info(f"🔄 Processing {i}/{len(KEY_COMPANIES)}: {ticker} ({name})")
                
                company_stats = await self.process_company(ticker, name)
                stats['total_records'] += company_stats['records']
                stats['successful_requests'] += company_stats['successful']
                stats['failed_requests'] += company_stats['failed']
                stats['companies_processed'] += 1
                
                # Small delay between companies
                await asyncio.sleep(3)
                
                # Progress update
                logger.info(f"✅ {ticker} completed: {company_stats['records']} records, "
                          f"{company_stats['successful']} success, {company_stats['failed']} failed")
        
        except Exception as e:
            logger.error(f"💥 Ingestion failed: {str(e)}")
            raise
        
        finally:
            stats['end_time'] = datetime.now()
            stats['duration'] = (stats['end_time'] - stats['start_time']).total_seconds()
            stats['rate_per_second'] = stats['total_records'] / stats['duration'] if stats['duration'] > 0 else 0
            
            await self.print_final_stats(stats)
        
        return stats
    
    async def normalize_endpoint_data(self, ticker: str, endpoint: str, raw_data: dict) -> list:
        """Normalize endpoint data for database storage"""
        try:
            normalized = []
            
            if endpoint == 'GLOBAL_QUOTE':
                quote_data = raw_data.get('Global Quote', {})
                if quote_data:
                    record = {
                        'ticker': ticker,
                        'endpoint': endpoint,
                        'timestamp': datetime.now(timezone.utc),
                        'raw_payload': raw_data,
                        'parsed_values': quote_data,
                        'quality_flag': 'success',
                        'source': 'alpha_vantage',
                        'data_type': 'market_data'
                    }
                    normalized.append(record)
            
            elif endpoint == 'OVERVIEW':
                if raw_data and 'Symbol' in raw_data:
                    record = {
                        'ticker': ticker,
                        'endpoint': endpoint,
                        'timestamp': datetime.now(timezone.utc),
                        'raw_payload': raw_data,
                        'parsed_values': raw_data,
                        'quality_flag': 'success',
                        'source': 'alpha_vantage',
                        'data_type': 'fundamental'
                    }
                    normalized.append(record)
            
            elif endpoint == 'EARNINGS':
                if raw_data and 'symbol' in raw_data:
                    record = {
                        'ticker': ticker,
                        'endpoint': endpoint,
                        'timestamp': datetime.now(timezone.utc),
                        'raw_payload': raw_data,
                        'parsed_values': raw_data,
                        'quality_flag': 'success',
                        'source': 'alpha_vantage',
                        'data_type': 'fundamental'
                    }
                    normalized.append(record)
            
            elif endpoint == 'TIME_SERIES_DAILY':
                time_series = raw_data.get('Time Series (Daily)', {})
                if time_series:
                    # Take only last 5 days to avoid too much data
                    sorted_dates = sorted(time_series.keys(), reverse=True)[:5]
                    
                    for date_str in sorted_dates:
                        values = time_series[date_str]
                        record = {
                            'ticker': ticker,
                            'endpoint': endpoint,
                            'timestamp': datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc),
                            'raw_payload': {date_str: values},
                            'parsed_values': values,
                            'quality_flag': 'success',
                            'source': 'alpha_vantage',
                            'data_type': 'time_series'
                        }
                        normalized.append(record)
            
            return normalized
            
        except Exception as e:
            logger.error(f"❌ Failed to normalize {endpoint} data for {ticker}: {str(e)}")
            return []
    
    async def process_company(self, ticker, name):
        """Process all essential endpoints for a company"""
        company_stats = {
            'records': 0,
            'successful': 0,
            'failed': 0,
            'endpoints': {}
        }
        
        for endpoint_idx, endpoint in enumerate(ESSENTIAL_ENDPOINTS):
            try:
                logger.info(f"📊 {ticker} - {endpoint}")
                
                # Fetch data
                success, raw_data, error = await self.fetcher.fetch_endpoint(endpoint, ticker)
                
                if success and raw_data:
                    # Prepare data for database write
                    normalized_data = await self.normalize_endpoint_data(ticker, endpoint, raw_data)
                    
                    if normalized_data:
                        # Write to database
                        record_count, failed_count, errors = await self.writer.write_normalized_data(
                            records=normalized_data,
                            ingestion_epoch=endpoint_idx + 1,  # Endpoint index as epoch
                            ingestion_sequence=hash(f"{ticker}_{endpoint}") % 1000000,  # Simple sequence
                            ingestion_session_id=self.session_id
                        )
                        
                        company_stats['records'] += record_count
                        company_stats['successful'] += 1
                        company_stats['endpoints'][endpoint] = 'success'
                        
                        logger.info(f"✅ {ticker} - {endpoint}: {record_count} records")
                    else:
                        company_stats['failed'] += 1
                        company_stats['endpoints'][endpoint] = 'no data after normalization'
                        logger.warning(f"⚠️ {ticker} - {endpoint}: No data after normalization")
                    
                else:
                    company_stats['failed'] += 1
                    company_stats['endpoints'][endpoint] = f'failed: {error}'
                    logger.warning(f"❌ {ticker} - {endpoint}: {error}")
                
                # Rate limiting delay
                await asyncio.sleep(5)  # 5 seconds between requests
                
            except Exception as e:
                company_stats['failed'] += 1
                company_stats['endpoints'][endpoint] = f'error: {str(e)}'
                logger.error(f"💥 {ticker} - {endpoint}: {str(e)}")
                
                # Continue with next endpoint
                continue
        
        return company_stats
    
    async def print_final_stats(self, stats):
        """Print final ingestion statistics"""
        print("\n" + "=" * 80)
        print("🎉 FOCUSED ALPHA VANTAGE INGESTION COMPLETED!")
        print("=" * 80)
        print(f"📊 Session ID: {stats['session_id']}")
        print(f"📈 Total Records: {stats['total_records']:,}")
        print(f"🏢 Companies Processed: {stats['companies_processed']}/{len(KEY_COMPANIES)}")
        print(f"✅ Successful Requests: {stats['successful_requests']}")
        print(f"❌ Failed Requests: {stats['failed_requests']}")
        print(f"⏱️ Duration: {stats['duration']:.1f} seconds")
        print(f"📈 Rate: {stats['rate_per_second']:.2f} records/second")
        
        success_rate = (stats['successful_requests'] / 
                       (stats['successful_requests'] + stats['failed_requests']) * 100) if stats['successful_requests'] + stats['failed_requests'] > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        print("=" * 80)

async def main():
    """Main execution function"""
    print("=" * 80)
    print("🚀 Focused Alpha Vantage Data Ingestion Pipeline")
    print("   Essential endpoints only - optimized for free tier")
    print("=" * 80)
    
    manager = FocusedIngestionManager()
    
    try:
        # Test connectivity first
        logger.info("🧪 Testing API connectivity...")
        test_result = await manager.fetcher.test_api_connectivity()
        
        if not test_result['connected']:
            logger.error(f"❌ API connectivity failed: {test_result['error']}")
            return
            
        logger.info("✅ API connectivity confirmed")
        
        # Run focused ingestion
        final_stats = await manager.run_focused_ingestion()
        
        logger.info("🎉 Focused ingestion completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Ingestion interrupted by user")
        
    except Exception as e:
        logger.error(f"💥 Fatal error: {str(e)}")
        raise
        
    finally:
        # Clean up
        if hasattr(manager.fetcher, 'close_session'):
            await manager.fetcher.close_session()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Ingestion interrupted")
        sys.exit(1)
