#!/usr/bin/env python3
"""
PostgreSQL to ChromaDB Data Ingestion Pipeline
Pure data ingestion focus - no RAG retrieval logic.

Commands:
    python run_vectordb_ingestion.py sync      # Run incremental ingestion 
    python run_vectordb_ingestion.py full      # Run full historical ingestion
    python run_vectordb_ingestion.py status    # Check ingestion status
    python run_vectordb_ingestion.py reset     # Reset sync state (re-ingest all)
"""

import asyncio
import logging
import argparse
import json
from datetime import datetime
from pathlib import Path

# Add the backend directory to Python path
import sys
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.services.postgres_to_vectordb import postgres_to_vectordb_pipeline
from backend.rag_engine.vector_store import vector_store

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('postgres_to_vectordb_ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def run_incremental_ingestion():
    """Run incremental data ingestion."""
    try:
        logger.info("🚀 Starting PostgreSQL → ChromaDB Data Ingestion")
        logger.info("=" * 60)
        
        # Initialize pipeline
        logger.info("📊 Initializing ingestion pipeline...")
        await postgres_to_vectordb_pipeline.initialize()
        
        # Run sync
        logger.info("🔄 Running incremental data ingestion...")
        sync_stats = await postgres_to_vectordb_pipeline.run_full_sync()
        
        # Display results
        logger.info("📈 Ingestion Results:")
        logger.info("-" * 40)
        
        if sync_stats.get("success", False):
            alpha_stats = sync_stats.get("alpha_vantage", {})
            logger.info(f"✅ Records Processed: {alpha_stats.get('processed', 0)}")
            logger.info(f"📁 Chunks Created: {alpha_stats.get('chunks_created', 0)}")
            logger.info(f"❌ Errors: {alpha_stats.get('errors', 0)}")
            logger.info(f"⏱️  Time: {sync_stats.get('total_time', 0):.1f}s")
        else:
            logger.error(f"❌ Ingestion failed: {sync_stats.get('error', 'Unknown error')}")
        
        return sync_stats
        
    except Exception as e:
        logger.error(f"💥 Ingestion pipeline failed: {e}")
        raise

async def run_full_historical_ingestion():
    """Run full historical data ingestion (process ALL data in batches)."""
    try:
        logger.info("🔥 Starting FULL Historical Data Ingestion")
        logger.info("⚠️  This will reset sync state and re-ingest all data")
        logger.info("=" * 60)
        
        # Initialize pipeline
        await postgres_to_vectordb_pipeline.initialize()
        
        # Reset sync state
        logger.info("🔄 Resetting sync state...")
        await postgres_to_vectordb_pipeline.postgres.async_execute_insert(
            "DELETE FROM vector_sync_state WHERE table_name = 'alpha_vantage_data'"
        )
        
        # Get total record count
        total_records_query = await postgres_to_vectordb_pipeline.postgres.async_execute_query(
            "SELECT COUNT(*) as count FROM alpha_vantage_data"
        )
        total_records = total_records_query[0]['count'] if total_records_query else 0
        logger.info(f"� Total records to process: {total_records:,}")
        
        # Process in batches until all data is ingested
        total_processed = 0
        total_chunks = 0
        total_errors = 0
        batch_num = 1
        
        while total_processed < total_records:
            logger.info(f"🔄 Processing batch {batch_num} (records {total_processed:,} - {min(total_processed + 5000, total_records):,})")
            
            # Run sync batch
            sync_stats = await postgres_to_vectordb_pipeline.sync_alpha_vantage_data(limit_per_batch=5000)
            
            # Update totals
            batch_processed = sync_stats.get('processed', 0)
            batch_chunks = sync_stats.get('chunks_created', 0)
            batch_errors = sync_stats.get('errors', 0)
            
            total_processed += batch_processed
            total_chunks += batch_chunks
            total_errors += batch_errors
            
            # Progress report
            progress = (total_processed / total_records) * 100
            logger.info(f"📈 Batch {batch_num} complete: +{batch_processed:,} records, +{batch_chunks:,} chunks ({progress:.1f}% total)")
            
            # Stop if no more records processed
            if batch_processed == 0:
                logger.info("✅ No more records to process")
                break
                
            batch_num += 1
            
            # Small delay to avoid overwhelming the system
            await asyncio.sleep(1)
        
        logger.info("🎉 FULL Historical Ingestion Complete!")
        logger.info("=" * 60)
        logger.info(f"📊 Total Records Processed: {total_processed:,}")
        logger.info(f"📁 Total Chunks Created: {total_chunks:,}")
        logger.info(f"❌ Total Errors: {total_errors:,}")
        logger.info(f"🎯 Final Progress: {(total_processed/total_records)*100:.1f}%")
        
        return {
            "success": True,
            "total_processed": total_processed,
            "total_chunks": total_chunks,
            "total_errors": total_errors,
            "progress_percent": (total_processed/total_records)*100
        }
        
    except Exception as e:
        logger.error(f"💥 Full ingestion failed: {e}")
        raise

async def get_ingestion_status():
    """Get ingestion pipeline status."""
    try:
        logger.info("📊 Data Ingestion Status")
        logger.info("-" * 40)
        
        # Initialize components
        await postgres_to_vectordb_pipeline.initialize()
        vector_store.initialize()
        
        # Get vector store stats
        vector_stats = vector_store.get_collection_stats()
        logger.info(f"📁 Vector Store Documents: {vector_stats.get('count', 0)}")
        logger.info(f"📚 Collection Name: {vector_stats.get('name', 'unknown')}")
        
        # Get sync state from database
        sync_state = await postgres_to_vectordb_pipeline.get_sync_state("alpha_vantage_data")
        if sync_state.last_synced_at:
            logger.info(f"🕐 Last Sync: {sync_state.last_synced_at}")
            logger.info(f"📊 Records Synced: {sync_state.records_synced}")
        else:
            logger.info("🔄 No previous sync found")
        
        # Check source data count
        total_records = await postgres_to_vectordb_pipeline.postgres.async_execute_query(
            "SELECT COUNT(*) as count FROM alpha_vantage_data"
        )
        source_count = total_records[0]['count'] if total_records else 0
        logger.info(f"💾 Source Records Available: {source_count}")
        
        progress = vector_stats.get('count', 0) / max(source_count, 1) * 100
        logger.info(f"🎯 Ingestion Progress: {vector_stats.get('count', 0)}/{source_count} ({progress:.1f}%)")
        
        return {
            "vector_store_count": vector_stats.get('count', 0),
            "source_records": source_count,
            "last_sync": sync_state.last_synced_at,
            "records_synced": sync_state.records_synced,
            "progress_percent": progress
        }
        
    except Exception as e:
        logger.error(f"💥 Status check failed: {e}")
        raise

async def reset_ingestion_state():
    """Reset sync state to re-ingest all data."""
    try:
        logger.info("🔄 Resetting Ingestion State")
        logger.info("-" * 40)
        
        await postgres_to_vectordb_pipeline.initialize()
        
        # Reset sync state
        await postgres_to_vectordb_pipeline.postgres.async_execute_insert(
            "DELETE FROM vector_sync_state"
        )
        
        logger.info("✅ Sync state reset complete")
        logger.info("💡 Run 'sync' or 'full' command to start fresh ingestion")
        
    except Exception as e:
        logger.error(f"💥 Reset failed: {e}")
        raise

async def sample_data_preview():
    """Preview a sample of ingested data."""
    try:
        logger.info("👀 Sample Data Preview")
        logger.info("-" * 40)
        
        vector_store.initialize()
        
        # Query for some sample NVDA data
        results = vector_store.query_documents(
            query_texts=["NVDA technical analysis"],
            n_results=5,
            where={"ticker": "NVDA"}
        )
        
        if results and results.get('documents') and results['documents'][0]:
            logger.info("📋 Sample NVDA Chunks:")
            for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
                logger.info(f"{i}. {meta.get('endpoint', 'N/A')} | {meta.get('timestamp', 'N/A')}")
                logger.info(f"   {doc[:100]}...")
                logger.info("")
        else:
            logger.info("No sample data found")
        
    except Exception as e:
        logger.error(f"💥 Sample preview failed: {e}")
        raise

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PostgreSQL to ChromaDB Data Ingestion Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_vectordb_ingestion.py sync      # Incremental ingestion
  python run_vectordb_ingestion.py full      # Full historical ingestion  
  python run_vectordb_ingestion.py status    # Check ingestion status
  python run_vectordb_ingestion.py reset     # Reset sync state
  python run_vectordb_ingestion.py preview   # Preview sample data
        """
    )
    
    parser.add_argument('command', 
                       choices=['sync', 'full', 'status', 'reset', 'preview'], 
                       help='Command to run')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'sync':
            await run_incremental_ingestion()
            
        elif args.command == 'full':
            await run_full_historical_ingestion()
            
        elif args.command == 'status':
            await get_ingestion_status()
            
        elif args.command == 'reset':
            await reset_ingestion_state()
            
        elif args.command == 'preview':
            await sample_data_preview()
            
        logger.info("🎉 Command completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Command failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
