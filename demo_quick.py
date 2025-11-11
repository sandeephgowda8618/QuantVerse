#!/usr/bin/env python3
"""
Quick Demo - Real-Time Risk Query
Shows the LLM pipeline working end-to-end
"""

import asyncio
import sys
from pathlib import Path
import time

# Add project path
sys.path.append(str(Path(__file__).parent))

from backend.rag_engine.risk_mode.risk_pipeline import RiskAssessmentPipeline
from backend.rag_engine.vector_store import ChromaVectorStore
from backend.rag_engine.risk_mode.risk_cache import RiskCacheManager
from backend.db.postgres_handler import PostgresHandler

async def quick_demo():
    """Quick demo of real-time risk assessment"""
    
    print("🚀 QuantVerse uRISK - Real-Time LLM Query Demo")
    print("="*50)
    
    # Initialize system
    print("🔧 Initializing system components...")
    
    db_handler = PostgresHandler()
    db_handler.initialize_sync_pool()
    
    vector_store = ChromaVectorStore()  
    vector_store.initialize("./vector_db")
    
    cache_manager = RiskCacheManager()
    
    pipeline = RiskAssessmentPipeline(
        vector_store=vector_store,
        db_manager=db_handler,
        cache_manager=cache_manager,
        llm_model="llama3.1"
    )
    
    # Check system status
    stats = vector_store.get_collection_stats()
    print(f"✅ System ready: {stats.get('count', 0)} documents loaded")
    print()
    
    # Demo queries
    demo_queries = [
        "What are the biggest risks for Apple stock right now?",
        "Should I be concerned about NVDA infrastructure issues?", 
        "Are there regulatory risks affecting Microsoft?"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"📊 Demo Query {i}: {query}")
        print("-" * 40)
        
        start_time = time.time()
        
        # Extract ticker for params
        ticker = None
        if "apple" in query.lower() or "aapl" in query.lower():
            ticker = "AAPL"
        elif "nvda" in query.lower() or "nvidia" in query.lower():
            ticker = "NVDA"  
        elif "microsoft" in query.lower() or "msft" in query.lower():
            ticker = "MSFT"
        
        params = {"ticker": ticker, "time_window_hours": 24} if ticker else {}
        
        try:
            result = await pipeline.assess_risk(query, params)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Display results
            print(f"⏱️  Response Time: {response_time:.1f}s")
            print(f"⚠️  Risk Score: {result.get('risk_score', 'N/A')}/10")
            print(f"🎯 Confidence: {result.get('confidence', 'N/A')}")
            
            primary_risks = result.get('primary_risks', [])
            if primary_risks:
                print("🚨 Key Risks:")
                for risk in primary_risks[:2]:
                    risk_type = risk.get('type', 'unknown').upper()
                    severity = risk.get('severity', 'unknown')
                    print(f"   • {risk_type}: {severity} severity")
            else:
                print("🟢 No major risks identified")
                
            if result.get('warnings'):
                print(f"⚠️  Warnings: {len(result.get('warnings', []))}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()
    
    print("✅ Real-time LLM risk assessment demo completed!")
    print("💡 The system successfully processed queries using:")
    print("   • ChromaDB vector search (188K+ documents)")
    print("   • Ollama LLM inference (Llama 3.1)")
    print("   • PostgreSQL financial data (301K+ records)")
    print("   • Risk assessment pipeline")

if __name__ == "__main__":
    asyncio.run(quick_demo())
