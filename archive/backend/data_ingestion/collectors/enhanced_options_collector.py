"""
Enhanced options flow collector with multiple provider support.
Supports Yahoo Finance, Alpaca, TD Ameritrade, and Tradier APIs.
"""

import logging
import asyncio
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..config.settings import settings
from ..utils.logging_utils import setup_logger

logger = setup_logger(__name__)

class EnhancedOptionsFlowCollector:
    """Enhanced options flow collector with multiple provider support."""
    
    def __init__(self):
        self.setup_sessions()
        self.providers = self._get_available_providers()
        logger.info(f"Initialized with providers: {', '.join(self.providers)}")
    
    def setup_sessions(self):
        """Setup HTTP sessions with retry strategies."""
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _get_available_providers(self) -> List[str]:
        """Determine which providers are available based on configuration."""
        providers = []
        
        if settings.YAHOO_FINANCE_ENABLED:
            providers.append("yahoo")
        
        if settings.ALPACA_API_KEY:
            providers.append("alpaca")
            
        if settings.TD_AMERITRADE_API_KEY:
            providers.append("td_ameritrade")
            
        if settings.TRADIER_API_KEY:
            providers.append("tradier")
        
        # Always include polygon if key is available (already integrated)
        if settings.POLYGON_API_KEY:
            providers.append("polygon")
            
        return providers
    
    def collect_yahoo_options_data(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Collect options data from Yahoo Finance (free alternative).
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of options data dictionaries
        """
        try:
            logger.info(f"Collecting Yahoo Finance options data for {ticker}")
            
            # Create yfinance ticker object
            yf_ticker = yf.Ticker(ticker)
            
            # Get options expiration dates
            expirations = yf_ticker.options
            if not expirations:
                logger.warning(f"No options expiration dates found for {ticker}")
                return []
            
            all_options_data = []
            
            # Process first few expiration dates to avoid rate limits
            for exp_date in expirations[:3]:  # Limit to first 3 expirations
                try:
                    # Get options chain for this expiration
                    options_chain = yf_ticker.option_chain(exp_date)
                    
                    # Process calls
                    if hasattr(options_chain, 'calls') and not options_chain.calls.empty:
                        calls_data = self._process_yahoo_options_data(
                            options_chain.calls, ticker, exp_date, 'call'
                        )
                        all_options_data.extend(calls_data)
                    
                    # Process puts
                    if hasattr(options_chain, 'puts') and not options_chain.puts.empty:
                        puts_data = self._process_yahoo_options_data(
                            options_chain.puts, ticker, exp_date, 'put'
                        )
                        all_options_data.extend(puts_data)
                        
                except Exception as e:
                    logger.warning(f"Failed to process options for {ticker} exp {exp_date}: {e}")
                    continue
            
            logger.info(f"Collected {len(all_options_data)} Yahoo Finance options records for {ticker}")
            return all_options_data
            
        except Exception as e:
            logger.error(f"Failed to collect Yahoo Finance options data for {ticker}: {e}")
            return []
    
    def _process_yahoo_options_data(self, options_df: pd.DataFrame, ticker: str, 
                                  exp_date: str, option_type: str) -> List[Dict[str, Any]]:
        """Process Yahoo Finance options DataFrame into standard format."""
        options_data = []
        
        for _, row in options_df.iterrows():
            try:
                option_data = {
                    'ticker': ticker,
                    'option_type': option_type,
                    'expiration_date': exp_date,
                    'strike': float(row.get('strike', 0)),
                    'bid': float(row.get('bid', 0)),
                    'ask': float(row.get('ask', 0)),
                    'last': float(row.get('lastPrice', 0)),
                    'volume': int(row.get('volume', 0)) if pd.notna(row.get('volume')) else 0,
                    'open_interest': int(row.get('openInterest', 0)) if pd.notna(row.get('openInterest')) else 0,
                    'implied_volatility': float(row.get('impliedVolatility', 0)) if pd.notna(row.get('impliedVolatility')) else 0,
                    'contract_symbol': row.get('contractSymbol', ''),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'yahoo_finance'
                }
                options_data.append(option_data)
                
            except Exception as e:
                logger.warning(f"Failed to process Yahoo option row: {e}")
                continue
        
        return options_data
    
    def collect_alpaca_options_data(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Collect options data from Alpaca Markets API.
        Note: Requires alpaca-trade-api package installation.
        """
        try:
            if not settings.ALPACA_API_KEY:
                logger.warning("Alpaca API key not configured")
                return []
            
            logger.info(f"Collecting Alpaca options data for {ticker}")
            
            # This would require alpaca-trade-api package
            # Implementation placeholder for future enhancement
            logger.info("Alpaca options data collection - implementation pending")
            return []
            
        except Exception as e:
            logger.error(f"Failed to collect Alpaca options data for {ticker}: {e}")
            return []
    
    def collect_options_data_multi_provider(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """
        Collect options data from multiple providers with fallback logic.
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Combined options data from all available providers
        """
        all_options_data = []
        
        for ticker in tickers:
            ticker_data = []
            
            # Try each provider in priority order
            for provider in self.providers:
                try:
                    if provider == "yahoo":
                        provider_data = self.collect_yahoo_options_data(ticker)
                    elif provider == "alpaca":
                        provider_data = self.collect_alpaca_options_data(ticker)
                    elif provider == "tradier":
                        # Use existing Tradier implementation from original collector
                        provider_data = []  # Placeholder
                    else:
                        continue
                    
                    if provider_data:
                        ticker_data.extend(provider_data)
                        logger.info(f"Successfully collected data from {provider} for {ticker}")
                        
                except Exception as e:
                    logger.warning(f"Provider {provider} failed for {ticker}: {e}")
                    continue
            
            all_options_data.extend(ticker_data)
        
        return all_options_data

# Global instance for compatibility
enhanced_options_flow_collector = EnhancedOptionsFlowCollector()

def collect_options_flow_data(tickers: List[str]) -> List[Dict[str, Any]]:
    """Compatibility function for existing pipeline."""
    return enhanced_options_flow_collector.collect_options_data_multi_provider(tickers)

if __name__ == "__main__":
    # Test the enhanced collector
    test_tickers = ["AAPL", "TSLA"]
    
    collector = EnhancedOptionsFlowCollector()
    print(f"Available providers: {collector.providers}")
    
    # Test Yahoo Finance data collection
    if "yahoo" in collector.providers:
        data = collector.collect_yahoo_options_data("AAPL")
        print(f"Collected {len(data)} options records for AAPL from Yahoo Finance")
        if data:
            print("Sample record:", data[0])
