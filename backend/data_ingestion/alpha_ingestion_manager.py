"""
Alpha Vantage Ingestion Manager - 200-Batch, Epoch-Based Ingestion System
Enterprise-grade, fault-tolerant data ingestion for 200 global tickers
Follows ML training paradigm with epochs, checkpoints, and batches
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import traceback
from dataclasses import dataclass
from pathlib import Path

from ..config.settings import settings
from ..db.postgres_handler import PostgresHandler
from ..utils.top_200_companies_complete import Top200Companies
from .alpha_fetcher import AlphaFetcher
from .alpha_normalizer import AlphaNormalizer
from .alpha_writer import AlphaWriter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('alpha_ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class IngestionProgress:
    """Represents ingestion progress for a ticker"""
    ticker: str
    last_completed_endpoint: Optional[str]
    epoch: int
    updated_at: datetime
    total_endpoints_completed: int = 0
    total_records_inserted: int = 0
    
@dataclass
class EpochResult:
    """Result of processing one epoch (one ticker)"""
    ticker: str
    epoch: int
    success: bool
    endpoints_completed: int
    total_records: int
    errors: List[str]
    duration_seconds: float
    start_time: datetime
    end_time: datetime

class AlphaIngestionManager:
    """
    Main orchestrator for Alpha Vantage data ingestion using epoch-based approach.
    Each epoch processes ALL endpoints for ONE ticker.
    
    Design Philosophy:
    - Epoch = One pass over all Alpha Vantage endpoints for one ticker
    - Checkpoint = Resume capability from last saved ticker + endpoint
    - Batch = 200 tickers broken into manageable chunks
    """
    
    def __init__(self):
        """Initialize the ingestion manager with all required components"""
        self.db = PostgresHandler()
        self.fetcher = AlphaFetcher()
        self.normalizer = AlphaNormalizer()
        self.writer = AlphaWriter()
        
        # Get complete company list
        self.companies = Top200Companies.get_all_companies()
        
        # Ingestion state
        self.current_epoch = 1
        self.total_epochs = len(self.companies)
        self.ingestion_start_time = None
        self.ingestion_id = None
        
        # Statistics
        self.total_records_inserted = 0
        self.total_api_calls = 0
        self.total_errors = 0
        self.epoch_results: List[EpochResult] = []
        
    async def initialize_ingestion_session(self) -> str:
        """Initialize a new ingestion session and create tracking tables"""
        logger.info("🚀 Initializing Alpha Vantage Ingestion Session")
        
        # Create ingestion session ID
        self.ingestion_start_time = datetime.now()
        self.ingestion_id = f"alpha_ingestion_{self.ingestion_start_time.strftime('%Y%m%d_%H%M%S')}"
        
        # Ensure all required tables exist
        await self.create_ingestion_tables()
        
        # Create ingestion session record
        await self.create_ingestion_session_record()
        
        logger.info(f"✅ Ingestion session initialized: {self.ingestion_id}")
        return self.ingestion_id
    
    async def create_ingestion_tables(self):
        """Create all required tables for ingestion tracking and data storage"""
        logger.info("📊 Creating ingestion tracking tables...")
        
        # Execute each statement separately
        statements = [
            # Ingestion progress tracking table
            """
            CREATE TABLE IF NOT EXISTS ingestion_progress (
                ticker VARCHAR(20) PRIMARY KEY,
                last_completed_endpoint VARCHAR(50),
                epoch INT,
                total_endpoints_completed INT DEFAULT 0,
                total_records_inserted INT DEFAULT 0,
                ingestion_session_id VARCHAR(100),
                updated_at TIMESTAMP DEFAULT NOW(),
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            
            # Ingestion session tracking
            """
            CREATE TABLE IF NOT EXISTS ingestion_sessions (
                session_id VARCHAR(100) PRIMARY KEY,
                start_time TIMESTAMP DEFAULT NOW(),
                end_time TIMESTAMP,
                status VARCHAR(20) DEFAULT 'running',
                total_tickers INT,
                completed_tickers INT DEFAULT 0,
                total_records INT DEFAULT 0,
                total_api_calls INT DEFAULT 0,
                total_errors INT DEFAULT 0,
                metadata JSONB
            )
            """,
            
            # Enhanced market data table with full metadata
            """
            CREATE TABLE IF NOT EXISTS alpha_vantage_data (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(20) NOT NULL,
                endpoint VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                raw_payload JSONB NOT NULL,
                parsed_values JSONB,
                quality_flag VARCHAR(20) DEFAULT 'success',
                ingestion_epoch INT,
                ingestion_sequence BIGINT,
                ingestion_session_id VARCHAR(100),
                ingestion_time TIMESTAMP DEFAULT NOW(),
                source VARCHAR(20) DEFAULT 'alpha_vantage',
                data_type VARCHAR(30),
                interval_period VARCHAR(10),
                metadata JSONB,
                UNIQUE(ticker, endpoint, timestamp)
            )
            """,
            
            # ChromaDB metadata tracking
            """
            CREATE TABLE IF NOT EXISTS chroma_embeddings (
                id SERIAL PRIMARY KEY,
                collection_name VARCHAR(100) NOT NULL,
                document_id VARCHAR(100) NOT NULL,
                ticker VARCHAR(20),
                endpoint VARCHAR(50),
                timestamp TIMESTAMP,
                chunk_index INT DEFAULT 0,
                embedding_model VARCHAR(100),
                text_content TEXT,
                metadata JSONB,
                ingestion_session_id VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(collection_name, document_id)
            )
            """
        ]
        
        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_alpha_data_ticker_endpoint ON alpha_vantage_data(ticker, endpoint)",
            "CREATE INDEX IF NOT EXISTS idx_alpha_data_timestamp ON alpha_vantage_data(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_alpha_data_ingestion_epoch ON alpha_vantage_data(ingestion_epoch)",
            "CREATE INDEX IF NOT EXISTS idx_alpha_data_session ON alpha_vantage_data(ingestion_session_id)",
            "CREATE INDEX IF NOT EXISTS idx_chroma_ticker ON chroma_embeddings(ticker)",
            "CREATE INDEX IF NOT EXISTS idx_chroma_collection ON chroma_embeddings(collection_name)"
        ]
        
        # Execute table creation
        for sql in statements:
            await self.db.async_execute_query(sql)
        
        # Execute index creation
        for sql in indexes:
            await self.db.async_execute_query(sql)
        
        logger.info("✅ All ingestion tables created successfully")
    
    async def create_ingestion_session_record(self):
        """Create a record for this ingestion session"""
        session_sql = """
        INSERT INTO ingestion_sessions (
            session_id, start_time, total_tickers, metadata
        ) VALUES ($1, $2, $3, $4)
        ON CONFLICT (session_id) DO UPDATE SET
            start_time = EXCLUDED.start_time,
            total_tickers = EXCLUDED.total_tickers,
            metadata = EXCLUDED.metadata;
        """
        
        metadata = {
            "system_info": {
                "python_version": "3.12.8",
                "platform": "macOS Darwin 25.0.0",
                "ingestion_strategy": "epoch_based_200_batch"
            },
            "configuration": {
                "total_companies": len(self.companies),
                "total_endpoints": len(self.fetcher.get_all_endpoints()),
                "rate_limit_delay": 0.6,
                "batch_size": 1,
                "parallel_endpoints": 3
            }
        }
        
        await self.db.async_execute_query(
            session_sql, 
            (self.ingestion_id, self.ingestion_start_time, len(self.companies), json.dumps(metadata))
        )
    
    async def run_complete_ingestion(self, start_epoch: int = 1, max_epochs: Optional[int] = None) -> Dict[str, Any]:
        """
        Run complete 200-batch ingestion with fault tolerance.
        
        Args:
            start_epoch: Which epoch to start from (for manual restart)
            max_epochs: Maximum number of epochs to run (for testing)
        """
        logger.info("🚀 Starting Alpha Vantage 200-Batch Epoch-Based Ingestion")
        logger.info(f"📊 Total Companies: {len(self.companies)}")
        logger.info(f"🎯 Total Endpoints: {len(self.fetcher.get_all_endpoints())}")
        
        # Initialize session
        await self.initialize_ingestion_session()
        
        # Determine epochs to process
        epochs_to_process = self.companies[start_epoch-1:]
        if max_epochs:
            epochs_to_process = epochs_to_process[:max_epochs]
        
        logger.info(f"🎯 Processing epochs {start_epoch} to {start_epoch + len(epochs_to_process) - 1}")
        
        try:
            # Process each epoch (ticker)
            for company in epochs_to_process:
                epoch_result = await self.process_epoch(company)
                self.epoch_results.append(epoch_result)
                
                # Update session statistics
                await self.update_session_statistics(epoch_result)
                
                # Log epoch completion
                self.log_epoch_completion(epoch_result)
                
                # Brief pause between epochs to respect rate limits
                await asyncio.sleep(1.0)
            
            # Complete ingestion
            final_stats = await self.complete_ingestion_session()
            
            logger.info("🎉 INGESTION COMPLETED SUCCESSFULLY!")
            return final_stats
            
        except Exception as e:
            logger.error(f"❌ Ingestion failed: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Mark session as failed
            await self.mark_session_failed(str(e))
            
            raise e
    
    async def process_epoch(self, company: Dict[str, Any]) -> EpochResult:
        """
        Process one epoch: fetch ALL Alpha Vantage endpoints for ONE ticker.
        
        Args:
            company: Company information dict with symbol, name, epoch, etc.
        
        Returns:
            EpochResult with success status and statistics
        """
        ticker = company["symbol"]
        epoch = company["epoch"]
        
        logger.info(f"🔄 Starting Epoch {epoch}: {ticker} ({company['name']})")
        epoch_start = datetime.now()
        
        # Get current progress for this ticker
        progress = await self.get_ticker_progress(ticker)
        
        # Get all endpoints to process
        all_endpoints = self.fetcher.get_all_endpoints()
        
        # Filter out already completed endpoints
        remaining_endpoints = self.filter_remaining_endpoints(all_endpoints, progress)
        
        logger.info(f"📋 Ticker {ticker}: {len(remaining_endpoints)} endpoints remaining")
        
        # Process each endpoint
        records_inserted = 0
        errors = []
        completed_endpoints = 0
        
        for endpoint_name in remaining_endpoints:
            try:
                # Fetch data from Alpha Vantage
                endpoint_result = await self.process_endpoint(ticker, endpoint_name, epoch)
                
                if endpoint_result['success']:
                    records_inserted += endpoint_result['records_count']
                    completed_endpoints += 1
                    
                    # Update progress checkpoint
                    await self.update_ticker_progress(ticker, endpoint_name, epoch, records_inserted)
                    
                    logger.debug(f"✅ {ticker} - {endpoint_name}: {endpoint_result['records_count']} records")
                else:
                    errors.append(f"{endpoint_name}: {endpoint_result['error']}")
                    logger.warning(f"⚠️ {ticker} - {endpoint_name}: {endpoint_result['error']}")
                
                # Respect rate limits
                await asyncio.sleep(0.6)  # 600ms delay between API calls
                
            except Exception as e:
                error_msg = f"{endpoint_name}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"❌ {ticker} - {endpoint_name}: {str(e)}")
                continue
        
        epoch_end = datetime.now()
        duration = (epoch_end - epoch_start).total_seconds()
        
        # Create epoch result
        epoch_result = EpochResult(
            ticker=ticker,
            epoch=epoch,
            success=len(errors) < len(remaining_endpoints) / 2,  # Success if < 50% errors
            endpoints_completed=completed_endpoints,
            total_records=records_inserted,
            errors=errors,
            duration_seconds=duration,
            start_time=epoch_start,
            end_time=epoch_end
        )
        
        return epoch_result
    
    async def process_endpoint(self, ticker: str, endpoint: str, epoch: int) -> Dict[str, Any]:
        """
        Process a single endpoint for a ticker.
        
        Returns:
            Dict with success status, records count, and error info
        """
        try:
            # Fetch data from Alpha Vantage
            success, raw_data, error = await self.fetcher.fetch_endpoint(endpoint, ticker)
            
            if not success or not raw_data:
                return {
                    'success': False,
                    'error': error or 'No data returned',
                    'records_count': 0
                }
            
            if 'Error Message' in str(raw_data):
                return {
                    'success': False,
                    'error': f"API error: {raw_data.get('Error Message', 'Unknown error')}",
                    'records_count': 0
                }
            
            # Normalize the data
            normalized_data = self.normalizer.normalize_endpoint_data(endpoint, raw_data, ticker)
            
            # Write to PostgreSQL
            postgres_records = await self.writer.write_to_postgres(
                ticker, endpoint, normalized_data, raw_data, epoch, self.ingestion_id or ""
            )
            
            # Write to ChromaDB for text-based endpoints
            if self.should_embed_endpoint(endpoint):
                await self.writer.write_to_chromadb(
                    ticker, endpoint, normalized_data, raw_data, self.ingestion_id or ""
                )
            
            self.total_api_calls += 1
            self.total_records_inserted += postgres_records
            
            return {
                'success': True,
                'records_count': postgres_records,
                'error': None
            }
            
        except Exception as e:
            self.total_errors += 1
            return {
                'success': False,
                'error': str(e),
                'records_count': 0
            }
    
    def should_embed_endpoint(self, endpoint: str) -> bool:
        """Determine if endpoint data should be embedded in ChromaDB"""
        text_endpoints = [
            'NEWS_SENTIMENT', 
            'EARNINGS_CALL_TRANSCRIPT', 
            'TOP_GAINERS_LOSERS',
            'INSIDER_TRANSACTIONS',
            'OVERVIEW'
        ]
        return endpoint in text_endpoints
    
    async def get_ticker_progress(self, ticker: str) -> Optional[IngestionProgress]:
        """Get current ingestion progress for a ticker"""
        sql = """
        SELECT ticker, last_completed_endpoint, epoch, total_endpoints_completed, 
               total_records_inserted, updated_at
        FROM ingestion_progress 
        WHERE ticker = $1
        """
        
        result = await self.db.async_execute_query(sql, (ticker,))
        
        if result and len(result) > 0:
            row = result[0]
            return IngestionProgress(
                ticker=row['ticker'],
                last_completed_endpoint=row['last_completed_endpoint'],
                epoch=row['epoch'],
                updated_at=row['updated_at'],
                total_endpoints_completed=row['total_endpoints_completed'],
                total_records_inserted=row['total_records_inserted']
            )
        
        return None
    
    def filter_remaining_endpoints(self, all_endpoints: List[str], progress: Optional[IngestionProgress]) -> List[str]:
        """Filter out already completed endpoints based on progress"""
        if not progress or not progress.last_completed_endpoint:
            return all_endpoints
        
        # Find index of last completed endpoint
        try:
            last_index = all_endpoints.index(progress.last_completed_endpoint)
            return all_endpoints[last_index + 1:]  # Return endpoints after the last completed one
        except ValueError:
            # Endpoint not found, return all endpoints
            return all_endpoints
    
    async def update_ticker_progress(self, ticker: str, endpoint: str, epoch: int, total_records: int):
        """Update progress checkpoint for a ticker"""
        sql = """
        INSERT INTO ingestion_progress (
            ticker, last_completed_endpoint, epoch, total_endpoints_completed, 
            total_records_inserted, ingestion_session_id, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (ticker) DO UPDATE SET
            last_completed_endpoint = EXCLUDED.last_completed_endpoint,
            epoch = EXCLUDED.epoch,
            total_endpoints_completed = ingestion_progress.total_endpoints_completed + 1,
            total_records_inserted = EXCLUDED.total_records_inserted,
            ingestion_session_id = EXCLUDED.ingestion_session_id,
            updated_at = EXCLUDED.updated_at;
        """
        
        await self.db.async_execute_query(sql, (
            ticker, endpoint, epoch, 1, total_records, self.ingestion_id or "", datetime.now()
        ))
    
    async def update_session_statistics(self, epoch_result: EpochResult):
        """Update ingestion session statistics"""
        sql = """
        UPDATE ingestion_sessions 
        SET completed_tickers = completed_tickers + 1,
            total_records = total_records + $1,
            total_errors = total_errors + $2,
            metadata = jsonb_set(
                metadata, 
                '{last_completed_epoch}', 
                to_jsonb($3::int)
            )
        WHERE session_id = $4;
        """
        
        await self.db.async_execute_query(sql, (
            epoch_result.total_records,
            len(epoch_result.errors),
            epoch_result.epoch,
            self.ingestion_id or ""
        ))
    
    async def complete_ingestion_session(self) -> Dict[str, Any]:
        """Mark ingestion session as complete and return final statistics"""
        end_time = datetime.now()
        duration = (end_time - (self.ingestion_start_time or datetime.now())).total_seconds()
        
        # Update session record
        sql = """
        UPDATE ingestion_sessions 
        SET end_time = $1,
            status = 'completed',
            total_api_calls = $2,
            metadata = jsonb_set(
                metadata,
                '{completion_stats}',
                $3::jsonb
            )
        WHERE session_id = $4;
        """
        
        completion_stats = {
            "total_duration_seconds": duration,
            "total_epochs_processed": len(self.epoch_results),
            "successful_epochs": len([r for r in self.epoch_results if r.success]),
            "failed_epochs": len([r for r in self.epoch_results if not r.success]),
            "average_epoch_duration": duration / len(self.epoch_results) if self.epoch_results else 0,
            "total_unique_tickers": len(set(r.ticker for r in self.epoch_results)),
            "records_per_second": self.total_records_inserted / duration if duration > 0 else 0
        }
        
        await self.db.async_execute_query(sql, (
            end_time, self.total_api_calls, json.dumps(completion_stats), self.ingestion_id or ""
        ))
        
        # Generate final report
        final_stats = {
            "session_id": self.ingestion_id,
            "status": "completed",
            "start_time": (self.ingestion_start_time or datetime.now()).isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "total_epochs": len(self.epoch_results),
            "successful_epochs": len([r for r in self.epoch_results if r.success]),
            "total_records_inserted": self.total_records_inserted,
            "total_api_calls": self.total_api_calls,
            "total_errors": self.total_errors,
            "average_records_per_epoch": self.total_records_inserted / len(self.epoch_results) if self.epoch_results else 0,
            "ingestion_rate_per_second": self.total_records_inserted / duration if duration > 0 else 0,
            "epoch_results": [
                {
                    "ticker": r.ticker,
                    "epoch": r.epoch,
                    "success": r.success,
                    "records": r.total_records,
                    "duration": r.duration_seconds,
                    "error_count": len(r.errors)
                }
                for r in self.epoch_results
            ]
        }
        
        return final_stats
    
    async def mark_session_failed(self, error_message: str):
        """Mark ingestion session as failed"""
        sql = """
        UPDATE ingestion_sessions 
        SET end_time = $1,
            status = 'failed',
            metadata = jsonb_set(
                metadata,
                '{error_info}',
                $2
            )
        WHERE session_id = $3;
        """
        
        error_info = {
            "error_message": error_message,
            "failed_at": datetime.now().isoformat(),
            "epochs_completed": len(self.epoch_results),
            "records_before_failure": self.total_records_inserted
        }
        
        await self.db.async_execute_query(sql, (
            datetime.now(), json.dumps(error_info), self.ingestion_id or ""
        ))
    
    def log_epoch_completion(self, epoch_result: EpochResult):
        """Log completion of an epoch with detailed statistics"""
        success_icon = "✅" if epoch_result.success else "❌"
        
        logger.info(
            f"{success_icon} Epoch {epoch_result.epoch} Complete: "
            f"{epoch_result.ticker} | "
            f"Records: {epoch_result.total_records} | "
            f"Duration: {epoch_result.duration_seconds:.1f}s | "
            f"Endpoints: {epoch_result.endpoints_completed} | "
            f"Errors: {len(epoch_result.errors)}"
        )
        
        if epoch_result.errors:
            for error in epoch_result.errors[:3]:  # Show first 3 errors
                logger.warning(f"   ⚠️ {error}")
    
    async def resume_from_checkpoint(self) -> Dict[str, Any]:
        """Resume ingestion from last checkpoint"""
        logger.info("🔄 Resuming ingestion from checkpoint...")
        
        # Find last incomplete session
        last_session_sql = """
        SELECT session_id, start_time, status, completed_tickers
        FROM ingestion_sessions 
        WHERE status = 'running'
        ORDER BY start_time DESC 
        LIMIT 1;
        """
        
        result = await self.db.async_execute_query(last_session_sql)
        
        if result and len(result) > 0:
            session = result[0]
            logger.info(f"📋 Found incomplete session: {session['session_id']}")
            logger.info(f"📊 Completed tickers: {session['completed_tickers']}")
            
            # Resume from next epoch
            start_epoch = session['completed_tickers'] + 1
            return await self.run_complete_ingestion(start_epoch=start_epoch)
        else:
            logger.info("ℹ️ No incomplete session found, starting fresh")
            return await self.run_complete_ingestion()


# Main execution function
async def main():
    """Main function to run the Alpha Vantage ingestion"""
    manager = AlphaIngestionManager()
    
    try:
        # Run complete ingestion
        final_stats = await manager.run_complete_ingestion()
        
        print("\n" + "="*80)
        print("🎉 ALPHA VANTAGE INGESTION COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(f"📊 Total Records: {final_stats['total_records_inserted']:,}")
        print(f"🎯 Total Epochs: {final_stats['total_epochs']}")
        print(f"⏱️ Duration: {final_stats['duration_seconds']:.1f} seconds")
        print(f"📈 Rate: {final_stats['ingestion_rate_per_second']:.2f} records/second")
        print(f"✅ Success Rate: {final_stats['successful_epochs']}/{final_stats['total_epochs']}")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n⚠️ Ingestion interrupted by user")
        print("💡 You can resume from checkpoint by running the script again")
    except Exception as e:
        print(f"\n❌ Ingestion failed: {e}")
        print("💡 Check logs for detailed error information")


if __name__ == "__main__":
    asyncio.run(main())
