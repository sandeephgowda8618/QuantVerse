"""
Market Move Pipeline - Main Orchestrator for Move Explanation

This pipeline orchestrates the SUDDEN MARKET MOVE explanation RAG process:
Query → Move Detection → News Correlation → Sentiment Analysis → Explanation Response
"""

import asyncio
import json
import hashlib
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
import logging

from ..vector_store import ChromaVectorStore
from ...db.postgres_handler import PostgresHandler
from ..llm_manager import LLMManager
from .market_move_llm import MarketMoveLLM
from .market_move_retriever import MarketMoveRetriever
from .market_move_cache import MarketMoveCacheManager

logger = logging.getLogger(__name__)

class MarketMovePipeline:
    """Main orchestrator for SUDDEN MARKET MOVE explanation RAG pipeline"""
    
    def __init__(self, 
                 vector_store: ChromaVectorStore,
                 db_manager: PostgresHandler,
                 llm_manager: LLMManager,
                 cache_manager: Optional[MarketMoveCacheManager] = None):
        """Initialize the market move explanation pipeline"""
        self.vector_store = vector_store
        self.db_manager = db_manager
        self.llm_manager = llm_manager
        self.cache_manager = cache_manager or MarketMoveCacheManager()
        
        # Initialize specialized components
        self.move_llm = MarketMoveLLM(llm_manager)
        self.move_retriever = MarketMoveRetriever(vector_store, db_manager)
        
        # Configuration
        self.min_move_threshold = 0.02  # 2% minimum move to analyze
        self.max_analysis_age_hours = 24  # Don't analyze moves older than 24h
        self.confidence_threshold = 0.3  # Minimum confidence to return result
        
        logger.info("MarketMovePipeline initialized")
    
    async def process_move_query(self, 
                               query: str, 
                               ticker: str, 
                               timestamp: Optional[datetime] = None,
                               move_magnitude: Optional[float] = None) -> Dict[str, Any]:
        """
        Main entry point for processing market move explanation queries
        """
        start_time = time.time()
        
        try:
            # Validate the query
            self._validate_move_query(query, timestamp)
            
            # Auto-detect move if timestamp not provided
            if timestamp is None:
                timestamp = await self._detect_recent_move(ticker, query)
            
            # Detect move parameters
            move_data = await self.detect_move_parameters(ticker, timestamp)
            
            if not move_data or abs(move_data.get('magnitude', 0)) < self.min_move_threshold:
                return self._format_no_significant_move_response(ticker, timestamp)
            
            # Check cache first
            cache_key = self._generate_cache_key(ticker, timestamp, move_data)
            cached_result = self.cache_manager.get_cached_move_explanation(cache_key)
            if cached_result:
                logger.info(f"Returning cached move explanation for {ticker}")
                return cached_result
            
            # Determine news search window based on move characteristics
            news_window = self._determine_news_search_window(timestamp, move_data.get('duration_minutes', 60))
            
            # Gather evidence in parallel
            evidence_tasks = [
                self.move_retriever.get_price_volume_data(ticker, news_window['start'], news_window['end']),
                self.move_retriever.get_news_around_move(ticker, timestamp, news_window),
                self.move_retriever.get_sentiment_shifts(ticker, news_window['start'], timestamp),
                self.move_retriever.analyze_cross_asset_moves(timestamp, ticker)
            ]
            
            price_data, news_data, sentiment_data, cross_asset_data = await asyncio.gather(*evidence_tasks)
            
            # Correlate news timing with price moves
            correlation_analysis = await self.correlate_news_to_move(move_data, news_data)
            
            # Analyze move causation using LLM
            causation_analysis = await self.analyze_move_causation(
                move_data, price_data, news_data, sentiment_data, cross_asset_data
            )
            
            # Format the final response
            explanation = await self.format_move_explanation(
                causation_analysis, move_data, correlation_analysis, 
                news_data, sentiment_data, cross_asset_data
            )
            
            # Cache the result
            self.cache_manager.cache_move_explanation(cache_key, explanation)
            
            logger.info(f"Move explanation completed for {ticker} in {time.time() - start_time:.2f}s")
            return explanation
            
        except Exception as e:
            logger.error(f"Error processing move query for {ticker}: {str(e)}")
            return self._format_error_response(str(e), ticker, timestamp)
    
    async def detect_move_parameters(self, ticker: str, timestamp: datetime) -> Dict[str, Any]:
        """
        Detect and analyze move characteristics around the given timestamp
        """
        try:
            # Get price data around the move
            start_time = timestamp - timedelta(hours=2)
            end_time = timestamp + timedelta(hours=1)
            
            price_data = await self.move_retriever.get_price_volume_data(ticker, start_time, end_time)
            
            if not price_data or len(price_data) < 2:
                return {}
            
            # Find the actual move period
            move_analysis = self._analyze_price_movement(price_data, timestamp)
            
            return {
                'timestamp': timestamp,
                'magnitude': move_analysis['magnitude'],
                'direction': move_analysis['direction'],
                'duration_minutes': move_analysis['duration_minutes'],
                'volume_spike': move_analysis['volume_spike'],
                'pre_move_price': move_analysis['pre_move_price'],
                'post_move_price': move_analysis['post_move_price'],
                'volume_ratio': move_analysis['volume_ratio'],
                'price_pattern': move_analysis['price_pattern']
            }
            
        except Exception as e:
            logger.error(f"Error detecting move parameters for {ticker}: {str(e)}")
            return {}
    
    async def correlate_news_to_move(self, move_data: Dict, news_data: List[Dict]) -> Dict[str, Any]:
        """
        Correlate news timing with price move timing
        """
        if not news_data or not move_data:
            return {'correlation_strength': 0.0, 'best_match': None}
        
        move_timestamp = move_data['timestamp']
        correlations = []
        
        for news_item in news_data:
            news_timestamp = news_item.get('timestamp')
            if not news_timestamp:
                continue
                
            # Calculate timing correlation
            time_diff_minutes = abs((move_timestamp - news_timestamp).total_seconds() / 60)
            
            # Scoring: closer timing = higher correlation
            if time_diff_minutes <= 5:
                timing_score = 1.0
            elif time_diff_minutes <= 15:
                timing_score = 0.8
            elif time_diff_minutes <= 60:
                timing_score = 0.5
            elif time_diff_minutes <= 120:
                timing_score = 0.2
            else:
                timing_score = 0.1
            
            # Factor in news relevance and sentiment magnitude
            relevance_score = news_item.get('relevance_score', 0.5)
            sentiment_magnitude = abs(news_item.get('sentiment_score', 0))
            
            correlation_score = timing_score * 0.6 + relevance_score * 0.3 + sentiment_magnitude * 0.1
            
            correlations.append({
                'news_item': news_item,
                'correlation_score': correlation_score,
                'time_diff_minutes': time_diff_minutes
            })
        
        # Sort by correlation strength
        correlations.sort(key=lambda x: x['correlation_score'], reverse=True)
        
        best_correlation = correlations[0] if correlations else None
        avg_correlation = sum(c['correlation_score'] for c in correlations) / len(correlations) if correlations else 0
        
        return {
            'correlation_strength': avg_correlation,
            'best_match': best_correlation,
            'all_correlations': correlations[:5],  # Top 5
            'news_count': len(news_data)
        }
    
    async def analyze_move_causation(self, 
                                   move_data: Dict, 
                                   price_data: List[Dict],
                                   news_data: List[Dict], 
                                   sentiment_data: List[Dict],
                                   cross_asset_data: Dict) -> Dict[str, Any]:
        """
        Use LLM to analyze the likely causation of the market move
        """
        try:
            context = {
                'move_data': move_data,
                'price_data': price_data,
                'news_data': news_data,
                'sentiment_data': sentiment_data,
                'cross_asset_data': cross_asset_data,
                'analysis_timestamp': datetime.utcnow()
            }
            
            # Let the LLM analyze causation
            causation_result = await self.move_llm.explain_market_move(context)
            
            return causation_result
            
        except Exception as e:
            logger.error(f"Error analyzing move causation: {str(e)}")
            return {
                'move_explanation': 'Unable to determine primary cause',
                'confidence': 0.1,
                'error': str(e)
            }
    
    async def format_move_explanation(self, 
                                    causation_analysis: Dict,
                                    move_data: Dict,
                                    correlation_analysis: Dict,
                                    news_data: List[Dict],
                                    sentiment_data: List[Dict],
                                    cross_asset_data: Dict) -> Dict[str, Any]:
        """
        Format the final move explanation response
        """
        explanation_confidence = self._calculate_explanation_confidence(
            correlation_analysis.get('correlation_strength', 0),
            len(news_data),
            causation_analysis.get('confidence', 0)
        )
        
        # Build evidence list
        evidence = []
        
        # Add news evidence
        for news_item in (news_data[:3] if news_data else []):
            evidence.append({
                'type': 'news',
                'headline': news_item.get('headline', ''),
                'source': news_item.get('source', ''),
                'timestamp': news_item.get('timestamp'),
                'sentiment': news_item.get('sentiment_score'),
                'relevance': news_item.get('relevance_score')
            })
        
        # Add sentiment evidence
        if sentiment_data:
            avg_sentiment = sum(s.get('sentiment_score', 0) for s in sentiment_data) / len(sentiment_data)
            evidence.append({
                'type': 'sentiment',
                'description': f'Average sentiment shift: {avg_sentiment:.2f}',
                'sample_size': len(sentiment_data)
            })
        
        # Add cross-asset evidence
        if cross_asset_data.get('correlated_moves'):
            evidence.append({
                'type': 'cross_asset',
                'description': 'Correlated moves in related assets',
                'details': cross_asset_data.get('correlated_moves', [])[:3]
            })
        
        return {
            'move_explanation': causation_analysis.get('move_explanation', 'Price movement detected'),
            'move_type': causation_analysis.get('move_type', 'unknown'),
            'contributing_factors': causation_analysis.get('contributing_factors', []),
            'move_characteristics': {
                'magnitude': f"{move_data.get('magnitude', 0):+.1f}%",
                'direction': move_data.get('direction', 'unknown'),
                'duration': f"{move_data.get('duration_minutes', 0):.0f} minutes",
                'volume_spike': f"{move_data.get('volume_ratio', 1):.1f}x average" if move_data.get('volume_ratio', 1) > 1.2 else "normal",
                'price_pattern': move_data.get('price_pattern', 'gradual')
            },
            'news_correlation': {
                'primary_news': correlation_analysis.get('best_match', {}).get('news_item'),
                'timing_correlation': correlation_analysis.get('correlation_strength', 0),
                'news_count': correlation_analysis.get('news_count', 0)
            },
            'confidence': explanation_confidence,
            'evidence': evidence,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'ticker': move_data.get('ticker', 'Unknown')
        }
    
    def _validate_move_query(self, query: str, timestamp: Optional[datetime] = None) -> None:
        """Validate the move query parameters"""
        if not query or len(query.strip()) < 5:
            raise ValueError("Query must be at least 5 characters long")
        
        if timestamp and timestamp > datetime.utcnow():
            raise ValueError("Cannot analyze future moves")
        
        if timestamp and (datetime.utcnow() - timestamp).total_seconds() > self.max_analysis_age_hours * 3600:
            raise ValueError(f"Move is too old (max {self.max_analysis_age_hours} hours)")
    
    def _determine_news_search_window(self, move_timestamp: datetime, move_duration_minutes: int) -> Dict[str, datetime]:
        """Determine the time window for searching relevant news"""
        
        # Extend search window based on move duration
        if move_duration_minutes <= 5:  # Very fast move
            pre_window_hours = 2
            post_window_hours = 0.5
        elif move_duration_minutes <= 30:  # Fast move
            pre_window_hours = 4
            post_window_hours = 1
        else:  # Gradual move
            pre_window_hours = 6
            post_window_hours = 2
        
        return {
            'start': move_timestamp - timedelta(hours=pre_window_hours),
            'end': move_timestamp + timedelta(hours=post_window_hours)
        }
    
    def _calculate_explanation_confidence(self, 
                                        correlation_strength: float,
                                        news_count: int,
                                        llm_confidence: float) -> float:
        """Calculate overall confidence in the move explanation"""
        
        # Base confidence from LLM analysis
        base_confidence = llm_confidence
        
        # Boost from news correlation
        correlation_boost = min(correlation_strength * 0.3, 0.3)
        
        # Boost from having multiple news sources
        news_boost = min(news_count * 0.05, 0.2)
        
        # Combined confidence
        total_confidence = min(base_confidence + correlation_boost + news_boost, 1.0)
        
        return round(total_confidence, 2)
    
    def _analyze_price_movement(self, price_data: List[Dict], target_timestamp: datetime) -> Dict[str, Any]:
        """Analyze price movement characteristics around target timestamp"""
        
        if len(price_data) < 2:
            return {'magnitude': 0, 'direction': 'unknown', 'duration_minutes': 0}
        
        # Sort by timestamp
        sorted_data = sorted(price_data, key=lambda x: x['timestamp'])
        
        # Find closest price point to target timestamp
        target_idx = 0
        min_diff = float('inf')
        
        for i, point in enumerate(sorted_data):
            diff = abs((point['timestamp'] - target_timestamp).total_seconds())
            if diff < min_diff:
                min_diff = diff
                target_idx = i
        
        # Analyze movement around target point
        start_idx = max(0, target_idx - 10)
        end_idx = min(len(sorted_data), target_idx + 10)
        
        pre_move_price = sorted_data[start_idx]['close']
        post_move_price = sorted_data[end_idx - 1]['close']
        
        magnitude = ((post_move_price - pre_move_price) / pre_move_price) * 100
        direction = 'up' if magnitude > 0 else 'down' if magnitude < 0 else 'flat'
        
        # Calculate duration
        duration_seconds = (sorted_data[end_idx - 1]['timestamp'] - sorted_data[start_idx]['timestamp']).total_seconds()
        duration_minutes = duration_seconds / 60
        
        # Calculate volume characteristics
        volumes = [point.get('volume', 0) for point in sorted_data[start_idx:end_idx]]
        avg_volume = sum(volumes) / len(volumes) if volumes else 1
        max_volume = max(volumes) if volumes else 0
        volume_ratio = max_volume / avg_volume if avg_volume > 0 else 1
        
        # Determine price pattern
        if duration_minutes <= 5:
            pattern = 'spike'
        elif duration_minutes <= 15:
            pattern = 'sharp'
        elif duration_minutes <= 60:
            pattern = 'gradual'
        else:
            pattern = 'trend'
        
        return {
            'magnitude': magnitude,
            'direction': direction,
            'duration_minutes': duration_minutes,
            'pre_move_price': pre_move_price,
            'post_move_price': post_move_price,
            'volume_ratio': volume_ratio,
            'volume_spike': volume_ratio > 1.5,
            'price_pattern': pattern
        }
    
    async def _detect_recent_move(self, ticker: str, query: str) -> datetime:
        """Auto-detect recent significant moves for the ticker"""
        
        # Look back 24 hours for recent moves
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        try:
            price_data = await self.move_retriever.get_price_volume_data(ticker, start_time, end_time)
            
            if not price_data or len(price_data) < 10:
                return end_time  # Default to current time
            
            # Find largest price movement in recent data
            max_move = 0
            move_timestamp = end_time
            
            for i in range(1, len(price_data)):
                prev_price = price_data[i-1]['close']
                curr_price = price_data[i]['close']
                move = abs(curr_price - prev_price) / prev_price
                
                if move > max_move:
                    max_move = move
                    move_timestamp = price_data[i]['timestamp']
            
            return move_timestamp
            
        except Exception as e:
            logger.error(f"Error detecting recent move for {ticker}: {str(e)}")
            return end_time
    
    def _generate_cache_key(self, ticker: str, timestamp: datetime, move_data: Dict) -> str:
        """Generate cache key for move explanation"""
        key_components = [
            ticker,
            timestamp.strftime('%Y%m%d_%H%M'),
            str(round(move_data.get('magnitude', 0), 1)),
            str(move_data.get('duration_minutes', 0))
        ]
        key_string = ':'.join(key_components)
        return f"move_explain:{hashlib.md5(key_string.encode()).hexdigest()[:12]}"
    
    def _format_no_significant_move_response(self, ticker: str, timestamp: datetime) -> Dict[str, Any]:
        """Format response when no significant move is detected"""
        return {
            'move_explanation': 'No significant price movement detected',
            'move_type': 'normal_trading',
            'contributing_factors': ['Normal market trading activity'],
            'move_characteristics': {
                'magnitude': '<2%',
                'duration': 'N/A',
                'volume_spike': 'normal',
                'price_pattern': 'normal'
            },
            'news_correlation': {
                'primary_news': None,
                'timing_correlation': 0.0,
                'news_count': 0
            },
            'confidence': 0.9,
            'evidence': [],
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'ticker': ticker
        }
    
    def _format_error_response(self, error: str, ticker: str, timestamp: Optional[datetime]) -> Dict[str, Any]:
        """Format error response"""
        return {
            'move_explanation': 'Analysis failed',
            'move_type': 'error',
            'contributing_factors': [f'Error: {error}'],
            'move_characteristics': {},
            'news_correlation': {},
            'confidence': 0.0,
            'evidence': [],
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'ticker': ticker,
            'error': error
        }
