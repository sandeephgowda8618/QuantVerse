#!/usr/bin/env python3
"""
Alpha Vantage Technical Indicators Collector
Handles technical indicators using key rotation and optimized endpoints
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
import random

from .config import config, PRIORITY_TICKERS
from .utils import http_client, db_manager, ingestion_logger, normalize_ticker, chunk_list, now_epoch

logger = logging.getLogger(__name__)

class AlphaVantageCollector:
    """Alpha Vantage collector with key rotation and technical indicators"""
    
    def __init__(self):
        self.provider = 'alpha_vantage'
        self.call_count = 0
        self.max_calls = 10
        self.base_url = 'https://www.alphavantage.co/query'
        self.api_keys = config.api.alpha_vantage_keys or []
        self.current_key_index = 0
        
        if not self.api_keys:
            logger.error("No Alpha Vantage API keys configured")
    
    def _get_next_api_key(self) -> Optional[str]:
        """Get next API key using rotation"""
        if not self.api_keys:
            return None
        
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key
    
    async def collect_technical_indicators(self, session_id: str, tickers: List[str]) -> Dict[str, Any]:
        """Collect technical indicators from Alpha Vantage"""
        results = {'records': 0, 'calls': 0, 'errors': []}
        
        if not self.api_keys:
            logger.error("Alpha Vantage API keys not configured")
            return results
        
        # Focus on priority tickers and key technical indicators
        priority_tickers = [t for t in tickers if t in PRIORITY_TICKERS[:self.max_calls]]
        
        # Technical indicators to collect (rotate to maximize coverage)
        indicators = ['RSI', 'MACD', 'SMA', 'EMA', 'BBANDS', 'ATR', 'ADX', 'CCI', 'STOCH', 'WILLR']
        
        try:
            for i, ticker in enumerate(priority_tickers):
                if self.call_count >= self.max_calls:
                    break
                
                # Select indicator for this ticker (rotate)
                indicator = indicators[i % len(indicators)]
                
                start_time = datetime.now()
                api_key = self._get_next_api_key()
                
                if not api_key:
                    logger.error("No API key available")
                    break
                
                try:
                    # Build query parameters
                    params = {
                        'function': indicator,
                        'symbol': ticker,
                        'interval': 'daily',
                        'time_period': '14',  # Common period
                        'apikey': api_key,
                        'datatype': 'json'
                    }
                    
                    # Special parameters for specific indicators
                    if indicator == 'MACD':
                        params.update({
                            'fastperiod': '12',
                            'slowperiod': '26',
                            'signalperiod': '9'
                        })
                    elif indicator == 'BBANDS':
                        params.update({
                            'nbdevup': '2',
                            'nbdevdn': '2',
                            'matype': '0'
                        })
                    elif indicator == 'STOCH':
                        params.update({
                            'fastkperiod': '14',
                            'slowkperiod': '3',
                            'slowdperiod': '3',
                            'slowkmatype': '0',
                            'slowdmatype': '0'
                        })
                    
                    response = await http_client.request_with_retries(
                        self.base_url, params=params, provider=self.provider
                    )
                    
                    # Process response
                    technical_records = []
                    alpha_vantage_records = []
                    
                    # Check for API errors
                    if 'Error Message' in response:
                        raise Exception(f"API Error: {response['Error Message']}")
                    elif 'Note' in response:
                        raise Exception(f"API Limit: {response['Note']}")
                    
                    # Process technical indicator data
                    if f'Technical Analysis: {indicator}' in response:
                        meta_data = response.get('Meta Data', {})
                        tech_data = response[f'Technical Analysis: {indicator}']
                        
                        # Get recent data points (last 30 days)
                        cutoff_date = datetime.now() - timedelta(days=30)
                        
                        for date_str, values in list(tech_data.items())[:30]:
                            try:
                                timestamp = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                                
                                if timestamp >= cutoff_date:
                                    # Create technical indicator record
                                    tech_record = {
                                        'ticker': normalize_ticker(ticker),
                                        'indicator': indicator,
                                        'timestamp': timestamp,
                                        'values': json.dumps(values),
                                        'source': 'alpha_vantage',
                                        'created_at': datetime.now(timezone.utc)
                                    }
                                    
                                    # Add specific value fields based on indicator
                                    if indicator == 'RSI':
                                        tech_record['rsi'] = float(values.get('RSI', 0))
                                    elif indicator == 'MACD':
                                        tech_record['macd'] = float(values.get('MACD', 0))
                                        tech_record['macd_signal'] = float(values.get('MACD_Signal', 0))
                                        tech_record['macd_hist'] = float(values.get('MACD_Hist', 0))
                                    elif indicator in ['SMA', 'EMA']:
                                        tech_record['ma_value'] = float(values.get(indicator, 0))
                                    elif indicator == 'BBANDS':
                                        tech_record['bb_upper'] = float(values.get(f'Real Upper Band', 0))
                                        tech_record['bb_middle'] = float(values.get(f'Real Middle Band', 0))
                                        tech_record['bb_lower'] = float(values.get(f'Real Lower Band', 0))
                                    elif indicator == 'ATR':
                                        tech_record['atr'] = float(values.get('ATR', 0))
                                    
                                    technical_records.append(tech_record)
                                    
                                    # Create raw Alpha Vantage record for audit trail
                                    alpha_record = {
                                        'ticker': normalize_ticker(ticker),
                                        'endpoint': indicator,
                                        'timestamp': timestamp,
                                        'raw_payload': response,
                                        'parsed_values': values,
                                        'quality_flag': 'success',
                                        'ingestion_epoch': now_epoch(),
                                        'ingestion_sequence': int(datetime.now().timestamp() * 1000000),
                                        'ingestion_session_id': session_id,
                                        'ingestion_time': datetime.now(timezone.utc),
                                        'source': 'alpha_vantage',
                                        'data_type': 'technical_indicator',
                                        'interval_period': 'daily',
                                        'metadata': json.dumps({
                                            'indicator': indicator,
                                            'symbol': ticker,
                                            'last_refreshed': meta_data.get('Last Refreshed', ''),
                                            'time_zone': meta_data.get('Time Zone', '')
                                        })
                                    }
                                    alpha_vantage_records.append(alpha_record)
                            
                            except (ValueError, KeyError) as e:
                                logger.warning(f"Error processing {indicator} data for {ticker} on {date_str}: {e}")
                    
                    # Handle time series data (if we requested TIME_SERIES_* functions)
                    elif 'Time Series (Daily)' in response:
                        await self._process_time_series(
                            response, ticker, session_id, alpha_vantage_records
                        )
                    
                    # Bulk upsert technical indicators
                    if technical_records:
                        await db_manager.upsert_batch(
                            'technical_indicators',
                            technical_records,
                            ['ticker', 'indicator', 'timestamp']
                        )
                    
                    # Bulk upsert Alpha Vantage raw data
                    if alpha_vantage_records:
                        await db_manager.upsert_batch(
                            'alpha_vantage_data',
                            alpha_vantage_records,
                            ['ticker', 'endpoint', 'timestamp']
                        )
                        results['records'] += len(alpha_vantage_records)
                    
                    self.call_count += 1
                    results['calls'] += 1
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'{indicator}_{ticker}',
                        duration, 'success', len(alpha_vantage_records)
                    )
                    
                    logger.info(f"Alpha Vantage: {ticker} {indicator} - {len(alpha_vantage_records)} records")
                
                except Exception as e:
                    duration = (datetime.now() - start_time).total_seconds()
                    error_msg = str(e)
                    results['errors'].append(f"{ticker} {indicator}: {error_msg}")
                    
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'{indicator}_{ticker}',
                        duration, 'error', 0, error_msg
                    )
                    
                    logger.error(f"Alpha Vantage {ticker} {indicator} failed: {e}")
                    
                    # If rate limited, wait before continuing
                    if 'rate limit' in error_msg.lower() or 'thank you for using alpha vantage' in error_msg.lower():
                        logger.info("Rate limited, waiting 60 seconds...")
                        await asyncio.sleep(60)
        
        except Exception as e:
            logger.error(f"Alpha Vantage collection failed: {e}")
            results['errors'].append(str(e))
        
        return results
    
    async def _process_time_series(self, response: Dict, ticker: str, session_id: str, alpha_records: List):
        """Process time series data from Alpha Vantage"""
        try:
            meta_data = response.get('Meta Data', {})
            time_series = response.get('Time Series (Daily)', {})
            
            # Get recent data (last 7 days)
            cutoff_date = datetime.now() - timedelta(days=7)
            
            for date_str, values in list(time_series.items())[:7]:
                try:
                    timestamp = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                    
                    if timestamp >= cutoff_date:
                        alpha_record = {
                            'ticker': normalize_ticker(ticker),
                            'endpoint': 'TIME_SERIES_DAILY',
                            'timestamp': timestamp,
                            'raw_payload': response,
                            'parsed_values': values,
                            'quality_flag': 'success',
                            'ingestion_epoch': now_epoch(),
                            'ingestion_sequence': int(datetime.now().timestamp() * 1000000),
                            'ingestion_session_id': session_id,
                            'ingestion_time': datetime.now(timezone.utc),
                            'source': 'alpha_vantage',
                            'data_type': 'time_series',
                            'interval_period': 'daily',
                            'metadata': json.dumps({
                                'symbol': ticker,
                                'last_refreshed': meta_data.get('Last Refreshed', ''),
                                'time_zone': meta_data.get('Time Zone', ''),
                                'output_size': meta_data.get('Output Size', '')
                            })
                        }
                        alpha_records.append(alpha_record)
                
                except ValueError as e:
                    logger.warning(f"Error processing time series for {ticker} on {date_str}: {e}")
        
        except Exception as e:
            logger.error(f"Error processing time series for {ticker}: {e}")
    
    async def collect_economic_indicators(self, session_id: str) -> Dict[str, Any]:
        """Collect economic indicators from Alpha Vantage"""
        results = {'records': 0, 'calls': 0, 'errors': []}
        
        if not self.api_keys:
            return results
        
        # Economic indicators to collect
        economic_functions = [
            'REAL_GDP',
            'REAL_GDP_PER_CAPITA', 
            'TREASURY_YIELD',
            'FEDERAL_FUNDS_RATE',
            'CPI',
            'INFLATION',
            'RETAIL_SALES',
            'DURABLES',
            'UNEMPLOYMENT',
            'NONFARM_PAYROLL'
        ]
        
        try:
            for func in economic_functions[:min(5, self.max_calls - self.call_count)]:
                if self.call_count >= self.max_calls:
                    break
                
                start_time = datetime.now()
                api_key = self._get_next_api_key()
                
                if not api_key:
                    break
                
                try:
                    params = {
                        'function': func,
                        'interval': 'monthly',
                        'apikey': api_key,
                        'datatype': 'json'
                    }
                    
                    # Special parameters for specific functions
                    if func == 'TREASURY_YIELD':
                        params['interval'] = 'daily'
                        params['maturity'] = '10year'
                    
                    response = await http_client.request_with_retries(
                        self.base_url, params=params, provider=self.provider
                    )
                    
                    economic_records = []
                    
                    # Check for errors
                    if 'Error Message' in response:
                        raise Exception(f"API Error: {response['Error Message']}")
                    elif 'Note' in response:
                        raise Exception(f"API Limit: {response['Note']}")
                    
                    # Process economic data
                    data_key = f'data'
                    if data_key in response or 'data' in response:
                        data_points = response.get('data', response.get(data_key, []))
                        
                        # Get recent data points (last 12 months)
                        cutoff_date = datetime.now() - timedelta(days=365)
                        
                        for item in data_points[:12]:
                            try:
                                if 'date' in item and 'value' in item:
                                    timestamp = datetime.strptime(item['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
                                    
                                    if timestamp >= cutoff_date:
                                        economic_record = {
                                            'indicator': func,
                                            'endpoint': func,
                                            'api_function': func,
                                            'timestamp': timestamp,
                                            'interval_type': params.get('interval', 'monthly'),
                                            'value': float(item['value']) if item['value'] != '.' else None,
                                            'unit': item.get('unit', ''),
                                            'source': 'alpha_vantage',
                                            'raw_payload': response,
                                            'quality_flag': 'complete',
                                            'ingestion_epoch': now_epoch(),
                                            'ingestion_sequence': int(datetime.now().timestamp() * 1000000),
                                            'ingestion_time': datetime.now(timezone.utc)
                                        }
                                        economic_records.append(economic_record)
                            
                            except (ValueError, KeyError) as e:
                                logger.warning(f"Error processing {func} data point: {e}")
                    
                    # Bulk upsert
                    if economic_records:
                        await db_manager.upsert_batch(
                            'alpha_economic_indicators',
                            economic_records,
                            ['indicator', 'timestamp']
                        )
                        results['records'] += len(economic_records)
                    
                    self.call_count += 1
                    results['calls'] += 1
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'economic_{func}',
                        duration, 'success', len(economic_records)
                    )
                    
                    logger.info(f"Alpha Vantage: {func} - {len(economic_records)} economic indicators")
                
                except Exception as e:
                    duration = (datetime.now() - start_time).total_seconds()
                    error_msg = str(e)
                    results['errors'].append(f"{func}: {error_msg}")
                    
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'economic_{func}',
                        duration, 'error', 0, error_msg
                    )
                    
                    logger.error(f"Alpha Vantage {func} failed: {e}")
        
        except Exception as e:
            logger.error(f"Alpha Vantage economic indicators failed: {e}")
            results['errors'].append(str(e))
        
        return results

class TechnicalIndicatorsOrchestrator:
    """Orchestrates technical indicators collection"""
    
    def __init__(self):
        self.alpha_vantage = AlphaVantageCollector()
    
    async def collect_all(self, session_id: str, tickers: Optional[List[str]] = None) -> Dict[str, Any]:
        """Collect technical indicators and economic data"""
        tickers = tickers or PRIORITY_TICKERS
        results = {
            'total_records': 0,
            'total_calls': 0,
            'providers': {},
            'errors': []
        }
        
        logger.info(f"Starting technical indicators collection for {len(tickers)} tickers")
        
        try:
            # Collect technical indicators for tickers
            tech_results = await self.alpha_vantage.collect_technical_indicators(session_id, tickers)
            results['providers']['alpha_vantage_technical'] = tech_results
            results['total_records'] += tech_results['records']
            results['total_calls'] += tech_results['calls']
            
            if tech_results['errors']:
                results['errors'].extend([f"technical: {err}" for err in tech_results['errors']])
            
            # Collect economic indicators
            econ_results = await self.alpha_vantage.collect_economic_indicators(session_id)
            results['providers']['alpha_vantage_economic'] = econ_results
            results['total_records'] += econ_results['records']
            results['total_calls'] += econ_results['calls']
            
            if econ_results['errors']:
                results['errors'].extend([f"economic: {err}" for err in econ_results['errors']])
            
            logger.info(f"Technical indicators collection complete: {results['total_records']} records, {results['total_calls']} calls")
        
        except Exception as e:
            error_msg = f"Technical indicators collection failed: {str(e)}"
            results['errors'].append(error_msg)
            logger.error(error_msg)
        
        return results
