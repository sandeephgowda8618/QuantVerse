#!/usr/bin/env python3
"""
Database Setup and Initial Sync Test
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_database_connection():
    """Test database connection and create sync table if needed."""
    try:
        from backend.db.postgres_handler import PostgresHandler
        
        # Initialize database handler
        db = PostgresHandler()
        
        # Test sync connection first
        logger.info("Testing synchronous database connection...")
        db.initialize_sync_pool(min_conn=1, max_conn=2)
        
        # Test a simple query
        result = db.execute_query("SELECT 1 as test")
        if result and result[0]['test'] == 1:
            logger.info("✅ Synchronous database connection successful!")
        else:
            logger.error("❌ Synchronous database test failed")
            return False
        
        # Test async connection
        logger.info("Testing asynchronous database connection...")
        await db.initialize_async_pool(min_size=1, max_size=2)
        
        async_result = await db.async_execute_query("SELECT 1 as test")
        if async_result and async_result[0]['test'] == 1:
            logger.info("✅ Asynchronous database connection successful!")
        else:
            logger.error("❌ Asynchronous database test failed")
            return False
        
        # Create sync state table with timezone-aware columns
        logger.info("Creating vector_sync_state table...")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS vector_sync_state (
            table_name VARCHAR(100) PRIMARY KEY,
            last_synced_at TIMESTAMPTZ,
            records_synced BIGINT DEFAULT 0,
            last_chunk_id VARCHAR(255),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        await db.async_execute_insert(create_table_sql)
        logger.info("✅ vector_sync_state table ready")
        
        # Fix timezone issues in existing tables
        logger.info("Fixing timezone issues in database...")
        try:
            timezone_fixes = [
                "ALTER TABLE alpha_vantage_data ALTER COLUMN timestamp TYPE TIMESTAMPTZ USING timestamp AT TIME ZONE 'UTC'",
                "ALTER TABLE vector_sync_state ALTER COLUMN last_synced_at TYPE TIMESTAMPTZ USING last_synced_at AT TIME ZONE 'UTC'",
                "ALTER TABLE vector_sync_state ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC'",
                "ALTER TABLE vector_sync_state ALTER COLUMN updated_at TYPE TIMESTAMPTZ USING updated_at AT TIME ZONE 'UTC'"
            ]
            
            for fix_sql in timezone_fixes:
                try:
                    await db.async_execute_insert(fix_sql)
                except Exception as e:
                    # Ignore if column already exists or other non-critical errors
                    logger.warning(f"Timezone fix skipped (may already be applied): {e}")
            
            logger.info("✅ Timezone fixes applied")
        except Exception as e:
            logger.warning(f"Some timezone fixes failed (may already be applied): {e}")
        
        # Initialize with default values (timezone-aware)
        init_sql = """
        INSERT INTO vector_sync_state (table_name, last_synced_at, records_synced) 
        VALUES 
            ('alpha_vantage_data', '2020-01-01 00:00:00+00'::TIMESTAMPTZ, 0)
        ON CONFLICT (table_name) DO NOTHING;
        """
        
        await db.async_execute_insert(init_sql)
        logger.info("✅ Initial sync state configured")
        
        # Check for existing data
        count_sql = "SELECT COUNT(*) as count FROM alpha_vantage_data"
        count_result = await db.async_execute_query(count_sql)
        record_count = count_result[0]['count'] if count_result else 0
        logger.info(f"📊 Found {record_count} records in alpha_vantage_data table")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False

async def test_vector_store():
    """Test ChromaDB setup."""
    try:
        from backend.rag_engine.vector_store import vector_store
        
        logger.info("Testing ChromaDB connection...")
        vector_store.initialize()
        
        stats = vector_store.get_collection_stats()
        logger.info(f"✅ ChromaDB ready - Collection: {stats.get('name')}, Documents: {stats.get('count', 0)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ChromaDB setup failed: {e}")
        return False

async def test_embedder():
    """Test sentence embedder."""
    try:
        from backend.embeddings.sentence_embedder import SentenceEmbedder
        
        logger.info("Testing sentence embedder...")
        embedder = SentenceEmbedder()
        await embedder.initialize()
        
        # Test embedding
        test_text = "NVDA RSI is 75, indicating overbought conditions"
        embedding = await embedder.embed_text(test_text)
        
        if embedding and len(embedding) > 0:
            logger.info(f"✅ Embedder ready - Dimension: {len(embedding)}, Model: {embedder.model_name}")
        else:
            logger.error("❌ Embedder test failed")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Embedder setup failed: {e}")
        return False

async def run_initial_sync():
    """Run the initial sync pipeline."""
    try:
        from backend.services.postgres_to_vectordb import postgres_to_vectordb_pipeline
        
        logger.info("🚀 Starting PostgreSQL → ChromaDB Sync Pipeline")
        logger.info("=" * 60)
        
        # Initialize pipeline
        logger.info("📊 Initializing pipeline components...")
        await postgres_to_vectordb_pipeline.initialize()
        
        # Run sync with smaller batch for initial test
        logger.info("🔄 Running incremental sync (limited batch)...")
        sync_stats = await postgres_to_vectordb_pipeline.sync_alpha_vantage_data(limit_per_batch=100)
        
        # Display results
        logger.info("📈 Sync Results:")
        logger.info("-" * 40)
        logger.info(f"✅ Records Processed: {sync_stats.get('processed', 0)}")
        logger.info(f"✅ Chunks Created: {sync_stats.get('chunks_created', 0)}")
        logger.info(f"❌ Errors: {sync_stats.get('errors', 0)}")
        
        # Check vector store after sync
        from backend.rag_engine.vector_store import vector_store
        final_stats = vector_store.get_collection_stats()
        logger.info(f"🗃️  ChromaDB Final Status: {final_stats.get('count', 0)} documents")
        
        if sync_stats.get('chunks_created', 0) > 0:
            logger.info("🎉 Initial sync completed successfully!")
        else:
            logger.warning("⚠️  No new chunks were created - this may be expected if data is already synced")
        
        return True
        
    except Exception as e:
        logger.error(f"💥 Initial sync failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main setup and test function."""
    logger.info("🔧 Setting up PostgreSQL → ChromaDB RAG Pipeline")
    logger.info("=" * 60)
    
    # Test database connection
    if not await test_database_connection():
        logger.error("❌ Database setup failed - please check your PostgreSQL configuration")
        return
    
    # Test vector store
    if not await test_vector_store():
        logger.error("❌ Vector store setup failed")
        return
    
    # Test embedder
    if not await test_embedder():
        logger.error("❌ Embedder setup failed")
        return
    
    logger.info("✅ All components ready!")
    logger.info("=" * 60)
    
    # Run initial sync
    success = await run_initial_sync()
    
    if success:
        logger.info("🚀 Pipeline setup complete! You can now run:")
        logger.info("   python run_vectordb_sync.py sync")
        logger.info("   python run_vectordb_sync.py test --query 'What is NVDA RSI?'")
    else:
        logger.error("❌ Setup incomplete - please check logs above")

if __name__ == "__main__":
    asyncio.run(main())
