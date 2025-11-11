#!/usr/bin/env python3
"""
Real-time LLM Query Test for QuantVerse uRISK
Tests the full pipeline: Vector search + LLM inference + Risk assessment
"""

import asyncio
import os
import sys
import time
import logging
from pathlib import Path

# Add project path
sys.path.append(str(Path(__file__).parent))

from backend.rag_engine.risk_mode.risk_pipeline import RiskAssessmentPipeline
from backend.rag_engine.vector_store import ChromaVectorStore
from backend.rag_engine.risk_mode.risk_cache import RiskCacheManager
from backend.db.postgres_handler import PostgresHandler
from backend.rag_engine.llm_manager import LLMManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_realtime_query():
    """Test real-time LLM queries with detailed timing breakdown"""
    
    logger.info("🚀 Starting Real-Time LLM Query Test...")
    
    try:
        # Initialize components with timing
        start_time = time.time()
        
        logger.info("Initializing PostgreSQL...")
        db_handler = PostgresHandler()
        db_handler.initialize_sync_pool()
        
        logger.info("Initializing ChromaDB Vector Store...")
        vector_store = ChromaVectorStore()
        vector_store.initialize("./vector_db")
        
        logger.info("Initializing Cache Manager...")
        cache_manager = RiskCacheManager()
        
        logger.info("Initializing Risk Assessment Pipeline...")
        pipeline = RiskAssessmentPipeline(
            vector_store=vector_store,
            db_manager=db_handler,
            cache_manager=cache_manager,
            llm_model="llama3.1"
        )
        
        init_time = time.time() - start_time
        logger.info(f"✅ All components initialized in {init_time:.2f}s")
        
        # Check vector store status first
        logger.info("\n📊 Vector Store Status Check...")
        stats = vector_store.get_collection_stats()
        logger.info(f"Vector Store Documents: {stats.get('count', 0)}")
        
        if stats.get('count', 0) == 0:
            logger.warning("⚠️  Vector store appears empty - queries may not return results")
        
        # Real-time queries with timing breakdown
        queries = [
            {
                "query": "What are the immediate risks for AAPL stock right now?",
                "params": {"ticker": "AAPL", "time_window_hours": 12},
                "expected_risks": ["sentiment", "liquidity", "regulatory"]
            },
            {
                "query": "Should I be worried about NVDA's infrastructure stability?", 
                "params": {"ticker": "NVDA", "time_window_hours": 24},
                "expected_risks": ["infrastructure", "technical"]
            },
            {
                "query": "Are there regulatory compliance issues for MSFT?",
                "params": {"ticker": "MSFT", "time_window_hours": 48}, 
                "expected_risks": ["regulatory", "compliance"]
            }
        ]
        
        logger.info(f"\n🔥 Running {len(queries)} Real-Time Risk Queries...\n")
        
        total_queries_start = time.time()
        
        for i, test in enumerate(queries, 1):
            logger.info(f"{'='*60}")
            logger.info(f"🎯 Query {i}: {test['query']}")
            logger.info(f"📋 Parameters: {test['params']}")
            logger.info(f"📋 Expected Risk Types: {test['expected_risks']}")
            
            query_start = time.time()
            
            try:
                # Run the risk assessment with detailed timing
                result = await pipeline.assess_risk(test["query"], test["params"])
                
                query_end = time.time()
                total_time = query_end - query_start
                
                # Results analysis
                logger.info(f"\n📈 Results Summary:")
                logger.info(f"⏱️  Total Response Time: {total_time:.2f}s")
                logger.info(f"⚠️  Risk Score: {result.get('risk_score', 'N/A')}/10")
                logger.info(f"🎯 Confidence Level: {result.get('confidence', 'N/A')}")
                logger.info(f"🔍 Evidence Chunks Used: {result.get('evidence_count', 'N/A')}")
                logger.info(f"⚡ Processing Time (LLM): {result.get('processing_time_ms', 'N/A')}ms")
                
                # Primary risks
                primary_risks = result.get('primary_risks', [])
                if primary_risks:
                    logger.info(f"🚨 Primary Risks Identified ({len(primary_risks)}):")
                    for j, risk in enumerate(primary_risks[:5], 1):
                        risk_type = risk.get('type', 'unknown')
                        severity = risk.get('severity', 'unknown')
                        confidence = risk.get('confidence', 'N/A')
                        logger.info(f"   {j}. {risk_type.upper()} - {severity} severity (confidence: {confidence})")
                else:
                    logger.info("🚨 No specific risks identified")
                
                # Secondary risks  
                secondary_risks = result.get('secondary_risks', [])
                if secondary_risks:
                    logger.info(f"⚠️  Secondary Risks ({len(secondary_risks)}):")
                    for risk in secondary_risks[:3]:
                        logger.info(f"   - {risk.get('type', 'unknown')}: {risk.get('severity', 'unknown')}")
                
                # Warnings
                warnings = result.get('warnings', [])
                if warnings:
                    logger.info(f"⚠️  Warnings: {', '.join(warnings)}")
                
                # Performance evaluation
                if total_time < 5:
                    logger.info(f"✅ EXCELLENT: Sub-5s response time!")
                elif total_time < 15:
                    logger.info(f"✅ GOOD: Reasonable response time")
                else:
                    logger.info(f"⚠️  SLOW: Response time could be improved")
                
                logger.info(f"\n")
                
            except Exception as e:
                logger.error(f"❌ Query {i} failed: {str(e)}")
                logger.exception("Full error details:")
        
        total_queries_end = time.time()
        avg_time = (total_queries_end - total_queries_start) / len(queries)
        
        logger.info(f"{'='*60}")
        logger.info(f"📊 Performance Summary:")
        logger.info(f"Total Queries: {len(queries)}")
        logger.info(f"Total Time: {total_queries_end - total_queries_start:.2f}s")
        logger.info(f"Average Response Time: {avg_time:.2f}s")
        
        # Final health check
        logger.info(f"\n🏥 Final System Health Check...")
        health = await pipeline.health_check()
        overall_health = health.get('overall', 'unknown')
        logger.info(f"Overall Health: {overall_health.upper()}")
        
        if overall_health == 'healthy':
            logger.info("✅ All systems operational!")
        else:
            logger.warning(f"⚠️  System health: {overall_health}")
            unhealthy = health.get('unhealthy_components', [])
            if unhealthy:
                logger.warning(f"Unhealthy components: {', '.join(unhealthy)}")
        
        logger.info(f"\n🎉 Real-Time LLM Query Test Completed Successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        logger.exception("Full error details:")

if __name__ == "__main__":
    asyncio.run(test_realtime_query())
