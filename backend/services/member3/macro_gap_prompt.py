"""
Member 3: Macro Gap Prediction Prompt Builder
Constructs prompts for predicting overnight gaps based on macro events.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MacroGapPrompt:
    """
    Builds structured prompts for macro-driven gap prediction analysis.
    """
    
    def __init__(self):
        self.system_prompt = """You are an expert macro analyst specializing in predicting overnight market gaps based on macro economic events. Your role is to analyze macro catalysts, historical patterns, and market conditions to forecast gap direction and magnitude.

ANALYSIS FRAMEWORK:
1. Identify relevant macro events and their market impact potential
2. Analyze historical gap patterns after similar events
3. Assess current market sentiment and positioning
4. Evaluate confluence of factors and timing
5. Provide directional bias with confidence-based magnitude estimates

RESPONSE FORMAT:
- Gap prediction: Direction and estimated magnitude
- Primary catalyst: Main macro driver
- Supporting factors: 3-5 reinforcing elements
- Confidence: 0.0-1.0 score based on pattern clarity
- Risk scenarios: Alternative outcomes to monitor
"""
        
        logger.info("MacroGapPrompt initialized")
    
    def build_gap_prediction_prompt(
        self, 
        ticker: str, 
        macro_events: Optional[Dict[str, Any]] = None,
        historical_patterns: Optional[Dict[str, Any]] = None,
        market_context: Optional[Dict[str, Any]] = None,
        sentiment_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build comprehensive prompt for gap prediction.
        
        Args:
            ticker: Asset ticker symbol
            macro_events: Upcoming/recent macro events
            historical_patterns: Historical gap patterns for similar events
            market_context: Current market conditions
            sentiment_data: Market sentiment indicators
            
        Returns:
            str: Complete prompt for analysis
        """
        
        prompt_parts = [self.system_prompt]
        
        # Add gap prediction context
        prompt_parts.append(f"\nGAP PREDICTION REQUEST:")
        prompt_parts.append(f"Asset: {ticker}")
        prompt_parts.append(f"Prediction For: Next trading session (overnight gap)")
        prompt_parts.append(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
        
        # Add macro events if available
        if macro_events:
            prompt_parts.append(f"\nMACRO EVENTS:")
            prompt_parts.append(self._format_macro_events(macro_events))
        
        # Add historical patterns  
        if historical_patterns:
            prompt_parts.append(f"\nHISTORICAL PATTERNS:")
            prompt_parts.append(self._format_historical_patterns(historical_patterns))
        
        # Add market context
        if market_context:
            prompt_parts.append(f"\nMARKET CONTEXT:")
            prompt_parts.append(self._format_market_context(market_context))
            
        # Add sentiment data
        if sentiment_data:
            prompt_parts.append(f"\nSENTIMENT INDICATORS:")
            prompt_parts.append(self._format_sentiment_data(sentiment_data))
        
        # Add analysis instructions
        prompt_parts.append(f"\nANALYSIS INSTRUCTIONS:")
        prompt_parts.append("1. Identify the primary macro catalyst for potential gap")
        prompt_parts.append("2. Assess historical precedent and pattern reliability")
        prompt_parts.append("3. Consider current market positioning and sentiment")
        prompt_parts.append("4. Evaluate confluence of bullish/bearish factors")
        prompt_parts.append("5. Provide specific gap direction and magnitude estimate")
        
        prompt_parts.append(f"\nPlease provide your analysis in this exact JSON format:")
        prompt_parts.append("""{
    "gap_prediction": {
        "direction": "gap_up|gap_down|no_gap",
        "magnitude_estimate": "0.5% to 1.2%",
        "probability": 0.75
    },
    "primary_catalyst": "Main macro event driving the prediction",
    "supporting_factors": [
        "Factor 1 supporting the prediction",
        "Factor 2 reinforcing the direction", 
        "Factor 3 adding to confidence"
    ],
    "confidence": 0.80,
    "risk_scenarios": [
        "Alternative outcome 1 if catalyst fails",
        "Risk factor that could reverse prediction"
    ]
}""")
        
        return "\n".join(prompt_parts)
    
    def _format_macro_events(self, macro_events: Dict[str, Any]) -> str:
        """Format macro events for prompt inclusion."""
        formatted_lines = []
        
        if 'upcoming_events' in macro_events:
            formatted_lines.append("Upcoming Events:")
            for event in macro_events['upcoming_events'][:5]:  # Top 5
                event_type = event.get('type', 'Unknown')
                description = event.get('description', 'No description')
                timing = event.get('timing', 'Unknown')
                impact = event.get('impact_score', 'Unknown')
                
                formatted_lines.append(f"  - {event_type}: {description}")
                formatted_lines.append(f"    Timing: {timing}, Impact: {impact}")
        
        if 'recent_events' in macro_events:
            formatted_lines.append("\nRecent Events:")
            for event in macro_events['recent_events'][:3]:
                formatted_lines.append(f"  - {event.get('type', 'Unknown')}: {event.get('description', '')}")
        
        return "\n".join(formatted_lines) if formatted_lines else "No significant macro events detected"
    
    def _format_historical_patterns(self, patterns: Dict[str, Any]) -> str:
        """Format historical pattern data for prompt inclusion."""
        formatted_lines = []
        
        if 'event_patterns' in patterns:
            for event_type, pattern_data in patterns['event_patterns'].items():
                total_occurrences = pattern_data.get('total_occurrences', 0)
                gap_up_prob = pattern_data.get('gap_up_probability', 0)
                avg_magnitude = pattern_data.get('average_magnitude', 0)
                
                formatted_lines.append(f"{event_type.upper()} Events:")
                formatted_lines.append(f"  - Total occurrences: {total_occurrences}")
                formatted_lines.append(f"  - Gap up probability: {gap_up_prob:.1%}")
                formatted_lines.append(f"  - Average magnitude: {avg_magnitude:.2f}%")
        
        if 'pattern_strength' in patterns:
            formatted_lines.append(f"\nOverall Pattern Strength: {patterns['pattern_strength']:.2f}")
        
        return "\n".join(formatted_lines) if formatted_lines else "Limited historical pattern data"
    
    def _format_market_context(self, market_context: Dict[str, Any]) -> str:
        """Format market context for prompt inclusion."""
        formatted_lines = []
        
        if 'current_trend' in market_context:
            formatted_lines.append(f"Current Trend: {market_context['current_trend']}")
        if 'volatility' in market_context:
            formatted_lines.append(f"Volatility Level: {market_context['volatility']}")
        if 'volume_profile' in market_context:
            formatted_lines.append(f"Volume Profile: {market_context['volume_profile']}")
        if 'support_resistance' in market_context:
            sr = market_context['support_resistance']
            formatted_lines.append(f"Key Levels - Support: {sr.get('support', 'N/A')}, Resistance: {sr.get('resistance', 'N/A')}")
        
        return "\n".join(formatted_lines) if formatted_lines else "Limited market context available"
    
    def _format_sentiment_data(self, sentiment_data: Dict[str, Any]) -> str:
        """Format sentiment data for prompt inclusion."""
        formatted_lines = []
        
        if 'overall_sentiment' in sentiment_data:
            formatted_lines.append(f"Overall Sentiment: {sentiment_data['overall_sentiment']}")
        if 'fear_greed_index' in sentiment_data:
            formatted_lines.append(f"Fear & Greed Index: {sentiment_data['fear_greed_index']}")
        if 'put_call_ratio' in sentiment_data:
            formatted_lines.append(f"Put/Call Ratio: {sentiment_data['put_call_ratio']}")
        if 'institutional_positioning' in sentiment_data:
            formatted_lines.append(f"Institutional Positioning: {sentiment_data['institutional_positioning']}")
        
        return "\n".join(formatted_lines) if formatted_lines else "Limited sentiment data available"
    
    def build_simple_gap_prompt(self, ticker: str, event_type: str, event_description: str) -> str:
        """
        Build a simplified prompt when minimal data is available.
        
        Args:
            ticker: Asset ticker symbol  
            event_type: Type of macro event
            event_description: Description of the event
            
        Returns:
            str: Simple gap prediction prompt
        """
        return f"""{self.system_prompt}

GAP PREDICTION REQUEST:
Asset: {ticker}
Prediction For: Next trading session (overnight gap)
Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

MACRO EVENT:
Type: {event_type}
Description: {event_description}

Note: Limited historical data available. Base prediction on general macro event impact patterns.

Please provide your analysis in this exact JSON format:
{{
    "gap_prediction": {{
        "direction": "gap_up|gap_down|no_gap",
        "magnitude_estimate": "0.3% to 0.8%",
        "probability": 0.60
    }},
    "primary_catalyst": "{event_description}",
    "supporting_factors": [
        "Factor 1 based on event type characteristics",
        "Factor 2 based on general market behavior",
        "Factor 3 based on timing considerations"
    ],
    "confidence": 0.55,
    "risk_scenarios": [
        "Market could ignore event if impact already priced in",
        "Unexpected news could override macro catalyst"
    ]
}}"""
