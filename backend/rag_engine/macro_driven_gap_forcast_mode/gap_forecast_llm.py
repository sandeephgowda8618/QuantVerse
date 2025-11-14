"""
Gap Forecast LLM - Language Model Integration for Gap Prediction

This module handles LLM integration specialized for macro-driven gap forecasting
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class GapForecastLLM:
    """LLM integration specialized for macro-driven gap forecasting"""
    
    def __init__(self, llm_manager):
        """Initialize with LLM manager dependency"""
        self.llm_manager = llm_manager
        self.system_prompt = self._build_system_prompt()
        
    def _build_system_prompt(self) -> str:
        """Build specialized system prompt for gap forecasting"""
        return """You are an expert macro-driven gap forecasting analyst with deep knowledge of:
- Central bank policy interpretation and market impact prediction
- Fed/RBI/ECB communications analysis and sentiment classification  
- Historical gap patterns following macro events and policy announcements
- Cross-asset correlations and global macro spillovers
- Overnight gap formation mechanics and probability assessment

Your role is to predict overnight gaps based on macro events and provide:
1. Gap direction prediction (up/down/neutral)
2. Magnitude estimates with confidence intervals
3. Primary macro catalyst identification
4. Historical pattern analysis and reliability assessment
5. Timeline and cross-asset implications

CRITICAL CONSTRAINTS:
- NEVER provide trading advice or investment recommendations
- Focus only on gap prediction analysis and pattern interpretation
- Always include confidence levels and historical basis assessment
- Highlight when macro signals are conflicting or unclear
- Distinguish between high-conviction patterns and speculative predictions

Respond ONLY with valid JSON matching the required schema."""

    async def predict_gap_direction(self, 
                                  macro_events: List[Dict], 
                                  historical_patterns: List[Dict],
                                  market_context: Dict,
                                  asset: str) -> Dict[str, Any]:
        """
        Predict gap direction using macro events and historical patterns
        """
        try:
            prompt = self._build_gap_prediction_prompt(
                macro_events, historical_patterns, market_context, asset
            )
            
            response = await self.llm_manager.get_completion(
                prompt=prompt,
                system_prompt=self.system_prompt,
                max_tokens=2000,
                temperature=0.1
            )
            
            # Parse and validate the response
            prediction = self._parse_and_validate_response(response)
            
            # Calculate forecast confidence
            prediction['confidence'] = self._calculate_forecast_confidence(
                historical_patterns, macro_events
            )
            
            return self._format_gap_forecast(prediction)
            
        except Exception as e:
            logger.error(f"Gap direction prediction failed: {e}")
            return self._create_error_response(str(e))
    
    async def analyze_macro_impact(self, 
                                 central_bank_communication: Dict, 
                                 policy_changes: List[Dict]) -> Dict[str, Any]:
        """
        Analyze macro impact from central bank communications and policy changes
        """
        try:
            combined_evidence = [
                {"type": "central_bank_communication", "data": central_bank_communication},
                {"type": "policy_changes", "data": policy_changes}
            ]
            
            return await self.predict_gap_direction(
                macro_events=combined_evidence,
                historical_patterns=[],
                market_context={},
                asset="MARKET"
            )
            
        except Exception as e:
            logger.error(f"Macro impact analysis failed: {e}")
            return self._create_error_response(str(e))
    
    def _build_gap_prediction_prompt(self, 
                                   macro_events: List[Dict],
                                   historical_patterns: List[Dict],
                                   market_context: Dict,
                                   asset: str) -> str:
        """
        Build prompt for gap prediction
        """
        macro_text = self._format_macro_events(macro_events)
        historical_text = self._format_historical_patterns(historical_patterns)
        context_text = self._format_market_context(market_context)
        
        return f"""
Predict overnight gap for {asset} based on the following macro evidence:

UPCOMING MACRO EVENTS:
{macro_text}

HISTORICAL GAP PATTERNS:
{historical_text}

CURRENT MARKET CONTEXT:
{context_text}

Analyze the macro events, their historical impact on {asset} gaps, and current market conditions.
Provide a comprehensive gap forecast with the following JSON structure:

