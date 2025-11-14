#!/usr/bin/env python3
"""
News Data Collectors
Handles news headlines and sentiment from multiple providers
"""

import asyncio
import logging
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
import hashlib
import re
# TextBlob for sentiment analysis (install with: pip install textblob)
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

from .config import config, PRIORITY_TICKERS
from .utils import http_client, db_manager, ingestion_logger, normalize_ticker, chunk_list, hash_content

logger = logging.getLogger(__name__)

class FinnhubNewsCollector:
    """Finnhub news collector - Real-time and historical news"""
    
    def __init__(self):
        self.provider = 'finnhub'
        self.call_count = 0
        self.max_calls = 9  # Save 1 for websocket
        self.base_url = config.api.finnhub_base_url
        self.api_key = config.api.finnhub_api_key
    
    async def collect_news(self, session_id: str, tickers: List[str]) -> Dict[str, Any]:
        """Collect company news from Finnhub"""
        results = {'records': 0, 'calls': 0, 'errors': []}
        
        if not self.api_key:
            logger.error("Finnhub API key not configured")
            return results
        
        try:
            # Get news for priority tickers first
            priority_tickers = [t for t in tickers if t in PRIORITY_TICKERS][:self.max_calls]
            
            for ticker in priority_tickers:
                if self.call_count >= self.max_calls:
                    break
                
                start_time = datetime.now()
                
                try:
                    # Get company news for last 7 days
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                    
                    url = f"{self.base_url}/company-news"
                    params = {
                        'symbol': ticker,
                        'from': start_date,
                        'to': end_date,
                        'token': self.api_key
                    }
                    
                    response = await http_client.request_with_retries(
                        url, params=params, provider=self.provider
                    )
                    
                    news_records = []
                    sentiment_records = []
                    
                    if isinstance(response, list):
                        for article in response:
                            if not article.get('headline') or not article.get('url'):
                                continue
                            
                            headline = article['headline']
                            url = article['url']
                            published_at = datetime.fromtimestamp(
                                article.get('datetime', 0), tz=timezone.utc
                            ) if article.get('datetime') else datetime.now(timezone.utc)
                            
                            # Calculate sentiment
                            sentiment_score, sentiment_label = self._analyze_sentiment(headline)
                            
                            news_record = {
                                'ticker': normalize_ticker(ticker),
                                'headline': headline,
                                'url': url,
                                'source': 'finnhub',
                                'published_at': published_at,
                                'inserted_at': datetime.now(timezone.utc),
                                'category': article.get('category', 'general'),
                                'relevance_score': 1.0,  # Finnhub pre-filters by ticker
                                'overall_sentiment_score': sentiment_score,
                                'overall_sentiment_label': sentiment_label
                            }
                            news_records.append(news_record)
                            
                            # Create sentiment record
                            sentiment_record = {
                                'ticker': normalize_ticker(ticker),
                                'headline': headline,
                                'url': url,
                                'sentiment_score': sentiment_score,
                                'sentiment_label': sentiment_label,
                                'relevance_score': 1.0,
                                'source': 'finnhub',
                                'analyzed_at': datetime.now(timezone.utc)
                            }
                            sentiment_records.append(sentiment_record)
                    
                    # Bulk upsert
                    if news_records:
                        await db_manager.upsert_batch('news_headlines', news_records, ['url'])
                        results['records'] += len(news_records)
                    
                    if sentiment_records:
                        await db_manager.upsert_batch('news_sentiment', sentiment_records, ['url'])
                    
                    self.call_count += 1
                    results['calls'] += 1
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'company_news_{ticker}',
                        duration, 'success', len(news_records)
                    )
                    
                    logger.info(f"Finnhub: {ticker} - {len(news_records)} news articles")
                    
                except Exception as e:
                    duration = (datetime.now() - start_time).total_seconds()
                    error_msg = str(e)
                    results['errors'].append(f"{ticker}: {error_msg}")
                    
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'company_news_{ticker}',
                        duration, 'error', 0, error_msg
                    )
                    
                    logger.error(f"Finnhub {ticker} failed: {e}")
        
        except Exception as e:
            logger.error(f"Finnhub news collection failed: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def _analyze_sentiment(self, text: str) -> tuple[float, str]:
        """Analyze sentiment using TextBlob or simple keyword analysis"""
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity  # -1 to 1
                
                if polarity > 0.1:
                    label = 'positive'
                elif polarity < -0.1:
                    label = 'negative'
                else:
                    label = 'neutral'
                
                return polarity, label
            except:
                pass
        
        # Fallback to simple keyword analysis
        text_lower = text.lower()
        positive_words = ['good', 'great', 'excellent', 'positive', 'up', 'gain', 'profit', 'win', 'success', 'buy']
        negative_words = ['bad', 'terrible', 'negative', 'down', 'loss', 'fail', 'drop', 'crash', 'sell', 'decline']
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return 0.5, 'positive'
        elif neg_count > pos_count:
            return -0.5, 'negative'
        else:
            return 0.0, 'neutral'

class PerplexityNewsCollector:
    """Perplexity AI collector for market news summaries"""
    
    def __init__(self):
        self.provider = 'perplexity'
        self.call_count = 0
        self.max_calls = 3  # Expensive
        self.base_url = config.api.perplexity_base_url
        self.api_key = config.api.perplexity_api_key
    
    async def collect_news(self, session_id: str, tickers: List[str]) -> Dict[str, Any]:
        """Collect summarized market news from Perplexity"""
        results = {'records': 0, 'calls': 0, 'errors': []}
        
        if not self.api_key:
            logger.error("Perplexity API key not configured")
            return results
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Group tickers for batch processing
            ticker_chunks = chunk_list(PRIORITY_TICKERS[:15], 5)  # Top tickers only
            
            for i, chunk in enumerate(ticker_chunks[:self.max_calls]):
                if self.call_count >= self.max_calls:
                    break
                
                start_time = datetime.now()
                
                try:
                    ticker_list = ', '.join(chunk)
                    
                    prompt = f"""
                    Provide a market news summary for these stocks: {ticker_list}
                    
                    For each stock, include:
                    1. Latest significant news or events
                    2. Market sentiment (positive/negative/neutral)
                    3. Key financial metrics mentioned
                    4. Risk factors or opportunities
                    
                    Format as JSON with ticker as key and summary as value.
                    """
                    
                    data = {
                        'model': 'sonar-pro',
                        'messages': [
                            {'role': 'system', 'content': 'You are a professional financial analyst.'},
                            {'role': 'user', 'content': prompt}
                        ]
                    }
                    
                    url = f"{self.base_url.replace('/finance', '')}/chat/completions"
                    response = await http_client.request_with_retries(
                        url, headers=headers, data=data, method='POST', provider=self.provider
                    )
                    
                    news_records = []
                    sentiment_records = []
                    
                    if 'choices' in response and response['choices']:
                        content = response['choices'][0]['message']['content']
                        
                        # Try to extract JSON from response
                        try:
                            # Look for JSON in the response
                            json_match = re.search(r'```json\s*({.*?})\s*```', content, re.DOTALL)
                            if json_match:
                                summaries = json.loads(json_match.group(1))
                            else:
                                # Try parsing the whole content as JSON
                                summaries = json.loads(content)
                            
                            for ticker, summary in summaries.items():
                                if ticker.upper() in [t.upper() for t in chunk]:
                                    ticker_norm = normalize_ticker(ticker)
                                    
                                    # Calculate sentiment from summary
                                    sentiment_score, sentiment_label = self._analyze_sentiment(summary)
                                    
                                    news_record = {
                                        'ticker': ticker_norm,
                                        'headline': f"Market Summary for {ticker_norm}",
                                        'url': f"perplexity://market_summary/{ticker_norm}/{int(datetime.now().timestamp())}",
                                        'source': 'perplexity',
                                        'published_at': datetime.now(timezone.utc),
                                        'inserted_at': datetime.now(timezone.utc),
                                        'category': 'market_summary',
                                        'relevance_score': 1.0,
                                        'overall_sentiment_score': sentiment_score,
                                        'overall_sentiment_label': sentiment_label
                                    }
                                    news_records.append(news_record)
                                    
                                    sentiment_record = {
                                        'ticker': ticker_norm,
                                        'headline': f"Market Summary for {ticker_norm}",
                                        'url': news_record['url'],
                                        'sentiment_score': sentiment_score,
                                        'sentiment_label': sentiment_label,
                                        'relevance_score': 1.0,
                                        'source': 'perplexity',
                                        'analyzed_at': datetime.now(timezone.utc)
                                    }
                                    sentiment_records.append(sentiment_record)
                        
                        except json.JSONDecodeError:
                            # Fallback: create single summary record
                            summary_text = content[:500] if len(content) > 500 else content
                            sentiment_score, sentiment_label = self._analyze_sentiment(summary_text)
                            
                            for ticker in chunk:
                                ticker_norm = normalize_ticker(ticker)
                                
                                news_record = {
                                    'ticker': ticker_norm,
                                    'headline': f"Market Analysis Summary",
                                    'url': f"perplexity://batch_summary/{i}/{int(datetime.now().timestamp())}",
                                    'source': 'perplexity',
                                    'published_at': datetime.now(timezone.utc),
                                    'inserted_at': datetime.now(timezone.utc),
                                    'category': 'market_analysis',
                                    'relevance_score': 0.8,
                                    'overall_sentiment_score': sentiment_score,
                                    'overall_sentiment_label': sentiment_label
                                }
                                news_records.append(news_record)
                    
                    # Bulk upsert
                    if news_records:
                        await db_manager.upsert_batch('news_headlines', news_records, ['url'])
                        results['records'] += len(news_records)
                    
                    if sentiment_records:
                        await db_manager.upsert_batch('news_sentiment', sentiment_records, ['url'])
                    
                    self.call_count += 1
                    results['calls'] += 1
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'market_summary_batch_{i}',
                        duration, 'success', len(news_records)
                    )
                    
                    logger.info(f"Perplexity: Batch {i+1} - {len(news_records)} summaries")
                    
                except Exception as e:
                    duration = (datetime.now() - start_time).total_seconds()
                    error_msg = str(e)
                    results['errors'].append(error_msg)
                    
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'market_summary_batch_{i}',
                        duration, 'error', 0, error_msg
                    )
                    
                    logger.error(f"Perplexity batch {i} failed: {e}")
        
        except Exception as e:
            logger.error(f"Perplexity news collection failed: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def _analyze_sentiment(self, text: str) -> tuple[float, str]:
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            return polarity, label
        except:
            return 0.0, 'neutral'

class GoogleNewsCollector:
    """Google News RSS collector"""
    
    def __init__(self):
        self.provider = 'google_news'
        self.call_count = 0
        self.max_calls = 10
        self.base_url = 'https://news.google.com/rss/search'
    
    async def collect_news(self, session_id: str, tickers: List[str]) -> Dict[str, Any]:
        """Collect news from Google News RSS"""
        results = {'records': 0, 'calls': 0, 'errors': []}
        
        try:
            # Search for top tickers
            priority_tickers = [t for t in tickers if t in PRIORITY_TICKERS][:self.max_calls]
            
            for ticker in priority_tickers:
                if self.call_count >= self.max_calls:
                    break
                
                start_time = datetime.now()
                
                try:
                    # Search for ticker + stock news
                    query = f"{ticker} stock"
                    params = {
                        'q': query,
                        'hl': 'en-US',
                        'gl': 'US',
                        'ceid': 'US:en'
                    }
                    
                    response = await http_client.request_with_retries(
                        self.base_url, params=params, provider=self.provider
                    )
                    
                    news_records = []
                    sentiment_records = []
                    
                    if 'data' in response:
                        # Parse XML
                        try:
                            root = ET.fromstring(response['data'])
                            
                            for item in root.findall('.//item'):
                                title_elem = item.find('title')
                                link_elem = item.find('link')
                                pub_date_elem = item.find('pubDate')
                                
                                if title_elem is not None and link_elem is not None:
                                    headline = title_elem.text or ""
                                    url = link_elem.text or ""
                                    
                                    if not headline or not url:
                                        continue
                                    
                                    # Parse publication date
                                    published_at = datetime.now(timezone.utc)
                                    if pub_date_elem is not None:
                                        try:
                                            # Parse RFC 2822 date format
                                            from email.utils import parsedate_to_datetime
                                            published_at = parsedate_to_datetime(pub_date_elem.text)
                                        except:
                                            pass
                                    
                                    # Calculate sentiment
                                    sentiment_score, sentiment_label = self._analyze_sentiment(headline)
                                    
                                    # Calculate relevance (simple keyword matching)
                                    relevance_score = self._calculate_relevance(headline, ticker)
                                    
                                    if relevance_score > 0.3:  # Only include relevant articles
                                        news_record = {
                                            'ticker': normalize_ticker(ticker),
                                            'headline': headline,
                                            'url': url,
                                            'source': 'google_news',
                                            'published_at': published_at,
                                            'inserted_at': datetime.now(timezone.utc),
                                            'category': 'general',
                                            'relevance_score': relevance_score,
                                            'overall_sentiment_score': sentiment_score,
                                            'overall_sentiment_label': sentiment_label
                                        }
                                        news_records.append(news_record)
                                        
                                        sentiment_record = {
                                            'ticker': normalize_ticker(ticker),
                                            'headline': headline,
                                            'url': url,
                                            'sentiment_score': sentiment_score,
                                            'sentiment_label': sentiment_label,
                                            'relevance_score': relevance_score,
                                            'source': 'google_news',
                                            'analyzed_at': datetime.now(timezone.utc)
                                        }
                                        sentiment_records.append(sentiment_record)
                        
                        except ET.ParseError as e:
                            logger.warning(f"Failed to parse XML for {ticker}: {e}")
                    
                    # Bulk upsert
                    if news_records:
                        await db_manager.upsert_batch('news_headlines', news_records, ['url'])
                        results['records'] += len(news_records)
                    
                    if sentiment_records:
                        await db_manager.upsert_batch('news_sentiment', sentiment_records, ['url'])
                    
                    self.call_count += 1
                    results['calls'] += 1
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'news_search_{ticker}',
                        duration, 'success', len(news_records)
                    )
                    
                    logger.info(f"Google News: {ticker} - {len(news_records)} articles")
                    
                except Exception as e:
                    duration = (datetime.now() - start_time).total_seconds()
                    error_msg = str(e)
                    results['errors'].append(f"{ticker}: {error_msg}")
                    
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'news_search_{ticker}',
                        duration, 'error', 0, error_msg
                    )
                    
                    logger.error(f"Google News {ticker} failed: {e}")
        
        except Exception as e:
            logger.error(f"Google News collection failed: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def _analyze_sentiment(self, text: str) -> tuple[float, str]:
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            return polarity, label
        except:
            return 0.0, 'neutral'
    
    def _calculate_relevance(self, headline: str, ticker: str) -> float:
        """Calculate relevance score based on keyword matching"""
        headline_lower = headline.lower()
        ticker_lower = ticker.lower()
        
        # Direct ticker mention
        if ticker_lower in headline_lower:
            return 1.0
        
        # Company name variations (simplified)
        company_keywords = {
            'AAPL': ['apple', 'iphone', 'ios', 'mac'],
            'MSFT': ['microsoft', 'windows', 'azure', 'office'],
            'GOOGL': ['google', 'alphabet', 'android', 'chrome'],
            'TSLA': ['tesla', 'musk', 'electric vehicle', 'ev'],
            'NVDA': ['nvidia', 'gpu', 'ai chip', 'graphics'],
            'META': ['meta', 'facebook', 'instagram', 'whatsapp']
        }
        
        keywords = company_keywords.get(ticker.upper(), [])
        for keyword in keywords:
            if keyword in headline_lower:
                return 0.8
        
        # General finance keywords
        finance_keywords = ['stock', 'share', 'earnings', 'revenue', 'profit', 'market']
        for keyword in finance_keywords:
            if keyword in headline_lower:
                return 0.5
        
        return 0.1

class RedditCollector:
    """Reddit finance community collector"""
    
    def __init__(self):
        self.provider = 'reddit'
        self.call_count = 0
        self.max_calls = 10
        self.base_url = 'https://www.reddit.com'
        self.user_agent = 'finance-rag-agent by u/sandeep'
    
    async def collect_news(self, session_id: str, tickers: List[str]) -> Dict[str, Any]:
        """Collect finance posts from Reddit"""
        results = {'records': 0, 'calls': 0, 'errors': []}
        
        headers = {'User-Agent': self.user_agent}
        
        try:
            # Search for different ticker combinations
            priority_tickers = [t for t in tickers if t in PRIORITY_TICKERS][:5]
            
            for ticker in priority_tickers:
                if self.call_count >= self.max_calls:
                    break
                
                start_time = datetime.now()
                
                try:
                    # Search Reddit for ticker discussions
                    query = f'{ticker} stock finance'
                    params = {
                        'q': query,
                        'sort': 'new',
                        'limit': 25
                    }
                    
                    url = f"{self.base_url}/search.json"
                    response = await http_client.request_with_retries(
                        url, headers=headers, params=params, provider=self.provider
                    )
                    
                    news_records = []
                    sentiment_records = []
                    
                    if 'data' in response and 'children' in response['data']:
                        for post in response['data']['children']:
                            post_data = post.get('data', {})
                            
                            title = post_data.get('title', '')
                            selftext = post_data.get('selftext', '')
                            permalink = post_data.get('permalink', '')
                            subreddit = post_data.get('subreddit', '')
                            ups = post_data.get('ups', 0)
                            created_utc = post_data.get('created_utc', 0)
                            
                            if title and permalink:
                                # Calculate relevance
                                relevance_score = self._calculate_relevance(title + ' ' + selftext, ticker)
                                
                                if relevance_score > 0.3:  # Filter relevant posts
                                    # Combine title and text for sentiment
                                    content = f"{title}. {selftext[:200]}"
                                    sentiment_score, sentiment_label = self._analyze_sentiment(content)
                                    
                                    news_record = {
                                        'ticker': normalize_ticker(ticker),
                                        'headline': title,
                                        'url': f"https://reddit.com{permalink}",
                                        'source': 'reddit',
                                        'published_at': datetime.fromtimestamp(created_utc, tz=timezone.utc),
                                        'inserted_at': datetime.now(timezone.utc),
                                        'category': f'reddit_{subreddit}',
                                        'relevance_score': relevance_score,
                                        'overall_sentiment_score': sentiment_score,
                                        'overall_sentiment_label': sentiment_label
                                    }
                                    news_records.append(news_record)
                                    
                                    sentiment_record = {
                                        'ticker': normalize_ticker(ticker),
                                        'headline': title,
                                        'url': news_record['url'],
                                        'sentiment_score': sentiment_score,
                                        'sentiment_label': sentiment_label,
                                        'relevance_score': relevance_score,
                                        'source': 'reddit',
                                        'analyzed_at': datetime.now(timezone.utc)
                                    }
                                    sentiment_records.append(sentiment_record)
                    
                    # Bulk upsert
                    if news_records:
                        await db_manager.upsert_batch('news_headlines', news_records, ['url'])
                        results['records'] += len(news_records)
                    
                    if sentiment_records:
                        await db_manager.upsert_batch('news_sentiment', sentiment_records, ['url'])
                    
                    self.call_count += 1
                    results['calls'] += 1
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'search_{ticker}',
                        duration, 'success', len(news_records)
                    )
                    
                    logger.info(f"Reddit: {ticker} - {len(news_records)} posts")
                    
                except Exception as e:
                    duration = (datetime.now() - start_time).total_seconds()
                    error_msg = str(e)
                    results['errors'].append(f"{ticker}: {error_msg}")
                    
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'search_{ticker}',
                        duration, 'error', 0, error_msg
                    )
                    
                    logger.error(f"Reddit {ticker} failed: {e}")
        
        except Exception as e:
            logger.error(f"Reddit collection failed: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def _analyze_sentiment(self, text: str) -> tuple[float, str]:
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            return polarity, label
        except:
            return 0.0, 'neutral'
    
    def _calculate_relevance(self, content: str, ticker: str) -> float:
        """Calculate relevance score"""
        content_lower = content.lower()
        ticker_lower = ticker.lower()
        
        if ticker_lower in content_lower:
            return 1.0
        
        # Basic keyword matching (can be enhanced)
        finance_keywords = ['stock', 'invest', 'buy', 'sell', 'price', 'market', 'earnings']
        keyword_count = sum(1 for keyword in finance_keywords if keyword in content_lower)
        
        return min(keyword_count * 0.2, 0.8)

class NewsOrchestrator:
    """Orchestrates news collection from all providers"""
    
    def __init__(self):
        self.collectors = {
            'finnhub': FinnhubNewsCollector(),
            'perplexity': PerplexityNewsCollector(),
            'google_news': GoogleNewsCollector(),
            'reddit': RedditCollector()
        }
    
    async def collect_all(self, session_id: str, tickers: Optional[List[str]] = None) -> Dict[str, Any]:
        """Collect news from all providers"""
        tickers = tickers or PRIORITY_TICKERS
        results = {
            'total_records': 0,
            'total_calls': 0,
            'providers': {},
            'errors': []
        }
        
        logger.info(f"Starting news collection for {len(tickers)} tickers")
        
        # Run collectors in parallel
        tasks = []
        for name, collector in self.collectors.items():
            task = asyncio.create_task(
                collector.collect_news(session_id, tickers),
                name=f"news_{name}"
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
                
                logger.info(f"News - {provider_name}: {provider_results['records']} records, {provider_results['calls']} calls")
                
            except Exception as e:
                error_msg = f"{provider_name} failed: {str(e)}"
                results['errors'].append(error_msg)
                logger.error(error_msg)
        
        logger.info(f"News collection complete: {results['total_records']} records, {results['total_calls']} calls")
        return results
