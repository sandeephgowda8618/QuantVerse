"""
Alpha Vantage Data Fetcher - Low-level API Client
Handles all API interactions with Alpha Vantage endpoints
Part of the 200-Batch, Epoch-Based Ingestion System
"""

import asyncio
import aiohttp
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
import json
from urllib.parse import urlencode

from ..config.settings import settings

logger = logging.getLogger(__name__)

class AlphaFetcher:
    """
    Low-level A                        # Success!
                        self.successful_calls += 1
                        self.key_stats[self.current_key_index]['successful_calls'] += 1
                        self.key_last_success[self.current_key_index] = time.time()
                        
                        # Record success and reset circuit breaker
                        self._record_success()
                        
                        # Cache fundamental data
                        if self._is_fundamental_endpoint(function) and ticker:
                            cache_key = self._get_cache_key(function, ticker, **request_params)
                            self._cache_data(cache_key, data)
                        
                        # Reduce rate limit delay on success
                        self._decrease_rate_limit_delay()
                        
                        # Add human-like pause after successful requests
                        await self._human_like_pause()
                        
                        logger.debug(f"✅ [API Key #{current_key_info['key_number']}] Successfully fetched {function}")
                        return True, data, NoneI client with intelligent API key rotation and rate limiting
    """
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self):
        self.api_keys = self._get_all_api_keys()
        self.current_key_index = 0
        self.api_key = self.api_keys[self.current_key_index] if self.api_keys else 'demo'
        
        # Anti-automation rate limiting fixes
        self.base_rate_limit_delay = 2.0  # Start with 2 seconds between requests
        self.current_rate_limit_delay = self.base_rate_limit_delay
        self.max_rate_limit_delay = 10.0  # Maximum delay for backoff
        self.last_request_time = 0
        self.session = None  # type: Optional[aiohttp.ClientSession]
        
        # Key rotation intelligence
        self.key_failure_counts = {}  # Track failures per key
        self.key_last_success = {}    # Track last successful request per key
        self.max_retries_same_key = 3  # Retry with same key before rotating
        
        # Cache for fundamental data (avoid redundant calls)
        self.fundamental_cache = {}
        self.cache_ttl = 86400  # 24 hours cache for fundamental data
        
        # Circuit breaker pattern
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 20  # Stop after 20 consecutive failures
        self.circuit_breaker_reset_time = 300  # 5 minutes
        self.circuit_breaker_open_time = 0
        
        # Anti-automation features
        self.successful_requests = 0
        self.pause_after_requests = 50  # Pause after every 50 successful requests
        self.pause_duration = 30  # 30 second pause to appear more human
        
        # Initialize failure tracking for each key
        for i, key in enumerate(self.api_keys):
            self.key_failure_counts[i] = 0
            self.key_last_success[i] = 0
        
        # API call statistics per key
        self.key_stats = {}
        for i, key in enumerate(self.api_keys):
            self.key_stats[i] = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'rate_limited_calls': 0,
                'key_preview': f"{key[:8]}..." if key else "demo"
            }
        
        # Global statistics
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.rate_limited_calls = 0
        self.key_rotations = 0
        
        # All available Alpha Vantage endpoints organized by category
        self.endpoints = self._initialize_endpoints()
        
        logger.info(f"🔑 Initialized Alpha Vantage fetcher with {len(self.api_keys)} API keys")
        logger.info(f"🎯 Starting with API Key #{self.current_key_index + 1}: {self.key_stats[self.current_key_index]['key_preview']}")
        
    def _get_all_api_keys(self) -> list:
        """Get all available Alpha Vantage API keys from settings"""
        valid_keys = []
        for key in settings.ALPHA_VANTAGE_API_KEYS:
            if key and len(key) > 5:  # Basic validation
                valid_keys.append(key)
        
        if not valid_keys:
            logger.warning("⚠️ No valid Alpha Vantage API keys found - using demo key")
            return ['demo']
        
        logger.info(f"✅ Found {len(valid_keys)} valid Alpha Vantage API keys")
        return valid_keys
    
    def rotate_api_key(self) -> bool:
        """Rotate to the next available API key with intelligent failure tracking"""
        if len(self.api_keys) <= 1:
            logger.warning("⚠️ No additional API keys available for rotation")
            return False
        
        old_index = self.current_key_index
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.api_key = self.api_keys[self.current_key_index]
        self.key_rotations += 1
        
        # Reset rate limiting delay when rotating keys
        self.current_rate_limit_delay = self.base_rate_limit_delay
        
        old_preview = self.key_stats[old_index]['key_preview']
        new_preview = self.key_stats[self.current_key_index]['key_preview']
        
        logger.info(f"🔄 API Key rotated: #{old_index + 1} ({old_preview}) -> #{self.current_key_index + 1} ({new_preview})")
        logger.info(f"📊 New key failure count: {self.key_failure_counts[self.current_key_index]}")
        return True
    
    def _increase_rate_limit_delay(self):
        """Increase rate limit delay for backoff strategy"""
        old_delay = self.current_rate_limit_delay
        self.current_rate_limit_delay = min(self.current_rate_limit_delay * 1.5, self.max_rate_limit_delay)
        logger.info(f"⚡ Increasing rate limit delay: {old_delay:.1f}s -> {self.current_rate_limit_delay:.1f}s")
    
    def _decrease_rate_limit_delay(self):
        """Decrease rate limit delay after successful requests"""
        if self.current_rate_limit_delay > self.base_rate_limit_delay:
            old_delay = self.current_rate_limit_delay
            self.current_rate_limit_delay = max(self.current_rate_limit_delay * 0.9, self.base_rate_limit_delay)
            logger.debug(f"⚡ Decreasing rate limit delay: {old_delay:.1f}s -> {self.current_rate_limit_delay:.1f}s")
    
    def _is_fundamental_endpoint(self, function: str) -> bool:
        """Check if endpoint is fundamental data (cacheable)"""
        fundamental_endpoints = {
            'COMPANY_OVERVIEW', 'OVERVIEW', 'ETF_PROFILE', 'DIVIDENDS', 'SPLITS',
            'INCOME_STATEMENT', 'BALANCE_SHEET', 'CASH_FLOW', 'SHARES_OUTSTANDING',
            'EARNINGS', 'EARNINGS_ESTIMATES', 'INSIDER_TRANSACTIONS'
        }
        return function in fundamental_endpoints
    
    def _get_cache_key(self, function: str, ticker: str, **params) -> str:
        """Generate cache key for fundamental data"""
        param_str = "_".join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"{function}_{ticker}_{param_str}" if param_str else f"{function}_{ticker}"
    
    def _get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """Get cached data if available and not expired"""
        if cache_key in self.fundamental_cache:
            cached_item = self.fundamental_cache[cache_key]
            if time.time() - cached_item['timestamp'] < self.cache_ttl:
                logger.debug(f"🎯 Cache hit for {cache_key}")
                return cached_item['data']
            else:
                # Expired cache entry
                del self.fundamental_cache[cache_key]
                logger.debug(f"🕐 Cache expired for {cache_key}")
        return None
    
    def _cache_data(self, cache_key: str, data: Dict):
        """Cache fundamental data"""
        self.fundamental_cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
        logger.debug(f"💾 Cached data for {cache_key}")
    
    def _should_retry_with_same_key(self, current_failures: int) -> bool:
        """Determine if we should retry with the same key"""
        return current_failures < self.max_retries_same_key
    
    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open (too many failures)"""
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            if time.time() - self.circuit_breaker_open_time >= self.circuit_breaker_reset_time:
                # Reset circuit breaker
                logger.info("🔄 Circuit breaker reset after timeout")
                self.circuit_breaker_failures = 0
                self.circuit_breaker_open_time = 0
                return False
            else:
                remaining = self.circuit_breaker_reset_time - (time.time() - self.circuit_breaker_open_time)
                logger.warning(f"🚫 Circuit breaker OPEN - {remaining:.0f}s remaining until reset")
                return True
        return False
    
    def _record_failure(self):
        """Record a failure for circuit breaker tracking"""
        self.circuit_breaker_failures += 1
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            self.circuit_breaker_open_time = time.time()
            logger.error(f"🚨 CIRCUIT BREAKER OPENED after {self.circuit_breaker_failures} failures")
    
    def _record_success(self):
        """Record a success and reset circuit breaker"""
        if self.circuit_breaker_failures > 0:
            logger.info(f"✅ Success after {self.circuit_breaker_failures} failures - resetting circuit breaker")
            self.circuit_breaker_failures = 0
            self.circuit_breaker_open_time = 0
        
        self.successful_requests += 1
    
    async def _human_like_pause(self):
        """Add human-like pauses after successful requests"""
        if self.successful_requests > 0 and self.successful_requests % self.pause_after_requests == 0:
            logger.info(f"😴 Human-like pause: {self.pause_duration}s after {self.successful_requests} requests")
            await asyncio.sleep(self.pause_duration)
    
    def get_current_key_info(self) -> dict:
        """Get information about the currently active API key"""
        return {
            'key_number': self.current_key_index + 1,
            'key_preview': self.key_stats[self.current_key_index]['key_preview'],
            'stats': self.key_stats[self.current_key_index].copy()
        }
        
    def _get_api_key(self) -> str:
        """Get Alpha Vantage API key from settings"""
        api_key = getattr(settings, 'ALPHA_VANTAGE_API_KEY', '')
        if not api_key:
            logger.warning("⚠️ ALPHA_VANTAGE_API_KEY not found - using demo key (limited)")
            return 'demo'
        return api_key
    
    def _initialize_endpoints(self) -> Dict[str, List[str]]:
        """Initialize all Alpha Vantage endpoints organized by category"""
        return {
            "core": [
                "TIME_SERIES_INTRADAY",
                "TIME_SERIES_DAILY",
                "TIME_SERIES_WEEKLY",
                "TIME_SERIES_WEEKLY_ADJUSTED",
                "TIME_SERIES_MONTHLY",
                "TIME_SERIES_MONTHLY_ADJUSTED",
                "GLOBAL_QUOTE",
                "SYMBOL_SEARCH",
                "MARKET_STATUS"
            ],
            "options": [
                "HISTORICAL_OPTIONS"
            ],
            "intelligence": [
                "NEWS_SENTIMENT",
                "EARNINGS_CALL_TRANSCRIPT",
                "TOP_GAINERS_LOSERS",
                "ANALYTICS_SENTIMENT",
                "ANALYTICS_FIXED_WINDOW",
                "ANALYTICS_SLIDING_WINDOW"
            ],
            "fundamental": [
                "COMPANY_OVERVIEW",
                "OVERVIEW",
                "ETF_PROFILE", 
                "DIVIDENDS",
                "SPLITS",
                "INCOME_STATEMENT",
                "BALANCE_SHEET",
                "CASH_FLOW",
                "SHARES_OUTSTANDING",
                "EARNINGS",
                "EARNINGS_ESTIMATES",
                "LISTING_STATUS",
                "IPO_CALENDAR",
                "EARNINGS_CALENDAR",
                "INSIDER_TRANSACTIONS"
            ],
            "forex": [
                "FX_DAILY",
                "FX_WEEKLY",
                "FX_MONTHLY",
                "CURRENCY_EXCHANGE_RATE"
            ],
            "crypto": [
                "DIGITAL_CURRENCY_DAILY",
                "DIGITAL_CURRENCY_WEEKLY",
                "DIGITAL_CURRENCY_MONTHLY"
            ],
            "commodities": [
                "WTI",
                "BRENT",
                "NATURAL_GAS",
                "COPPER",
                "ALUMINUM",
                "WHEAT",
                "CORN",
                "COTTON",
                "SUGAR",
                "COFFEE",
                "GLOBAL_COMMODITIES"
            ],
            "economic": [
                "REAL_GDP",
                "REAL_GDP_PER_CAPITA",
                "TREASURY_YIELD",
                "FEDERAL_FUNDS_RATE",
                "CPI",
                "INFLATION",
                "RETAIL_SALES",
                "DURABLES",
                "UNEMPLOYMENT",
                "NONFARM_PAYROLL"
            ],
            "technical": [
                "SMA",
                "EMA",
                "WMA",
                "DEMA",
                "TEMA",
                "TRIMA",
                "KAMA",
                "MAMA",
                "T3",
                "MACDEXT",
                "STOCH",
                "STOCHF",
                "RSI",
                "STOCHRSI",
                "WILLR",
                "ADX",
                "ADXR",
                "APO",
                "PPO",
                "MOM",
                "BOP",
                "CCI",
                "CMO",
                "ROC",
                "ROCR",
                "AROON",
                "AROONOSC",
                "MFI",
                "TRIX",
                "ULTOSC",
                "DX",
                "MINUS_DI",
                "PLUS_DI",
                "MINUS_DM",
                "PLUS_DM",
                "BBANDS",
                "MIDPOINT",
                "MIDPRICE",
                "SAR",
                "TRANGE",
                "ATR",
                "NATR",
                "AD",
                "ADOSC",
                "OBV",
                "HT_TRENDLINE",
                "HT_SINE",
                "HT_TRENDMODE",
                "HT_DCPERIOD",
                "HT_DCPHASE",
                "HT_PHASOR"
            ]
        }
    
    async def ensure_session(self):
        """Ensure aiohttp session is created"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
            logger.debug("🔗 Created new aiohttp session")
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def get_all_endpoints(self) -> List[str]:
        """Get all available endpoints as a flat list"""
        all_endpoints = []
        for category, endpoints in self.endpoints.items():
            all_endpoints.extend(endpoints)
        return all_endpoints
    
    def get_endpoints_by_category(self, category: str) -> List[str]:
        """Get endpoints for a specific category"""
        return self.endpoints.get(category, [])
    
    def build_url(self, function: str, **params) -> str:
        """Build Alpha Vantage API URL with parameters"""
        query_params = {
            'function': function,
            'apikey': self.api_key
        }
        query_params.update(params)
        return f"{self.BASE_URL}?{urlencode(query_params)}"
    
    async def _respect_rate_limit(self):
        """Ensure we respect API rate limits with adaptive delays"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.current_rate_limit_delay:
            sleep_time = self.current_rate_limit_delay - time_since_last
            logger.debug(f"⏱️ Rate limiting: sleeping {sleep_time:.2f}s (adaptive delay: {self.current_rate_limit_delay:.1f}s)")
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    async def fetch_endpoint(self, function: str, ticker: Optional[str] = None, **params) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Fetch data from a single Alpha Vantage endpoint with intelligent API key rotation and caching
        
        Returns:
            Tuple of (success: bool, data: Dict, error: str)
        """
        # Check circuit breaker
        if self._is_circuit_breaker_open():
            return False, None, "Circuit breaker is open - too many recent failures"
        
        await self.ensure_session()
        
        # Check cache for fundamental endpoints
        if self._is_fundamental_endpoint(function) and ticker:
            cache_key = self._get_cache_key(function, ticker, **params)
            cached_data = self._get_cached_data(cache_key)
            if cached_data:
                return True, cached_data, None
        
        # Build parameters
        request_params = dict(params)
        if ticker and self._endpoint_needs_symbol(function):
            request_params['symbol'] = ticker
        
        # Special parameter handling
        request_params = self._prepare_endpoint_params(function, request_params)
        
        # Track retry attempts for current key
        current_key_failures = 0
        max_total_retries = len(self.api_keys) * self.max_retries_same_key
        total_attempts = 0
        
        while total_attempts < max_total_retries:
            # Apply rate limiting before each request
            await self._respect_rate_limit()
            
            # Update URL with current API key
            url = self.build_url(function, **request_params)
            
            current_key_info = self.get_current_key_info()
            logger.debug(f"🌐 [API Key #{current_key_info['key_number']} - Attempt {current_key_failures + 1}] Fetching {function} for {ticker or 'N/A'}")
            
            try:
                self.total_calls += 1
                self.key_stats[self.current_key_index]['total_calls'] += 1
                total_attempts += 1
                
                if self.session is None:
                    raise RuntimeError("Session not properly initialized")
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for Alpha Vantage API errors
                        if self._is_api_error(data):
                            error_msg = self._extract_error_message(data)
                            
                            # Check if it's a rate limit error
                            if self._is_rate_limit_error(error_msg):
                                logger.warning(f"🚫 [API Key #{current_key_info['key_number']}] Rate limited for {function}: {error_msg}")
                                self.rate_limited_calls += 1
                                self.key_stats[self.current_key_index]['rate_limited_calls'] += 1
                                self.key_failure_counts[self.current_key_index] += 1
                                current_key_failures += 1
                                
                                # Increase delay for rate limiting
                                self._increase_rate_limit_delay()
                                self._record_failure()
                                
                                # Should we retry with same key or rotate?
                                if self._should_retry_with_same_key(current_key_failures):
                                    # Wait longer before retrying with same key
                                    backoff_delay = 2 ** current_key_failures  # Exponential backoff: 2s, 4s, 8s
                                    logger.info(f"⏳ Backing off for {backoff_delay}s before retrying with same key...")
                                    await asyncio.sleep(backoff_delay)
                                    continue
                                else:
                                    # Try rotating to next API key
                                    if self.rotate_api_key():
                                        current_key_failures = 0  # Reset failure count for new key
                                        logger.info(f"🔄 Retrying {function} with new API key...")
                                        continue
                                    else:
                                        return False, None, f"All API keys rate limited: {error_msg}"
                            else:
                                logger.warning(f"⚠️ [API Key #{current_key_info['key_number']}] API error for {function}: {error_msg}")
                                self.failed_calls += 1
                                self.key_stats[self.current_key_index]['failed_calls'] += 1
                                return False, None, error_msg
                        
                        # Success!
                        self.successful_calls += 1
                        self.key_stats[self.current_key_index]['successful_calls'] += 1
                        self.key_last_success[self.current_key_index] = time.time()
                        
                        # Cache fundamental data
                        if self._is_fundamental_endpoint(function) and ticker:
                            cache_key = self._get_cache_key(function, ticker, **request_params)
                            self._cache_data(cache_key, data)
                        
                        # Reduce rate limit delay on success
                        self._decrease_rate_limit_delay()
                        
                        logger.debug(f"✅ [API Key #{current_key_info['key_number']}] Successfully fetched {function}")
                        
                        # Anti-automation feature: pause after a number of successful requests
                        self.successful_requests += 1
                        if self.successful_requests >= self.pause_after_requests:
                            logger.info(f"⏸️ Pausing for {self.pause_duration} seconds to avoid automation detection...")
                            await asyncio.sleep(self.pause_duration)
                            self.successful_requests = 0  # Reset counter after pause
                        
                        return True, data, None
                        
                    else:
                        error_msg = f"HTTP {response.status}: {response.reason}"
                        logger.error(f"❌ [API Key #{current_key_info['key_number']}] HTTP error for {function}: {error_msg}")
                        self.failed_calls += 1
                        self.key_stats[self.current_key_index]['failed_calls'] += 1
                        self.key_failure_counts[self.current_key_index] += 1
                        current_key_failures += 1
                        self._record_failure()
                        
                        # For HTTP errors, try next key immediately
                        if not self.rotate_api_key():
                            return False, None, error_msg
                        current_key_failures = 0
                        continue
                        
            except asyncio.TimeoutError:
                error_msg = "Request timeout"
                logger.error(f"⏱️ [API Key #{current_key_info['key_number']}] Timeout for {function}")
                self.failed_calls += 1
                self.key_stats[self.current_key_index]['failed_calls'] += 1
                self.key_failure_counts[self.current_key_index] += 1
                current_key_failures += 1
                
                # For timeout, try next key
                if not self.rotate_api_key():
                    return False, None, error_msg
                current_key_failures = 0
                continue
                
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(f"💥 [API Key #{current_key_info['key_number']}] Unexpected error for {function}: {error_msg}")
                self.failed_calls += 1
                self.key_stats[self.current_key_index]['failed_calls'] += 1
                return False, None, error_msg
        
        # If we get here, all keys and retries have been exhausted
        return False, None, f"Failed to fetch {function} after {total_attempts} attempts with all {len(self.api_keys)} API keys"
    
    def _is_rate_limit_error(self, error_message: str) -> bool:
        """Check if error message indicates rate limiting"""
        rate_limit_indicators = [
            "rate limit",
            "requests per day",
            "requests per minute", 
            "quota exceeded",
            "too many requests"
        ]
        error_lower = error_message.lower()
        return any(indicator in error_lower for indicator in rate_limit_indicators)
    
    def _endpoint_needs_symbol(self, function: str) -> bool:
        """Check if endpoint requires a symbol parameter"""
        no_symbol_endpoints = {
            'LISTING_STATUS', 'IPO_CALENDAR', 'EARNINGS_CALENDAR',
            'REAL_GDP', 'REAL_GDP_PER_CAPITA', 'TREASURY_YIELD',
            'FEDERAL_FUNDS_RATE', 'CPI', 'INFLATION', 'RETAIL_SALES',
            'DURABLES', 'UNEMPLOYMENT', 'NONFARM_PAYROLL',
            'WTI', 'BRENT', 'NATURAL_GAS', 'COPPER', 'ALUMINUM',
            'WHEAT', 'CORN', 'COTTON', 'SUGAR', 'COFFEE'
        }
        return function not in no_symbol_endpoints
    
    def _prepare_endpoint_params(self, function: str, params: Dict) -> Dict:
        """Prepare endpoint-specific parameters"""
        # Set default parameters for specific endpoints
        if function == "TIME_SERIES_INTRADAY":
            params.setdefault('interval', '5min')
            params.setdefault('outputsize', 'compact')
        elif function in ["TIME_SERIES_DAILY", "TIME_SERIES_DAILY_ADJUSTED"]:
            params.setdefault('outputsize', 'compact')
        elif function == "NEWS_SENTIMENT":
            params.setdefault('limit', '50')
            if 'symbol' not in params:
                params.setdefault('topics', 'technology')
        elif function in self.endpoints.get('technical', []):
            params.setdefault('interval', 'daily')
            params.setdefault('time_period', '20')
            params.setdefault('series_type', 'close')
        
        return params
    
    def _is_api_error(self, data: Dict) -> bool:
        """Check if response contains an API error"""
        if isinstance(data, dict):
            return (
                "Error Message" in data or
                "Note" in data or
                "Information" in data or
                "error" in str(data).lower()
            )
        return False
    
    def _is_rate_limited(self, data: Dict) -> bool:
        """Check if response indicates rate limiting"""
        if isinstance(data, dict):
            text = str(data).lower()
            return (
                "api call frequency" in text or
                "thank you for using alpha vantage" in text or
                "premium" in text
            )
        return False
    
    def _extract_error_message(self, data: Dict) -> str:
        """Extract error message from API response"""
        if isinstance(data, dict):
            return (
                data.get("Error Message") or
                data.get("Note") or
                data.get("Information") or
                str(data)
            )
        return str(data)
    
    async def fetch_all_endpoints_for_ticker(self, ticker: str, endpoint_filter: Optional[List[str]] = None) -> Dict[str, Dict]:
        """
        Fetch data from all relevant endpoints for a given ticker
        
        Returns:
            Dict mapping endpoint names to their results
        """
        endpoints_to_fetch = endpoint_filter or self.get_all_endpoints()
        results = {}
        
        logger.info(f"📊 Fetching {len(endpoints_to_fetch)} endpoints for {ticker}")
        
        # Group endpoints by category for better organization
        for category, category_endpoints in self.endpoints.items():
            category_results = {}
            
            for endpoint in category_endpoints:
                if endpoint not in endpoints_to_fetch:
                    continue
                
                success, data, error = await self.fetch_endpoint(endpoint, ticker)
                
                category_results[endpoint] = {
                    'success': success,
                    'data': data,
                    'error': error,
                    'timestamp': datetime.utcnow().isoformat(),
                    'category': category
                }
                
                # Small delay between endpoints to be gentle on the API
                await asyncio.sleep(0.1)
            
            if category_results:
                results[category] = category_results
        
        logger.info(f"✅ Completed fetching for {ticker}: {self.successful_calls}/{self.total_calls} successful")
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get fetcher statistics"""
        total = self.total_calls
        success_rate = (self.successful_calls / total * 100) if total > 0 else 0
        
        return {
            'total_calls': total,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'rate_limited_calls': self.rate_limited_calls,
            'success_rate': round(success_rate, 2),
            'endpoints_available': len(self.get_all_endpoints()),
            'categories': list(self.endpoints.keys())
        }
    
    def reset_statistics(self):
        """Reset call statistics"""
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.rate_limited_calls = 0
    
    async def test_api_connectivity(self) -> Dict[str, Any]:
        """Test API connectivity with a simple call"""
        logger.info("🧪 Testing Alpha Vantage API connectivity...")
        
        success, data, error = await self.fetch_endpoint("GLOBAL_QUOTE", "AAPL")
        
        return {
            'connected': success,
            'api_key_valid': success and data is not None,
            'error': error,
            'test_timestamp': datetime.utcnow().isoformat(),
            'response_sample': data if success else None
        }
    
    def get_api_key_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics for all API keys"""
        stats = {
            'total_keys': len(self.api_keys),
            'current_key': self.get_current_key_info(),
            'total_rotations': self.key_rotations,
            'global_stats': {
                'total_calls': self.total_calls,
                'successful_calls': self.successful_calls,
                'failed_calls': self.failed_calls,
                'rate_limited_calls': self.rate_limited_calls,
                'success_rate': (self.successful_calls / self.total_calls * 100) if self.total_calls > 0 else 0
            },
            'per_key_stats': {}
        }
        
        for i, key_stat in self.key_stats.items():
            total_key_calls = key_stat['total_calls']
            success_rate = (key_stat['successful_calls'] / total_key_calls * 100) if total_key_calls > 0 else 0
            
            stats['per_key_stats'][f'key_{i+1}'] = {
                **key_stat,
                'success_rate': success_rate
            }
        
        return stats
    
    def log_api_key_summary(self):
        """Log a summary of API key usage"""
        stats = self.get_api_key_statistics()
        logger.info("📊 API Key Usage Summary:")
        logger.info(f"🔑 Total Keys: {stats['total_keys']}")
        logger.info(f"🔄 Current Key: #{stats['current_key']['key_number']} ({stats['current_key']['key_preview']})")
        logger.info(f"🔄 Total Rotations: {stats['total_rotations']}")
        logger.info(f"📈 Global Success Rate: {stats['global_stats']['success_rate']:.1f}%")
        
        # Show top performing keys
        sorted_keys = sorted(
            stats['per_key_stats'].items(),
            key=lambda x: x[1]['successful_calls'],
            reverse=True
        )
        
        logger.info("🏆 Top performing keys:")
        for key_name, key_data in sorted_keys[:3]:
            if key_data['total_calls'] > 0:
                logger.info(f"  {key_name}: {key_data['successful_calls']} successful calls ({key_data['success_rate']:.1f}%)")

    # ...existing code...
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_session()
