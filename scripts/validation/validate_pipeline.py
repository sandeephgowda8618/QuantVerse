#!/usr/bin/env python3
"""
Simple validation test for the uRISK data pipeline components.
Tests basic functionality without requiring external APIs or database.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        # Core dependencies
        import fastapi
        import pandas as pd
        import numpy as np
        import chromadb
        import sentence_transformers
        print("  ✓ Core dependencies imported")
        
        # Data collection modules (without database connection)
        from backend.config.settings import TRACKED_ASSETS
        print("  ✓ Settings module imported")
        
        from backend.utils.logging_utils import setup_logger
        logger = setup_logger("test")
        print("  ✓ Logging utilities imported")
        
        # Embedding modules
        try:
            from backend.embeddings.embedder import FinancialEmbedder
            print("  ✓ Advanced embedding modules imported")
        except:
            from backend.embeddings.simple_embedder import Embedder
            print("  ✓ Simple embedding modules imported")
        
        # Vector store
        try:
            from backend.embeddings.vector_store import ChromaVectorStore
            print("  ✓ Advanced vector store modules imported")
        except:
            from backend.embeddings.simple_vector_store import VectorStore
            print("  ✓ Simple vector store modules imported")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_embedder():
    """Test the embedding functionality."""
    print("\nTesting embedder...")
    
    try:
        from backend.embeddings.embedder import FinancialEmbedder
        
        embedder = FinancialEmbedder()
        info = embedder.get_embedding_info()
        print(f"  ✓ Embedder initialized: {info['model_type']} ({info['embedding_dimension']}d)")
        
        # Test embedding generation
        test_text = "Apple stock price increased 5% due to strong earnings report"
        embedding = embedder.embed_text(test_text)
        
        if embedding is not None:
            print(f"  ✓ Generated embedding: shape {embedding.shape}")
            return True
        else:
            print("  ✗ Failed to generate embedding")
            return False
            
    except Exception as e:
        print(f"  ✗ Embedder test failed: {e}")
        return False

def test_vector_store():
    """Test the vector store functionality."""
    print("\nTesting vector store...")
    
    try:
        from backend.embeddings.vector_store import ChromaVectorStore
        
        # Reset collections to avoid conflicts
        store = ChromaVectorStore()
        try:
            store.reset_collections()
            print("  ✓ Collections reset successfully")
        except Exception as e:
            print(f"  ! Collection reset failed, continuing: {e}")
        
        stats = store.get_collection_stats()
        print(f"  ✓ Vector store initialized with {len(stats)} collections")
        
        for collection_name, stat in stats.items():
            count = stat.get('document_count', 0)
            print(f"    - {collection_name}: {count} documents")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Vector store test failed: {e}")
        return False

def test_preprocessing():
    """Test the preprocessing pipeline."""
    print("\nTesting preprocessing pipeline...")
    
    try:
        from backend.data_ingestion.preprocess_pipeline import PreprocessingPipeline
        
        pipeline = PreprocessingPipeline()
        
        # Test text cleaning
        dirty_text = "<p>Apple Inc. stock <strong>increased</strong> 5%!</p>"
        clean_text = pipeline.clean_text(dirty_text)
        print(f"  ✓ Text cleaning: '{dirty_text}' → '{clean_text}'")
        
        # Test chunking
        test_text = "This is a test article about Apple Inc. " * 20  # Make it long enough
        chunks = pipeline.chunk_text(test_text, {'ticker': 'AAPL', 'source': 'test'})
        print(f"  ✓ Text chunking: created {len(chunks)} chunks")
        
        if chunks:
            print(f"    - First chunk: {len(chunks[0]['text_chunk'].split())} words")
            print(f"    - Metadata preserved: {chunks[0].get('ticker', 'missing')}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Preprocessing test failed: {e}")
        return False

def test_integration():
    """Test basic integration between components."""
    print("\nTesting component integration...")
    
    try:
        from backend.data_ingestion.preprocess_pipeline import PreprocessingPipeline
        from backend.embeddings.embedder import FinancialEmbedder
        
        # Create test data
        pipeline = PreprocessingPipeline()
        embedder = FinancialEmbedder()
        
        test_text = "Apple Inc reported strong quarterly earnings with revenue growth of 15% year-over-year."
        
        # Chunk the text
        chunks = pipeline.chunk_text(test_text, {
            'ticker': 'AAPL',
            'source': 'test',
            'content_type': 'news'
        })
        
        print(f"  ✓ Created {len(chunks)} chunks")
        
        # Generate embeddings
        embedded_chunks = embedder.embed_chunks(chunks)
        
        successful_embeddings = sum(1 for chunk in embedded_chunks if chunk.get('embedding') is not None)
        print(f"  ✓ Generated embeddings for {successful_embeddings}/{len(embedded_chunks)} chunks")
        
        if successful_embeddings > 0:
            sample_chunk = next(chunk for chunk in embedded_chunks if chunk.get('embedding'))
            embedding_dim = len(sample_chunk['embedding'])
            print(f"    - Embedding dimension: {embedding_dim}")
        
        return successful_embeddings > 0
        
    except Exception as e:
        print(f"  ✗ Integration test failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("=" * 60)
    print("uRISK DATA PIPELINE - VALIDATION TEST")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Embedder Test", test_embedder),
        ("Vector Store Test", test_vector_store),
        ("Preprocessing Test", test_preprocessing),
        ("Integration Test", test_integration)
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
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All validation tests passed! The pipeline is ready for use.")
        return True
    else:
        print(f"\n⚠️  {total-passed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
