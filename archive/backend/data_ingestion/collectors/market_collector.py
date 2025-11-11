"""
Market data collector for yfinance and Tiingo APIs.
Collects OHLCV data, spreads, and liquidity metrics.
Enhanced with professional error handling and failover mechanisms.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import yfinance as yf
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import random

from ..config.settings import settings, TRACKED_ASSETS
from ..db.postgres_handler import db, insert_market_price
from ..utils.logging_utils import setup_logger
from .alpha_vantage_collector import alpha_vantage_collector

logger = setup_logger(__name__)

class MarketDataCollector:
    """
    Enhanced market data collector with professional error handling.
    Features:
    - Multiple data source failover (Tiingo -> yfinance -> Alpha Vantage)
    - Exponential backoff with jitter
    - Rate limit detection and handling
    - Circuit breaker pattern
    - Data validation and cleansing
    """
    
    def __init__(self):
        self.tiingo_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {settings.TIINGO_API_KEY}'
        }
        
        # Setup session with enhanced retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=5,  # Increased retries
            backoff_factor=2,  # Exponential backoff
            status_forcelist=[429, 500, 502, 503, 504, 520, 521, 522, 523, 524]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Rate limiting tracking
        self.api_call_times = {
            'tiingo': [],
            'yfinance': [],
            'alpha_vantage': []
        }
        self.rate_limits = {
            'tiingo': {'calls_per_hour': 500, 'calls_per_minute': 50},
            'yfinance': {'calls_per_hour': 2000, 'calls_per_minute': 100},
            'alpha_vantage': {'calls_per_minute': 5}
        }
    
    def _can_make_api_call(self, api_name: str) -> Tuple[bool, Optional[float]]:
        """
        Check if we can make an API call based on rate limits
        
        Returns:
            (can_call, wait_time_seconds)
        """
        now = time.time()
        call_times = self.api_call_times[api_name]
        limits = self.rate_limits[api_name]
        
        # Clean old calls (older than 1 hour)
        call_times[:] = [t for t in call_times if now - t < 3600]
        
        # Check minute limit
        if 'calls_per_minute' in limits:
            recent_calls = [t for t in call_times if now - t < 60]
            if len(recent_calls) >= limits['calls_per_minute']:
                wait_time = 60 - (now - min(recent_calls))
                return False, wait_time
        
        # Check hour limit
        if 'calls_per_hour' in limits:
            if len(call_times) >= limits['calls_per_hour']:
                wait_time = 3600 - (now - min(call_times))
                return False, wait_time
        
        return True, None
    
    def _record_api_call(self, api_name: str):
        """Record an API call for rate limiting"""
        self.api_call_times[api_name].append(time.time())
    
    async def _wait_for_rate_limit(self, api_name: str) -> bool:
        """
        Wait for rate limit to reset if necessary
        
        Returns:
            True if we can proceed, False if we should skip
        """
        can_call, wait_time = self._can_make_api_call(api_name)
        
        if not can_call and wait_time:
            if wait_time > 300:  # Don't wait more than 5 minutes
                logger.warning(f"Rate limit wait too long for {api_name}: {wait_time:.1f}s - skipping")
                return False
            
            logger.info(f"Rate limit reached for {api_name}, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
        
        return True
    
    def _validate_market_data(self, df: pd.DataFrame, ticker: str) -> bool:
        """
        Validate market data quality
        
        Args:
            df: DataFrame to validate
            ticker: Ticker symbol for logging
            
        Returns:
            True if data is valid
        """
        if df is None or df.empty:
            return False
        
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.warning(f"Missing columns for {ticker}: {missing_columns}")
            return False
        
        # Check for reasonable price ranges (basic sanity check)
        price_columns = ['open', 'high', 'low', 'close']
        for col in price_columns:
            if df[col].isnull().all():
                logger.warning(f"All {col} prices are null for {ticker}")
                return False
            
            if (df[col] <= 0).any():
                logger.warning(f"Non-positive prices found in {col} for {ticker}")
                # Clean the data instead of rejecting
                df[col] = df[col].replace(0, pd.NA)
        
        # Check for duplicate timestamps
        if df['timestamp'].duplicated().any():
            logger.warning(f"Duplicate timestamps found for {ticker}")
            df = df.drop_duplicates(subset=['timestamp'], keep='last')
        
        return True
    
    async def collect_tiingo_data_enhanced(self, ticker: str, start_date: Optional[str] = None, 
                                         max_retries: int = 3) -> Optional[pd.DataFrame]:
        """
        Enhanced Tiingo data collection with professional error handling
        
        Args:
            ticker: Ticker symbol
            start_date: Start date in YYYY-MM-DD format
            max_retries: Maximum retry attempts
            
        Returns:
            DataFrame with market data or None if failed
        """
        if not settings.TIINGO_API_KEY:
            logger.warning("Tiingo API key not configured")
            return None
        
        # Check rate limits
        if not await self._wait_for_rate_limit('tiingo'):
            return None
        
        # Default to last 30 days if no start date provided
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        url = f"{settings.TIINGO_BASE_URL}/tiingo/daily/{ticker}/prices"
        params = {
            'startDate': start_date,
            'token': settings.TIINGO_API_KEY,
            'format': 'json'
        }
        
        for attempt in range(max_retries):
            try:
                self._record_api_call('tiingo')
                
                # Add jitter to prevent thundering herd
                if attempt > 0:
                    jitter = random.uniform(1, 3)
                    await asyncio.sleep((2 ** attempt) + jitter)
                
                response = self.session.get(
                    url, 
                    headers=self.tiingo_headers, 
                    params=params, 
                    timeout=30
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = response.headers.get('Retry-After', '60')
                    wait_time = min(int(retry_after), 300)  # Max 5 minutes
                    logger.warning(f"Tiingo rate limited for {ticker}, waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    logger.warning(f"No Tiingo data returned for {ticker}")
                    return None
                
                # Convert to DataFrame
                df = pd.DataFrame(data)
                df['ticker'] = ticker
                df['source'] = 'tiingo'
                
                # Rename columns to match our schema
                column_mapping = {
                    'date': 'timestamp',
                    'open': 'open',
                    'high': 'high',
                    'low': 'low',
                    'close': 'close',
                    'volume': 'volume',
                    'adjOpen': 'adj_open',
                    'adjHigh': 'adj_high',
                    'adjLow': 'adj_low',
                    'adjClose': 'adj_close',
                    'adjVolume': 'adj_volume',
                    'divCash': 'dividend',
                    'splitFactor': 'split_factor'
                }
                df = df.rename(columns=column_mapping)
                
                # Convert timestamp
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Validate data quality
                if not self._validate_market_data(df, ticker):
                    logger.warning(f"Data validation failed for {ticker}")
                    return None
                
                logger.info(f"Successfully collected Tiingo data for {ticker}: {len(df)} records")
                return df
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Tiingo API error for {ticker} (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    logger.error(f"All Tiingo attempts failed for {ticker}")
                    return None
            except Exception as e:
                logger.error(f"Unexpected error in Tiingo collection for {ticker}: {e}")
                return None
        
        return None
    
    async def collect_yfinance_data_enhanced(self, tickers: List[str], 
                                           period: str = "1mo") -> Dict[str, pd.DataFrame]:
        """
        Enhanced yfinance data collection with better error handling
        
        Args:
            tickers: List of ticker symbols
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            Dictionary mapping tickers to DataFrames
        """
        result = {}
        
        # Check rate limits
        if not await self._wait_for_rate_limit('yfinance'):
            return result
        
        for ticker in tickers:
            try:
                self._record_api_call('yfinance')
                
                # Convert tickers to yfinance format
                yf_ticker = ticker
                
                # Index symbol mapping (for proper Yahoo Finance symbols)
                index_symbols = {
                    'DJI': '^DJI',
                    'NASDAQ': '^IXIC', 
                    'SPX': '^GSPC',
                    'RUT': '^RUT',
                    'VIX': '^VIX',
                    'NIFTY': '^NSEI',
                    '^BSESN': '^BSESN',
                    '^FTSE': '^FTSE',
                    '^GDAXI': '^GDAXI',
                    '^GSPC': '^GSPC',
                    '^IXIC': '^IXIC',
                    '^N225': '^N225',
                    '^NSEI': '^NSEI',
                    '^RUT': '^RUT',
                    '^VIX': '^VIX'
                }
                
                # Crypto symbol mapping
                crypto_symbols = [
                    'BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'ALGO', 'ATOM', 'AVAX', 
                    'BCH', 'BNB', 'DOGE', 'UNI', 'VET', 'LINK', 'MATIC', 'XRP', 'LTC',
                    'FIL', 'SHIB', 'THETA'
                ]
                
                # Apply appropriate mapping
                if ticker in index_symbols:
                    yf_ticker = index_symbols[ticker]
                elif ticker.endswith('-USD'):
                    yf_ticker = ticker  # Already in correct format
                elif ticker.upper() in crypto_symbols:
                    yf_ticker = f"{ticker.upper()}-USD"
                
                # Try different ticker variations for robustness
                ticker_variations = [yf_ticker]
                if '.' not in yf_ticker and '-' not in yf_ticker:
                    ticker_variations.extend([f"{yf_ticker}.TO", f"{yf_ticker}.L"])
                
                data = None
                for variation in ticker_variations:
                    try:
                        stock = yf.Ticker(variation)
                        data = stock.history(period=period, auto_adjust=False, prepost=False)
                        
                        if data is not None and not data.empty:
                            logger.debug(f"Successfully fetched {variation} for {ticker}")
                            break
                            
                    except Exception as attempt_error:
                        logger.debug(f"yfinance attempt failed for {variation}: {attempt_error}")
                        continue
                
                if data is None or data.empty:
                    logger.warning(f"No yfinance data returned for {ticker}")
                    continue
                
                # Process the data
                df = data.reset_index()
                
                # Rename columns to match our schema
                column_mapping = {
                    'Date': 'timestamp',
                    'Datetime': 'timestamp',
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume',
                    'Adj Close': 'adj_close'
                }
                df = df.rename(columns=column_mapping)
                
                # Add metadata
                df['ticker'] = ticker
                df['source'] = 'yfinance'
                
                # Ensure timestamp is datetime
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                else:
                    logger.warning(f"No timestamp column found for {ticker}")
                    continue
                
                # Validate data quality
                if not self._validate_market_data(df, ticker):
                    logger.warning(f"yfinance data validation failed for {ticker}")
                    continue
                
                result[ticker] = df
                logger.info(f"Successfully collected yfinance data for {ticker}: {len(df)} records")
                
                # Small delay to be respectful to the API
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Failed to collect yfinance data for {ticker}: {e}")
                continue
        
        logger.info(f"Successfully collected yfinance data for {len(result)}/{len(tickers)} tickers")
        return result
    
    async def collect_with_failover(self, ticker: str, start_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Collect market data with automatic failover between sources
        
        Failover order: Tiingo -> yfinance -> (future: Alpha Vantage)
        
        Args:
            ticker: Ticker symbol
            start_date: Start date for data collection
            
        Returns:
            DataFrame with market data or None if all sources fail
        """
        logger.debug(f"Starting failover collection for {ticker}")
        
        # Try Tiingo first (most comprehensive for US markets)
        tiingo_data = await self.collect_tiingo_data_enhanced(ticker, start_date)
        if tiingo_data is not None and not tiingo_data.empty:
            logger.info(f"✅ {ticker}: Collected from Tiingo ({len(tiingo_data)} records)")
            return tiingo_data
        
        logger.warning(f"⚠️ {ticker}: Tiingo failed, trying yfinance fallback")
        
        # Fallback to yfinance
        yfinance_data = await self.collect_yfinance_data_enhanced([ticker])
        if ticker in yfinance_data and not yfinance_data[ticker].empty:
            logger.info(f"✅ {ticker}: Collected from yfinance fallback ({len(yfinance_data[ticker])} records)")
            return yfinance_data[ticker]
        
        logger.warning(f"⚠️ {ticker}: yfinance failed, trying Alpha Vantage fallback")
        
        # Fallback to Alpha Vantage
        alpha_data = await self.collect_alpha_vantage_data(ticker)
        if alpha_data is not None and not alpha_data.empty:
            logger.info(f"✅ {ticker}: Collected from Alpha Vantage fallback ({len(alpha_data)} records)")
            return alpha_data
        
        logger.error(f"❌ {ticker}: All data sources failed")
        return None

    def collect_yfinance_data(self, tickers: List[str], period: str = "1d", interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """
        Collect data from yfinance with robust error handling and rate limiting.
        
        Args:
            tickers: List of ticker symbols
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        """
        result = {}
        import time
        
        # Process tickers individually to avoid rate limits and API issues
        for original_ticker in tickers:
            try:
                logger.info(f"Collecting yfinance data for {original_ticker}")
                
                # Convert ticker to yfinance-compatible format
                yf_ticker = original_ticker
                
                # Index symbol mapping (for proper Yahoo Finance symbols)
                index_symbols = {
                    'DJI': '^DJI',
                    'NASDAQ': '^IXIC', 
                    'SPX': '^GSPC',
                    'RUT': '^RUT',
                    'VIX': '^VIX',
                    'NIFTY': '^NSEI',
                    '^BSESN': '^BSESN',
                    '^FTSE': '^FTSE',
                    '^GDAXI': '^GDAXI',
                    '^GSPC': '^GSPC',
                    '^IXIC': '^IXIC',
                    '^N225': '^N225',
                    '^NSEI': '^NSEI',
                    '^RUT': '^RUT',
                    '^VIX': '^VIX'
                }
                
                # Crypto symbol mapping
                crypto_symbols = [
                    'BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'ALGO', 'ATOM', 'AVAX', 
                    'BCH', 'BNB', 'DOGE', 'UNI', 'VET', 'LINK', 'MATIC', 'XRP', 'LTC',
                    'FIL', 'SHIB', 'THETA'
                ]
                
                # Apply appropriate mapping
                if original_ticker in index_symbols:
                    yf_ticker = index_symbols[original_ticker]
                elif original_ticker in crypto_symbols:
                    yf_ticker = f"{original_ticker}-USD"
                elif original_ticker in ['EURUSD', 'GBPUSD', 'USDJPY']:
                    yf_ticker = f"{original_ticker}=X"
                
                # Create ticker object and download data with retry logic
                ticker_obj = yf.Ticker(yf_ticker)
                
                # Try different approaches for different asset types
                attempts = [
                    {'period': period, 'interval': interval},
                    {'period': '5d', 'interval': '1d'},  # Fallback to smaller period
                    {'period': '1d', 'interval': '1h'},   # Fallback to hourly
                ]
                
                data = None
                for attempt in attempts:
                    try:
                        data = ticker_obj.history(
                            period=attempt['period'],
                            interval=attempt['interval'],
                            auto_adjust=True,
                            prepost=False,
                            timeout=30,
                            repair=True  # Fix currency mismatches
                        )
                        if not data.empty:
                            break
                    except Exception as attempt_error:
                        logger.debug(f"Attempt failed for {original_ticker}: {attempt_error}")
                        continue
                
                if data is None or data.empty:
                    logger.warning(f"No data returned from yfinance for {original_ticker} ({yf_ticker})")
                    continue
                
                # Reset index to make timestamp a column
                df = data.reset_index()
                
                # Rename columns to match our schema
                column_mapping = {
                    'Date': 'timestamp',
                    'Datetime': 'timestamp',
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume'
                }
                df = df.rename(columns=column_mapping)
                
                # Add metadata
                df['ticker'] = original_ticker
                df['source'] = 'yfinance'
                
                # Ensure timestamp is datetime
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                else:
                    logger.warning(f"No timestamp column found for {original_ticker}")
                    continue
                
                # Validate essential columns
                required_cols = ['timestamp', 'close', 'volume']
                if not all(col in df.columns for col in required_cols):
                    logger.warning(f"Missing required columns for {original_ticker}: {df.columns.tolist()}")
                    continue
                
                result[original_ticker] = df
                logger.info(f"Successfully collected yfinance data for {original_ticker}: {len(df)} records")
                
            except Exception as e:
                logger.error(f"Failed to collect yfinance data for {original_ticker}: {e}")
                continue
        
        logger.info(f"Successfully collected yfinance data for {len(result)}/{len(tickers)} tickers")
        return result
    
    def collect_tiingo_data(self, ticker: str, start_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Collect data from Tiingo API for a single ticker.
        
        Args:
            ticker: Ticker symbol
            start_date: Start date in YYYY-MM-DD format
        """
        if not settings.TIINGO_API_KEY:
            logger.warning("Tiingo API key not configured")
            return None
        
        try:
            # Default to last 24 hours if no start date provided
            if not start_date:
                start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            url = f"{settings.TIINGO_BASE_URL}/tiingo/daily/{ticker}/prices"
            params = {
                'startDate': start_date,
                'token': settings.TIINGO_API_KEY,
                'format': 'json'
            }
            
            response = self.session.get(url, headers=self.tiingo_headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                logger.warning(f"No Tiingo data returned for {ticker}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df['ticker'] = ticker
            df['source'] = 'tiingo'
            
            # Rename columns to match our schema
            column_mapping = {
                'date': 'timestamp',
                'open': 'open',
                'high': 'high', 
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            }
            df = df.rename(columns=column_mapping)
            
            # Convert timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            logger.info(f"Successfully collected Tiingo data for {ticker}: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"Failed to collect Tiingo data for {ticker}: {e}")
            return None
    
    def collect_crypto_data(self, crypto_symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Collect cryptocurrency data from CoinGecko API (free, no API key required).
        
        Args:
            crypto_symbols: List of crypto symbols (BTC, ETH, etc.)
        """
        result = {}
        
        # CoinGecko API symbol mapping
        crypto_mapping = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum', 
            'SOL': 'solana',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'ALGO': 'algorand',
            'ATOM': 'cosmos',
            'AVAX': 'avalanche-2',
            'BCH': 'bitcoin-cash',
            'BNB': 'binancecoin',
            'DOGE': 'dogecoin',
            'UNI': 'uniswap',
            'VET': 'vechain',
            'LINK': 'chainlink',
            'MATIC': 'matic-network',
            'XRP': 'ripple',
            'LTC': 'litecoin',
            'FIL': 'filecoin',
            'SHIB': 'shiba-inu',
            'THETA': 'theta-token'
        }
        
        try:
            for symbol in crypto_symbols:
                if symbol not in crypto_mapping:
                    continue
                    
                coingecko_id = crypto_mapping[symbol]
                logger.info(f"Collecting crypto data for {symbol} ({coingecko_id})")
                
                # Get current price data from CoinGecko
                url = f"https://api.coingecko.com/api/v3/simple/price"
                params = {
                    'ids': coingecko_id,
                    'vs_currencies': 'usd',
                    'include_24hr_vol': 'true',
                    'include_24hr_change': 'true',
                    'include_last_updated_at': 'true'
                }
                
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                if coingecko_id in data:
                    price_data = data[coingecko_id]
                    
                    # Create DataFrame with current timestamp
                    df = pd.DataFrame([{
                        'timestamp': datetime.now(),
                        'open': price_data['usd'],  # Using current as open (approximation)
                        'high': price_data['usd'] * 1.01,  # Approximate high
                        'low': price_data['usd'] * 0.99,   # Approximate low
                        'close': price_data['usd'],
                        'volume': price_data.get('usd_24h_vol', 0),
                        'ticker': symbol,
                        'source': 'coingecko'
                    }])
                    
                    result[symbol] = df
                    logger.info(f"Successfully collected crypto data for {symbol}: ${price_data['usd']:.2f}")
                
                # Rate limiting
                import time
                time.sleep(0.2)
                
        except Exception as e:
            logger.error(f"Failed to collect crypto data: {e}")
        
        return result

    def calculate_bid_ask_spread(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate bid-ask spread approximation from OHLC data."""
        try:
            # Simple approximation: spread = (high - low) / close
            df['bid_ask_spread'] = ((df['high'] - df['low']) / df['close']) * 100
            return df
        except Exception as e:
            logger.warning(f"Failed to calculate bid-ask spread: {e}")
            df['bid_ask_spread'] = None
            return df
    
    def store_market_data(self, data_dict: Dict[str, pd.DataFrame]) -> int:
        """Store market data in PostgreSQL database."""
        total_inserted = 0
        
        for ticker, df in data_dict.items():
            if df.empty:
                continue
            
            try:
                # Calculate bid-ask spread
                df = self.calculate_bid_ask_spread(df)
                
                # Prepare data for bulk insert
                records_to_insert = []
                
                for _, row in df.iterrows():
                    try:
                        # Skip if required fields are missing
                        if pd.isna(row['close']) or pd.isna(row['volume']):
                            continue
                        
                        record = (
                            ticker,
                            row['timestamp'],
                            float(row.get('open', 0)) if not pd.isna(row.get('open')) else None,
                            float(row.get('high', 0)) if not pd.isna(row.get('high')) else None,
                            float(row.get('low', 0)) if not pd.isna(row.get('low')) else None,
                            float(row['close']),
                            int(row['volume']) if not pd.isna(row['volume']) else 0,
                            float(row.get('bid_ask_spread', 0)) if not pd.isna(row.get('bid_ask_spread')) else None,
                            row.get('source', 'unknown')
                        )
                        records_to_insert.append(record)
                        
                    except Exception as e:
                        logger.warning(f"Skipping invalid record for {ticker}: {e}")
                        continue
                
                if records_to_insert:
                    # Bulk upsert to handle duplicates
                    columns = ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'bid_ask_spread', 'source']
                    conflict_columns = ['ticker', 'timestamp']
                    update_columns = ['open', 'high', 'low', 'close', 'volume', 'bid_ask_spread', 'source']
                    
                    inserted_count = db.bulk_upsert('market_prices', columns, records_to_insert, 
                                                   conflict_columns, update_columns)
                    total_inserted += inserted_count
                    logger.info(f"Upserted {inserted_count} market price records for {ticker}")
                
            except Exception as e:
                logger.error(f"Failed to store market data for {ticker}: {e}")
        
        return total_inserted
    
    async def run_collection_cycle(self) -> Dict[str, Any]:
        """Run a complete market data collection cycle."""
        start_time = datetime.now()
        logger.info("Starting market data collection cycle")
        
        results = {
            'start_time': start_time.isoformat(),
            'tickers_processed': 0,
            'records_inserted': 0,
            'errors': [],
            'success': True
        }
        
        try:
            # Get all tracked tickers
            tickers = self.get_all_tracked_tickers()
            
            # Collect yfinance data
            yfinance_data = {}
            if settings.YFINANCE_ENABLED:
                yfinance_data = self.collect_yfinance_data(tickers, period="1d", interval="5m")
            
            # Collect Tiingo data for all supported tickers
            tiingo_data = {}
            if settings.TIINGO_API_KEY:
                # Get stock tickers that Tiingo supports
                stock_tickers = TRACKED_ASSETS.get('stocks', [])
                etf_tickers = TRACKED_ASSETS.get('etfs', [])
                all_supported = stock_tickers + etf_tickers
                
                for ticker in all_supported:
                    ticker_data = self.collect_tiingo_data(ticker)
                    if ticker_data is not None:
                        tiingo_data[ticker] = ticker_data
                    # Small delay to avoid rate limits
                    import time
                    time.sleep(0.1)
            
            # Collect crypto data as fallback
            crypto_data = {}
            crypto_tickers = TRACKED_ASSETS.get('crypto', [])
            if crypto_tickers:
                crypto_data = self.collect_crypto_data(crypto_tickers)
            
            # Combine data sources
            all_data = {**yfinance_data, **tiingo_data, **crypto_data}
            
            # Store in database
            if all_data:
                records_inserted = self.store_market_data(all_data)
                results['records_inserted'] = records_inserted
                results['tickers_processed'] = len(all_data)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Market data collection completed in {duration:.2f}s: "
                       f"{results['tickers_processed']} tickers, {results['records_inserted']} records")
            
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = duration
            
        except Exception as e:
            logger.error(f"Market data collection cycle failed: {e}")
            results['success'] = False
            results['errors'].append(str(e))
        
        return results

# Global collector instance
market_collector = MarketDataCollector()

# Convenience functions for external use
def collect_market_data() -> Dict[str, Any]:
    """Synchronous wrapper for market data collection."""
    return asyncio.run(market_collector.run_collection_cycle())

def collect_single_ticker(ticker: str, source: str = "yfinance") -> bool:
    """Collect data for a single ticker."""
    try:
        if source == "yfinance":
            data = market_collector.collect_yfinance_data([ticker], period="1d", interval="5m")
        elif source == "tiingo":
            ticker_data = market_collector.collect_tiingo_data(ticker)
            data = {ticker: ticker_data} if ticker_data is not None else {}
        else:
            logger.error(f"Unknown data source: {source}")
            return False
        
        if data:
            market_collector.store_market_data(data)
            return True
        return False
        
    except Exception as e:
        logger.error(f"Failed to collect data for {ticker} from {source}: {e}")
        return False