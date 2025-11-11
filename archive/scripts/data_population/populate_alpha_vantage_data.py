#!/usr/bin/env python3
"""
Comprehensive Alpha Vantage Data Population Script
Immense data ingestion for Top 200 global companies using all Alpha Vantage APIs
Populates both PostgreSQL and ChromaDB with comprehensive financial data
"""

import asyncio
import sys
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import time
import traceback

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_alpha_vantage_collector import EnhancedAlphaVantageCollector, get_alpha_vantage_config
from top_200_companies import TOP_200_COMPANIES, US_TRADEABLE_SYMBOLS, MEGA_CAP_SYMBOLS, LARGE_CAP_SYMBOLS, MID_CAP_SYMBOLS
from backend.db.postgres_handler import PostgresHandler
from backend.embeddings.vector_store import ChromaVectorStore

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('alpha_vantage_population.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AlphaVantageDataPopulator:
    """
    Comprehensive Alpha Vantage data populator
    Handles massive data ingestion with intelligent prioritization and rate limiting
    """
    
    def __init__(self):
        self.db = PostgresHandler()
        self.vector_store = ChromaVectorStore()
        self.config = get_alpha_vantage_config()
        self.total_metrics = {
            "start_time": datetime.now(),
            "companies_processed": 0,
            "total_api_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "data_points_collected": 0,
            "vector_embeddings_created": 0,
            "errors": []
        }
    
    async def setup_database(self):
        """Setup enhanced database schema"""
        logger.info("🏗️ Setting up enhanced database schema...")
        
        try:
            # Read and execute enhanced schema
            with open('enhanced_alpha_vantage_schema.sql', 'r') as f:
                schema_sql = f.read()
            
            # Execute schema in chunks (split by semicolons)
            sql_statements = schema_sql.split(';')
            
            for statement in sql_statements:
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        await self.db.async_execute_query(statement + ';')
                    except Exception as e:
                        if "already exists" not in str(e).lower():
                            logger.warning(f"Schema statement failed: {e}")
            
            logger.info("✅ Database schema setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up database schema: {e}")
            raise
    
    async def populate_top_companies_metadata(self):
        """Populate top 200 companies metadata in assets table"""
        logger.info("📊 Populating top 200 companies metadata...")
        
        try:
            # Clear existing top companies data
            await self.db.async_execute_query("""
                DELETE FROM assets WHERE ticker IN (
                    SELECT unnest($1::text[])
                )
            """, (US_TRADEABLE_SYMBOLS,))
            
            # Insert top 200 companies
            for company in TOP_200_COMPANIES:
                if company["symbol"] in US_TRADEABLE_SYMBOLS:
                    try:
                        await self.db.async_execute_query("""
                            INSERT INTO assets (ticker, name, asset_type, exchange, sector, country)
                            VALUES ($1, $2, $3, $4, $5, $6)
                            ON CONFLICT (ticker) DO UPDATE SET
                                name = EXCLUDED.name,
                                asset_type = EXCLUDED.asset_type,
                                exchange = EXCLUDED.exchange,
                                sector = EXCLUDED.sector,
                                country = EXCLUDED.country
                        """, (
                            company["symbol"],
                            company["company"],
                            "stock",
                            "US",  # Assuming US exchange for tradeable symbols
                            "Unknown",  # Will be updated from fundamental data
                            "US"
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to insert company {company['symbol']}: {e}")
            
            logger.info(f"✅ Populated metadata for {len(US_TRADEABLE_SYMBOLS)} companies")
            
        except Exception as e:
            logger.error(f"Error populating companies metadata: {e}")
            raise
    
    async def collect_tier_data(self, tier: str, collector: EnhancedAlphaVantageCollector) -> Dict[str, Any]:
        """Collect data for a specific market cap tier"""
        logger.info(f"🎯 Collecting data for {tier} cap companies...")
        
        tier_results = await collector.collect_comprehensive_data(focus_tier=tier)
        
        # Update metrics
        if "metrics" in tier_results:
            metrics = tier_results["metrics"]
            self.total_metrics["total_api_calls"] += metrics.get("total_api_calls", 0)
            self.total_metrics["successful_calls"] += metrics.get("successful_calls", 0)
            self.total_metrics["failed_calls"] += metrics.get("failed_calls", 0)
            self.total_metrics["data_points_collected"] += metrics.get("data_points_collected", 0)
            self.total_metrics["vector_embeddings_created"] += metrics.get("vector_embeddings_created", 0)
        
        return tier_results
    
    async def collect_supplementary_data(self, collector: EnhancedAlphaVantageCollector) -> Dict[str, Any]:
        """Collect supplementary market data (forex, crypto, commodities, economic indicators)"""
        logger.info("🌍 Collecting supplementary market data...")
        
        supplementary_results = {
            "forex": {},
            "crypto": {},
            "commodities": {},
            "economic_indicators": {},
            "market_status": {}
        }
        
        try:
            # Forex data
            logger.info("💱 Collecting forex data...")
            supplementary_results["forex"] = await collector.collect_forex_data()
            await asyncio.sleep(2)  # Rate limiting
            
            # Crypto data  
            logger.info("₿ Collecting crypto data...")
            supplementary_results["crypto"] = await collector.collect_crypto_data()
            await asyncio.sleep(2)
            
            # Commodities data
            logger.info("🛢️ Collecting commodities data...")
            supplementary_results["commodities"] = await collector.collect_commodities_data()
            await asyncio.sleep(2)
            
            # Economic indicators
            logger.info("🏛️ Collecting economic indicators...")
            supplementary_results["economic_indicators"] = await collector.collect_economic_indicators()
            
        except Exception as e:
            logger.error(f"Error collecting supplementary data: {e}")
            self.total_metrics["errors"].append(f"Supplementary data error: {e}")
        
        return supplementary_results
    
    async def run_comprehensive_population(self, tiers: List[str] = ["mega", "large", "mid"]):
        """
        Run comprehensive data population for specified tiers
        tiers: List of tiers to process ['mega', 'large', 'mid']
        """
        logger.info("🚀 STARTING COMPREHENSIVE ALPHA VANTAGE DATA POPULATION")
        logger.info("=" * 80)
        logger.info(f"Target Tiers: {', '.join(tiers)}")
        logger.info(f"Total US Tradeable Symbols: {len(US_TRADEABLE_SYMBOLS)}")
        logger.info(f"API Key Available: {'Yes' if self.config.api_key != 'demo' else 'No (using demo)'}")
        logger.info(f"Premium Tier: {'Yes' if self.config.premium_tier else 'No'}")
        logger.info("=" * 80)
        
        try:
            # 1. Setup database schema
            await self.setup_database()
            
            # 2. Populate company metadata
            await self.populate_top_companies_metadata()
            
            # 3. Initialize collector
            async with EnhancedAlphaVantageCollector(self.config) as collector:
                
                # 4. Process each tier
                tier_results = {}
                
                for tier in tiers:
                    try:
                        logger.info(f"\n🎯 Processing {tier.upper()} cap companies...")
                        tier_results[tier] = await self.collect_tier_data(tier, collector)
                        
                        # Update companies processed count
                        if tier == "mega":
                            self.total_metrics["companies_processed"] += len(MEGA_CAP_SYMBOLS)
                        elif tier == "large":
                            self.total_metrics["companies_processed"] += len(LARGE_CAP_SYMBOLS)
                        elif tier == "mid":
                            self.total_metrics["companies_processed"] += len(MID_CAP_SYMBOLS)
                        
                        logger.info(f"✅ Completed {tier} cap companies data collection")
                        
                        # Pause between tiers to respect rate limits
                        logger.info("⏸️ Pausing for rate limit management...")
                        await asyncio.sleep(10)
                        
                    except Exception as e:
                        logger.error(f"Error processing {tier} tier: {e}")
                        self.total_metrics["errors"].append(f"Tier {tier} error: {e}")
                        continue
                
                # 5. Collect supplementary data (forex, crypto, commodities, economic)
                supplementary_results = await self.collect_supplementary_data(collector)
                
                # 6. Final data summary and metrics
                await self.generate_final_report(tier_results, supplementary_results)
                
        except Exception as e:
            logger.error(f"Critical error in comprehensive population: {e}")
            logger.error(traceback.format_exc())
            self.total_metrics["errors"].append(f"Critical error: {e}")
            raise
    
    async def generate_final_report(self, tier_results: Dict, supplementary_results: Dict):
        """Generate comprehensive final report"""
        end_time = datetime.now()
        runtime = (end_time - self.total_metrics["start_time"]).total_seconds()
        
        logger.info("\n" + "="*100)
        logger.info("🏆 COMPREHENSIVE ALPHA VANTAGE DATA POPULATION COMPLETED")
        logger.info("="*100)
        
        # Summary statistics
        logger.info("📊 SUMMARY STATISTICS:")
        logger.info(f"   🏢 Companies Processed: {self.total_metrics['companies_processed']}")
        logger.info(f"   📞 Total API Calls: {self.total_metrics['total_api_calls']}")
        logger.info(f"   ✅ Successful Calls: {self.total_metrics['successful_calls']}")
        logger.info(f"   ❌ Failed Calls: {self.total_metrics['failed_calls']}")
        logger.info(f"   📈 Success Rate: {(self.total_metrics['successful_calls'] / max(1, self.total_metrics['total_api_calls'])) * 100:.1f}%")
        logger.info(f"   💾 Data Points Collected: {self.total_metrics['data_points_collected']:,}")
        logger.info(f"   🔢 Vector Embeddings Created: {self.total_metrics['vector_embeddings_created']:,}")
        logger.info(f"   ⏱️ Total Runtime: {runtime:.1f} seconds ({runtime/60:.1f} minutes)")
        
        # Tier breakdown
        logger.info("\n📋 TIER BREAKDOWN:")
        for tier, results in tier_results.items():
            if "metrics" in results:
                metrics = results["metrics"]
                logger.info(f"   📊 {tier.upper()} Cap:")
                logger.info(f"      • API Calls: {metrics.get('total_api_calls', 0)}")
                logger.info(f"      • Success Rate: {metrics.get('success_rate', 0)*100:.1f}%")
                logger.info(f"      • Data Points: {metrics.get('data_points_collected', 0):,}")
                logger.info(f"      • Embeddings: {metrics.get('vector_embeddings_created', 0):,}")
        
        # Data categories collected
        logger.info("\n🗂️ DATA CATEGORIES COLLECTED:")
        for tier, results in tier_results.items():
            for category, data in results.items():
                if category != "metrics" and data:
                    if isinstance(data, dict):
                        count = len(data)
                    elif isinstance(data, list):
                        count = len(data)
                    else:
                        count = 1
                    
                    if count > 0:
                        logger.info(f"   ✅ {category} ({tier}): {count} items")
        
        # Supplementary data
        logger.info("\n🌍 SUPPLEMENTARY DATA:")
        for category, data in supplementary_results.items():
            if data and isinstance(data, dict):
                logger.info(f"   ✅ {category}: {len(data)} items")
        
        # Database summary
        try:
            await self.log_database_summary()
        except Exception as e:
            logger.warning(f"Could not generate database summary: {e}")
        
        # Errors summary
        if self.total_metrics["errors"]:
            logger.info(f"\n⚠️ ERRORS ENCOUNTERED ({len(self.total_metrics['errors'])}):")
            for error in self.total_metrics["errors"][:10]:  # Show first 10 errors
                logger.info(f"   • {error}")
        
        # Save detailed report to file
        report_data = {
            "summary": self.total_metrics,
            "tier_results": tier_results,
            "supplementary_results": supplementary_results,
            "runtime_seconds": runtime,
            "completion_time": end_time.isoformat()
        }
        
        report_filename = f"alpha_vantage_population_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"\n💾 Detailed report saved to: {report_filename}")
        logger.info("="*100)
    
    async def log_database_summary(self):
        """Log database summary statistics"""
        try:
            # Count records in key tables
            tables_to_check = [
                "assets", "market_prices", "fundamental_data", "news_headlines",
                "earnings_data", "forex_prices", "crypto_prices", "commodities_prices",
                "economic_indicators", "technical_indicators"
            ]
            
            logger.info("\n💾 DATABASE SUMMARY:")
            
            for table in tables_to_check:
                try:
                    count = await self.db.async_fetch_scalar(f"SELECT COUNT(*) FROM {table}")
                    logger.info(f"   📊 {table}: {count:,} records")
                except Exception as e:
                    logger.info(f"   ❌ {table}: Error ({e})")
            
            # Check vector database status
            try:
                vector_count = await self.vector_store.get_collection_size()
                logger.info(f"   🔢 Vector Database: {vector_count:,} embeddings")
            except Exception as e:
                logger.info(f"   🔢 Vector Database: Error ({e})")
                
        except Exception as e:
            logger.error(f"Error generating database summary: {e}")

async def main():
    """Main execution function with command line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Alpha Vantage Data Population")
    parser.add_argument("--tiers", nargs="+", default=["mega"], 
                       choices=["mega", "large", "mid", "all"],
                       help="Market cap tiers to process (default: mega)")
    parser.add_argument("--demo", action="store_true",
                       help="Run with limited demo data (for testing)")
    
    args = parser.parse_args()
    
    # Handle 'all' tier option
    if "all" in args.tiers:
        tiers = ["mega", "large", "mid"]
    else:
        tiers = args.tiers
    
    # Validate Alpha Vantage API key
    config = get_alpha_vantage_config()
    if config.api_key == "demo" and not args.demo:
        logger.warning("⚠️ ALPHA_VANTAGE_API_KEY not found in environment!")
        logger.warning("   Set your API key: export ALPHA_VANTAGE_API_KEY='your_key_here'")
        logger.warning("   Get free API key: https://www.alphavantage.co/support/#api-key")
        logger.warning("   Running with demo key (limited data)...")
        
        # Give user option to continue
        if input("\nContinue with demo key? (y/N): ").lower() != 'y':
            logger.info("Exiting. Please set your Alpha Vantage API key and try again.")
            return
    
    # Start population
    populator = AlphaVantageDataPopulator()
    
    try:
        await populator.run_comprehensive_population(tiers)
        logger.info("🎉 Data population completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("\n⏸️ Population interrupted by user")
    except Exception as e:
        logger.error(f"💥 Population failed: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    asyncio.run(main())
