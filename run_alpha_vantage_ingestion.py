#!/usr/bin/env python3
"""
Alpha Vantage 200-Batch, Epoch-Based Ingestion System
Enterprise-grade, fault-tolerant data ingestion for 200 global tickers

Usage:
    python run_alpha_vantage_ingestion.py [--start-epoch 1] [--max-epochs 10] [--resume]

Examples:
    python run_alpha_vantage_ingestion.py                    # Full ingestion
    python run_alpha_vantage_ingestion.py --max-epochs 5    # Test with 5 companies
    python run_alpha_vantage_ingestion.py --resume          # Resume from checkpoint
    python run_alpha_vantage_ingestion.py --start-epoch 50  # Start from epoch 50
"""

import asyncio
import argparse
import sys
import logging
import os
from datetime import datetime
from pathlib import Path

# Add backend to Python path
sys.path.append(str(Path(__file__).parent / 'backend'))

from backend.config.settings import settings
from backend.data_ingestion.alpha_ingestion_manager import AlphaIngestionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'alpha_ingestion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def validate_environment():
    """Validate that all required environment variables are set"""
    logger.info("🔍 Validating environment configuration...")
    
    # Check required API keys
    missing_keys = settings.validate_required_keys()
    if missing_keys:
        logger.error("❌ Missing required API keys:")
        for key in missing_keys:
            logger.error(f"   - {key}")
        logger.error("💡 Please set these environment variables or add them to .env file")
        return False
    
    # Check Alpha Vantage API key specifically
    if not settings.ALPHA_VANTAGE_API_KEY or settings.ALPHA_VANTAGE_API_KEY == "demo":
        logger.warning("⚠️ Using demo Alpha Vantage API key - limited functionality")
        logger.warning("💡 Get a free API key from: https://www.alphavantage.co/support/#api-key")
    
    # Check database configuration
    if not settings.DATABASE_URL or "postgresql://" not in settings.DATABASE_URL:
        logger.error("❌ Invalid DATABASE_URL configuration")
        logger.error("💡 Set DATABASE_URL to a valid PostgreSQL connection string")
        return False
    
    logger.info("✅ Environment validation passed")
    return True

async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Alpha Vantage 200-Batch, Epoch-Based Ingestion System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--start-epoch', 
        type=int, 
        default=1,
        help='Which epoch to start from (for manual restart)'
    )
    
    parser.add_argument(
        '--max-epochs', 
        type=int, 
        help='Maximum number of epochs to run (for testing)'
    )
    
    parser.add_argument(
        '--resume', 
        action='store_true',
        help='Resume from last checkpoint'
    )
    
    parser.add_argument(
        '--test-connectivity', 
        action='store_true',
        help='Test API connectivity and exit'
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Test the configuration without running ingestion'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print("=" * 80)
    print("🚀 Alpha Vantage 200-Batch, Epoch-Based Ingestion System")
    print("   Enterprise-grade, fault-tolerant data ingestion")
    print("=" * 80)
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    # Initialize ingestion manager
    logger.info("🔧 Initializing ingestion manager...")
    manager = AlphaIngestionManager()
    
    try:
        # Test connectivity if requested
        if args.test_connectivity:
            logger.info("🧪 Testing Alpha Vantage API connectivity...")
            test_result = await manager.fetcher.test_api_connectivity()
            
            if test_result['connected']:
                logger.info("✅ API connectivity test passed")
                print(f"   API Key Valid: {test_result['api_key_valid']}")
                print(f"   Test Time: {test_result['test_timestamp']}")
            else:
                logger.error(f"❌ API connectivity test failed: {test_result['error']}")
                sys.exit(1)
            
            return
        
        # Dry run
        if args.dry_run:
            logger.info("🧪 Performing dry run...")
            logger.info(f"📊 Total companies to process: {len(manager.companies)}")
            logger.info(f"🎯 Total endpoints per company: {len(manager.fetcher.get_all_endpoints())}")
            
            if args.max_epochs:
                logger.info(f"🎯 Test mode: processing {args.max_epochs} epochs")
            
            logger.info("✅ Dry run completed - ready for ingestion")
            return
        
        # Resume from checkpoint
        if args.resume:
            logger.info("🔄 Resuming from checkpoint...")
            final_stats = await manager.resume_from_checkpoint()
        else:
            # Run complete ingestion
            final_stats = await manager.run_complete_ingestion(
                start_epoch=args.start_epoch,
                max_epochs=args.max_epochs
            )
        
        # Print completion summary
        print("\n" + "=" * 80)
        print("🎉 ALPHA VANTAGE INGESTION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"📊 Session ID: {final_stats['session_id']}")
        print(f"📈 Total Records: {final_stats['total_records_inserted']:,}")
        print(f"🎯 Total Epochs: {final_stats['total_epochs']}")
        print(f"✅ Successful Epochs: {final_stats['successful_epochs']}")
        print(f"⏱️ Duration: {final_stats['duration_seconds']:.1f} seconds")
        print(f"📈 Ingestion Rate: {final_stats['ingestion_rate_per_second']:.2f} records/second")
        print(f"🔄 Total API Calls: {final_stats['total_api_calls']:,}")
        print(f"❌ Total Errors: {final_stats['total_errors']}")
        print("=" * 80)
        
        # Show top performing epochs
        if final_stats.get('epoch_results'):
            print("\n📊 TOP PERFORMING EPOCHS:")
            epoch_results = final_stats['epoch_results']
            top_epochs = sorted(epoch_results, key=lambda x: x['records'], reverse=True)[:5]
            
            for i, epoch in enumerate(top_epochs, 1):
                print(f"   {i}. {epoch['ticker']}: {epoch['records']:,} records in {epoch['duration']:.1f}s")
        
        logger.info("🎉 Ingestion completed successfully!")
        
    except KeyboardInterrupt:
        print("\n" + "⚠️" * 20)
        print("⚠️ INGESTION INTERRUPTED BY USER")
        print("⚠️" * 20)
        print("💡 Progress has been saved - you can resume by running:")
        print(f"   python {sys.argv[0]} --resume")
        
    except Exception as e:
        print("\n" + "❌" * 20)
        print("❌ INGESTION FAILED")
        print("❌" * 20)
        logger.error(f"💥 Fatal error: {str(e)}")
        
        print("💡 Check the log file for detailed error information")
        print("💡 You can resume from checkpoint by running:")
        print(f"   python {sys.argv[0]} --resume")
        
        sys.exit(1)
    
    finally:
        # Clean up resources
        if hasattr(manager, 'fetcher') and hasattr(manager.fetcher, 'close_session'):
            await manager.fetcher.close_session()
        
        if hasattr(manager, 'db') and hasattr(manager.db, 'close'):
            await manager.db.close()

if __name__ == "__main__":
    # Set event loop policy for Windows compatibility
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Ingestion interrupted by user")
        sys.exit(1)
