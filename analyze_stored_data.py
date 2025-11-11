#!/usr/bin/env python3
"""
Alpha Vantage Data Analysis Script
Analyze what data has been stored in the database
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to Python path
sys.path.append(str(Path(__file__).parent / 'backend'))

from backend.db.postgres_handler import PostgresHandler

async def analyze_stored_data():
    """Comprehensive analysis of stored Alpha Vantage data"""
    print("📊 Alpha Vantage Stored Data Analysis")
    print("="*80)
    
    db = PostgresHandler()
    await db.initialize_async_pool()
    
    try:
        # ==========================================
        # OVERALL DATA SUMMARY
        # ==========================================
        print("\n🎯 OVERALL DATA SUMMARY")
        print("-"*40)
        
        overall_query = """
        SELECT 
            'alpha_vantage_data' as table_name,
            COUNT(*) as total_records,
            COUNT(DISTINCT ticker) as unique_tickers,
            COUNT(DISTINCT endpoint) as unique_endpoints,
            MIN(ingestion_time) as earliest_data,
            MAX(ingestion_time) as latest_data
        FROM alpha_vantage_data
        WHERE ticker IS NOT NULL
        """
        
        overall_result = await db.async_execute_query(overall_query)
        if overall_result:
            data = overall_result[0]
            print(f"📈 Total Records: {data['total_records']:,}")
            print(f"🏢 Unique Companies: {data['unique_tickers']}")
            print(f"🔗 Unique Endpoints: {data['unique_endpoints']}")
            print(f"📅 Data Range: {data['earliest_data']} to {data['latest_data']}")
        
        # ==========================================
        # COMPANY ANALYSIS
        # ==========================================
        print("\n🏢 COMPANIES WITH DATA")
        print("-"*40)
        
        companies_query = """
        SELECT 
            ticker,
            COUNT(*) as total_records,
            COUNT(DISTINCT endpoint) as endpoints_count,
            MAX(ingestion_time) as last_updated
        FROM alpha_vantage_data 
        WHERE ticker IS NOT NULL AND ticker != ''
        GROUP BY ticker 
        ORDER BY total_records DESC
        LIMIT 20
        """
        
        companies = await db.async_execute_query(companies_query)
        
        print(f"{'Ticker':<8} {'Records':<10} {'Endpoints':<10} {'Last Updated'}")
        print("-"*60)
        for company in companies:
            last_updated = company['last_updated'].strftime('%Y-%m-%d %H:%M') if company['last_updated'] else 'N/A'
            print(f"{company['ticker']:<8} {company['total_records']:<10,} {company['endpoints_count']:<10} {last_updated}")
        
        # ==========================================
        # ENDPOINT ANALYSIS
        # ==========================================
        print("\n🔗 DATA BY ENDPOINT TYPE")
        print("-"*40)
        
        endpoints_query = """
        SELECT 
            endpoint,
            COUNT(*) as record_count,
            COUNT(DISTINCT ticker) as ticker_count,
            MAX(ingestion_time) as last_updated
        FROM alpha_vantage_data 
        WHERE endpoint IS NOT NULL
        GROUP BY endpoint 
        ORDER BY record_count DESC
        """
        
        endpoints = await db.async_execute_query(endpoints_query)
        
        print(f"{'Endpoint':<25} {'Records':<10} {'Tickers':<8} {'Last Updated'}")
        print("-"*70)
        for endpoint in endpoints:
            last_updated = endpoint['last_updated'].strftime('%Y-%m-%d') if endpoint['last_updated'] else 'N/A'
            print(f"{endpoint['endpoint']:<25} {endpoint['record_count']:<10,} {endpoint['ticker_count']:<8} {last_updated}")
        
        # ==========================================
        # MARKET DATA ANALYSIS
        # ==========================================
        print("\n📈 MARKET DATA ANALYSIS")
        print("-"*40)
        
        # Check alpha_market_data table
        market_query = """
        SELECT 
            COUNT(*) as total_market_records,
            COUNT(DISTINCT ticker) as market_tickers,
            MIN(timestamp) as earliest_price,
            MAX(timestamp) as latest_price,
            AVG(volume) as avg_volume
        FROM alpha_market_data
        WHERE close_price IS NOT NULL
        """
        
        market_result = await db.async_execute_query(market_query)
        if market_result and market_result[0]['total_market_records']:
            data = market_result[0]
            print(f"📊 Market Records: {data['total_market_records']:,}")
            print(f"🏢 Market Tickers: {data['market_tickers']}")
            print(f"📅 Price Range: {data['earliest_price']} to {data['latest_price']}")
            print(f"📊 Avg Volume: {data['avg_volume']:,.0f}" if data['avg_volume'] else "📊 Avg Volume: N/A")
        else:
            print("📊 No dedicated market data found (data may be in alpha_vantage_data table)")
        
        # Sample market data from main table
        sample_market_query = """
        SELECT 
            ticker,
            endpoint,
            timestamp,
            parsed_values
        FROM alpha_vantage_data 
        WHERE endpoint LIKE '%TIME_SERIES%' OR endpoint LIKE '%QUOTE%'
        ORDER BY ingestion_time DESC
        LIMIT 5
        """
        
        sample_market = await db.async_execute_query(sample_market_query)
        if sample_market:
            print("\n📈 SAMPLE MARKET DATA:")
            for sample in sample_market:
                print(f"   🔹 {sample['ticker']} - {sample['endpoint']} ({sample['timestamp']})")
        
        # ==========================================
        # FUNDAMENTAL DATA ANALYSIS
        # ==========================================
        print("\n🏦 FUNDAMENTAL DATA ANALYSIS")
        print("-"*40)
        
        fundamental_query = """
        SELECT 
            COUNT(*) as total_fundamental,
            COUNT(DISTINCT ticker) as fundamental_tickers
        FROM alpha_fundamental_data
        """
        
        fundamental_result = await db.async_execute_query(fundamental_query)
        if fundamental_result and fundamental_result[0]['total_fundamental']:
            data = fundamental_result[0]
            print(f"📊 Fundamental Records: {data['total_fundamental']:,}")
            print(f"🏢 Companies with Fundamentals: {data['fundamental_tickers']}")
        else:
            print("📊 No dedicated fundamental data found")
        
        # Check for fundamental data in main table
        fundamental_main_query = """
        SELECT 
            COUNT(*) as fundamental_count,
            COUNT(DISTINCT ticker) as ticker_count
        FROM alpha_vantage_data 
        WHERE endpoint IN ('OVERVIEW', 'COMPANY_OVERVIEW', 'INCOME_STATEMENT', 'BALANCE_SHEET', 'CASH_FLOW', 'EARNINGS')
        """
        
        fund_main = await db.async_execute_query(fundamental_main_query)
        if fund_main and fund_main[0]['fundamental_count']:
            data = fund_main[0]
            print(f"📊 Fundamental Records (main table): {data['fundamental_count']:,}")
            print(f"🏢 Companies with Fundamentals: {data['ticker_count']}")
        
        # ==========================================
        # NEWS & INTELLIGENCE ANALYSIS
        # ==========================================
        print("\n📰 NEWS & INTELLIGENCE ANALYSIS")
        print("-"*40)
        
        news_query = """
        SELECT 
            COUNT(*) as total_news,
            COUNT(DISTINCT ticker) as news_tickers
        FROM alpha_news_intelligence
        """
        
        news_result = await db.async_execute_query(news_query)
        if news_result and news_result[0]['total_news']:
            data = news_result[0]
            print(f"📰 News Records: {data['total_news']:,}")
            print(f"🏢 Tickers with News: {data['news_tickers']}")
        else:
            print("📰 No dedicated news data found")
        
        # Check for news data in main table
        news_main_query = """
        SELECT 
            COUNT(*) as news_count,
            COUNT(DISTINCT ticker) as ticker_count
        FROM alpha_vantage_data 
        WHERE endpoint IN ('NEWS_SENTIMENT', 'NEWS', 'EARNINGS_CALL_TRANSCRIPT')
        """
        
        news_main = await db.async_execute_query(news_main_query)
        if news_main and news_main[0]['news_count']:
            data = news_main[0]
            print(f"📰 News Records (main table): {data['news_count']:,}")
            print(f"🏢 Companies with News: {data['ticker_count']}")
        
        # ==========================================
        # DATA QUALITY ANALYSIS
        # ==========================================
        print("\n🎯 DATA QUALITY ANALYSIS")
        print("-"*40)
        
        quality_query = """
        SELECT 
            quality_flag,
            COUNT(*) as record_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
        FROM alpha_vantage_data 
        WHERE quality_flag IS NOT NULL
        GROUP BY quality_flag
        ORDER BY record_count DESC
        """
        
        quality_result = await db.async_execute_query(quality_query)
        if quality_result:
            print(f"{'Quality Flag':<15} {'Records':<10} {'Percentage'}")
            print("-"*35)
            for quality in quality_result:
                print(f"{quality['quality_flag']:<15} {quality['record_count']:<10,} {quality['percentage']}%")
        
        # ==========================================
        # RECENT INGESTION ACTIVITY
        # ==========================================
        print("\n⏰ RECENT INGESTION ACTIVITY")
        print("-"*40)
        
        recent_query = """
        SELECT 
            DATE(ingestion_time) as ingestion_date,
            COUNT(*) as records_ingested,
            COUNT(DISTINCT ticker) as tickers_processed,
            COUNT(DISTINCT endpoint) as endpoints_used
        FROM alpha_vantage_data 
        WHERE ingestion_time >= NOW() - INTERVAL '7 days'
        GROUP BY DATE(ingestion_time)
        ORDER BY ingestion_date DESC
        """
        
        recent_result = await db.async_execute_query(recent_query)
        if recent_result:
            print(f"{'Date':<12} {'Records':<10} {'Tickers':<8} {'Endpoints'}")
            print("-"*40)
            for recent in recent_result:
                print(f"{recent['ingestion_date']:<12} {recent['records_ingested']:<10,} {recent['tickers_processed']:<8} {recent['endpoints_used']}")
        else:
            print("No recent ingestion activity found (last 7 days)")
        
        # ==========================================
        # SAMPLE DATA PREVIEW
        # ==========================================
        print("\n👁️ SAMPLE DATA PREVIEW")
        print("-"*40)
        
        sample_query = """
        SELECT 
            ticker,
            endpoint,
            timestamp,
            LEFT(raw_payload::text, 100) as sample_payload,
            ingestion_time
        FROM alpha_vantage_data 
        ORDER BY ingestion_time DESC
        LIMIT 5
        """
        
        samples = await db.async_execute_query(sample_query)
        if samples:
            for i, sample in enumerate(samples, 1):
                print(f"\n📋 Sample {i}:")
                print(f"   🏢 Ticker: {sample['ticker']}")
                print(f"   🔗 Endpoint: {sample['endpoint']}")
                print(f"   ⏰ Timestamp: {sample['timestamp']}")
                print(f"   📄 Payload: {sample['sample_payload']}...")
                print(f"   💾 Ingested: {sample['ingestion_time']}")
        
        # ==========================================
        # STORAGE STATISTICS
        # ==========================================
        print("\n💾 STORAGE STATISTICS")
        print("-"*40)
        
        storage_query = """
        SELECT 
            pg_size_pretty(pg_total_relation_size('alpha_vantage_data')) as total_size,
            pg_size_pretty(pg_relation_size('alpha_vantage_data')) as data_size,
            pg_size_pretty(pg_total_relation_size('alpha_vantage_data') - pg_relation_size('alpha_vantage_data')) as index_size
        """
        
        storage_result = await db.async_execute_query(storage_query)
        if storage_result:
            data = storage_result[0]
            print(f"💾 Total Size: {data['total_size']}")
            print(f"📊 Data Size: {data['data_size']}")
            print(f"🔍 Index Size: {data['index_size']}")
        
        print("\n" + "="*80)
        print("✅ DATA ANALYSIS COMPLETE")
        print("="*80)
        
        # Summary insights
        if overall_result and overall_result[0]['total_records'] > 0:
            total_records = overall_result[0]['total_records']
            unique_tickers = overall_result[0]['unique_tickers']
            unique_endpoints = overall_result[0]['unique_endpoints']
            
            print(f"\n💡 KEY INSIGHTS:")
            print(f"   📈 You have {total_records:,} records across {unique_tickers} companies")
            print(f"   🔗 Data from {unique_endpoints} different Alpha Vantage endpoints")
            print(f"   📊 Average {total_records//unique_tickers if unique_tickers > 0 else 0} records per company")
            
            if total_records > 100000:
                print(f"   🎉 Substantial dataset - excellent for analysis!")
            elif total_records > 10000:
                print(f"   ✅ Good dataset size - ready for insights!")
            else:
                print(f"   📝 Growing dataset - continue ingestion for better coverage")
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
    
    finally:
        await db.close_async_pool()

if __name__ == "__main__":
    asyncio.run(analyze_stored_data())
