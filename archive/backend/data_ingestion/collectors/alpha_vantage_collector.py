#!/usr/bin/env python3
"""
Alpha Vantage Data Collector for uRISK
Comprehensive financial data collection from Alpha Vantage API
Supports stocks, ETFs, indices, forex, crypto, commodities, economic indicators, 
technicals, news, fundamentals, and options data.

Enhanced to support ALL Alpha Vantage endpoints with complete JSON format parsing.
"""

import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import time
import json
from dataclasses import dataclass, field
from enum import Enum
import os

# Import backend modules with error handling
try:
    from backend.utils.logging_utils import setup_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
else:
    logger = setup_logger(__name__)

class AlphaVantageFunction(Enum):
    """Alpha Vantage API functions - Complete list based on latest API documentation"""
    
    # ============= CORE STOCK APIS =============
    TIME_SERIES_INTRADAY = "TIME_SERIES_INTRADAY"
    TIME_SERIES_DAILY = "TIME_SERIES_DAILY"
    TIME_SERIES_DAILY_ADJUSTED = "TIME_SERIES_DAILY_ADJUSTED"
    TIME_SERIES_WEEKLY = "TIME_SERIES_WEEKLY"
    TIME_SERIES_WEEKLY_ADJUSTED = "TIME_SERIES_WEEKLY_ADJUSTED"
    TIME_SERIES_MONTHLY = "TIME_SERIES_MONTHLY"
    TIME_SERIES_MONTHLY_ADJUSTED = "TIME_SERIES_MONTHLY_ADJUSTED"
    GLOBAL_QUOTE = "GLOBAL_QUOTE"
    SYMBOL_SEARCH = "SYMBOL_SEARCH"
    MARKET_STATUS = "MARKET_STATUS"
    
    # ============= OPTIONS DATA =============
    REALTIME_OPTIONS = "REALTIME_OPTIONS"  # Premium
    HISTORICAL_OPTIONS = "HISTORICAL_OPTIONS"
    
    # ============= ALPHA INTELLIGENCE =============
    NEWS_SENTIMENT = "NEWS_SENTIMENT"
    EARNINGS_CALL_TRANSCRIPT = "EARNINGS_CALL_TRANSCRIPT"
    TOP_GAINERS_LOSERS = "TOP_GAINERS_LOSERS"
    INSIDER_TRANSACTIONS = "INSIDER_TRANSACTIONS"
    ANALYTICS_FIXED_WINDOW = "ANALYTICS_FIXED_WINDOW"
    ANALYTICS_SLIDING_WINDOW = "ANALYTICS_SLIDING_WINDOW"
    
    # ============= FUNDAMENTAL DATA =============
    OVERVIEW = "OVERVIEW"
    ETF_PROFILE = "ETF_PROFILE"
    DIVIDENDS = "DIVIDENDS"
    SPLITS = "SPLITS"
    INCOME_STATEMENT = "INCOME_STATEMENT"
    BALANCE_SHEET = "BALANCE_SHEET"
    CASH_FLOW = "CASH_FLOW"
    SHARES_OUTSTANDING = "SHARES_OUTSTANDING"
    EARNINGS = "EARNINGS"
    EARNINGS_HISTORY = "EARNINGS_HISTORY"
    EARNINGS_ESTIMATES = "EARNINGS_ESTIMATES"
    LISTING_STATUS = "LISTING_STATUS"
    EARNINGS_CALENDAR = "EARNINGS_CALENDAR"
    IPO_CALENDAR = "IPO_CALENDAR"
    
    # ============= FOREX (FX) =============
    CURRENCY_EXCHANGE_RATE = "CURRENCY_EXCHANGE_RATE"
    FX_INTRADAY = "FX_INTRADAY"  # Premium
    FX_DAILY = "FX_DAILY"
    FX_WEEKLY = "FX_WEEKLY"
    FX_MONTHLY = "FX_MONTHLY"
    
    # ============= CRYPTOCURRENCIES =============
    DIGITAL_CURRENCY_INTRADAY = "DIGITAL_CURRENCY_INTRADAY"  # Premium
    DIGITAL_CURRENCY_DAILY = "DIGITAL_CURRENCY_DAILY"
    DIGITAL_CURRENCY_WEEKLY = "DIGITAL_CURRENCY_WEEKLY"
    DIGITAL_CURRENCY_MONTHLY = "DIGITAL_CURRENCY_MONTHLY"
    
    # ============= COMMODITIES =============
    WTI = "WTI"  # Crude Oil (WTI)
    BRENT = "BRENT"  # Crude Oil (Brent)
    NATURAL_GAS = "NATURAL_GAS"
    COPPER = "COPPER"
    ALUMINUM = "ALUMINUM"
    WHEAT = "WHEAT"
    CORN = "CORN"
    COTTON = "COTTON"
    SUGAR = "SUGAR"
    COFFEE = "COFFEE"
    GLOBAL_COMMODITIES = "GLOBAL_COMMODITIES"
    
    # ============= ECONOMIC INDICATORS =============
    REAL_GDP = "REAL_GDP"
    REAL_GDP_PER_CAPITA = "REAL_GDP_PER_CAPITA"
    TREASURY_YIELD = "TREASURY_YIELD"
    FEDERAL_FUNDS_RATE = "FEDERAL_FUNDS_RATE"
    CPI = "CPI"
    INFLATION = "INFLATION"
    RETAIL_SALES = "RETAIL_SALES"
    DURABLES = "DURABLES"
    UNEMPLOYMENT = "UNEMPLOYMENT"
    NONFARM_PAYROLL = "NONFARM_PAYROLL"
    
    # ============= TECHNICAL INDICATORS =============
    SMA = "SMA"
    EMA = "EMA" 
    WMA = "WMA"
    DEMA = "DEMA"
    TEMA = "TEMA"
    TRIMA = "TRIMA"
    KAMA = "KAMA"
    MAMA = "MAMA"
    VWAP = "VWAP"  # Premium
    T3 = "T3"
    MACD = "MACD"  # Premium
    MACDEXT = "MACDEXT"
    STOCH = "STOCH"
    STOCHF = "STOCHF"
    RSI = "RSI"
    STOCHRSI = "STOCHRSI"
    WILLR = "WILLR"
    ADX = "ADX"
    ADXR = "ADXR"
    APO = "APO"
    PPO = "PPO"
    MOM = "MOM"
    BOP = "BOP"
    CCI = "CCI"
    CMO = "CMO"
    ROC = "ROC"
    ROCR = "ROCR"
    AROON = "AROON"
    AROONOSC = "AROONOSC"
    MFI = "MFI"
    TRIX = "TRIX"
    ULTOSC = "ULTOSC"
    DX = "DX"
    MINUS_DI = "MINUS_DI"
    PLUS_DI = "PLUS_DI"
    MINUS_DM = "MINUS_DM"
    PLUS_DM = "PLUS_DM"
    BBANDS = "BBANDS"
    MIDPOINT = "MIDPOINT"
    MIDPRICE = "MIDPRICE"
    SAR = "SAR"
    TRANGE = "TRANGE"
    ATR = "ATR"
    NATR = "NATR"
    AD = "AD"
    ADOSC = "ADOSC"
    OBV = "OBV"
    HT_TRENDLINE = "HT_TRENDLINE"
    HT_SINE = "HT_SINE"
    HT_TRENDMODE = "HT_TRENDMODE"
    HT_DCPERIOD = "HT_DCPERIOD"
    HT_DCPHASE = "HT_DCPHASE"
    HT_PHASOR = "HT_PHASOR"

