#!/usr/bin/env python3
"""
Shared utilities for the data collection pipeline
HTTP requests, database operations, logging, and common helpers
"""

import asyncio
import logging
import time
import random
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta, timedelta
import asyncpg
import aiohttp
from dataclasses import asdict

from .config import config

# Setup logging
def setup_logging(log_type: str = 'pipeline', log_level: Optional[str] = None) -> str:
    """Setup logging with both file and console handlers"""
    log_level = log_level or config.log_level
    log_file_path = config.get_log_file_path(log_type)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(getattr(logging, log_level))
    file_formatter = logging.Formatter(config.log_format)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    console_formatter = logging.Formatter(config.log_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return log_file_path

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Async database operations manager"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self._connection_string = config.database.url
    
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self._connection_string,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("Database pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")
    
    async def execute_query(self, query: str, params: Tuple = ()) -> List[Dict]:
        """Execute a SELECT query and return results"""
        if not self.pool:
            await self.initialize()
        
        async with self.pool.acquire() as conn:
            try:
                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                logger.error(f"Query: {query}")
                logger.error(f"Params: {params}")
                raise
    
    async def execute_insert(self, query: str, params: Tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        if not self.pool:
            await self.initialize()
        
        async with self.pool.acquire() as conn:
            try:
                result = await conn.execute(query, *params)
                # Extract number from result string like "INSERT 0 5"
                return int(result.split()[-1]) if result else 0
            except Exception as e:
                logger.error(f"Insert execution failed: {e}")
                logger.error(f"Query: {query}")
                logger.error(f"Params: {params}")
                raise
    
    async def upsert_batch(self, table: str, rows: List[Dict], conflict_columns: List[str]) -> int:
        """Bulk upsert using temp table approach"""
        if not rows:
            return 0
        
        if not self.pool:
            await self.initialize()
        
        # Create temp table name
        temp_table = f"temp_{table}_{int(time.time())}"
        
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                try:
                    # Get table schema
                    schema_query = """
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = $1 AND table_schema = 'public'
                    ORDER BY ordinal_position;
                    """
                    schema = await conn.fetch(schema_query, table)
                    
                    if not schema:
                        raise ValueError(f"Table {table} not found")
                    
                    # Filter rows to only include existing columns
                    valid_columns = [col['column_name'] for col in schema]
                    filtered_rows = []
                    for row in rows:
                        filtered_row = {k: v for k, v in row.items() if k in valid_columns}
                        filtered_rows.append(filtered_row)
                    
                    if not filtered_rows or not filtered_rows[0]:
                        logger.warning(f"No valid data for table {table}")
                        return 0
                    
                    # Create temp table
                    columns = list(filtered_rows[0].keys())
                    create_temp_query = f"""
                    CREATE TEMP TABLE {temp_table} AS 
                    SELECT {', '.join(columns)} FROM {table} WHERE FALSE;
                    """
                    await conn.execute(create_temp_query)
                    
                    # Insert data into temp table using COPY
                    await conn.copy_records_to_table(
                        temp_table,
                        records=[tuple(row[col] for col in columns) for row in filtered_rows],
                        columns=columns
                    )
                    
                    # Create upsert query
                    set_clause = ', '.join([
                        f"{col} = EXCLUDED.{col}" 
                        for col in columns 
                        if col not in conflict_columns
                    ])
                    
                    conflict_clause = f"({', '.join(conflict_columns)})"
                    
                    upsert_query = f"""
                    INSERT INTO {table} ({', '.join(columns)})
                    SELECT {', '.join(columns)} FROM {temp_table}
                    ON CONFLICT {conflict_clause} 
                    DO UPDATE SET {set_clause};
                    """
                    
                    result = await conn.execute(upsert_query)
                    affected_rows = int(result.split()[-1]) if result else 0
                    
                    logger.info(f"Upserted {affected_rows} rows into {table}")
                    return affected_rows
                    
                except Exception as e:
                    logger.error(f"Batch upsert failed for table {table}: {e}")
                    raise

class HTTPClient:
    """Async HTTP client with retry logic and rate limiting"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self._rate_limiters: Dict[str, float] = {}
    
    async def initialize(self):
        """Initialize HTTP session"""
        connector = aiohttp.TCPConnector(limit=config.max_concurrent_requests)
        timeout = aiohttp.ClientTimeout(total=config.request_timeout)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        logger.info("HTTP client initialized")
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            logger.info("HTTP client closed")
    
    async def request_with_retries(
        self,
        url: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        method: str = 'GET',
        data: Optional[Dict] = None,
        provider: str = 'generic',
        max_attempts: Optional[int] = None,
        backoff: Optional[float] = None,
        jitter: float = 0.1
    ) -> Optional[Dict]:
        """Make HTTP request with exponential backoff and retry logic"""
        
        if not self.session:
            await self.initialize()
        
        max_attempts = max_attempts or config.retry_attempts
        backoff = backoff or config.backoff_factor
        
        # Check if provider is rate limited
        if not error_handler.can_use_provider(provider):
            logger.warning(f"Provider {provider} is rate limited, skipping request")
            return None
        
        # Rate limiting per provider
        await self._rate_limit(provider)
        
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=data if method in ['POST', 'PUT'] else None
                ) as response:
                    
                    # Use error handler to check response
                    try:
                        await error_handler.handle_api_response(response, provider)
                    except RateLimitExceeded as e:
                        logger.error(f"Rate limit exceeded for {provider}: {e}")
                        return None  # Skip this provider
                    except APIError as e:
                        logger.error(f"API error for {provider}: {e}")
                        if attempt < max_attempts - 1:
                            sleep_time = (backoff ** attempt) + (random.random() * jitter)
                            logger.info(f"Retrying in {sleep_time:.2f}s...")
                            await asyncio.sleep(sleep_time)
                            continue
                        else:
                            return None
                    
                    # Success case
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        
                        if 'application/json' in content_type:
                            return await response.json()
                        else:
                            text_data = await response.text()
                            return {'data': text_data, 'content_type': content_type}
            
            except RateLimitExceeded:
                logger.error(f"Rate limit exceeded for {provider}, skipping")
                return None
            except APIError as e:
                logger.error(f"API error: {e}")
                return None
            except Exception as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    sleep_time = (backoff ** attempt) + (random.random() * jitter)
                    logger.warning(f"Request failed (attempt {attempt + 1}/{max_attempts}): {e}")
                    logger.info(f"Retrying in {sleep_time:.2f}s...")
                    await asyncio.sleep(sleep_time)
                else:
                    logger.error(f"Request failed after {max_attempts} attempts: {e}")
                    return None
        
        logger.error(f"Request to {url} failed after {max_attempts} attempts")
        return None
    
    async def _rate_limit(self, provider: str):
        """Simple rate limiting per provider"""
        now = time.time()
        last_request = self._rate_limiters.get(provider, 0)
        
        # Minimum time between requests (per provider)
        min_interval = {
            'alpha_vantage': 12,  # 5 calls per minute
            'perplexity': 60,     # 1 call per minute
            'generic': 1          # 1 call per second
        }.get(provider, 1)
        
        time_since_last = now - last_request
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            await asyncio.sleep(sleep_time)
        
        self._rate_limiters[provider] = time.time()

# Error handling and rate limit management
class RateLimitExceeded(Exception):
    """Custom exception for rate limit exceeded"""
    def __init__(self, provider: str, retry_after: Optional[int] = None):
        self.provider = provider
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded for {provider}")

class APIError(Exception):
    """Custom exception for API errors"""
    def __init__(self, provider: str, status_code: int, message: str):
        self.provider = provider
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error for {provider}: {status_code} - {message}")

class ErrorHandler:
    """Centralized error handling for all providers"""
    
    def __init__(self):
        self.provider_errors = {}
        self.rate_limit_status = {}
        
    def is_rate_limited(self, provider: str) -> bool:
        """Check if provider is currently rate limited"""
        if provider not in self.rate_limit_status:
            return False
        
        rate_limit_info = self.rate_limit_status[provider]
        if datetime.now(timezone.utc) > rate_limit_info['reset_time']:
            # Rate limit has expired
            del self.rate_limit_status[provider]
            return False
        
        return True
    
    def set_rate_limited(self, provider: str, retry_after: int = 3600):
        """Mark provider as rate limited"""
        reset_time = datetime.now(timezone.utc) + timedelta(seconds=retry_after)
        self.rate_limit_status[provider] = {
            'reset_time': reset_time,
            'retry_after': retry_after
        }
        logger.warning(f"Provider {provider} rate limited until {reset_time}")
    
    def can_use_provider(self, provider: str) -> bool:
        """Check if provider can be used (not rate limited)"""
        return not self.is_rate_limited(provider)
    
    async def handle_api_response(self, response, provider: str):
        """Handle API response and check for rate limiting"""
        if response.status == 429:  # Rate limited
            retry_after = int(response.headers.get('Retry-After', 3600))
            self.set_rate_limited(provider, retry_after)
            raise RateLimitExceeded(provider, retry_after)
        
        elif response.status == 403:  # Forbidden - might be quota exceeded
            # Check if it's quota exceeded
            response_text = await response.text()
            if 'quota' in response_text.lower() or 'limit' in response_text.lower():
                self.set_rate_limited(provider, 3600)  # 1 hour default
                raise RateLimitExceeded(provider, 3600)
            else:
                raise APIError(provider, response.status, "Forbidden")
        
        elif response.status >= 400:
            response_text = await response.text()
            raise APIError(provider, response.status, response_text[:200])
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors"""
        return {
            'provider_errors': self.provider_errors,
            'rate_limited_providers': list(self.rate_limit_status.keys())
        }

class IngestionLogger:
    """Logs ingestion activities to database"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_session(self, session_id: str, metadata: Optional[Dict] = None) -> str:
        """Create a new ingestion session"""
        try:
            if not self.db_manager.pool:
                await self.db_manager.initialize()
            
            query = """
                INSERT INTO ingestion_sessions 
                (session_id, status, start_time, metadata)
                VALUES ($1, $2, $3, $4)
                RETURNING session_id
            """
            if self.db_manager.pool:
                async with self.db_manager.pool.acquire() as conn:
                    result = await conn.fetchval(
                        query, session_id, "RUNNING", datetime.now(timezone.utc), 
                        json.dumps(metadata or {})
                    )
                    logger.info(f"Created ingestion session: {result}")
                    return result
            return session_id
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return session_id
    
    async def update_session(self, session_id: str, status: str, total_records: int = 0, 
                           total_api_calls: int = 0):
        """Update ingestion session with results"""
        try:
            if not self.db_manager.pool:
                await self.db_manager.initialize()
            
            query = """
                UPDATE ingestion_sessions 
                SET status = $2, end_time = $3, total_records = $4, 
                    total_api_calls = $5
                WHERE session_id = $1
            """
            if self.db_manager.pool:
                async with self.db_manager.pool.acquire() as conn:
                    await conn.execute(
                        query, session_id, status, datetime.now(timezone.utc),
                        total_records, total_api_calls
                    )
                    logger.info(f"Updated session {session_id}: {status}")
        except Exception as e:
            logger.error(f"Failed to update session: {e}")
    
    async def log_api_call(self, session_id: str, provider: str, endpoint: str, 
                          status: str, records_count: int = 0, error_message: Optional[str] = None):
        """Log API call to alpha_ingestion_logs table"""
        try:
            if not self.db_manager.pool:
                await self.db_manager.initialize()
            
            query = """
                INSERT INTO alpha_ingestion_logs 
                (session_id, api_provider, endpoint, status, records_ingested, error_message, timestamp, duration)
                VALUES ($1, $2, $3, $4, $5, $6, $7, 0)
            """
            if self.db_manager.pool:
                async with self.db_manager.pool.acquire() as conn:
                    await conn.execute(
                        query, session_id, provider, endpoint, status, records_count, 
                        error_message, datetime.now(timezone.utc)
                    )
        except Exception as e:
            logger.error(f"Failed to log API call: {e}")
    
    async def log_ingestion(self, session_id: str, provider: str, endpoint: str, 
                          status: str, records_count: int = 0, error_message: Optional[str] = None,
                          duration: float = 0.0):
        """Log ingestion activity - alias for log_api_call with duration support"""
        try:
            if not self.db_manager.pool:
                await self.db_manager.initialize()
            
            query = """
                INSERT INTO alpha_ingestion_logs 
                (session_id, api_provider, endpoint, status, records_ingested, error_message, timestamp, duration)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """
            if self.db_manager.pool:
                async with self.db_manager.pool.acquire() as conn:
                    await conn.execute(
                        query, session_id, provider, endpoint, str(status), int(records_count), 
                        error_message, datetime.now(timezone.utc), float(duration)
                    )
        except Exception as e:
            logger.error(f"Failed to log ingestion: {e}")

# Global instances
db_manager = DatabaseManager()
http_client = HTTPClient()
ingestion_logger = IngestionLogger(db_manager)
error_handler = ErrorHandler()

def now_epoch() -> int:
    """Get current epoch timestamp"""
    return int(time.time())

def generate_session_id(prefix: str = "pipeline") -> str:
    """Generate unique session ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}"

def normalize_ticker(ticker: str) -> str:
    """Normalize ticker symbol"""
    return ticker.upper().strip()

def hash_content(content: str) -> str:
    """Generate hash for content deduplication"""
    return hashlib.md5(content.encode()).hexdigest()

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

class ResilientCollector:
    """Base class for all data collectors with comprehensive error handling"""
    
    def __init__(self, name: str):
        self.name = name
        self.session_id: Optional[str] = None
        self.api_calls_made = 0
        self.max_api_calls = 10  # Default budget
        self.errors = []
        self.fallback_providers = []
        
    def set_session(self, session_id: str):
        """Set the current ingestion session"""
        self.session_id = session_id
        self.api_calls_made = 0
        self.errors = []
    
    def set_api_budget(self, budget: int):
        """Set API call budget for this collector"""
        self.max_api_calls = budget
    
    def add_fallback_provider(self, provider_name: str):
        """Add fallback provider for when primary fails"""
        self.fallback_providers.append(provider_name)
    
    def can_make_api_call(self) -> bool:
        """Check if we can make another API call within budget"""
        return self.api_calls_made < self.max_api_calls
    
    async def safe_api_call(self, provider: str, url: str, headers: Optional[Dict] = None, 
                           params: Optional[Dict] = None, method: str = 'GET') -> Optional[Dict]:
        """Make a safe API call with comprehensive error handling"""
        
        if not self.session_id:
            logger.error(f"{self.name}: No session ID set, cannot make API call")
            return None
        
        if not self.can_make_api_call():
            logger.warning(f"{self.name}: API budget exceeded ({self.api_calls_made}/{self.max_api_calls})")
            return None
        
        if not error_handler.can_use_provider(provider):
            logger.warning(f"{self.name}: Provider {provider} is rate limited, trying fallback")
            return await self._try_fallback_providers(url, headers, params, method)
        
        try:
            self.api_calls_made += 1
            
            # Log API call attempt
            await ingestion_logger.log_api_call(
                self.session_id, provider, url, "ATTEMPTING", 0
            )
            
            result = await http_client.request_with_retries(
                url=url, headers=headers, params=params, method=method, provider=provider
            )
            
            if result is not None:
                # Success
                record_count = self._count_records(result)
                await ingestion_logger.log_api_call(
                    self.session_id, provider, url, "SUCCESS", record_count
                )
                logger.info(f"{self.name}: {provider} API call successful, {record_count} records")
                return result
            else:
                # Failed or rate limited
                await ingestion_logger.log_api_call(
                    self.session_id, provider, url, "FAILED", 0, "No data returned"
                )
                logger.warning(f"{self.name}: {provider} API call returned no data")
                return await self._try_fallback_providers(url, headers, params, method)
                
        except Exception as e:
            error_msg = str(e)
            self.errors.append({
                'provider': provider,
                'url': url,
                'error': error_msg,
                'timestamp': datetime.now(timezone.utc)
            })
            
            await ingestion_logger.log_api_call(
                self.session_id, provider, url, "ERROR", 0, error_msg
            )
            
            logger.error(f"{self.name}: {provider} API call failed: {error_msg}")
            return await self._try_fallback_providers(url, headers, params, method)
    
    async def _try_fallback_providers(self, url: str, headers: Optional[Dict], params: Optional[Dict], method: str) -> Optional[Dict]:
        """Try fallback providers when primary fails"""
        for fallback_provider in self.fallback_providers:
            if not self.can_make_api_call():
                break
                
            if error_handler.can_use_provider(fallback_provider):
                logger.info(f"{self.name}: Trying fallback provider {fallback_provider}")
                # Modify URL/headers for fallback provider if needed
                fallback_result = await self.safe_api_call(fallback_provider, url, headers, params, method)
                if fallback_result:
                    return fallback_result
        
        return None
    
    def _count_records(self, response: Dict) -> int:
        """Count records in API response - override in subclasses"""
        if isinstance(response, dict):
            if 'data' in response and isinstance(response['data'], list):
                return len(response['data'])
            elif isinstance(response, list):
                return len(response)
        return 1 if response else 0
    
    def get_collection_summary(self) -> Dict[str, Any]:
        """Get summary of collection results"""
        return {
            'collector_name': self.name,
            'api_calls_made': self.api_calls_made,
            'api_budget': self.max_api_calls,
            'errors': len(self.errors),
            'error_details': self.errors[-5:] if self.errors else []  # Last 5 errors
        }
