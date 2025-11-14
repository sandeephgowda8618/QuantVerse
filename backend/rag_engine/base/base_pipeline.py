"""
Base Pipeline Class for RAG-based LLM Systems

This provides a common interface and shared functionality for all specialized
RAG pipelines (options flow, market move, macro gap, etc.)
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)


class BasePipeline(ABC):
    """
    Abstract base class for all RAG pipelines in the uRISK system
    
    Provides common functionality:
    - Query validation and preprocessing
    - Error handling and logging
    - Performance monitoring
    - Cache key generation
    - Response formatting
    """
    
    def __init__(self, vector_store, db_manager, llm_manager, cache_manager=None):
        """Initialize base pipeline with shared dependencies"""
        self.vector_store = vector_store
        self.db_manager = db_manager
        self.llm_manager = llm_manager
        self.cache_manager = cache_manager
        
        # Common configuration
        self.max_query_length = 1000
        self.max_response_tokens = 2000
        self.timeout_seconds = 30
        self.confidence_threshold = 0.3
        
        logger.info(f"{self.__class__.__name__} initialized")
    
    @abstractmethod
    async def process_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Main entry point for processing queries
        
        Args:
            query: User's query string
            **kwargs: Additional parameters specific to each pipeline
            
        Returns:
            Dict containing analysis results
        """
        pass
    
    def _validate_query(self, query: str) -> None:
        """
        Validate input query
        
        Args:
            query: Query string to validate
            
        Raises:
            ValueError: If query is invalid
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
        
        if len(query.strip()) < 5:
            raise ValueError("Query must be at least 5 characters long")
        
        if len(query) > self.max_query_length:
            raise ValueError(f"Query exceeds maximum length of {self.max_query_length} characters")
    
    def _generate_cache_key(self, query: str, **kwargs) -> str:
        """
        Generate cache key for query and parameters
        
        Args:
            query: Query string
            **kwargs: Additional parameters
            
        Returns:
            Cache key string
        """
        import hashlib
        
        # Create a consistent string from query and sorted kwargs
        key_parts = [query.lower().strip()]
        for key, value in sorted(kwargs.items()):
            if value is not None:
                key_parts.append(f"{key}:{str(value)}")
        
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _track_performance(self, operation_name: str, coro):
        """
        Track performance of async operations
        
        Args:
            operation_name: Name of the operation for logging
            coro: Coroutine to execute and time
            
        Returns:
            Result of the coroutine
        """
        start_time = time.time()
        try:
            result = await coro
            duration = time.time() - start_time
            logger.info(f"{operation_name} completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{operation_name} failed after {duration:.2f}s: {str(e)}")
            raise
    
    def _format_error_response(self, error_message: str, query: str = None) -> Dict[str, Any]:
        """
        Create standardized error response
        
        Args:
            error_message: Error description
            query: Original query (optional)
            
        Returns:
            Standardized error response dict
        """
        return {
            'status': 'error',
            'error': error_message,
            'query': query,
            'confidence': 0.0,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'results': []
        }
    
    def _format_success_response(self, data: Dict[str, Any], query: str, confidence: float = None) -> Dict[str, Any]:
        """
        Create standardized success response
        
        Args:
            data: Response data
            query: Original query
            confidence: Confidence score (0.0-1.0)
            
        Returns:
            Standardized success response dict
        """
        return {
            'status': 'success',
            'query': query,
            'confidence': confidence or data.get('confidence', 0.5),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            **data
        }
    
    async def _safe_execute_with_timeout(self, coro, timeout: float = None) -> Any:
        """
        Execute coroutine with timeout protection
        
        Args:
            coro: Coroutine to execute
            timeout: Timeout in seconds (uses self.timeout_seconds if None)
            
        Returns:
            Result of coroutine
            
        Raises:
            asyncio.TimeoutError: If operation times out
        """
        timeout = timeout or self.timeout_seconds
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.error(f"Operation timed out after {timeout} seconds")
            raise
    
    def _extract_ticker_from_query(self, query: str) -> Optional[str]:
        """
        Extract ticker symbol from query using simple pattern matching
        
        Args:
            query: Query string
            
        Returns:
            Ticker symbol if found, None otherwise
        """
        import re
        
        # Common ticker patterns
        patterns = [
            r'\b([A-Z]{2,5})\b',  # 2-5 uppercase letters
            r'\$([A-Z]{2,5})\b',  # $TICKER format
            r'\b([A-Z]{2,5})(?:\s|$)',  # Ticker at word boundary
        ]
        
        query_upper = query.upper()
        
        for pattern in patterns:
            matches = re.findall(pattern, query_upper)
            if matches:
                # Return first valid looking ticker
                for match in matches:
                    if len(match) >= 2 and match.isalpha():
                        return match
        
        return None
    
    def _calculate_confidence(self, evidence_count: int, query_match_score: float = 0.5) -> float:
        """
        Calculate confidence score based on evidence and query matching
        
        Args:
            evidence_count: Number of evidence pieces found
            query_match_score: How well evidence matches query (0.0-1.0)
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence from evidence count
        evidence_confidence = min(evidence_count / 10.0, 0.8)  # Max 0.8 from evidence
        
        # Combine with query match score
        confidence = (evidence_confidence * 0.6) + (query_match_score * 0.4)
        
        return min(max(confidence, 0.0), 1.0)  # Clamp to [0.0, 1.0]
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on pipeline components
        
        Returns:
            Health status dict
        """
        health_status = {
            'pipeline': self.__class__.__name__,
            'status': 'healthy',
            'components': {},
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # Check vector store
            if hasattr(self.vector_store, 'get_collection'):
                collection = self.vector_store.get_collection()
                health_status['components']['vector_store'] = {
                    'status': 'healthy',
                    'collection_name': collection.name if collection else 'unknown'
                }
            else:
                health_status['components']['vector_store'] = {'status': 'unknown'}
            
            # Check database
            if hasattr(self.db_manager, 'async_execute_query'):
                await self.db_manager.async_execute_query("SELECT 1")
                health_status['components']['database'] = {'status': 'healthy'}
            else:
                health_status['components']['database'] = {'status': 'unknown'}
            
            # Check LLM
            if hasattr(self.llm_manager, 'is_ready'):
                health_status['components']['llm'] = {
                    'status': 'healthy' if self.llm_manager.is_ready else 'not_ready'
                }
            else:
                health_status['components']['llm'] = {'status': 'unknown'}
                
        except Exception as e:
            health_status['status'] = 'degraded'
            health_status['error'] = str(e)
        
        return health_status
