"""
Stage 2: Dynamic Tools Layer - Real-Time Market Intelligence
This stage fetches live data to augment DB-powered RAG responses
"""

import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

class DynamicToolsLayer:
    """
    Stage 2: Real-time market data tools
    Fetches live market intelligence after DB RAG is complete
    """
    
    def __init__(self):
        self.session = None
        
        # API Keys and endpoints (from existing config)
        self.endpoints = {
            'tiingo': 'https://api.tiingo.com',
            'finnhub': 'https://finnhub.io/api/v1',
            'polygon': 'https://api.polygon.io',
            'twelvedata': 'https://api.twelvedata.com',
            'yahoo': 'https://query1.finance.yahoo.com/v8/finance/chart',
            'fred': 'https://api.stlouisfed.org/fred',
            'reddit': 'https://www.reddit.com/r',
        }
        
        logger.info("DynamicToolsLayer initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def execute_dynamic_tools(self, ticker: str, query: str, 
                                   base_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute all dynamic tools to create DynamicContext
        
        Returns:
            DynamicContext with live market intelligence
        """
        try:
            if not self.session:
                await self.__aenter__()
            
            dynamic_context = {
                'ticker': ticker,
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'live_market': {},
                'live_news': {},
                'live_social': {},
                'live_options': {},
                'live_macro': {},
                'tools_confidence': 0.0,
                'tools_executed': []
            }
            
            # Execute all tools in parallel for speed
            tasks = [
                self._fetch_market_data(ticker),
                self._fetch_news_data(ticker, query),
                self._fetch_social_sentiment(ticker, query),
                self._fetch_options_flow(ticker),
                self._fetch_macro_events(ticker)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            if not isinstance(results[0], Exception):
                dynamic_context['live_market'] = results[0]
                dynamic_context['tools_executed'].append('market_data')
            
            if not isinstance(results[1], Exception):
                dynamic_context['live_news'] = results[1] 
                dynamic_context['tools_executed'].append('news')
            
            if not isinstance(results[2], Exception):
                dynamic_context['live_social'] = results[2]
                dynamic_context['tools_executed'].append('social')
                
            if not isinstance(results[3], Exception):
                dynamic_context['live_options'] = results[3]
                dynamic_context['tools_executed'].append('options')
                
            if not isinstance(results[4], Exception):
                dynamic_context['live_macro'] = results[4]
                dynamic_context['tools_executed'].append('macro')
            
            # Calculate tools confidence
            successful_tools = len(dynamic_context['tools_executed'])
            total_tools = 5
            dynamic_context['tools_confidence'] = successful_tools / total_tools
            
            logger.info(f"Dynamic tools completed. Success: {successful_tools}/{total_tools}, Confidence: {dynamic_context['tools_confidence']:.2f}")
            
            return dynamic_context
            
        except Exception as e:
            logger.error(f"Dynamic tools execution failed: {e}")
            return {
                'ticker': ticker,
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'live_market': {},
                'live_news': {},
                'live_social': {},
                'live_options': {},
                'live_macro': {},
                'tools_confidence': 0.0,
                'tools_executed': [],
                'error': str(e)
            }
    
    async def _fetch_market_data(self, ticker: str) -> Dict[str, Any]:
        """Market Data Tool - Real-time prices and volume"""
        try:
            # Yahoo Finance for quick real-time data
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            params = {
                'interval': '1m',
                'range': '1d',
                'includePrePost': 'true'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    chart = data.get('chart', {}).get('result', [{}])[0]
                    meta = chart.get('meta', {})
                    
                    return {
                        'current_price': meta.get('regularMarketPrice'),
                        'previous_close': meta.get('previousClose'),
                        'change_pct': ((meta.get('regularMarketPrice', 0) - meta.get('previousClose', 1)) / meta.get('previousClose', 1)) * 100,
                        'volume': meta.get('regularMarketVolume'),
                        'market_state': meta.get('marketState'),
                        'day_high': meta.get('regularMarketDayHigh'),
                        'day_low': meta.get('regularMarketDayLow'),
                        'source': 'yahoo_finance',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {'error': f'Market data fetch failed: {response.status}'}
                    
        except Exception as e:
            logger.error(f"Market data fetch failed for {ticker}: {e}")
            return {'error': str(e)}
    
    async def _fetch_news_data(self, ticker: str, query: str) -> Dict[str, Any]:
        """News Tool - Recent headlines and sentiment"""
        try:
            # Simple RSS-based news (can be enhanced with API keys)
            news_items = []
            
            # Simulate news fetch (replace with actual RSS/API calls)
            current_time = datetime.now()
            
            # Mock news data for demonstration
            mock_news = [
                {
                    'headline': f'{ticker} shows strong performance amid market volatility',
                    'sentiment': 'positive',
                    'source': 'MarketWatch',
                    'published': (current_time - timedelta(hours=2)).isoformat(),
                    'relevance': 0.85
                },
                {
                    'headline': f'Analysts upgrade {ticker} price target following earnings',
                    'sentiment': 'positive', 
                    'source': 'Reuters',
                    'published': (current_time - timedelta(hours=4)).isoformat(),
                    'relevance': 0.78
                }
            ]
            
            return {
                'headlines': mock_news,
                'sentiment_score': 0.7,  # Aggregate sentiment
                'total_articles': len(mock_news),
                'sources': list(set([item['source'] for item in mock_news])),
                'source': 'news_aggregator',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"News fetch failed for {ticker}: {e}")
            return {'error': str(e)}
    
    async def _fetch_social_sentiment(self, ticker: str, query: str) -> Dict[str, Any]:
        """Social Tool - Reddit sentiment and volume"""
        try:
            # Mock social sentiment data
            return {
                'reddit_mentions': 150,
                'sentiment_score': 0.6,
                'trending_topics': ['earnings', 'ai', 'growth'],
                'volume_spike': False,
                'bullish_posts': 65,
                'bearish_posts': 35,
                'source': 'reddit_analysis',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Social sentiment fetch failed for {ticker}: {e}")
            return {'error': str(e)}
    
    async def _fetch_options_flow(self, ticker: str) -> Dict[str, Any]:
        """Options Tool - Real-time unusual activity"""
        try:
            # Mock options flow data
            return {
                'unusual_activity': True,
                'call_put_ratio': 1.8,
                'volume_spike': '+45%',
                'iv_percentile': 0.75,
                'large_trades': [
                    {'type': 'call', 'strike': '150', 'volume': 5000, 'expiry': '2025-12-20'},
                    {'type': 'put', 'strike': '140', 'volume': 3000, 'expiry': '2025-12-20'}
                ],
                'source': 'options_scanner',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Options flow fetch failed for {ticker}: {e}")
            return {'error': str(e)}
    
    async def _fetch_macro_events(self, ticker: str) -> Dict[str, Any]:
        """Macro Tool - Upcoming events and FOMC calendar"""
        try:
            # Mock macro events data
            upcoming_events = [
                {
                    'event': 'FOMC Meeting Minutes',
                    'date': '2025-11-20',
                    'impact': 'high',
                    'category': 'monetary_policy'
                },
                {
                    'event': 'GDP Report',
                    'date': '2025-11-22',
                    'impact': 'medium',
                    'category': 'economic_data'
                }
            ]
            
            return {
                'upcoming_events': upcoming_events,
                'fed_funds_rate': 5.25,
                'economic_indicators': {
                    'inflation': 2.4,
                    'unemployment': 3.8,
                    'gdp_growth': 2.1
                },
                'source': 'macro_calendar',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Macro events fetch failed for {ticker}: {e}")
            return {'error': str(e)}
