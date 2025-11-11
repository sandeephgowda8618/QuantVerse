"""
This module provides a simplified cache manager that doesn't use any external caching.
All caching methods are implemented as no-ops for simplicity and reliability.
"""

import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class RiskCacheManager:
    """Simple no-cache manager for risk assessment pipeline"""
    
    def __init__(self, redis_client=None):
        # Ignore redis_client parameter - we don't use caching
        logger.info("Risk cache manager initialized (no caching)")
    
    def generate_cache_key(self, query: str, params: Dict[str, Any]) -> str:
        """Generate cache key (unused in no-cache implementation)"""
        # Create a simple hash for consistency
        normalized_params = {k: v for k, v in params.items() if v is not None}
        cache_string = f"{query}:{json.dumps(normalized_params, sort_keys=True)}"
        return hashlib.md5(cache_string.encode()).hexdigest()[:16]
    
    def cache_risk_assessment(self, cache_key: str, assessment: Dict[str, Any]) -> bool:
        """Store risk assessment in cache (no-op)"""
        # No caching - just return success
        logger.debug(f"Risk assessment cache store skipped (no caching): {cache_key}")
        return True
    
    def get_cached_risk_assessment(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached risk assessment (always returns None)"""
        # No caching - always return None to force fresh computation
        logger.debug(f"Risk assessment cache lookup skipped (no caching): {cache_key}")
        return None
    
    def cache_ml_signals(self, ticker: str, signals: Dict[str, Any]) -> bool:
        """Store ML signals in cache (no-op)"""
        # No caching - just return success
        logger.debug(f"ML signals cache store skipped (no caching): {ticker}")
        return True
    
    def get_cached_ml_signals(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get cached ML signals (always returns None)"""
        # No caching - always return None
        logger.debug(f"ML signals cache lookup skipped (no caching): {ticker}")
        return None
    
    def cache_evidence_results(self, query_hash: str, evidence: List[Any]) -> bool:
        """Store evidence search results in cache (no-op)"""
        # No caching - just return success
        logger.debug(f"Evidence cache store skipped (no caching): {query_hash}")
        return True
    
    def get_cached_evidence(self, query_hash: str) -> Optional[List[Any]]:
        """Get cached evidence results (always returns None)"""
        # No caching - always return None
        logger.debug(f"Evidence cache lookup skipped (no caching): {query_hash}")
        return None
    
    def cache_database_features(self, features_key: str, features: Dict[str, Any]) -> bool:
        """Store database features in cache (no-op)"""
        # No caching - just return success
        logger.debug(f"Database features cache store skipped (no caching): {features_key}")
        return True
    
    def get_cached_database_features(self, features_key: str) -> Optional[Dict[str, Any]]:
        """Get cached database features (always returns None)"""
        # No caching - always return None
        logger.debug(f"Database features cache lookup skipped (no caching): {features_key}")
        return None
    
    def invalidate_cache(self, pattern: str = "*") -> int:
        """Invalidate cache entries by pattern (no-op)"""
        # No caching - just return 0
        logger.debug(f"Cache invalidation skipped (no caching): {pattern}")
        return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        return {
            "cache_type": "no_cache",
            "status": "disabled",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stats": {
                "hits": 0,
                "misses": 0,
                "total_entries": 0
            },
            "message": "Caching is disabled for simplicity"
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform cache health check"""
        return {
            "status": "healthy",
            "cache_type": "no_cache", 
            "connection": "n/a",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "No external cache dependencies"
        }
