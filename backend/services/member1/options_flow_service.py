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
from ...rag_engine.vector_store import ChromaVectorStore
from ...rag_engine.llm_manager import LLMManager
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
        self.vector_store = ChromaVectorStore()
        self.llm_manager = LLMManager()
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
            
            # Step 3.5: Get vector database evidence  
            vector_evidence = await self._get_vector_evidence(ticker, user_question)
            
            # Build comprehensive evidence for LLM
            all_evidence = {
                'anomalies': anomalies,
                'market_data': market_data,
                'supporting_evidence': evidence,
                'vector_evidence': vector_evidence
            }
            
            # Step 5: Generate LLM analysis
            analysis = await self._generate_llm_analysis(ticker, user_question, all_evidence)
            
            return {
                'ticker': ticker,
                'insight': analysis.get('insight', 'Analysis completed'),
                'reasons': analysis.get('reasons', ['Data analysis performed']),
                'confidence': analysis.get('confidence', 0.6),
                'evidence': self._format_evidence_for_response(all_evidence),
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
            SELECT headline, overall_sentiment_label, relevance_score, published_at
            FROM news_headlines 
            WHERE ticker = $1 
            AND published_at >= NOW() - INTERVAL '30 days'
            ORDER BY published_at DESC, relevance_score DESC
            LIMIT 5
            """
            
            news_result = await self.db.async_execute_query(news_query, (ticker,))
            if news_result:
                for row in news_result:
                    evidence.append({
                        'source': 'news',
                        'content': row['headline'],
                        'sentiment': row.get('overall_sentiment_label'),
                        'relevance_score': float(row.get('relevance_score', 0.8)),
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

    async def _get_vector_evidence(self, ticker: str, question: str) -> List[Dict]:
        """Get evidence from vector database"""
        try:
            # Search vector database for relevant context
            search_query = f"{ticker} options flow unusual activity {question}"
            
            results = self.vector_store.query_documents(
                query_texts=[search_query],
                n_results=3,
                where={"ticker": ticker} if ticker else None
            )
            
            evidence = []
            if results and results.get('documents') and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results.get('metadatas', [[]])[0]
                    distances = results.get('distances', [[]])[0]
                    
                    score = 1.0 - (distances[i] if i < len(distances) else 0.5)
                    evidence.append({
                        'source': 'vector_db',
                        'content': doc,
                        'relevance_score': max(0.0, score),
                        'metadata': metadata[i] if i < len(metadata) else {}
                    })
            
            return evidence
            
        except Exception as e:
            logger.error(f"Error fetching vector evidence for {ticker}: {str(e)}")
            return []

    async def _generate_llm_analysis(self, ticker: str, question: str, evidence: Dict) -> Dict:
        """Generate LLM-powered analysis from evidence"""
        try:
            # Build comprehensive prompt with all evidence
            prompt = self._build_analysis_prompt(ticker, question, evidence)
            
            # Get LLM completion
            llm_response = await self.llm_manager.generate(
                prompt=prompt,
                system_prompt=self._get_system_prompt()
            )
            
            # Parse LLM response
            analysis = self._parse_llm_response(llm_response)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating LLM analysis for {ticker}: {str(e)}")
            return {
                'insight': 'LLM analysis unavailable',
                'reasons': [f'LLM error: {str(e)}'],
                'confidence': 0.2
            }

    def _format_evidence_for_response(self, all_evidence: Dict) -> List[Dict]:
        """Format evidence for API response"""
        formatted_evidence = []
        
        # Format anomalies
        for anomaly in all_evidence.get('anomalies', []):
            formatted_evidence.append({
                'type': 'anomaly',
                'details': {
                    'anomaly_type': anomaly.get('anomaly_type'),
                    'severity': anomaly.get('severity'),
                    'description': anomaly.get('description'),
                    'confidence': anomaly.get('confidence_score')
                }
            })
        
        # Format market data
        market_data = all_evidence.get('market_data')
        if market_data:
            formatted_evidence.append({
                'type': 'market_data',
                'details': {
                    'current_price': market_data.get('current_price'),
                    'volume': market_data.get('volume'),
                    'price_change': market_data.get('price_change')
                }
            })
        
        # Format supporting evidence
        for evidence in all_evidence.get('supporting_evidence', [])[:3]:  # Limit to top 3
            formatted_evidence.append({
                'type': evidence.get('source'),
                'details': {
                    'content': evidence.get('content'),
                    'relevance_score': evidence.get('relevance_score'),
                    'timestamp': str(evidence.get('timestamp', ''))
                }
            })
        
        # Format vector evidence
        for evidence in all_evidence.get('vector_evidence', [])[:3]:  # Limit to top 3
            formatted_evidence.append({
                'type': 'vector_search',
                'details': {
                    'content': evidence.get('content'),
                    'relevance_score': evidence.get('relevance_score'),
                    'metadata': evidence.get('metadata', {})
                }
            })
        
        return formatted_evidence

    def _build_analysis_prompt(self, ticker: str, question: str, evidence: Dict) -> str:
        """Build prompt for LLM analysis"""
        anomalies = evidence.get('anomalies', [])
        market_data = evidence.get('market_data', {})
        supporting_evidence = evidence.get('supporting_evidence', [])
        
        prompt = f"""Analyze the options flow for {ticker} based on the available evidence.

USER QUESTION: {question}

RECENT ANOMALIES ({len(anomalies)} found):
{self._format_anomalies_for_prompt(anomalies)}

CURRENT MARKET DATA:
{self._format_market_data_for_prompt(market_data)}

SUPPORTING EVIDENCE ({len(supporting_evidence)} items):
{self._format_supporting_evidence_for_prompt(supporting_evidence)}

Based on this evidence, provide an options flow analysis with:

1. **CLEAR INSIGHT**: A 2-3 sentence summary of what the options activity suggests
2. **SPECIFIC REASONS**: 3-5 concrete reasons that support your analysis (based on the evidence above)  
3. **CONFIDENCE SCORE**: 0.0-1.0 based on evidence quality and certainty

IMPORTANT: 
- If you have strong evidence from anomalies/volume/news, confidence should be 0.7-0.9
- If you have moderate evidence, confidence should be 0.5-0.7  
- If you have little evidence, confidence should be 0.2-0.5
- Base your reasons ONLY on the evidence provided above
- Be specific about volume patterns, IV changes, or institutional positioning when mentioned in evidence

Respond in this EXACT JSON format:
{{
    "insight": "Your main insight about the options flow pattern...",
    "reasons": [
        "Specific reason 1 based on evidence",
        "Specific reason 2 based on evidence", 
        "Specific reason 3 based on evidence"
    ],
    "confidence": 0.75
}}"""
        
        return prompt

    def _get_system_prompt(self) -> str:
        """Get system prompt for options analysis"""
        return """You are an expert options flow analyst. Analyze unusual options activity patterns and provide clear, evidence-based insights. Focus on institutional positioning, volume spikes, and IV changes. Never provide trading advice."""

    def _parse_llm_response(self, response: str) -> Dict:
        """Parse LLM response into structured format"""
        try:
            # Try to extract JSON from response if it's wrapped in markdown or other text
            import json
            import re
            
            # First try direct JSON parsing
            try:
                parsed = json.loads(response.strip())
                return {
                    'insight': parsed.get('insight', 'Analysis completed'),
                    'reasons': parsed.get('reasons', ['Based on available data']),
                    'confidence': min(max(float(parsed.get('confidence', 0.5)), 0.0), 1.0)
                }
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks or other wrapping
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    parsed = json.loads(json_str)
                    return {
                        'insight': parsed.get('insight', 'Analysis completed'),
                        'reasons': parsed.get('reasons', ['Based on available data']),
                        'confidence': min(max(float(parsed.get('confidence', 0.5)), 0.0), 1.0)
                    }
                
                # If still can't parse, try to find individual fields
                insight_match = re.search(r'"insight":\s*"([^"]*)"', response)
                reasons_match = re.search(r'"reasons":\s*\[(.*?)\]', response, re.DOTALL)
                confidence_match = re.search(r'"confidence":\s*([0-9.]+)', response)
                
                insight = insight_match.group(1) if insight_match else 'Analysis completed'
                
                reasons = ['Based on available data']
                if reasons_match:
                    reasons_str = reasons_match.group(1)
                    # Extract individual reasons from array
                    reason_matches = re.findall(r'"([^"]*)"', reasons_str)
                    if reason_matches:
                        reasons = reason_matches
                
                confidence = 0.5
                if confidence_match:
                    confidence = min(max(float(confidence_match.group(1)), 0.0), 1.0)
                
                return {
                    'insight': insight,
                    'reasons': reasons,
                    'confidence': confidence
                }
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            # Fallback if all parsing fails
            return {
                'insight': response[:200] + "..." if len(response) > 200 else response,
                'reasons': ['Analysis based on available evidence'],
                'confidence': 0.5
            }

    def _format_anomalies_for_prompt(self, anomalies: List[Dict]) -> str:
        """Format anomalies for LLM prompt"""
        if not anomalies:
            return "No recent anomalies detected"
        
        formatted = []
        for anomaly in anomalies[:5]:  # Top 5 anomalies
            formatted.append(f"- {anomaly.get('anomaly_type', 'Unknown')}: {anomaly.get('description', 'N/A')} (Severity: {anomaly.get('severity', 'Unknown')}, Confidence: {anomaly.get('confidence_score', 0):.2f})")
        
        return "\n".join(formatted)

    def _format_market_data_for_prompt(self, market_data: Dict) -> str:
        """Format market data for LLM prompt"""
        if not market_data:
            return "No recent market data available"
        
        return f"""Current Price: ${market_data.get('current_price', 'N/A')}
Volume: {market_data.get('volume', 'N/A'):,} shares
Price Change: {market_data.get('price_change', 0):.2f}%"""

    def _format_supporting_evidence_for_prompt(self, evidence: List[Dict]) -> str:
        """Format supporting evidence for LLM prompt"""
        if not evidence:
            return "No additional supporting evidence"
        
        formatted = []
        for item in evidence[:3]:  # Top 3 items
            formatted.append(f"- {item.get('source', 'Unknown')}: {item.get('content', 'N/A')}")
        
        return "\n".join(formatted)
