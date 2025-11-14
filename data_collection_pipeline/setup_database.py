#!/usr/bin/env python3
"""
Setup script to initialize the new 'quant_verse' database
and update the pipeline configuration to use it.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
log_file = f"logs/database_setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def create_database():
    """Create the quant_verse database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (default database)
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='sandeep',
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'quant_verse'")
        exists = cursor.fetchone()
        
        if not exists:
            logger.info("Creating 'quant_verse' database...")
            cursor.execute("CREATE DATABASE quant_verse")
            logger.info("Database 'quant_verse' created successfully!")
        else:
            logger.info("Database 'quant_verse' already exists")
            
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False

def run_schema_script():
    """Run the schema creation script on the new database"""
    try:
        # Connect to the new quant_verse database
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='sandeep',
            database='quant_verse'
        )
        cursor = conn.cursor()
        
        # Read and execute the schema script
        schema_file = Path('quant_verse_schema_clean.sql')
        if not schema_file.exists():
            logger.error("Schema file 'quant_verse_schema_clean.sql' not found!")
            return False
            
        logger.info("Executing schema creation script...")
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
            
        # Execute the schema (split by semicolons for better error handling)
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements):
            try:
                cursor.execute(statement)
                if i % 10 == 0:  # Log progress every 10 statements
                    logger.info(f"Executed {i+1}/{len(statements)} statements...")
            except Exception as e:
                if "already exists" not in str(e).lower():
                    logger.warning(f"Statement {i+1} failed: {e}")
                    logger.warning(f"Statement: {statement[:100]}...")
        
        conn.commit()
        logger.info("Schema creation completed successfully!")
        
        # Verify table creation
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        logger.info(f"Created {len(tables)} tables:")
        for table in tables:
            logger.info(f"  - {table[0]}")
            
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error running schema script: {e}")
        return False

def update_config():
    """Update the config.py file to use the new database"""
    try:
        config_file = Path('config.py')
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Replace database references
        updated_content = content.replace(
            "database: str = os.getenv('POSTGRES_DB', 'urisk_core')",
            "database: str = os.getenv('POSTGRES_DB', 'quant_verse')"
        ).replace(
            "'postgresql://postgres:sandeep@localhost:5432/urisk_core'",
            "'postgresql://postgres:sandeep@localhost:5432/quant_verse'"
        )
        
        with open(config_file, 'w') as f:
            f.write(updated_content)
            
        logger.info("Updated config.py to use 'quant_verse' database")
        return True
        
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return False

def test_connection():
    """Test connection to the new database"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='sandeep',
            database='quant_verse'
        )
        cursor = conn.cursor()
        
        # Test basic queries
        cursor.execute("SELECT COUNT(*) FROM assets")
        result = cursor.fetchone()
        asset_count = result[0] if result else 0
        logger.info(f"Found {asset_count} assets in the database")
        
        cursor.execute("SELECT COUNT(*) FROM provider_status")
        result = cursor.fetchone()
        provider_count = result[0] if result else 0
        logger.info(f"Found {provider_count} providers configured")
        
        cursor.execute("SELECT session_id FROM ingestion_sessions LIMIT 1")
        session = cursor.fetchone()
        if session:
            logger.info(f"Sample session found: {session[0]}")
        else:
            logger.info("No ingestion sessions yet (expected for new database)")
        
        cursor.close()
        conn.close()
        logger.info("Database connection test successful!")
        return True
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Starting QuantVerse database setup...")
    
    # Step 1: Create database
    if not create_database():
        logger.error("❌ Failed to create database. Exiting.")
        sys.exit(1)
    
    # Step 2: Run schema script
    if not run_schema_script():
        logger.error("❌ Failed to create schema. Exiting.")
        sys.exit(1)
    
    # Step 3: Update configuration
    if not update_config():
        logger.error("❌ Failed to update configuration. Exiting.")
        sys.exit(1)
    
    # Step 4: Test connection
    if not test_connection():
        logger.error("❌ Database connection test failed. Exiting.")
        sys.exit(1)
    
    logger.info("✅ QuantVerse database setup completed successfully!")
    logger.info("🎯 Ready to run data collection pipeline with new schema")
    logger.info(f"📋 Setup log saved to: {log_file}")
    
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("✅ Database: quant_verse")
    print("✅ Schema: QuantVerse Unified v2.1")
    print("✅ Configuration: Updated")
    print("✅ Connection: Tested")
    print("\n🚀 Ready to run: python main.py --mode full")
    print("="*60)

if __name__ == "__main__":
    main()
