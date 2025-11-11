"""
Member 2: Explain Market Move Prompt Builder
Constructs prompts for explaining sudden market movements.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ExplainMovePrompt:
    """
    Builds structured prompts for market move explanation using movement data and evidence.
    """
    
    def __init__(self):
        self.system_prompt = """You are an expert market analyst specializing in explaining sudden price movements and market volatility. Your role is to analyze price movements, identify catalysts, and provide clear explanations.

ANALYSIS FRAMEWORK:
1. Identify the magnitude and timing of the movement
2. Correlate with relevant events and catalysts
3. Assess the market sentiment and institutional activity
4. Evaluate the significance and likely continuation
5. Provide confidence-based explanations

RESPONSE FORMAT:
- Explanation: Clear, comprehensive explanation of the movement
- Catalyst: Primary driver of the movement
- Supporting factors: 3-5 contributing elements
- Confidence: 0.0-1.0 score based on evidence quality
- Market implications: Forward-looking insights
"""
        
        logger.info("ExplainMovePrompt initialized")
    
    def build_movement_explanation_prompt(
        self, 
        ticker: str, 
        timestamp: str,
        movement_data: Optional[Dict[str, Any]] = None,
        events: Optional[List[Dict[str, Any]]] = None,
        sentiment_data: Optional[Dict[str, Any]] = None,
        evidence: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Build comprehensive prompt for movement explanation.
        
        Args:
            ticker: Stock ticker symbol
            timestamp: When the movement occurred
            movement_data: Price movement details
            events: Related events and catalysts
            sentiment_data: Market sentiment around the time
            evidence: Supporting evidence from database
            
        Returns:
            str: Complete prompt for analysis
        """
        
        prompt_parts = [self.system_prompt]
        
        # Add movement analysis context
        prompt_parts.append(f"\nMOVEMENT ANALYSIS REQUEST:")
        prompt_parts.append(f"Ticker: {ticker}")
        prompt_parts.append(f"Movement Timestamp: {timestamp}")
        prompt_parts.append(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
        
        # Add movement data if available
        if movement_data:
            prompt_parts.append(f"\nMOVEMENT DETAILS:")
            prompt_parts.append(self._format_movement_data(movement_data))
        
        # Add events if available  
        if events:
            prompt_parts.append(f"\nRELATED EVENTS:")
            prompt_parts.append(self._format_events(events))
        
        # Add sentiment data
        if sentiment_data:
            prompt_parts.append(f"\nMARKET SENTIMENT:")
            prompt_parts.append(self._format_sentiment_data(sentiment_data))
        
        # Add supporting evidence
        if evidence:
            prompt_parts.append(f"\nSUPPORTING EVIDENCE:")
            prompt_parts.append(self._format_evidence(evidence))
        
        # Add analysis instructions
        prompt_parts.append(f"\nANALYSIS INSTRUCTIONS:")
        prompt_parts.append("1. Analyze the magnitude and speed of the price movement")
        prompt_parts.append("2. Identify the most likely catalyst or trigger event")
        prompt_parts.append("3. Consider market context and institutional activity")
        prompt_parts.append("4. Assess the significance and potential continuation")
        prompt_parts.append("5. Provide clear, evidence-based explanation")
        
        prompt_parts.append(f"\nPlease provide your analysis in this exact JSON format:")
        prompt_parts.append("""{
    "explanation": "Comprehensive explanation of the movement and its causes",
    "primary_catalyst": "Main driver of the movement",
    "supporting_factors": [
        "Contributing factor 1 with evidence",
        "Contributing factor 2 with evidence", 
        "Contributing factor 3 with evidence"
    ],
    "confidence": 0.75,
    "market_implications": "Forward-looking insights and expectations"
}""")
        
        return "\n".join(prompt_parts)
    
    def _format_movement_data(self, movement_data: Dict[str, Any]) -> str:
        """Format movement data for prompt inclusion."""
        formatted_lines = []
        
        if 'price_change' in movement_data:
            formatted_lines.append(f"Price Change: {movement_data['price_change']}%")
        if 'price_before' in movement_data:
            formatted_lines.append(f"Price Before: ${movement_data['price_before']}")
        if 'price_after' in movement_data:
            formatted_lines.append(f"Price After: ${movement_data['price_after']}")
        if 'volume_surge' in movement_data:
            formatted_lines.append(f"Volume Surge: {movement_data['volume_surge']}x normal")
        if 'duration' in movement_data:
            formatted_lines.append(f"Movement Duration: {movement_data['duration']} minutes")
        
        return "\n".join(formatted_lines) if formatted_lines else "Movement data unavailable"
    
    def _format_events(self, events: List[Dict[str, Any]]) -> str:
        """Format event data for prompt inclusion."""
        if not events:
            return "No related events detected"
        
        formatted_lines = []
        for i, event in enumerate(events[:5], 1):  # Limit to top 5
            event_type = event.get('type', 'Unknown')
            description = event.get('description', 'No description')
            timestamp = event.get('timestamp', 'Unknown time')
            impact = event.get('impact_score', 'Unknown')
            
            formatted_lines.append(f"{i}. {event_type} (Impact: {impact})")
            formatted_lines.append(f"   Description: {description}")
            formatted_lines.append(f"   Time: {timestamp}")
        
        return "\n".join(formatted_lines)
    
    def _format_sentiment_data(self, sentiment_data: Dict[str, Any]) -> str:
        """Format sentiment data for prompt inclusion."""
        formatted_lines = []
        
        if 'overall_sentiment' in sentiment_data:
            formatted_lines.append(f"Overall Sentiment: {sentiment_data['overall_sentiment']}")
        if 'news_sentiment' in sentiment_data:
            formatted_lines.append(f"News Sentiment: {sentiment_data['news_sentiment']}")
        if 'social_sentiment' in sentiment_data:
            formatted_lines.append(f"Social Sentiment: {sentiment_data['social_sentiment']}")
        if 'sentiment_change' in sentiment_data:
            formatted_lines.append(f"Sentiment Change: {sentiment_data['sentiment_change']}")
        
        return "\n".join(formatted_lines) if formatted_lines else "Sentiment data unavailable"
    
    def _format_evidence(self, evidence: List[Dict[str, Any]]) -> str:
        """Format supporting evidence for prompt inclusion."""
        if not evidence:
            return "No additional evidence available"
        
        formatted_lines = []
        for i, item in enumerate(evidence[:5], 1):  # Limit to top 5
            source = item.get('source', 'Unknown')
            content = item.get('content', 'No content')
            relevance = item.get('relevance_score', 0)
            timestamp = item.get('timestamp', 'Unknown')
            
            formatted_lines.append(f"{i}. Source: {source} (Relevance: {relevance:.2f})")
            formatted_lines.append(f"   Content: {content}")
            formatted_lines.append(f"   Time: {timestamp}")
        
        return "\n".join(formatted_lines)
    
    def build_simple_explanation_prompt(self, ticker: str, timestamp: str, price_change: float) -> str:
        """
        Build a simplified prompt when minimal data is available.
        
        Args:
            ticker: Stock ticker symbol  
            timestamp: Movement timestamp
            price_change: Price change percentage
            
        Returns:
            str: Simple explanation prompt
        """
        return f"""{self.system_prompt}

MOVEMENT ANALYSIS REQUEST:
Ticker: {ticker}
Movement Timestamp: {timestamp}
Price Change: {price_change}%
Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

Note: Limited data available. Please provide general explanation based on typical market patterns.

Please provide your analysis in this exact JSON format:
{{
    "explanation": "General explanation based on movement characteristics and timing",
    "primary_catalyst": "Most likely catalyst type based on movement pattern",
    "supporting_factors": [
        "Factor 1 based on movement characteristics",
        "Factor 2 based on timing analysis",
        "Factor 3 based on market context"
    ],
    "confidence": 0.50,
    "market_implications": "General expectations based on movement type"
}}"""