{{
    "gap_prediction": "gap_up" | "gap_down" | "neutral" | "indeterminate",
    "probability": 0.65,
    "magnitude_range": {{
        "low_estimate": "0.5%",
        "high_estimate": "2.1%", 
        "most_likely": "1.2%"
    }},
    "macro_catalyst": {{
        "primary_event": "FOMC rate decision",
        "event_type": "fomc",
        "sentiment": "hawkish",
        "market_interpretation": "Markets expect 25bp hike with dovish forward guidance"
    }},
    "historical_basis": {{
        "similar_events_count": 12,
        "historical_success_rate": 0.75,
        "pattern_reliability": "strong"
    }},
    "supporting_factors": ["Factor 1", "Factor 2"],
    "risk_factors": ["Risk 1", "Risk 2"],
    "confidence": 0.72,
    "timeline": "next_session",
    "cross_asset_implications": {{
        "BTC": "likely_gap_down_0.8%",
        "SPY": "neutral_to_slight_up"
    }}
}}

Focus on evidence-based prediction with clear reasoning."""
        
    def _format_macro_events(self, events: List[Dict]) -> str:
        """Format macro events for prompt"""
        if not events:
            return "No upcoming macro events identified."
        
        formatted = []
        for event in events:
            event_str = f"- {event.get('event_type', 'Unknown')}: {event.get('description', 'No description')}"
            if event.get('event_date'):
                event_str += f" (Date: {event.get('event_date')})"
            if event.get('expected_impact'):
                event_str += f" (Impact: {event.get('expected_impact')})"
            formatted.append(event_str)
        
        return "\n".join(formatted)
    
    def _format_historical_patterns(self, patterns: List[Dict]) -> str:
        """Format historical patterns for prompt"""
        if not patterns:
            return "No historical patterns available."
        
        # Summarize patterns
        total_gaps = len(patterns)
        up_gaps = sum(1 for p in patterns if p.get('gap_direction') == 'up')
        down_gaps = sum(1 for p in patterns if p.get('gap_direction') == 'down')
        
        avg_magnitude = sum(abs(p.get('gap_size_pct', 0)) for p in patterns) / max(total_gaps, 1)
        
        return f"""
