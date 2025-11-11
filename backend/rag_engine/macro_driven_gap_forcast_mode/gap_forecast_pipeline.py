"""
Gap Forecast Pipeline - Main Orchestrator for Macro Gap Prediction

Orchestrates the MACRO GAP FORECASTING RAG process:
Query → Macro Event Detection → Historical Pattern Analysis → Gap Prediction Response
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

from ..base.base_pipeline import BasePipeline
from .gap_forecast_retriever import GapForecastRetriever
from .gap_forecast_llm import GapForecastLLM
from .gap_forecast_cache import GapForecastCacheManager

logger = logging.getLogger(__name__)


class GapForecastPipeline(BasePipeline):
    """
    Main pipeline for macro-driven gap prediction analysis.
    
    Handles gap prediction queries with macro event context, detects and classifies
    macro events, analyzes historical gap patterns, and provides predictions with
    confidence metrics and rationale.
    """
    
    def __init__(self, vector_store, db_manager, llm_manager, cache_manager=None):
        """
        Initialize the Gap Forecast Pipeline.
        
        Args:
            vector_store: ChromaDB or similar vector storage instance
            db_manager: Database manager for historical data
            llm_manager: LLM manager for generating predictions
            cache_manager: Optional cache manager for performance optimization
        """
        super().__init__(vector_store, db_manager, llm_manager, cache_manager)
        
        self.retriever = GapForecastRetriever(vector_store, db_manager)
        self.llm = GapForecastLLM(llm_manager)
        self.cache = cache_manager or GapForecastCacheManager()
        
        # Gap prediction configuration
        self.supported_events = [
            'fomc', 'fed_rate', 'rbi_rate', 'ecb_rate', 'boj_rate',
            'gdp', 'inflation', 'employment', 'earnings',
            'regulatory', 'geopolitical', 'monetary_policy'
        ]
        
        self.confidence_thresholds = {
            'high': 0.75,
            'medium': 0.60,
            'low': 0.45
        }
        
        logger.info("GapForecastPipeline initialized successfully")

    async def process_gap_query(
        self, 
        query: str, 
        asset: str, 
        macro_event_context: Optional[Dict[str, Any]] = None,
        timeframe: str = "next_session"
    ) -> Dict[str, Any]:
        """
        Main method to process gap prediction queries.
        
        Args:
            query: User query about gap prediction
            asset: Asset symbol/identifier
            macro_event_context: Optional context about macro events
            timeframe: Prediction timeframe
            
        Returns:
            Complete gap prediction analysis
        """
        try:
            # Validate input
            if not self._validate_gap_query(query, asset):
                raise ValueError("Invalid gap prediction query or asset")
            
            # Check cache first
            cache_key = f"gap_forecast:{asset}:{hash(query)}:{timeframe}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached gap prediction for {asset}")
                return cached_result
            
            # Step 1: Detect relevant macro events
            logger.info(f"Detecting macro events for gap prediction: {asset}")
            macro_events = await self.detect_relevant_macro_events(
                asset, timeframe, macro_event_context
            )
            
            # Step 2: Analyze historical gap patterns
            logger.info(f"Analyzing historical gap patterns for {asset}")
            historical_patterns = await self.analyze_historical_gap_patterns(
                asset, macro_events
            )
            
            # Step 3: Generate gap prediction
            logger.info(f"Generating gap prediction for {asset}")
            prediction_result = await self.predict_gap_direction(
                macro_events, historical_patterns, asset
            )
            
            # Step 4: Format final response
            formatted_response = await self.format_gap_prediction(
                prediction_result, asset, timeframe
            )
            
            # Cache the result
            await self.cache.set(cache_key, formatted_response, ttl=1800)  # 30 minutes
            
            logger.info(f"Gap prediction completed for {asset}")
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error in gap forecast pipeline: {str(e)}")
            return self._create_error_response(str(e), asset)

    async def detect_relevant_macro_events(
        self, 
        asset: str, 
        timeframe: str,
        event_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect and classify macro events relevant for gap prediction.
        
        Args:
            asset: Asset to analyze
            timeframe: Analysis timeframe
            event_context: Optional event context
            
        Returns:
            Detected macro events with classifications
        """
        try:
            # Get upcoming macro events
            upcoming_events = await self.retriever.get_upcoming_macro_events(
                asset, timeframe
            )
            
            # Get recent macro announcements
            recent_events = await self.retriever.get_recent_macro_events(
                asset, days_back=5
            )
            
            # Classify event types and impact
            classified_events = []
            for event in upcoming_events + recent_events:
                event_type = self._classify_macro_event_type(event.get('description', ''))
                impact_score = await self._calculate_event_impact_score(event, asset)
                
                classified_events.append({
                    'event': event,
                    'type': event_type,
                    'impact_score': impact_score,
                    'timing': event.get('datetime'),
                    'description': event.get('description', '')
                })
            
            # Sort by impact score
            classified_events.sort(key=lambda x: x['impact_score'], reverse=True)
            
            return {
                'primary_events': classified_events[:3],  # Top 3 most impactful
                'all_events': classified_events,
                'event_count': len(classified_events),
                'highest_impact_score': classified_events[0]['impact_score'] if classified_events else 0
            }
            
        except Exception as e:
            logger.error(f"Error detecting macro events: {str(e)}")
            return {'primary_events': [], 'all_events': [], 'event_count': 0, 'highest_impact_score': 0}

    async def analyze_historical_gap_patterns(
        self, 
        asset: str, 
        macro_events: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze historical gap patterns after similar macro events.
        
        Args:
            asset: Asset to analyze
            macro_events: Detected macro events
            
        Returns:
            Historical gap pattern analysis
        """
        try:
            patterns = {}
            
            for event_data in macro_events.get('primary_events', []):
                event_type = event_data['type']
                
                # Get historical gaps after similar events
                historical_gaps = await self.retriever.get_historical_gaps(
                    asset, event_type, lookback_days=730  # 2 years
                )
                
                if historical_gaps:
                    # Calculate statistics
                    gap_directions = [gap['direction'] for gap in historical_gaps]
                    gap_magnitudes = [abs(gap['magnitude']) for gap in historical_gaps]
                    
                    gap_up_count = sum(1 for d in gap_directions if d == 'up')
                    gap_down_count = sum(1 for d in gap_directions if d == 'down')
                    total_count = len(gap_directions)
                    
                    patterns[event_type] = {
                        'total_occurrences': total_count,
                        'gap_up_count': gap_up_count,
                        'gap_down_count': gap_down_count,
                        'gap_up_probability': gap_up_count / total_count if total_count > 0 else 0,
                        'average_magnitude': sum(gap_magnitudes) / len(gap_magnitudes) if gap_magnitudes else 0,
                        'max_magnitude': max(gap_magnitudes) if gap_magnitudes else 0,
                        'sample_events': historical_gaps[:5]  # Keep top 5 for reference
                    }
            
            # Calculate overall pattern strength
            pattern_strength = self._calculate_pattern_strength(patterns)
            
            return {
                'patterns': patterns,
                'pattern_strength': pattern_strength,
                'analysis_confidence': self._calculate_analysis_confidence(patterns),
                'dominant_direction': self._determine_dominant_direction(patterns)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing historical patterns: {str(e)}")
            return {'patterns': {}, 'pattern_strength': 0, 'analysis_confidence': 0, 'dominant_direction': 'neutral'}

    async def predict_gap_direction(
        self, 
        macro_context: Dict[str, Any], 
        historical_data: Dict[str, Any],
        asset: str
    ) -> Dict[str, Any]:
        """
        Predict gap direction and magnitude based on macro context and historical patterns.
        
        Args:
            macro_context: Macro event context
            historical_data: Historical gap pattern data
            asset: Asset being analyzed
            
        Returns:
            Gap prediction with confidence metrics
        """
        try:
            # Use LLM to generate prediction
            prediction_data = await self.llm.generate_gap_prediction(
                macro_context, historical_data, asset
            )
            
            # Calculate confidence based on pattern strength and event clarity
            event_clarity = self._calculate_event_clarity(macro_context)
            pattern_strength = historical_data.get('pattern_strength', 0)
            
            confidence = self._calculate_prediction_confidence(pattern_strength, event_clarity)
            
            # Determine gap magnitude range
            magnitude_range = self._calculate_magnitude_range(
                historical_data, macro_context, confidence
            )
            
            return {
                'direction': prediction_data.get('direction', 'neutral'),
                'probability': prediction_data.get('probability', 0.5),
                'magnitude_range': magnitude_range,
                'confidence': confidence,
                'reasoning': prediction_data.get('reasoning', ''),
                'macro_catalyst': self._extract_primary_catalyst(macro_context),
                'risk_factors': prediction_data.get('risk_factors', [])
            }
            
        except Exception as e:
            logger.error(f"Error generating gap prediction: {str(e)}")
            return {
                'direction': 'neutral',
                'probability': 0.5,
                'magnitude_range': '0% to 0.5%',
                'confidence': 0.3,
                'reasoning': f'Error in prediction: {str(e)}',
                'macro_catalyst': {},
                'risk_factors': ['Prediction error occurred']
            }

    async def format_gap_prediction(
        self, 
        prediction_result: Dict[str, Any],
        asset: str,
        timeframe: str
    ) -> Dict[str, Any]:
        """
        Format the final gap prediction response.
        
        Args:
            prediction_result: Raw prediction data
            asset: Asset being analyzed
            timeframe: Prediction timeframe
            
        Returns:
            Formatted gap prediction response
        """
        try:
            confidence_level = self._get_confidence_level(prediction_result['confidence'])
            
            return {
                'status': 'success',
                'asset': asset,
                'timestamp': datetime.now().isoformat(),
                'gap_prediction': {
                    'direction': prediction_result['direction'],
                    'probability': prediction_result['probability'],
                    'expected_magnitude': prediction_result['magnitude_range'],
                    'confidence': prediction_result['confidence'],
                    'confidence_level': confidence_level
                },
                'macro_catalyst': prediction_result['macro_catalyst'],
                'historical_basis': {
                    'pattern_strength': prediction_result.get('pattern_strength', 'medium'),
                    'sample_size': prediction_result.get('sample_size', 'sufficient'),
                    'reliability': confidence_level
                },
                'analysis': {
                    'reasoning': prediction_result['reasoning'],
                    'risk_factors': prediction_result['risk_factors'],
                    'timeline': timeframe,
                    'next_update': (datetime.now() + timedelta(hours=6)).isoformat()
                },
                'metadata': {
                    'model_version': '1.0',
                    'analysis_time': datetime.now().isoformat(),
                    'data_freshness': 'real_time'
                }
            }
            
        except Exception as e:
            logger.error(f"Error formatting gap prediction: {str(e)}")
            return self._create_error_response(str(e), asset)

    def _validate_gap_query(self, query: str, asset: str) -> bool:
        """Validate gap prediction query and asset."""
        if not query or not asset:
            return False
        if len(query.strip()) < 5:
            return False
        if len(asset.strip()) < 1:
            return False
        return True

    def _classify_macro_event_type(self, event_description: str) -> str:
        """Classify macro event type based on description."""
        description_lower = event_description.lower()
        
        if any(term in description_lower for term in ['fomc', 'fed', 'federal reserve']):
            return 'fomc'
        elif any(term in description_lower for term in ['rbi', 'reserve bank of india']):
            return 'rbi_rate'
        elif any(term in description_lower for term in ['ecb', 'european central bank']):
            return 'ecb_rate'
        elif any(term in description_lower for term in ['boj', 'bank of japan']):
            return 'boj_rate'
        elif any(term in description_lower for term in ['gdp', 'growth']):
            return 'gdp'
        elif any(term in description_lower for term in ['inflation', 'cpi', 'ppi']):
            return 'inflation'
        elif any(term in description_lower for term in ['employment', 'jobs', 'unemployment']):
            return 'employment'
        elif any(term in description_lower for term in ['earnings', 'quarterly']):
            return 'earnings'
        elif any(term in description_lower for term in ['regulatory', 'regulation']):
            return 'regulatory'
        elif any(term in description_lower for term in ['geopolitical', 'war', 'conflict']):
            return 'geopolitical'
        else:
            return 'other'

    async def _calculate_event_impact_score(self, event: Dict[str, Any], asset: str) -> float:
        """Calculate impact score for a macro event."""
        # Base score based on event type
        event_type = self._classify_macro_event_type(event.get('description', ''))
        
        base_scores = {
            'fomc': 0.9,
            'fed_rate': 0.9,
            'rbi_rate': 0.7,
            'ecb_rate': 0.6,
            'boj_rate': 0.6,
            'gdp': 0.8,
            'inflation': 0.7,
            'employment': 0.6,
            'earnings': 0.5,
            'regulatory': 0.4,
            'geopolitical': 0.8,
            'other': 0.3
        }
        
        base_score = base_scores.get(event_type, 0.3)
        
        # Adjust based on asset type (US stocks more sensitive to US events)
        if asset.startswith('US') or len(asset) <= 4:  # US symbols typically shorter
            if event_type in ['fomc', 'fed_rate', 'gdp', 'employment', 'inflation']:
                base_score *= 1.2
        
        return min(base_score, 1.0)

    def _calculate_pattern_strength(self, patterns: Dict[str, Any]) -> float:
        """Calculate overall pattern strength from historical data."""
        if not patterns:
            return 0.0
        
        total_strength = 0
        valid_patterns = 0
        
        for event_type, pattern_data in patterns.items():
            total_occurrences = pattern_data.get('total_occurrences', 0)
            if total_occurrences >= 3:  # Minimum sample size
                # Higher strength for more occurrences and clearer directional bias
                directional_bias = max(
                    pattern_data.get('gap_up_probability', 0.5),
                    1 - pattern_data.get('gap_up_probability', 0.5)
                )
                occurrence_factor = min(total_occurrences / 20, 1.0)  # Cap at 20 occurrences
                strength = directional_bias * occurrence_factor
                total_strength += strength
                valid_patterns += 1
        
        return total_strength / valid_patterns if valid_patterns > 0 else 0.0

    def _calculate_analysis_confidence(self, patterns: Dict[str, Any]) -> float:
        """Calculate confidence in the pattern analysis."""
        if not patterns:
            return 0.2
        
        total_samples = sum(p.get('total_occurrences', 0) for p in patterns.values())
        pattern_consistency = self._calculate_pattern_strength(patterns)
        
        # More samples and consistent patterns = higher confidence
        sample_factor = min(total_samples / 30, 1.0)  # Cap at 30 total samples
        
        return (sample_factor * 0.6 + pattern_consistency * 0.4)

    def _determine_dominant_direction(self, patterns: Dict[str, Any]) -> str:
        """Determine the dominant gap direction from patterns."""
        if not patterns:
            return 'neutral'
        
        total_up = sum(p.get('gap_up_count', 0) for p in patterns.values())
        total_down = sum(p.get('gap_down_count', 0) for p in patterns.values())
        total = total_up + total_down
        
        if total == 0:
            return 'neutral'
        
        up_ratio = total_up / total
        if up_ratio > 0.65:
            return 'gap_up'
        elif up_ratio < 0.35:
            return 'gap_down'
        else:
            return 'neutral'

    def _calculate_event_clarity(self, macro_context: Dict[str, Any]) -> float:
        """Calculate how clear/unambiguous the macro events are."""
        if not macro_context.get('primary_events'):
            return 0.3
        
        primary_event = macro_context['primary_events'][0]
        impact_score = primary_event.get('impact_score', 0.5)
        
        # Higher impact events are typically clearer
        return min(impact_score * 1.2, 1.0)

    def _calculate_prediction_confidence(self, pattern_strength: float, event_clarity: float) -> float:
        """Calculate overall prediction confidence."""
        return (pattern_strength * 0.6 + event_clarity * 0.4)

    def _calculate_magnitude_range(
        self, 
        historical_data: Dict[str, Any], 
        macro_context: Dict[str, Any],
        confidence: float
    ) -> str:
        """Calculate expected gap magnitude range."""
        patterns = historical_data.get('patterns', {})
        
        if not patterns:
            return "0% to 1%"
        
        # Get average magnitude from patterns
        avg_magnitudes = [p.get('average_magnitude', 0) for p in patterns.values()]
        overall_avg = sum(avg_magnitudes) / len(avg_magnitudes) if avg_magnitudes else 0.5
        
        # Adjust based on confidence
        confidence_multiplier = 0.5 + (confidence * 1.0)  # 0.5 to 1.5 range
        adjusted_magnitude = overall_avg * confidence_multiplier
        
        # Create range
        lower = max(0, adjusted_magnitude * 0.7)
        upper = adjusted_magnitude * 1.3
        
        return f"{lower:.1f}% to {upper:.1f}%"

    def _extract_primary_catalyst(self, macro_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the primary macro catalyst."""
        primary_events = macro_context.get('primary_events', [])
        if not primary_events:
            return {}
        
        primary_event = primary_events[0]
        return {
            'event_type': primary_event.get('type', 'unknown'),
            'description': primary_event.get('description', ''),
            'impact_score': primary_event.get('impact_score', 0),
            'timing': primary_event.get('timing', '')
        }

    def _get_confidence_level(self, confidence: float) -> str:
        """Convert numeric confidence to level."""
        if confidence >= self.confidence_thresholds['high']:
            return 'high'
        elif confidence >= self.confidence_thresholds['medium']:
            return 'medium'
        else:
            return 'low'

    def _create_error_response(self, error_message: str, asset: str) -> Dict[str, Any]:
        """Create error response format."""
        return {
            'status': 'error',
            'asset': asset,
            'timestamp': datetime.now().isoformat(),
            'error': error_message,
            'gap_prediction': {
                'direction': 'neutral',
                'probability': 0.5,
                'expected_magnitude': '0% to 0.5%',
                'confidence': 0.2,
                'confidence_level': 'low'
            }
        }

# TODO: Implement GapForecastPipeline class
# Follow the same async pattern as RiskAssessmentPipeline
# Include macro event classification and historical pattern matching
# Add gap prediction algorithms with confidence scoring
