#!/usr/bin/env python3
"""
PostgreSQL to ChromaDB Data Ingestion Pipeline
Pure ingestion focus - no RAG retrieval logic.

Commands:
    python run_vectordb_sync.py sync      # Run incremental ingestion 
    python run_vectordb_sync.py full      # Run full historical ingestion
    python run_vectordb_sync.py status    # Check ingestion status
    python run_vectordb_sync.py reset     # Reset sync state (re-ingest all)
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
        logging.FileHandler('postgres_to_vectordb_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def run_pipeline_sync():
    """Run the full pipeline sync."""
    try:
        logger.info("🚀 Starting PostgreSQL → ChromaDB Sync Pipeline")
        logger.info("=" * 60)
        
        # Initialize pipeline
        logger.info("📊 Initializing pipeline components...")
        await postgres_to_vectordb_pipeline.initialize()
        
        # Run sync
        logger.info("🔄 Running incremental sync...")
        sync_stats = await postgres_to_vectordb_pipeline.run_full_sync()
        
        # Display results
        logger.info("📈 Sync Results:")
        logger.info("-" * 40)
        
        if sync_stats.get("success", False):
            alpha_stats = sync_stats.get("alpha_vantage", {})
            
            logger.info(f"✅ Alpha Vantage Records Processed: {alpha_stats.get('processed', 0)}")
            logger.info(f"✅ Chunks Created: {alpha_stats.get('chunks_created', 0)}")
            logger.info(f"❌ Errors: {alpha_stats.get('errors', 0)}")
            logger.info(f"⏱️  Total Time: {sync_stats.get('total_time', 0):.1f} seconds")
            
            if alpha_stats.get('chunks_created', 0) > 0:
                logger.info(f"🎯 Average Speed: {alpha_stats.get('chunks_created', 0) / max(sync_stats.get('total_time', 1), 1):.1f} chunks/second")
            
        else:
            logger.error(f"❌ Sync failed: {sync_stats.get('error', 'Unknown error')}")
        
        # Get final vector store stats
        from backend.rag_engine.vector_store import vector_store
        vector_stats = vector_store.get_collection_stats()
        
        logger.info("🗃️  ChromaDB Status:")
        logger.info(f"   Total Documents: {vector_stats.get('count', 0)}")
        logger.info(f"   Collection: {vector_stats.get('name', 'unknown')}")
        
        logger.info("=" * 60)
        logger.info("✅ Pipeline sync completed!")
        
        return sync_stats
        
    except Exception as e:
        logger.error(f"💥 Pipeline failed: {e}")
        raise

async def test_rag_query(query: str = "What is NVDA's latest RSI?"):
    """Test the RAG pipeline with a sample query."""
    try:
        logger.info(f"🧪 Testing RAG query: '{query}'")
        
        # Initialize RAG service
        await rag_service.initialize()
        
        # Run query
        response = await rag_service.query(query)
        
        logger.info("🎯 RAG Query Results:")
        logger.info("-" * 40)
        logger.info(f"Reply: {response.get('reply', 'No reply')}")
        logger.info(f"Confidence: {response.get('confidence', 0):.2f}")
        logger.info(f"Ticker: {response.get('ticker', 'Not detected')}")
        logger.info(f"Context Chunks: {response.get('context_chunks_used', 0)}")
        
        evidence_sources = response.get('evidence_sources', [])
        if evidence_sources:
            logger.info("📚 Evidence Sources:")
            for i, source in enumerate(evidence_sources[:3], 1):
                logger.info(f"  {i}. {source.get('ticker', 'N/A')} {source.get('risk_type', 'N/A')} "
                          f"(score: {source.get('relevance_score', 0):.2f})")
                logger.info(f"     {source.get('snippet', '')[:80]}...")
        
        return response
        
    except Exception as e:
        logger.error(f"💥 RAG query test failed: {e}")
        raise

async def get_system_status():
    """Get comprehensive system status."""
    try:
        logger.info("📊 System Status Check")
        logger.info("-" * 40)
        
        await rag_service.initialize()
        status = await rag_service.get_system_status()
        
        logger.info(f"System Status: {status.get('status', 'unknown')}")
        
        vector_stats = status.get('vector_store', {})
        logger.info(f"Vector Store Documents: {vector_stats.get('count', 0)}")
        
        retriever_stats = status.get('retriever', {})
        embedder_info = retriever_stats.get('embedder', {})
        logger.info(f"Embedder Model: {embedder_info.get('model_name', 'unknown')}")
        logger.info(f"Embedding Dimension: {embedder_info.get('embedding_dimension', 0)}")
        
        pipeline_ready = status.get('pipeline_ready', False)
        logger.info(f"Pipeline Ready: {'✅' if pipeline_ready else '❌'}")
        
        return status
        
    except Exception as e:
        logger.error(f"💥 Status check failed: {e}")
        raise

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="PostgreSQL to ChromaDB Sync Pipeline")
    parser.add_argument('command', choices=['sync', 'test', 'status'], 
                       help='Command to run')
    parser.add_argument('--query', type=str, default="What is NVDA's latest RSI?",
                       help='Test query for RAG (only used with test command)')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'sync':
            await run_pipeline_sync()
            
        elif args.command == 'test':
            await test_rag_query(args.query)
            
        elif args.command == 'status':
            await get_system_status()
            
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
