"""
Member 2: Sudden Market Move Explainer Service
Core business logic for explaining sudden price movements with timestamp analysis.

IMPLEMENTATION STATUS: TEMPLATE READY  
TODO: Follow the implementation guide in docs/MEMBER2_EXPLAIN_MOVE_IMPLEMENTATION.md
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# TODO: Uncomment these when implementing
# from ...db.queries.move_queries import MoveQueries
# from ...rag_engine.vector_store import ChromaVectorStore
# from ...rag_engine.llm_manager import LLMManager
# from ...utils.time_utils import TimeUtils
# from .explain_move_prompt import ExplainMovePrompt

from ...db.postgres_handler import PostgresHandler
from .explain_move_prompt import ExplainMovePrompt

logger = logging.getLogger(__name__)

class ExplainMoveService:
    """
    Service for explaining sudden market movements.
    
    This service orchestrates:
    1. Movement detection around target timestamp
    2. Evidence gathering (anomalies, sentiment, incidents, news)
    3. LLM-powered explanation generation
    """
    
    def __init__(self):
        self.db = PostgresHandler()
        self.prompt_builder = ExplainMovePrompt()
        
        # Configuration
        self.SIGNIFICANT_MOVE_THRESHOLD = 2.0  # 2% price change
        self.ANALYSIS_WINDOW_MINUTES = 30      # ±30 minutes around timestamp
        
        logger.info("ExplainMoveService initialized")
    
    async def validate_ticker(self, ticker: str) -> bool:
        """
        Check if ticker exists in assets table
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            bool: True if ticker exists, False otherwise
        """
        try:
            query = "SELECT COUNT(*) as count FROM assets WHERE ticker = $1"
            result = await self.db.async_execute_query(query, (ticker,))
            return result[0]['count'] > 0
        except Exception as e:
            logger.error(f"Error validating ticker {ticker}: {str(e)}")
            return False
    
    async def detect_movement(self, ticker: str, timestamp: datetime) -> Dict:
        """
        Detect if significant price movement occurred around timestamp
        
        Args:
            ticker: Stock ticker symbol
            timestamp: Target timestamp to analyze
            
        Returns:
            Dict: Movement detection result with significance flag and data
        """
        try:
            # Define time window for movement detection  
            start_time = timestamp - timedelta(minutes=self.ANALYSIS_WINDOW_MINUTES)
            end_time = timestamp + timedelta(minutes=self.ANALYSIS_WINDOW_MINUTES)
            
            # Get price data around the timestamp
            price_query = """
            SELECT price, timestamp, volume
            FROM market_prices 
            WHERE ticker = $1 
            AND timestamp BETWEEN $2 AND $3
            ORDER BY timestamp ASC
            """
            
            price_data = await self.db.async_execute_query(
                price_query, (ticker, start_time, end_time)
            )
            
            if not price_data or len(price_data) < 2:
                return {
                    "significant_move": False,
                    "reason": "Insufficient price data",
                    "price_change": {
                        "start_price": 0.0,
                        "end_price": 0.0,
                        "percent_change": 0.0,
                        "direction": "unknown"
                    },
                    "threshold_used": self.SIGNIFICANT_MOVE_THRESHOLD,
                    "window_minutes": self.ANALYSIS_WINDOW_MINUTES
                }
            
            # Calculate price change
            start_price = float(price_data[0]['price'])
            end_price = float(price_data[-1]['price'])
            percent_change = ((end_price - start_price) / start_price) * 100
            
            # Check if movement is significant
            is_significant = abs(percent_change) >= self.SIGNIFICANT_MOVE_THRESHOLD
            
            direction = "up" if percent_change > 0 else "down" if percent_change < 0 else "sideways"
            
            return {
                "significant_move": is_significant,
                "reason": f"Price moved {percent_change:.2f}%" if is_significant else "Movement below threshold",
                "price_change": {
                    "start_price": start_price,
                    "end_price": end_price,
                    "percent_change": percent_change,
                    "direction": direction
                },
                "threshold_used": self.SIGNIFICANT_MOVE_THRESHOLD,
                "window_minutes": self.ANALYSIS_WINDOW_MINUTES,
                "data_points": len(price_data)
            }
            
        except Exception as e:
            logger.error(f"Movement detection error: {str(e)}")
            return {
                "significant_move": False,
                "reason": f"Detection error: {str(e)}",
                "price_change": {
                    "start_price": 0.0,
                    "end_price": 0.0,
                    "percent_change": 0.0,
                    "direction": "unknown"
                },
                "threshold_used": self.SIGNIFICANT_MOVE_THRESHOLD,
                "window_minutes": self.ANALYSIS_WINDOW_MINUTES
            }
    
    async def analyze_movement(self, ticker: str, timestamp: datetime) -> Dict:
        """
        Main analysis function - gathers all evidence and generates explanation
        
        Args:
            ticker: Stock ticker symbol
            timestamp: Target timestamp when movement occurred
            
        Returns:
            Dict: Complete movement explanation with evidence
        """
        try:
            # Step 1: Detect the movement
            movement_data = await self.detect_movement(ticker, timestamp)
            
            if not movement_data['significant_move']:
                return {
                    "ticker": ticker,
                    "summary": f"No significant movement detected for {ticker} around {timestamp.strftime('%Y-%m-%d %H:%M')}",
                    "primary_causes": ["Movement below threshold"],
                    "confidence": 0.8,
                    "evidence_used": [],
                    "movement_data": movement_data,
                    "timestamp": timestamp.isoformat()
                }
            
            # Step 2: Gather supporting evidence
            events = await self._get_related_events(ticker, timestamp)
            sentiment_data = await self._get_sentiment_data(ticker, timestamp)
            anomalies = await self._get_anomalies_around_time(ticker, timestamp)
            
            # Step 3: Generate analysis using available data
            analysis = await self._generate_movement_analysis(
                ticker, timestamp, movement_data, events, sentiment_data, anomalies
            )
            
            return {
                "ticker": ticker,
                "summary": analysis.get('explanation', 'Movement analysis completed'),
                "primary_causes": analysis.get('supporting_factors', []),
                "confidence": analysis.get('confidence', 0.6),
                "evidence_used": events + anomalies,
                "movement_data": movement_data,
                "market_implications": analysis.get('market_implications', ''),
                "timestamp": timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Movement analysis error for {ticker}: {str(e)}")
            return {
                "ticker": ticker,
                "summary": f"Analysis error occurred: {str(e)}",
                "primary_causes": ["Analysis error"],
                "confidence": 0.1,
                "evidence_used": [],
                "movement_data": {},
                "timestamp": timestamp.isoformat()
            }
    
    async def _get_related_events(self, ticker: str, timestamp: datetime) -> List[Dict]:
        """Get events that occurred around the timestamp"""
        try:
            start_time = timestamp - timedelta(hours=2)
            end_time = timestamp + timedelta(hours=1)
            
            # Check for earnings announcements
            earnings_query = """
            SELECT 'earnings' as type, fiscal_date_ending, reported_eps, estimated_eps, surprise_pct
            FROM earnings_data 
            WHERE ticker = $1 
            AND fiscal_date_ending BETWEEN $2 AND $3
            ORDER BY fiscal_date_ending DESC
            LIMIT 3
            """
            
            earnings = await self.db.async_execute_query(earnings_query, (ticker, start_time, end_time))
            
            events = []
            for earning in earnings or []:
                events.append({
                    'source': 'earnings',
                    'type': 'earnings',
                    'description': f"Earnings: {earning['reported_eps']} vs {earning['estimated_eps']} est",
                    'impact_score': abs(float(earning.get('surprise_pct', 0))),
                    'timestamp': earning['fiscal_date_ending']
                })
            
            # Check for news around the time
            news_query = """
            SELECT headline, sentiment, published_at
            FROM news_headlines 
            WHERE ticker = $1 
            AND published_at BETWEEN $2 AND $3
            ORDER BY relevance_score DESC
            LIMIT 5
            """
            
            news = await self.db.async_execute_query(news_query, (ticker, start_time, end_time))
            
            for article in news or []:
                events.append({
                    'source': 'news',
                    'type': 'news',
                    'description': article['headline'],
                    'impact_score': abs(float(article.get('sentiment', 0))),
                    'timestamp': article['published_at']
                })
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting related events: {str(e)}")
            return []
    
    async def _get_sentiment_data(self, ticker: str, timestamp: datetime) -> Dict:
        """Get sentiment data around the timestamp"""
        try:
            start_time = timestamp - timedelta(hours=1)
            end_time = timestamp + timedelta(hours=1)
            
            query = """
            SELECT AVG(sentiment) as avg_sentiment, COUNT(*) as news_count
            FROM news_headlines 
            WHERE ticker = $1 
            AND published_at BETWEEN $2 AND $3
            """
            
            result = await self.db.async_execute_query(query, (ticker, start_time, end_time))
            
            if result and result[0]['avg_sentiment'] is not None:
                return {
                    'overall_sentiment': float(result[0]['avg_sentiment']),
                    'news_count': int(result[0]['news_count']),
                    'sentiment_label': 'positive' if result[0]['avg_sentiment'] > 0.1 else 'negative' if result[0]['avg_sentiment'] < -0.1 else 'neutral'
                }
            
            return {'overall_sentiment': 0, 'news_count': 0, 'sentiment_label': 'neutral'}
            
        except Exception as e:
            logger.error(f"Error getting sentiment data: {str(e)}")
            return {'overall_sentiment': 0, 'news_count': 0, 'sentiment_label': 'neutral'}
    
    async def _get_anomalies_around_time(self, ticker: str, timestamp: datetime) -> List[Dict]:
        """Get anomalies detected around the timestamp"""
        try:
            start_time = timestamp - timedelta(hours=1)
            end_time = timestamp + timedelta(hours=1)
            
            query = """
            SELECT anomaly_type, severity, description, detected_at, confidence_score
            FROM anomalies 
            WHERE ticker = $1 
            AND detected_at BETWEEN $2 AND $3
            ORDER BY confidence_score DESC
            LIMIT 5
            """
            
            anomalies = await self.db.async_execute_query(query, (ticker, start_time, end_time))
            
            result = []
            for anomaly in anomalies or []:
                result.append({
                    'source': 'anomaly_detection',
                    'type': anomaly['anomaly_type'],
                    'description': anomaly['description'],
                    'severity': anomaly['severity'],
                    'confidence': float(anomaly['confidence_score']),
                    'timestamp': anomaly['detected_at']
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting anomalies: {str(e)}")
            return []
    
    async def _generate_movement_analysis(self, ticker: str, timestamp: datetime, 
                                        movement_data: Dict, events: List[Dict], 
                                        sentiment_data: Dict, anomalies: List[Dict]) -> Dict:
        """Generate analysis based on collected evidence"""
        
        # For now, provide rule-based analysis
        # TODO: This is where the RAG engine integration will be added
        
        price_change = movement_data['price_change']['percent_change']
        direction = movement_data['price_change']['direction']
        
        explanation = f"{ticker} moved {direction} by {abs(price_change):.2f}% around {timestamp.strftime('%H:%M on %Y-%m-%d')}"
        
        supporting_factors = []
        confidence = 0.5
        
        # Analyze events
        if events:
            earnings_events = [e for e in events if e['type'] == 'earnings']
            if earnings_events:
                supporting_factors.append(f"Earnings announcement detected with surprise factor")
                confidence += 0.2
            
            news_events = [e for e in events if e['type'] == 'news']
            if news_events:
                supporting_factors.append(f"{len(news_events)} news articles published around the time")
                confidence += 0.1
        
        # Analyze sentiment
        if sentiment_data['news_count'] > 0:
            sentiment_label = sentiment_data['sentiment_label']
            if sentiment_label != 'neutral':
                supporting_factors.append(f"News sentiment was {sentiment_label} around the movement")
                confidence += 0.1
        
        # Analyze anomalies
        if anomalies:
            high_confidence_anomalies = [a for a in anomalies if a.get('confidence', 0) > 0.7]
            if high_confidence_anomalies:
                supporting_factors.append(f"{len(high_confidence_anomalies)} high-confidence anomalies detected")
                confidence += 0.2
        
        if not supporting_factors:
            supporting_factors.append("Movement occurred without clear immediate catalysts")
            
        market_implications = f"Monitor for continued {direction}ward momentum" if abs(price_change) > 3 else "Movement appears contained"
        
        return {
            'explanation': explanation,
            'supporting_factors': supporting_factors,
            'confidence': min(0.95, confidence),
            'market_implications': market_implications
        }
    
    async def find_recent_moves(self, ticker: str, hours_back: int) -> List[Dict]:
        """Find recent significant movements for a ticker"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            # Look for significant price movements in recent history
            query = """
            SELECT timestamp, price, volume
            FROM market_prices 
            WHERE ticker = $1 
            AND timestamp >= $2
            ORDER BY timestamp DESC
            LIMIT 100
            """
            
            price_data = await self.db.async_execute_query(query, (ticker, cutoff_time))
            
            movements = []
            if len(price_data) >= 2:
                for i in range(1, len(price_data)):
                    current_price = float(price_data[i]['price'])
                    prev_price = float(price_data[i-1]['price'])
                    
                    if prev_price > 0:
                        percent_change = ((current_price - prev_price) / prev_price) * 100
                        
                        if abs(percent_change) >= self.SIGNIFICANT_MOVE_THRESHOLD:
                            movements.append({
                                'timestamp': price_data[i]['timestamp'],
                                'price_change': percent_change,
                                'price_before': prev_price,
                                'price_after': current_price,
                                'direction': 'up' if percent_change > 0 else 'down'
                            })
            
            return movements[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Error finding recent moves: {str(e)}")
            return []
    pass

class TimeUtils:
    """
    Time manipulation utilities
    TODO: Implement following the guide
    """
    pass

"""
IMPLEMENTATION CHECKLIST:

□ Create MoveQueries class with SQL queries
□ Create ExplainMovePrompt class with LLM prompt templates
□ Create TimeUtils class for time window calculations
□ Implement detect_movement method with price change detection
□ Implement analyze_movement method with evidence gathering
□ Implement _calculate_price_change helper method  
□ Implement _format_movement_response method
□ Add comprehensive error handling and logging
□ Create unit tests for each component
□ Test with real market data
□ Update route to use this service

Follow the detailed guide in: docs/MEMBER2_EXPLAIN_MOVE_IMPLEMENTATION.md
"""
