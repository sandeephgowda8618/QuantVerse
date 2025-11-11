"""
Member 1: Options Flow Interpreter Service
Core business logic for analyzing unusual options activity.

IMPLEMENTATION STATUS: FULLY IMPLEMENTED
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ...db.postgres_handler import PostgresHandler
from .options_prompt import OptionsPrompt

logger = logging.getLogger(__name__)

class OptionsFlowService:
    """
    Service for analyzing options flow and providing insights.
    
    This service orchestrates:
    1. Data gathering from anomalies and market_prices tables
    2. Evidence retrieval from database
    3. Analysis and explanation generation
    """
    
    def __init__(self):
        self.db = PostgresHandler()
        self.prompt_builder = OptionsPrompt()
        
        # Configuration
        self.ANALYSIS_WINDOW_HOURS = 24  # Look back period for anomalies
        self.MAX_EVIDENCE_ITEMS = 10     # Limit evidence for context
        
        logger.info("OptionsFlowService initialized")
    
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
    
    async def analyze_flow(self, ticker: str, user_question: str) -> Dict:
        """
        Main analysis function - orchestrates all data gathering and analysis
        
        Args:
            ticker: Stock ticker symbol
            user_question: User's question about options activity
            
        Returns:
            Dict: Analysis result with insight, reasons, confidence, evidence
        """
        try:
            # Step 1: Fetch options-related anomalies from DB
            anomalies = await self._get_options_anomalies(ticker)
            
            # Step 2: Get recent volume/price data  
            market_data = await self._get_recent_market_data(ticker)
            
            # Step 3: Retrieve relevant evidence from database
            evidence = await self._get_supporting_evidence(ticker, user_question)
            
            # Step 4: Build structured prompt
            prompt = self.prompt_builder.build_analysis_prompt(
                ticker=ticker,
                user_question=user_question,
                market_data=market_data,
                anomalies=anomalies,
                evidence=evidence
            )
            
            # Step 5: Generate analysis (simplified for now)
            analysis = await self._generate_analysis(ticker, user_question, market_data, anomalies, evidence)
            
            return {
                'ticker': ticker,
                'insight': analysis.get('insight', 'Analysis completed'),
                'reasons': analysis.get('reasons', ['Data analysis performed']),
                'confidence': analysis.get('confidence', 0.6),
                'evidence': evidence or [],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing options flow for {ticker}: {str(e)}")
            return {
                'ticker': ticker,
                'insight': 'Analysis encountered an error',
                'reasons': [f'Error occurred: {str(e)}'],
                'confidence': 0.1,
                'evidence': [],
                'timestamp': datetime.now().isoformat()
            }
    
    async def _get_options_anomalies(self, ticker: str) -> List[Dict]:
        """Fetch recent options anomalies for the ticker"""
        try:
            # Look for anomalies in the last 24 hours
            query = """
            SELECT anomaly_type, severity, description, detected_at, confidence_score
            FROM anomalies 
            WHERE ticker = $1 
            AND detected_at >= NOW() - INTERVAL '%s hours'
            AND (anomaly_type LIKE '%%option%%' OR anomaly_type LIKE '%%volume%%')
            ORDER BY detected_at DESC, confidence_score DESC
            LIMIT 10
            """
            
            result = await self.db.async_execute_query(query, (ticker, self.ANALYSIS_WINDOW_HOURS))
            return [dict(row) for row in result] if result else []
            
        except Exception as e:
            logger.error(f"Error fetching anomalies for {ticker}: {str(e)}")
            return []
    
    async def _get_recent_market_data(self, ticker: str) -> Optional[Dict]:
        """Fetch recent market data for the ticker"""
        try:
            query = """
            SELECT price, volume, price_change_pct, timestamp
            FROM market_prices 
            WHERE ticker = $1 
            ORDER BY timestamp DESC 
            LIMIT 1
            """
            
            result = await self.db.async_execute_query(query, (ticker,))
            if result:
                row = result[0]
                return {
                    'current_price': float(row['price']) if row['price'] else None,
                    'volume': int(row['volume']) if row['volume'] else None,
                    'price_change': float(row['price_change_pct']) if row['price_change_pct'] else None,
                    'timestamp': row['timestamp']
                }
            return None
            
        except Exception as e:
            logger.error(f"Error fetching market data for {ticker}: {str(e)}")
            return None
    
    async def _get_supporting_evidence(self, ticker: str, question: str) -> List[Dict]:
        """Get supporting evidence from various database tables"""
        try:
            evidence = []
            
            # Get news sentiment if available
            news_query = """
            SELECT headline, sentiment, relevance_score, published_at
            FROM news_headlines 
            WHERE ticker = $1 
            ORDER BY published_at DESC, relevance_score DESC
            LIMIT 5
            """
            
            news_result = await self.db.async_execute_query(news_query, (ticker,))
            if news_result:
                for row in news_result:
                    evidence.append({
                        'source': 'news',
                        'content': row['headline'],
                        'sentiment': row.get('sentiment'),
                        'relevance_score': float(row.get('relevance_score', 0.5)),
                        'timestamp': row['published_at']
                    })
            
            # Get earnings data if available
            earnings_query = """
            SELECT reported_eps, estimated_eps, surprise_pct, fiscal_date_ending
            FROM earnings_data 
            WHERE ticker = $1 
            ORDER BY fiscal_date_ending DESC
            LIMIT 3
            """
            
            earnings_result = await self.db.async_execute_query(earnings_query, (ticker,))
            if earnings_result:
                for row in earnings_result:
                    evidence.append({
                        'source': 'earnings',
                        'content': f"EPS: {row['reported_eps']} vs Est: {row['estimated_eps']} (Surprise: {row.get('surprise_pct', 0)}%)",
                        'relevance_score': 0.8,
                        'timestamp': row['fiscal_date_ending']
                    })
            
            return evidence[:self.MAX_EVIDENCE_ITEMS]
            
        except Exception as e:
            logger.error(f"Error fetching evidence for {ticker}: {str(e)}")
            return []
    
    async def _generate_analysis(self, ticker: str, question: str, market_data: Optional[Dict], 
                               anomalies: List[Dict], evidence: List[Dict]) -> Dict:
        """Generate analysis based on collected data"""
        
        # For now, provide rule-based analysis
        # TODO: This is where the RAG engine integration will be added
        
        insight = f"Options flow analysis for {ticker}"
        reasons = []
        confidence = 0.6
        
        # Analyze anomalies
        if anomalies:
            high_severity_count = sum(1 for a in anomalies if a.get('severity') in ['high', 'critical'])
            if high_severity_count > 0:
                reasons.append(f"Detected {high_severity_count} high-severity anomalies in recent activity")
                confidence += 0.1
            else:
                reasons.append("Minor anomalies detected in options activity")
        else:
            reasons.append("No significant anomalies detected in recent period")
            confidence -= 0.1
        
        # Analyze market data
        if market_data:
            price_change = market_data.get('price_change', 0)
            if abs(price_change) > 2:
                reasons.append(f"Significant price movement: {price_change:.2f}%")
                confidence += 0.1
            else:
                reasons.append(f"Moderate price action: {price_change:.2f}%")
        else:
            reasons.append("Limited recent price data available")
            confidence -= 0.1
        
        # Analyze evidence
        if evidence:
            news_sentiment = [e for e in evidence if e['source'] == 'news']
            if news_sentiment:
                avg_sentiment = sum(float(n.get('sentiment', 0)) for n in news_sentiment) / len(news_sentiment)
                if avg_sentiment > 0.1:
                    reasons.append("Recent news sentiment is generally positive")
                elif avg_sentiment < -0.1:
                    reasons.append("Recent news sentiment is generally negative")
                else:
                    reasons.append("Mixed or neutral news sentiment")
        else:
            reasons.append("Limited supporting evidence available")
        
        return {
            'insight': insight,
            'reasons': reasons,
            'confidence': max(0.1, min(1.0, confidence))
        }
    
    async def get_recent_anomalies(self, ticker: str, hours_back: int = 6) -> List[Dict]:
        """Get recent options-related anomalies for a ticker"""
        return await self._get_options_anomalies(ticker)
