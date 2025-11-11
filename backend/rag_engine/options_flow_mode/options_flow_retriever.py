"""
Options Flow Evidence Retriever - Vector Database and Options Data Integration

This module handles evidence retrieval specialized for options flow analysis
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
import hashlib
import json

logger = logging.getLogger(__name__)

class OptionsFlowRetriever:
    """Retrieves and analyzes evidence for options flow analysis"""
    
    def __init__(self, vector_store, db_manager):
        self.vector_store = vector_store
        self.db_manager = db_manager
        
        # Options-specific configuration
        self.unusual_volume_multiplier = 2.0
        self.min_volume_threshold = 100
        self.max_options_items = 50
        self.lookback_hours = 6
        
        # Strike analysis configuration
        self.strike_clustering_threshold = 0.05  # 5% price clustering
        
    async def retrieve_options_evidence(self, 
                                      ticker: str, 
                                      query: str, 
                                      timeframe: str) -> List[Dict[str, Any]]:
        """
        Retrieve comprehensive options evidence for flow analysis
        """
        try:
            # Search vector database for options-related content
            vector_evidence = await self._get_vector_options_evidence(ticker, query, timeframe)
            
            # Get database options activity
            db_evidence = await self._get_database_options_evidence(ticker, timeframe)
            
            # Combine and rank evidence
            combined_evidence = self._combine_options_evidence(vector_evidence, db_evidence)
            
            return combined_evidence
            
        except Exception as e:
            logger.error(f"Error retrieving options evidence for {ticker}: {str(e)}")
            return []
    
    async def get_unusual_volume_data(self, 
                                    ticker: str, 
                                    strike_range: Tuple[float, float]) -> List[Dict]:
        """
        Get unusual options volume data within strike range
        """
        try:
            # Mock implementation - in real system would query options data tables
            # For now, simulate options volume data based on technical indicators
            
            technical_query = """
            SELECT 
                timestamp,
                value_1 as indicator_value,
                endpoint
            FROM alpha_technical_indicators 
            WHERE ticker = $1 
              AND endpoint IN ('RSI', 'MACD', 'BBANDS')
              AND timestamp >= NOW() - INTERVAL '6 hours'
            ORDER BY timestamp DESC
            LIMIT 20
            """
            
            async with self.db_manager.get_async_connection() as conn:
                results = await conn.fetch(technical_query, ticker)
            
            # Convert technical data to mock options volume data
            volume_data = []
            
            current_price = (strike_range[0] + strike_range[1]) / 2  # Approximate current price
            
            for i, row in enumerate(results):
                # Generate mock strike prices around current price
                strike_offset = (i - 10) * 0.02  # ±2% per step
                strike_price = current_price * (1 + strike_offset)
                
                if strike_range[0] <= strike_price <= strike_range[1]:
                    # Mock volume based on technical indicator values
                    indicator_value = float(row['indicator_value']) if row['indicator_value'] else 50
                    
                    # Simulate call/put volumes
                    base_volume = max(100, int(abs(indicator_value) * 10))
                    volume_ratio = abs(indicator_value) / 50  # Normalized
                    
                    call_volume = int(base_volume * (1 + volume_ratio) if indicator_value > 50 else base_volume)
                    put_volume = int(base_volume * (1 + volume_ratio) if indicator_value < 50 else base_volume)
                    
                    volume_data.append({
                        'strike': round(strike_price, 2),
                        'call_volume': call_volume,
                        'put_volume': put_volume,
                        'total_volume': call_volume + put_volume,
                        'volume_ratio': volume_ratio + 1,  # Ratio vs average
                        'timestamp': row['timestamp'],
                        'unusual': volume_ratio > self.unusual_volume_multiplier,
                        'option_type': 'both'
                    })
            
            return volume_data
            
        except Exception as e:
            logger.error(f"Error getting unusual volume data for {ticker}: {str(e)}")
            return []
    
    async def get_flow_direction_indicators(self, 
                                          ticker: str, 
                                          expiration_dates: List[str]) -> List[Dict]:
        """
        Get flow direction indicators from options activity
        """
        try:
            # Mock implementation based on technical indicators
            # In real system, would analyze actual options flow data
            
            query = """
            SELECT 
                endpoint,
                value_1,
                value_2,
                value_3,
                timestamp
            FROM alpha_technical_indicators 
            WHERE ticker = $1 
              AND endpoint IN ('RSI', 'MACD', 'CCI', 'MOM')
              AND timestamp >= NOW() - INTERVAL '4 hours'
            ORDER BY timestamp DESC
            LIMIT 10
            """
            
            async with self.db_manager.get_async_connection() as conn:
                results = await conn.fetch(query, ticker)
            
            flow_indicators = []
            
            for row in results:
                endpoint = row['endpoint']
                value1 = float(row['value_1']) if row['value_1'] else 50
                value2 = float(row['value_2']) if row['value_2'] else 0
                
                # Convert technical indicators to flow signals
                if endpoint == 'RSI':
                    if value1 > 70:
                        signal = 'bearish'  # Overbought
                        strength = (value1 - 70) / 20
                    elif value1 < 30:
                        signal = 'bullish'  # Oversold
                        strength = (30 - value1) / 20
                    else:
                        signal = 'neutral'
                        strength = 0.5
                
                elif endpoint == 'MACD':
                    if value1 > value2:
                        signal = 'bullish'
                        strength = min((value1 - value2) / 10, 1.0)
                    else:
                        signal = 'bearish'
                        strength = min((value2 - value1) / 10, 1.0)
                
                elif endpoint == 'CCI':
                    if value1 > 100:
                        signal = 'bearish'
                        strength = min((value1 - 100) / 200, 1.0)
                    elif value1 < -100:
                        signal = 'bullish'
                        strength = min((abs(value1) - 100) / 200, 1.0)
                    else:
                        signal = 'neutral'
                        strength = 0.5
                
                else:  # MOM
                    if value1 > 0:
                        signal = 'bullish'
                        strength = min(value1 / 10, 1.0)
                    else:
                        signal = 'bearish'
                        strength = min(abs(value1) / 10, 1.0)
                
                flow_indicators.append({
                    'indicator': endpoint,
                    'signal': signal,
                    'strength': round(strength, 2),
                    'value': value1,
                    'timestamp': row['timestamp'],
                    'interpretation': self._interpret_flow_signal(endpoint, signal, strength)
                })
            
            return flow_indicators
            
        except Exception as e:
            logger.error(f"Error getting flow direction indicators for {ticker}: {str(e)}")
            return []
    
    async def rank_options_relevance(self, evidence_chunks: List[Dict]) -> List[Dict]:
        """
        Rank options evidence by relevance for flow analysis
        """
        if not evidence_chunks:
            return []
        
        scored_chunks = []
        
        for chunk in evidence_chunks:
            relevance_score = self._calculate_options_relevance(chunk)
            chunk['options_relevance_score'] = relevance_score
            scored_chunks.append(chunk)
        
        # Sort by relevance score
        return sorted(scored_chunks, key=lambda x: x['options_relevance_score'], reverse=True)
    
    async def correlate_spot_options_data(self, ticker: str, evidence: List[Dict]) -> Dict[str, Any]:
        """
        Correlate spot price movements with options activity
        """
        try:
            # Get recent spot price data
            price_query = """
            SELECT 
                timestamp,
                close_price,
                volume
            FROM alpha_market_data 
            WHERE ticker = $1 
              AND timestamp >= NOW() - INTERVAL '6 hours'
            ORDER BY timestamp DESC
            LIMIT 50
            """
            
            async with self.db_manager.get_async_connection() as conn:
                price_results = await conn.fetch(price_query, ticker)
            
            if not price_results:
                return {}
            
            # Analyze price movement patterns
            prices = [float(row['close_price']) for row in price_results]
            volumes = [int(row['volume'] or 0) for row in price_results]
            
            if len(prices) < 2:
                return {}
            
            # Calculate spot metrics
            price_change = (prices[0] - prices[-1]) / prices[-1] * 100
            avg_volume = sum(volumes) / len(volumes)
            volume_spike = max(volumes) / avg_volume if avg_volume > 0 else 1
            
            # Determine correlation with options activity
            correlation_strength = self._calculate_spot_options_correlation(
                price_change, volume_spike, evidence
            )
            
            return {
                'spot_price_change': round(price_change, 2),
                'volume_spike_ratio': round(volume_spike, 2),
                'correlation_strength': correlation_strength,
                'analysis_period_hours': self.lookback_hours,
                'data_points': len(price_results)
            }
            
        except Exception as e:
            logger.error(f"Error correlating spot-options data for {ticker}: {str(e)}")
            return {}
    
    def _filter_by_options_metadata(self, 
                                   chunks: List[Dict], 
                                   strike_prices: List[float], 
                                   expirations: List[str]) -> List[Dict]:
        """Filter evidence by options-specific metadata"""
        
        filtered_chunks = []
        
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            
            # Check if content mentions options concepts
            content = chunk.get('content', '').lower()
            options_keywords = ['option', 'call', 'put', 'strike', 'volatility', 'gamma', 'delta']
            
            if any(keyword in content for keyword in options_keywords):
                filtered_chunks.append(chunk)
            
            # Check metadata for options relevance
            elif metadata.get('risk_type') in ['options', 'volatility', 'derivatives']:
                filtered_chunks.append(chunk)
        
        return filtered_chunks
    
    def _calculate_volume_anomaly_score(self, volume_data: List[Dict]) -> float:
        """Calculate volume anomaly score for options activity"""
        
        if not volume_data:
            return 0.0
        
        anomaly_scores = []
        
        for item in volume_data:
            volume_ratio = item.get('volume_ratio', 1.0)
            total_volume = item.get('total_volume', 0)
            
            # Score based on volume ratio and absolute volume
            ratio_score = min((volume_ratio - 1.0) / 2.0, 1.0)  # Normalize to 0-1
            volume_score = min(total_volume / 10000, 1.0)  # Volume significance
            
            combined_score = (ratio_score * 0.7) + (volume_score * 0.3)
            anomaly_scores.append(combined_score)
        
        return round(sum(anomaly_scores) / len(anomaly_scores), 2) if anomaly_scores else 0.0
    
    async def _get_vector_options_evidence(self, ticker: str, query: str, timeframe: str) -> List[Dict]:
        """Get options-related evidence from vector database"""
        
        try:
            # Build options-focused search query
            options_query = f"{ticker} options flow volume unusual activity {query}"
            
            # Define filters for options content
            filter_conditions = {
                "ticker": ticker,
                "risk_type": {"$in": ["options", "volatility", "unusual_activity", "derivatives"]},
                "timestamp": {
                    "$gte": (datetime.utcnow() - timedelta(hours=self.lookback_hours)).isoformat()
                }
            }
            
            if hasattr(self.vector_store, 'collection') and self.vector_store.collection:
                results = self.vector_store.collection.query(
                    query_texts=[options_query],
                    where=filter_conditions,
                    n_results=self.max_options_items
                )
                
                vector_evidence = []
                if results and 'documents' in results:
                    for i, doc in enumerate(results['documents'][0]):
                        metadata = results['metadatas'][0][i] if 'metadatas' in results else {}
                        
                        vector_evidence.append({
                            'type': 'vector_search',
                            'content': doc,
                            'source': metadata.get('source', 'vector_db'),
                            'timestamp': datetime.fromisoformat(metadata.get('timestamp', datetime.utcnow().isoformat())),
                            'relevance_score': 1 - (results['distances'][0][i] if 'distances' in results else 0.3),
                            'risk_type': metadata.get('risk_type', 'options'),
                            'metadata': metadata
                        })
                
                return vector_evidence
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting vector options evidence: {str(e)}")
            return []
    
    async def _get_database_options_evidence(self, ticker: str, timeframe: str) -> List[Dict]:
        """Get options-related evidence from database"""
        
        try:
            # Get technical indicators that might relate to options activity
            query = """
            SELECT 
                endpoint,
                indicator_name,
                value_1,
                value_2,
                timestamp,
                parameters
            FROM alpha_technical_indicators 
            WHERE ticker = $1 
              AND endpoint IN ('RSI', 'BBANDS', 'CCI', 'STOCH')
              AND timestamp >= NOW() - INTERVAL '6 hours'
            ORDER BY timestamp DESC
            LIMIT 20
            """
            
            async with self.db_manager.get_async_connection() as conn:
                results = await conn.fetch(query, ticker)
            
            db_evidence = []
            
            for row in results:
                # Convert technical indicators to options-relevant insights
                evidence_item = {
                    'type': 'technical_indicator',
                    'indicator': row['endpoint'],
                    'value': float(row['value_1']) if row['value_1'] else 0,
                    'secondary_value': float(row['value_2']) if row['value_2'] else 0,
                    'timestamp': row['timestamp'],
                    'options_implication': self._derive_options_implication(row['endpoint'], row['value_1'])
                }
                
                db_evidence.append(evidence_item)
            
            return db_evidence
            
        except Exception as e:
            logger.error(f"Error getting database options evidence: {str(e)}")
            return []
    
    def _combine_options_evidence(self, vector_evidence: List[Dict], db_evidence: List[Dict]) -> List[Dict]:
        """Combine options evidence from multiple sources"""
        
        combined_evidence = []
        
        # Add vector evidence
        for item in vector_evidence:
            combined_evidence.append({
                'type': 'options_research',
                'description': item.get('content', '')[:200] + "..." if len(item.get('content', '')) > 200 else item.get('content', ''),
                'source': item.get('source', 'research'),
                'timestamp': item.get('timestamp'),
                'relevance': item.get('relevance_score', 0.5),
                'category': 'vector_analysis'
            })
        
        # Add database evidence
        for item in db_evidence:
            combined_evidence.append({
                'type': 'technical_analysis',
                'description': f"{item['indicator']}: {item.get('options_implication', 'Technical signal detected')}",
                'source': 'technical_indicators',
                'timestamp': item.get('timestamp'),
                'relevance': 0.6,  # Default relevance for technical indicators
                'category': 'technical_analysis',
                'indicator_value': item.get('value', 0)
            })
        
        # Sort by relevance and timestamp
        combined_evidence.sort(key=lambda x: (x.get('relevance', 0), x.get('timestamp', datetime.min)), reverse=True)
        
        return combined_evidence[:20]  # Return top 20 pieces of evidence
    
    def _calculate_options_relevance(self, chunk: Dict) -> float:
        """Calculate relevance score for options analysis"""
        
        content = chunk.get('content', '').lower()
        metadata = chunk.get('metadata', {})
        
        # Base relevance
        relevance = 0.3
        
        # Boost for options keywords
        options_keywords = {
            'option': 0.3, 'call': 0.25, 'put': 0.25, 'strike': 0.2,
            'volatility': 0.2, 'gamma': 0.15, 'delta': 0.15, 'theta': 0.1,
            'unusual': 0.2, 'volume': 0.15, 'flow': 0.15
        }
        
        for keyword, boost in options_keywords.items():
            if keyword in content:
                relevance += boost
        
        # Boost for metadata indicators
        risk_type = metadata.get('risk_type', '')
        if risk_type in ['options', 'volatility', 'derivatives']:
            relevance += 0.2
        
        # Temporal relevance (newer content gets boost)
        timestamp = chunk.get('timestamp')
        if timestamp:
            age_hours = (datetime.utcnow() - timestamp).total_seconds() / 3600
            if age_hours <= 1:
                relevance += 0.2
            elif age_hours <= 6:
                relevance += 0.1
        
        return min(relevance, 1.0)
    
    def _interpret_flow_signal(self, indicator: str, signal: str, strength: float) -> str:
        """Interpret flow signal from technical indicator"""
        
        if indicator == 'RSI':
            if signal == 'bearish':
                return f"Overbought conditions may drive put buying (strength: {strength:.1f})"
            elif signal == 'bullish':
                return f"Oversold conditions may drive call buying (strength: {strength:.1f})"
            else:
                return "Neutral momentum, mixed options flow expected"
        
        elif indicator == 'MACD':
            if signal == 'bullish':
                return f"Positive momentum may increase call activity (strength: {strength:.1f})"
            else:
                return f"Negative momentum may increase put activity (strength: {strength:.1f})"
        
        elif indicator == 'CCI':
            if signal == 'bearish':
                return f"Extreme overbought, protective put buying likely (strength: {strength:.1f})"
            elif signal == 'bullish':
                return f"Extreme oversold, speculative call buying likely (strength: {strength:.1f})"
            else:
                return "Normal range, balanced options flow expected"
        
        else:  # MOM
            if signal == 'bullish':
                return f"Upward momentum supports call flow (strength: {strength:.1f})"
            else:
                return f"Downward momentum supports put flow (strength: {strength:.1f})"
    
    def _derive_options_implication(self, indicator: str, value: Any) -> str:
        """Derive options implications from technical indicator values"""
        
        if not value:
            return "No clear options implication"
        
        val = float(value)
        
        if indicator == 'RSI':
            if val > 70:
                return "High RSI suggests potential put option activity as hedge"
            elif val < 30:
                return "Low RSI may drive speculative call option purchases"
            else:
                return "Moderate RSI indicates balanced options interest"
        
        elif indicator == 'BBANDS':
            # Assuming value is distance from middle band
            if abs(val) > 2:
                return "Price near Bollinger Band extremes may trigger options hedging"
            else:
                return "Price in normal range, typical options flow expected"
        
        elif indicator == 'CCI':
            if val > 100:
                return "Extreme CCI reading may increase protective put demand"
            elif val < -100:
                return "Oversold CCI may increase speculative call interest"
            else:
                return "CCI in normal range, balanced options sentiment"
        
        else:
            return f"Technical signal may influence options positioning"
    
    def _calculate_spot_options_correlation(self, 
                                          price_change: float, 
                                          volume_spike: float, 
                                          evidence: List[Dict]) -> float:
        """Calculate correlation between spot and options activity"""
        
        # Base correlation from price movement
        price_correlation = min(abs(price_change) / 5.0, 1.0)  # Normalize to 0-1
        
        # Volume correlation
        volume_correlation = min((volume_spike - 1.0) / 2.0, 1.0) if volume_spike > 1 else 0
        
        # Evidence correlation (number of options-related signals)
        evidence_correlation = min(len(evidence) / 10.0, 1.0)
        
        # Combined correlation
        total_correlation = (price_correlation * 0.5) + (volume_correlation * 0.3) + (evidence_correlation * 0.2)
        
        return round(total_correlation, 2)
