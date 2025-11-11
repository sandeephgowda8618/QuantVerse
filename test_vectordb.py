#!/usr/bin/env python3
"""
Quick vector database test script to verify RAG retrieval functionality
"""

import sys
import asyncio
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.rag_engine.vector_store import vector_store
from backend.embeddings.sentence_embedder import SentenceEmbedder

async def test_vector_db():
    """Test vector database query functionality."""
    print("🧪 Testing Vector Database Query Functionality")
    print("=" * 60)
    
    try:
        # Initialize components
        print("📊 Initializing components...")
        vector_store.initialize()
        
        embedder = SentenceEmbedder()
        await embedder.initialize()
        
        # Test 1: Basic collection stats
        print("\n📈 Vector Store Statistics:")
        stats = vector_store.get_collection_stats()
        print(f"   📁 Total Documents: {stats.get('count', 0)}")
        print(f"   📚 Collection Name: {stats.get('name', 'N/A')}")
        
        # Test 2: Sample query with metadata filtering
        print("\n🔍 Testing Semantic Search:")
        
        # Query for NVDA RSI data
        test_queries = [
            {
                "query": "NVIDIA RSI technical indicator overbought oversold",
                "filter": {"ticker": "NVDA"},
                "description": "NVDA RSI Technical Analysis"
            },
            {
                "query": "Apple earnings financial results revenue",
                "filter": {"ticker": "AAPL"},
                "description": "AAPL Earnings Data"
            },
            {
                "query": "Bitcoin cryptocurrency price movement",
                "filter": {"ticker": "BTC"},
                "description": "BTC Price Analysis"
            }
        ]
        
        for i, test in enumerate(test_queries, 1):
            print(f"\n   Test {i}: {test['description']}")
            print(f"   Query: '{test['query']}'")
            print(f"   Filter: {test['filter']}")
            
            # Perform query
            results = vector_store.query_documents(
                query_texts=[test['query']],
                n_results=3,
                where=test['filter']
            )
            
            if results and results.get('documents') and results['documents'][0]:
                print(f"   ✅ Found {len(results['documents'][0])} results:")
                for j, (doc, meta, distance) in enumerate(zip(
                    results['documents'][0][:3], 
                    results['metadatas'][0][:3],
                    results['distances'][0][:3]
                ), 1):
                    print(f"      {j}. {meta.get('endpoint', 'N/A')} | {meta.get('timestamp', 'N/A')[:10]}")
                    print(f"         Distance: {distance:.3f}")
                    print(f"         Snippet: {doc[:80]}...")
            else:
                print("   ❌ No results found")
        
        # Test 3: Different asset types
        print(f"\n🎯 Testing Asset Coverage:")
        asset_tests = [
            {"ticker": "NVDA", "name": "NVIDIA (Tech Stock)"},
            {"ticker": "BTC", "name": "Bitcoin (Crypto)"},
            {"ticker": "SPY", "name": "S&P 500 (Index)"}
        ]
        
        for asset in asset_tests:
            results = vector_store.query_documents(
                query_texts=["technical analysis price movement"],
                n_results=1,
                where={"ticker": asset["ticker"]}
            )
            count = len(results.get('documents', [[]])[0])
            print(f"   {asset['name']}: {count} relevant chunks found {'✅' if count > 0 else '❌'}")
        
        # Test 4: Risk type filtering
        print(f"\n🔬 Testing Risk Type Filtering:")
        risk_types = ["technical", "fundamental", "sentiment", "macro"]
        
        for risk_type in risk_types:
            results = vector_store.query_documents(
                query_texts=["financial analysis market data"],
                n_results=1,
                where={"risk_type": risk_type}
            )
            count = len(results.get('documents', [[]])[0])
            print(f"   {risk_type.capitalize()}: {count} chunks found {'✅' if count > 0 else '❌'}")
        
        # Test 5: Date range verification
        print(f"\n📅 Testing Date Range Coverage:")
        try:
            # Query for data from different years
            all_results = vector_store.query_documents(
                query_texts=["market data analysis"],
                n_results=100,
                where={}
            )
            
            if all_results and all_results.get('metadatas') and all_results['metadatas'][0]:
                dates = [meta.get('timestamp', '')[:4] for meta in all_results['metadatas'][0] if meta.get('timestamp')]
                unique_years = sorted(set(filter(None, dates)))
                print(f"   Date Coverage: {min(unique_years) if unique_years else 'N/A'} - {max(unique_years) if unique_years else 'N/A'}")
                print(f"   Years Available: {len(unique_years)} years")
                print(f"   Sample Years: {', '.join(unique_years[:10])}{' ...' if len(unique_years) > 10 else ''}")
            else:
                print("   ❌ No date information found")
        except Exception as e:
            print(f"   ❌ Date range test failed: {e}")
        
        print(f"\n🎉 Vector Database Testing Complete!")
        print(f"✅ Database is operational and ready for RAG queries")
        
    except Exception as e:
        print(f"❌ Vector database test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_vector_db())
    exit(0 if success else 1)
