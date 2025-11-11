"""
PostgreSQL database handler for the uRISK system.
Provides connection management and query execution utilities.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from contextlib import asynccontextmanager
import asyncpg
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool

from ..config.settings import settings

logger = logging.getLogger(__name__)

class PostgresHandler:
    """Handles PostgreSQL database connections and operations."""
    
    def __init__(self):
        self.pool: Optional[ThreadedConnectionPool] = None
        self.async_pool: Optional[asyncpg.Pool] = None
        
    def initialize_sync_pool(self, min_conn: int = 1, max_conn: int = 10):
        """Initialize synchronous connection pool."""
        try:
            self.pool = ThreadedConnectionPool(
                min_conn,
                max_conn,
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                database=settings.POSTGRES_DB,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD
            )
            logger.info("Synchronous PostgreSQL connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize sync connection pool: {e}")
            raise
    
    async def initialize_async_pool(self, min_size: int = 5, max_size: int = 20):
        """Initialize asynchronous connection pool."""
        try:
            self.async_pool = await asyncpg.create_pool(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                database=settings.POSTGRES_DB,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                min_size=min_size,
                max_size=max_size
            )
            logger.info("Asynchronous PostgreSQL connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize async connection pool: {e}")
            raise
    
    @asynccontextmanager
    async def get_async_connection(self):
        """Get async database connection from pool."""
        if not self.async_pool:
            await self.initialize_async_pool()
        
        async with self.async_pool.acquire() as connection:
            yield connection
    
    def get_sync_connection(self):
        """Get synchronous database connection from pool."""
        if not self.pool:
            self.initialize_sync_pool()
        
        return self.pool.getconn()
    
    def return_sync_connection(self, conn):
        """Return synchronous connection to pool."""
        if self.pool:
            self.pool.putconn(conn)
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query synchronously."""
        conn = None
        try:
            conn = self.get_sync_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            if conn:
                self.return_sync_connection(conn)
    
    def execute_insert(self, query: str, params: Optional[tuple] = None) -> Optional[int]:
        """Execute an INSERT query and return the inserted ID."""
        conn = None
        try:
            conn = self.get_sync_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                
                # Try to get the inserted ID if available
                if cursor.description:
                    result = cursor.fetchone()
                    return result[0] if result else None
                return None
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Insert execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            if conn:
                self.return_sync_connection(conn)
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an UPDATE/DELETE query and return affected rows count."""
        conn = None
        try:
            conn = self.get_sync_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Update execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            if conn:
                self.return_sync_connection(conn)
    
    def bulk_insert(self, table: str, columns: List[str], data: List[tuple]) -> int:
        """Execute bulk insert operation."""
        if not data:
            return 0
        
        conn = None
        try:
            conn = self.get_sync_connection()
            
            # Create the INSERT query
            placeholders = ','.join(['%s'] * len(columns))
            query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
            
            with conn.cursor() as cursor:
                cursor.executemany(query, data)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Bulk insert failed: {e}")
            logger.error(f"Table: {table}, Columns: {columns}")
            raise
        finally:
            if conn:
                self.return_sync_connection(conn)
    
    def bulk_upsert(self, table: str, columns: List[str], data: List[tuple], 
                   conflict_columns: List[str], update_columns: Optional[List[str]] = None) -> int:
        """Execute bulk upsert operation (INSERT ... ON CONFLICT ... DO UPDATE)."""
        if not data:
            return 0
        
        conn = None
        try:
            conn = self.get_sync_connection()
            
            # Default to updating all non-conflict columns
            if update_columns is None:
                update_columns = [col for col in columns if col not in conflict_columns]
            
            # Create the INSERT query with ON CONFLICT
            placeholders = ','.join(['%s'] * len(columns))
            conflict_clause = ','.join(conflict_columns)
            
            # Build UPDATE clause
            update_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in update_columns])
            
            query = f"""
                INSERT INTO {table} ({','.join(columns)}) 
                VALUES ({placeholders})
                ON CONFLICT ({conflict_clause}) 
                DO UPDATE SET {update_clause}
            """
            
            with conn.cursor() as cursor:
                cursor.executemany(query, data)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Bulk upsert failed: {e}")
            logger.error(f"Table: {table}, Columns: {columns}")
            raise
        finally:
            if conn:
                self.return_sync_connection(conn)
    
    async def async_execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query asynchronously."""
        async with self.get_async_connection() as conn:
            try:
                rows = await conn.fetch(query, *(params or ()))
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Async query execution failed: {e}")
                logger.error(f"Query: {query}")
                logger.error(f"Params: {params}")
                raise
    
    async def async_execute_insert(self, query: str, params: Optional[tuple] = None) -> Optional[int]:
        """Execute an INSERT query asynchronously."""
        async with self.get_async_connection() as conn:
            try:
                result = await conn.fetchval(query, *(params or ()))
                return result
            except Exception as e:
                logger.error(f"Async insert execution failed: {e}")
                logger.error(f"Query: {query}")
                logger.error(f"Params: {params}")
                raise
    
    async def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Async method to execute a SELECT query and return all results.
        Added for backward compatibility with preprocessing pipeline.
        """
        return await self.async_execute_query(query, params)
    
    def fetch_all_sync(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Synchronous method to execute a SELECT query and return all results.
        Added for backward compatibility.
        """
        try:
            if not self.pool:
                self.initialize_sync_pool()
            
            conn = self.pool.getconn()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)
                    results = cur.fetchall()
                    return [dict(row) for row in results]
            finally:
                self.pool.putconn(conn)
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            return []
    
    def close_pools(self):
        """Close all connection pools."""
        if self.pool:
            self.pool.closeall()
            logger.info("Synchronous connection pool closed")
        
        if self.async_pool:
            asyncio.create_task(self.async_pool.close())
            logger.info("Asynchronous connection pool closed")
    
    def health_check(self) -> bool:
        """Check database connectivity."""
        try:
            result = self.execute_query("SELECT 1 as health_check")
            return len(result) > 0 and result[0]['health_check'] == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def async_fetch_scalar(self, query: str, params: Optional[tuple] = None):
        """Execute a query and return a single scalar value asynchronously."""
        rows = await self.async_execute_query(query, params)
        if rows and len(rows) > 0:
            return list(rows[0].values())[0]
        return None

    async def close_async_pool(self):
        """Close the async connection pool."""
        if hasattr(self, "async_pool") and self.async_pool:
            await self.async_pool.close()
            logger.info("Async connection pool closed")

