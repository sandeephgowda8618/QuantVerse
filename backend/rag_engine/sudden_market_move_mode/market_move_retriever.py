"""
Market Move Evidence Retriever - News and Price Data Correlation

This module handles evidence retrieval specialized for market move explanation
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
import hashlib
import json

logger = logging.getLogger(__name__)

class MarketMoveRetriever:
    """Retrieves and correlates evidence for market move explanation"""
    
    def __init__(self, vector_store, db_manager):
        self.vector_store = vector_store
        self.db_manager = db_manager
        
        # Move-specific configuration
        self.relevance_threshold = 0.6
        self.max_news_items = 20
        self.max_sentiment_items = 50
        self.correlation_window_minutes = 120
        
    async def retrieve_move_evidence(self, 
                                   ticker: str, 
                                   timestamp: datetime, 
                                   move_magnitude: float) -> Dict[str, Any]:
        """
        Retrieve comprehensive evidence for a market move
        """
        try:
            # Determine search windows
            search_window = self._calculate_search_windows(timestamp, move_magnitude)
            
            # Gather evidence in parallel
            import asyncio
            
            tasks = [
                self.get_price_volume_data(ticker, search_window['start'], search_window['end']),
                self.get_news_around_move(ticker, timestamp, search_window),
                self.get_sentiment_shifts(ticker, search_window['start'], search_window['end']),
                self.analyze_cross_asset_moves(timestamp, ticker)
            ]
            
            price_data, news_data, sentiment_data, cross_asset_data = await asyncio.gather(*tasks)
            
            return {
                'price_data': price_data,
                'news_data': news_data,
                'sentiment_data': sentiment_data,
                'cross_asset_data': cross_asset_data,
                'search_window': search_window,
                'retrieval_timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error retrieving move evidence for {ticker}: {str(e)}")
            return {}
    
    async def get_price_volume_data(self, 
                                  ticker: str, 
                                  start_time: datetime, 
                                  end_time: datetime) -> List[Dict]:
        """
        Get granular price and volume data for the move period
        """
        try:
            query = """
            SELECT 
                timestamp,
                open_price as open,
                high_price as high,
                low_price as low,
                close_price as close,
                volume,
                adjusted_close
            FROM alpha_market_data 
            WHERE ticker = $1 
              AND timestamp BETWEEN $2 AND $3
            ORDER BY timestamp ASC
            """
            
            async with self.db_manager.get_async_connection() as conn:
                results = await conn.fetch(query, ticker, start_time, end_time)
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error fetching price data for {ticker}: {str(e)}")
            return []
    
    async def get_news_around_move(self, 
                                 ticker: str, 
                                 timestamp: datetime, 
                                 search_window: Dict[str, datetime]) -> List[Dict]:
        """
        Get news articles around the move timestamp with relevance scoring
        """
        try:
            # First get from vector store
            vector_news = await self._get_vector_news(ticker, timestamp, search_window)
            
            # Then get from database
            db_news = await self._get_database_news(ticker, search_window)
            
            # Combine and deduplicate
            all_news = self._combine_news_sources(vector_news, db_news)
            
            # Score for timing relevance
            scored_news = self._score_news_timing_relevance(all_news, timestamp)
            
            # Return top news items
            return sorted(scored_news, key=lambda x: x['relevance_score'], reverse=True)[:self.max_news_items]
            
        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {str(e)}")
            return []
    
    async def get_sentiment_shifts(self, 
                                 ticker: str, 
                                 before_time: datetime, 
                                 after_time: datetime) -> List[Dict]:
        """
        Analyze sentiment shifts before and after the move
        """
        try:
            query = """
            SELECT 
                ni.title,
                ni.published_at as timestamp,
                ni.overall_sentiment_score as sentiment_score,
                ni.overall_sentiment_label as sentiment_label,
                ni.ticker_sentiment_score,
                ni.relevance_score,
                ni.source_name as source
            FROM alpha_news_intelligence ni
            WHERE ni.ticker = $1 
              AND ni.published_at BETWEEN $2 AND $3
            ORDER BY ni.published_at DESC
            LIMIT $4
            """
            
            async with self.db_manager.get_async_connection() as conn:
                results = await conn.fetch(query, ticker, before_time, after_time, self.max_sentiment_items)
            
            sentiment_data = [dict(row) for row in results]
            
            # Calculate sentiment shift
            before_cutoff = before_time + (after_time - before_time) / 2
            
            before_sentiment = [
                s for s in sentiment_data 
                if s['timestamp'] < before_cutoff
            ]
            after_sentiment = [
                s for s in sentiment_data 
                if s['timestamp'] >= before_cutoff
            ]
            
            # Add shift analysis
            for item in sentiment_data:
                item['sentiment_period'] = 'before' if item['timestamp'] < before_cutoff else 'after'
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error fetching sentiment data for {ticker}: {str(e)}")
            return []
    
    async def analyze_cross_asset_moves(self, timestamp: datetime, primary_ticker: str) -> Dict[str, Any]:
        """
        Analyze correlated moves in other assets around the same time
        """
        try:
            # Get related assets (sector, market indices)
            related_tickers = await self._get_related_assets(primary_ticker)
            
            # Check for moves in related assets
            window_start = timestamp - timedelta(minutes=30)
            window_end = timestamp + timedelta(minutes=30)
            
            correlated_moves = []
            
            for ticker in related_tickers:
                move_data = await self._check_asset_move(ticker, window_start, window_end)
                if move_data and abs(move_data.get('magnitude', 0)) > 1.0:  # >1% move
                    correlated_moves.append(move_data)
            
            return {
                'correlated_moves': correlated_moves,
                'correlation_strength': len(correlated_moves) / len(related_tickers) if related_tickers else 0,
                'market_wide_event': len(correlated_moves) >= 3
            }
            
        except Exception as e:
            logger.error(f"Error analyzing cross-asset moves: {str(e)}")
            return {'correlated_moves': [], 'correlation_strength': 0}
    
    async def correlate_news_timing(self, news_items: List[Dict], move_timestamp: datetime) -> List[Dict]:
        """
        Calculate precise timing correlation between news and price moves
        """
        correlations = []
        
        for news in news_items:
            news_time = news.get('timestamp')
            if not news_time:
                continue
            
            time_diff_seconds = abs((move_timestamp - news_time).total_seconds())
            time_diff_minutes = time_diff_seconds / 60
            
            # Calculate timing correlation score
            correlation_score = self._calculate_timing_correlation(time_diff_minutes)
            
            correlations.append({
                **news,
                'timing_correlation': correlation_score,
                'time_diff_minutes': time_diff_minutes,
                'timing_quality': self._classify_timing_quality(time_diff_minutes)
            })
        
        return sorted(correlations, key=lambda x: x['timing_correlation'], reverse=True)
    
    def _calculate_search_windows(self, timestamp: datetime, move_magnitude: float) -> Dict[str, datetime]:
        """Calculate appropriate search windows based on move characteristics"""
        
        # Larger moves may have longer lead times
        magnitude = abs(move_magnitude)
        
        if magnitude > 10:  # Major move (>10%)
            pre_hours = 6
            post_hours = 2
        elif magnitude > 5:  # Significant move (5-10%)
            pre_hours = 4
            post_hours = 1
        elif magnitude > 2:  # Notable move (2-5%)
            pre_hours = 2
            post_hours = 0.5
        else:  # Small move (<2%)
            pre_hours = 1
            post_hours = 0.25
        
        return {
            'start': timestamp - timedelta(hours=pre_hours),
            'end': timestamp + timedelta(hours=post_hours)
        }
    
    async def _get_vector_news(self, ticker: str, timestamp: datetime, search_window: Dict) -> List[Dict]:
        """Get news from vector database"""
        try:
            # Build search query
            search_query = f"{ticker} news market move price {timestamp.strftime('%Y-%m-%d')}"
            
            # Define filters
            filter_conditions = {
                "ticker": ticker,
                "risk_type": {"$in": ["news", "sentiment", "fundamental"]},
                "timestamp": {
                    "$gte": search_window['start'].isoformat(),
                    "$lte": search_window['end'].isoformat()
                }
            }
            
            # Query vector store
            if hasattr(self.vector_store, 'collection') and self.vector_store.collection:
                results = self.vector_store.collection.query(
                    query_texts=[search_query],
                    where=filter_conditions,
                    n_results=self.max_news_items
                )
                
                # Format results
                vector_news = []
                if results and 'documents' in results:
                    for i, doc in enumerate(results['documents'][0]):
                        metadata = results['metadatas'][0][i] if 'metadatas' in results else {}
                        vector_news.append({
                            'headline': metadata.get('title', doc[:100]),
                            'content': doc,
                            'source': 'vector_db',
                            'timestamp': datetime.fromisoformat(metadata.get('timestamp', timestamp.isoformat())),
                            'relevance_score': 1 - (results['distances'][0][i] if 'distances' in results else 0.5),
                            'sentiment_score': metadata.get('sentiment_score', 0)
                        })
                
                return vector_news
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting vector news: {str(e)}")
            return []
    
    async def _get_database_news(self, ticker: str, search_window: Dict) -> List[Dict]:
        """Get news from database"""
        try:
            query = """
            SELECT 
                title as headline,
                summary as content,
                source_name as source,
                published_at as timestamp,
                overall_sentiment_score as sentiment_score,
                relevance_score
            FROM alpha_news_intelligence 
            WHERE ticker = $1 
              AND published_at BETWEEN $2 AND $3
            ORDER BY published_at DESC
            """
            
            async with self.db_manager.get_async_connection() as conn:
                results = await conn.fetch(query, ticker, search_window['start'], search_window['end'])
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting database news: {str(e)}")
            return []
    
    def _combine_news_sources(self, vector_news: List[Dict], db_news: List[Dict]) -> List[Dict]:
        """Combine and deduplicate news from different sources"""
        all_news = vector_news.copy()
        
        # Add database news, avoiding duplicates
        for db_item in db_news:
            is_duplicate = False
            db_headline = db_item.get('headline', '').lower()
            
            for existing in all_news:
                existing_headline = existing.get('headline', '').lower()
                if self._are_headlines_similar(db_headline, existing_headline):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                all_news.append(db_item)
        
        return all_news
    
    def _are_headlines_similar(self, headline1: str, headline2: str) -> bool:
        """Check if two headlines are similar enough to be duplicates"""
        if not headline1 or not headline2:
            return False
        
        # Simple similarity check
        words1 = set(headline1.lower().split())
        words2 = set(headline2.lower().split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union) if union else 0
        return similarity > 0.7
    
    def _score_news_timing_relevance(self, news_items: List[Dict], move_timestamp: datetime) -> List[Dict]:
        """Score news items based on timing relevance to the move"""
        scored_news = []
        
        for item in news_items:
            item_time = item.get('timestamp')
            if not item_time:
                continue
            
            # Calculate timing score
            time_diff_minutes = abs((move_timestamp - item_time).total_seconds() / 60)
            timing_score = self._calculate_timing_correlation(time_diff_minutes)
            
            # Combine with existing relevance
            existing_relevance = item.get('relevance_score', 0.5)
            combined_relevance = (timing_score * 0.7) + (existing_relevance * 0.3)
            
            item['relevance_score'] = combined_relevance
            item['timing_score'] = timing_score
            
            scored_news.append(item)
        
        return scored_news
    
    def _calculate_timing_correlation(self, time_diff_minutes: float) -> float:
        """Calculate timing correlation based on time difference"""
        if time_diff_minutes <= 5:
            return 1.0
        elif time_diff_minutes <= 15:
            return 0.9
        elif time_diff_minutes <= 30:
            return 0.7
        elif time_diff_minutes <= 60:
            return 0.5
        elif time_diff_minutes <= 120:
            return 0.3
        else:
            return 0.1
    
    def _classify_timing_quality(self, time_diff_minutes: float) -> str:
        """Classify timing quality"""
        if time_diff_minutes <= 5:
            return 'immediate'
        elif time_diff_minutes <= 30:
            return 'very_close'
        elif time_diff_minutes <= 60:
            return 'close'
        elif time_diff_minutes <= 120:
            return 'related'
        else:
            return 'distant'
    
    async def _get_related_assets(self, primary_ticker: str) -> List[str]:
        """Get related assets for cross-correlation analysis"""
        # Simple mapping for demonstration
        sector_mapping = {
            'AAPL': ['MSFT', 'GOOGL', 'AMZN', 'NVDA'],
            'MSFT': ['AAPL', 'GOOGL', 'AMZN', 'NVDA'],
            'NVDA': ['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
            'TSLA': ['AAPL', 'MSFT', 'NVDA'],
            'GOOGL': ['AAPL', 'MSFT', 'AMZN', 'NVDA']
        }
        
        # Always include major indices
        related = ['SPY', 'QQQ', 'NASDAQ']
        
        # Add sector-specific assets
        if primary_ticker in sector_mapping:
            related.extend(sector_mapping[primary_ticker])
        
        return list(set(related))  # Remove duplicates
    
    async def _check_asset_move(self, ticker: str, start_time: datetime, end_time: datetime) -> Optional[Dict]:
        """Check if an asset had a significant move in the time window"""
        try:
            query = """
            SELECT 
                timestamp,
                close_price,
                volume
            FROM alpha_market_data 
            WHERE ticker = $1 
              AND timestamp BETWEEN $2 AND $3
            ORDER BY timestamp ASC
            """
            
            async with self.db_manager.get_async_connection() as conn:
                results = await conn.fetch(query, ticker, start_time, end_time)
            
            if len(results) < 2:
                return None
            
            # Calculate move
            start_price = results[0]['close_price']
            end_price = results[-1]['close_price']
            magnitude = ((end_price - start_price) / start_price) * 100
            
            return {
                'ticker': ticker,
                'magnitude': magnitude,
                'direction': 'up' if magnitude > 0 else 'down',
                'start_price': start_price,
                'end_price': end_price
            }
            
        except Exception as e:
            logger.error(f"Error checking move for {ticker}: {str(e)}")
            return None
