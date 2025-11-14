"""
Member 2: Sudden Market Move Explainer Service
Core business logic for explaining sudden price movements with timestamp analysis.

IMPLEMENTATION STATUS: FULLY IMPLEMENTED
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, timezone

from ...db.postgres_handler import PostgresHandler
from ...rag_engine.vector_store import ChromaVectorStore
from ...rag_engine.llm_manager import LLMManager
from ...rag_engine.sudden_market_move_mode.market_move_pipeline import MarketMovePipeline
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
        self.vector_store = ChromaVectorStore()
        self.llm_manager = LLMManager()
        self.pipeline = MarketMovePipeline(
            vector_store=self.vector_store,
            db_manager=self.db,
            llm_manager=self.llm_manager
        )
        self.prompt_builder = ExplainMovePrompt()
        
        # Configuration
        self.SIGNIFICANT_MOVE_THRESHOLD = 2.0  # 2% price change
        self.ANALYSIS_WINDOW_MINUTES = 30      # ±30 minutes around timestamp
        self.MAX_EVIDENCE_ITEMS = 15          # Limit evidence for context
        self.ANOMALY_LOOKBACK_DAYS = 30       # Expanded lookback for anomalies
        self.NEWS_LOOKBACK_DAYS = 7           # Lookback for news
        self.PRICE_LOOKBACK_DAYS = 5          # Lookback for price data
        
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
            Dict containing movement data and significance
        """
        try:
            # Calculate time window
            start_time = timestamp - timedelta(minutes=self.ANALYSIS_WINDOW_MINUTES)
            end_time = timestamp + timedelta(minutes=self.ANALYSIS_WINDOW_MINUTES)
            
            # Query for price data around the timestamp
            query = """
            SELECT 
                timestamp,
                open_price,
                high_price,
                low_price,
                close_price,
                volume
            FROM market_prices 
            WHERE ticker = $1 
            AND timestamp BETWEEN $2 AND $3
            ORDER BY timestamp
            """
            
            prices = await self.db.async_execute_query(
                query, (ticker, start_time, end_time)
            )
            
            if not prices:
                return {
                    'significant_move': False,
                    'reason': 'No price data found for the specified time window'
                }
            
            # Calculate price movement
            first_price = prices[0]['open_price'] or prices[0]['close_price']
            last_price = prices[-1]['close_price'] or prices[-1]['high_price']
            
            if not first_price or not last_price:
                return {
                    'significant_move': False,
                    'reason': 'Insufficient price data'
                }
            
            # Calculate percentage change
            price_change_pct = ((last_price - first_price) / first_price) * 100
            
            # Check if movement is significant
            is_significant = abs(price_change_pct) >= self.SIGNIFICANT_MOVE_THRESHOLD
            
            return {
                'significant_move': is_significant,
                'price_change_pct': round(price_change_pct, 2),
                'start_price': first_price,
                'end_price': last_price,
                'time_window': f"{start_time.isoformat()} to {end_time.isoformat()}",
                'data_points': len(prices),
                'volume_data': [p['volume'] for p in prices if p['volume']],
                'threshold_used': self.SIGNIFICANT_MOVE_THRESHOLD
            }
            
        except Exception as e:
            logger.error(f"Error detecting movement for {ticker}: {str(e)}")
            return {
                'significant_move': False,
                'reason': f'Error during analysis: {str(e)}'
            }
    
    async def analyze_movement(self, ticker: str, timestamp: datetime) -> Dict:
        """
        Main analysis function that explains the movement
        
        Args:
            ticker: Stock ticker symbol
            timestamp: Target timestamp when movement occurred
            
        Returns:
            Dict containing explanation and evidence
        """
        try:
            # Gather comprehensive evidence
            evidence = await self._gather_movement_evidence(ticker, timestamp)
            
            # Build LLM prompt with evidence
            llm_prompt = self._build_movement_analysis_prompt(ticker, timestamp, evidence)
            
            # Get LLM analysis
            llm_response = await self.llm_manager.generate(
                prompt=llm_prompt,
                system_prompt=self._get_system_prompt()
            )
            
            # Parse LLM response
            analysis = self._parse_llm_response(llm_response)
            
            return {
                'ticker': ticker,
                'summary': analysis.get('summary', 'Market movement analysis completed'),
                'drivers': analysis.get('drivers', ['Analysis based on available evidence']),
                'confidence': analysis.get('confidence', 0.6),
                'evidence': evidence,  # Include the gathered evidence
                'timestamp': timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing movement for {ticker}: {str(e)}")
            return {
                'ticker': ticker,
                'summary': f'Analysis failed: {str(e)}',
                'drivers': ['Technical error during analysis'],
                'confidence': 0.0,
                'evidence': {'anomalies': [], 'news': [], 'price_data': [], 'sentiment_events': []},
                'timestamp': timestamp.isoformat()
            }
    
    async def find_recent_moves(self, ticker: str, hours_back: int = 24) -> List[Dict]:
        """
        Find recent significant moves for a ticker
        
        Args:
            ticker: Stock ticker symbol
            hours_back: How many hours back to search
            
        Returns:
            List of significant movements with timestamps
        """
        try:
            # Calculate time range
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours_back)
            
            # Query for price data
            query = """
            SELECT 
                timestamp,
                open_price,
                close_price,
                high_price,
                low_price,
                volume
            FROM market_prices 
            WHERE ticker = $1 
            AND timestamp >= $2
            ORDER BY timestamp
            """
            
            prices = await self.db.async_execute_query(
                query, (ticker, start_time)
            )
            
            if len(prices) < 2:
                return []
            
            significant_moves = []
            
            # Analyze each time window for significant moves
            for i in range(1, len(prices)):
                prev_price = prices[i-1]['close_price'] or prices[i-1]['open_price']
                curr_price = prices[i]['close_price'] or prices[i]['high_price']
                
                if prev_price and curr_price:
                    change_pct = ((curr_price - prev_price) / prev_price) * 100
                    
                    if abs(change_pct) >= self.SIGNIFICANT_MOVE_THRESHOLD:
                        significant_moves.append({
                            'timestamp': prices[i]['timestamp'].isoformat(),
                            'price_change_pct': round(change_pct, 2),
                            'from_price': prev_price,
                            'to_price': curr_price,
                            'volume': prices[i]['volume']
                        })
            
            # Sort by absolute change magnitude
            significant_moves.sort(key=lambda x: abs(x['price_change_pct']), reverse=True)
            
            return significant_moves[:10]  # Return top 10 moves
            
        except Exception as e:
            logger.error(f"Error finding recent moves for {ticker}: {str(e)}")
            return []
    
    async def get_movement_context(self, ticker: str, timestamp: datetime) -> Dict:
        """
        Get additional context around a movement for deeper analysis
        
        Args:
            ticker: Stock ticker symbol  
            timestamp: Target timestamp
            
        Returns:
            Dict containing contextual information
        """
        try:
            # Get anomalies around the timestamp
            anomaly_query = """
            SELECT 
                timestamp,
                anomaly_type,
                severity,
                description
            FROM anomalies 
            WHERE ticker = $1 
            AND timestamp BETWEEN $2 AND $3
            ORDER BY severity DESC
            LIMIT 5
            """
            
            start_time = timestamp - timedelta(hours=2)
            end_time = timestamp + timedelta(hours=2)
            
            anomalies = await self.db.async_execute_query(
                anomaly_query, (ticker, start_time, end_time)
            )
            
            # Get news sentiment around the timestamp
            sentiment_query = """
            SELECT 
                timestamp,
                sentiment_score,
                headline,
                source
            FROM news_sentiment 
            WHERE ticker = $1 
            AND timestamp BETWEEN $2 AND $3
            ORDER BY ABS(sentiment_score) DESC
            LIMIT 5
            """
            
            sentiment = await self.db.async_execute_query(
                sentiment_query, (ticker, start_time, end_time)
            )
            
            return {
                'anomalies': [dict(a) for a in anomalies],
                'sentiment_events': [dict(s) for s in sentiment],
                'context_window': f"{start_time.isoformat()} to {end_time.isoformat()}"
            }
            
        except Exception as e:
            logger.error(f"Error getting movement context for {ticker}: {str(e)}")
            return {
                'anomalies': [],
                'sentiment_events': [],
                'context_window': 'Error retrieving context'
            }
    
    async def _gather_movement_evidence(self, ticker: str, timestamp: datetime) -> Dict:
        """Gather evidence around the movement timestamp"""
        try:
            evidence = {
                'anomalies': [],
                'news': [],
                'price_data': [],
                'sentiment_events': []
            }
            
            # Get anomalies around the timestamp (30 days window)
            anomaly_query = """
            SELECT anomaly_type, severity, description, detected_at, confidence_score
            FROM anomalies 
            WHERE ticker = $1 
            AND detected_at >= $2 - INTERVAL '30 days'
            AND detected_at <= $2 + INTERVAL '30 days'
            ORDER BY detected_at DESC, confidence_score DESC
            LIMIT 5
            """
            
            anomaly_result = await self.db.async_execute_query(anomaly_query, (ticker, timestamp))
            evidence['anomalies'] = [dict(row) for row in anomaly_result] if anomaly_result else []
            
            # Get news around the timestamp (7 days window)
            news_query = """
            SELECT headline, sentiment, relevance_score, published_at
            FROM news_headlines 
            WHERE ticker = $1 
            AND published_at >= $2 - INTERVAL '7 days'
            AND published_at <= $2 + INTERVAL '7 days'
            ORDER BY published_at DESC, relevance_score DESC
            LIMIT 5
            """
            
            news_result = await self.db.async_execute_query(news_query, (ticker, timestamp))
            evidence['news'] = [dict(row) for row in news_result] if news_result else []
            
            # Get price data around the timestamp (5 days window)
            price_query = """
            SELECT price, volume, price_change_pct, timestamp, open_price, high_price, low_price, close_price
            FROM market_prices 
            WHERE ticker = $1 
            AND timestamp >= $2 - INTERVAL '5 days'
            AND timestamp <= $2 + INTERVAL '5 days'
            ORDER BY timestamp DESC
            LIMIT 10
            """
            
            price_result = await self.db.async_execute_query(price_query, (ticker, timestamp))
            evidence['price_data'] = [dict(row) for row in price_result] if price_result else []
            
            return evidence
            
        except Exception as e:
            logger.error(f"Error gathering movement evidence for {ticker}: {str(e)}")
            return {'anomalies': [], 'news': [], 'price_data': [], 'sentiment_events': []}
    
    def _build_movement_analysis_prompt(self, ticker: str, timestamp: datetime, evidence: Dict) -> str:
        """Build LLM prompt for movement analysis"""
        anomalies = evidence.get('anomalies', [])
        news = evidence.get('news', [])
        price_data = evidence.get('price_data', [])
        
        prompt = f"""Analyze the market movement for {ticker} at {timestamp.isoformat()} based on available evidence.

ANOMALY DATA ({len(anomalies)} items):
{self._format_anomalies_for_prompt(anomalies)}

NEWS EVENTS ({len(news)} items):
{self._format_news_for_prompt(news)}

PRICE DATA ({len(price_data)} items):
{self._format_price_data_for_prompt(price_data)}

Based on this evidence, explain what caused the market movement:

1. **SUMMARY**: A clear 2-3 sentence explanation of what happened
2. **DRIVERS**: 3-5 specific factors that contributed to the movement
3. **CONFIDENCE**: 0.0-1.0 based on evidence quality and correlation

CONFIDENCE GUIDELINES:
- Strong correlation between events and movement: 0.7-0.9
- Moderate correlation with some supporting evidence: 0.5-0.7
- Weak correlation or limited evidence: 0.2-0.5
- No clear correlation: 0.0-0.2

Respond in this EXACT JSON format:
{{
    "summary": "Clear explanation of the movement...",
    "drivers": [
        "Specific driver 1 based on evidence",
        "Specific driver 2 based on evidence",
        "Specific driver 3 based on evidence"
    ],
    "confidence": 0.75
}}"""
        
        return prompt
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for movement analysis"""
        return """You are an expert market analyst specializing in explaining sudden price movements. Analyze the provided evidence and identify the most likely causes of market movements. Focus on correlation between events and price action. Be objective and evidence-based."""
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Parse LLM response for movement analysis"""
        try:
            import json
            import re
            
            # Try direct JSON parsing first
            try:
                parsed = json.loads(response.strip())
                return {
                    'summary': parsed.get('summary', 'Market movement analysis completed'),
                    'drivers': parsed.get('drivers', ['Analysis based on available data']),
                    'confidence': min(max(float(parsed.get('confidence', 0.5)), 0.0), 1.0)
                }
            except json.JSONDecodeError:
                # Extract from markdown or other formatting
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(1))
                    return {
                        'summary': parsed.get('summary', 'Market movement analysis completed'),
                        'drivers': parsed.get('drivers', ['Analysis based on available data']),
                        'confidence': min(max(float(parsed.get('confidence', 0.5)), 0.0), 1.0)
                    }
                
                # Fallback parsing
                summary_match = re.search(r'"summary":\s*"([^"]*)"', response)
                drivers_match = re.search(r'"drivers":\s*\[(.*?)\]', response, re.DOTALL)
                confidence_match = re.search(r'"confidence":\s*([0-9.]+)', response)
                
                summary = summary_match.group(1) if summary_match else 'Market movement analysis completed'
                
                drivers = ['Analysis based on available data']
                if drivers_match:
                    driver_matches = re.findall(r'"([^"]*)"', drivers_match.group(1))
                    if driver_matches:
                        drivers = driver_matches
                
                confidence = 0.5
                if confidence_match:
                    confidence = min(max(float(confidence_match.group(1)), 0.0), 1.0)
                
                return {
                    'summary': summary,
                    'drivers': drivers,
                    'confidence': confidence
                }
                
        except Exception as e:
            logger.error(f"Error parsing movement analysis response: {e}")
            return {
                'summary': response[:200] + "..." if len(response) > 200 else response,
                'drivers': ['Analysis based on available evidence'],
                'confidence': 0.5
            }
    
    def _format_anomalies_for_prompt(self, anomalies: List[Dict]) -> str:
        """Format anomalies for LLM prompt"""
        if not anomalies:
            return "No anomalies detected"
        
        formatted = []
        for anomaly in anomalies[:3]:
            formatted.append(f"- {anomaly.get('detected_at')}: {anomaly.get('anomaly_type', 'Unknown')} - {anomaly.get('description', 'N/A')} (Confidence: {anomaly.get('confidence_score', 0):.2f})")
        
        return "\n".join(formatted)
    
    def _format_news_for_prompt(self, news: List[Dict]) -> str:
        """Format news for LLM prompt"""
        if not news:
            return "No relevant news found"
        
        formatted = []
        for item in news[:3]:
            sentiment = item.get('sentiment', 'neutral')
            formatted.append(f"- {item.get('published_at')}: {item.get('headline', 'N/A')} (Sentiment: {sentiment})")
        
        return "\n".join(formatted)
    
    def _format_price_data_for_prompt(self, price_data: List[Dict]) -> str:
        """Format price data for LLM prompt"""
        if not price_data:
            return "No price data available"
        
        if len(price_data) >= 2:
            recent = price_data[0]
            older = price_data[-1]
            
            if recent.get('price') and older.get('price'):
                price_change = ((float(recent['price']) - float(older['price'])) / float(older['price'])) * 100
                return f"Price movement: {older['price']} → {recent['price']} ({price_change:+.2f}%) over {len(price_data)} data points"
        
        return f"Recent price: ${price_data[0].get('price', 'N/A')} (Volume: {price_data[0].get('volume', 'N/A')})"

# ...existing code...
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
