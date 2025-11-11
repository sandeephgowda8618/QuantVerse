"""
Options Flow Cache Manager - Caching for Options Flow Analysis
Specialized caching for options flow results with short TTL due to data volatility.
"""
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class OptionsFlowCacheManager:
    """Cache manager specialized for options flow analysis results"""
    
    def __init__(self, redis_client: Optional[Any] = None):
        """Initialize cache manager. Start with no-cache implementation."""
        self.redis_client = redis_client
        self.cache_enabled = redis_client is not None
        self.default_ttl = 300  # 5 minutes - short due to options volatility
        self.max_ttl = 900  # 15 minutes maximum
        
        # In-memory cache for when Redis is not available
        self._memory_cache = {}
        self._cache_timestamps = {}
        
        logger.info(f"Options flow cache initialized. Redis enabled: {self.cache_enabled}")
    
    def generate_options_cache_key(
        self, 
        ticker: str, 
        timeframe: str,
        strike_range: Optional[str] = None,
        volume_threshold: Optional[int] = None,
        query: Optional[str] = None
    ) -> str:
        """Generate cache key for options flow analysis"""
        
        # Build key components
        components = [
            f"ticker:{ticker.upper()}",
            f"timeframe:{timeframe}",
        ]
        
        if strike_range:
            components.append(f"strikes:{strike_range}")
        
        if volume_threshold:
            components.append(f"vol_thresh:{volume_threshold}")
        
        # Hash the query for consistent key generation
        if query:
            query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
            components.append(f"query:{query_hash}")
        
        # Create final key
        key_string = "|".join(components)
        cache_key = f"options_flow:{hashlib.md5(key_string.encode()).hexdigest()}"
        
        return cache_key
    
    async def cache_options_analysis(
        self, 
        cache_key: str, 
        analysis_result: Dict[str, Any],
        custom_ttl: Optional[int] = None
    ) -> bool:
        """Cache options flow analysis result"""
        
        if not self._should_cache_result(analysis_result):
            return False
        
        ttl = custom_ttl or self._determine_ttl(analysis_result)
        
        try:
            # Prepare data for caching
            cache_data = {
                'result': analysis_result,
                'cached_at': datetime.utcnow().isoformat(),
                'ttl': ttl
            }
            
            if self.cache_enabled:
                # Use Redis if available
                await self._cache_to_redis(cache_key, cache_data, ttl)
            else:
                # Use in-memory cache
                self._cache_to_memory(cache_key, cache_data, ttl)
            
            logger.debug(f"Cached options analysis: {cache_key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache options analysis: {e}")
            return False
    
    async def get_cached_options_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached options flow analysis"""
        
        try:
            if self.cache_enabled:
                # Try Redis first
                cached_data = await self._get_from_redis(cache_key)
            else:
                # Use in-memory cache
                cached_data = self._get_from_memory(cache_key)
            
            if cached_data:
                # Check if cache is still valid
                if self._is_cache_valid(cached_data):
                    logger.debug(f"Cache hit for options analysis: {cache_key}")
                    return cached_data['result']
                else:
                    # Clean up expired cache
                    await self._remove_from_cache(cache_key)
            
            logger.debug(f"Cache miss for options analysis: {cache_key}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve cached options analysis: {e}")
            return None
    
    async def invalidate_options_cache(self, ticker: str) -> int:
        """Invalidate all options cache entries for a ticker"""
        
        try:
            invalidated_count = 0
            
            if self.cache_enabled:
                # Pattern match for Redis keys
                pattern = f"options_flow:*ticker:{ticker.upper()}*"
                keys = await self._find_redis_keys(pattern)
                
                if keys:
                    invalidated_count = await self._delete_redis_keys(keys)
            else:
                # Clean in-memory cache
                keys_to_remove = [
                    key for key in self._memory_cache.keys()
                    if f"ticker:{ticker.upper()}" in key
                ]
                
                for key in keys_to_remove:
                    del self._memory_cache[key]
                    if key in self._cache_timestamps:
                        del self._cache_timestamps[key]
                
                invalidated_count = len(keys_to_remove)
            
            logger.info(f"Invalidated {invalidated_count} options cache entries for {ticker}")
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Failed to invalidate options cache for {ticker}: {e}")
            return 0
    
    async def cleanup_expired_options_cache(self) -> int:
        """Clean up expired options cache entries"""
        
        try:
            cleaned_count = 0
            
            if not self.cache_enabled:
                # Clean in-memory cache
                current_time = datetime.utcnow()
                expired_keys = []
                
                for key, timestamp in self._cache_timestamps.items():
                    if current_time - timestamp > timedelta(seconds=self.max_ttl):
                        expired_keys.append(key)
                
                for key in expired_keys:
                    if key in self._memory_cache:
                        del self._memory_cache[key]
                    if key in self._cache_timestamps:
                        del self._cache_timestamps[key]
                
                cleaned_count = len(expired_keys)
            
            logger.info(f"Cleaned up {cleaned_count} expired options cache entries")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired options cache: {e}")
            return 0
    
    def _should_cache_result(self, analysis_result: Dict[str, Any]) -> bool:
        """Determine if analysis result should be cached"""
        
        # Don't cache error results
        if 'error' in analysis_result:
            return False
        
        # Don't cache very low confidence results
        confidence = analysis_result.get('confidence', 0)
        if confidence < 0.1:
            return False
        
        # Don't cache if no unusual activity and neutral flow
        unusual_activity = analysis_result.get('unusual_activity', False)
        flow_direction = analysis_result.get('flow_direction', 'neutral')
        
        if not unusual_activity and flow_direction == 'neutral':
            return False
        
        return True
    
    def _determine_ttl(self, analysis_result: Dict[str, Any]) -> int:
        """Determine TTL based on analysis characteristics"""
        
        # Base TTL
        ttl = self.default_ttl
        
        # Adjust based on time sensitivity
        time_sensitivity = analysis_result.get('time_sensitivity', 'intraday')
        sensitivity_multipliers = {
            'immediate': 0.5,  # 2.5 minutes
            'intraday': 1.0,   # 5 minutes
            'swing': 2.0,      # 10 minutes
            'positional': 3.0  # 15 minutes
        }
        
        multiplier = sensitivity_multipliers.get(time_sensitivity, 1.0)
        ttl = int(ttl * multiplier)
        
        # Cap at max TTL
        return min(ttl, self.max_ttl)
    
    def _is_cache_valid(self, cached_data: Dict[str, Any]) -> bool:
        """Check if cached data is still valid"""
        
        cached_at_str = cached_data.get('cached_at')
        if not cached_at_str:
            return False
        
        try:
            cached_at = datetime.fromisoformat(cached_at_str.replace('Z', '+00:00'))
            ttl = cached_data.get('ttl', self.default_ttl)
            
            age = (datetime.utcnow() - cached_at).total_seconds()
            return age < ttl
            
        except (ValueError, TypeError):
            return False
    
    async def _cache_to_redis(self, key: str, data: Dict, ttl: int):
        """Cache to Redis (placeholder for Redis implementation)"""
        # This would be implemented when Redis is integrated
        pass
    
    async def _get_from_redis(self, key: str) -> Optional[Dict]:
        """Get from Redis (placeholder for Redis implementation)"""
        # This would be implemented when Redis is integrated
        return None
    
    async def _find_redis_keys(self, pattern: str) -> List[str]:
        """Find Redis keys by pattern (placeholder)"""
        return []
    
    async def _delete_redis_keys(self, keys: List[str]) -> int:
        """Delete Redis keys (placeholder)"""
        return 0
    
    async def _remove_from_cache(self, key: str):
        """Remove from cache (both Redis and memory)"""
        if key in self._memory_cache:
            del self._memory_cache[key]
        if key in self._cache_timestamps:
            del self._cache_timestamps[key]
    
    def _cache_to_memory(self, key: str, data: Dict, ttl: int):
        """Cache to in-memory storage"""
        self._memory_cache[key] = data
        self._cache_timestamps[key] = datetime.utcnow()
    
    def _get_from_memory(self, key: str) -> Optional[Dict]:
        """Get from in-memory cache"""
        return self._memory_cache.get(key)
