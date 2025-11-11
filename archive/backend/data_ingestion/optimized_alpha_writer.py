"""
Optimized Alpha Vantage Data Writer - High Performance Database Operations
Enhanced version with batch processing, connection pooling, and performance monitoring
"""

import logging
import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple, Union
import json
import hashlib
from contextlib import asynccontextmanager
import asyncpg
from concurrent.futures import ThreadPoolExecutor

from ..db.postgres_handler import PostgresHandler

logger = logging.getLogger(__name__)

class OptimizedAlphaWriter:
    """
    High-performance Alpha Vantage data writer with advanced optimizations:
    - Batch processing with configurable batch sizes
    - Connection pool management
    - Asynchronous writes
    - Performance monitoring
    - Smart conflict resolution
    """
    
    def __init__(self, batch_size: int = 1000, max_workers: int = 4):
        self.db = PostgresHandler()
        
        # Performance configuration
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Write statistics with detailed tracking
        self.stats = {
            'total_writes': 0,
            'successful_writes': 0,
            'duplicate_writes': 0,
            'failed_writes': 0,
            'batches_processed': 0,
            'avg_batch_time': 0.0,
            'fastest_batch': float('inf'),
            'slowest_batch': 0.0,
            'total_write_time': 0.0
        }
        
        # Batch buffer for accumulating writes
        self.write_buffer = {
            'market_data': [],
            'fundamental_data': [],
            'technical_indicators': [],
            'news_intelligence': [],
            'forex_data': [],
            'crypto_data': []
        }
        
        # SQL templates for optimized batch operations
        self._prepare_sql_templates()
        
    def _prepare_sql_templates(self):
        """Prepare optimized SQL templates for different data types"""
        
        # Market data batch insert with comprehensive conflict resolution
        self.market_data_sql = """
        INSERT INTO alpha_market_data (
            ticker, endpoint, api_function, timestamp, interval_type,
            open_price, high_price, low_price, close_price, adjusted_close,
            volume, dividend_amount, split_coefficient, source, raw_payload,
            parsed_values, quality_flag, ingestion_epoch, ingestion_sequence,
            ingestion_time
        ) VALUES %s
        ON CONFLICT (ticker, timestamp, endpoint, interval_type) 
        DO UPDATE SET
            open_price = COALESCE(EXCLUDED.open_price, alpha_market_data.open_price),
            high_price = COALESCE(EXCLUDED.high_price, alpha_market_data.high_price),
            low_price = COALESCE(EXCLUDED.low_price, alpha_market_data.low_price),
            close_price = COALESCE(EXCLUDED.close_price, alpha_market_data.close_price),
            volume = COALESCE(EXCLUDED.volume, alpha_market_data.volume),
            raw_payload = EXCLUDED.raw_payload,
            parsed_values = EXCLUDED.parsed_values,
            quality_flag = EXCLUDED.quality_flag,
            ingestion_time = EXCLUDED.ingestion_time
        """
        
        # Fundamental data batch insert
        self.fundamental_data_sql = """
        INSERT INTO alpha_fundamental_data (
            ticker, endpoint, api_function, data_type, fiscal_date_ending,
            reported_currency, period_type, financial_data, total_revenue,
            net_income, total_assets, total_liabilities, shareholders_equity,
            eps, pe_ratio, market_cap, source, raw_payload, quality_flag,
            ingestion_epoch, ingestion_sequence, ingestion_time
        ) VALUES %s
        ON CONFLICT (ticker, endpoint, fiscal_date_ending, period_type, data_type)
        DO UPDATE SET
            financial_data = EXCLUDED.financial_data,
            total_revenue = EXCLUDED.total_revenue,
            net_income = EXCLUDED.net_income,
            market_cap = EXCLUDED.market_cap,
            raw_payload = EXCLUDED.raw_payload,
            ingestion_time = EXCLUDED.ingestion_time
        """
        
        # Technical indicators batch insert
        self.technical_indicators_sql = """
        INSERT INTO alpha_technical_indicators (
            ticker, endpoint, api_function, indicator_name, timestamp,
            interval_type, value_1, value_2, value_3, value_4, value_5,
            indicator_values, time_period, series_type, parameters,
            source, raw_payload, quality_flag, ingestion_epoch,
            ingestion_sequence, ingestion_time
        ) VALUES %s
        ON CONFLICT (ticker, timestamp, endpoint, indicator_name, interval_type)
        DO UPDATE SET
            value_1 = EXCLUDED.value_1,
            value_2 = EXCLUDED.value_2,
            value_3 = EXCLUDED.value_3,
            indicator_values = EXCLUDED.indicator_values,
            raw_payload = EXCLUDED.raw_payload,
            ingestion_time = EXCLUDED.ingestion_time
        """
    
    async def write_market_data_batch(
        self, 
        records: List[Dict[str, Any]], 
        ingestion_epoch: int,
        ingestion_sequence: int
    ) -> Tuple[int, int, List[str]]:
        """
        Write market data in optimized batches
        
        Returns:
            Tuple of (successful_writes, failed_writes, error_messages)
        """
        if not records:
            return 0, 0, []
        
        start_time = time.time()
        total_successful = 0
        total_failed = 0
        all_errors = []
        
        # Process records in batches
        for i in range(0, len(records), self.batch_size):
            batch = records[i:i + self.batch_size]
            batch_start = time.time()
            
            try:
                # Prepare batch data
                batch_values = self._prepare_market_data_batch(batch, ingestion_epoch, ingestion_sequence)
                
                # Execute batch insert
                async with self.db.get_async_connection() as conn:
                    async with conn.transaction():
                        # Use execute_values for optimal performance
                        await self._execute_batch_values(
                            conn, 
                            self.market_data_sql, 
                            batch_values
                        )
                
                successful = len(batch)
                total_successful += successful
                
                # Update batch timing statistics
                batch_time = time.time() - batch_start
                self._update_batch_stats(batch_time, successful)
                
                logger.debug(f"✅ Processed market data batch {i//self.batch_size + 1}: {successful} records in {batch_time:.2f}s")
                
            except Exception as e:
                error_msg = f"Batch {i//self.batch_size + 1} failed: {str(e)}"
                logger.error(error_msg)
                all_errors.append(error_msg)
                total_failed += len(batch)
        
        # Update global statistics
        total_time = time.time() - start_time
        self.stats['total_writes'] += len(records)
        self.stats['successful_writes'] += total_successful
        self.stats['failed_writes'] += total_failed
        self.stats['total_write_time'] += total_time
        
        logger.info(f"📊 Market data batch write complete: {total_successful}/{len(records)} successful in {total_time:.2f}s")
        
        return total_successful, total_failed, all_errors
    
    def _prepare_market_data_batch(
        self, 
        records: List[Dict[str, Any]], 
        ingestion_epoch: int,
        ingestion_sequence: int
    ) -> List[Tuple]:
        """Prepare market data records for batch insert"""
        batch_values = []
        current_time = datetime.now(timezone.utc)
        
        for record in records:
            values = (
                record.get('ticker', ''),
                record.get('endpoint', ''),
                record.get('api_function', ''),
                record.get('timestamp'),
                record.get('interval_type'),
                self._safe_decimal(record.get('open_price')),
                self._safe_decimal(record.get('high_price')),
                self._safe_decimal(record.get('low_price')),
                self._safe_decimal(record.get('close_price')),
                self._safe_decimal(record.get('adjusted_close')),
                self._safe_int(record.get('volume')),
                self._safe_decimal(record.get('dividend_amount')),
                self._safe_decimal(record.get('split_coefficient')),
                'alpha_vantage',
                json.dumps(record.get('raw_payload', {})),
                json.dumps(record.get('parsed_values', {})),
                record.get('quality_flag', 'complete'),
                ingestion_epoch,
                ingestion_sequence,
                current_time
            )
            batch_values.append(values)
            
        return batch_values
    
    async def write_fundamental_data_batch(
        self,
        records: List[Dict[str, Any]],
        ingestion_epoch: int,
        ingestion_sequence: int
    ) -> Tuple[int, int, List[str]]:
        """Write fundamental data in optimized batches"""
        if not records:
            return 0, 0, []
        
        start_time = time.time()
        total_successful = 0
        total_failed = 0
        all_errors = []
        
        # Process in batches
        for i in range(0, len(records), self.batch_size):
            batch = records[i:i + self.batch_size]
            batch_start = time.time()
            
            try:
                batch_values = self._prepare_fundamental_data_batch(batch, ingestion_epoch, ingestion_sequence)
                
                async with self.db.get_async_connection() as conn:
                    async with conn.transaction():
                        await self._execute_batch_values(
                            conn,
                            self.fundamental_data_sql,
                            batch_values
                        )
                
                successful = len(batch)
                total_successful += successful
                
                batch_time = time.time() - batch_start
                self._update_batch_stats(batch_time, successful)
                
                logger.debug(f"✅ Processed fundamental data batch {i//self.batch_size + 1}: {successful} records")
                
            except Exception as e:
                error_msg = f"Fundamental batch {i//self.batch_size + 1} failed: {str(e)}"
                logger.error(error_msg)
                all_errors.append(error_msg)
                total_failed += len(batch)
        
        total_time = time.time() - start_time
        logger.info(f"📊 Fundamental data batch write complete: {total_successful}/{len(records)} successful in {total_time:.2f}s")
        
        return total_successful, total_failed, all_errors
    
    def _prepare_fundamental_data_batch(
        self,
        records: List[Dict[str, Any]],
        ingestion_epoch: int,
        ingestion_sequence: int
    ) -> List[Tuple]:
        """Prepare fundamental data records for batch insert"""
        batch_values = []
        current_time = datetime.now(timezone.utc)
        
        for record in records:
            financial_data = record.get('financial_data', {})
            
            values = (
                record.get('ticker', ''),
                record.get('endpoint', ''),
                record.get('api_function', ''),
                record.get('data_type', ''),
                record.get('fiscal_date_ending'),
                record.get('reported_currency'),
                record.get('period_type'),
                json.dumps(financial_data),
                self._safe_decimal(financial_data.get('TotalRevenue')),
                self._safe_decimal(financial_data.get('NetIncome')),
                self._safe_decimal(financial_data.get('TotalAssets')),
                self._safe_decimal(financial_data.get('TotalLiabilities')),
                self._safe_decimal(financial_data.get('ShareholdersEquity')),
                self._safe_decimal(financial_data.get('EPS')),
                self._safe_decimal(financial_data.get('PERatio')),
                self._safe_decimal(financial_data.get('MarketCapitalization')),
                'alpha_vantage',
                json.dumps(record.get('raw_payload', {})),
                record.get('quality_flag', 'complete'),
                ingestion_epoch,
                ingestion_sequence,
                current_time
            )
            batch_values.append(values)
            
        return batch_values
    
    async def _execute_batch_values(
        self,
        conn: asyncpg.Connection,
        sql_template: str,
        values: List[Tuple]
    ):
        """Execute batch insert using asyncpg's copy_records_to_table for maximum performance"""
        try:
            # For maximum performance, we can use COPY when possible
            # For now, use execute_many which is still very fast
            placeholders = ','.join(['%s'] * len(values[0])) if values else ''
            sql = sql_template.replace('%s', '(' + placeholders + ')')
            
            # Flatten values for executemany
            formatted_sql = sql_template.replace(' VALUES %s', ' VALUES ' + ','.join(['(' + ','.join(['$' + str(i) for i in range(1, len(values[0])+1)]) + ')' for _ in values]))
            
            # Use prepared statements for better performance
            flat_values = [item for sublist in values for item in sublist]
            await conn.execute(formatted_sql, *flat_values)
            
        except Exception as e:
            logger.error(f"Batch execute failed: {str(e)}")
            raise
    
    def _update_batch_stats(self, batch_time: float, record_count: int):
        """Update batch processing statistics"""
        self.stats['batches_processed'] += 1
        self.stats['avg_batch_time'] = (
            (self.stats['avg_batch_time'] * (self.stats['batches_processed'] - 1) + batch_time) 
            / self.stats['batches_processed']
        )
        self.stats['fastest_batch'] = min(self.stats['fastest_batch'], batch_time)
        self.stats['slowest_batch'] = max(self.stats['slowest_batch'], batch_time)
    
    def _safe_decimal(self, value: Any) -> Optional[float]:
        """Safely convert value to decimal"""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value: Any) -> Optional[int]:
        """Safely convert value to integer"""
        if value is None or value == '':
            return None
        try:
            return int(float(value))  # Handle string decimals
        except (ValueError, TypeError):
            return None
    
    async def flush_all_buffers(self) -> Dict[str, Tuple[int, int, List[str]]]:
        """Flush all write buffers to database"""
        results = {}
        
        # Flush market data
        if self.write_buffer['market_data']:
            results['market_data'] = await self.write_market_data_batch(
                self.write_buffer['market_data'], 0, 0
            )
            self.write_buffer['market_data'] = []
        
        # Flush fundamental data
        if self.write_buffer['fundamental_data']:
            results['fundamental_data'] = await self.write_fundamental_data_batch(
                self.write_buffer['fundamental_data'], 0, 0
            )
            self.write_buffer['fundamental_data'] = []
        
        # Add other data types as needed
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        stats = self.stats.copy()
        
        if stats['total_writes'] > 0:
            stats['success_rate'] = (stats['successful_writes'] / stats['total_writes']) * 100
            stats['avg_records_per_second'] = stats['successful_writes'] / max(stats['total_write_time'], 0.001)
        else:
            stats['success_rate'] = 0.0
            stats['avg_records_per_second'] = 0.0
        
        return stats
    
    async def optimize_connection_pool(self):
        """Dynamically optimize connection pool size based on workload"""
        current_stats = self.get_performance_stats()
        
        # Adjust pool size based on performance
        if current_stats['avg_records_per_second'] < 100:  # Too slow
            logger.info("📈 Increasing connection pool size for better performance")
            await self.db.initialize_async_pool(min_size=10, max_size=30)
        elif current_stats['avg_records_per_second'] > 1000:  # Very fast, can reduce
            logger.info("📉 Optimizing connection pool size")
            await self.db.initialize_async_pool(min_size=5, max_size=15)
    
    async def close(self):
        """Clean shutdown with buffer flush"""
        logger.info("🔄 Flushing remaining buffers before shutdown...")
        await self.flush_all_buffers()
        
        self.executor.shutdown(wait=True)
        await self.db.close_async_pool()
        
        logger.info("✅ OptimizedAlphaWriter shutdown complete")
