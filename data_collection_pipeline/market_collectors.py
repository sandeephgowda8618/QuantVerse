#!/usr/bin/env python3
"""
Market Data Collectors
Handles OHLCV data from multiple providers with 10 call budget per provider
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
import yfinance as yf
import pandas as pd
from urllib.parse import urlencode

from .config import config, PRIORITY_TICKERS
from .utils import http_client, db_manager, ingestion_logger, normalize_ticker, chunk_list, now_epoch

logger = logging.getLogger(__name__)

class YFinanceCollector:
    """Yahoo Finance data collector - Free, bulk endpoints"""
    
    def __init__(self):
        self.provider = 'yfinance'
        self.call_count = 0
        self.max_calls = 10
    
    async def collect_market_data(self, session_id: str, tickers: List[str]) -> Dict[str, Any]:
        """Collect market data using yfinance bulk endpoints"""
        results = {'records': 0, 'calls': 0, 'errors': []}
        
        try:
            # Split tickers into chunks for batch processing
            ticker_chunks = chunk_list(tickers, 50)  # Yahoo handles ~50 tickers per call
            
            for i, chunk in enumerate(ticker_chunks[:self.max_calls]):
                if self.call_count >= self.max_calls:
                    break
                
                start_time = datetime.now()
                
                try:
                    # Use yfinance for bulk ticker data
                    ticker_string = ' '.join(chunk)
                    data = yf.download(
                        ticker_string,
                        period='5d',
                        interval='1d',
                        group_by='ticker',
                        progress=False,
                        threads=True
                    )
                    
                    # Process and normalize data
                    market_records = []
                    asset_records = []
                    
                    for ticker in chunk:
                        try:
                            ticker_data = data[ticker] if len(chunk) > 1 else data
                            
                            if ticker_data.empty:
                                continue
                            
                            # Add asset record
                            asset_records.append({
                                'ticker': normalize_ticker(ticker),
                                'name': ticker,  # Could be enhanced with company name lookup
                                'asset_type': 'stock',
                                'exchange': 'NYSE/NASDAQ',  # Default
                                'added_at': datetime.now(timezone.utc)
                            })
                            
                            # Add price records
                            for date, row in ticker_data.iterrows():
                                if not row.isna().all():
                                    market_records.append({
                                        'ticker': normalize_ticker(ticker),
                                        'timestamp': date.tz_localize('UTC') if date.tz is None else date,
                                        'open': float(row['Open']) if not pd.isna(row['Open']) else None,
                                        'high': float(row['High']) if not pd.isna(row['High']) else None,
                                        'low': float(row['Low']) if not pd.isna(row['Low']) else None,
                                        'close': float(row['Close']) if not pd.isna(row['Close']) else None,
                                        'volume': int(row['Volume']) if not pd.isna(row['Volume']) else None,
                                        'source': 'yahoo_finance'
                                    })
                        
                        except Exception as e:
                            logger.warning(f"Error processing {ticker}: {e}")
                            results['errors'].append(f"{ticker}: {str(e)}")
                    
                    # Bulk upsert to database
                    if asset_records:
                        await db_manager.upsert_batch('assets', asset_records, ['ticker'])
                    
                    if market_records:
                        await db_manager.upsert_batch('market_prices', market_records, ['ticker', 'timestamp'])
                        results['records'] += len(market_records)
                    
                    self.call_count += 1
                    results['calls'] += 1
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'bulk_download_chunk_{i}',
                        duration, 'success', len(market_records)
                    )
                    
                    logger.info(f"YFinance: Processed chunk {i+1}/{len(ticker_chunks)}, {len(market_records)} records")
                    
                except Exception as e:
                    duration = (datetime.now() - start_time).total_seconds()
                    error_msg = str(e)
                    results['errors'].append(error_msg)
                    
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'bulk_download_chunk_{i}',
                        duration, 'error', 0, error_msg
                    )
                    
                    logger.error(f"YFinance chunk {i} failed: {e}")
        
        except Exception as e:
            logger.error(f"YFinance collection failed: {e}")
            results['errors'].append(str(e))
        
        return results

class TiingoCollector:
    """Tiingo data collector - High quality financial data"""
    
    def __init__(self):
        self.provider = 'tiingo'
        self.call_count = 0
        self.max_calls = 10
        self.base_url = config.api.tiingo_base_url
        self.api_key = config.api.tiingo_api_key
    
    async def collect_market_data(self, session_id: str, tickers: List[str]) -> Dict[str, Any]:
        """Collect market data from Tiingo"""
        results = {'records': 0, 'calls': 0, 'errors': []}
        
        if not self.api_key:
            logger.error("Tiingo API key not configured")
            return results
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {self.api_key}'
        }
        
        try:
            # Split tickers for batch processing
            ticker_chunks = chunk_list(tickers, 10)  # Tiingo batch size
            
            # Process individual tickers (Tiingo doesn't support comma-separated in daily endpoint)
            for ticker in tickers[:self.max_calls]:
                if self.call_count >= self.max_calls:
                    break
                
                start_time = datetime.now()
                
                try:
                    # Individual ticker endpoint
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
                    
                    url = f"{self.base_url}/tiingo/daily/{ticker}/prices"
                    params = {
                        'startDate': start_date,
                        'endDate': end_date,
                        'format': 'json'
                    }
                    
                    response = await http_client.request_with_retries(
                        url, headers=headers, params=params, provider=self.provider
                    )
                    
                    # Process response
                    market_records = []
                    asset_records = []
                    
                    if isinstance(response, list):
                        for item in response:
                            if 'ticker' in item and 'date' in item:
                                ticker = normalize_ticker(item['ticker'])
                                
                                # Add asset record
                                asset_records.append({
                                    'ticker': ticker,
                                    'name': ticker,
                                    'asset_type': 'stock',
                                    'exchange': 'NYSE/NASDAQ',
                                    'added_at': datetime.now(timezone.utc)
                                })
                                
                                # Add price record
                                market_records.append({
                                    'ticker': ticker,
                                    'timestamp': datetime.fromisoformat(item['date'].replace('Z', '+00:00')),
                                    'open': item.get('open'),
                                    'high': item.get('high'),
                                    'low': item.get('low'),
                                    'close': item.get('close'),
                                    'volume': item.get('volume'),
                                    'source': 'tiingo'
                                })
                    
                    # Bulk upsert
                    if asset_records:
                        await db_manager.upsert_batch('assets', asset_records, ['ticker'])
                    
                    if market_records:
                        await db_manager.upsert_batch('market_prices', market_records, ['ticker', 'timestamp'])
                        results['records'] += len(market_records)
                    
                    self.call_count += 1
                    results['calls'] += 1
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'daily_prices_chunk_{i}',
                        duration, 'success', len(market_records)
                    )
                    
                    logger.info(f"Tiingo: Processed chunk {i+1}, {len(market_records)} records")
                    
                except Exception as e:
                    duration = (datetime.now() - start_time).total_seconds()
                    error_msg = str(e)
                    results['errors'].append(error_msg)
                    
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'daily_prices_chunk_{i}',
                        duration, 'error', 0, error_msg
                    )
                    
                    logger.error(f"Tiingo chunk {i} failed: {e}")
        
        except Exception as e:
            logger.error(f"Tiingo collection failed: {e}")
            results['errors'].append(str(e))
        
        return results

class PolygonCollector:
    """Polygon.io data collector - Comprehensive market data"""
    
    def __init__(self):
        self.provider = 'polygon'
        self.call_count = 0
        self.max_calls = 10
        self.base_url = config.api.polygon_base_url
        self.api_key = config.api.polygon_api_key
    
    async def collect_market_data(self, session_id: str, tickers: List[str]) -> Dict[str, Any]:
        """Collect market data from Polygon"""
        results = {'records': 0, 'calls': 0, 'errors': []}
        
        if not self.api_key:
            logger.error("Polygon API key not configured")
            return results
        
        try:
            # Get recent aggregates for each ticker
            for i, ticker in enumerate(tickers[:self.max_calls]):
                if self.call_count >= self.max_calls:
                    break
                
                start_time = datetime.now()
                
                try:
                    # Get 5-day aggregates
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
                    
                    url = f"{self.base_url}/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
                    params = {'apikey': self.api_key}
                    
                    response = await http_client.request_with_retries(
                        url, params=params, provider=self.provider
                    )
                    
                    market_records = []
                    
                    if response.get('status') == 'OK' and 'results' in response:
                        ticker_norm = normalize_ticker(ticker)
                        
                        # Add asset record
                        asset_record = {
                            'ticker': ticker_norm,
                            'name': ticker_norm,
                            'asset_type': 'stock',
                            'exchange': 'NYSE/NASDAQ',
                            'added_at': datetime.now(timezone.utc)
                        }
                        await db_manager.upsert_batch('assets', [asset_record], ['ticker'])
                        
                        # Process price data
                        for item in response['results']:
                            market_records.append({
                                'ticker': ticker_norm,
                                'timestamp': datetime.fromtimestamp(item['t'] / 1000, tz=timezone.utc),
                                'open': item.get('o'),
                                'high': item.get('h'),
                                'low': item.get('l'),
                                'close': item.get('c'),
                                'volume': item.get('v'),
                                'source': 'polygon'
                            })
                    
                    if market_records:
                        await db_manager.upsert_batch('market_prices', market_records, ['ticker', 'timestamp'])
                        results['records'] += len(market_records)
                    
                    self.call_count += 1
                    results['calls'] += 1
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'aggregates_{ticker}',
                        duration, 'success', len(market_records)
                    )
                    
                    logger.info(f"Polygon: Processed {ticker}, {len(market_records)} records")
                    
                except Exception as e:
                    duration = (datetime.now() - start_time).total_seconds()
                    error_msg = str(e)
                    results['errors'].append(f"{ticker}: {error_msg}")
                    
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'aggregates_{ticker}',
                        duration, 'error', 0, error_msg
                    )
                    
                    logger.error(f"Polygon {ticker} failed: {e}")
        
        except Exception as e:
            logger.error(f"Polygon collection failed: {e}")
            results['errors'].append(str(e))
        
        return results

class AlpacaCollector:
    """Alpaca data collector - Trading platform data"""
    
    def __init__(self):
        self.provider = 'alpaca'
        self.call_count = 0
        self.max_calls = 10
        self.base_url = config.api.alpaca_data_url
        self.api_key = config.api.alpaca_api_key
        self.secret_key = config.api.alpaca_secret_key
    
    async def collect_market_data(self, session_id: str, tickers: List[str]) -> Dict[str, Any]:
        """Collect market data from Alpaca"""
        results = {'records': 0, 'calls': 0, 'errors': []}
        
        if not self.api_key or not self.secret_key:
            logger.error("Alpaca API credentials not configured")
            return results
        
        headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.secret_key
        }
        
        try:
            # Get historical bars in batches
            ticker_chunks = chunk_list(tickers, 5)  # Alpaca batch limit
            
            for i, chunk in enumerate(ticker_chunks[:self.max_calls]):
                if self.call_count >= self.max_calls:
                    break
                
                start_time = datetime.now()
                
                try:
                    symbols = ','.join(chunk)
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
                    
                    url = f"{self.base_url}/v2/stocks/bars"
                    params = {
                        'symbols': symbols,
                        'timeframe': '1Day',
                        'start': start_date,
                        'end': end_date,
                        'limit': 1000
                    }
                    
                    response = await http_client.request_with_retries(
                        url, headers=headers, params=params, provider=self.provider
                    )
                    
                    market_records = []
                    asset_records = []
                    
                    if 'bars' in response:
                        for ticker, bars in response['bars'].items():
                            ticker_norm = normalize_ticker(ticker)
                            
                            # Add asset record
                            asset_records.append({
                                'ticker': ticker_norm,
                                'name': ticker_norm,
                                'asset_type': 'stock',
                                'exchange': 'NYSE/NASDAQ',
                                'added_at': datetime.now(timezone.utc)
                            })
                            
                            # Process bars
                            for bar in bars:
                                market_records.append({
                                    'ticker': ticker_norm,
                                    'timestamp': datetime.fromisoformat(bar['t'].replace('Z', '+00:00')),
                                    'open': bar.get('o'),
                                    'high': bar.get('h'),
                                    'low': bar.get('l'),
                                    'close': bar.get('c'),
                                    'volume': bar.get('v'),
                                    'source': 'alpaca'
                                })
                    
                    # Bulk upsert
                    if asset_records:
                        await db_manager.upsert_batch('assets', asset_records, ['ticker'])
                    
                    if market_records:
                        await db_manager.upsert_batch('market_prices', market_records, ['ticker', 'timestamp'])
                        results['records'] += len(market_records)
                    
                    self.call_count += 1
                    results['calls'] += 1
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'bars_chunk_{i}',
                        duration, 'success', len(market_records)
                    )
                    
                    logger.info(f"Alpaca: Processed chunk {i+1}, {len(market_records)} records")
                    
                except Exception as e:
                    duration = (datetime.now() - start_time).total_seconds()
                    error_msg = str(e)
                    results['errors'].append(error_msg)
                    
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'bars_chunk_{i}',
                        duration, 'error', 0, error_msg
                    )
                    
                    logger.error(f"Alpaca chunk {i} failed: {e}")
        
        except Exception as e:
            logger.error(f"Alpaca collection failed: {e}")
            results['errors'].append(str(e))
        
        return results

class MarketDataOrchestrator:
    """Orchestrates market data collection from all providers"""
    
    def __init__(self):
        self.collectors = {
            'yfinance': YFinanceCollector(),
            'tiingo': TiingoCollector(),
            'polygon': PolygonCollector(),
            'alpaca': AlpacaCollector()
        }
    
    async def collect_all(self, session_id: str, tickers: Optional[List[str]] = None) -> Dict[str, Any]:
        """Collect market data from all providers"""
        tickers = tickers or PRIORITY_TICKERS
        results = {
            'total_records': 0,
            'total_calls': 0,
            'providers': {},
            'errors': []
        }
        
        logger.info(f"Starting market data collection for {len(tickers)} tickers")
        
        # Run collectors in parallel
        tasks = []
        for name, collector in self.collectors.items():
            task = asyncio.create_task(
                collector.collect_market_data(session_id, tickers),
                name=f"market_{name}"
            )
            tasks.append((name, task))
        
        # Wait for all collectors to complete
        for provider_name, task in tasks:
            try:
                provider_results = await task
                results['providers'][provider_name] = provider_results
                results['total_records'] += provider_results['records']
                results['total_calls'] += provider_results['calls']
                
                if provider_results['errors']:
                    results['errors'].extend([f"{provider_name}: {err}" for err in provider_results['errors']])
                
                logger.info(f"Market data - {provider_name}: {provider_results['records']} records, {provider_results['calls']} calls")
                
            except Exception as e:
                error_msg = f"{provider_name} failed: {str(e)}"
                results['errors'].append(error_msg)
                logger.error(error_msg)
        
        logger.info(f"Market data collection complete: {results['total_records']} records, {results['total_calls']} calls")
        return results