# Global database instance
db = PostgresHandler()

# Utility functions for common operations
def insert_market_price(ticker: str, timestamp: str, open_price: float, high: float, 
                       low: float, close: float, volume: int, source: str, 
                       bid_ask_spread: Optional[float] = None) -> Optional[int]:
    """Insert a market price record."""
    query = """
        INSERT INTO market_prices (ticker, timestamp, open, high, low, close, volume, bid_ask_spread, source)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ticker, timestamp) DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume,
            bid_ask_spread = EXCLUDED.bid_ask_spread,
            source = EXCLUDED.source
        RETURNING id
    """
    params = (ticker, timestamp, open_price, high, low, close, volume, bid_ask_spread, source)
    return db.execute_insert(query, params)

def insert_news_headline(ticker: str, headline: str, url: str, source: str, published_at: str) -> Optional[int]:
    """Insert a news headline record."""
    query = """
        INSERT INTO news_headlines (ticker, headline, url, source, published_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """
    params = (ticker, headline, url, source, published_at)
    return db.execute_insert(query, params)

def insert_sentiment(headline_id: int, sentiment_score: float, sentiment_label: str, 
                    confidence: float, model_version: str) -> Optional[int]:
    """Insert a sentiment analysis record."""
    query = """
        INSERT INTO news_sentiment (headline_id, sentiment_score, sentiment_label, confidence, model_version)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """
    params = (headline_id, sentiment_score, sentiment_label, confidence, model_version)
    return db.execute_insert(query, params)

def insert_anomaly(ticker: str, metric: str, anomaly_score: float, severity: str, 
                  explanation: str, timestamp: str) -> Optional[int]:
    """Insert an anomaly detection record."""
    query = """
        INSERT INTO anomalies (ticker, metric, anomaly_score, severity, explanation, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    params = (ticker, metric, anomaly_score, severity, explanation, timestamp)
    return db.execute_insert(query, params)

def insert_alert(ticker: str, risk_type: str, severity: str, message: str) -> Optional[int]:
    """Insert an alert record."""
    query = """
        INSERT INTO alerts (ticker, risk_type, severity, message)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """
    params = (ticker, risk_type, severity, message)
    return db.execute_insert(query, params)