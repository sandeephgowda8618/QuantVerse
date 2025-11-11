#!/usr/bin/env python3
"""
Alpha Vantage Quick Demo
Fast demonstration of Alpha Vantage integration with immediate results
Shows data collection for top companies without waiting for full population
"""

import asyncio
import sys
import os
import logging
from datetime import datetime
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_alpha_vantage_collector import EnhancedAlphaVantageCollector, AlphaVantageFunction, get_alpha_vantage_config
from top_200_companies import MEGA_CAP_SYMBOLS
from backend.db.postgres_handler import PostgresHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def quick_demo():
    """Quick demonstration of Alpha Vantage capabilities"""
    
    print("🚀 ALPHA VANTAGE QUICK DEMO")
    print("=" * 60)
    print("Demonstrating comprehensive financial data collection")
    print("for the Top 200 Global Companies by Market Cap")
    print("=" * 60)
    
    # Check API key
    config = get_alpha_vantage_config()
    if config.api_key == "demo":
        print("⚠️ DEMO MODE: Using Alpha Vantage demo key")
        print("   For full functionality, get your free API key at:")
        print("   https://www.alphavantage.co/support/#api-key")
        print("   Then set: export ALPHA_VANTAGE_API_KEY='your_key'")
    else:
        print(f"✅ Using Alpha Vantage API key: {config.api_key[:8]}...")
    
    print(f"📊 Premium Tier: {'Yes' if config.premium_tier else 'No'}")
    print(f"⚡ Rate Limit: {config.effective_calls_per_minute} calls/minute")
    print()
    
    # Initialize collector
    async with EnhancedAlphaVantageCollector(config) as collector:
        demo_results = {}
        
        print("🏢 TOP COMPANIES TO COLLECT:")
        for i, symbol in enumerate(MEGA_CAP_SYMBOLS[:5]):
            print(f"   {i+1}. {symbol}")
        print()
        
        # 1. Test API Connection
        print("1️⃣ Testing API Connection...")
        try:
            market_status = await collector._make_api_call(
                AlphaVantageFunction.MARKET_STATUS
            )
            if market_status:
                print("✅ API Connection successful!")
                if "markets" in market_status:
                    print(f"   📊 Found {len(market_status['markets'])} global markets")
                demo_results["api_connection"] = True
            else:
                print("❌ API Connection failed")
                demo_results["api_connection"] = False
        except Exception as e:
            print(f"❌ API Connection error: {e}")
            demo_results["api_connection"] = False
        print()
        
        # 2. Collect Stock Data for One Company
        print("2️⃣ Collecting Stock Data (Sample Company)...")
        try:
            test_symbol = MEGA_CAP_SYMBOLS[0] if MEGA_CAP_SYMBOLS else "AAPL"
            stock_data = await collector.collect_daily_prices([test_symbol])
            
            if stock_data and test_symbol in stock_data:
                df = stock_data[test_symbol]
                latest_price = df.iloc[0]['close'] if not df.empty else "N/A"
                print(f"✅ Stock data collected for {test_symbol}")
                print(f"   📈 Records: {len(df)}")
                print(f"   💰 Latest Price: ${latest_price}")
                print(f"   📅 Data Range: {df.index.min().date()} to {df.index.max().date()}")
                demo_results["stock_data"] = {
                    "symbol": test_symbol,
                    "records": len(df),
                    "latest_price": float(latest_price) if latest_price != "N/A" else None
                }
            else:
                print(f"❌ No stock data collected for {test_symbol}")
                demo_results["stock_data"] = None
        except Exception as e:
            print(f"❌ Stock data error: {e}")
            demo_results["stock_data"] = None
        print()
        
        # 3. Collect Company Overview
        print("3️⃣ Collecting Fundamental Data...")
        try:
            fundamental_data = await collector.collect_company_overviews([test_symbol])
            
            if fundamental_data and test_symbol in fundamental_data:
                overview = fundamental_data[test_symbol]
                print(f"✅ Fundamental data collected for {test_symbol}")
                print(f"   🏢 Company: {overview.get('Name', 'N/A')}")
                print(f"   🏭 Sector: {overview.get('Sector', 'N/A')}")
                print(f"   🌍 Country: {overview.get('Country', 'N/A')}")
                print(f"   💹 Market Cap: ${overview.get('MarketCapitalization', 'N/A')}")
                print(f"   📊 P/E Ratio: {overview.get('PERatio', 'N/A')}")
                demo_results["fundamental_data"] = {
                    "company": overview.get('Name'),
                    "sector": overview.get('Sector'),
                    "market_cap": overview.get('MarketCapitalization')
                }
            else:
                print(f"❌ No fundamental data collected for {test_symbol}")
                demo_results["fundamental_data"] = None
        except Exception as e:
            print(f"❌ Fundamental data error: {e}")
            demo_results["fundamental_data"] = None
        print()
        
        # 4. Collect News and Sentiment
        print("4️⃣ Collecting News and Sentiment...")
        try:
            news_data = await collector.collect_news_sentiment(tickers=[test_symbol])
            
            if news_data and "feed" in news_data:
                articles = news_data["feed"]
                print(f"✅ News sentiment collected")
                print(f"   📰 Articles: {len(articles)}")
                
                if articles:
                    sample_article = articles[0]
                    print(f"   📈 Sample Title: {sample_article.get('title', 'N/A')[:60]}...")
                    print(f"   😊 Sentiment: {sample_article.get('overall_sentiment_label', 'N/A')}")
                    print(f"   📊 Score: {sample_article.get('overall_sentiment_score', 'N/A')}")
                
                demo_results["news_sentiment"] = {
                    "articles_count": len(articles),
                    "sample_sentiment": articles[0].get('overall_sentiment_label') if articles else None
                }
            else:
                print("❌ No news data collected")
                demo_results["news_sentiment"] = None
        except Exception as e:
            print(f"❌ News sentiment error: {e}")
            demo_results["news_sentiment"] = None
        print()
        
        # 5. Collect Forex Data (Sample)
        print("5️⃣ Collecting Forex Data (Sample)...")
        try:
            # Just test USD/EUR for demo
            forex_data = await collector._make_api_call(
                AlphaVantageFunction.CURRENCY_EXCHANGE_RATE,
                from_currency="USD",
                to_currency="EUR"
            )
            
            if forex_data and "Realtime Currency Exchange Rate" in forex_data:
                rate_data = forex_data["Realtime Currency Exchange Rate"]
                rate = rate_data.get("5. Exchange Rate", "N/A")
                print(f"✅ Forex data collected")
                print(f"   💱 USD/EUR Rate: {rate}")
                print(f"   🕐 Last Updated: {rate_data.get('6. Last Refreshed', 'N/A')}")
                demo_results["forex_data"] = {"usd_eur_rate": rate}
            else:
                print("❌ No forex data collected")
                demo_results["forex_data"] = None
        except Exception as e:
            print(f"❌ Forex data error: {e}")
            demo_results["forex_data"] = None
        print()
        
        # 6. Database Test
        print("6️⃣ Testing Database Storage...")
        try:
            db = PostgresHandler()
            
            # Test basic database connection
            test_result = await db.async_fetch_scalar("SELECT 1")
            if test_result == 1:
                print("✅ Database connection successful")
                
                # Check if tables exist
                tables_count = await db.async_fetch_scalar("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name IN 
                    ('assets', 'market_prices', 'fundamental_data')
                """)
                print(f"   📊 Database tables ready: {tables_count}/3")
                demo_results["database"] = {"connection": True, "tables": int(tables_count)}
            else:
                print("❌ Database connection failed")
                demo_results["database"] = {"connection": False}
                
        except Exception as e:
            print(f"❌ Database error: {e}")
            demo_results["database"] = {"error": str(e)}
        print()
        
        # 7. Implementation Summary
        print("7️⃣ Implementation Summary...")
        
        # Count successful components
        successful_components = sum([
            demo_results.get("api_connection", False),
            demo_results.get("stock_data") is not None,
            demo_results.get("fundamental_data") is not None,
            demo_results.get("news_sentiment") is not None,
            demo_results.get("forex_data") is not None,
            demo_results.get("database", {}).get("connection", False)
        ])
        
        total_components = 6
        success_rate = (successful_components / total_components) * 100
        
        print(f"📊 Components Working: {successful_components}/{total_components} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 Implementation Status: EXCELLENT")
        elif success_rate >= 60:
            print("🟡 Implementation Status: GOOD")
        else:
            print("🔴 Implementation Status: NEEDS ATTENTION")
        print()
        
        # Final metrics from collector
        metrics = collector.metrics.get_summary()
        print("📈 Collection Metrics:")
        print(f"   📞 API Calls: {metrics['total_api_calls']}")
        print(f"   ✅ Success Rate: {metrics['success_rate']:.1%}")
        print(f"   💾 Data Points: {metrics['data_points_collected']}")
        print(f"   🔢 Vector Embeddings: {metrics['vector_embeddings_created']}")
        print(f"   ⏱️ Runtime: {metrics['runtime_seconds']:.1f}s")
        
        # Save demo results
        demo_results["metrics"] = metrics
        demo_results["success_rate"] = success_rate
        demo_results["timestamp"] = datetime.now().isoformat()
        
        demo_filename = f"alpha_vantage_demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(demo_filename, 'w') as f:
            json.dump(demo_results, f, indent=2, default=str)
        
        print()
        print("=" * 60)
        print("🏆 DEMO COMPLETED!")
        print(f"💾 Results saved to: {demo_filename}")
        print()
        print("🚀 Next Steps:")
        print("   1. Set up your Alpha Vantage API key for full functionality")
        print("   2. Run: python populate_alpha_vantage_data.py --tiers mega")
        print("   3. Run: python test_alpha_vantage_implementation.py")
        print("=" * 60)

def main():
    """Main demo execution"""
    try:
        asyncio.run(quick_demo())
    except KeyboardInterrupt:
        print("\n⏸️ Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
