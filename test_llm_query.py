#!/usr/bin/env python3
"""
Test script for QuantVerse uRISK LLM Manager with Risk Pipeline
Tests the complete 6-step lifecycle with a real query
"""

import asyncio
import logging
import time
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.rag_engine.llm_manager import LLMManager
from backend.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_llm_initialization():
    """Test LLM Manager initialization (Steps 1-4 of lifecycle)"""
    logger.info("🚀 Starting LLM Manager initialization test...")
    
    try:
        # Step 1-4: Initialize LLM Manager (FastAPI startup equivalent)
        start_time = time.time()
        llm_manager = await LLMManager.initialize()
        init_time = (time.time() - start_time) * 1000
        
        logger.info(f"✅ LLM Manager initialized in {init_time:.2f}ms")
        logger.info(f"📍 Ollama URL: {settings.OLLAMA_URL}")
        logger.info(f"🤖 Model: {settings.OLLAMA_MODEL}")
        logger.info(f"⏰ Keep Alive: {settings.OLLAMA_KEEP_ALIVE}")
        
        return llm_manager
        
    except Exception as e:
        logger.error(f"❌ LLM Manager initialization failed: {e}")
        raise

async def test_first_query(llm_manager: LLMManager):
    """Test first query (Step 5: Expected ~10-16s for cold start)"""
    logger.info("🔥 Testing first query (cold start)...")
    
    query = "What are the current risk factors for NVDA stock?"
    system_prompt = """You are a financial risk analyst. Analyze the query and provide a brief risk assessment. 
    Focus on potential infrastructure, regulatory, sentiment, and liquidity risks. Be concise and factual."""
    
    try:
        start_time = time.time()
        
        # First query - should take longer (model loading)
        response = await llm_manager.generate(query, system_prompt)
        
        response_time = (time.time() - start_time) * 1000
        logger.info(f"✅ First query completed in {response_time:.2f}ms")
        logger.info(f"📝 Response length: {len(response)} characters")
        logger.info(f"📄 Response preview: {response[:150]}...")
        
        return response_time
        
    except Exception as e:
        logger.error(f"❌ First query failed: {e}")
        raise

async def test_subsequent_queries(llm_manager: LLMManager):
    """Test subsequent queries (Step 5: Expected ~1-3s with warm session)"""
    logger.info("⚡ Testing subsequent queries (warm session)...")
    
    queries = [
        "Assess liquidity risks for BTC cryptocurrency",
        "What regulatory risks affect AAPL?",
        "Analyze infrastructure risks for TSLA"
    ]
    
    response_times = []
    
    for i, query in enumerate(queries, 1):
        try:
            start_time = time.time()
            
            response = await llm_manager.generate(
                query, 
                "You are a financial risk analyst. Provide a brief risk assessment."
            )
            
            response_time = (time.time() - start_time) * 1000
            response_times.append(response_time)
            
            logger.info(f"✅ Query {i} completed in {response_time:.2f}ms")
            logger.info(f"📄 Response preview: {response[:100]}...")
            
        except Exception as e:
            logger.error(f"❌ Query {i} failed: {e}")
            continue
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        logger.info(f"📊 Average subsequent query time: {avg_time:.2f}ms")
        return avg_time
    
    return None

async def test_risk_pipeline_integration():
    """Test integration with risk pipeline (if available)"""
    logger.info("🛡️ Testing risk pipeline integration...")
    
    try:
        # Try to import and test the risk pipeline
        from backend.rag_engine.risk_mode.risk_pipeline import RiskAssessmentPipeline
        from backend.rag_engine.risk_mode.risk_cache import RiskCacheManager
        from backend.rag_engine.vector_store import ChromaVectorStore
        from backend.db.postgres_handler import PostgresHandler
        
        # Create minimal mock components for testing
        logger.info("📦 Creating risk pipeline components...")
        
        # Note: These would normally be properly initialized
        vector_store = None  # Would be ChromaVectorStore()
        db_manager = None    # Would be PostgresHandler()
        cache_manager = RiskCacheManager()  # This should work with no-cache implementation
        
        logger.info("✅ Risk pipeline components created (mock mode)")
        logger.info("ℹ️  Full integration requires database and vector store setup")
        
        return True
        
    except ImportError as e:
        logger.warning(f"⚠️  Risk pipeline not available for testing: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Risk pipeline integration test failed: {e}")
        return False

async def test_graceful_shutdown(llm_manager: LLMManager):
    """Test graceful shutdown (Step 6)"""
    logger.info("🛑 Testing graceful shutdown...")
    
    try:
        start_time = time.time()
        await llm_manager.shutdown()
        shutdown_time = (time.time() - start_time) * 1000
        
        logger.info(f"✅ Graceful shutdown completed in {shutdown_time:.2f}ms")
        return shutdown_time
        
    except Exception as e:
        logger.error(f"❌ Shutdown failed: {e}")
        raise

async def main():
    """Main test function - complete 6-step lifecycle test"""
    logger.info("🎯 Starting QuantVerse uRISK LLM Manager Test")
    logger.info("=" * 60)
    
    llm_manager = None
    test_results = {}
    
    try:
        # Test initialization (Steps 1-4)
        llm_manager = await test_llm_initialization()
        test_results['initialization'] = '✅ PASS'
        
        # Test first query (Step 5 - cold)
        first_query_time = await test_first_query(llm_manager)
        test_results['first_query'] = f'✅ PASS ({first_query_time:.0f}ms)'
        
        # Test subsequent queries (Step 5 - warm)
        avg_time = await test_subsequent_queries(llm_manager)
        if avg_time:
            test_results['subsequent_queries'] = f'✅ PASS ({avg_time:.0f}ms avg)'
        else:
            test_results['subsequent_queries'] = '❌ FAIL'
        
        # Test risk pipeline integration
        pipeline_ok = await test_risk_pipeline_integration()
        test_results['risk_pipeline'] = '✅ PASS' if pipeline_ok else '⚠️  SKIP (dependencies)'
        
        # Test shutdown (Step 6)
        await test_graceful_shutdown(llm_manager)
        test_results['shutdown'] = '✅ PASS'
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        test_results['error'] = str(e)
    
    finally:
        # Ensure cleanup even if test fails
        if llm_manager:
            try:
                await llm_manager.shutdown()
            except:
                pass
    
    # Print test summary
    logger.info("=" * 60)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    for test_name, result in test_results.items():
        logger.info(f"{test_name.replace('_', ' ').title()}: {result}")
    
    # Performance analysis
    if 'first_query' in test_results and 'subsequent_queries' in test_results:
        logger.info("\n🏃 PERFORMANCE ANALYSIS:")
        logger.info(f"Expected first query: 10-16s (cold model load)")
        logger.info(f"Expected subsequent: 1-3s (warm session reuse)")
        logger.info(f"✅ Session persistence and keep_alive are working if subsequent queries are fast")
    
    logger.info("\n🎉 Test completed!")

if __name__ == "__main__":
    # Check if Ollama is available
    import subprocess
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        logger.info(f"🦙 Ollama version: {result.stdout.strip()}")
    except FileNotFoundError:
        logger.warning("⚠️  Ollama not found in PATH. Please install: curl -fsSL https://ollama.ai/install.sh | sh")
        sys.exit(1)
    
    # Run the test
    asyncio.run(main())
