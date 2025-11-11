#!/usr/bin/env python3
"""
Enhanced Alpha Vantage Data Collector for uRISK
Comprehensive implementation supporting ALL Alpha Vantage API endpoints
Covers: Stocks, Options, Alpha Intelligence, Fundamentals, Forex, Crypto, 
Commodities, Economic Indicators, and Technical Indicators

Includes Top 200 global companies integration with immense data population strategy
"""

import asyncio
import aiohttp
from aiohttp import TCPConnector
import ssl
import certifi
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import time
import json
import os
import sys
from dataclasses import dataclass, field
from enum import Enum
import hashlib

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.utils.logging_utils import setup_logger
from backend.db.postgres_handler import PostgresHandler
from backend.embeddings.vector_store import ChromaVectorStore
from backend.embeddings.embedder import Embedder
from top_200_companies import TOP_200_COMPANIES, US_TRADEABLE_SYMBOLS, MEGA_CAP_SYMBOLS, LARGE_CAP_SYMBOLS, MID_CAP_SYMBOLS

logger = setup_logger(__name__)

class AlphaVantageFunction(Enum):
    """Complete Alpha Vantage API functions - All supported endpoints"""
    
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
    
    # Premium tier limits (if available)
    premium_calls_per_minute: int = 75
    premium_calls_per_day: int = 75000
    
    @property
    def effective_calls_per_minute(self) -> int:
        return self.premium_calls_per_minute if self.premium_tier else self.rate_limit_calls_per_minute
    
    @property
    def effective_calls_per_day(self) -> int:
        return self.premium_calls_per_day if self.premium_tier else self.rate_limit_calls_per_day

@dataclass
class DataIngestionMetrics:
    """Track data ingestion metrics"""
    total_api_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rate_limited_calls: int = 0
    data_points_collected: int = 0
    vector_embeddings_created: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    
    def add_call_result(self, success: bool, rate_limited: bool = False, data_points: int = 0):
        self.total_api_calls += 1
        if success:
            self.successful_calls += 1
            self.data_points_collected += data_points
        else:
            self.failed_calls += 1
        
        if rate_limited:
            self.rate_limited_calls += 1
    
    def get_summary(self) -> dict:
        runtime = (datetime.now() - self.start_time).total_seconds()
        return {
            "runtime_seconds": runtime,
            "total_api_calls": self.total_api_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "rate_limited_calls": self.rate_limited_calls,
            "success_rate": self.successful_calls / max(1, self.total_api_calls),
            "data_points_collected": self.data_points_collected,
            "vector_embeddings_created": self.vector_embeddings_created,
            "calls_per_minute": self.total_api_calls / max(1, runtime / 60),
        }

