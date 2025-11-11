"""
PostgreSQL to ChromaDB Incremental Sync Pipeline
Converts financial data from PostgreSQL into semantic chunks for RAG.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
import json
import hashlib
import re
from dataclasses import dataclass

from ..db.postgres_handler import PostgresHandler
from ..rag_engine.vector_store import vector_store
from ..embeddings.sentence_embedder import SentenceEmbedder  # We'll create this

logger = logging.getLogger(__name__)

def make_aware(dt):
    """Convert naive datetime to UTC-aware datetime for safe comparison."""
    if dt is None:
        return None
    if dt.tzinfo is None:  # naive → convert to UTC
        return dt.replace(tzinfo=timezone.utc)
    return dt

@dataclass
class SyncState:
    """Tracks synchronization state for each table."""
    table_name: str
    last_synced_at: Optional[datetime] = None
    records_synced: int = 0
    last_chunk_id: Optional[str] = None

@dataclass
class DataChunk:
    """Represents a data chunk ready for embedding."""
    text: str
    metadata: Dict[str, Any]
    chunk_id: str

class PostgresToVectorDBPipeline:
    """Main pipeline for syncing PostgreSQL data to ChromaDB."""
    
    def __init__(self):
        self.postgres = PostgresHandler()
        self.embedder = None
        self.batch_size = 256  # Updated to match config
        
    async def initialize(self):
        """Initialize all components."""
        try:
            # Initialize PostgreSQL connections
            await self.postgres.initialize_async_pool(min_size=2, max_size=10)
            self.postgres.initialize_sync_pool(min_conn=1, max_conn=5)
            
            # Initialize ChromaDB
            vector_store.initialize()
            
            # Initialize embedder
            self.embedder = SentenceEmbedder()
            await self.embedder.initialize()
            
            # Create sync state table if not exists
            await self.create_sync_state_table()
            
            logger.info("PostgreSQL to VectorDB pipeline initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            raise
    
    async def create_sync_state_table(self):
        """Create vector sync state tracking table."""
        try:
            query = """
            CREATE TABLE IF NOT EXISTS vector_sync_state (
                table_name VARCHAR(100) PRIMARY KEY,
                last_synced_at TIMESTAMP,
                records_synced BIGINT DEFAULT 0,
                last_chunk_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            """
            await self.postgres.async_execute_insert(query)
            logger.info("Vector sync state table ready")
            
        except Exception as e:
            logger.error(f"Failed to create sync state table: {e}")
            raise
    
    async def get_sync_state(self, table_name: str) -> SyncState:
        """Get last sync state for a table."""
        try:
            query = """
            SELECT table_name, last_synced_at, records_synced, last_chunk_id
            FROM vector_sync_state 
            WHERE table_name = $1
            """
            
            results = await self.postgres.async_execute_query(query, (table_name,))
            result = results[0] if results else None
            
            if result:
                return SyncState(
                    table_name=result['table_name'],
                    last_synced_at=result['last_synced_at'],
                    records_synced=result['records_synced'],
                    last_chunk_id=result['last_chunk_id']
                )
            else:
                # First time sync - return default state
                return SyncState(table_name=table_name)
                
        except Exception as e:
            logger.error(f"Failed to get sync state for {table_name}: {e}")
            return SyncState(table_name=table_name)
    
    async def update_sync_state(self, state: SyncState):
        """Update sync state after successful processing."""
        try:
            query = """
            INSERT INTO vector_sync_state (table_name, last_synced_at, records_synced, last_chunk_id, updated_at)
            VALUES ($1, $2, $3, $4, NOW())
            ON CONFLICT (table_name) 
            DO UPDATE SET 
                last_synced_at = EXCLUDED.last_synced_at,
                records_synced = EXCLUDED.records_synced,
                last_chunk_id = EXCLUDED.last_chunk_id,
                updated_at = NOW()
            """
            
            await self.postgres.async_execute_insert(
                query, 
                (state.table_name, 
                state.last_synced_at, 
                state.records_synced, 
                state.last_chunk_id)
            )
            
        except Exception as e:
            logger.error(f"Failed to update sync state: {e}")
            raise
    
    def generate_chunk_id(self, table_name: str, record_id: Any, chunk_index: int = 0) -> str:
        """Generate unique chunk ID."""
        content = f"{table_name}_{record_id}_{chunk_index}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def convert_to_readable_text(self, endpoint: str, data: Dict[str, Any], ticker: str, timestamp: datetime) -> List[str]:
        """Convert data record to human-readable text chunks."""
        chunks = []
        
        try:
            if endpoint in ['RSI', 'EMA', 'BBANDS', 'MFI', 'ADX', 'TRIX']:
                # Technical indicators
                chunks.extend(self._convert_technical_indicator(endpoint, data, ticker, timestamp))
                
            elif endpoint in ['OVERVIEW', 'EARNINGS', 'BALANCE_SHEET', 'CASH_FLOW']:
                # Fundamental data
                chunks.extend(self._convert_fundamental_data(endpoint, data, ticker, timestamp))
                
            elif endpoint in ['TIME_SERIES_DAILY', 'TIME_SERIES_WEEKLY', 'TIME_SERIES_MONTHLY']:
                # Time series data (summarized)
                chunks.extend(self._convert_time_series_data(endpoint, data, ticker, timestamp))
                
            elif endpoint in ['NEWS_SENTIMENT']:
                # News and sentiment
                chunks.extend(self._convert_news_sentiment(data, ticker, timestamp))
                
            elif endpoint in ['TOP_GAINERS_LOSERS', 'MARKET_STATUS']:
                # Market intelligence
                chunks.extend(self._convert_market_intelligence(endpoint, data, timestamp))
                
            else:
                # Generic conversion
                chunks.extend(self._convert_generic_data(endpoint, data, ticker, timestamp))
                
        except Exception as e:
            logger.error(f"Failed to convert {endpoint} data for {ticker}: {e}")
            # Fallback to generic conversion
            chunks.extend(self._convert_generic_data(endpoint, data, ticker, timestamp))
        
        return chunks
    
    def _convert_technical_indicator(self, endpoint: str, data: Dict[str, Any], ticker: str, timestamp: datetime) -> List[str]:
        """Convert technical indicator data to readable text."""
        chunks = []
        date_str = timestamp.strftime('%Y-%m-%d')
        
        if endpoint == 'RSI':
            rsi_value = data.get('RSI', 'N/A')
            if rsi_value != 'N/A':
                try:
                    rsi_float = float(rsi_value)
                    momentum = "overbought" if rsi_float > 70 else "oversold" if rsi_float < 30 else "neutral"
                    chunks.append(f"On {date_str}, {ticker} RSI was {rsi_value}, indicating {momentum} momentum.")
                except:
                    chunks.append(f"On {date_str}, {ticker} RSI was {rsi_value}.")
                    
        elif endpoint == 'EMA':
            for key, value in data.items():
                if 'EMA' in key and value != 'N/A':
                    chunks.append(f"On {date_str}, {ticker} {key} was ${value}.")
                    
        elif endpoint == 'BBANDS':
            upper = data.get('Real Upper Band', 'N/A')
            middle = data.get('Real Middle Band', 'N/A') 
            lower = data.get('Real Lower Band', 'N/A')
            if all(x != 'N/A' for x in [upper, middle, lower]):
                chunks.append(f"On {date_str}, {ticker} Bollinger Bands: Upper ${upper}, Middle ${middle}, Lower ${lower}.")
                
        elif endpoint == 'MFI':
            mfi_value = data.get('MFI', 'N/A')
            if mfi_value != 'N/A':
                try:
                    mfi_float = float(mfi_value)
                    flow = "strong buying" if mfi_float > 80 else "strong selling" if mfi_float < 20 else "balanced"
                    chunks.append(f"On {date_str}, {ticker} Money Flow Index was {mfi_value}, indicating {flow} pressure.")
                except:
                    chunks.append(f"On {date_str}, {ticker} Money Flow Index was {mfi_value}.")
        
        return chunks
    
    def _convert_fundamental_data(self, endpoint: str, data: Dict[str, Any], ticker: str, timestamp: datetime) -> List[str]:
        """Convert fundamental data to readable text."""
        chunks = []
        
        if endpoint == 'OVERVIEW':
            # Company overview
            market_cap = data.get('MarketCapitalization', 'N/A')
            pe_ratio = data.get('PERatio', 'N/A')
            sector = data.get('Sector', 'N/A')
            industry = data.get('Industry', 'N/A')
            
            if market_cap != 'N/A':
                try:
                    market_cap_billions = float(market_cap) / 1e9
                    chunks.append(f"{ticker} has a market cap of ${market_cap_billions:.1f}B in {sector} sector.")
                except:
                    chunks.append(f"{ticker} market cap: {market_cap}, sector: {sector}.")
                    
            if pe_ratio not in ['N/A', 'None']:
                chunks.append(f"{ticker} trading at P/E ratio of {pe_ratio}.")
                
        elif endpoint == 'EARNINGS':
            # Earnings data
            eps = data.get('reportedEPS', data.get('estimatedEPS', 'N/A'))
            revenue = data.get('reportedRevenue', 'N/A') 
            
            if eps != 'N/A':
                chunks.append(f"{ticker} reported EPS of ${eps}.")
            if revenue != 'N/A':
                try:
                    revenue_millions = float(revenue) / 1e6
                    chunks.append(f"{ticker} reported revenue of ${revenue_millions:.1f}M.")
                except:
                    chunks.append(f"{ticker} reported revenue of {revenue}.")
        
        return chunks
    
    def _convert_time_series_data(self, endpoint: str, data: Dict[str, Any], ticker: str, timestamp: datetime) -> List[str]:
        """Convert time series data to summarized readable text."""
        chunks = []
        
        # For time series, we'll create summary chunks rather than individual price points
        close_price = data.get('4. close', data.get('close', 'N/A'))
        volume = data.get('5. volume', data.get('volume', 'N/A'))
        
        date_str = timestamp.strftime('%Y-%m-%d')
        
        if close_price != 'N/A':
            chunks.append(f"On {date_str}, {ticker} closed at ${close_price}.")
            
        if volume != 'N/A':
            try:
                volume_millions = float(volume) / 1e6
                volume_level = "high" if volume_millions > 10 else "normal"
                chunks.append(f"On {date_str}, {ticker} traded {volume_millions:.1f}M shares ({volume_level} volume).")
            except:
                chunks.append(f"On {date_str}, {ticker} volume was {volume}.")
        
        return chunks
    
    def _convert_news_sentiment(self, data: Dict[str, Any], ticker: str, timestamp: datetime) -> List[str]:
        """Convert news sentiment data to readable text.""" 
        chunks = []
        
        headline = data.get('title', data.get('headline', ''))
        sentiment_score = data.get('sentiment_score', data.get('overall_sentiment_score', 0))
        
        if headline:
            sentiment_text = "positive" if sentiment_score > 0.1 else "negative" if sentiment_score < -0.1 else "neutral"
            date_str = timestamp.strftime('%Y-%m-%d')
            chunks.append(f"{sentiment_text.capitalize()} sentiment for {ticker} on {date_str}: '{headline}' (score {sentiment_score:.2f})")
        
        return chunks
    
    def _convert_market_intelligence(self, endpoint: str, data: Dict[str, Any], timestamp: datetime) -> List[str]:
        """Convert market intelligence data to readable text."""
        chunks = []
        date_str = timestamp.strftime('%Y-%m-%d')
        
        if endpoint == 'TOP_GAINERS_LOSERS':
            # Top gainers/losers
            if 'ticker' in data and 'change_percentage' in data:
                ticker = data['ticker']
                change_pct = data['change_percentage']
                chunks.append(f"On {date_str}, {ticker} was a top mover with {change_pct} change.")
                
        elif endpoint == 'MARKET_STATUS':
            # Market status
            status = data.get('current_status', 'unknown')
            chunks.append(f"Market status on {date_str}: {status}")
        
        return chunks
    
    def _convert_generic_data(self, endpoint: str, data: Dict[str, Any], ticker: str, timestamp: datetime) -> List[str]:
        """Fallback generic conversion."""
        date_str = timestamp.strftime('%Y-%m-%d')
        
        # Extract key metrics from any data
        text_parts = [f"On {date_str}, {ticker} {endpoint} data"]
        
        for key, value in data.items():
            if isinstance(value, (int, float)) and key.lower() not in ['timestamp', 'id', 'created_at']:
                text_parts.append(f"{key}: {value}")
        
        return [". ".join(text_parts[:3]) + "."]  # Limit length
    
    def create_chunk_metadata(self, endpoint: str, ticker: str, timestamp: datetime, record_id: Any) -> Dict[str, Any]:
        """Create metadata for a chunk."""
        
        # Determine asset type
        asset_type = "stock"  # Default
        if ticker.endswith("USD") or ticker in ["BTC", "ETH", "DOGE"]:
            asset_type = "crypto"
        elif ticker.startswith("^") or ticker in ["SPY", "QQQ", "DIA"]:
            asset_type = "index"
        
        # Determine risk type
        risk_type = "technical"
        if endpoint in ['NEWS_SENTIMENT']:
            risk_type = "sentiment"
        elif endpoint in ['OVERVIEW', 'EARNINGS', 'BALANCE_SHEET']:
            risk_type = "fundamental"
        elif endpoint in ['MARKET_STATUS', 'TOP_GAINERS_LOSERS']:
            risk_type = "macro"
        
        # Determine severity (for anomaly detection)
        severity = "low"  # Default
        
        return {
            "ticker": ticker,
            "asset_type": asset_type,
            "source": "alpha_vantage",
            "endpoint": endpoint,
            "risk_type": risk_type,
            "timestamp": timestamp.isoformat(),
            "severity": severity,
            "anomaly_flag": False,
            "record_id": str(record_id)
        }
    
    async def sync_alpha_vantage_data(self, limit_per_batch: int = 5000) -> Dict[str, int]:
        """Sync Alpha Vantage data from PostgreSQL to ChromaDB."""
        stats = {"processed": 0, "chunks_created": 0, "errors": 0}
        
        try:
            # Get sync state
            sync_state = await self.get_sync_state("alpha_vantage_data")
            
            # For data ingestion, process ALL data or from last sync point
            cutoff_time = sync_state.last_synced_at
            
            if cutoff_time:
                base_query = """
                SELECT id, ticker, endpoint, timestamp, parsed_values, raw_payload
                FROM alpha_vantage_data
                WHERE timestamp > $1
                ORDER BY timestamp ASC
                LIMIT $2
                """
                records = await self.postgres.async_execute_query(base_query, (cutoff_time, limit_per_batch))
            else:
                base_query = """
                SELECT id, ticker, endpoint, timestamp, parsed_values, raw_payload
                FROM alpha_vantage_data
                ORDER BY timestamp ASC
                LIMIT $1
                """
                records = await self.postgres.async_execute_query(base_query, (limit_per_batch,))
            
            if not records:
                logger.info("No new Alpha Vantage data to sync")
                return stats
            
            logger.info(f"Ingesting {len(records)} Alpha Vantage records to ChromaDB")
            
            # Process records in batches
            batch_chunks = []
            latest_timestamp = cutoff_time
            
            for record in records:
                try:
                    # Convert record to chunks
                    parsed_data = record['parsed_values'] or {}
                    if isinstance(parsed_data, str):
                        parsed_data = json.loads(parsed_data)
                    
                    text_chunks = self.convert_to_readable_text(
                        record['endpoint'], 
                        parsed_data, 
                        record['ticker'], 
                        record['timestamp']
                    )
                    
                    # Create DataChunk objects
                    for i, text in enumerate(text_chunks):
                        chunk_id = self.generate_chunk_id(
                            "alpha_vantage", 
                            record['id'], 
                            i
                        )
                        
                        metadata = self.create_chunk_metadata(
                            record['endpoint'],
                            record['ticker'],
                            record['timestamp'],
                            record['id']
                        )
                        
                        batch_chunks.append(DataChunk(
                            text=text,
                            metadata=metadata,
                            chunk_id=chunk_id
                        ))
                    
                    stats["processed"] += 1
                    
                    # Track latest timestamp for sync state
                    record_timestamp = make_aware(record['timestamp'])
                    if latest_timestamp:
                        latest_timestamp = make_aware(latest_timestamp)
                    
                    if record_timestamp:
                        if latest_timestamp:
                            latest_timestamp = max(latest_timestamp, record_timestamp)
                        else:
                            latest_timestamp = record_timestamp
                    
                    # Process batch when it's full
                    if len(batch_chunks) >= self.batch_size:
                        await self.process_chunk_batch(batch_chunks)
                        stats["chunks_created"] += len(batch_chunks)
                        batch_chunks = []
                        
                except Exception as e:
                    logger.error(f"Error processing record {record['id']}: {e}")
                    stats["errors"] += 1
                    continue
            
            # Process remaining chunks
            if batch_chunks:
                await self.process_chunk_batch(batch_chunks)
                stats["chunks_created"] += len(batch_chunks)
            
            # Update sync state
            sync_state.last_synced_at = latest_timestamp
            sync_state.records_synced = stats["processed"]
            await self.update_sync_state(sync_state)
            
            logger.info(f"Alpha Vantage ingestion complete: {stats}")
            
        except Exception as e:
            logger.error(f"Failed to sync Alpha Vantage data: {e}")
            stats["errors"] += 1
            
        return stats
    
    async def process_chunk_batch(self, chunks: List[DataChunk]):
        """Process a batch of chunks - embed and store in ChromaDB."""
        try:
            if not chunks:
                return
            
            # Extract data for embedding
            texts = [chunk.text for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks] 
            ids = [chunk.chunk_id for chunk in chunks]
            
            # Generate embeddings
            embeddings = None
            if self.embedder:
                try:
                    embeddings = await self.embedder.embed_texts(texts)
                except Exception as e:
                    logger.warning(f"Failed to generate embeddings: {e}")
            
            # Upsert to ChromaDB
            success = vector_store.upsert_documents(
                documents=texts,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            
            if success:
                logger.debug(f"Successfully upserted {len(chunks)} chunks to ChromaDB")
            else:
                logger.error(f"Failed to upsert {len(chunks)} chunks to ChromaDB")
                
        except Exception as e:
            logger.error(f"Failed to process chunk batch: {e}")
            raise
    
    async def run_full_sync(self) -> Dict[str, Any]:
        """Run full incremental ingestion for all data sources."""
        total_stats = {
            "alpha_vantage": {"processed": 0, "chunks_created": 0, "errors": 0},
            "total_time": 0,
            "success": True
        }
        
        start_time = datetime.now()
        
        try:
            logger.info("Starting PostgreSQL → ChromaDB Data Ingestion Pipeline")
            
            # Sync Alpha Vantage data
            alpha_stats = await self.sync_alpha_vantage_data()
            total_stats["alpha_vantage"] = alpha_stats
            
            # TODO: Add other data source ingestion here
            # - News sentiment data ingestion
            # - Anomaly data ingestion
            # - Options data ingestion
            # - Regulatory filings ingestion
            
            end_time = datetime.now()
            total_stats["total_time"] = (end_time - start_time).total_seconds()
            
            total_chunks = sum(s.get('chunks_created', 0) for s in total_stats.values() if isinstance(s, dict))
            total_processed = sum(s.get('processed', 0) for s in total_stats.values() if isinstance(s, dict))
            total_errors = sum(s.get('errors', 0) for s in total_stats.values() if isinstance(s, dict))
            
            logger.info(f"✅ Ingestion completed in {total_stats['total_time']:.1f} seconds")
            logger.info(f"📊 Records processed: {total_processed}")
            logger.info(f"📁 Chunks created: {total_chunks}")
            logger.info(f"❌ Errors: {total_errors}")
            
        except Exception as e:
            logger.error(f"❌ Ingestion pipeline failed: {e}")
            total_stats["success"] = False
            total_stats["error"] = str(e)
            
        return total_stats

# Global pipeline instance
postgres_to_vectordb_pipeline = PostgresToVectorDBPipeline()
