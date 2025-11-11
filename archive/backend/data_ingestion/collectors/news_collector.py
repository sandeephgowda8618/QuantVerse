"""
News data collector for Finnhub WebSocket and Perplexity Finance.
Collects real-time headlines, trade halts, and earnings alerts.
"""

import logging
import asyncio
import json
import websockets
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
import feedparser
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..config.settings import settings, TRACKED_ASSETS
from ..db.postgres_handler import db, insert_news_headline
from ..utils.logging_utils import setup_logger

logger = setup_logger(__name__)

class NewsCollector:
    """Collects news data from Finnhub and Perplexity APIs."""
    
    def __init__(self):
        self.finnhub_ws_url = f"{settings.FINNHUB_WEBSOCKET_URL}?token={settings.FINNHUB_API_KEY}"
        self.finnhub_headers = {'X-Finnhub-Token': settings.FINNHUB_API_KEY}
        self.perplexity_headers = {
            'Authorization': f'Bearer {settings.PERPLEXITY_API_KEY}',
            'Content-Type': 'application/json'
        }
        
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
        
        self.websocket = None
        self.is_collecting = False
    
    def get_relevant_tickers(self) -> List[str]:
        """Get all tracked tickers for news collection."""
        all_tickers = []
        for asset_type, tickers in TRACKED_ASSETS.items():
            all_tickers.extend(tickers)
        return all_tickers
    
    def collect_finnhub_news(self, category: str = "general", limit: int = 50) -> List[Dict[str, Any]]:
        """
        Collect news from Finnhub REST API.
        
        Args:
            category: News category (general, forex, crypto, merger)
            limit: Maximum number of articles to fetch
        """
        if not settings.FINNHUB_API_KEY:
            logger.warning("Finnhub API key not configured")
            return []
        
        try:
            url = f"{settings.FINNHUB_BASE_URL}/news"
            params = {
                'category': category,
                'token': settings.FINNHUB_API_KEY
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            news_data = response.json()
            
            if not news_data:
                logger.warning(f"No Finnhub news data returned for category: {category}")
                return []
            
            # Limit results
            news_data = news_data[:limit]
            
            # Process and standardize the data
            processed_news = []
            for article in news_data:
                try:
                    processed_article = {
                        'headline': article.get('headline', ''),
                        'url': article.get('url', ''),
                        'source': f"finnhub_{category}",
                        'published_at': datetime.fromtimestamp(article.get('datetime', 0)),
                        'ticker': self.extract_ticker_from_headline(article.get('headline', '')),
                        'raw_data': article
                    }
                    processed_news.append(processed_article)
                except Exception as e:
                    logger.warning(f"Failed to process Finnhub article: {e}")
                    continue
            
            logger.info(f"Collected {len(processed_news)} Finnhub news articles")
            return processed_news
            
        except Exception as e:
            logger.error(f"Failed to collect Finnhub news: {e}")
            return []
    
    def collect_company_news(self, ticker: str, days_back: int = 1) -> List[Dict[str, Any]]:
        """
        Collect company-specific news from Finnhub.
        
        Args:
            ticker: Company ticker symbol
            days_back: Number of days to look back
        """
        if not settings.FINNHUB_API_KEY:
            return []
        
        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)
            
            url = f"{settings.FINNHUB_BASE_URL}/company-news"
            params = {
                'symbol': ticker,
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d'),
                'token': settings.FINNHUB_API_KEY
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            news_data = response.json()
            
            if not news_data:
                return []
            
            # Process articles
            processed_news = []
            for article in news_data:
                try:
                    processed_article = {
                        'headline': article.get('headline', ''),
                        'url': article.get('url', ''),
                        'source': 'finnhub_company',
                        'published_at': datetime.fromtimestamp(article.get('datetime', 0)),
                        'ticker': ticker,
                        'raw_data': article
                    }
                    processed_news.append(processed_article)
                except Exception as e:
                    logger.warning(f"Failed to process company news for {ticker}: {e}")
                    continue
            
            logger.info(f"Collected {len(processed_news)} company news articles for {ticker}")
            return processed_news
            
        except Exception as e:
            logger.error(f"Failed to collect company news for {ticker}: {e}")
            return []
    
    def collect_perplexity_finance_news(self, query: str = "financial markets news") -> List[Dict[str, Any]]:
        """
        Collect summarized financial news from Perplexity.
        
        Args:
            query: Search query for financial news
        """
        if not settings.PERPLEXITY_API_KEY:
            logger.warning("Perplexity API key not configured")
            return []
        
        try:
            url = f"{settings.PERPLEXITY_BASE_URL}/chat/completions"
            
            payload = {
                "model": "sonar-pro",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a financial news summarizer. Provide concise, factual summaries of recent financial market developments."
                    },
                    {
                        "role": "user", 
                        "content": f"Summarize the latest {query} from the past 24 hours. Focus on market-moving events, regulatory changes, and major corporate news."
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            response = self.session.post(
                url, 
                headers=self.perplexity_headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            if not result.get('choices'):
                logger.warning("No Perplexity response received")
                return []
            
            content = result['choices'][0]['message']['content']
            
            # Create a single news entry with the summary
            processed_article = {
                'headline': f"Financial Market Summary: {query}",
                'url': '',
                'source': 'perplexity_finance',
                'published_at': datetime.now(),
                'ticker': None,  # General market news
                'content': content,
                'raw_data': result
            }
            
            logger.info("Collected Perplexity finance summary")
            return [processed_article]
            
        except Exception as e:
            logger.error(f"Failed to collect Perplexity finance news: {e}")
            return []
    
    def extract_ticker_from_headline(self, headline: str) -> Optional[str]:
        """
        Extract ticker symbol from news headline.
        Simple keyword matching approach.
        """
        if not headline:
            return None
        
        headline_upper = headline.upper()
        
        # Check for explicit ticker mentions
        all_tickers = self.get_relevant_tickers()
        for ticker in all_tickers:
            # Look for ticker in parentheses like "Apple (AAPL)" or just "AAPL"
            if f"({ticker})" in headline_upper or f" {ticker} " in headline_upper:
                return ticker
        
        # Check for company name mentions (basic mapping)
        company_mappings = {
            'APPLE': 'AAPL',
            'TESLA': 'TSLA', 
            'MICROSOFT': 'MSFT',
            'GOOGLE': 'GOOGL',
            'AMAZON': 'AMZN',
            'BITCOIN': 'BTC',
            'ETHEREUM': 'ETH'
        }
        
        for company, ticker in company_mappings.items():
            if company in headline_upper:
                return ticker
        
        return None
    
    async def start_finnhub_websocket(self, symbols: Optional[List[str]] = None):
        """
        Start Finnhub WebSocket connection for real-time news.
        
        Args:
            symbols: List of symbols to subscribe to
        """
        if not settings.FINNHUB_API_KEY:
            logger.warning("Finnhub API key not configured for WebSocket")
            return
        
        if symbols is None:
            symbols = self.get_relevant_tickers()[:10]  # Limit to avoid rate limits
        
        try:
            self.websocket = await websockets.connect(self.finnhub_ws_url)
            self.is_collecting = True
            
            # Subscribe to news for each symbol
            for symbol in symbols:
                subscribe_msg = json.dumps({"type": "subscribe", "symbol": symbol})
                await self.websocket.send(subscribe_msg)
                logger.info(f"Subscribed to Finnhub news for {symbol}")
            
            # Listen for messages
            logger.info("Started Finnhub WebSocket news collection")
            await self.listen_to_websocket()
            
        except Exception as e:
            logger.error(f"Finnhub WebSocket connection failed: {e}")
            self.is_collecting = False
    
    async def listen_to_websocket(self):
        """Listen to WebSocket messages and process news."""
        try:
            async for message in self.websocket:
                if not self.is_collecting:
                    break
                
                try:
                    data = json.loads(message)
                    
                    # Process different message types
                    if data.get('type') == 'news':
                        await self.process_websocket_news(data)
                    elif data.get('type') == 'trade':
                        # Handle trade halt notifications
                        await self.process_trade_halt(data)
                    
                except json.JSONDecodeError:
                    logger.warning(f"Invalid WebSocket message: {message}")
                except Exception as e:
                    logger.error(f"Error processing WebSocket message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("Finnhub WebSocket connection closed")
        except Exception as e:
            logger.error(f"WebSocket listening error: {e}")
        finally:
            self.is_collecting = False
    
    async def process_websocket_news(self, news_data: Dict[str, Any]):
        """Process news data from WebSocket."""
        try:
            for news_item in news_data.get('data', []):
                headline = news_item.get('headline', '')
                if not headline:
                    continue
                
                processed_article = {
                    'headline': headline,
                    'url': news_item.get('url', ''),
                    'source': 'finnhub_websocket',
                    'published_at': datetime.fromtimestamp(news_item.get('datetime', 0)),
                    'ticker': news_item.get('symbol') or self.extract_ticker_from_headline(headline),
                    'raw_data': news_item
                }
                
                # Store in database
                await self.store_news_article(processed_article)
                
        except Exception as e:
            logger.error(f"Failed to process WebSocket news: {e}")
    
    async def process_trade_halt(self, trade_data: Dict[str, Any]):
        """Process trade halt notifications."""
        try:
            # Create a news entry for trade halts
            symbol = trade_data.get('s', '')
            if symbol:
                headline = f"Trade halt notification for {symbol}"
                processed_article = {
                    'headline': headline,
                    'url': '',
                    'source': 'finnhub_trade_halt',
                    'published_at': datetime.now(),
                    'ticker': symbol,
                    'raw_data': trade_data
                }
                
                await self.store_news_article(processed_article)
                logger.info(f"Processed trade halt for {symbol}")
                
        except Exception as e:
            logger.error(f"Failed to process trade halt: {e}")
    
    async def store_news_article(self, article: Dict[str, Any]):
        """Store a news article in the database."""
        try:
            headline_id = insert_news_headline(
                ticker=article.get('ticker') or '',
                headline=article['headline'],
                url=article.get('url', ''),
                source=article['source'],
                published_at=article['published_at'].isoformat()
            )
            
            if headline_id:
                logger.debug(f"Stored news article: {article['headline'][:50]}...")
                
        except Exception as e:
            logger.error(f"Failed to store news article: {e}")
    
    def store_news_batch(self, articles: List[Dict[str, Any]]) -> int:
        """Store multiple news articles in batch."""
        stored_count = 0
        
        for article in articles:
            try:
                headline_id = insert_news_headline(
                    ticker=article.get('ticker') or '',
                    headline=article['headline'],
                    url=article.get('url', ''), 
                    source=article['source'],
                    published_at=article['published_at'].isoformat()
                )
                
                if headline_id:
                    stored_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to store article: {e}")
                continue
        
        logger.info(f"Stored {stored_count} news articles in database")
        return stored_count
    
    async def stop_websocket(self):
        """Stop WebSocket connection."""
        self.is_collecting = False
        if self.websocket:
            await self.websocket.close()
            logger.info("Finnhub WebSocket connection stopped")
    
    async def run_collection_cycle(self) -> Dict[str, Any]:
        """Run a complete news collection cycle."""
        start_time = datetime.now()
        logger.info("Starting news collection cycle")
        
        results = {
            'start_time': start_time.isoformat(),
            'articles_collected': 0,
            'articles_stored': 0,
            'sources_processed': [],
            'errors': [],
            'success': True
        }
        
        try:
            all_articles = []
            
            # Collect general Finnhub news
            if settings.FINNHUB_API_KEY:
                general_news = self.collect_finnhub_news(category="general", limit=20)
                all_articles.extend(general_news)
                results['sources_processed'].append("finnhub_general")
                
                # Collect crypto news
                crypto_news = self.collect_finnhub_news(category="crypto", limit=15)
                all_articles.extend(crypto_news)
                results['sources_processed'].append("finnhub_crypto")
                
                # Collect company-specific news for top tickers
                top_tickers = TRACKED_ASSETS.get('stocks', [])[:5]
                for ticker in top_tickers:
                    company_news = self.collect_company_news(ticker, days_back=1)
                    all_articles.extend(company_news)
                
                results['sources_processed'].append("finnhub_company")
            
            # Collect Perplexity finance summary
            if settings.PERPLEXITY_API_KEY:
                perplexity_news = self.collect_perplexity_finance_news()
                all_articles.extend(perplexity_news)
                results['sources_processed'].append("perplexity_finance")
            
            # Store articles in database
            if all_articles:
                stored_count = self.store_news_batch(all_articles)
                results['articles_collected'] = len(all_articles)
                results['articles_stored'] = stored_count
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"News collection completed in {duration:.2f}s: "
                       f"{results['articles_collected']} collected, {results['articles_stored']} stored")
            
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = duration
            
        except Exception as e:
            logger.error(f"News collection cycle failed: {e}")
            results['success'] = False
            results['errors'].append(str(e))
        
        return results

# Global collector instance
news_collector = NewsCollector()

# Convenience functions for external use
def collect_news() -> Dict[str, Any]:
    """Synchronous wrapper for news collection."""
    return asyncio.run(news_collector.run_collection_cycle())

def start_realtime_news_collection(symbols: Optional[List[str]] = None):
    """Start real-time news collection via WebSocket."""
    return asyncio.run(news_collector.start_finnhub_websocket(symbols))

def stop_realtime_news_collection():
    """Stop real-time news collection."""
    return asyncio.run(news_collector.stop_websocket())