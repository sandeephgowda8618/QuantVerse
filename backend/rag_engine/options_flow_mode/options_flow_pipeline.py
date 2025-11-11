"""
Options Flow Pipeline - Main Orchestrator for Options Flow Analysis

This pipeline orchestrates the OPTIONS FLOW analysis RAG process:
Query → Options Filter → Retrieve Evidence → Flow Analysis → JSON Response
"""

import asyncio
import json
import hashlib
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
import logging

from ..vector_store import ChromaVectorStore
from ...db.postgres_handler import PostgresHandler
from ..llm_manager import LLMManager
from .options_flow_llm import OptionsFlowLLM
from .options_flow_retriever import OptionsFlowRetriever
from .options_flow_cache import OptionsFlowCacheManager

logger = logging.getLogger(__name__)

class OptionsFlowPipeline:
    """Main orchestrator for OPTIONS FLOW analysis RAG pipeline"""
    
    def __init__(self, 
                 vector_store: ChromaVectorStore,
                 db_manager: PostgresHandler,
                 llm_manager: LLMManager,
                 cache_manager: Optional[OptionsFlowCacheManager] = None):
        """Initialize the options flow analysis pipeline"""
        self.vector_store = vector_store
        self.db_manager = db_manager
        self.llm_manager = llm_manager
        self.cache_manager = cache_manager or OptionsFlowCacheManager()
        
        # Initialize specialized components
        self.flow_llm = OptionsFlowLLM(llm_manager)
        self.flow_retriever = OptionsFlowRetriever(vector_store, db_manager)
        
        # Configuration
        self.unusual_volume_threshold = 2.0  # 2x average volume
        self.min_option_volume = 100  # Minimum volume for analysis
        self.max_analysis_age_hours = 6  # Only analyze recent options activity
        self.confidence_threshold = 0.4  # Minimum confidence to return result
        
        # Strike range configuration (relative to current price)
        self.strike_range_pct = 0.15  # ±15% from current price
        
        logger.info("OptionsFlowPipeline initialized")
    
    async def process_options_query(self, 
                                  query: str, 
                                  ticker: str, 
                                  timeframe: str = "1h",
                                  strike_range: Optional[Tuple[float, float]] = None) -> Dict[str, Any]:
        """
        Main entry point for processing options flow analysis queries
        """
        start_time = time.time()
        
        try:
            # Validate the query
            self._validate_options_query(query, ticker)
            
            # Extract options parameters from query
            options_params = self._extract_options_parameters(query, timeframe)
            
            # Determine strike range if not provided
            if strike_range is None:
                strike_range = await self._determine_strike_range(ticker)
            
            # Check cache first
            cache_key = self._generate_cache_key(ticker, timeframe, strike_range, options_params)
            cached_result = self.cache_manager.get_cached_options_analysis(cache_key)
            if cached_result:
                logger.info(f"Returning cached options analysis for {ticker}")
                return cached_result
            
            # Gather evidence in parallel
            evidence_tasks = [
                self.flow_retriever.get_unusual_volume_data(ticker, strike_range),
                self.flow_retriever.get_flow_direction_indicators(ticker, options_params.get('expiration_dates', [])),
                self.flow_retriever.retrieve_options_evidence(ticker, query, timeframe),
                self._get_current_market_context(ticker)
            ]
            
            volume_data, flow_indicators, options_evidence, market_context = await asyncio.gather(*evidence_tasks)
            
            # Analyze options flow using all gathered data
            flow_analysis = await self.analyze_options_flow({
                'ticker': ticker,
                'query': query,
                'timeframe': timeframe,
                'strike_range': strike_range,
                'volume_data': volume_data,
                'flow_indicators': flow_indicators,
                'options_evidence': options_evidence,
                'market_context': market_context,
                'options_params': options_params
            })
            
            # Format the final response
            analysis_result = await self.format_options_response(flow_analysis)
            
            # Calculate flow confidence
            confidence = self._calculate_flow_confidence(
                volume_data, flow_indicators, len(options_evidence)
            )
            analysis_result['confidence'] = confidence
            
            # Cache the result if confidence is high enough
            if confidence >= self.confidence_threshold:
                self.cache_manager.cache_options_analysis(cache_key, analysis_result)
            
            logger.info(f"Options flow analysis completed for {ticker} in {time.time() - start_time:.2f}s")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error processing options query for {ticker}: {str(e)}")
            return self._format_error_response(str(e), ticker, timeframe)
    
    async def analyze_options_flow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze options flow using LLM with all gathered evidence
        """
        try:
            # Prepare comprehensive context for LLM analysis
            analysis_context = {
                'ticker': context['ticker'],
                'query': context['query'],
                'timeframe': context['timeframe'],
                'volume_analysis': self._analyze_volume_patterns(context['volume_data']),
                'flow_direction': self._determine_flow_direction(context['flow_indicators']),
                'unusual_activity': self._detect_unusual_activity(context['volume_data']),
                'market_context': context['market_context'],
                'evidence_summary': self._summarize_options_evidence(context['options_evidence']),
                'strike_analysis': self._analyze_strike_distribution(context['volume_data'], context['strike_range'])
            }
            
            # Get LLM analysis
            flow_prediction = await self.flow_llm.analyze_options_flow(analysis_context)
            
            return flow_prediction
            
        except Exception as e:
            logger.error(f"Error analyzing options flow: {str(e)}")
            return {
                'flow_direction': 'neutral',
                'unusual_activity': False,
                'confidence': 0.1,
                'error': str(e)
            }
    
    async def format_options_response(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the final options flow analysis response
        """
        return {
            'flow_direction': analysis_result.get('flow_direction', 'neutral'),
            'unusual_activity': analysis_result.get('unusual_activity', False),
            'key_strikes': analysis_result.get('key_strikes', []),
            'volume_analysis': {
                'call_volume': analysis_result.get('volume_analysis', {}).get('call_volume', 0),
                'put_volume': analysis_result.get('volume_analysis', {}).get('put_volume', 0),
                'put_call_ratio': analysis_result.get('volume_analysis', {}).get('put_call_ratio', 1.0),
                'unusual_threshold_exceeded': analysis_result.get('unusual_activity', False)
            },
            'volatility_insights': {
                'skew_direction': analysis_result.get('volatility_insights', {}).get('skew_direction', 'neutral'),
                'implied_vol_trend': analysis_result.get('volatility_insights', {}).get('implied_vol_trend', 'stable')
            },
            'time_sensitivity': analysis_result.get('time_sensitivity', 'intraday'),
            'evidence_summary': analysis_result.get('evidence_summary', []),
            'confidence': analysis_result.get('confidence', 0.5),
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'ticker': analysis_result.get('ticker', 'Unknown')
        }
    
    def _validate_options_query(self, query: str, ticker: str) -> None:
        """Validate options flow query parameters"""
        if not query or len(query.strip()) < 5:
            raise ValueError("Query must be at least 5 characters long")
        
        if not ticker or len(ticker) > 10:
            raise ValueError("Invalid ticker symbol")
        
        # Check if query is options-related
        options_keywords = ['option', 'call', 'put', 'strike', 'volume', 'flow', 'unusual', 'volatility']
        if not any(keyword in query.lower() for keyword in options_keywords):
            logger.warning(f"Query may not be options-related: {query}")
    
    def _extract_options_parameters(self, query: str, timeframe: str) -> Dict[str, Any]:
        """Extract options-specific parameters from query"""
        query_lower = query.lower()
        
        # Extract expiration timeframe
        expiration_dates = []
        if 'weekly' in query_lower or 'week' in query_lower:
            expiration_dates = ['weekly']
        elif 'monthly' in query_lower or 'month' in query_lower:
            expiration_dates = ['monthly']
        elif 'quarterly' in query_lower:
            expiration_dates = ['quarterly']
        else:
            expiration_dates = ['weekly', 'monthly']  # Default to both
        
        # Extract option type preference
        option_type = 'both'
        if 'call' in query_lower and 'put' not in query_lower:
            option_type = 'calls'
        elif 'put' in query_lower and 'call' not in query_lower:
            option_type = 'puts'
        
        # Extract volume threshold if mentioned
        volume_threshold = self.unusual_volume_threshold
        if 'high volume' in query_lower or 'heavy volume' in query_lower:
            volume_threshold = 3.0
        elif 'moderate volume' in query_lower:
            volume_threshold = 1.5
        
        return {
            'timeframe': timeframe,
            'expiration_dates': expiration_dates,
            'option_type': option_type,
            'volume_threshold': volume_threshold,
            'analysis_focus': self._determine_analysis_focus(query_lower)
        }
    
    def _determine_analysis_focus(self, query_lower: str) -> str:
        """Determine the primary focus of the options analysis"""
        if 'gamma' in query_lower or 'dealer' in query_lower:
            return 'gamma_exposure'
        elif 'dark pool' in query_lower or 'block' in query_lower:
            return 'block_trades'
        elif 'skew' in query_lower or 'volatility' in query_lower:
            return 'volatility_skew'
        elif 'flow' in query_lower:
            return 'flow_direction'
        elif 'unusual' in query_lower:
            return 'unusual_activity'
        else:
            return 'general_analysis'
    
    async def _determine_strike_range(self, ticker: str) -> Tuple[float, float]:
        """Determine appropriate strike range based on current price"""
        try:
            # Get current price
            current_price = await self._get_current_price(ticker)
            
            if current_price <= 0:
                return (0, 1000)  # Fallback range
            
            # Calculate ±15% range
            range_pct = self.strike_range_pct
            lower_strike = current_price * (1 - range_pct)
            upper_strike = current_price * (1 + range_pct)
            
            return (lower_strike, upper_strike)
            
        except Exception as e:
            logger.error(f"Error determining strike range for {ticker}: {str(e)}")
            return (0, 1000)  # Fallback range
    
    async def _get_current_price(self, ticker: str) -> float:
        """Get current market price for the ticker"""
        try:
            query = """
            SELECT close_price
            FROM alpha_market_data 
            WHERE ticker = $1 
            ORDER BY timestamp DESC 
            LIMIT 1
            """
            
            async with self.db_manager.get_async_connection() as conn:
                result = await conn.fetchval(query, ticker)
            
            return float(result) if result else 0.0
            
        except Exception as e:
            logger.error(f"Error getting current price for {ticker}: {str(e)}")
            return 0.0
    
    async def _get_current_market_context(self, ticker: str) -> Dict[str, Any]:
        """Get current market context for options analysis"""
        try:
            # Get recent price action and volatility
            query = """
            SELECT 
                close_price,
                volume,
                timestamp
            FROM alpha_market_data 
            WHERE ticker = $1 
              AND timestamp >= NOW() - INTERVAL '24 hours'
            ORDER BY timestamp DESC
            LIMIT 50
            """
            
            async with self.db_manager.get_async_connection() as conn:
                results = await conn.fetch(query, ticker)
            
            if not results:
                return {}
            
            prices = [float(row['close_price']) for row in results]
            volumes = [int(row['volume'] or 0) for row in results]
            
            # Calculate basic metrics
            current_price = prices[0] if prices else 0
            price_change_24h = ((prices[0] - prices[-1]) / prices[-1] * 100) if len(prices) > 1 and prices[-1] > 0 else 0
            avg_volume = sum(volumes) / len(volumes) if volumes else 0
            current_volume = volumes[0] if volumes else 0
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            return {
                'current_price': current_price,
                'price_change_24h': price_change_24h,
                'volume_ratio': volume_ratio,
                'avg_volume_24h': avg_volume,
                'price_volatility': self._calculate_price_volatility(prices)
            }
            
        except Exception as e:
            logger.error(f"Error getting market context for {ticker}: {str(e)}")
            return {}
    
    def _calculate_price_volatility(self, prices: List[float]) -> float:
        """Calculate simple price volatility"""
        if len(prices) < 2:
            return 0.0
        
        # Calculate returns
        returns = []
        for i in range(1, len(prices)):
            if prices[i] > 0:
                ret = (prices[i-1] - prices[i]) / prices[i]
                returns.append(ret)
        
        if not returns:
            return 0.0
        
        # Simple standard deviation
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        volatility = (variance ** 0.5) * 100  # Convert to percentage
        
        return volatility
    
    def _analyze_volume_patterns(self, volume_data: List[Dict]) -> Dict[str, Any]:
        """Analyze volume patterns in options data"""
        if not volume_data:
            return {'call_volume': 0, 'put_volume': 0, 'put_call_ratio': 1.0}
        
        total_call_volume = sum(item.get('call_volume', 0) for item in volume_data)
        total_put_volume = sum(item.get('put_volume', 0) for item in volume_data)
        
        put_call_ratio = total_put_volume / total_call_volume if total_call_volume > 0 else float('inf')
        
        return {
            'call_volume': total_call_volume,
            'put_volume': total_put_volume,
            'put_call_ratio': put_call_ratio,
            'total_volume': total_call_volume + total_put_volume,
            'volume_distribution': self._calculate_volume_distribution(volume_data)
        }
    
    def _calculate_volume_distribution(self, volume_data: List[Dict]) -> Dict[str, float]:
        """Calculate volume distribution across strikes"""
        if not volume_data:
            return {}
        
        strike_volumes = {}
        for item in volume_data:
            strike = item.get('strike', 0)
            volume = item.get('total_volume', 0)
            if strike and volume:
                strike_volumes[str(strike)] = volume
        
        return strike_volumes
    
    def _determine_flow_direction(self, flow_indicators: List[Dict]) -> str:
        """Determine overall flow direction from indicators"""
        if not flow_indicators:
            return 'neutral'
        
        bullish_signals = 0
        bearish_signals = 0
        
        for indicator in flow_indicators:
            signal = indicator.get('signal', 'neutral')
            if signal == 'bullish':
                bullish_signals += 1
            elif signal == 'bearish':
                bearish_signals += 1
        
        if bullish_signals > bearish_signals:
            return 'bullish'
        elif bearish_signals > bullish_signals:
            return 'bearish'
        else:
            return 'neutral'
    
    def _detect_unusual_activity(self, volume_data: List[Dict]) -> bool:
        """Detect if there's unusual options activity"""
        if not volume_data:
            return False
        
        for item in volume_data:
            volume_ratio = item.get('volume_ratio', 1.0)
            if volume_ratio >= self.unusual_volume_threshold:
                return True
        
        return False
    
    def _summarize_options_evidence(self, evidence: List[Dict]) -> List[str]:
        """Summarize options evidence into key points"""
        summary = []
        
        if not evidence:
            return ['No significant options evidence found']
        
        for item in evidence[:5]:  # Top 5 evidence items
            evidence_type = item.get('type', 'unknown')
            description = item.get('description', '')
            
            if evidence_type == 'unusual_volume':
                summary.append(f"Unusual volume detected: {description}")
            elif evidence_type == 'flow_direction':
                summary.append(f"Flow direction: {description}")
            elif evidence_type == 'volatility':
                summary.append(f"Volatility insight: {description}")
            else:
                summary.append(description[:100] + "..." if len(description) > 100 else description)
        
        return summary
    
    def _analyze_strike_distribution(self, volume_data: List[Dict], strike_range: Tuple[float, float]) -> List[str]:
        """Analyze strike distribution for key levels"""
        if not volume_data:
            return []
        
        key_strikes = []
        
        # Sort by volume and get top strikes
        sorted_data = sorted(volume_data, key=lambda x: x.get('total_volume', 0), reverse=True)
        
        for item in sorted_data[:5]:  # Top 5 strikes by volume
            strike = item.get('strike', 0)
            volume = item.get('total_volume', 0)
            
            if strike_range[0] <= strike <= strike_range[1] and volume >= self.min_option_volume:
                key_strikes.append(f"${strike:.2f}")
        
        return key_strikes
    
    def _calculate_flow_confidence(self, 
                                 volume_data: List[Dict], 
                                 flow_indicators: List[Dict],
                                 evidence_count: int) -> float:
        """Calculate confidence in options flow analysis"""
        
        # Base confidence from data availability
        base_confidence = 0.3
        
        # Volume data quality
        if volume_data:
            volume_boost = min(len(volume_data) * 0.05, 0.3)
            unusual_activity = self._detect_unusual_activity(volume_data)
            if unusual_activity:
                volume_boost += 0.2
        else:
            volume_boost = 0
        
        # Flow indicators quality
        if flow_indicators:
            flow_boost = min(len(flow_indicators) * 0.03, 0.2)
        else:
            flow_boost = 0
        
        # Evidence quality
        evidence_boost = min(evidence_count * 0.02, 0.15)
        
        total_confidence = base_confidence + volume_boost + flow_boost + evidence_boost
        
        return round(min(max(total_confidence, 0.1), 0.95), 2)
    
    def _generate_cache_key(self, 
                          ticker: str, 
                          timeframe: str, 
                          strike_range: Tuple[float, float],
                          options_params: Dict) -> str:
        """Generate cache key for options analysis"""
        key_components = [
            ticker.upper(),
            timeframe,
            f"{strike_range[0]:.2f}-{strike_range[1]:.2f}",
            str(options_params.get('volume_threshold', 2.0)),
            options_params.get('option_type', 'both'),
            datetime.utcnow().strftime('%Y%m%d_%H')  # Hour-level caching
        ]
        
        key_string = ':'.join(key_components)
        hash_key = hashlib.md5(key_string.encode()).hexdigest()[:16]
        
        return f"options_flow:{ticker}:{hash_key}"
    
    def _format_error_response(self, error: str, ticker: str, timeframe: str) -> Dict[str, Any]:
        """Format error response for options flow analysis"""
        return {
            'flow_direction': 'unknown',
            'unusual_activity': False,
            'key_strikes': [],
            'volume_analysis': {
                'call_volume': 0,
                'put_volume': 0,
                'put_call_ratio': 1.0,
                'unusual_threshold_exceeded': False
            },
            'volatility_insights': {
                'skew_direction': 'unknown',
                'implied_vol_trend': 'unknown'
            },
            'time_sensitivity': 'unknown',
            'evidence_summary': [f'Error: {error}'],
            'confidence': 0.0,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'ticker': ticker,
            'error': error
        }
