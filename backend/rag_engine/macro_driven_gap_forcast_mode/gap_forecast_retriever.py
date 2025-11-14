"""
Gap Forecast Evidence Retriever - Macro Events and Historical Gap Analysis

This module handles evidence retrieval specialized for gap forecasting based on macro events
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
import hashlib
import json

logger = logging.getLogger(__name__)

class GapForecastRetriever:
    """Retrieves and analyzes evidence for macro-driven gap forecasting"""
    
    def __init__(self, vector_store, db_manager):
        self.vector_store = vector_store
        self.db_manager = db_manager
        
        # Gap-specific configuration
        self.min_gap_threshold = 0.5  # 0.5% minimum gap
        self.max_events_items = 30
        self.max_historical_gaps = 100
        self.lookback_days = 365
        
        # Event classification
        self.macro_event_types = {
            'monetary': ['fomc', 'fed', 'rbi', 'ecb', 'boj'],
            'regulatory': ['sec', 'cftc', 'finra'],
            'economic': ['cpi', 'nfp', 'gdp', 'unemployment'],
            'geopolitical': ['election', 'war', 'trade', 'sanctions']
        }
        
    async def retrieve_gap_evidence(self, 
                                  asset: str, 
                                  query: str, 
                                  prediction_horizon: int = 24) -> Dict[str, Any]:
        """
        Retrieve comprehensive evidence for gap prediction
        
        Args:
            asset: Asset symbol (e.g., 'NVDA', 'BTC', 'SPY')
            query: User query about gap prediction
            prediction_horizon: Hours ahead to predict
            
        Returns:
            Dict containing macro events, historical gaps, and patterns
        """
        try:
            # Get upcoming macro events
            upcoming_events = await self.get_macro_announcements(
                event_types=['fomc', 'rbi', 'regulatory'],
                time_window=prediction_horizon
            )
            
            # Get historical gap patterns
            historical_gaps = await self.get_historical_gaps(
                asset=asset,
                event_type='macro',
                lookback_period=self.lookback_days
            )
            
            # Get vector database evidence
            vector_evidence = await self._search_macro_context(asset, query)
            
            # Correlate gaps with events
            event_correlations = await self.correlate_gaps_with_events(
                historical_gaps, upcoming_events
            )
            
            return {
                'upcoming_events': upcoming_events,
                'historical_gaps': historical_gaps,
                'vector_evidence': vector_evidence,
                'event_correlations': event_correlations,
                'search_metadata': {
                    'asset': asset,
                    'prediction_horizon': prediction_horizon,
                    'retrieved_at': datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Gap evidence retrieval failed: {e}")
            return {
                'upcoming_events': [],
                'historical_gaps': [],
                'vector_evidence': [],
                'event_correlations': {},
                'error': str(e)
            }
    
    async def get_macro_announcements(self, 
                                    event_types: List[str], 
                                    time_window: int) -> List[Dict[str, Any]]:
        """
        Get upcoming macro events from database
        """
        try:
            # Calculate time range
            start_time = datetime.now(timezone.utc)
            end_time = start_time + timedelta(hours=time_window)
            
            # Query for upcoming events
            query = """
            SELECT 
                event_date,
                event_type,
                description,
                expected_impact,
                asset_relevance,
                announcement_time,
                previous_value,
                forecast_value,
                actual_value
            FROM macro_events 
            WHERE event_date BETWEEN $1 AND $2
            AND event_type = ANY($3)
            ORDER BY event_date ASC, expected_impact DESC
            LIMIT 30
            """
            
            result = await self.db_manager.async_execute_query(
                query, (start_time, end_time, event_types)
            )
            
            return [dict(row) for row in result] if result else []
            
        except Exception as e:
            logger.error(f"Macro announcements retrieval failed: {e}")
            return []
    
    async def get_historical_gaps(self, 
                                asset: str, 
                                event_type: str, 
                                lookback_period: int) -> List[Dict[str, Any]]:
        """
        Get historical gap data for pattern analysis
        """
        try:
            # Calculate lookback date
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=lookback_period)
            
            # Query for historical gaps
            query = """
            SELECT 
                gap_date,
                open_price,
                prev_close,
                gap_size_pct,
                gap_direction,
                volume_ratio,
                catalyst_identified,
                event_correlation,
                market_session
            FROM historical_gaps 
            WHERE ticker = $1 
            AND gap_date >= $2
            AND ABS(gap_size_pct) >= $3
            ORDER BY gap_date DESC
            LIMIT 100
            """
            
            result = await self.db_manager.async_execute_query(
                query, (asset, start_date, self.min_gap_threshold)
            )
            
            return [dict(row) for row in result] if result else []
            
        except Exception as e:
            logger.error(f"Historical gaps retrieval failed: {e}")
            return []
    
    async def analyze_fed_communication(self, 
                                      fomc_statements: List[Dict], 
                                      fed_speeches: List[Dict]) -> Dict[str, Any]:
        """
        Analyze Fed communications for sentiment and policy direction
        """
        try:
            fed_sentiment = []
            
            # Analyze FOMC statements
            for statement in fomc_statements:
                sentiment = self._classify_macro_event_sentiment(
                    statement.get('text', '')
                )
                fed_sentiment.append({
                    'date': statement.get('date'),
                    'type': 'fomc_statement',
                    'sentiment': sentiment,
                    'key_phrases': self._extract_key_phrases(statement.get('text', ''))
                })
            
            # Analyze Fed speeches
            for speech in fed_speeches:
                sentiment = self._classify_macro_event_sentiment(
                    speech.get('text', '')
                )
                fed_sentiment.append({
                    'date': speech.get('date'),
                    'type': 'fed_speech',
                    'speaker': speech.get('speaker'),
                    'sentiment': sentiment,
                    'key_phrases': self._extract_key_phrases(speech.get('text', ''))
                })
            
            # Aggregate sentiment trend
            overall_sentiment = self._calculate_overall_sentiment(fed_sentiment)
            
            return {
                'individual_sentiments': fed_sentiment,
                'overall_sentiment': overall_sentiment,
                'policy_direction': self._determine_policy_direction(fed_sentiment)
            }
            
        except Exception as e:
            logger.error(f"Fed communication analysis failed: {e}")
            return {}
    
    async def analyze_rbi_policy_impact(self, 
                                      rbi_decisions: List[Dict], 
                                      indian_markets: List[str]) -> Dict[str, Any]:
        """
        Analyze RBI policy decisions and their impact on Indian markets
        """
        try:
            rbi_impact = {
                'policy_changes': [],
                'market_reactions': {},
                'spillover_effects': {}
            }
            
            for decision in rbi_decisions:
                # Analyze policy change
                policy_analysis = {
                    'date': decision.get('date'),
                    'repo_rate_change': decision.get('repo_rate_change', 0),
                    'stance': decision.get('policy_stance'),
                    'rationale': decision.get('rationale', ''),
                    'expected_impact': self._assess_rbi_impact(decision)
                }
                rbi_impact['policy_changes'].append(policy_analysis)
                
                # Get market reactions for Indian assets
                for market in indian_markets:
                    decision_date = decision.get('date')
                    if decision_date:
                        reaction = await self._get_market_reaction_to_rbi(
                            decision_date, market
                        )
                        rbi_impact['market_reactions'][market] = reaction
            
            return rbi_impact
            
        except Exception as e:
            logger.error(f"RBI policy analysis failed: {e}")
            return {}
    
    async def get_regulatory_announcements(self, 
                                         agencies: List[str], 
                                         sectors: List[str]) -> List[Dict[str, Any]]:
        """
        Get recent regulatory announcements from specified agencies
        """
        try:
            # Query for regulatory announcements
            query = """
            SELECT 
                announcement_date,
                agency,
                sector_affected,
                announcement_type,
                description,
                expected_impact,
                implementation_date
            FROM regulatory_announcements 
            WHERE agency = ANY($1)
            AND sector_affected = ANY($2)
            AND announcement_date >= NOW() - INTERVAL '30 days'
            ORDER BY announcement_date DESC, expected_impact DESC
            LIMIT 20
            """
            
            result = await self.db_manager.async_execute_query(
                query, (agencies, sectors)
            )
            
            return [dict(row) for row in result] if result else []
            
        except Exception as e:
            logger.error(f"Regulatory announcements retrieval failed: {e}")
            return []
    
    async def correlate_gaps_with_events(self, 
                                       gap_data: List[Dict], 
                                       event_data: List[Dict]) -> Dict[str, Any]:
        """
        Find correlations between historical gaps and macro events
        """
        try:
            correlations = {
                'event_gap_pairs': [],
                'correlation_strength': {},
                'pattern_analysis': {}
            }
            
            # Match gaps with events within time window
            for gap in gap_data:
                gap_date = gap.get('gap_date')
                if not gap_date:
                    continue
                
                # Find events within 24 hours before gap
                matching_events = []
                for event in event_data:
                    event_date = event.get('event_date')
                    if not event_date:
                        continue
                    
                    time_diff = (gap_date - event_date).total_seconds() / 3600
                    if 0 <= time_diff <= 24:  # Event happened 0-24 hours before gap
                        matching_events.append({
                            'event': event,
                            'time_to_gap_hours': time_diff,
                            'gap_magnitude': gap.get('gap_size_pct', 0)
                        })
                
                if matching_events:
                    correlations['event_gap_pairs'].append({
                        'gap': gap,
                        'events': matching_events
                    })
            
            # Calculate correlation strengths by event type
            for event_type in self.macro_event_types.get('monetary', []):
                strength = self._calculate_correlation_strength(
                    correlations['event_gap_pairs'], event_type
                )
                correlations['correlation_strength'][event_type] = strength
            
            return correlations
            
        except Exception as e:
            logger.error(f"Gap-event correlation failed: {e}")
            return {}
    
    async def _search_macro_context(self, asset: str, query: str) -> List[Dict[str, Any]]:
        """
        Search vector database for macro-related context
        """
        try:
            # Search for macro-related content
            search_results = await self.vector_store.semantic_search(
                query=f"{query} {asset} macro economic policy",
                filters={
                    "risk_type": {"$in": ["macro", "regulatory", "monetary"]},
                    "ticker": asset
                },
                limit=15
            )
            
            return search_results
            
        except Exception as e:
            logger.error(f"Macro context search failed: {e}")
            return []
    
    def _classify_macro_event_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Classify sentiment of macro event text
        """
        hawkish_keywords = [
            'inflation', 'rate hike', 'tightening', 'aggressive',
            'concerns', 'restrictive', 'combat'
        ]
        dovish_keywords = [
            'accommodative', 'stimulus', 'support', 'dovish',
            'cut rates', 'easing', 'growth'
        ]
        
        text_lower = text.lower()
        hawkish_score = sum(1 for keyword in hawkish_keywords if keyword in text_lower)
        dovish_score = sum(1 for keyword in dovish_keywords if keyword in text_lower)
        
        if hawkish_score > dovish_score:
            sentiment = 'hawkish'
            confidence = min(hawkish_score / (hawkish_score + dovish_score + 1), 0.9)
        elif dovish_score > hawkish_score:
            sentiment = 'dovish'
            confidence = min(dovish_score / (hawkish_score + dovish_score + 1), 0.9)
        else:
            sentiment = 'neutral'
            confidence = 0.5
            
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'hawkish_signals': hawkish_score,
            'dovish_signals': dovish_score
        }
    
    def _calculate_event_market_impact(self, 
                                     event_magnitude: float, 
                                     asset_sensitivity: float) -> float:
        """
        Calculate expected market impact from event characteristics
        """
        # Simple impact calculation (can be made more sophisticated)
        base_impact = event_magnitude * asset_sensitivity
        
        # Apply decay based on time since event
        time_decay = 0.8  # Assume 20% decay per day
        
        return base_impact * time_decay
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """
        Extract key phrases from macro event text
        """
        key_phrases = []
        
        # Simple keyword extraction (can be enhanced with NLP)
        important_terms = [
            'interest rate', 'inflation target', 'employment',
            'economic growth', 'monetary policy', 'financial stability'
        ]
        
        text_lower = text.lower()
        for term in important_terms:
            if term in text_lower:
                key_phrases.append(term)
        
        return key_phrases
    
    def _calculate_overall_sentiment(self, sentiment_list: List[Dict]) -> Dict[str, Any]:
        """
        Calculate overall sentiment from individual sentiments
        """
        if not sentiment_list:
            return {'sentiment': 'neutral', 'confidence': 0.0}
        
        sentiments = [s.get('sentiment') for s in sentiment_list]
        hawkish_count = sentiments.count('hawkish')
        dovish_count = sentiments.count('dovish')
        neutral_count = sentiments.count('neutral')
        
        total = len(sentiments)
        if hawkish_count > dovish_count:
            overall = 'hawkish'
            confidence = hawkish_count / total
        elif dovish_count > hawkish_count:
            overall = 'dovish' 
            confidence = dovish_count / total
        else:
            overall = 'neutral'
            confidence = neutral_count / total
            
        return {
            'sentiment': overall,
            'confidence': confidence,
            'distribution': {
                'hawkish': hawkish_count,
                'dovish': dovish_count,
                'neutral': neutral_count
            }
        }
    
    def _determine_policy_direction(self, sentiment_list: List[Dict]) -> str:
        """
        Determine overall policy direction from sentiments
        """
        overall = self._calculate_overall_sentiment(sentiment_list)
        sentiment = overall.get('sentiment', 'neutral')
        confidence = overall.get('confidence', 0)
        
        if confidence > 0.6:
            if sentiment == 'hawkish':
                return 'tightening'
            elif sentiment == 'dovish':
                return 'easing'
        
        return 'neutral'
    
    def _assess_rbi_impact(self, decision: Dict) -> str:
        """
        Assess expected impact of RBI policy decision
        """
        repo_change = decision.get('repo_rate_change', 0)
        stance = decision.get('policy_stance', 'neutral')
        
        if repo_change > 0:
            return 'hawkish_tightening'
        elif repo_change < 0:
            return 'dovish_easing'
        elif 'accommodative' in stance.lower():
            return 'dovish_hold'
        elif 'neutral' in stance.lower():
            return 'neutral_hold'
        else:
            return 'hawkish_hold'
    
    async def _get_market_reaction_to_rbi(self, decision_date: datetime, market: str) -> Dict:
        """
        Get market reaction data following RBI decision
        """
        try:
            # Query for market data around RBI decision
            start_date = decision_date - timedelta(days=1)
            end_date = decision_date + timedelta(days=3)
            
            query = """
            SELECT 
                timestamp,
                open_price,
                close_price,
                volume
            FROM market_prices 
            WHERE ticker = $1 
            AND timestamp BETWEEN $2 AND $3
            ORDER BY timestamp ASC
            """
            
            result = await self.db_manager.async_execute_query(
                query, (market, start_date, end_date)
            )
            
            if result and len(result) >= 2:
                pre_decision = result[0]
                post_decision = result[-1]
                
                price_change = (
                    (post_decision['close_price'] - pre_decision['close_price']) /
                    pre_decision['close_price'] * 100
                )
                
                return {
                    'price_change_pct': round(price_change, 2),
                    'volume_change': 'data_available',
                    'reaction_strength': 'significant' if abs(price_change) > 2 else 'moderate'
                }
            
            return {'price_change_pct': 0, 'volume_change': 'no_data', 'reaction_strength': 'none'}
            
        except Exception as e:
            logger.error(f"RBI market reaction analysis failed: {e}")
            return {'error': str(e)}
    
    def _calculate_correlation_strength(self, 
                                      event_gap_pairs: List[Dict], 
                                      event_type: str) -> float:
        """
        Calculate correlation strength between events and gaps
        """
        relevant_pairs = []
        
        for pair in event_gap_pairs:
            for event_info in pair.get('events', []):
                if event_info.get('event', {}).get('event_type') == event_type:
                    relevant_pairs.append(event_info.get('gap_magnitude', 0))
        
        if not relevant_pairs:
            return 0.0
        
        # Simple correlation metric (can be enhanced)
        avg_gap_size = sum(abs(gap) for gap in relevant_pairs) / len(relevant_pairs)
        return min(avg_gap_size / 5.0, 1.0)  # Normalize to 0-1
