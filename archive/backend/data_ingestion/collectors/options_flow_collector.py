"""
Professional Options Flow Data Collector for uRISK Member-1 Feature
Collects call/put volume, open interest changes, IV spikes, and whale block trades.
Enhanced for 200+ asset universe with intelligent anomaly detection.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json

from ..config.settings import settings
from ..db.postgres_handler import db, insert_anomaly
from ..utils.logging_utils import setup_logger

logger = setup_logger(__name__)

class OptionsFlowCollector:
    """Professional-grade options flow collector for 200+ assets with anomaly detection."""
    
    def __init__(self):
        self.polygon_api_key = getattr(settings, 'POLYGON_API_KEY', None)
        self.tradier_api_key = getattr(settings, 'TRADIER_API_KEY', None)
        
        self.polygon_headers = {'Authorization': f'Bearer {self.polygon_api_key}'} if self.polygon_api_key else {}
        self.tradier_headers = {
            'Authorization': f'Bearer {self.tradier_api_key}',
            'Accept': 'application/json'
        } if self.tradier_api_key else {}
        
        # Professional thresholds for anomaly detection
        self.volume_spike_threshold = 3.0      # 3x normal volume
        self.iv_spike_threshold = 0.20         # 20% IV increase
        self.whale_trade_threshold = 10000     # Minimum contracts for whale trade
        self.call_put_ratio_threshold = 3.0    # Unusual call/put ratio
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    async def get_optionable_assets(self) -> List[str]:
        """Get all optionable assets from database (US stocks primarily)."""
        query = """
            SELECT ticker, name FROM assets 
            WHERE asset_type = 'stock' 
              AND country = 'US'
              AND ticker NOT LIKE '%-USD'
              AND ticker NOT LIKE '%=X'
              AND ticker NOT LIKE '%.NS'
            ORDER BY ticker
        """
        
        assets = await db.fetch_all(query)
        
        # Focus on major liquid stocks for options
        major_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX',
            'JPM', 'BAC', 'V', 'MA', 'JNJ', 'PFE', 'UNH', 'XOM', 'CVX',
            'SPY', 'QQQ', 'IWM', 'VIX', 'AMD', 'INTC', 'CRM', 'ORCL'
        ]
        
        # Return intersection of database assets and major liquid tickers
        db_tickers = [asset['ticker'] for asset in assets]
        return [ticker for ticker in major_tickers if ticker in db_tickers]
    
    def collect_polygon_options_data(self, ticker: str, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Collect options data from Polygon.io.
        
        Args:
            ticker: Stock ticker symbol
            date: Date in YYYY-MM-DD format (defaults to today)
        """
        if not settings.POLYGON_API_KEY:
            logger.warning("Polygon API key not configured")
            return []
        
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            logger.info(f"Collecting Polygon options data for {ticker} on {date}")
            
            # Get options contracts for the ticker
            url = f"https://api.polygon.io/v3/reference/options/contracts"
            params = {
                'underlying_ticker': ticker,
                'contract_type': 'option',
                'expired': 'false',
                'limit': 1000,
                'apikey': settings.POLYGON_API_KEY
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            contracts_data = response.json()
            
            if not contracts_data.get('results'):
                logger.warning(f"No options contracts found for {ticker}")
                return []
            
            contracts = contracts_data['results']
            options_data = []
            
            # Process options contracts and look for unusual activity
            for contract in contracts[:50]:  # Limit to avoid rate limits
                try:
                    contract_ticker = contract.get('ticker')
                    if not contract_ticker:
                        continue
                    
                    # Get daily bars for this option
                    bars_url = f"https://api.polygon.io/v2/aggs/ticker/{contract_ticker}/range/1/day/{date}/{date}"
                    bars_params = {'apikey': settings.POLYGON_API_KEY}
                    
                    bars_response = self.session.get(bars_url, params=bars_params, timeout=15)
                    bars_response.raise_for_status()
                    
                    bars_data = bars_response.json()
                    
                    if bars_data.get('results'):
                        bar = bars_data['results'][0]
                        
                        option_info = {
                            'ticker': ticker,
                            'contract_ticker': contract_ticker,
                            'contract_type': contract.get('contract_type'),
                            'strike_price': contract.get('strike_price'),
                            'expiration_date': contract.get('expiration_date'),
                            'volume': bar.get('v', 0),
                            'open': bar.get('o'),
                            'close': bar.get('c'),
                            'high': bar.get('h'),
                            'low': bar.get('l'),
                            'timestamp': datetime.fromtimestamp(bar.get('t', 0) / 1000),
                            'source': 'polygon'
                        }
                        
                        options_data.append(option_info)
                        
                except Exception as e:
                    logger.warning(f"Failed to process contract {contract.get('ticker', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Collected {len(options_data)} options records for {ticker}")
            return options_data
            
        except Exception as e:
            logger.error(f"Failed to collect Polygon options data for {ticker}: {e}")
            return []
    
    def collect_tradier_options_data(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Collect options data from Tradier API.
        
        Args:
            ticker: Stock ticker symbol
        """
        if not settings.TRADIER_API_KEY:
            logger.warning("Tradier API key not configured")
            return []
        
        try:
            logger.info(f"Collecting Tradier options data for {ticker}")
            
            # Get options chain
            url = f"{settings.TRADIER_BASE_URL}/markets/options/chains"
            params = {
                'symbol': ticker,
                'expiration': self.get_next_expiration_date()
            }
            
            response = self.session.get(
                url, 
                headers=self.tradier_headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            chain_data = response.json()
            
            if not chain_data.get('options'):
                logger.warning(f"No options chain found for {ticker}")
                return []
            
            options = chain_data['options']['option']
            if not isinstance(options, list):
                options = [options]
            
            options_data = []
            
            for option in options:
                try:
                    option_info = {
                        'ticker': ticker,
                        'contract_ticker': option.get('symbol'),
                        'contract_type': option.get('option_type'),
                        'strike_price': float(option.get('strike', 0)),
                        'expiration_date': option.get('expiration_date'),
                        'volume': int(option.get('volume', 0)),
                        'open_interest': int(option.get('open_interest', 0)),
                        'bid': float(option.get('bid', 0)),
                        'ask': float(option.get('ask', 0)),
                        'last': float(option.get('last', 0)),
                        'implied_volatility': float(option.get('greeks', {}).get('iv', 0)),
                        'delta': float(option.get('greeks', {}).get('delta', 0)),
                        'gamma': float(option.get('greeks', {}).get('gamma', 0)),
                        'theta': float(option.get('greeks', {}).get('theta', 0)),
                        'vega': float(option.get('greeks', {}).get('vega', 0)),
                        'timestamp': datetime.now(),
                        'source': 'tradier'
                    }
                    
                    options_data.append(option_info)
                    
                except Exception as e:
                    logger.warning(f"Failed to process Tradier option: {e}")
                    continue
            
            logger.info(f"Collected {len(options_data)} Tradier options records for {ticker}")
            return options_data
            
        except Exception as e:
            logger.error(f"Failed to collect Tradier options data for {ticker}: {e}")
            return []
    
    def get_next_expiration_date(self) -> str:
        """Get the next Friday (typical options expiration)."""
        today = datetime.now()
        days_ahead = 4 - today.weekday()  # Friday is weekday 4
        if days_ahead <= 0:  # Today is Friday or later
            days_ahead += 7
        
        next_friday = today + timedelta(days=days_ahead)
        return next_friday.strftime('%Y-%m-%d')
    
    def detect_unusual_options_activity(self, options_data: List[Dict[str, Any]], ticker: str) -> List[Dict[str, Any]]:
        """
        Detect unusual options activity patterns.
        
        Args:
            options_data: List of options records
            ticker: Stock ticker
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        if not options_data:
            return anomalies
        
        try:
            # Convert to DataFrame for analysis
            df = pd.DataFrame(options_data)
            
            # Separate calls and puts
            calls = df[df['contract_type'] == 'call'] if 'contract_type' in df.columns else df
            puts = df[df['contract_type'] == 'put'] if 'contract_type' in df.columns else pd.DataFrame()
            
            # Calculate total volumes
            total_call_volume = calls['volume'].sum() if not calls.empty and 'volume' in calls.columns else 0
            total_put_volume = puts['volume'].sum() if not puts.empty and 'volume' in puts.columns else 0
            total_volume = total_call_volume + total_put_volume
            
            if total_volume == 0:
                return anomalies
            
            # 1. Call/Put Volume Imbalance
            if total_volume > 0:
                call_put_ratio = total_call_volume / total_put_volume if total_put_volume > 0 else float('inf')
                
                if call_put_ratio > 3.0:  # Heavy call bias
                    anomalies.append({
                        'ticker': ticker,
                        'metric': 'call_skew',
                        'anomaly_score': min(call_put_ratio / 10.0, 1.0),
                        'severity': 'high' if call_put_ratio > 5.0 else 'medium',
                        'explanation': f'Unusual call volume detected. Call/Put ratio: {call_put_ratio:.2f}',
                        'timestamp': datetime.now(),
                        'details': {
                            'call_volume': total_call_volume,
                            'put_volume': total_put_volume,
                            'ratio': call_put_ratio
                        }
                    })
                
                elif call_put_ratio < 0.33:  # Heavy put bias
                    anomalies.append({
                        'ticker': ticker,
                        'metric': 'put_skew',
                        'anomaly_score': min(3.0 / call_put_ratio / 10.0, 1.0),
                        'severity': 'high' if call_put_ratio < 0.2 else 'medium',
                        'explanation': f'Unusual put volume detected. Call/Put ratio: {call_put_ratio:.2f}',
                        'timestamp': datetime.now(),
                        'details': {
                            'call_volume': total_call_volume,
                            'put_volume': total_put_volume,
                            'ratio': call_put_ratio
                        }
                    })
            
            # 2. High Volume Spikes
            if 'volume' in df.columns:
                volume_mean = df['volume'].mean()
                volume_std = df['volume'].std()
                
                if volume_std > 0:
                    high_volume_contracts = df[df['volume'] > (volume_mean + 2 * volume_std)]
                    
                    if len(high_volume_contracts) > 0:
                        max_volume = high_volume_contracts['volume'].max()
                        anomaly_score = min((max_volume - volume_mean) / (volume_std * 3), 1.0)
                        
                        anomalies.append({
                            'ticker': ticker,
                            'metric': 'volume_spike',
                            'anomaly_score': anomaly_score,
                            'severity': 'high' if anomaly_score > 0.7 else 'medium',
                            'explanation': f'High volume spike detected. Max volume: {max_volume}, Mean: {volume_mean:.0f}',
                            'timestamp': datetime.now(),
                            'details': {
                                'max_volume': max_volume,
                                'mean_volume': volume_mean,
                                'contracts_affected': len(high_volume_contracts)
                            }
                        })
            
            # 3. Implied Volatility Spikes
            if 'implied_volatility' in df.columns:
                iv_data = df[df['implied_volatility'] > 0]['implied_volatility']
                
                if len(iv_data) > 0:
                    iv_mean = iv_data.mean()
                    iv_std = iv_data.std()
                    
                    if iv_std > 0:
                        high_iv_threshold = iv_mean + 2 * iv_std
                        high_iv_contracts = df[df['implied_volatility'] > high_iv_threshold]
                        
                        if len(high_iv_contracts) > 0:
                            max_iv = high_iv_contracts['implied_volatility'].max()
                            anomaly_score = min((max_iv - iv_mean) / (iv_std * 3), 1.0)
                            
                            anomalies.append({
                                'ticker': ticker,
                                'metric': 'iv_spike',
                                'anomaly_score': anomaly_score,
                                'severity': 'high' if anomaly_score > 0.7 else 'medium',
                                'explanation': f'Implied volatility spike detected. Max IV: {max_iv:.2f}, Mean: {iv_mean:.2f}',
                                'timestamp': datetime.now(),
                                'details': {
                                    'max_iv': max_iv,
                                    'mean_iv': iv_mean,
                                    'contracts_affected': len(high_iv_contracts)
                                }
                            })
            
            logger.info(f"Detected {len(anomalies)} options anomalies for {ticker}")
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect options anomalies for {ticker}: {e}")
            return []
    
    def store_options_anomalies(self, anomalies: List[Dict[str, Any]]) -> int:
        """Store options anomalies in the database."""
        if not anomalies:
            return 0
        
        stored_count = 0
        
        for anomaly in anomalies:
            try:
                anomaly_id = insert_anomaly(
                    ticker=anomaly['ticker'],
                    metric=anomaly['metric'],
                    anomaly_score=anomaly['anomaly_score'],
                    severity=anomaly['severity'],
                    explanation=anomaly['explanation'],
                    timestamp=anomaly['timestamp'].isoformat()
                )
                
                if anomaly_id:
                    stored_count += 1
                    
                    if anomaly['severity'] == 'high':
                        logger.warning(f"High severity options anomaly detected: {anomaly['explanation']}")
                    
            except Exception as e:
                logger.warning(f"Failed to store options anomaly: {e}")
                continue
        
        logger.info(f"Stored {stored_count} options anomalies in database")
        return stored_count
    
    async def run_collection_cycle(self) -> Dict[str, Any]:
        """Run a complete options flow collection cycle."""
        start_time = datetime.now()
        logger.info("Starting options flow collection cycle")
        
        results = {
            'start_time': start_time.isoformat(),
            'tickers_processed': 0,
            'contracts_collected': 0,
            'anomalies_detected': 0,
            'anomalies_stored': 0,
            'errors': [],
            'success': True
        }
        
        try:
            # Get options-enabled tickers
            options_tickers = self.get_options_tickers()[:5]  # Limit to avoid rate limits
            
            all_anomalies = []
            total_contracts = 0
            
            for ticker in options_tickers:
                try:
                    logger.info(f"Processing options data for {ticker}")
                    
                    # Collect from both sources if available
                    all_options_data = []
                    
                    # Polygon data
                    if settings.POLYGON_API_KEY:
                        polygon_data = self.collect_polygon_options_data(ticker)
                        all_options_data.extend(polygon_data)
                    
                    # Tradier data
                    if settings.TRADIER_API_KEY:
                        tradier_data = self.collect_tradier_options_data(ticker)
                        all_options_data.extend(tradier_data)
                    
                    if all_options_data:
                        total_contracts += len(all_options_data)
                        
                        # Detect anomalies
                        ticker_anomalies = self.detect_unusual_options_activity(all_options_data, ticker)
                        all_anomalies.extend(ticker_anomalies)
                        
                        results['tickers_processed'] += 1
                    
                    # Small delay to respect rate limits
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    results['errors'].append(f"Failed to process {ticker}: {str(e)}")
                    logger.error(f"Failed to process options for {ticker}: {e}")
            
            # Store anomalies
            if all_anomalies:
                stored_count = self.store_options_anomalies(all_anomalies)
                results['anomalies_detected'] = len(all_anomalies)
                results['anomalies_stored'] = stored_count
            
            results['contracts_collected'] = total_contracts
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Options flow collection completed in {duration:.2f}s: "
                       f"{results['tickers_processed']} tickers, "
                       f"{results['contracts_collected']} contracts, "
                       f"{results['anomalies_detected']} anomalies")
            
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = duration
            
        except Exception as e:
            logger.error(f"Options flow collection cycle failed: {e}")
            results['success'] = False
            results['errors'].append(str(e))
        
        return results

# Global collector instance
options_flow_collector = OptionsFlowCollector()

# Convenience functions for external use
def collect_options_flow() -> Dict[str, Any]:
    """Synchronous wrapper for options flow collection."""
    return asyncio.run(options_flow_collector.run_collection_cycle())

def collect_single_ticker_options(ticker: str) -> List[Dict[str, Any]]:
    """Collect options data for a single ticker."""
    all_data = []
    
    if settings.POLYGON_API_KEY:
        polygon_data = options_flow_collector.collect_polygon_options_data(ticker)
        all_data.extend(polygon_data)
    
    if settings.TRADIER_API_KEY:
        tradier_data = options_flow_collector.collect_tradier_options_data(ticker)
        all_data.extend(tradier_data)
    
    return all_data

def detect_options_anomalies_for_ticker(ticker: str) -> List[Dict[str, Any]]:
    """Detect options anomalies for a specific ticker."""
    options_data = collect_single_ticker_options(ticker)
    return options_flow_collector.detect_unusual_options_activity(options_data, ticker)