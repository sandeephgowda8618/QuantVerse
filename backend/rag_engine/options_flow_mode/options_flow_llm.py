"""
Options Flow LLM - Language Model Integration for Options Flow Analysis
Specialized LLM integration for interpreting and predicting options flow patterns.
"""
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class OptionsFlowLLM:
    """LLM integration specialized for options flow analysis and interpretation"""
    
    def __init__(self, llm_manager):
        """Initialize with LLM manager dependency"""
        self.llm_manager = llm_manager
        self.system_prompt = self._build_system_prompt()
        
    def _build_system_prompt(self) -> str:
        """Build specialized system prompt for options flow analysis"""
        return """You are an expert options flow analyst with deep knowledge of:
- Options market microstructure and flow interpretation
- Unusual volume detection and significance assessment  
- Volatility skew analysis and gamma exposure patterns
- Put/call ratio analysis and market sentiment indicators
- Correlation between options activity and underlying price movements

Your role is to analyze options flow data and provide insights into:
1. Flow direction (bullish/bearish/neutral/mixed)
2. Unusual activity detection and significance
3. Key strike levels with significant activity
4. Volume analysis including put/call ratios
5. Volatility insights and skew patterns
6. Time-sensitivity of the flow signals

CRITICAL CONSTRAINTS:
- NEVER provide trading advice or recommendations
- Focus only on flow interpretation and pattern analysis
- Always include confidence levels and evidence quality assessment
- Highlight when data is insufficient for reliable analysis
- Distinguish between statistical significance and market significance

Respond ONLY with valid JSON matching the required schema."""

    async def analyze_options_flow(self, evidence: List[Dict], ticker: str, query: str) -> Dict[str, Any]:
        """Analyze options flow patterns using LLM"""
        try:
            prompt = self._build_options_prompt(evidence, ticker, query)
            
            response = await self.llm_manager.get_completion(
                prompt=prompt,
                system_prompt=self.system_prompt,
                max_tokens=2000,
                temperature=0.1
            )
            
            # Parse and validate the response
            analysis = self._parse_and_validate_response(response)
            
            # Calculate confidence based on evidence quality
            analysis['confidence'] = self._calculate_flow_confidence(evidence, analysis)
            
            return self._format_options_analysis(analysis)
            
        except Exception as e:
            logger.error(f"Options flow analysis failed: {e}")
            return self._create_error_response(str(e))
    
    async def generate_flow_prediction(self, volume_data: Dict, sentiment_data: Dict) -> Dict[str, Any]:
        """Generate options flow predictions from volume and sentiment data"""
        try:
            combined_evidence = [
                {"type": "volume_data", "data": volume_data},
                {"type": "sentiment_data", "data": sentiment_data}
            ]
            
            return await self.analyze_options_flow(
                evidence=combined_evidence,
                ticker=volume_data.get('ticker', 'UNKNOWN'),
                query="Predict options flow direction and timing based on volume and sentiment"
            )
            
        except Exception as e:
            logger.error(f"Flow prediction failed: {e}")
            return self._create_error_response(str(e))
    
    def _build_options_prompt(self, evidence_chunks: List[Dict], ticker: str, query: str) -> str:
        """Build prompt for options flow analysis"""
        evidence_text = "\n".join([
            f"Evidence {i+1} ({chunk.get('type', 'unknown')}):\n{chunk.get('content', chunk)}"
            for i, chunk in enumerate(evidence_chunks)
        ])
        
        return f"""
Analyze the following options flow evidence for {ticker}:

QUERY: {query}

EVIDENCE:
{evidence_text}

Provide a comprehensive options flow analysis in JSON format with the following structure:
{{
    "flow_direction": "bullish" | "bearish" | "neutral" | "mixed",
    "unusual_activity": boolean,
    "key_strikes": [array of strike prices with significant activity],
    "volume_analysis": {{
        "call_volume": number,
        "put_volume": number, 
        "put_call_ratio": number,
        "unusual_threshold_exceeded": boolean
    }},
    "volatility_insights": {{
        "skew_direction": "call" | "put" | "neutral",
        "implied_vol_trend": "rising" | "falling" | "stable"
    }},
    "time_sensitivity": "immediate" | "intraday" | "swing" | "positional",
    "evidence_summary": [array of key evidence points],
    "pattern_strength": "strong" | "moderate" | "weak",
    "risk_factors": [array of factors that could invalidate analysis]
}}

Focus on statistical significance and avoid speculation beyond what the data supports.
"""

    def _parse_and_validate_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate LLM response"""
        try:
            # Extract JSON from response
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
                
            analysis = json.loads(response_clean)
            
            # Validate required fields
            required_fields = [
                'flow_direction', 'unusual_activity', 'key_strikes',
                'volume_analysis', 'volatility_insights', 'time_sensitivity'
            ]
            
            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate enum values
            valid_directions = {'bullish', 'bearish', 'neutral', 'mixed'}
            if analysis['flow_direction'] not in valid_directions:
                analysis['flow_direction'] = 'neutral'
                
            valid_sensitivity = {'immediate', 'intraday', 'swing', 'positional'}
            if analysis['time_sensitivity'] not in valid_sensitivity:
                analysis['time_sensitivity'] = 'intraday'
            
            return analysis
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._create_default_analysis()
    
    def _calculate_flow_confidence(self, evidence: List[Dict], analysis: Dict) -> float:
        """Calculate confidence score based on evidence quality and analysis consistency"""
        confidence_factors = []
        
        # Evidence quality factors
        if evidence:
            evidence_score = min(len(evidence) * 0.1, 0.3)  # More evidence = higher confidence
            confidence_factors.append(evidence_score)
        
        # Volume anomaly strength
        if analysis.get('volume_analysis', {}).get('unusual_threshold_exceeded'):
            confidence_factors.append(0.3)
        
        # Pattern strength
        pattern_strength = analysis.get('pattern_strength', 'weak')
        pattern_scores = {'strong': 0.4, 'moderate': 0.2, 'weak': 0.1}
        confidence_factors.append(pattern_scores.get(pattern_strength, 0.1))
        
        # Consistency check - neutral/mixed flows get lower confidence
        if analysis.get('flow_direction') in ['neutral', 'mixed']:
            confidence_factors.append(-0.1)
        
        # Calculate final confidence
        base_confidence = 0.1
        total_confidence = base_confidence + sum(confidence_factors)
        
        return max(0.0, min(1.0, total_confidence))
    
    def _format_options_analysis(self, raw_analysis: Dict) -> Dict[str, Any]:
        """Format and enrich the options analysis response"""
        formatted = raw_analysis.copy()
        
        # Add metadata
        formatted['analysis_type'] = 'options_flow'
        formatted['timestamp'] = datetime.utcnow().isoformat()
        
        # Ensure all required fields are present
        defaults = {
            'evidence_summary': [],
            'pattern_strength': 'weak',
            'risk_factors': [],
            'confidence': 0.1
        }
        
        for key, default_value in defaults.items():
            if key not in formatted:
                formatted[key] = default_value
        
        return formatted
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            'flow_direction': 'neutral',
            'unusual_activity': False,
            'key_strikes': [],
            'volume_analysis': {
                'call_volume': 0,
                'put_volume': 0,
                'put_call_ratio': 1.0,
                'unusual_threshold_exceeded': False
            },
            'volatility_insights': {
                'skew_direction': 'neutral',
                'implied_vol_trend': 'stable'
            },
            'time_sensitivity': 'intraday',
            'evidence_summary': [],
            'pattern_strength': 'weak',
            'risk_factors': ['Analysis failed due to insufficient data'],
            'confidence': 0.0,
            'error': error_msg,
            'analysis_type': 'options_flow',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _create_default_analysis(self) -> Dict[str, Any]:
        """Create default analysis when parsing fails"""
        return {
            'flow_direction': 'neutral',
            'unusual_activity': False,
            'key_strikes': [],
            'volume_analysis': {
                'call_volume': 0,
                'put_volume': 0,
                'put_call_ratio': 1.0,
                'unusual_threshold_exceeded': False
            },
            'volatility_insights': {
                'skew_direction': 'neutral',
                'implied_vol_trend': 'stable'
            },
            'time_sensitivity': 'intraday',
            'evidence_summary': [],
            'pattern_strength': 'weak',
            'risk_factors': ['Unable to parse analysis response'],
            'confidence': 0.0
        }

# TODO: Implement OptionsFlowLLM class
# Include options-specific prompt templates
# Add JSON schema validation for options responses
# Implement confidence scoring based on options metrics
