#!/usr/bin/env python3
"""
Simple test to verify Alpha Vantage API key works with new fixes
This is a minimal test to validate the basic functionality
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add backend to Python path
sys.path.append(str(Path(__file__).parent / 'backend'))

from backend.config.settings import settings
from backend.data_ingestion.alpha_fetcher import AlphaFetcher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def simple_test():
    """Simple test to verify API key functionality"""
    logger.info("🔧 Initializing Alpha Vantage fetcher with improved anti-automation fixes...")
    
    fetcher = AlphaFetcher()
    
    logger.info(f"🔑 Using {len(fetcher.api_keys)} API keys")
    logger.info(f"⏱️ Base rate limit delay: {fetcher.base_rate_limit_delay}s")
    logger.info(f"🎯 Testing basic functionality...")
    
    try:
        # Test 1: Simple quote
        logger.info("📊 Testing GLOBAL_QUOTE for AAPL...")
        success, data, error = await fetcher.fetch_endpoint('GLOBAL_QUOTE', 'AAPL')
        
        if success:
            logger.info("✅ GLOBAL_QUOTE: SUCCESS")
            if data and '01. symbol' in str(data):
                logger.info("✅ Valid data structure received")
            else:
                logger.warning("⚠️ Unexpected data structure")
        else:
            logger.error(f"❌ GLOBAL_QUOTE failed: {error}")
            return False
        
        # Test 2: Company Overview (fundamental - cacheable)
        logger.info("🏢 Testing COMPANY_OVERVIEW for AAPL...")
        success, data, error = await fetcher.fetch_endpoint('COMPANY_OVERVIEW', 'AAPL')
        
        if success:
            logger.info("✅ COMPANY_OVERVIEW: SUCCESS")
            if data and 'Symbol' in data:
                logger.info("✅ Valid company data received")
            else:
                logger.warning("⚠️ Unexpected company data structure")
        else:
            logger.error(f"❌ COMPANY_OVERVIEW failed: {error}")
            return False
        
        # Test 3: Cache functionality - request same endpoint again
        logger.info("💾 Testing cache functionality...")
        import time
        start = time.time()
        success, data, error = await fetcher.fetch_endpoint('COMPANY_OVERVIEW', 'AAPL')
        duration = time.time() - start
        
        if success and duration < 0.1:
            logger.info(f"✅ Cache working! Request took {duration:.3f}s (cache hit)")
        elif success:
            logger.info(f"⚠️ Request took {duration:.3f}s (possible fresh request)")
        else:
            logger.error(f"❌ Cache test failed: {error}")
        
        # Print statistics
        logger.info("📊 Final Statistics:")
        logger.info(f"   Total calls: {fetcher.total_calls}")
        logger.info(f"   Successful: {fetcher.successful_calls}")
        logger.info(f"   Failed: {fetcher.failed_calls}")
        logger.info(f"   Rate limited: {fetcher.rate_limited_calls}")
        logger.info(f"   Current key: {fetcher.get_current_key_info()['key_preview']}")
        logger.info(f"   Cache entries: {len(fetcher.fundamental_cache)}")
        
        return True
        
    except Exception as e:
        logger.error(f"💥 Test failed with exception: {str(e)}")
        return False
        
    finally:
        await fetcher.close_session()

if __name__ == "__main__":
    print("🧪 Alpha Vantage Simple Test")
    print("=" * 50)
    
    try:
        result = asyncio.run(simple_test())
        if result:
            print("\n🎉 TEST PASSED - Alpha Vantage fixes are working!")
        else:
            print("\n❌ TEST FAILED - Issues detected")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
        sys.exit(1)