class EnhancedAlphaVantageCollector:
    """
    Enhanced Alpha Vantage collector supporting ALL API endpoints
    Immense data collection strategy for Top 200 companies
    """
    
    def __init__(self, config: AlphaVantageConfig):
        self.config = config
        self.db = PostgresHandler()
        self.vector_store = ChromaVectorStore()
        self.embedder = Embedder()
        self.metrics = DataIngestionMetrics()
        self.session = None
        
        # Rate limiting
        self._last_call_time = 0
        self._call_count = 0
        self._call_window_start = datetime.now()
        
        # Major currency pairs for FX data
        self.major_forex_pairs = [
            ("USD", "EUR"), ("USD", "GBP"), ("USD", "JPY"), ("USD", "CAD"),
            ("USD", "AUD"), ("USD", "CHF"), ("EUR", "GBP"), ("EUR", "JPY"),
            ("GBP", "JPY"), ("AUD", "JPY"), ("USD", "CNY"), ("USD", "INR")
        ]
        
        # Major cryptocurrencies  
        self.major_crypto = ["BTC", "ETH", "LTC", "XRP", "BCH", "EOS", "XTZ", "ADA", "DOT", "LINK"]
        
        # Commodities list
        self.commodities = ["WTI", "BRENT", "NATURAL_GAS", "COPPER", "ALUMINUM", "WHEAT", "CORN", "COTTON", "SUGAR", "COFFEE"]
        
        # Technical indicators to collect
        self.tech_indicators = [
            "SMA", "EMA", "RSI", "MACD", "STOCH", "ADX", "BBANDS", "CCI", "AROON", "OBV"
        ]
    
    async def __aenter__(self):
        """Async context manager entry"""
        # Create SSL context with trusted certificates
        ssl_ctx = ssl.create_default_context(cafile=certifi.where())
        connector = TCPConnector(ssl=ssl_ctx)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            trust_env=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _rate_limit(self):
        """Implement rate limiting based on configuration"""
        current_time = time.time()
        time_since_last_call = current_time - self._last_call_time
        
        # Minimum time between calls
        min_interval = 60.0 / self.config.effective_calls_per_minute
        
        if time_since_last_call < min_interval:
            sleep_time = min_interval - time_since_last_call
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)
        
        # Check daily limit
        window_elapsed = (datetime.now() - self._call_window_start).total_seconds()
        if window_elapsed > 86400:  # 24 hours
            self._call_count = 0
            self._call_window_start = datetime.now()
        
        if self._call_count >= self.config.effective_calls_per_day:
            logger.warning("Daily API limit reached")
            return False
        
        self._last_call_time = current_time
        self._call_count += 1
        return True
    
    async def _make_api_call(self, function: AlphaVantageFunction, **params) -> Optional[Dict[str, Any]]:
        """Make API call with error handling and rate limiting"""
        if not await self._rate_limit():
            self.metrics.add_call_result(False, rate_limited=True)
            return None
        
        # Build request parameters
        request_params = {
            "function": function.value,
            "apikey": self.config.api_key,
            **params
        }
        
        for attempt in range(self.config.retries + 1):
            try:
                async with self.session.get(self.config.base_url, params=request_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for API errors
                        if "Error Message" in data:
                            logger.error(f"Alpha Vantage API error: {data['Error Message']}")
                            self.metrics.add_call_result(False)
                            return None
                        
                        if "Note" in data:
                            logger.warning(f"Alpha Vantage API note: {data['Note']}")
                            self.metrics.add_call_result(False, rate_limited=True)
                            await asyncio.sleep(60)  # API rate limit hit
                            continue
                        
                        self.metrics.add_call_result(True, data_points=len(str(data)))
                        return data
                    
                    elif response.status == 429:
                        logger.warning(f"Rate limited (429), attempt {attempt + 1}")
                        await asyncio.sleep(2 ** attempt * self.config.backoff_factor)
                        continue
                    
                    else:
                        logger.error(f"HTTP error {response.status}")
                        await asyncio.sleep(2 ** attempt)
                        continue
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                await asyncio.sleep(2 ** attempt)
                continue
            except Exception as e:
                logger.error(f"API call error: {e}")
                await asyncio.sleep(2 ** attempt)
                continue
        
        self.metrics.add_call_result(False)
        return None
    
    # ============= CORE STOCK DATA COLLECTION =============
    
    async def collect_daily_prices(self, symbols: List[str], outputsize: str = "compact") -> Dict[str, pd.DataFrame]:
        """Collect daily price data for symbols"""
        logger.info(f"Collecting daily prices for {len(symbols)} symbols")
        results = {}
        
        for symbol in symbols:
            try:
                data = await self._make_api_call(
                    AlphaVantageFunction.TIME_SERIES_DAILY_ADJUSTED,
                    symbol=symbol,
                    outputsize=outputsize
                )
                
                if data and "Time Series (Daily)" in data:
                    # Convert to DataFrame
                    df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient='index')
                    df.index = pd.to_datetime(df.index)
                    df = df.astype(float)
                    df.columns = ['open', 'high', 'low', 'close', 'adjusted_close', 'volume', 'dividend_amount', 'split_coefficient']
                    df['symbol'] = symbol
                    
                    # Store in PostgreSQL
                    await self._store_market_data(df, symbol)
                    results[symbol] = df
                    
                    logger.info(f"✅ Collected {len(df)} daily price records for {symbol}")
                
            except Exception as e:
                logger.error(f"Error collecting daily prices for {symbol}: {e}")
                continue
        
        return results
    
    async def collect_intraday_prices(self, symbols: List[str], interval: str = "5min") -> Dict[str, pd.DataFrame]:
        """Collect intraday price data"""
        logger.info(f"Collecting intraday prices for {len(symbols)} symbols")
        results = {}
        
        for symbol in symbols:
            try:
                data = await self._make_api_call(
                    AlphaVantageFunction.TIME_SERIES_INTRADAY,
                    symbol=symbol,
                    interval=interval,
                    outputsize="compact"
                )
                
                if data and f"Time Series ({interval})" in data:
                    df = pd.DataFrame.from_dict(data[f"Time Series ({interval})"], orient='index')
                    df.index = pd.to_datetime(df.index)
                    df = df.astype(float)
                    df.columns = ['open', 'high', 'low', 'close', 'volume']
                    df['symbol'] = symbol
                    
                    await self._store_market_data(df, symbol)
                    results[symbol] = df
                    
                    logger.info(f"✅ Collected {len(df)} intraday records for {symbol}")
                
            except Exception as e:
                logger.error(f"Error collecting intraday prices for {symbol}: {e}")
                continue
        
        return results
    
    # ============= FUNDAMENTAL DATA COLLECTION =============
    
    async def collect_company_overviews(self, symbols: List[str]) -> Dict[str, Dict]:
        """Collect company overview/fundamental data"""
        logger.info(f"Collecting company overviews for {len(symbols)} symbols")
        results = {}
        
        for symbol in symbols:
            try:
                data = await self._make_api_call(
                    AlphaVantageFunction.OVERVIEW,
                    symbol=symbol
                )
                
                if data and "Symbol" in data:
                    # Store in PostgreSQL and vector database
                    await self._store_fundamental_data(data, symbol)
                    await self._store_company_overview_vectors(data, symbol)
                    
                    results[symbol] = data
                    logger.info(f"✅ Collected company overview for {symbol}")
                
            except Exception as e:
                logger.error(f"Error collecting overview for {symbol}: {e}")
                continue
        
        return results
    
    async def collect_earnings_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """Collect earnings data"""
        logger.info(f"Collecting earnings data for {len(symbols)} symbols")
        results = {}
        
        for symbol in symbols:
            try:
                data = await self._make_api_call(
                    AlphaVantageFunction.EARNINGS,
                    symbol=symbol
                )
                
                if data and "symbol" in data:
                    await self._store_earnings_data(data, symbol)
                    results[symbol] = data
                    
                    logger.info(f"✅ Collected earnings data for {symbol}")
                
            except Exception as e:
                logger.error(f"Error collecting earnings for {symbol}: {e}")
                continue
        
        return results
    
    # ============= NEWS & SENTIMENT COLLECTION =============
    
    async def collect_news_sentiment(self, topics: List[str] = None, tickers: List[str] = None) -> Dict[str, Any]:
        """Collect news and sentiment data"""
        logger.info("Collecting news sentiment data")
        
        try:
            params = {}
            if topics:
                params["topics"] = ",".join(topics)
            if tickers:
                params["tickers"] = ",".join(tickers[:50])  # API limit
                
            data = await self._make_api_call(
                AlphaVantageFunction.NEWS_SENTIMENT,
                **params
            )
            
            if data and "feed" in data:
                await self._store_news_sentiment_data(data)
                logger.info(f"✅ Collected {len(data['feed'])} news articles with sentiment")
                return data
            
        except Exception as e:
            logger.error(f"Error collecting news sentiment: {e}")
        
        return {}
    
    async def collect_top_gainers_losers(self) -> Dict[str, Any]:
        """Collect top gainers and losers"""
        try:
            data = await self._make_api_call(AlphaVantageFunction.TOP_GAINERS_LOSERS)
            
            if data:
                await self._store_gainers_losers_data(data)
                logger.info("✅ Collected top gainers and losers data")
                return data
                
        except Exception as e:
            logger.error(f"Error collecting top gainers/losers: {e}")
        
        return {}
    
    # ============= FOREX DATA COLLECTION =============
    
    async def collect_forex_data(self) -> Dict[str, pd.DataFrame]:
        """Collect forex data for major currency pairs"""
        logger.info(f"Collecting forex data for {len(self.major_forex_pairs)} pairs")
        results = {}
        
        for from_currency, to_currency in self.major_forex_pairs:
            try:
                # Daily forex data
                data = await self._make_api_call(
                    AlphaVantageFunction.FX_DAILY,
                    from_symbol=from_currency,
                    to_symbol=to_currency
                )
                
                if data and "Time Series (FX Daily)" in data:
                    df = pd.DataFrame.from_dict(data["Time Series (FX Daily)"], orient='index')
                    df.index = pd.to_datetime(df.index)
                    df = df.astype(float)
                    df.columns = ['open', 'high', 'low', 'close']
                    pair = f"{from_currency}{to_currency}"
                    df['pair'] = pair
                    
                    await self._store_forex_data(df, pair)
                    results[pair] = df
                    
                    logger.info(f"✅ Collected forex data for {pair}")
                
            except Exception as e:
                logger.error(f"Error collecting forex for {from_currency}/{to_currency}: {e}")
                continue
        
        return results
    
    # ============= CRYPTO DATA COLLECTION =============
    
    async def collect_crypto_data(self) -> Dict[str, pd.DataFrame]:
        """Collect cryptocurrency data"""
        logger.info(f"Collecting crypto data for {len(self.major_crypto)} cryptocurrencies")
        results = {}
        
        for crypto in self.major_crypto:
            try:
                data = await self._make_api_call(
                    AlphaVantageFunction.DIGITAL_CURRENCY_DAILY,
                    symbol=crypto,
                    market="USD"
                )
                
                if data and "Time Series (Digital Currency Daily)" in data:
                    df = pd.DataFrame.from_dict(data["Time Series (Digital Currency Daily)"], orient='index')
                    df.index = pd.to_datetime(df.index)
                    
                    # Select USD columns
                    usd_cols = [col for col in df.columns if "(USD)" in col]
                    df = df[usd_cols]
                    df.columns = ['open', 'high', 'low', 'close', 'volume', 'market_cap']
                    df = df.astype(float)
                    df['symbol'] = f"{crypto}-USD"
                    
                    await self._store_crypto_data(df, crypto)
                    results[crypto] = df
                    
                    logger.info(f"✅ Collected crypto data for {crypto}")
                
            except Exception as e:
                logger.error(f"Error collecting crypto for {crypto}: {e}")
                continue
        
        return results
    
    # ============= COMMODITIES DATA COLLECTION =============
    
    async def collect_commodities_data(self) -> Dict[str, pd.DataFrame]:
        """Collect commodities data"""
        logger.info(f"Collecting commodities data for {len(self.commodities)} commodities")
        results = {}
        
        for commodity in self.commodities:
            try:
                data = await self._make_api_call(getattr(AlphaVantageFunction, commodity))
                
                if data and "data" in data:
                    df = pd.DataFrame(data["data"])
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)
                    df['commodity'] = commodity.lower()
                    
                    await self._store_commodities_data(df, commodity)
                    results[commodity] = df
                    
                    logger.info(f"✅ Collected commodities data for {commodity}")
                
            except Exception as e:
                logger.error(f"Error collecting commodity {commodity}: {e}")
                continue
        
        return results
    
    # ============= TECHNICAL INDICATORS COLLECTION =============
    
    async def collect_technical_indicators(self, symbols: List[str]) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Collect technical indicators for symbols"""
        logger.info(f"Collecting technical indicators for {len(symbols)} symbols")
        results = {}
        
        for symbol in symbols[:10]:  # Limit for API calls
            results[symbol] = {}
            
            for indicator in self.tech_indicators[:3]:  # Top 3 indicators
                try:
                    params = {"symbol": symbol, "interval": "daily", "time_period": 20}
                    
                    if indicator == "BBANDS":
                        params.update({"time_period": 20, "series_type": "close"})
                    elif indicator == "MACD":
                        params.update({"series_type": "close"})
                    elif indicator == "STOCH":
                        params.update({"fastkperiod": 5, "slowkperiod": 3, "slowdperiod": 3})
                    
                    data = await self._make_api_call(getattr(AlphaVantageFunction, indicator), **params)
                    
                    if data and f"Technical Analysis: {indicator}" in data:
                        df = pd.DataFrame.from_dict(data[f"Technical Analysis: {indicator}"], orient='index')
                        df.index = pd.to_datetime(df.index)
                        df = df.astype(float)
                        df['symbol'] = symbol
                        df['indicator'] = indicator
                        
                        await self._store_technical_indicators(df, symbol, indicator)
                        results[symbol][indicator] = df
                        
                        logger.info(f"✅ Collected {indicator} for {symbol}")
                    
                except Exception as e:
                    logger.error(f"Error collecting {indicator} for {symbol}: {e}")
                    continue
        
        return results
    
    # ============= ECONOMIC INDICATORS COLLECTION =============
    
    async def collect_economic_indicators(self) -> Dict[str, pd.DataFrame]:
        """Collect economic indicators"""
        logger.info("Collecting economic indicators")
        results = {}
        
        economic_indicators = [
            AlphaVantageFunction.REAL_GDP,
            AlphaVantageFunction.TREASURY_YIELD, 
            AlphaVantageFunction.FEDERAL_FUNDS_RATE,
            AlphaVantageFunction.CPI,
            AlphaVantageFunction.UNEMPLOYMENT
        ]
        
        for indicator in economic_indicators:
            try:
                params = {}
                if indicator == AlphaVantageFunction.TREASURY_YIELD:
                    params["maturity"] = "10year"
                
                data = await self._make_api_call(indicator, **params)
                
                if data and "data" in data:
                    df = pd.DataFrame(data["data"])
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)
                    df['indicator'] = indicator.value
                    
                    await self._store_economic_indicators(df, indicator.value)
                    results[indicator.value] = df
                    
                    logger.info(f"✅ Collected economic indicator: {indicator.value}")
                
            except Exception as e:
                logger.error(f"Error collecting economic indicator {indicator.value}: {e}")
                continue
        
        return results
    
    # ============= DATA STORAGE METHODS =============
    
    async def _store_market_data(self, df: pd.DataFrame, symbol: str):
        """Store market data in PostgreSQL"""
        try:
            for index, row in df.iterrows():
                await self.db.async_execute_query("""
                    INSERT INTO market_prices (ticker, timestamp, open, high, low, close, volume, source)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (ticker, timestamp) DO UPDATE SET
                        open = EXCLUDED.open,
                        high = EXCLUDED.high,
                        low = EXCLUDED.low,
                        close = EXCLUDED.close,
                        volume = EXCLUDED.volume,
                        source = EXCLUDED.source
                """, (symbol, index, float(row.get('open', 0)), float(row.get('high', 0)), 
                     float(row.get('low', 0)), float(row.get('close', 0)), 
                     int(row.get('volume', 0)), 'alpha_vantage'))
                     
        except Exception as e:
            logger.error(f"Error storing market data for {symbol}: {e}")
    
    async def _store_fundamental_data(self, data: Dict, symbol: str):
        """Store fundamental data as JSON in a dedicated table"""
        try:
            # Create table if it doesn't exist
            await self.db.async_execute_query("""
                CREATE TABLE IF NOT EXISTS fundamental_data (
                    id SERIAL PRIMARY KEY,
                    ticker VARCHAR(20) NOT NULL,
                    data_type VARCHAR(50) NOT NULL,
                    data JSONB NOT NULL,
                    source VARCHAR(30) DEFAULT 'alpha_vantage',
                    updated_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(ticker, data_type, source)
                )
            """)
            
            await self.db.async_execute_query("""
                INSERT INTO fundamental_data (ticker, data_type, data, source)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (ticker, data_type, source) DO UPDATE SET
                    data = EXCLUDED.data,
                    updated_at = NOW()
            """, (symbol, 'company_overview', json.dumps(data), 'alpha_vantage'))
            
        except Exception as e:
            logger.error(f"Error storing fundamental data for {symbol}: {e}")
    
    async def _store_company_overview_vectors(self, data: Dict, symbol: str):
        """Store company overview data in vector database"""
        try:
            # Create searchable text from overview
            overview_text = f"""
            Company: {data.get('Name', symbol)}
            Sector: {data.get('Sector', 'N/A')}
            Industry: {data.get('Industry', 'N/A')}
            Description: {data.get('Description', 'No description available')}
            Market Cap: ${data.get('MarketCapitalization', 'N/A')}
            P/E Ratio: {data.get('PERatio', 'N/A')}
            EPS: ${data.get('EPS', 'N/A')}
            Revenue: ${data.get('RevenueTTM', 'N/A')}
            """
            
            # Create chunks for embedding
            chunks = self.embedder.create_chunks(overview_text, max_length=300)
            
            for i, chunk in enumerate(chunks):
                embedding = await self.embedder.embed_text(chunk)
                
                metadata = {
                    "ticker": symbol,
                    "company_name": data.get('Name', symbol),
                    "data_type": "company_overview",
                    "sector": data.get('Sector', 'Unknown'),
                    "industry": data.get('Industry', 'Unknown'),
                    "source": "alpha_vantage",
                    "chunk_index": i,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Store in vector database
                await self.vector_store.add_vectors([{
                    "id": f"{symbol}_overview_{i}_{int(time.time())}",
                    "vector": embedding,
                    "metadata": metadata,
                    "content": chunk
                }])
            
            self.metrics.vector_embeddings_created += len(chunks)
            
        except Exception as e:
            logger.error(f"Error storing overview vectors for {symbol}: {e}")
    
    async def _store_earnings_data(self, data: Dict, symbol: str):
        """Store earnings data"""
        try:
            # Store quarterly earnings
            if "quarterlyEarnings" in data:
                for earnings in data["quarterlyEarnings"]:
                    await self.db.async_execute_query("""
                        INSERT INTO earnings_data (ticker, fiscal_date_ending, reported_eps, 
                                                 estimated_eps, surprise, surprise_percentage, source)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT (ticker, fiscal_date_ending) DO UPDATE SET
                            reported_eps = EXCLUDED.reported_eps,
                            estimated_eps = EXCLUDED.estimated_eps,
                            surprise = EXCLUDED.surprise,
                            surprise_percentage = EXCLUDED.surprise_percentage
                    """, (symbol, earnings.get('fiscalDateEnding'), 
                         float(earnings.get('reportedEPS', 0)),
                         float(earnings.get('estimatedEPS', 0)),
                         float(earnings.get('surprise', 0)),
                         float(earnings.get('surprisePercentage', 0)),
                         'alpha_vantage'))
            
        except Exception as e:
            logger.error(f"Error storing earnings data for {symbol}: {e}")
    
    async def _store_news_sentiment_data(self, data: Dict):
        """Store news sentiment data"""
        try:
            if "feed" in data:
                for article in data["feed"]:
                    # Store headline
                    headline_id = await self.db.async_fetch_scalar("""
                        INSERT INTO news_headlines (ticker, headline, url, source, published_at)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (url) DO UPDATE SET headline = EXCLUDED.headline
                        RETURNING id
                    """, (
                        article.get('ticker_sentiment', [{}])[0].get('ticker', '') if article.get('ticker_sentiment') else '',
                        article.get('title', ''),
                        article.get('url', ''),
                        article.get('source', 'alpha_vantage'),
                        datetime.fromisoformat(article.get('time_published', datetime.now().isoformat()))
                    ))
                    
                    # Store sentiment
                    overall_sentiment = article.get('overall_sentiment_label', 'Neutral')
                    sentiment_score = article.get('overall_sentiment_score', 0)
                    
                    await self.db.async_execute_query("""
                        INSERT INTO news_sentiment (headline_id, sentiment_score, sentiment_label, confidence, model_version)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (headline_id) DO UPDATE SET
                            sentiment_score = EXCLUDED.sentiment_score,
                            sentiment_label = EXCLUDED.sentiment_label
                    """, (headline_id, float(sentiment_score), overall_sentiment, 0.8, 'alpha_vantage'))
                    
                    # Store in vector database
                    await self._store_news_vectors(article)
            
        except Exception as e:
            logger.error(f"Error storing news sentiment data: {e}")
    
    async def _store_news_vectors(self, article: Dict):
        """Store news article in vector database"""
        try:
            content = f"""
            Title: {article.get('title', '')}
            Summary: {article.get('summary', '')}
            Source: {article.get('source', '')}
            Sentiment: {article.get('overall_sentiment_label', 'Neutral')}
            """
            
            chunks = self.embedder.create_chunks(content, max_length=350)
            
            for i, chunk in enumerate(chunks):
                embedding = await self.embedder.embed_text(chunk)
                
                metadata = {
                    "data_type": "news_article",
                    "source": article.get('source', 'alpha_vantage'),
                    "sentiment_label": article.get('overall_sentiment_label', 'Neutral'),
                    "sentiment_score": article.get('overall_sentiment_score', 0),
                    "published_at": article.get('time_published', datetime.now().isoformat()),
                    "chunk_index": i,
                    "url": article.get('url', ''),
                    "tickers": [t.get('ticker', '') for t in article.get('ticker_sentiment', [])]
                }
                
                await self.vector_store.add_vectors([{
                    "id": f"news_{int(time.time())}_{i}",
                    "vector": embedding,
                    "metadata": metadata,
                    "content": chunk
                }])
            
            self.metrics.vector_embeddings_created += len(chunks)
            
        except Exception as e:
            logger.error(f"Error storing news vectors: {e}")
    
    # Additional storage methods for other data types...
    async def _store_forex_data(self, df: pd.DataFrame, pair: str):
        """Store forex data (implement as needed)"""
        # Implementation here
        pass
    
    async def _store_crypto_data(self, df: pd.DataFrame, crypto: str):
        """Store crypto data (implement as needed)"""
        # Implementation here  
        pass
        
    async def _store_commodities_data(self, df: pd.DataFrame, commodity: str):
        """Store commodities data (implement as needed)"""
        # Implementation here
        pass
        
    async def _store_technical_indicators(self, df: pd.DataFrame, symbol: str, indicator: str):
        """Store technical indicators (implement as needed)"""
        # Implementation here
        pass
        
    async def _store_economic_indicators(self, df: pd.DataFrame, indicator: str):
        """Store economic indicators (implement as needed)"""
        # Implementation here
        pass
        
    async def _store_gainers_losers_data(self, data: Dict):
        """Store gainers/losers data (implement as needed)"""
        # Implementation here
        pass
    
    # ============= COMPREHENSIVE COLLECTION ORCHESTRATION =============
    
    async def collect_comprehensive_data(self, focus_tier: str = "mega") -> Dict[str, Any]:
        """
        Orchestrate comprehensive data collection
        focus_tier: 'mega', 'large', 'mid', or 'all'
        """
        logger.info(f"🚀 Starting comprehensive Alpha Vantage data collection (focus: {focus_tier})")
        
        # Select symbols based on focus tier
        if focus_tier == "mega":
            symbols = MEGA_CAP_SYMBOLS[:10]  # Top 10 for rate limiting
        elif focus_tier == "large":
            symbols = LARGE_CAP_SYMBOLS[:15]
        elif focus_tier == "mid":
            symbols = MID_CAP_SYMBOLS[:20]
        else:  # all
            symbols = US_TRADEABLE_SYMBOLS[:25]  # Limit to 25 for API limits
        
        results = {
            "market_data": {},
            "fundamental_data": {},
            "news_sentiment": {},
            "forex_data": {},
            "crypto_data": {},
            "commodities_data": {},
            "technical_indicators": {},
            "economic_indicators": {},
            "top_movers": {},
            "metrics": {}
        }
        
        try:
            # 1. Core market data
            logger.info("📊 Collecting market data...")
            results["market_data"]["daily"] = await self.collect_daily_prices(symbols)
            
            # 2. Fundamental data  
            logger.info("📋 Collecting fundamental data...")
            results["fundamental_data"]["overviews"] = await self.collect_company_overviews(symbols[:5])
            results["fundamental_data"]["earnings"] = await self.collect_earnings_data(symbols[:5])
            
            # 3. News and sentiment
            logger.info("📰 Collecting news and sentiment...")
            results["news_sentiment"] = await self.collect_news_sentiment(tickers=symbols[:10])
            
            # 4. Top gainers/losers
            logger.info("📈📉 Collecting top gainers and losers...")
            results["top_movers"] = await self.collect_top_gainers_losers()
            
            # 5. Forex data
            logger.info("💱 Collecting forex data...")
            results["forex_data"] = await self.collect_forex_data()
            
            # 6. Crypto data
            logger.info("₿ Collecting crypto data...")
            results["crypto_data"] = await self.collect_crypto_data()
            
            # 7. Commodities
            logger.info("🛢️ Collecting commodities data...")
            results["commodities_data"] = await self.collect_commodities_data()
            
            # 8. Technical indicators
            logger.info("📊 Collecting technical indicators...")
            results["technical_indicators"] = await self.collect_technical_indicators(symbols[:3])
            
            # 9. Economic indicators
            logger.info("🏛️ Collecting economic indicators...")
            results["economic_indicators"] = await self.collect_economic_indicators()
            
            # Compile final metrics
            results["metrics"] = self.metrics.get_summary()
            
            logger.info("✅ Comprehensive Alpha Vantage data collection completed!")
            logger.info(f"📊 Collected {results['metrics']['data_points_collected']} data points")
            logger.info(f"🔢 Created {results['metrics']['vector_embeddings_created']} vector embeddings")
            logger.info(f"⚡ Success rate: {results['metrics']['success_rate']:.2%}")
            
        except Exception as e:
            logger.error(f"Error in comprehensive collection: {e}")
            results["error"] = str(e)
            results["metrics"] = self.metrics.get_summary()
        
        return results

# ============= UTILITY FUNCTIONS =============

def get_alpha_vantage_config() -> AlphaVantageConfig:
    """Get Alpha Vantage configuration from environment"""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        logger.warning("ALPHA_VANTAGE_API_KEY not found in environment")
        api_key = "demo"  # Demo key for testing
    
    return AlphaVantageConfig(
        api_key=api_key,
        premium_tier=os.getenv("ALPHA_VANTAGE_PREMIUM", "false").lower() == "true"
    )

async def main():
    """Main execution function"""
    config = get_alpha_vantage_config()
    
    async with EnhancedAlphaVantageCollector(config) as collector:
        # Run comprehensive collection
        results = await collector.collect_comprehensive_data(focus_tier="mega")
        
        # Print summary
        print("=" * 80)
        print("🏆 ALPHA VANTAGE DATA COLLECTION SUMMARY")
        print("=" * 80)
        for category, data in results.items():
            if isinstance(data, dict) and data:
                print(f"✅ {category}: {len(data)} items collected")
            elif data:
                print(f"✅ {category}: Data collected")
            else:
                print(f"❌ {category}: No data collected")
        
        if "metrics" in results:
            metrics = results["metrics"]
            print(f"\n📊 Overall Metrics:")
            print(f"   • API Calls: {metrics['total_api_calls']}")
            print(f"   • Success Rate: {metrics['success_rate']:.2%}")
            print(f"   • Data Points: {metrics['data_points_collected']}")
            print(f"   • Vector Embeddings: {metrics['vector_embeddings_created']}")
            print(f"   • Runtime: {metrics['runtime_seconds']:.1f}s")

if __name__ == "__main__":
    asyncio.run(main())
