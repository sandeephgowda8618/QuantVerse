#!/usr/bin/env python3
"""
Quick performance test to verify keep_alive optimization
"""

import asyncio
import logging
import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.rag_engine.llm_manager import LLMManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_rapid_queries():
    """Test rapid-fire queries to verify session persistence"""
    logger.info("🚀 Testing rapid-fire queries for session persistence...")
    
    # Initialize LLM manager
    llm_manager = await LLMManager.initialize()
    
    queries = [
        "Risk assessment for NVDA?",
        "Risk assessment for AAPL?", 
        "Risk assessment for TSLA?",
        "Risk assessment for BTC?",
        "Risk assessment for ETH?"
    ]
    
    response_times = []
    
    try:
        for i, query in enumerate(queries, 1):
            start_time = time.time()
            
            response = await llm_manager.generate(
                query, 
                "Respond with a brief 2-sentence risk assessment."
            )
            
            response_time = (time.time() - start_time) * 1000
            response_times.append(response_time)
            
            logger.info(f"Query {i}: {response_time:.0f}ms - {response[:50]}...")
            
            # Small delay to see if keep_alive helps
            await asyncio.sleep(1)
    
    finally:
        await llm_manager.shutdown()
    
    # Analysis
    if len(response_times) > 1:
        first_time = response_times[0]
        subsequent_avg = sum(response_times[1:]) / len(response_times[1:])
        
        logger.info(f"\n📊 PERFORMANCE SUMMARY:")
        logger.info(f"First query: {first_time:.0f}ms")
        logger.info(f"Subsequent average: {subsequent_avg:.0f}ms")
        logger.info(f"Improvement: {((first_time - subsequent_avg) / first_time * 100):.1f}%")
        
        if subsequent_avg < 3000:  # Less than 3 seconds
            logger.info("✅ Keep-alive optimization is working!")
        else:
            logger.info("⚠️  Keep-alive may need tuning - responses still slow")

if __name__ == "__main__":
    asyncio.run(test_rapid_queries())
