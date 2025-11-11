#!/usr/bin/env python3
"""
Alpha Vantage Implementation Test Suite
Comprehensive testing of all implemented Alpha Vantage APIs and data collection
"""

import asyncio
import sys
import os
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import traceback

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_alpha_vantage_collector import EnhancedAlphaVantageCollector, get_alpha_vantage_config, AlphaVantageFunction
from top_200_companies import MEGA_CAP_SYMBOLS, LARGE_CAP_SYMBOLS, MID_CAP_SYMBOLS
from backend.db.postgres_handler import PostgresHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('alpha_vantage_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AlphaVantageTestSuite:
    """Comprehensive test suite for Alpha Vantage implementation"""
    
    def __init__(self):
        self.config = get_alpha_vantage_config()
        self.db = PostgresHandler()
        self.test_results = {
            "start_time": datetime.now(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": [],
            "api_endpoints_tested": [],
            "errors": []
        }
    
    def log_test_result(self, test_name: str, passed: bool, details: str = "", error: str = ""):
        """Log test result"""
        self.test_results["tests_run"] += 1
        
        if passed:
            self.test_results["tests_passed"] += 1
            logger.info(f"✅ {test_name}: PASSED - {details}")
        else:
            self.test_results["tests_failed"] += 1
            logger.error(f"❌ {test_name}: FAILED - {details} - Error: {error}")
            self.test_results["errors"].append(f"{test_name}: {error}")
        
        self.test_results["test_details"].append({
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_database_schema(self):
        """Test database schema setup"""
        test_name = "Database Schema Setup"
        
        try:
            # Test core tables exist
            tables_to_check = [
                "assets", "market_prices", "fundamental_data", "earnings_data",
                "forex_prices", "crypto_prices", "commodities_prices",
                "economic_indicators", "technical_indicators", "news_headlines"
            ]
            
            missing_tables = []
            for table in tables_to_check:
                try:
                    result = await self.db.async_fetch_scalar(
                        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = $1",
                        (table,)
                    )
                    if result == 0:
                        missing_tables.append(table)
                except Exception as e:
                    missing_tables.append(f"{table} (error: {e})")
            
            if missing_tables:
                self.log_test_result(
                    test_name, False,
                    f"Missing tables: {', '.join(missing_tables)}",
                    "Database schema incomplete"
                )
            else:
                self.log_test_result(
                    test_name, True,
                    f"All {len(tables_to_check)} required tables exist"
                )
                
        except Exception as e:
            self.log_test_result(test_name, False, "", str(e))
    
    async def test_api_connection(self):
        """Test basic API connection and authentication"""
        test_name = "API Connection Test"
        
        try:
            async with EnhancedAlphaVantageCollector(self.config) as collector:
                # Test with a simple market status call
                data = await collector._make_api_call(AlphaVantageFunction.MARKET_STATUS)
                
                if data and "markets" in data:
                    self.log_test_result(
                        test_name, True,
                        f"API connection successful, got {len(data['markets'])} markets"
                    )
                    self.test_results["api_endpoints_tested"].append("MARKET_STATUS")
                else:
                    self.log_test_result(
                        test_name, False,
                        "API call succeeded but unexpected response format",
                        f"Response: {data}"
                    )
                    
        except Exception as e:
            self.log_test_result(test_name, False, "", str(e))
    
    async def test_stock_data_collection(self):
        """Test stock data collection"""
        test_name = "Stock Data Collection"
        
        try:
            async with EnhancedAlphaVantageCollector(self.config) as collector:
                # Test with one mega cap stock
                test_symbol = MEGA_CAP_SYMBOLS[0] if MEGA_CAP_SYMBOLS else "AAPL"
                
                # Test daily data collection
                data = await collector.collect_daily_prices([test_symbol])
                
                if data and test_symbol in data:
                    df = data[test_symbol]
                    self.log_test_result(
                        test_name, True,
                        f"Collected {len(df)} daily price records for {test_symbol}"
                    )
                    self.test_results["api_endpoints_tested"].append("TIME_SERIES_DAILY_ADJUSTED")
                else:
                    self.log_test_result(
                        test_name, False,
                        f"No data collected for {test_symbol}",
                        "Daily price collection failed"
                    )
                    
        except Exception as e:
            self.log_test_result(test_name, False, "", str(e))
    
    async def test_fundamental_data_collection(self):
        """Test fundamental data collection"""
        test_name = "Fundamental Data Collection"
        
        try:
            async with EnhancedAlphaVantageCollector(self.config) as collector:
                test_symbol = MEGA_CAP_SYMBOLS[0] if MEGA_CAP_SYMBOLS else "AAPL"
                
                # Test company overview
                data = await collector.collect_company_overviews([test_symbol])
                
                if data and test_symbol in data:
                    overview = data[test_symbol]
                    company_name = overview.get("Name", "Unknown")
                    sector = overview.get("Sector", "Unknown")
                    
                    self.log_test_result(
                        test_name, True,
                        f"Collected overview for {company_name} in {sector} sector"
                    )
                    self.test_results["api_endpoints_tested"].append("OVERVIEW")
                else:
                    self.log_test_result(
                        test_name, False,
                        f"No fundamental data collected for {test_symbol}",
                        "Company overview collection failed"
                    )
                    
        except Exception as e:
            self.log_test_result(test_name, False, "", str(e))
    
    async def test_news_sentiment_collection(self):
        """Test news sentiment collection"""
        test_name = "News Sentiment Collection"
        
        try:
            async with EnhancedAlphaVantageCollector(self.config) as collector:
                # Test news sentiment without specific tickers (general market news)
                data = await collector.collect_news_sentiment()
                
                if data and "feed" in data and len(data["feed"]) > 0:
                    articles_count = len(data["feed"])
                    self.log_test_result(
                        test_name, True,
                        f"Collected {articles_count} news articles with sentiment"
                    )
                    self.test_results["api_endpoints_tested"].append("NEWS_SENTIMENT")
                else:
                    self.log_test_result(
                        test_name, False,
                        "No news articles collected",
                        "News sentiment collection failed"
                    )
                    
        except Exception as e:
            self.log_test_result(test_name, False, "", str(e))
    
    async def test_forex_data_collection(self):
        """Test forex data collection"""
        test_name = "Forex Data Collection"
        
        try:
            async with EnhancedAlphaVantageCollector(self.config) as collector:
                # Test forex data for major pairs
                data = await collector.collect_forex_data()
                
                if data:
                    pairs_collected = len(data)
                    self.log_test_result(
                        test_name, True,
                        f"Collected forex data for {pairs_collected} currency pairs"
                    )
                    self.test_results["api_endpoints_tested"].append("FX_DAILY")
                else:
                    self.log_test_result(
                        test_name, False,
                        "No forex data collected",
                        "Forex collection failed"
                    )
                    
        except Exception as e:
            self.log_test_result(test_name, False, "", str(e))
    
    async def test_crypto_data_collection(self):
        """Test cryptocurrency data collection"""
        test_name = "Crypto Data Collection"
        
        try:
            async with EnhancedAlphaVantageCollector(self.config) as collector:
                # Test crypto data collection
                data = await collector.collect_crypto_data()
                
                if data:
                    cryptos_collected = len(data)
                    self.log_test_result(
                        test_name, True,
                        f"Collected crypto data for {cryptos_collected} cryptocurrencies"
                    )
                    self.test_results["api_endpoints_tested"].append("DIGITAL_CURRENCY_DAILY")
                else:
                    self.log_test_result(
                        test_name, False,
                        "No crypto data collected",
                        "Crypto collection failed"
                    )
                    
        except Exception as e:
            self.log_test_result(test_name, False, "", str(e))
    
    async def test_economic_indicators_collection(self):
        """Test economic indicators collection"""
        test_name = "Economic Indicators Collection"
        
        try:
            async with EnhancedAlphaVantageCollector(self.config) as collector:
                # Test economic indicators
                data = await collector.collect_economic_indicators()
                
                if data:
                    indicators_collected = len(data)
                    self.log_test_result(
                        test_name, True,
                        f"Collected {indicators_collected} economic indicators"
                    )
                    self.test_results["api_endpoints_tested"].extend(["REAL_GDP", "TREASURY_YIELD", "CPI"])
                else:
                    self.log_test_result(
                        test_name, False,
                        "No economic indicators collected",
                        "Economic indicators collection failed"
                    )
                    
        except Exception as e:
            self.log_test_result(test_name, False, "", str(e))
    
    async def test_technical_indicators_collection(self):
        """Test technical indicators collection"""
        test_name = "Technical Indicators Collection"
        
        try:
            async with EnhancedAlphaVantageCollector(self.config) as collector:
                test_symbol = MEGA_CAP_SYMBOLS[0] if MEGA_CAP_SYMBOLS else "AAPL"
                
                # Test technical indicators
                data = await collector.collect_technical_indicators([test_symbol])
                
                if data and test_symbol in data and data[test_symbol]:
                    indicators_collected = len(data[test_symbol])
                    self.log_test_result(
                        test_name, True,
                        f"Collected {indicators_collected} technical indicators for {test_symbol}"
                    )
                    self.test_results["api_endpoints_tested"].extend(["SMA", "EMA", "RSI"])
                else:
                    self.log_test_result(
                        test_name, False,
                        f"No technical indicators collected for {test_symbol}",
                        "Technical indicators collection failed"
                    )
                    
        except Exception as e:
            self.log_test_result(test_name, False, "", str(e))
    
    async def test_top_movers_collection(self):
        """Test top gainers/losers collection"""
        test_name = "Top Movers Collection"
        
        try:
            async with EnhancedAlphaVantageCollector(self.config) as collector:
                # Test top gainers and losers
                data = await collector.collect_top_gainers_losers()
                
                if data:
                    gainers = data.get("top_gainers", [])
                    losers = data.get("top_losers", [])
                    most_active = data.get("most_actively_traded", [])
                    
                    total_movers = len(gainers) + len(losers) + len(most_active)
                    
                    self.log_test_result(
                        test_name, True,
                        f"Collected {total_movers} top movers ({len(gainers)} gainers, {len(losers)} losers, {len(most_active)} active)"
                    )
                    self.test_results["api_endpoints_tested"].append("TOP_GAINERS_LOSERS")
                else:
                    self.log_test_result(
                        test_name, False,
                        "No top movers data collected",
                        "Top movers collection failed"
                    )
                    
        except Exception as e:
            self.log_test_result(test_name, False, "", str(e))
    
    async def test_database_storage(self):
        """Test database storage functionality"""
        test_name = "Database Storage Test"
        
        try:
            # Test inserting and retrieving sample data
            test_ticker = "TEST"
            test_timestamp = datetime.now()
            
            # Insert test market data
            await self.db.async_execute_query("""
                INSERT INTO market_prices (ticker, timestamp, open, high, low, close, volume, source)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (ticker, timestamp) DO NOTHING
            """, (test_ticker, test_timestamp, 100.0, 105.0, 99.0, 103.0, 1000000, 'test'))
            
            # Retrieve the data
            result = await self.db.async_fetch_one("""
                SELECT * FROM market_prices WHERE ticker = $1 AND timestamp = $2
            """, (test_ticker, test_timestamp))
            
            if result:
                # Clean up test data
                await self.db.async_execute_query("""
                    DELETE FROM market_prices WHERE ticker = $1 AND source = 'test'
                """, (test_ticker,))
                
                self.log_test_result(
                    test_name, True,
                    f"Successfully stored and retrieved test data for {test_ticker}"
                )
            else:
                self.log_test_result(
                    test_name, False,
                    "Failed to retrieve inserted test data",
                    "Database storage/retrieval failed"
                )
                
        except Exception as e:
            self.log_test_result(test_name, False, "", str(e))
    
    async def test_rate_limiting(self):
        """Test rate limiting functionality"""
        test_name = "Rate Limiting Test"
        
        try:
            async with EnhancedAlphaVantageCollector(self.config) as collector:
                start_time = time.time()
                
                # Make 3 rapid API calls to test rate limiting
                calls_made = 0
                for i in range(3):
                    data = await collector._make_api_call(AlphaVantageFunction.MARKET_STATUS)
                    if data:
                        calls_made += 1
                
                end_time = time.time()
                elapsed_time = end_time - start_time
                
                # Rate limiting should ensure minimum time between calls
                expected_min_time = (calls_made - 1) * (60.0 / collector.config.effective_calls_per_minute)
                
                if elapsed_time >= expected_min_time * 0.9:  # Allow 10% tolerance
                    self.log_test_result(
                        test_name, True,
                        f"Rate limiting working: {calls_made} calls in {elapsed_time:.1f}s (expected min: {expected_min_time:.1f}s)"
                    )
                else:
                    self.log_test_result(
                        test_name, False,
                        f"Rate limiting too fast: {calls_made} calls in {elapsed_time:.1f}s (expected min: {expected_min_time:.1f}s)",
                        "Rate limiting not working properly"
                    )
                    
        except Exception as e:
            self.log_test_result(test_name, False, "", str(e))
    
    async def run_all_tests(self):
        """Run all tests in the test suite"""
        logger.info("🧪 STARTING ALPHA VANTAGE IMPLEMENTATION TEST SUITE")
        logger.info("=" * 80)
        
        # List of all test methods
        test_methods = [
            self.test_database_schema,
            self.test_api_connection,
            self.test_stock_data_collection,
            self.test_fundamental_data_collection,
            self.test_news_sentiment_collection,
            self.test_forex_data_collection,
            self.test_crypto_data_collection,
            self.test_economic_indicators_collection,
            self.test_technical_indicators_collection,
            self.test_top_movers_collection,
            self.test_database_storage,
            self.test_rate_limiting
        ]
        
        # Run each test
        for test_method in test_methods:
            try:
                await test_method()
                # Add delay between tests to respect API limits
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Test method {test_method.__name__} crashed: {e}")
                self.test_results["errors"].append(f"{test_method.__name__}: {e}")
        
        # Generate final report
        await self.generate_test_report()
    
    async def generate_test_report(self):
        """Generate comprehensive test report"""
        end_time = datetime.now()
        runtime = (end_time - self.test_results["start_time"]).total_seconds()
        
        logger.info("\n" + "=" * 80)
        logger.info("🏆 ALPHA VANTAGE TEST SUITE RESULTS")
        logger.info("=" * 80)
        
        # Summary statistics
        pass_rate = (self.test_results["tests_passed"] / max(1, self.test_results["tests_run"])) * 100
        
        logger.info("📊 TEST SUMMARY:")
        logger.info(f"   🏃 Tests Run: {self.test_results['tests_run']}")
        logger.info(f"   ✅ Tests Passed: {self.test_results['tests_passed']}")
        logger.info(f"   ❌ Tests Failed: {self.test_results['tests_failed']}")
        logger.info(f"   📈 Pass Rate: {pass_rate:.1f}%")
        logger.info(f"   ⏱️ Runtime: {runtime:.1f} seconds")
        logger.info(f"   🔌 API Endpoints Tested: {len(set(self.test_results['api_endpoints_tested']))}")
        
        # API endpoints coverage
        if self.test_results["api_endpoints_tested"]:
            logger.info(f"\n🔌 API ENDPOINTS TESTED:")
            unique_endpoints = set(self.test_results["api_endpoints_tested"])
            for endpoint in sorted(unique_endpoints):
                logger.info(f"   ✅ {endpoint}")
        
        # Test details
        logger.info(f"\n📋 DETAILED RESULTS:")
        for test in self.test_results["test_details"]:
            status = "✅ PASS" if test["passed"] else "❌ FAIL"
            logger.info(f"   {status}: {test['test_name']}")
            if test["details"]:
                logger.info(f"        {test['details']}")
            if test["error"]:
                logger.info(f"        Error: {test['error']}")
        
        # Errors summary
        if self.test_results["errors"]:
            logger.info(f"\n⚠️ ERRORS ENCOUNTERED:")
            for error in self.test_results["errors"]:
                logger.info(f"   • {error}")
        
        # Recommendations
        logger.info(f"\n💡 RECOMMENDATIONS:")
        if self.test_results["tests_failed"] == 0:
            logger.info("   🎉 All tests passed! Implementation is ready for production.")
        else:
            logger.info("   🔧 Fix failed tests before proceeding to production.")
            
        if len(set(self.test_results["api_endpoints_tested"])) < 5:
            logger.info("   📞 Limited API endpoints tested - consider testing more endpoints.")
            
        logger.info("=" * 80)
        
        # Save test report
        report_filename = f"alpha_vantage_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        import json
        with open(report_filename, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        logger.info(f"💾 Test report saved to: {report_filename}")

async def main():
    """Main test execution"""
    test_suite = AlphaVantageTestSuite()
    
    # Check API key
    if test_suite.config.api_key == "demo":
        logger.warning("⚠️ Using demo API key - some tests may fail")
        logger.warning("   Set ALPHA_VANTAGE_API_KEY environment variable for full testing")
    
    try:
        await test_suite.run_all_tests()
    except KeyboardInterrupt:
        logger.info("\n⏸️ Test suite interrupted by user")
    except Exception as e:
        logger.error(f"💥 Test suite failed: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