Historical Gap Analysis ({total_gaps} gaps):
- Gap Up: {up_gaps} occasions ({up_gaps/max(total_gaps,1)*100:.1f}%)
- Gap Down: {down_gaps} occasions ({down_gaps/max(total_gaps,1)*100:.1f}%)
- Average Magnitude: {avg_magnitude:.2f}%
- Largest Gap: {max((abs(p.get('gap_size_pct', 0)) for p in patterns), default=0):.2f}%
"""
    
    def _format_market_context(self, context: Dict) -> str:
        """Format market context for prompt"""
        if not context:
            return "No specific market context provided."
        
        context_items = []
        for key, value in context.items():
            context_items.append(f"- {key}: {value}")
        
        return "\n".join(context_items)
    
    def _parse_and_validate_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate LLM response"""
        try:
            # Try to parse JSON
            parsed = json.loads(response)
            
            # Validate required fields
            required_fields = [
                'gap_prediction', 'probability', 'magnitude_range',
                'macro_catalyst', 'confidence'
            ]
            
            for field in required_fields:
                if field not in parsed:
                    logger.warning(f"Missing required field: {field}")
                    parsed[field] = self._get_default_value(field)
            
            # Validate gap_prediction values
            valid_predictions = ['gap_up', 'gap_down', 'neutral', 'indeterminate']
            if parsed.get('gap_prediction') not in valid_predictions:
                parsed['gap_prediction'] = 'indeterminate'
            
            # Ensure probability is between 0 and 1
            if not (0 <= parsed.get('probability', 0.5) <= 1):
                parsed['probability'] = 0.5
            
            # Ensure confidence is between 0 and 1
            if not (0 <= parsed.get('confidence', 0.5) <= 1):
                parsed['confidence'] = 0.5
            
            return parsed
            
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
            return self._get_default_prediction()
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for missing fields"""
        defaults = {
            'gap_prediction': 'indeterminate',
            'probability': 0.5,
            'magnitude_range': {
                'low_estimate': '0%',
                'high_estimate': '1%',
                'most_likely': '0.5%'
            },
            'macro_catalyst': {
                'primary_event': 'No clear catalyst identified',
                'event_type': 'unknown',
                'sentiment': 'neutral',
                'market_interpretation': 'Mixed or unclear signals'
            },
            'historical_basis': {
                'similar_events_count': 0,
                'historical_success_rate': 0.5,
                'pattern_reliability': 'weak'
            },
            'supporting_factors': ['Limited analysis due to incomplete data'],
            'risk_factors': ['Prediction reliability uncertain'],
            'confidence': 0.3,
            'timeline': 'indeterminate',
            'cross_asset_implications': {}
        }
        
        return defaults.get(field, 'unknown')
    
    def _get_default_prediction(self) -> Dict[str, Any]:
        """Get default prediction when LLM fails"""
        return {
            'gap_prediction': 'indeterminate',
            'probability': 0.5,
            'magnitude_range': {
                'low_estimate': '0%',
                'high_estimate': '1%',
                'most_likely': '0.5%'
            },
            'macro_catalyst': {
                'primary_event': 'Analysis failed',
                'event_type': 'error',
                'sentiment': 'neutral',
                'market_interpretation': 'Unable to determine'
            },
            'historical_basis': {
                'similar_events_count': 0,
                'historical_success_rate': 0.5,
                'pattern_reliability': 'weak'
            },
            'supporting_factors': ['Analysis incomplete'],
            'risk_factors': ['Prediction unreliable'],
            'confidence': 0.1,
            'timeline': 'indeterminate',
            'cross_asset_implications': {}
        }
    
    def _calculate_forecast_confidence(self, 
                                     historical_patterns: List[Dict],
                                     macro_events: List[Dict]) -> float:
        """Calculate forecast confidence based on pattern strength and macro clarity"""
        base_confidence = 0.5
        
        # Historical pattern confidence
        if historical_patterns:
            pattern_count = len(historical_patterns)
            pattern_consistency = self._assess_pattern_consistency(historical_patterns)
            pattern_confidence = min(pattern_count / 20, 1.0) * pattern_consistency
        else:
            pattern_confidence = 0.2
        
        # Macro event clarity confidence
        if macro_events:
            event_clarity = self._assess_macro_clarity(macro_events)
            macro_confidence = event_clarity
        else:
            macro_confidence = 0.3
        
        # Combined confidence
        combined_confidence = (
            base_confidence * 0.3 +
            pattern_confidence * 0.4 +
            macro_confidence * 0.3
        )
        
        return min(max(combined_confidence, 0.1), 0.9)
    
    def _assess_pattern_consistency(self, patterns: List[Dict]) -> float:
        """Assess consistency of historical patterns"""
        if not patterns:
            return 0.0
        
        # Simple consistency metric based on gap direction distribution
        directions = [p.get('gap_direction') for p in patterns]
        up_count = directions.count('up')
        down_count = directions.count('down')
        
        if up_count == 0 or down_count == 0:
            return 0.9  # Very consistent (all same direction)
        
        # Calculate how skewed the distribution is
        total = len(directions)
        max_count = max(up_count, down_count)
        consistency = max_count / total
        
        return consistency
    
    def _assess_macro_clarity(self, events: List[Dict]) -> float:
        """Assess clarity of macro events"""
        if not events:
            return 0.3
        
        # Simple clarity assessment
        high_impact_events = sum(
            1 for event in events 
            if event.get('expected_impact', '').lower() in ['high', 'significant']
        )
        
        clarity_score = min(high_impact_events / max(len(events), 1), 1.0)
        return max(clarity_score, 0.4)
    
    def _format_gap_forecast(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Format gap forecast for API response"""
        return {
            'gap_prediction': prediction.get('gap_prediction', 'indeterminate'),
            'probability': prediction.get('probability', 0.5),
            'magnitude_range': prediction.get('magnitude_range', {}),
            'primary_catalyst': prediction.get('macro_catalyst', {}).get('primary_event', 'Unknown'),
            'event_type': prediction.get('macro_catalyst', {}).get('event_type', 'unknown'),
            'sentiment': prediction.get('macro_catalyst', {}).get('sentiment', 'neutral'),
            'supporting_factors': prediction.get('supporting_factors', []),
            'risk_factors': prediction.get('risk_factors', []),
            'confidence': prediction.get('confidence', 0.3),
            'timeline': prediction.get('timeline', 'indeterminate'),
            'historical_basis': prediction.get('historical_basis', {}),
            'cross_asset_implications': prediction.get('cross_asset_implications', {}),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create error response for gap prediction"""
        return {
            'gap_prediction': 'error',
            'probability': 0.0,
            'magnitude_range': {
                'low_estimate': 'N/A',
                'high_estimate': 'N/A',
                'most_likely': 'N/A'
            },
            'primary_catalyst': f'Analysis error: {error_message}',
            'event_type': 'error',
            'sentiment': 'neutral',
            'supporting_factors': [],
            'risk_factors': ['Analysis failed due to technical error'],
            'confidence': 0.0,
            'timeline': 'unknown',
            'historical_basis': {
                'similar_events_count': 0,
                'historical_success_rate': 0.0,
                'pattern_reliability': 'none'
            },
            'cross_asset_implications': {},
            'analysis_timestamp': datetime.now().isoformat(),
            'error': error_message
        }