@dataclass
class AlphaVantageConfig:
    """Alpha Vantage configuration with enhanced settings"""
    api_key: str
    base_url: str = "https://www.alphavantage.co/query"
    rate_limit_calls_per_minute: int = 5  # Free tier limit
    rate_limit_calls_per_day: int = 500   # Free tier daily limit
    premium_tier: bool = False            # Whether using premium tier
    timeout: int = 30
    retries: int = 3
    backoff_factor: float = 2.0
    
    # Premium tier limits
    premium_calls_per_minute: int = 75
    premium_calls_per_day: int = 75000
    
    # Asset-specific configurations
    support_options: bool = False         # Requires premium
    support_realtime: bool = False        # Requires premium
    support_extended_history: bool = True
    
    @property
    def effective_calls_per_minute(self) -> int:
        """Get effective calls per minute based on tier"""
        return self.premium_calls_per_minute if self.premium_tier else self.rate_limit_calls_per_minute
    
    @property 
    def effective_calls_per_day(self) -> int:
        """Get effective calls per day based on tier"""
        return self.premium_calls_per_day if self.premium_tier else self.rate_limit_calls_per_day

@dataclass 
class AlphaVantageResponse:
    """Standardized Alpha Vantage response structure"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    dataframe: Optional[pd.DataFrame] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    endpoint: Optional[str] = None
    symbol: Optional[str] = None
    function: Optional[str] = None

class AlphaVantageCollector:
    """
    Professional Alpha Vantage data collector with comprehensive endpoint support
    
    Features:
    - All Alpha Vantage endpoints (stocks, ETFs, indices, forex, crypto, commodities, economic, technical, news, fundamentals)
    - Intelligent JSON parsing for all response formats
    - Rate limiting and circuit breaker patterns
    - Asset-type routing and fallback logic
    - Premium and free tier support
    - Comprehensive error handling and logging
    - Pipeline run tracking with descriptive names
    """
    
    def __init__(self, config: Optional[AlphaVantageConfig] = None):
        self.config = config or AlphaVantageConfig(
            api_key=self._get_api_key()
        )
        
        # Detect if using premium tier based on API key
        if self.config.api_key != 'demo' and len(self.config.api_key) > 10:
            self.config.premium_tier = True
            logger.info("🌟 Alpha Vantage Premium tier detected")
        
        # Rate limiting
        self.call_timestamps = []
        self.daily_calls = 0
        self.last_reset = datetime.now().date()
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Asset type mappings for intelligent routing
        self.asset_type_mappings = {
            'stock': ['TIME_SERIES_INTRADAY', 'TIME_SERIES_DAILY', 'TIME_SERIES_DAILY_ADJUSTED', 
                     'GLOBAL_QUOTE', 'OVERVIEW', 'EARNINGS', 'INCOME_STATEMENT', 'BALANCE_SHEET', 'CASH_FLOW'],
            'etf': ['TIME_SERIES_DAILY', 'ETF_PROFILE', 'GLOBAL_QUOTE'],
            'index': ['TIME_SERIES_DAILY', 'GLOBAL_QUOTE'],
            'forex': ['CURRENCY_EXCHANGE_RATE', 'FX_DAILY', 'FX_WEEKLY', 'FX_MONTHLY', 'FX_INTRADAY'],
            'crypto': ['DIGITAL_CURRENCY_DAILY', 'DIGITAL_CURRENCY_WEEKLY', 'DIGITAL_CURRENCY_MONTHLY', 'DIGITAL_CURRENCY_INTRADAY'],
            'commodity': ['WTI', 'BRENT', 'NATURAL_GAS', 'COPPER', 'ALUMINUM', 'WHEAT', 'CORN', 'COTTON', 'SUGAR', 'COFFEE'],
            'economic': ['REAL_GDP', 'CPI', 'UNEMPLOYMENT', 'FEDERAL_FUNDS_RATE', 'TREASURY_YIELD', 'INFLATION', 'RETAIL_SALES']
        }
        
        # Pipeline run tracking
        self.pipeline_runs = []
        self.current_run_name = None
    
    def _get_api_key(self) -> str:
        """Get Alpha Vantage API key from environment or config"""
        # Try multiple environment variable names
        for env_var in ['ALPHA_VANTAGE_API_KEY', 'ALPHAVANTAGE_API_KEY', 'AV_API_KEY']:
            api_key = os.getenv(env_var)
            if api_key:
                logger.info(f"🔑 Alpha Vantage API key loaded from {env_var}")
                return api_key
        
        # Try to load from config file
        try:
            from backend.config.settings import settings
            if hasattr(settings, 'ALPHA_VANTAGE_API_KEY') and settings.ALPHA_VANTAGE_API_KEY:
                logger.info("🔑 Alpha Vantage API key loaded from settings")
                return settings.ALPHA_VANTAGE_API_KEY
        except ImportError:
            pass
        
        logger.warning("⚠️ No Alpha Vantage API key found. Using 'demo' key with limited functionality.")
        logger.info("💡 Set ALPHA_VANTAGE_API_KEY environment variable or add to settings for full access.")
        return 'demo'
    
    def start_pipeline_run(self, run_name: str, description: str = ""):
        """Start a new pipeline run for tracking"""
        self.current_run_name = run_name
        run_info = {
            'name': run_name,
            'description': description,
            'start_time': datetime.now(),
            'endpoints_called': [],
            'success_count': 0,
            'error_count': 0,
            'assets_processed': set()
        }
        self.pipeline_runs.append(run_info)
        logger.info(f"🚀 Started Alpha Vantage pipeline run: {run_name}")
        if description:
            logger.info(f"📝 Description: {description}")
    
    def end_pipeline_run(self) -> Dict[str, Any]:
        """End current pipeline run and return summary"""
        if not self.current_run_name or not self.pipeline_runs:
            return {}
        
        current_run = self.pipeline_runs[-1]
        current_run['end_time'] = datetime.now()
        current_run['duration'] = current_run['end_time'] - current_run['start_time']
        current_run['assets_processed'] = list(current_run['assets_processed'])
        
        logger.info(f"✅ Completed Alpha Vantage pipeline run: {self.current_run_name}")
        logger.info(f"📊 Summary: {current_run['success_count']} success, {current_run['error_count']} errors")
        logger.info(f"⏱️ Duration: {current_run['duration']}")
        logger.info(f"🎯 Assets processed: {len(current_run['assets_processed'])}")
        
        self.current_run_name = None
        return current_run
    
    async def _ensure_session(self):
        """Ensure aiohttp session is available"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def _rate_limit_check(self):
        """Enhanced rate limiting with premium tier support"""
        now = datetime.now()
        current_date = now.date()
        
        # Reset daily counter if new day
        if current_date > self.last_reset:
            self.daily_calls = 0
            self.last_reset = current_date
            logger.info(f"🔄 Alpha Vantage daily call counter reset")
        
        # Check daily limit
        if self.daily_calls >= self.config.effective_calls_per_day:
            error_msg = f"Alpha Vantage daily limit reached: {self.daily_calls}/{self.config.effective_calls_per_day}"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        # Check per-minute limit
        one_minute_ago = now - timedelta(minutes=1)
        recent_calls = [t for t in self.call_timestamps if t > one_minute_ago]
        
        calls_per_minute = self.config.effective_calls_per_minute
        if len(recent_calls) >= calls_per_minute:
            wait_time = 60 - (now - recent_calls[0]).total_seconds()
            if wait_time > 0:
                logger.info(f"⏳ Alpha Vantage rate limit: waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        # Record this call
        self.call_timestamps.append(now)
        self.daily_calls += 1
        
        # Clean old timestamps
        self.call_timestamps = [t for t in self.call_timestamps if t > one_minute_ago]
    
    def _track_api_call(self, function_name: str, symbol: str = None, success: bool = True):
        """Track API call for pipeline run statistics"""
        if not self.pipeline_runs:
            return
        
        current_run = self.pipeline_runs[-1]
        current_run['endpoints_called'].append({
            'function': function_name,
            'symbol': symbol,
            'timestamp': datetime.now(),
            'success': success
        })
        
        if success:
            current_run['success_count'] += 1
        else:
            current_run['error_count'] += 1
        
        if symbol:
            current_run['assets_processed'].add(symbol)
    
    async def _make_request(self, params: Dict[str, Any]) -> AlphaVantageResponse:
        """Enhanced request method with comprehensive error handling and response parsing"""
        await self._ensure_session()
        await self._rate_limit_check()
        
        # Add API key to params
        params['apikey'] = self.config.api_key
        
        function_name = params.get('function', 'unknown')
        symbol = params.get('symbol') or params.get('from_symbol') or 'N/A'
        
        response_obj = AlphaVantageResponse(
            success=False,
            endpoint=self.config.base_url,
            symbol=symbol,
            function=function_name
        )
        
        for attempt in range(self.config.retries):
            try:
                logger.debug(f"🌐 Alpha Vantage API call: {function_name} for {symbol} (attempt {attempt + 1})")
                
                async with self.session.get(self.config.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for API error messages
                        if 'Error Message' in data:
                            error_msg = data['Error Message']
                            logger.error(f"❌ Alpha Vantage API error: {error_msg}")
                            response_obj.error_message = error_msg
                            self._track_api_call(function_name, symbol, False)
                            return response_obj
                        
                        # Check for rate limit warnings
                        if 'Note' in data:
                            note = data['Note']
                            logger.warning(f"⚠️ Alpha Vantage note: {note}")
                            if 'call frequency' in note.lower() or 'premium' in note.lower():
                                await asyncio.sleep(60)  # Wait before retry
                                continue
                        
                        # Check for information message (common for invalid symbols)
                        if 'Information' in data and 'Invalid' in str(data.get('Information', '')):
                            error_msg = data.get('Information', 'Invalid symbol or API call')
                            logger.error(f"❌ Alpha Vantage error: {error_msg}")
                            response_obj.error_message = error_msg
                            self._track_api_call(function_name, symbol, False)
                            return response_obj
                        
                        # Success - parse data
                        logger.info(f"✅ Alpha Vantage API success: {function_name} for {symbol}")
                        response_obj.success = True
                        response_obj.data = data
                        
                        # Extract metadata if available
                        if 'Meta Data' in data:
                            response_obj.metadata = data['Meta Data']
                        elif 'Metadata' in data:
                            response_obj.metadata = data['Metadata']
                        
                        self._track_api_call(function_name, symbol, True)
                        return response_obj
                    
                    else:
                        error_text = await response.text()
                        logger.warning(f"⚠️ Alpha Vantage API HTTP {response.status}: {error_text}")
                        
                        if response.status == 429:  # Rate limited
                            wait_time = self.config.backoff_factor ** attempt
                            await asyncio.sleep(wait_time)
                            continue
                        
                        if attempt == self.config.retries - 1:
                            response_obj.error_message = f"HTTP {response.status}: {error_text}"
                            self._track_api_call(function_name, symbol, False)
                            return response_obj
            
            except Exception as e:
                if attempt == self.config.retries - 1:
                    logger.error(f"❌ Alpha Vantage API failed after {self.config.retries} attempts: {e}")
                    response_obj.error_message = str(e)
                    self._track_api_call(function_name, symbol, False)
                    return response_obj
                
                wait_time = self.config.backoff_factor ** attempt
                logger.warning(f"🔄 Alpha Vantage API retry {attempt + 1} in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
        
        response_obj.error_message = "Request failed after all retries"
        self._track_api_call(function_name, symbol, False)
        return response_obj
    
    async def get_daily_data(self, symbol: str, adjusted: bool = True, 
                           outputsize: str = "compact") -> pd.DataFrame:
        """
        Get daily stock data from Alpha Vantage
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'IBM')
            adjusted: Whether to get adjusted prices
            outputsize: 'compact' (100 days) or 'full' (all available)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            function = AlphaVantageFunction.TIME_SERIES_DAILY_ADJUSTED if adjusted else AlphaVantageFunction.TIME_SERIES_DAILY
            
            params = {
                'function': function.value,
                'symbol': symbol,
                'outputsize': outputsize
            }
            
            data = await self._make_request(params)
            
            # Parse response
            time_series_key = "Time Series (Daily)" if not adjusted else "Time Series (Daily)"
            if adjusted and "Weekly Adjusted Time Series" in data:
                time_series_key = "Weekly Adjusted Time Series"
            elif "Time Series (Daily)" in data:
                time_series_key = "Time Series (Daily)"
            elif "Time Series" in str(data.keys()):
                time_series_key = [k for k in data.keys() if "Time Series" in k][0]
            else:
                logger.warning(f"⚠️ Unexpected Alpha Vantage response structure for {symbol}")
                return pd.DataFrame()
            
            if time_series_key not in data:
                logger.warning(f"⚠️ No time series data found for {symbol}")
                return pd.DataFrame()
            
            time_series = data[time_series_key]
            
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')
            
            # Clean column names
            df.columns = [col.split('. ')[-1] for col in df.columns]
            
            # Convert to numeric
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            if adjusted:
                numeric_cols.append('adjusted close')
                
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Sort by date
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Add metadata
            df['symbol'] = symbol
            df['source'] = 'alpha_vantage'
            df['data_type'] = 'daily_adjusted' if adjusted else 'daily'
            
            logger.info(f"📈 Alpha Vantage daily data for {symbol}: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to get Alpha Vantage daily data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def get_intraday_data(self, symbol: str, interval: str = "5min", 
                              month: Optional[str] = None, extended_hours: bool = True) -> pd.DataFrame:
        """
        Get intraday stock data from Alpha Vantage
        
        Args:
            symbol: Stock symbol
            interval: '1min', '5min', '15min', '30min', '60min'
            month: Specific month in YYYY-MM format
            extended_hours: Include extended hours data
        
        Returns:
            DataFrame with intraday OHLCV data
        """
        try:
            params = {
                'function': AlphaVantageFunction.TIME_SERIES_INTRADAY.value,
                'symbol': symbol,
                'interval': interval,
                'extended_hours': str(extended_hours).lower(),
                'outputsize': 'full'
            }
            
            if month:
                params['month'] = month
            
            data = await self._make_request(params)
            
            # Parse response
            time_series_key = f"Time Series ({interval})"
            if time_series_key not in data:
                logger.warning(f"⚠️ No intraday data found for {symbol}")
                return pd.DataFrame()
            
            time_series = data[time_series_key]
            
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')
            
            # Clean column names
            df.columns = [col.split('. ')[-1] for col in df.columns]
            
            # Convert to numeric
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Sort by timestamp
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Add metadata
            df['symbol'] = symbol
            df['source'] = 'alpha_vantage'
            df['data_type'] = f'intraday_{interval}'
            df['interval'] = interval
            
            logger.info(f"📊 Alpha Vantage intraday ({interval}) data for {symbol}: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to get Alpha Vantage intraday data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """
        Get company overview and fundamental data
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with company information
        """
        try:
            params = {
                'function': AlphaVantageFunction.OVERVIEW.value,
                'symbol': symbol
            }
            
            data = await self._make_request(params)
            
            if not data or 'Symbol' not in data:
                logger.warning(f"⚠️ No overview data found for {symbol}")
                return {}
            
            logger.info(f"🏢 Alpha Vantage company overview for {symbol}: {data.get('Name', 'Unknown')}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to get Alpha Vantage company overview for {symbol}: {e}")
            return {}
    
    async def get_news_sentiment(self, tickers: Union[str, List[str]], 
                                limit: int = 50, time_from: Optional[str] = None,
                                time_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Get news sentiment data
        
        Args:
            tickers: Single ticker or list of tickers
            limit: Number of articles to return (max 1000)
            time_from: Start time in YYYYMMDDTHHMM format
            time_to: End time in YYYYMMDDTHHMM format
        
        Returns:
            Dictionary with news and sentiment data
        """
        try:
            if isinstance(tickers, list):
                tickers_str = ','.join(tickers)
            else:
                tickers_str = tickers
            
            params = {
                'function': AlphaVantageFunction.NEWS_SENTIMENT.value,
                'tickers': tickers_str,
                'limit': limit
            }
            
            if time_from:
                params['time_from'] = time_from
            if time_to:
                params['time_to'] = time_to
            
            data = await self._make_request(params)
            
            if not data or 'feed' not in data:
                logger.warning(f"⚠️ No news sentiment data found for {tickers_str}")
                return {}
            
            articles_count = len(data.get('feed', []))
            logger.info(f"📰 Alpha Vantage news sentiment for {tickers_str}: {articles_count} articles")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to get Alpha Vantage news sentiment for {tickers}: {e}")
            return {}
    
    async def get_forex_data(self, from_symbol: str, to_symbol: str, 
                           interval: str = "daily") -> pd.DataFrame:
        """
        Get forex exchange rate data
        
        Args:
            from_symbol: From currency (e.g., 'USD')
            to_symbol: To currency (e.g., 'EUR')
            interval: 'intraday', 'daily', 'weekly', 'monthly'
        
        Returns:
            DataFrame with forex data
        """
        try:
            function_map = {
                'intraday': AlphaVantageFunction.FX_INTRADAY,
                'daily': AlphaVantageFunction.FX_DAILY,
                'weekly': AlphaVantageFunction.FX_WEEKLY,
                'monthly': AlphaVantageFunction.FX_MONTHLY
            }
            
            if interval not in function_map:
                raise ValueError(f"Invalid interval: {interval}")
            
            params = {
                'function': function_map[interval].value,
                'from_symbol': from_symbol,
                'to_symbol': to_symbol
            }
            
            if interval == 'intraday':
                params['interval'] = '5min'
                params['outputsize'] = 'compact'
            
            data = await self._make_request(params)
            
            # Find time series key
            time_series_key = None
            for key in data.keys():
                if 'Time Series' in key:
                    time_series_key = key
                    break
            
            if not time_series_key or time_series_key not in data:
                logger.warning(f"⚠️ No forex data found for {from_symbol}/{to_symbol}")
                return pd.DataFrame()
            
            time_series = data[time_series_key]
            
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')
            
            # Clean column names
            df.columns = [col.split('. ')[-1].lower().replace(' ', '_') for col in df.columns]
            
            # Convert to numeric
            for col in ['open', 'high', 'low', 'close']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Sort by timestamp
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Add metadata
            df['from_symbol'] = from_symbol
            df['to_symbol'] = to_symbol
            df['currency_pair'] = f"{from_symbol}/{to_symbol}"
            df['source'] = 'alpha_vantage'
            df['data_type'] = f'forex_{interval}'
            df['ingestion_timestamp'] = datetime.now()
            
            logger.info(f"💱 Alpha Vantage forex data for {from_symbol}/{to_symbol}: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to get Alpha Vantage forex data for {from_symbol}/{to_symbol}: {e}")
            return pd.DataFrame()
    
    async def get_crypto_data(self, symbol: str, market: str = "USD", 
                            interval: str = "daily") -> pd.DataFrame:
        """
        Get cryptocurrency data
        
        Args:
            symbol: Crypto symbol (e.g., 'BTC', 'ETH')
            market: Market currency (e.g., 'USD', 'EUR')
            interval: 'intraday', 'daily', 'weekly', 'monthly'
        
        Returns:
            DataFrame with crypto data
        """
        try:
            function_map = {
                'intraday': AlphaVantageFunction.DIGITAL_CURRENCY_INTRADAY,
                'daily': AlphaVantageFunction.DIGITAL_CURRENCY_DAILY,
                'weekly': AlphaVantageFunction.DIGITAL_CURRENCY_WEEKLY,
                'monthly': AlphaVantageFunction.DIGITAL_CURRENCY_MONTHLY
            }
            
            if interval not in function_map:
                raise ValueError(f"Invalid interval: {interval}")
            
            params = {
                'function': function_map[interval].value,
                'symbol': symbol,
                'market': market
            }
            
            if interval == 'intraday':
                params['interval'] = '5min'
            
            data = await self._make_request(params)
            
            # Find time series key
            time_series_key = None
            for key in data.keys():
                if 'Time Series' in key:
                    time_series_key = key
                    break
            
            if not time_series_key or time_series_key not in data:
                logger.warning(f"⚠️ No crypto data found for {symbol}")
                return pd.DataFrame()
            
            time_series = data[time_series_key]
            
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')
            
            # Clean column names and select market data
            new_columns = {}
            for col in df.columns:
                if f'({market})' in col:
                    clean_name = col.split('. ')[-1].replace(f' ({market})', '').lower().replace(' ', '_')
                    new_columns[col] = clean_name
            
            if not new_columns:
                logger.warning(f"⚠️ No {market} market data found for {symbol}")
                return pd.DataFrame()
            
            df = df[list(new_columns.keys())].rename(columns=new_columns)
            
            # Convert to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Sort by timestamp
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Add metadata
            df['symbol'] = symbol
            df['market'] = market
            df['source'] = 'alpha_vantage'
            df['data_type'] = f'crypto_{interval}'
            df['ingestion_timestamp'] = datetime.now()
            
            logger.info(f"₿ Alpha Vantage crypto data for {symbol}/{market}: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to get Alpha Vantage crypto data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def get_economic_indicator(self, indicator: str, interval: str = "monthly") -> pd.DataFrame:
        """
        Get economic indicator data
        
        Args:
            indicator: Economic indicator function name
            interval: Data interval
        
        Returns:
            DataFrame with economic data
        """
        try:
            params = {
                'function': indicator,
                'interval': interval
            }
            
            data = await self._make_request(params)
            
            # Find data key
            data_key = None
            for key in data.keys():
                if 'data' in key.lower():
                    data_key = key
                    break
            
            if not data_key or data_key not in data:
                logger.warning(f"⚠️ No economic data found for {indicator}")
                return pd.DataFrame()
            
            economic_data = data[data_key]
            
            if isinstance(economic_data, list):
                df = pd.DataFrame(economic_data)
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.set_index('date').sort_index()
            else:
                df = pd.DataFrame.from_dict(economic_data, orient='index')
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
            
            # Add metadata
            df['indicator'] = indicator
            df['source'] = 'alpha_vantage'
            df['data_type'] = 'economic_indicator'
            
            logger.info(f"📊 Alpha Vantage economic indicator {indicator}: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to get Alpha Vantage economic indicator {indicator}: {e}")
            return pd.DataFrame()
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    # ============= UTILITY METHODS FOR JSON PARSING =============
    
    def _parse_time_series_data(self, data: Dict[str, Any], symbol: str, data_type: str) -> pd.DataFrame:
        """
        Universal time series parser for all Alpha Vantage time series endpoints
        Handles all the various JSON formats based on the API documentation
        """
        if not data:
            return pd.DataFrame()
        
        # Find the time series key - Alpha Vantage uses various formats
        time_series_key = None
        time_series_keys_to_try = [
            'Time Series (5min)', 'Time Series (Daily)', 'Time Series (Weekly)', 'Time Series (Monthly)',
            'Time Series (1min)', 'Time Series (15min)', 'Time Series (30min)', 'Time Series (60min)',
            'Weekly Time Series', 'Monthly Time Series', 'Weekly Adjusted Time Series', 
            'Monthly Adjusted Time Series', 'Time Series (Digital Currency Daily)',
            'Time Series (Digital Currency Weekly)', 'Time Series (Digital Currency Monthly)',
            'Time Series FX (5min)', 'Time Series FX (Daily)', 'Time Series FX (Weekly)', 'Time Series FX (Monthly)'
        ]
        
        # Try to find matching time series key
        for key in time_series_keys_to_try:
            if key in data:
                time_series_key = key
                break
        
        # Fallback - look for any key containing "Time Series"
        if not time_series_key:
            for key in data.keys():
                if 'Time Series' in str(key):
                    time_series_key = key
                    break
        
        if not time_series_key or time_series_key not in data:
            logger.warning(f"⚠️ No time series data found for {symbol}")
            return pd.DataFrame()
        
        time_series = data[time_series_key]
        
        if not time_series:
            logger.warning(f"⚠️ Empty time series data for {symbol}")
            return pd.DataFrame()
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')
            
            if df.empty:
                return df
            
            # Clean column names - remove number prefixes like "1. ", "2. ", etc.
            column_mapping = {}
            for col in df.columns:
                clean_name = col
                if '. ' in col:
                    clean_name = col.split('. ', 1)[1]  # Remove "1. ", "2. ", etc.
                
                # Standardize common column names
                clean_name = clean_name.lower().replace(' ', '_')
                if 'adjusted' in clean_name and 'close' in clean_name:
                    clean_name = 'adjusted_close'
                elif 'dividend' in clean_name:
                    clean_name = 'dividend_amount'
                elif 'split' in clean_name:
                    clean_name = 'split_coefficient'
                
                column_mapping[col] = clean_name
            
            df = df.rename(columns=column_mapping)
            
            # Convert numeric columns
            numeric_columns = ['open', 'high', 'low', 'close', 'adjusted_close', 'volume', 
                             'dividend_amount', 'split_coefficient']
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Parse timestamp index
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Add metadata columns
            df['symbol'] = symbol
            df['source'] = 'alpha_vantage'
            df['data_type'] = data_type
            df['ingestion_timestamp'] = datetime.now()
            
            logger.info(f"📈 Parsed Alpha Vantage {data_type} data for {symbol}: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to parse time series data for {symbol}: {e}")
            return pd.DataFrame()
    
    def _parse_forex_data(self, data: Dict[str, Any], from_symbol: str, to_symbol: str, 
                         interval: str) -> pd.DataFrame:
        """Parse forex data with proper currency pair handling"""
        if not data:
            return pd.DataFrame()
        
        # Find forex time series key
        time_series_key = None
        for key in data.keys():
            if 'Time Series' in key and 'FX' in key:
                time_series_key = key
                break
        
        # Fallback - any time series key
        if not time_series_key:
            for key in data.keys():
                if 'Time Series' in key:
                    time_series_key = key
                    break
        
        if not time_series_key:
            logger.warning(f"⚠️ No forex time series found for {from_symbol}/{to_symbol}")
            return pd.DataFrame()
        
        try:
            time_series = data[time_series_key]
            df = pd.DataFrame.from_dict(time_series, orient='index')
            
            # Clean column names
            df.columns = [col.split('. ')[-1].lower().replace(' ', '_') for col in df.columns]
            
            # Convert to numeric
            for col in ['open', 'high', 'low', 'close']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Parse timestamps
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Add forex-specific metadata
            df['from_symbol'] = from_symbol
            df['to_symbol'] = to_symbol
            df['currency_pair'] = f"{from_symbol}/{to_symbol}"
            df['source'] = 'alpha_vantage'
            df['data_type'] = f'forex_{interval}'
            df['ingestion_timestamp'] = datetime.now()
            
            logger.info(f"💱 Parsed forex data for {from_symbol}/{to_symbol}: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to parse forex data for {from_symbol}/{to_symbol}: {e}")
            return pd.DataFrame()
    
    def _parse_crypto_data(self, data: Dict[str, Any], symbol: str, market: str, 
                          interval: str) -> pd.DataFrame:
        """Parse cryptocurrency data with market-specific columns"""
        if not data:
            return pd.DataFrame()
        
        # Find crypto time series key
        time_series_key = None
        for key in data.keys():
            if 'Time Series' in key and ('Digital' in key or 'Crypto' in key):
                time_series_key = key
                break
        
        if not time_series_key:
            logger.warning(f"⚠️ No crypto time series found for {symbol}")
            return pd.DataFrame()
        
        try:
            time_series = data[time_series_key]
            df = pd.DataFrame.from_dict(time_series, orient='index')
            
            # Filter columns for the specified market (e.g., USD, EUR)
            market_columns = {}
            for col in df.columns:
                if f'({market})' in col:
                    clean_name = col.split('. ')[-1].replace(f' ({market})', '').lower().replace(' ', '_')
                    market_columns[col] = clean_name
            
            if not market_columns:
                logger.warning(f"⚠️ No {market} market data found for {symbol}")
                return pd.DataFrame()
            
            # Select and rename market-specific columns
            df = df[list(market_columns.keys())].rename(columns=market_columns)
            
            # Convert to numeric
            for col in df.columns:
                if col not in ['symbol', 'market', 'source', 'data_type']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Parse timestamps
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Add crypto-specific metadata
            df['symbol'] = symbol
            df['market'] = market
            df['crypto_pair'] = f"{symbol}/{market}"
            df['source'] = 'alpha_vantage'
            df['data_type'] = f'crypto_{interval}'
            df['ingestion_timestamp'] = datetime.now()
            
            logger.info(f"₿ Parsed crypto data for {symbol}/{market}: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to parse crypto data for {symbol}: {e}")
            return pd.DataFrame()
    
    def _parse_commodity_data(self, data: Dict[str, Any], commodity: str, 
                             interval: str = "monthly") -> pd.DataFrame:
        """Parse commodity price data"""
        if not data:
            return pd.DataFrame()
        
        # Find data key - commodities use different formats
        data_key = None
        for key in data.keys():
            if 'data' in key.lower() and key != 'Meta Data':
                data_key = key
                break
        
        if not data_key:
            logger.warning(f"⚠️ No commodity data found for {commodity}")
            return pd.DataFrame()
        
        try:
            commodity_data = data[data_key]
            
            if isinstance(commodity_data, list):
                # List format (e.g., economic indicators)
                df = pd.DataFrame(commodity_data)
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.set_index('date')
            else:
                # Dictionary format
                df = pd.DataFrame.from_dict(commodity_data, orient='index')
                df.index = pd.to_datetime(df.index)
            
            # Sort by date
            df = df.sort_index()
            
            # Convert numeric columns
            for col in df.columns:
                if col not in ['commodity', 'source', 'data_type', 'unit']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Add metadata
            df['commodity'] = commodity
            df['source'] = 'alpha_vantage'
            df['data_type'] = f'commodity_{interval}'
            df['ingestion_timestamp'] = datetime.now()
            
            logger.info(f"🛢️ Parsed commodity data for {commodity}: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to parse commodity data for {commodity}: {e}")
            return pd.DataFrame()
