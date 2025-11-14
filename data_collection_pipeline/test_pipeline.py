#!/usr/bin/env python3
"""
Test script for the data collection pipeline
Runs basic functionality tests and connectivity checks
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from data_collection_pipeline.config import config
from data_collection_pipeline.utils import db_manager, http_client, setup_logging
from data_collection_pipeline.orchestrator import pipeline

async def test_database_connection():
    """Test database connectivity"""
    print("🔌 Testing database connection...")
    try:
        await db_manager.initialize()
        
        # Test basic query
        result = await db_manager.execute_query("SELECT 1 as test")
        if result and result[0]['test'] == 1:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database query failed")
            return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    finally:
        await db_manager.close()

async def test_http_client():
    """Test HTTP client functionality"""
    print("🌐 Testing HTTP client...")
    try:
        await http_client.initialize()
        
        # Test basic HTTP request
        response = await http_client.request_with_retries(
            "https://httpbin.org/json",
            provider="test"
        )
        
        if response and isinstance(response, dict):
            print("✅ HTTP client working")
            return True
        else:
            print("❌ HTTP client failed")
            return False
    except Exception as e:
        print(f"❌ HTTP client failed: {e}")
        return False
    finally:
        await http_client.close()

async def test_api_keys():
    """Test API key configuration"""
    print("🔑 Testing API key configuration...")
    
    results = {
        'tiingo': bool(config.api.tiingo_api_key),
        'finnhub': bool(config.api.finnhub_api_key),
        'perplexity': bool(config.api.perplexity_api_key),
        'polygon': bool(config.api.polygon_api_key),
        'alpaca': bool(config.api.alpaca_api_key and config.api.alpaca_secret_key),
        'alpha_vantage': bool(config.api.alpha_vantage_keys),
    }
    
    configured_count = sum(results.values())
    total_count = len(results)
    
    print(f"📊 API Keys configured: {configured_count}/{total_count}")
    
    for provider, configured in results.items():
        status = "✅" if configured else "⚠️ "
        print(f"  {status} {provider}: {'Configured' if configured else 'Not configured'}")
    
    if config.api.alpha_vantage_keys:
        print(f"  📈 Alpha Vantage: {len(config.api.alpha_vantage_keys)} keys available")
    
    return configured_count > 0

async def test_configuration():
    """Test configuration values"""
    print("⚙️  Testing configuration...")
    
    print(f"  Environment: {config.environment}")
    print(f"  Database: {config.database.host}:{config.database.port}/{config.database.database}")
    print(f"  Log Level: {config.log_level}")
    print(f"  Market Data Interval: {config.scheduler.market_data_interval}s")
    print(f"  News Data Interval: {config.scheduler.news_data_interval}s")
    print(f"  Regulatory Interval: {config.scheduler.regulatory_interval}s")
    
    return True

async def test_pipeline_dry_run():
    """Test pipeline initialization without data collection"""
    print("🚀 Testing pipeline initialization...")
    try:
        await pipeline.initialize()
        print("✅ Pipeline initialization successful")
        
        # Test session creation
        from data_collection_pipeline.utils import ingestion_logger, generate_session_id
        
        test_session_id = generate_session_id("test")
        await ingestion_logger.create_session(
            test_session_id,
            metadata={'test': True, 'total_tickers': 5}
        )
        
        await ingestion_logger.update_session(
            test_session_id,
            status='completed',
            total_records=0,
            total_api_calls=0
        )
        
        print("✅ Session management working")
        return True
        
    except Exception as e:
        print(f"❌ Pipeline initialization failed: {e}")
        return False
    finally:
        await pipeline.shutdown()

async def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 QuantVerse Data Collection Pipeline - Test Suite")
    print("=" * 60)
    
    # Set up logging to file and console
    log_file_path = setup_logging('test', 'INFO')
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("Starting pipeline test suite")
    logger.info(f"Test log file: {log_file_path}")
    logger.info("=" * 60)
    
    tests = [
        ("Configuration", test_configuration()),
        ("API Keys", test_api_keys()),
        ("Database Connection", test_database_connection()),
        ("HTTP Client", test_http_client()),
        ("Pipeline Initialization", test_pipeline_dry_run())
    ]
    
    results = []
    
    for test_name, test_coro in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            result = await test_coro
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Pipeline is ready to run.")
        return 0
    else:
        print("⚠️  Some tests failed. Check configuration and dependencies.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
