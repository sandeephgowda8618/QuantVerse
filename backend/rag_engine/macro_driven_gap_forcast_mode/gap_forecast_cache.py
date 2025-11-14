"""
Gap Forecast Cache Manager - Caching for Gap Predictions

This module manages caching for gap forecasting results to improve performance
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class GapForecastCacheManager:
    """Cache manager for gap forecasting predictions and analyses"""
    
    def __init__(self, redis_client=None):
        """
        Initialize cache manager
        
        Args:
            redis_client: Optional Redis client for distributed caching
        """
        self.redis_client = redis_client
        self.use_redis = redis_client is not None
        self.local_cache = {}
        
        # Cache TTL settings (in seconds)
        self.prediction_ttl = 1800  # 30 minutes for predictions
        self.historical_ttl = 14400  # 4 hours for historical patterns
        self.event_analysis_ttl = 3600  # 1 hour for event analysis
        
        logger.info(f"GapForecastCacheManager initialized with Redis: {self.use_redis}")
    
    def generate_forecast_cache_key(self, 
                                  asset: str, 
                                  macro_event: str, 
                                  prediction_horizon: int,
                                  query: str = "") -> str:
        """
        Generate cache key for gap forecast
        
        Args:
            asset: Asset symbol (e.g., 'NASDAQ', 'BTC')
            macro_event: Type of macro event ('fomc', 'rbi', 'regulatory')
            prediction_horizon: Hours ahead for prediction
            query: Optional query string for additional context
            
        Returns:
            str: Cache key for the forecast
        """
        # Create hash of query for consistent key generation
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8] if query else "default"
        
        # Include current hour to ensure cache invalidation on time progression
        current_hour = datetime.now().strftime("%Y%m%d%H")
        
        cache_key = f"gap_forecast:{asset}:{macro_event}:{prediction_horizon}:{current_hour}:{query_hash}"
        
        return cache_key.lower()
    
    async def cache_gap_prediction(self, 
                                 cache_key: str, 
                                 prediction_result: Dict[str, Any]) -> bool:
        """
        Cache gap prediction result
        
        Args:
            cache_key: Cache key for storage
            prediction_result: Prediction result to cache
            
        Returns:
            bool: Success of caching operation
        """
        try:
            # Add cache metadata
            cache_data = {
                'prediction': prediction_result,
                'cached_at': datetime.now().isoformat(),
                'ttl': self.prediction_ttl
            }
            
            cache_value = json.dumps(cache_data)
            
            if self.use_redis:
                # Use Redis for distributed caching
                await self.redis_client.setex(
                    cache_key, 
                    self.prediction_ttl, 
                    cache_value
                )
            else:
                # Use local cache with expiration
                expiry = datetime.now() + timedelta(seconds=self.prediction_ttl)
                self.local_cache[cache_key] = {
                    'data': cache_data,
                    'expires_at': expiry
                }
            
            logger.debug(f"Cached gap prediction: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache gap prediction {cache_key}: {e}")
            return False
    
    async def get_cached_gap_prediction(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached gap prediction
        
        Args:
            cache_key: Cache key to retrieve
            
        Returns:
            Optional[Dict]: Cached prediction result or None
        """
        try:
            if self.use_redis:
                # Get from Redis
                cached_value = await self.redis_client.get(cache_key)
                if cached_value:
                    cache_data = json.loads(cached_value)
                    logger.debug(f"Cache hit (Redis): {cache_key}")
                    return cache_data.get('prediction')
            else:
                # Get from local cache
                cache_entry = self.local_cache.get(cache_key)
                if cache_entry and cache_entry['expires_at'] > datetime.now():
                    logger.debug(f"Cache hit (local): {cache_key}")
                    return cache_entry['data'].get('prediction')
                elif cache_entry:
                    # Remove expired entry
                    del self.local_cache[cache_key]
            
            logger.debug(f"Cache miss: {cache_key}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve cached prediction {cache_key}: {e}")
            return None
    
    async def invalidate_forecast_cache(self, 
                                      asset: str, 
                                      event_type: str = None) -> int:
        """
        Invalidate cache entries for specific asset/event
        
        Args:
            asset: Asset to invalidate cache for
            event_type: Optional specific event type to invalidate
            
        Returns:
            int: Number of invalidated entries
        """
        invalidated_count = 0
        
        try:
            if self.use_redis:
                # Pattern-based deletion in Redis
                if event_type:
                    pattern = f"gap_forecast:{asset}:{event_type}:*"
                else:
                    pattern = f"gap_forecast:{asset}:*"
                
                keys = await self.redis_client.keys(pattern)
                if keys:
                    invalidated_count = await self.redis_client.delete(*keys)
            else:
                # Local cache invalidation
                keys_to_remove = []
                for key in self.local_cache.keys():
                    if key.startswith(f"gap_forecast:{asset}:"):
                        if not event_type or f":{event_type}:" in key:
                            keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    del self.local_cache[key]
                    invalidated_count += 1
            
            logger.info(f"Invalidated {invalidated_count} cache entries for {asset}:{event_type}")
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache for {asset}:{event_type}: {e}")
            return 0
    
    async def cleanup_expired_forecast_cache(self) -> int:
        """
        Clean up expired cache entries
        
        Returns:
            int: Number of cleaned up entries
        """
        cleaned_count = 0
        
        try:
            if not self.use_redis:  # Redis handles expiration automatically
                # Clean up local cache
                current_time = datetime.now()
                expired_keys = [
                    key for key, entry in self.local_cache.items()
                    if entry['expires_at'] <= current_time
                ]
                
                for key in expired_keys:
                    del self.local_cache[key]
                    cleaned_count += 1
                
                logger.debug(f"Cleaned up {cleaned_count} expired cache entries")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired cache: {e}")
            return 0
    
    async def cache_historical_patterns(self, 
                                      asset: str, 
                                      patterns: Dict[str, Any]) -> bool:
        """
        Cache historical gap patterns (longer TTL)
        
        Args:
            asset: Asset symbol
            patterns: Historical pattern analysis
            
        Returns:
            bool: Success of caching operation
        """
        cache_key = f"gap_patterns:{asset}:{datetime.now().strftime('%Y%m%d')}"
        
        try:
            cache_data = {
                'patterns': patterns,
                'cached_at': datetime.now().isoformat(),
                'ttl': self.historical_ttl
            }
            
            cache_value = json.dumps(cache_data)
            
            if self.use_redis:
                await self.redis_client.setex(
                    cache_key,
                    self.historical_ttl,
                    cache_value
                )
            else:
                expiry = datetime.now() + timedelta(seconds=self.historical_ttl)
                self.local_cache[cache_key] = {
                    'data': cache_data,
                    'expires_at': expiry
                }
            
            logger.debug(f"Cached historical patterns: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache historical patterns {cache_key}: {e}")
            return False
    
    async def get_cached_historical_patterns(self, asset: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached historical patterns
        
        Args:
            asset: Asset symbol
            
        Returns:
            Optional[Dict]: Cached patterns or None
        """
        cache_key = f"gap_patterns:{asset}:{datetime.now().strftime('%Y%m%d')}"
        
        try:
            if self.use_redis:
                cached_value = await self.redis_client.get(cache_key)
                if cached_value:
                    cache_data = json.loads(cached_value)
                    return cache_data.get('patterns')
            else:
                cache_entry = self.local_cache.get(cache_key)
                if cache_entry and cache_entry['expires_at'] > datetime.now():
                    return cache_entry['data'].get('patterns')
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve cached patterns {cache_key}: {e}")
            return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dict: Cache statistics
        """
        stats = {
            'cache_type': 'redis' if self.use_redis else 'local',
            'prediction_ttl': self.prediction_ttl,
            'historical_ttl': self.historical_ttl,
            'event_analysis_ttl': self.event_analysis_ttl
        }
        
        if not self.use_redis:
            stats.update({
                'local_cache_size': len(self.local_cache),
                'active_keys': list(self.local_cache.keys())
            })
        
        return stats

"""
Gap Forecast Cache Manager - Additional Implementation Notes

Cache Strategy:
- Pre-event predictions vs post-event predictions should be cached separately
- Major macro events (FOMC, RBI decisions) warrant cache warming for popular assets
- Cross-asset predictions can share cache components

Cache Invalidation Triggers:
- New macro announcements or policy changes
- Significant market moves that change context
- Updated economic data releases
- Central bank communication updates

Cache Tiers:
# 1. Historical gap patterns (longest TTL - 24h)
# 2. Macro event analysis (medium TTL - 2h)
# 3. Real-time gap predictions (shortest TTL - 30min)

Initial Implementation:
- Start with simple no-cache approach (like risk_cache.py)
- Add event-driven cache invalidation once prediction accuracy is proven
- Focus on correct invalidation logic for changing macro conditions
"""
