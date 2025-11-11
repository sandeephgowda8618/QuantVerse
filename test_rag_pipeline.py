#!/usr/bin/env python3
"""
Test Script for RAG Pipeline
Tests the full RAG pipeline without ML components
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add project path
sys.path.append(str(Path(__file__).parent))

from backend.rag_engine.risk_mode.risk_pipeline import RiskAssessmentPipeline
from backend.rag_engine.vector_store import ChromaVectorStore
from backend.rag_engine.risk_mode.risk_cache import RiskCacheManager
from backend.db.postgres_handler import PostgresHandler
from backend.config.settings import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_rag_pipeline():
    """Test the full RAG pipeline"""
    
    logger.info("🚀 Starting RAG Pipeline Test...")
    
    try:
        # Initialize components
        logger.info("Initializing components...")
        
        # Database
        db_handler = PostgresHandler()
        db_handler.initialize_sync_pool()
        
        # Vector store  
        vector_store = ChromaVectorStore()
        vector_store.initialize("./vector_db")  # Initialize the vector store
        
        # Cache manager
        cache_manager = RiskCacheManager()
        
        # Risk assessment pipeline
        pipeline = RiskAssessmentPipeline(
            vector_store=vector_store,
            db_manager=db_handler,
            cache_manager=cache_manager,
            llm_model="llama3.1"  # Use Ollama model
        )
        
        logger.info("✅ Components initialized successfully!")
        
        # Test queries
        test_queries = [
            {
                "query": "What are the current risks for NVDA?", 
                "params": {"ticker": "NVDA", "time_window_hours": 24}
            },
            {
                "query": "Are there any infrastructure risks for MSFT?",
                "params": {"ticker": "MSFT", "time_window_hours": 72}
            },
            {
                "query": "What regulatory risks should I monitor for AAPL?", 
                "params": {"ticker": "AAPL", "time_window_hours": 168}
            }
        ]
        
        # Run tests
        for i, test in enumerate(test_queries, 1):
            logger.info(f"\n📊 Test {i}: {test['query']}")
            logger.info(f"Parameters: {test['params']}")
            
            try:
                start_time = asyncio.get_event_loop().time()
                
                # Run risk assessment
                result = await pipeline.assess_risk(test["query"], test["params"])
                
                end_time = asyncio.get_event_loop().time()
                duration = end_time - start_time
                
                logger.info(f"✅ Test {i} completed in {duration:.2f}s")
                logger.info(f"Risk Score: {result.get('risk_score', 'N/A')}")
                logger.info(f"Confidence: {result.get('confidence', 'N/A')}")
                logger.info(f"Primary Risks: {len(result.get('primary_risks', []))}")
                logger.info(f"Warnings: {result.get('warnings', [])}")
                
                # Print summary
                if result.get('primary_risks'):
                    logger.info("Top risks identified:")
                    for risk in result['primary_risks'][:3]:
                        logger.info(f"  - {risk.get('type', 'unknown')}: {risk.get('severity', 'unknown')} severity")
                
            except Exception as e:
                logger.error(f"❌ Test {i} failed: {str(e)}")
                logger.exception("Full error details:")
        
        # Test health check
        logger.info("\n🏥 Testing health check...")
        health = await pipeline.health_check()
        logger.info(f"Health status: {health}")
        
        logger.info("\n✅ RAG Pipeline tests completed!")
        
    except Exception as e:
        logger.error(f"❌ Test setup failed: {str(e)}")
        logger.exception("Full error details:")

if __name__ == "__main__":
    asyncio.run(test_rag_pipeline())
