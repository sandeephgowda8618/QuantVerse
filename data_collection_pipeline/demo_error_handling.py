#!/usr/bin/env python3
"""
Demo script showing comprehensive error handling and rate limit management
"""

import asyncio
import logging
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from data_collection_pipeline.utils import ResilientCollector, error_handler, setup_logging, ingestion_logger, generate_session_id

class DemoCollector(ResilientCollector):
    """Demo collector to showcase error handling"""
    
    def __init__(self):
        super().__init__("DemoCollector")
        self.set_api_budget(5)  # Small budget for demo
        
        # Add fallback providers
        self.add_fallback_provider("backup_api")
        self.add_fallback_provider("emergency_api")
    
    async def collect_data(self, tickers: list):
        """Collect data with comprehensive error handling"""
        session_id = generate_session_id("demo")
        self.set_session(session_id)
        
        print(f"🚀 Starting collection with session: {session_id}")
        print(f"📊 API Budget: {self.max_api_calls} calls")
        print(f"🎯 Target tickers: {tickers}")
        
        # Create session in database
        await ingestion_logger.create_session(session_id, {
            'demo': True,
            'tickers': tickers,
            'collector': self.name
        })
        
        results = []
        
        for ticker in tickers:
            if not self.can_make_api_call():
                print(f"⚠️  API budget exhausted ({self.api_calls_made}/{self.max_api_calls})")
                break
            
            print(f"\n📈 Collecting data for {ticker}...")
            
            # Try to make API call (will fail gracefully)
            result = await self.safe_api_call(
                provider="demo_api",
                url=f"https://httpbin.org/status/429",  # Will return 429 (rate limited)
                headers={"Authorization": "Bearer demo_token"}
            )
            
            if result:
                results.append({ticker: result})
                print(f"✅ {ticker}: Success")
            else:
                print(f"❌ {ticker}: Failed (will try fallback)")
                
                # Try alternative endpoint
                backup_result = await self.safe_api_call(
                    provider="fallback_api", 
                    url=f"https://httpbin.org/json",  # Should work
                    headers={"User-Agent": "Demo-Collector"}
                )
                
                if backup_result:
                    results.append({ticker: backup_result})
                    print(f"✅ {ticker}: Success via fallback")
                else:
                    print(f"❌ {ticker}: All methods failed")
        
        # Update session
        await ingestion_logger.update_session(
            session_id, "COMPLETED", len(results), self.api_calls_made
        )
        
        return results
    
    def _count_records(self, response):
        """Count records in response"""
        if isinstance(response, dict):
            return 1
        elif isinstance(response, list):
            return len(response)
        return 0

async def main():
    """Demo main function"""
    
    # Setup logging
    log_file = setup_logging('demo_error_handling', 'INFO')
    logger = logging.getLogger(__name__)
    
    print("=" * 60)
    print("🧪 QuantVerse Error Handling & Rate Limit Demo")
    print("=" * 60)
    print(f"📋 Log file: {log_file}")
    
    # Create demo collector
    collector = DemoCollector()
    
    # Demo tickers
    demo_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META"]
    
    try:
        # Collect data
        results = await collector.collect_data(demo_tickers)
        
        print("\n" + "=" * 60)
        print("📊 COLLECTION RESULTS")
        print("=" * 60)
        
        summary = collector.get_collection_summary()
        print(f"Collector: {summary['collector_name']}")
        print(f"API Calls: {summary['api_calls_made']}/{summary['api_budget']}")
        print(f"Errors: {summary['errors']}")
        print(f"Results: {len(results)} successful collections")
        
        if summary['error_details']:
            print(f"\n⚠️  Error Details:")
            for error in summary['error_details'][-3:]:  # Show last 3 errors
                print(f"  - {error['provider']}: {error['error'][:100]}...")
        
        # Show rate limit status
        error_summary = error_handler.get_error_summary()
        if error_summary['rate_limited_providers']:
            print(f"\n🚫 Rate Limited Providers:")
            for provider in error_summary['rate_limited_providers']:
                print(f"  - {provider}")
        
        print(f"\n🎯 Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
