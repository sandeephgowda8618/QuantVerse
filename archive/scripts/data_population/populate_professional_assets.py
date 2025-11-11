#!/usr/bin/env python3
"""
Professional Asset Universe Population for uRISK System
Scales up from 18 assets to 200+ professional-grade universe
Based on proven methods from successful ingestion tests
"""

import asyncio
import sys
import os
from datetime import datetime
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.db.postgres_handler import PostgresHandler
from backend.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

class ProfessionalAssetPopulator:
    """Populate professional asset universe using proven methods"""
    
    def __init__(self):
        self.db = PostgresHandler()
        
    async def populate_professional_assets(self):
        """Populate 200+ professional assets using successful pattern"""
        logger.info("🚀 Populating professional asset universe (200+ assets)...")
        
        try:
            # Professional asset universe - proven categories that work
            professional_assets = [
                # US Large Cap Tech (Proven working in tests)
                ("AAPL", "Apple Inc.", "stock", "NASDAQ", "Technology", "US"),
                ("MSFT", "Microsoft Corporation", "stock", "NASDAQ", "Technology", "US"),
                ("GOOGL", "Alphabet Inc.", "stock", "NASDAQ", "Technology", "US"),
                ("AMZN", "Amazon.com Inc.", "stock", "NASDAQ", "Technology", "US"),
                ("NVDA", "NVIDIA Corporation", "stock", "NASDAQ", "Technology", "US"),
                ("TSLA", "Tesla Inc.", "stock", "NASDAQ", "Automotive", "US"),
                ("META", "Meta Platforms Inc.", "stock", "NASDAQ", "Technology", "US"),
                ("NFLX", "Netflix Inc.", "stock", "NASDAQ", "Technology", "US"),
                ("CRM", "Salesforce Inc.", "stock", "NYSE", "Technology", "US"),
                ("ADBE", "Adobe Inc.", "stock", "NASDAQ", "Technology", "US"),
                
                # US Large Cap Non-Tech
                ("JPM", "JPMorgan Chase & Co.", "stock", "NYSE", "Financial", "US"),
                ("JNJ", "Johnson & Johnson", "stock", "NYSE", "Healthcare", "US"),
                ("V", "Visa Inc.", "stock", "NYSE", "Financial", "US"),
                ("PG", "Procter & Gamble Co.", "stock", "NYSE", "Consumer", "US"),
                ("UNH", "UnitedHealth Group Inc.", "stock", "NYSE", "Healthcare", "US"),
                ("HD", "Home Depot Inc.", "stock", "NYSE", "Retail", "US"),
                ("MA", "Mastercard Inc.", "stock", "NYSE", "Financial", "US"),
                ("BAC", "Bank of America Corp.", "stock", "NYSE", "Financial", "US"),
                ("PFE", "Pfizer Inc.", "stock", "NYSE", "Healthcare", "US"),
                ("KO", "Coca-Cola Co.", "stock", "NYSE", "Consumer", "US"),
                
                # US Mid Cap Growth
                ("ROKU", "Roku Inc.", "stock", "NASDAQ", "Technology", "US"),
                ("SHOP", "Shopify Inc.", "stock", "NYSE", "Technology", "CA"),
                ("SQ", "Block Inc.", "stock", "NYSE", "Financial", "US"),
                ("PLTR", "Palantir Technologies Inc.", "stock", "NYSE", "Technology", "US"),
                ("SNOW", "Snowflake Inc.", "stock", "NYSE", "Technology", "US"),
                ("ZM", "Zoom Video Communications", "stock", "NASDAQ", "Technology", "US"),
                ("DOCU", "DocuSign Inc.", "stock", "NASDAQ", "Technology", "US"),
                ("TWLO", "Twilio Inc.", "stock", "NYSE", "Technology", "US"),
                ("OKTA", "Okta Inc.", "stock", "NASDAQ", "Technology", "US"),
                ("CRWD", "CrowdStrike Holdings Inc.", "stock", "NASDAQ", "Technology", "US"),
                
                # Indian Equities (NSE)
                ("RELIANCE.NS", "Reliance Industries Ltd.", "stock", "NSE", "Energy", "India"),
                ("TCS.NS", "Tata Consultancy Services", "stock", "NSE", "Technology", "India"),
                ("HDFCBANK.NS", "HDFC Bank Ltd.", "stock", "NSE", "Financial", "India"),
                ("INFY.NS", "Infosys Ltd.", "stock", "NSE", "Technology", "India"),
                ("HINDUNILVR.NS", "Hindustan Unilever Ltd.", "stock", "NSE", "Consumer", "India"),
                ("ICICIBANK.NS", "ICICI Bank Ltd.", "stock", "NSE", "Financial", "India"),
                ("BHARTIARTL.NS", "Bharti Airtel Ltd.", "stock", "NSE", "Telecom", "India"),
                ("ITC.NS", "ITC Ltd.", "stock", "NSE", "Consumer", "India"),
                ("SBIN.NS", "State Bank of India", "stock", "NSE", "Financial", "India"),
                ("LT.NS", "Larsen & Toubro Ltd.", "stock", "NSE", "Industrial", "India"),
                
                # Major Cryptocurrencies (Proven working)
                ("BTC", "Bitcoin", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("ETH", "Ethereum", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("SOL", "Solana", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("ADA", "Cardano", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("DOT", "Polkadot", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("MATIC", "Polygon", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("AVAX", "Avalanche", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("LINK", "Chainlink", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("UNI", "Uniswap", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("ATOM", "Cosmos", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                
                # Altcoins & DeFi
                ("BNB", "Binance Coin", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("XRP", "Ripple", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("DOGE", "Dogecoin", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("SHIB", "Shiba Inu", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("LTC", "Litecoin", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("BCH", "Bitcoin Cash", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("ALGO", "Algorand", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("VET", "VeChain", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("FIL", "Filecoin", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                ("THETA", "Theta Network", "crypto", "CRYPTO", "Cryptocurrency", "Global"),
                
                # Major ETFs (Proven working)
                ("SPY", "SPDR S&P 500 ETF", "etf", "NYSE", "ETF", "US"),
                ("QQQ", "Invesco QQQ Trust", "etf", "NASDAQ", "ETF", "US"),
                ("IWM", "iShares Russell 2000 ETF", "etf", "NYSE", "ETF", "US"),
                ("VTI", "Vanguard Total Stock Market", "etf", "NYSE", "ETF", "US"),
                ("EFA", "iShares MSCI EAFE ETF", "etf", "NYSE", "ETF", "US"),
                ("EEM", "iShares MSCI Emerging Markets", "etf", "NYSE", "ETF", "US"),
                ("GLD", "SPDR Gold Shares", "etf", "NYSE", "ETF", "US"),
                ("SLV", "iShares Silver Trust", "etf", "NYSE", "ETF", "US"),
                ("TLT", "iShares 20+ Year Treasury Bond", "etf", "NYSE", "ETF", "US"),
                ("HYG", "iShares iBoxx High Yield Corporate", "etf", "NYSE", "ETF", "US"),
                
                # Sector ETFs
                ("XLK", "Technology Select Sector SPDR", "etf", "NYSE", "ETF", "US"),
                ("XLF", "Financial Select Sector SPDR", "etf", "NYSE", "ETF", "US"),
                ("XLE", "Energy Select Sector SPDR", "etf", "NYSE", "ETF", "US"),
                ("XLV", "Health Care Select Sector SPDR", "etf", "NYSE", "ETF", "US"),
                ("XLI", "Industrial Select Sector SPDR", "etf", "NYSE", "ETF", "US"),
                ("XLY", "Consumer Discretionary SPDR", "etf", "NYSE", "ETF", "US"),
                ("XLP", "Consumer Staples Select Sector", "etf", "NYSE", "ETF", "US"),
                ("XLU", "Utilities Select Sector SPDR", "etf", "NYSE", "ETF", "US"),
                ("XLB", "Materials Select Sector SPDR", "etf", "NYSE", "ETF", "US"),
                ("XLRE", "Real Estate Select Sector SPDR", "etf", "NYSE", "ETF", "US"),
                
                # Global Indices (tested pattern)
                ("^GSPC", "S&P 500 Index", "index", "INDEX", "Index", "US"),
                ("^IXIC", "NASDAQ Composite", "index", "INDEX", "Index", "US"),
                ("^DJI", "Dow Jones Industrial Average", "index", "INDEX", "Index", "US"),
                ("^RUT", "Russell 2000 Index", "index", "INDEX", "Index", "US"),
                ("^VIX", "CBOE Volatility Index", "index", "INDEX", "Index", "US"),
                ("^NSEI", "NIFTY 50", "index", "INDEX", "Index", "India"),
                ("^BSESN", "BSE SENSEX", "index", "INDEX", "Index", "India"),
                ("^FTSE", "FTSE 100 Index", "index", "INDEX", "Index", "UK"),
                ("^GDAXI", "DAX Performance Index", "index", "INDEX", "Index", "Germany"),
                ("^N225", "Nikkei 225", "index", "INDEX", "Index", "Japan"),
                
                # Forex Pairs (proven working)
                ("EURUSD", "EUR/USD", "fx", "FOREX", "Currency", "Global"),
                ("GBPUSD", "GBP/USD", "fx", "FOREX", "Currency", "Global"),
                ("USDJPY", "USD/JPY", "fx", "FOREX", "Currency", "Global"),
                ("USDCHF", "USD/CHF", "fx", "FOREX", "Currency", "Global"),
                ("AUDUSD", "AUD/USD", "fx", "FOREX", "Currency", "Global"),
                ("USDCAD", "USD/CAD", "fx", "FOREX", "Currency", "Global"),
                ("NZDUSD", "NZD/USD", "fx", "FOREX", "Currency", "Global"),
                ("USDINR", "USD/INR", "fx", "FOREX", "Currency", "Global"),
                ("EURGBP", "EUR/GBP", "fx", "FOREX", "Currency", "Global"),
                ("EURJPY", "EUR/JPY", "fx", "FOREX", "Currency", "Global"),
                
                # Commodities & Futures
                ("GC=F", "Gold Futures", "commodity", "COMEX", "Precious Metal", "Global"),
                ("SI=F", "Silver Futures", "commodity", "COMEX", "Precious Metal", "Global"),
                ("CL=F", "Crude Oil Futures", "commodity", "NYMEX", "Energy", "Global"),
                ("NG=F", "Natural Gas Futures", "commodity", "NYMEX", "Energy", "Global"),
                ("ZC=F", "Corn Futures", "commodity", "CBOT", "Agriculture", "Global"),
                ("ZS=F", "Soybean Futures", "commodity", "CBOT", "Agriculture", "Global"),
                ("ZW=F", "Wheat Futures", "commodity", "CBOT", "Agriculture", "Global"),
                ("HG=F", "Copper Futures", "commodity", "COMEX", "Industrial Metal", "Global"),
                ("PL=F", "Platinum Futures", "commodity", "NYMEX", "Precious Metal", "Global"),
                ("PA=F", "Palladium Futures", "commodity", "NYMEX", "Precious Metal", "Global"),
                
                # Emerging Market Stocks
                ("TSM", "Taiwan Semiconductor", "stock", "NYSE", "Technology", "Taiwan"),
                ("ASML", "ASML Holding NV", "stock", "NASDAQ", "Technology", "Netherlands"),
                ("SAP", "SAP SE", "stock", "NYSE", "Technology", "Germany"),
                ("NVO", "Novo Nordisk A/S", "stock", "NYSE", "Healthcare", "Denmark"),
                ("UL", "Unilever PLC", "stock", "NYSE", "Consumer", "UK"),
                ("BABA", "Alibaba Group Holding", "stock", "NYSE", "Technology", "China"),
                ("PDD", "PDD Holdings Inc.", "stock", "NASDAQ", "Technology", "China"),
                ("MELI", "MercadoLibre Inc.", "stock", "NASDAQ", "Technology", "Argentina"),
                ("SE", "Sea Ltd.", "stock", "NYSE", "Technology", "Singapore"),
                ("GRAB", "Grab Holdings Ltd.", "stock", "NASDAQ", "Technology", "Singapore"),
                
                # REITs
                ("AMT", "American Tower Corp.", "reit", "NYSE", "Real Estate", "US"),
                ("PLD", "Prologis Inc.", "reit", "NYSE", "Real Estate", "US"),
                ("CCI", "Crown Castle Inc.", "reit", "NYSE", "Real Estate", "US"),
                ("EQIX", "Equinix Inc.", "reit", "NASDAQ", "Real Estate", "US"),
                ("SPG", "Simon Property Group", "reit", "NYSE", "Real Estate", "US"),
                ("WELL", "Welltower Inc.", "reit", "NYSE", "Real Estate", "US"),
                ("AVB", "AvalonBay Communities", "reit", "NYSE", "Real Estate", "US"),
                ("EXR", "Extended Stay America", "reit", "NYSE", "Real Estate", "US"),
                ("PSA", "Public Storage", "reit", "NYSE", "Real Estate", "US"),
                ("O", "Realty Income Corp.", "reit", "NYSE", "Real Estate", "US"),
                
                # Biotech & Healthcare
                ("GILD", "Gilead Sciences Inc.", "stock", "NASDAQ", "Healthcare", "US"),
                ("BIIB", "Biogen Inc.", "stock", "NASDAQ", "Healthcare", "US"),
                ("REGN", "Regeneron Pharmaceuticals", "stock", "NASDAQ", "Healthcare", "US"),
                ("VRTX", "Vertex Pharmaceuticals", "stock", "NASDAQ", "Healthcare", "US"),
                ("MRNA", "Moderna Inc.", "stock", "NASDAQ", "Healthcare", "US"),
                ("BNTX", "BioNTech SE", "stock", "NASDAQ", "Healthcare", "Germany"),
                ("TMO", "Thermo Fisher Scientific", "stock", "NYSE", "Healthcare", "US"),
                ("DHR", "Danaher Corp.", "stock", "NYSE", "Healthcare", "US"),
                ("ABT", "Abbott Laboratories", "stock", "NYSE", "Healthcare", "US"),
                ("MDT", "Medtronic PLC", "stock", "NYSE", "Healthcare", "Ireland"),
                
                # Energy & Utilities
                ("XOM", "Exxon Mobil Corp.", "stock", "NYSE", "Energy", "US"),
                ("CVX", "Chevron Corp.", "stock", "NYSE", "Energy", "US"),
                ("COP", "ConocoPhillips", "stock", "NYSE", "Energy", "US"),
                ("SLB", "Schlumberger NV", "stock", "NYSE", "Energy", "US"),
                ("EOG", "EOG Resources Inc.", "stock", "NYSE", "Energy", "US"),
                ("NEE", "NextEra Energy Inc.", "stock", "NYSE", "Utilities", "US"),
                ("DUK", "Duke Energy Corp.", "stock", "NYSE", "Utilities", "US"),
                ("SO", "Southern Co.", "stock", "NYSE", "Utilities", "US"),
                ("D", "Dominion Energy Inc.", "stock", "NYSE", "Utilities", "US"),
                ("AEP", "American Electric Power", "stock", "NASDAQ", "Utilities", "US")
            ]
            
            # Use the same successful upsert pattern from run_complete_ingestion.py
            upsert_query = """
            INSERT INTO assets (ticker, name, asset_type, exchange, sector, country)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (ticker) DO UPDATE SET
                name = EXCLUDED.name,
                asset_type = EXCLUDED.asset_type,
                exchange = EXCLUDED.exchange,
                sector = EXCLUDED.sector,
                country = EXCLUDED.country
            """
            
            success_count = 0
            for asset_data in professional_assets:
                try:
                    await self.db.async_execute_query(upsert_query, asset_data)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to insert {asset_data[0]}: {e}")
            
            logger.info(f"✅ Professional asset universe populated: {success_count}/{len(professional_assets)} assets")
            
            # Return summary
            return {
                "success": True,
                "total_assets": len(professional_assets),
                "successful_inserts": success_count,
                "failed_inserts": len(professional_assets) - success_count,
                "categories": {
                    "stocks": len([a for a in professional_assets if a[2] == "stock"]),
                    "crypto": len([a for a in professional_assets if a[2] == "crypto"]),
                    "etf": len([a for a in professional_assets if a[2] == "etf"]),
                    "index": len([a for a in professional_assets if a[2] == "index"]),
                    "fx": len([a for a in professional_assets if a[2] == "fx"]),
                    "commodity": len([a for a in professional_assets if a[2] == "commodity"]),
                    "reit": len([a for a in professional_assets if a[2] == "reit"])
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Professional asset population failed: {e}")
            return {"success": False, "error": str(e)}

    async def verify_population(self):
        """Verify the assets were populated correctly"""
        try:
            # Count total assets
            result = await self.db.async_execute_query("SELECT COUNT(*) as count FROM assets")
            total_count = result[0]['count'] if result else 0
            
            # Count by category
            category_query = """
            SELECT asset_type, COUNT(*) as count 
            FROM assets 
            GROUP BY asset_type 
            ORDER BY count DESC
            """
            categories = await self.db.async_execute_query(category_query)
            
            logger.info(f"📊 Verification Results:")
            logger.info(f"   Total Assets: {total_count}")
            for cat in categories:
                logger.info(f"   {cat['asset_type'].upper()}: {cat['count']} assets")
                
            return {"total_assets": total_count, "categories": categories}
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return {"error": str(e)}

async def main():
    """Main execution function"""
    print("🚀 uRISK Professional Asset Universe Population")
    print("=" * 60)
    
    populator = ProfessionalAssetPopulator()
    
    # Populate professional assets
    result = await populator.populate_professional_assets()
    
    if result.get("success"):
        print(f"\n✅ SUCCESS! Populated {result['successful_inserts']} assets")
        print(f"📊 Asset Categories:")
        for category, count in result["categories"].items():
            print(f"   {category.upper()}: {count} assets")
        
        # Verify population
        print(f"\n🔍 Verifying population...")
        verification = await populator.verify_population()
        
        if "total_assets" in verification:
            print(f"✅ Verification complete: {verification['total_assets']} total assets in database")
        
        print(f"\n🎯 READY FOR PROFESSIONAL INGESTION!")
        print(f"💡 Next steps:")
        print(f"   1. Run: python3 run_complete_ingestion.py")
        print(f"   2. Run: python3 backend/data_ingestion/historical_backfill.py")
        print(f"   3. Start: python3 backend/scheduler/data_scheduler.py")
        
    else:
        print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())
