#!/usr/bin/env python3
"""
QuantVerse Data Collection Pipeline - Main CLI
Run various data collection modes from command line
"""

import asyncio
import argparse
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data_collection_pipeline.orchestrator import pipeline
from data_collection_pipeline.config import config, PRIORITY_TICKERS
from data_collection_pipeline.utils import setup_logging

async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="QuantVerse Data Collection Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --single-cycle                    # Run one complete collection cycle
  python main.py --scheduled                       # Run continuous scheduled collection
  python main.py --market-only                     # Run only market data collection
  python main.py --news-only                       # Run only news collection
  python main.py --tickers AAPL MSFT GOOGL         # Run with specific tickers
  python main.py --single-cycle --tickers TSLA     # Single cycle for TSLA only
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--single-cycle',
        action='store_true',
        help='Run a single complete data collection cycle'
    )
    mode_group.add_argument(
        '--scheduled',
        action='store_true',
        help='Run continuous scheduled data collection'
    )
    mode_group.add_argument(
        '--market-only',
        action='store_true',
        help='Run only market data collection'
    )
    mode_group.add_argument(
        '--news-only',
        action='store_true',
        help='Run only news collection'
    )
    
    # Configuration options
    parser.add_argument(
        '--tickers',
        nargs='+',
        help='Specific tickers to collect data for (default: priority tickers)'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be collected without actually running'
    )
    
    args = parser.parse_args()
    
    # Override log level if specified
    if args.log_level:
        config.log_level = args.log_level
    
    # Setup logging and get log file path
    log_file_path = setup_logging('pipeline', args.log_level)
    logger = logging.getLogger(__name__)
    
    # Log startup information
    logger.info("=" * 60)
    logger.info("QuantVerse Data Collection Pipeline Starting")
    logger.info(f"Log file: {log_file_path}")
    logger.info(f"Environment: {config.environment}")
    logger.info(f"Database: {config.database.host}:{config.database.port}/{config.database.database}")
    logger.info(f"Log Level: {config.log_level}")
    logger.info("=" * 60)
    
    # Determine tickers to use
    tickers = args.tickers or PRIORITY_TICKERS
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No data will be collected")
        logger.info(f"Would collect data for: {', '.join(tickers)}")
        logger.info(f"Configuration: {config.environment} environment")
        return
    
    logger.info("=" * 60)
    logger.info("🚀 QuantVerse Data Collection Pipeline")
    logger.info("=" * 60)
    logger.info(f"Environment: {config.environment}")
    logger.info(f"Database: {config.database.host}:{config.database.port}/{config.database.database}")
    logger.info(f"Target tickers: {len(tickers)} ({', '.join(tickers[:10])}{'...' if len(tickers) > 10 else ''})")
    
    try:
        # Initialize pipeline
        await pipeline.initialize()
        
        # Run selected mode
        if args.single_cycle:
            logger.info("Running single collection cycle...")
            results = await pipeline.run_single_collection_cycle(tickers)
            
            # Print summary
            print("\n" + "=" * 60)
            print("📊 COLLECTION CYCLE SUMMARY")
            print("=" * 60)
            print(f"Session ID: {results['session_id']}")
            print(f"Duration: {results['duration_seconds']:.1f} seconds")
            print(f"Total Records: {results['total_records']:,}")
            print(f"Total API Calls: {results['total_api_calls']}")
            print(f"Errors: {len(results['errors'])}")
            
            if results['errors']:
                print("\n⚠️  ERRORS:")
                for error in results['errors'][:5]:  # Show first 5 errors
                    print(f"  - {error}")
                if len(results['errors']) > 5:
                    print(f"  ... and {len(results['errors']) - 5} more errors")
            
            print("\n📈 BY COLLECTOR:")
            for collector_name, collector_results in results['collectors'].items():
                print(f"  {collector_name.upper()}:")
                print(f"    Records: {collector_results['total_records']:,}")
                print(f"    API Calls: {collector_results['total_calls']}")
                print(f"    Errors: {len(collector_results['errors'])}")
        
        elif args.scheduled:
            logger.info("Starting scheduled collection pipeline...")
            logger.info("Press Ctrl+C to stop gracefully")
            await pipeline.run_scheduled_pipeline()
        
        elif args.market_only:
            logger.info("Running market data collection only...")
            results = await pipeline.run_market_data_only(tickers)
            
            print(f"\n📈 Market Data Collection Complete:")
            print(f"  Records: {results['total_records']:,}")
            print(f"  API Calls: {results['total_calls']}")
            print(f"  Errors: {len(results['errors'])}")
        
        elif args.news_only:
            logger.info("Running news collection only...")
            results = await pipeline.run_news_only(tickers)
            
            print(f"\n📰 News Collection Complete:")
            print(f"  Records: {results['total_records']:,}")
            print(f"  API Calls: {results['total_calls']}")
            print(f"  Errors: {len(results['errors'])}")
        
        logger.info("Pipeline execution completed successfully")
    
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        print("\n⚠️  Pipeline stopped by user")
    
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        print(f"\n❌ Pipeline failed: {e}")
        sys.exit(1)
    
    finally:
        await pipeline.shutdown()
        logger.info("Pipeline shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
