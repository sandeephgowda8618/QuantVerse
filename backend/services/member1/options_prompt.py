"""
Member 1: Options Flow Prompt Builder
Constructs prompts for options flow analysis and interpretation.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class OptionsPrompt:
    """
    Builds structured prompts for options flow analysis using retrieved data.
    """
    
    def __init__(self):
        self.system_prompt = """You are an expert options flow analyst specializing in interpreting unusual options activity and market movements. Your role is to analyze options data, market conditions, and provide actionable insights.

ANALYSIS FRAMEWORK:
1. Identify unusual options activity patterns
2. Correlate with market price movements and volume
3. Assess sentiment and directional bias
4. Evaluate magnitude and timing implications
5. Provide confidence-based insights

RESPONSE FORMAT:
- Insight: Clear, actionable interpretation
- Reasons: 3-5 specific supporting factors
- Confidence: 0.0-1.0 score
- Risk factors: Key uncertainties to monitor
"""
        
        logger.info("OptionsPrompt initialized")
    
    def build_analysis_prompt(
        self, 
        ticker: str, 
        user_question: str,
        market_data: Optional[Dict[str, Any]] = None,
        anomalies: Optional[List[Dict[str, Any]]] = None,
        evidence: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Build comprehensive prompt for options flow analysis.
        
        Args:
            ticker: Stock ticker symbol
            user_question: User's specific question
            market_data: Recent price and volume data
            anomalies: Detected options/volume anomalies
            evidence: Supporting evidence from database
            
        Returns:
            str: Complete prompt for analysis
        """
        
        prompt_parts = [self.system_prompt]
        
        # Add current analysis context
        prompt_parts.append(f"\nANALYSIS REQUEST:")
        prompt_parts.append(f"Ticker: {ticker}")
        prompt_parts.append(f"Question: {user_question}")
        prompt_parts.append(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
        
        # Add market data if available
        if market_data:
            prompt_parts.append(f"\nCURRENT MARKET DATA:")
            prompt_parts.append(self._format_market_data(market_data))
        
        # Add anomalies if available  
        if anomalies:
            prompt_parts.append(f"\nDETECTED ANOMALIES:")
            prompt_parts.append(self._format_anomalies(anomalies))
        
        # Add supporting evidence
        if evidence:
            prompt_parts.append(f"\nSUPPORTING EVIDENCE:")
            prompt_parts.append(self._format_evidence(evidence))
        
        # Add analysis instructions
        prompt_parts.append(f"\nANALYSIS INSTRUCTIONS:")
        prompt_parts.append("1. Analyze the provided data for unusual options activity patterns")
        prompt_parts.append("2. Consider market context and price movements")
        prompt_parts.append("3. Identify key directional signals and sentiment indicators")
        prompt_parts.append("4. Assess confidence based on data quality and pattern clarity")
        prompt_parts.append("5. Provide specific, actionable insights")
        
        prompt_parts.append(f"\nPlease provide your analysis in this exact JSON format:")
        prompt_parts.append("""{
    "insight": "Primary interpretation of the options activity",
    "reasons": [
        "Specific reason 1 with data support",
        "Specific reason 2 with data support", 
        "Specific reason 3 with data support"
    ],
    "confidence": 0.75,
    "risk_factors": [
        "Key uncertainty 1",
        "Key uncertainty 2"
    ]
}""")
        
        return "\n".join(prompt_parts)
    
    def _format_market_data(self, market_data: Dict[str, Any]) -> str:
        """Format market data for prompt inclusion."""
        formatted_lines = []
        
        if 'current_price' in market_data:
            formatted_lines.append(f"Current Price: ${market_data['current_price']}")
        if 'price_change' in market_data:
            formatted_lines.append(f"Price Change: {market_data['price_change']}%")
        if 'volume' in market_data:
            formatted_lines.append(f"Volume: {market_data['volume']:,}")
        if 'volume_ratio' in market_data:
            formatted_lines.append(f"Volume vs Average: {market_data['volume_ratio']:.2f}x")
        
        return "\n".join(formatted_lines) if formatted_lines else "Market data unavailable"
    
    def _format_anomalies(self, anomalies: List[Dict[str, Any]]) -> str:
        """Format anomaly data for prompt inclusion."""
        if not anomalies:
            return "No significant anomalies detected"
        
        formatted_lines = []
        for i, anomaly in enumerate(anomalies[:5], 1):  # Limit to top 5
            anomaly_type = anomaly.get('anomaly_type', 'Unknown')
            severity = anomaly.get('severity', 'Unknown')
            description = anomaly.get('description', 'No description')
            timestamp = anomaly.get('detected_at', 'Unknown time')
            
            formatted_lines.append(f"{i}. {anomaly_type} (Severity: {severity})")
            formatted_lines.append(f"   Description: {description}")
            formatted_lines.append(f"   Time: {timestamp}")
        
        return "\n".join(formatted_lines)
    
    def _format_evidence(self, evidence: List[Dict[str, Any]]) -> str:
        """Format supporting evidence for prompt inclusion."""
        if not evidence:
            return "No additional evidence available"
        
        formatted_lines = []
        for i, item in enumerate(evidence[:5], 1):  # Limit to top 5
            source = item.get('source', 'Unknown')
            content = item.get('content', 'No content')
            relevance = item.get('relevance_score', 0)
            
            formatted_lines.append(f"{i}. Source: {source} (Relevance: {relevance:.2f})")
            formatted_lines.append(f"   Content: {content}")
        
        return "\n".join(formatted_lines)
    
    def build_simple_prompt(self, ticker: str, question: str) -> str:
        """
        Build a simplified prompt when minimal data is available.
        
        Args:
            ticker: Stock ticker symbol  
            question: User's question
            
        Returns:
            str: Simple analysis prompt
        """
        return f"""{self.system_prompt}

ANALYSIS REQUEST:
Ticker: {ticker}
Question: {question}
Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

Note: Limited data available. Please provide general guidance based on typical options flow patterns for this ticker.

Please provide your analysis in this exact JSON format:
{{
    "insight": "General interpretation based on typical patterns",
    "reasons": [
        "Reason 1 based on general market knowledge",
        "Reason 2 based on ticker characteristics",
        "Reason 3 based on current market conditions"
    ],
    "confidence": 0.45,
    "risk_factors": [
        "Data limitation uncertainty",
        "Market condition uncertainty"
    ]
}}"""
