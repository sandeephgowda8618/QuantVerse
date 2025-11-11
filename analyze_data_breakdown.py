#!/usr/bin/env python3
"""
Enhanced data analysis for Alpha Vantage stored data
"""

import os
import sys
import psycopg2
import json
from collections import defaultdict, Counter
from datetime import datetime
import pandas as pd

# Add parent directory to path for imports
sys.path.append('/Users/sandeeph/Documents/QuantVerse/urisk')

def load_db_config():
    """Load database configuration from environment"""
    from dotenv import load_dotenv
    load_dotenv()
    
    return {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
        'database': os.getenv('POSTGRES_DB', 'urisk'),
        'user': os.getenv('POSTGRES_USER', 'urisk_user'),
        'password': os.getenv('POSTGRES_PASSWORD', 'urisk_password')
    }

def analyze_data_breakdown():
    """Analyze stored data with enhanced breakdown"""
    
    print("📊 Enhanced Alpha Vantage Data Breakdown")
    print("=" * 80)
    
    db_config = load_db_config()
    
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                
                # 1. Company Coverage Analysis
                print("\n🏢 COMPANY COVERAGE ANALYSIS")
                print("-" * 40)
                
                cur.execute("""
                    SELECT 
                        ticker,
                        COUNT(*) as total_records,
                        COUNT(DISTINCT endpoint) as endpoints,
                        MIN(ingestion_time) as first_record,
                        MAX(ingestion_time) as latest_record,
                        ROUND(AVG(CASE WHEN quality_flag = 'success' THEN 1.0 ELSE 0.0 END) * 100, 2) as success_rate
                    FROM alpha_vantage_data 
                    GROUP BY ticker
                    ORDER BY total_records DESC
                """)
                
                companies = cur.fetchall()
                for ticker, total, endpoints, first, latest, success in companies:
                    print(f"   🏢 {ticker}: {total:,} records, {endpoints} endpoints, {success}% success")
                    print(f"      📅 {first.strftime('%Y-%m-%d')} → {latest.strftime('%Y-%m-%d')}")
                
                # 2. Data Type Categorization
                print("\n📈 DATA TYPE BREAKDOWN")
                print("-" * 40)
                
                cur.execute("""
                    SELECT endpoint, COUNT(*) as records, COUNT(DISTINCT ticker) as tickers
                    FROM alpha_vantage_data
                    GROUP BY endpoint
                    ORDER BY records DESC
                """)
                
                endpoints = cur.fetchall()
                
                # Categorize endpoints
                categories = {
                    'Technical Indicators': [],
                    'Time Series': [],
                    'Fundamental Data': [],
                    'Market Intelligence': [],
                    'Options': [],
                    'News & Sentiment': []
                }
                
                for endpoint, records, tickers in endpoints:
                    if endpoint in ['EMA', 'RSI', 'BBANDS', 'MACD', 'SMA', 'WMA', 'ATR', 'OBV', 'MFI', 
                                  'CCI', 'AROON', 'PPO', 'DX', 'MINUS_DI', 'PLUS_DI', 'SAR', 'TRIX',
                                  'HT_TRENDLINE', 'HT_SINE', 'HT_PHASOR', 'HT_DCPERIOD', 'HT_DCPHASE',
                                  'HT_TRENDMODE', 'CMO', 'ROC', 'ROCR', 'MOM', 'TRANGE', 'NATR',
                                  'ADOSC', 'ULTOSC', 'MIDPOINT', 'MIDPRICE', 'MINUS_DM', 'PLUS_DM',
                                  'AROONOSC']:
                        categories['Technical Indicators'].append((endpoint, records, tickers))
                    elif endpoint.startswith('TIME_SERIES') or endpoint == 'GLOBAL_QUOTE':
                        categories['Time Series'].append((endpoint, records, tickers))
                    elif endpoint in ['OVERVIEW', 'EARNINGS', 'INCOME_STATEMENT', 'BALANCE_SHEET', 
                                    'CASH_FLOW', 'SHARES_OUTSTANDING']:
                        categories['Fundamental Data'].append((endpoint, records, tickers))
                    elif endpoint in ['MARKET_STATUS', 'TOP_GAINERS_LOSERS', 'SECTOR_PERFORMANCE']:
                        categories['Market Intelligence'].append((endpoint, records, tickers))
                    elif 'OPTIONS' in endpoint:
                        categories['Options'].append((endpoint, records, tickers))
                    elif 'NEWS' in endpoint or 'SENTIMENT' in endpoint or 'TRANSCRIPT' in endpoint:
                        categories['News & Sentiment'].append((endpoint, records, tickers))
                
                for category, data in categories.items():
                    if data:
                        total_records = sum(r[1] for r in data)
                        print(f"\n   📊 {category}: {total_records:,} records")
                        for endpoint, records, tickers in sorted(data, key=lambda x: x[1], reverse=True)[:5]:
                            print(f"      • {endpoint}: {records:,} records ({tickers} tickers)")
                        if len(data) > 5:
                            print(f"      ... and {len(data) - 5} more endpoints")
                
                # 3. Historical Data Depth
                print("\n📅 HISTORICAL DATA DEPTH")
                print("-" * 40)
                
                cur.execute("""
                    SELECT 
                        ticker,
                        endpoint,
                        MIN(timestamp) as earliest_data,
                        MAX(timestamp) as latest_data,
                        COUNT(*) as data_points
                    FROM alpha_vantage_data
                    WHERE endpoint LIKE 'TIME_SERIES%' OR endpoint = 'GLOBAL_QUOTE'
                    GROUP BY ticker, endpoint
                    ORDER BY ticker, data_points DESC
                """)
                
                time_series = cur.fetchall()
                for ticker, endpoint, earliest, latest, points in time_series:
                    years = (latest - earliest).days / 365.25 if latest and earliest else 0
                    print(f"   📈 {ticker} {endpoint}: {points:,} points, {years:.1f} years")
                    if earliest and latest:
                        print(f"      📅 {earliest.strftime('%Y-%m-%d')} → {latest.strftime('%Y-%m-%d')}")
                
                # 4. Technical Indicators Coverage
                print("\n🔧 TECHNICAL INDICATORS COVERAGE")
                print("-" * 40)
                
                cur.execute("""
                    SELECT 
                        ticker,
                        COUNT(DISTINCT endpoint) as indicators,
                        STRING_AGG(endpoint, ', ' ORDER BY endpoint) as indicator_list
                    FROM alpha_vantage_data
                    WHERE endpoint NOT LIKE 'TIME_SERIES%' 
                      AND endpoint NOT IN ('OVERVIEW', 'EARNINGS', 'INCOME_STATEMENT', 'BALANCE_SHEET', 
                                         'CASH_FLOW', 'SHARES_OUTSTANDING', 'GLOBAL_QUOTE', 'MARKET_STATUS',
                                         'TOP_GAINERS_LOSERS', 'NEWS_SENTIMENT', 'HISTORICAL_OPTIONS',
                                         'EARNINGS_CALL_TRANSCRIPT')
                    GROUP BY ticker
                    ORDER BY indicators DESC
                """)
                
                indicators = cur.fetchall()
                for ticker, count, indicator_list in indicators:
                    print(f"   🔧 {ticker}: {count} indicators")
                    # Truncate long lists
                    if len(indicator_list) > 100:
                        print(f"      {indicator_list[:100]}...")
                    else:
                        print(f"      {indicator_list}")
                
                # 5. Recent Activity Summary
                print("\n⚡ RECENT ACTIVITY (Last 24h)")
                print("-" * 40)
                
                cur.execute("""
                    SELECT 
                        DATE(ingestion_time) as date,
                        COUNT(*) as records,
                        COUNT(DISTINCT ticker) as tickers,
                        COUNT(DISTINCT endpoint) as endpoints
                    FROM alpha_vantage_data
                    WHERE ingestion_time >= NOW() - INTERVAL '24 hours'
                    GROUP BY DATE(ingestion_time)
                    ORDER BY date DESC
                """)
                
                activity = cur.fetchall()
                for date, records, tickers, endpoints in activity:
                    print(f"   📅 {date}: {records:,} records, {tickers} tickers, {endpoints} endpoints")
                
                # 6. Data Quality by Category
                print("\n🎯 DATA QUALITY BY CATEGORY")
                print("-" * 40)
                
                quality_categories = {
                    'Technical': ['EMA', 'RSI', 'BBANDS', 'MACD', 'ATR'],
                    'Time Series': ['TIME_SERIES_DAILY', 'TIME_SERIES_WEEKLY', 'GLOBAL_QUOTE'],
                    'Fundamental': ['OVERVIEW', 'EARNINGS', 'INCOME_STATEMENT', 'BALANCE_SHEET']
                }
                
                for category, endpoints_list in quality_categories.items():
                    placeholders = ','.join(['%s'] * len(endpoints_list))
                    cur.execute(f"""
                        SELECT 
                            quality_flag,
                            COUNT(*) as count
                        FROM alpha_vantage_data
                        WHERE endpoint IN ({placeholders})
                        GROUP BY quality_flag
                        ORDER BY count DESC
                    """, endpoints_list)
                    
                    quality = cur.fetchall()
                    if quality:
                        total = sum(count for _, count in quality)
                        print(f"   📊 {category}: {total:,} total records")
                        for flag, count in quality:
                            pct = (count / total * 100) if total > 0 else 0
                            print(f"      • {flag}: {count:,} ({pct:.1f}%)")
                
                print("\n" + "=" * 80)
                print("✅ ENHANCED DATA BREAKDOWN COMPLETE")
                print("=" * 80)
                
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")
        return False

if __name__ == "__main__":
    analyze_data_breakdown()
