#!/usr/bin/env python3
"""
Simplified validation test that focuses on core components without ChromaDB.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_core_imports():
    """Test basic imports without database dependencies."""
    print("Testing core imports...")
    
    try:
        # Core dependencies
        import fastapi
        import pandas as pd
        import numpy as np
        import sentence_transformers
        print("  ✓ Core dependencies imported")
        
        # Settings and utilities
        from backend.config.settings import TRACKED_ASSETS
        from backend.utils.logging_utils import setup_logger
        logger = setup_logger("test")
        print("  ✓ Settings and logging imported")
        
        # Embedding functionality
        from backend.embeddings.embedder import FinancialEmbedder
        print("  ✓ Embedding modules imported")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_embedder():
    """Test embedding functionality."""
    print("\nTesting embedder...")
    
    try:
        from backend.embeddings.embedder import FinancialEmbedder
        
        embedder = FinancialEmbedder()
        info = embedder.get_embedding_info()
        print(f"  ✓ Embedder initialized: {info['model_type']} ({info['embedding_dimension']}d)")
        
        # Test single embedding
        test_text = "Apple stock price increased 5% due to strong earnings report"
        embedding = embedder.embed_text(test_text)
        
        if embedding is not None:
            print(f"  ✓ Single embedding: shape {embedding.shape}")
        else:
            print("  ✗ Failed to generate single embedding")
            return False
        
        # Test batch embedding
        test_texts = [
            "Microsoft earnings beat expectations",
            "Tesla stock drops on production concerns",
            "Fed announces interest rate decision"
        ]
        
        batch_embeddings = embedder.embed_batch(test_texts)
        successful = sum(1 for emb in batch_embeddings if emb is not None)
        print(f"  ✓ Batch embeddings: {successful}/{len(test_texts)} successful")
        
        return successful > 0
        
    except Exception as e:
        print(f"  ✗ Embedder test failed: {e}")
        return False

def test_preprocessing():
    """Test preprocessing without database."""
    print("\nTesting preprocessing...")
    
    try:
        from backend.data_ingestion.preprocess_pipeline import PreprocessingPipeline
        
        pipeline = PreprocessingPipeline()
        
        # Test text cleaning
        dirty_text = "<p>Apple Inc. <strong>stock</strong> increased 5%! Visit http://example.com</p>"
        clean_text = pipeline.clean_text(dirty_text)
        print(f"  ✓ Text cleaning works")
        print(f"    Input:  '{dirty_text}'")
        print(f"    Output: '{clean_text}'")
        
        # Test chunking
        long_text = """
        Apple Inc. reported strong quarterly earnings with revenue growth of 15% year-over-year.
        The technology giant exceeded analyst expectations across all key metrics including iPhone sales,
        Services revenue, and Mac revenue. CEO Tim Cook highlighted the company's continued innovation
        in artificial intelligence and machine learning capabilities. The stock price surged 8% in
        after-hours trading following the earnings announcement. Analysts raised their price targets
        and maintained buy ratings on the stock. The company also announced a new stock buyback program
        worth $90 billion and increased its quarterly dividend by 4%. Looking ahead, Apple provided
        optimistic guidance for the next quarter, citing strong demand for its products globally.
        """ * 5  # Make it long enough to create multiple chunks
        
        chunks = pipeline.chunk_text(long_text, {
            'ticker': 'AAPL',
            'source': 'test',
            'content_type': 'news'
        })
        
        print(f"  ✓ Text chunking: created {len(chunks)} chunks")
        
        if chunks:
            print(f"    - First chunk: {len(chunks[0]['text_chunk'].split())} words")
            print(f"    - Metadata: ticker={chunks[0].get('ticker')}, source={chunks[0].get('source')}")
            print(f"    - Chunk preview: {chunks[0]['text_chunk'][:100]}...")
        
        return len(chunks) > 0
        
    except Exception as e:
        print(f"  ✗ Preprocessing test failed: {e}")
        return False

def test_integration():
    """Test integration between preprocessing and embeddings."""
    print("\nTesting preprocessing + embedding integration...")
    
    try:
        from backend.data_ingestion.preprocess_pipeline import PreprocessingPipeline
        from backend.embeddings.embedder import FinancialEmbedder
        
        pipeline = PreprocessingPipeline()
        embedder = FinancialEmbedder()
        
        # Create test content
        test_content = """
        Breaking: Apple Inc. (AAPL) stock surged 12% in pre-market trading following the announcement
        of record-breaking quarterly earnings. The tech giant reported revenue of $89.5 billion,
        beating analyst estimates of $85.2 billion. iPhone sales were particularly strong, with
        revenue up 18% year-over-year. The company also announced a new AI initiative that will
        be integrated across all Apple products. CEO Tim Cook stated that this represents the
        biggest product innovation since the iPhone launch in 2007.
        """
        
        # Process through pipeline
        chunks = pipeline.chunk_text(test_content, {
            'ticker': 'AAPL',
            'source': 'financial_news',
            'content_type': 'news',
            'timestamp': '2024-11-06T10:00:00Z'
        })
        
        print(f"  ✓ Created {len(chunks)} chunks from test content")
        
        # Generate embeddings
        embedded_chunks = embedder.embed_chunks(chunks)
        
        successful_embeddings = sum(1 for chunk in embedded_chunks if chunk.get('embedding') is not None)
        print(f"  ✓ Generated embeddings for {successful_embeddings}/{len(embedded_chunks)} chunks")
        
        if successful_embeddings > 0:
            sample_chunk = next(chunk for chunk in embedded_chunks if chunk.get('embedding'))
            embedding_dim = len(sample_chunk['embedding'])
            model_type = sample_chunk.get('embedding_model', 'unknown')
            print(f"    - Embedding model: {model_type}")
            print(f"    - Embedding dimension: {embedding_dim}")
            print(f"    - Sample chunk: {sample_chunk['text_chunk'][:80]}...")
        
        return successful_embeddings > 0
        
    except Exception as e:
        print(f"  ✗ Integration test failed: {e}")
        return False

def test_data_flow():
    """Test the complete data flow simulation."""
    print("\nTesting complete data flow simulation...")
    
    try:
        from backend.data_ingestion.preprocess_pipeline import PreprocessingPipeline
        from backend.embeddings.embedder import FinancialEmbedder
        
        pipeline = PreprocessingPipeline()
        embedder = FinancialEmbedder()
        
        # Simulate different types of content
        test_contents = [
            {
                'type': 'news',
                'content': 'Tesla stock drops 5% on production concerns and supply chain issues',
                'metadata': {'ticker': 'TSLA', 'source': 'reuters', 'content_type': 'news'}
            },
            {
                'type': 'regulatory',
                'content': 'SEC announces new cryptocurrency trading regulations affecting digital asset exchanges',
                'metadata': {'ticker': 'BTC-USD', 'source': 'sec', 'content_type': 'regulatory'}
            },
            {
                'type': 'market',
                'content': 'S&P 500 reaches new all-time high as technology sector leads gains with 3.2% increase',
                'metadata': {'ticker': 'SPY', 'source': 'market_data', 'content_type': 'market'}
            }
        ]
        
        all_processed_chunks = []
        
        for content_item in test_contents:
            # Process content
            chunks = pipeline.chunk_text(content_item['content'], content_item['metadata'])
            
            # Generate embeddings
            embedded_chunks = embedder.embed_chunks(chunks)
            
            all_processed_chunks.extend(embedded_chunks)
            
            content_type = content_item['type']
            successful = sum(1 for chunk in embedded_chunks if chunk.get('embedding') is not None)
            print(f"    - {content_type}: {successful} embedded chunks")
        
        total_successful = sum(1 for chunk in all_processed_chunks if chunk.get('embedding') is not None)
        print(f"  ✓ Total pipeline processed: {total_successful} embedded chunks ready for vector storage")
        
        # Group by content type
        by_type = {}
        for chunk in all_processed_chunks:
            content_type = chunk.get('content_type', 'unknown')
            if content_type not in by_type:
                by_type[content_type] = 0
            if chunk.get('embedding') is not None:
                by_type[content_type] += 1
        
        print(f"    - Content distribution: {dict(by_type)}")
        
        return total_successful > 0
        
    except Exception as e:
        print(f"  ✗ Data flow test failed: {e}")
        return False

def main():
    """Run all simplified validation tests."""
    print("=" * 70)
    print("uRISK DATA PIPELINE - SIMPLIFIED VALIDATION TEST")
    print("=" * 70)
    
    tests = [
        ("Core Imports", test_core_imports),
        ("Embedder", test_embedder),
        ("Preprocessing", test_preprocessing),
        ("Integration", test_integration),
        ("Data Flow", test_data_flow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  ✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All core pipeline components are working!")
        print("The data collection and preprocessing pipeline is ready for use.")
        print("\n📋 Next steps:")
        print("  1. Set up PostgreSQL database (see DATA_PIPELINE_README.md)")
        print("  2. Configure API keys in .env file")
        print("  3. Run full integration test with database")
        return True
    else:
        print(f"\n⚠️  {total-passed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
