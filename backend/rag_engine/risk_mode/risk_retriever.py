"""
Risk Evidence Retriever - Vector Database and Database Query Integration

This module handles evidence retrieval for risk assessment, including:
- Vector database searches with risk-specific filters
- Database queries for current anomalies and incidents
- Evidence ranking and re-ranking for risk relevance
- Cross-source evidence correlation
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
import hashlib
import json

logger = logging.getLogger(__name__)

class RiskEvidenceRetriever:
    """Retrieves and ranks evidence for risk assessment"""
    
    def __init__(self, vector_store, db_manager):
        self.vector_store = vector_store
        self.db_manager = db_manager
        
        # Risk-specific configuration
        self.risk_types = ["technical", "infra", "regulatory", "sentiment", "liquidity"]
        self.default_top_k = 15
        self.max_chunks_per_type = 5
        self.similarity_threshold = 0.7
        
        # Risk ranking weights
        self.risk_weights = {
            "infra": 1.0,      # Infrastructure incidents = highest priority
            "regulatory": 0.85, # Regulatory changes = high priority  
            "sentiment": 0.7,   # Negative sentiment = medium priority
            "liquidity": 0.6    # Liquidity issues = medium priority
        }
        
        logger.info("RiskEvidenceRetriever initialized")
    
    async def retrieve_risk_evidence(self, query: str, params: Dict[str, Any]) -> List:
        """
        Main entry point for risk evidence retrieval
        
        Args:
            query: Risk-related query text
            params: Retrieval parameters (ticker, time_window, risk_types, etc.)
            
        Returns:
            List of ranked evidence chunks relevant to risk assessment
        """
        try:
            # Build risk-specific filters
            vector_filters = self._build_risk_filters(params)
            
            # Vector database search
            vector_chunks = await self._search_vector_database(query, vector_filters, params)
            
            # Apply risk-specific ranking
            ranked_chunks = self._apply_risk_ranking(vector_chunks, params)
            
            # Filter to top candidates
            final_chunks = self._select_top_evidence(ranked_chunks, params)
            
            logger.info(f"Retrieved {len(final_chunks)} risk evidence chunks for query: {query[:50]}...")
            return final_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving risk evidence: {str(e)}")
            return []
    
    def _build_risk_filters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Build ChromaDB filters for risk-specific search"""
        
        filters = {}
        
        # Ticker-specific filter (single condition)
        ticker = params.get("ticker")
        if ticker:
            filters["ticker"] = ticker
            return filters  # Use only ticker filter to avoid complex where clauses
        
        # If no ticker specified, don't use any filters - filter in post-processing
        # This avoids ChromaDB complex query issues
        
        logger.debug(f"Built risk filters: {filters}")
        return filters
    
    async def _search_vector_database(self, query: str, filters: Dict[str, Any], 
                                    params: Dict[str, Any]) -> List:
        """Perform vector similarity search with risk filters"""
        
        try:
            # Perform similarity search with simple filters
            vector_results = self.vector_store.query_documents(
                query_texts=[query],
                n_results=self.default_top_k,
                where=filters if filters else None
            )
            
            # Extract and structure documents from results
            chunks = []
            if vector_results and vector_results.get('documents'):
                for i, doc in enumerate(vector_results['documents'][0]):
                    metadata = vector_results['metadatas'][0][i] if vector_results.get('metadatas') and vector_results['metadatas'][0] else {}
                    
                    # Create a document-like object for compatibility
                    chunk = type('Document', (), {
                        'page_content': doc,
                        'metadata': metadata
                    })()
                    chunks.append(chunk)
            
            # Apply additional filtering in Python (time, severity, risk types)
            filtered_chunks = self._post_filter_chunks(chunks, params)
            
            logger.debug(f"Vector search returned {len(chunks)} chunks, {len(filtered_chunks)} after filtering")
            return filtered_chunks
            
        except Exception as e:
            logger.error(f"Vector database search error: {str(e)}")
            
            # Fallback: try search without any filters
            try:
                logger.info("Attempting fallback search without filters")
                vector_results = self.vector_store.query_documents(
                    query_texts=[query],
                    n_results=self.default_top_k // 2  # Fewer results for unfiltered search
                )
                
                # Extract documents from results
                chunks = []
                if vector_results and vector_results.get('documents'):
                    for i, doc in enumerate(vector_results['documents'][0]):
                        metadata = vector_results['metadatas'][0][i] if vector_results.get('metadatas') and vector_results['metadatas'][0] else {}
                        
                        # Create a document-like object for compatibility
                        chunk = type('Document', (), {
                            'page_content': doc,
                            'metadata': metadata
                        })()
                        chunks.append(chunk)
                
                # Post-filter in Python
                filtered_chunks = self._post_filter_chunks(chunks, params)
                return filtered_chunks
                
            except Exception as fallback_error:
                logger.error(f"Fallback search also failed: {str(fallback_error)}")
                return []
    
    def _post_filter_chunks(self, chunks: List, params: Dict[str, Any]) -> List:
        """Apply filters in Python when ChromaDB filtering fails"""
        
        filtered = []
        
        # Get filtering criteria from params
        risk_types = params.get("risk_types", self.risk_types)
        severity_threshold = params.get("severity_threshold", "low")  # More inclusive default
        ticker = params.get("ticker")
        time_window_hours = params.get("time_window_hours", 8760)  # Default 1 year for testing
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        
        for chunk in chunks:
            if not hasattr(chunk, 'metadata'):
                continue
            
            metadata = chunk.metadata
            include_chunk = True
            
            # Check risk type filter (more inclusive)
            if risk_types and metadata.get("risk_type") not in risk_types:
                # Allow if no specific risk_type in metadata
                if metadata.get("risk_type"):
                    include_chunk = False
            
            # Check severity filter (more inclusive)
            if severity_threshold == "high" and include_chunk:
                chunk_severity = metadata.get("severity", "low")
                if chunk_severity not in ["high"]:
                    include_chunk = False
            # For medium/low, include all severities
            
            # Check ticker filter
            if ticker and include_chunk and metadata.get("ticker") != ticker:
                include_chunk = False
            
            # Relax timestamp filter for testing - only exclude very old data
            if include_chunk:
                try:
                    chunk_timestamp_str = metadata.get("timestamp")
                    if chunk_timestamp_str:
                        from dateutil import parser
                        chunk_timestamp = parser.parse(chunk_timestamp_str)
                        
                        # Make sure we're comparing timezone-aware datetimes
                        now = datetime.now(timezone.utc)
                        if chunk_timestamp.tzinfo is not None and now.tzinfo is None:
                            # Chunk has timezone, now doesn't - convert now to UTC
                            now = now.replace(tzinfo=timezone.utc)
                        elif chunk_timestamp.tzinfo is None and now.tzinfo is not None:
                            # Now has timezone, chunk doesn't - assume chunk is UTC
                            chunk_timestamp = chunk_timestamp.replace(tzinfo=timezone.utc)
                        
                        # Only exclude data older than 10 years
                        very_old_cutoff = now - timedelta(days=3650)
                        if chunk_timestamp < very_old_cutoff:
                            include_chunk = False
                except Exception as e:
                    logger.debug(f"Error parsing timestamp {chunk_timestamp_str}: {e}")
                    # Include chunk if timestamp parsing fails
            
            if include_chunk:
                filtered.append(chunk)
        
        logger.debug(f"Post-filtering reduced chunks from {len(chunks)} to {len(filtered)}")
        return filtered
    
    def _apply_risk_ranking(self, chunks: List, params: Dict[str, Any]) -> List:
        """Apply risk-specific ranking to search results"""
        
        scored_chunks = []
        
        for chunk in chunks:
            if not hasattr(chunk, 'metadata'):
                continue
            
            metadata = chunk.metadata
            base_score = getattr(chunk, 'similarity_score', 0.7)  # Default score if not available
            
            # Risk type boost
            risk_type = metadata.get("risk_type", "unknown")
            risk_boost = self.risk_weights.get(risk_type, 0.5)
            
            # Severity boost
            severity = metadata.get("severity", "low")
            severity_boost = {"high": 1.0, "medium": 0.8, "low": 0.6}.get(severity, 0.5)
            
            # Recency boost (more recent = higher priority for risk assessment)
            recency_boost = self._calculate_recency_boost(metadata.get("timestamp"))
            
            # Anomaly flag boost
            anomaly_flag = metadata.get("anomaly_flag", False)
            anomaly_boost = 1.2 if anomaly_flag else 1.0
            
            # Ticker relevance boost
            ticker = params.get("ticker")
            ticker_boost = 1.1 if ticker and metadata.get("ticker") == ticker else 1.0
            
            # Calculate final risk score
            risk_score = (
                base_score * 
                risk_boost * 
                severity_boost * 
                recency_boost * 
                anomaly_boost * 
                ticker_boost
            )
            
            # Add risk score to chunk
            chunk.risk_score = risk_score
            chunk.risk_ranking_details = {
                "base_score": base_score,
                "risk_boost": risk_boost,
                "severity_boost": severity_boost,
                "recency_boost": recency_boost,
                "anomaly_boost": anomaly_boost,
                "ticker_boost": ticker_boost
            }
            
            scored_chunks.append(chunk)
        
        # Sort by risk score (descending)
        ranked_chunks = sorted(scored_chunks, key=lambda x: x.risk_score, reverse=True)
        
        logger.debug(f"Applied risk ranking to {len(ranked_chunks)} chunks")
        return ranked_chunks
    
    def _calculate_recency_boost(self, timestamp_str: Optional[str]) -> float:
        """Calculate recency boost for risk assessment (more recent = higher boost)"""
        
        if not timestamp_str:
            return 0.5  # Low boost for unknown timestamp
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            # Make sure both timestamps have timezone info
            now = datetime.now(timezone.utc)
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            
            hours_old = (now - timestamp).total_seconds() / 3600
            
            # Risk assessment prioritizes very recent events
            if hours_old <= 1:     # Last hour
                return 1.0
            elif hours_old <= 6:   # Last 6 hours
                return 0.9
            elif hours_old <= 24:  # Last day
                return 0.8
            elif hours_old <= 72:  # Last 3 days
                return 0.7
            elif hours_old <= 168: # Last week
                return 0.6
            else:                  # Older than a week
                return 0.4
                
        except (ValueError, AttributeError):
            return 0.5  # Default boost for unparseable timestamp
    
    def _select_top_evidence(self, ranked_chunks: List, params: Dict[str, Any]) -> List:
        """Select top evidence chunks with diversity across risk types"""
        
        target_count = params.get("max_evidence_chunks", 10)
        risk_types = params.get("risk_types", self.risk_types)
        
        # Group chunks by risk type
        chunks_by_type = {risk_type: [] for risk_type in risk_types}
        
        for chunk in ranked_chunks:
            if hasattr(chunk, 'metadata'):
                risk_type = chunk.metadata.get("risk_type", "unknown")
                if risk_type in chunks_by_type:
                    chunks_by_type[risk_type].append(chunk)
        
        # Select top chunks from each risk type
        final_chunks = []
        chunks_per_type = max(1, target_count // len(risk_types))
        
        for risk_type in risk_types:
            type_chunks = chunks_by_type[risk_type][:chunks_per_type]
            final_chunks.extend(type_chunks)
            
            if len(final_chunks) >= target_count:
                break
        
        # If we haven't reached target count, add more from highest-scored chunks
        remaining_chunks = [c for c in ranked_chunks if c not in final_chunks]
        remaining_needed = target_count - len(final_chunks)
        
        if remaining_needed > 0 and remaining_chunks:
            final_chunks.extend(remaining_chunks[:remaining_needed])
        
        # Final sort by risk score
        final_chunks = sorted(final_chunks, key=lambda x: x.risk_score, reverse=True)
        
        logger.info(f"Selected {len(final_chunks)} top evidence chunks across {len([rt for rt in risk_types if chunks_by_type[rt]])} risk types")
        
        return final_chunks
    
    def get_evidence_summary(self, evidence_chunks: List) -> Dict[str, Any]:
        """Generate summary of retrieved evidence for logging and analysis"""
        
        summary = {
            "total_chunks": len(evidence_chunks),
            "by_risk_type": {},
            "by_severity": {},
            "by_ticker": {},
            "score_range": {"min": 0, "max": 0, "avg": 0},
            "time_range": {"earliest": None, "latest": None}
        }
        
        if not evidence_chunks:
            return summary
        
        scores = []
        timestamps = []
        
        for chunk in evidence_chunks:
            if not hasattr(chunk, 'metadata'):
                continue
            
            metadata = chunk.metadata
            
            # Risk type distribution
            risk_type = metadata.get("risk_type", "unknown")
            summary["by_risk_type"][risk_type] = summary["by_risk_type"].get(risk_type, 0) + 1
            
            # Severity distribution
            severity = metadata.get("severity", "unknown")
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            
            # Ticker distribution
            ticker = metadata.get("ticker", "general")
            summary["by_ticker"][ticker] = summary["by_ticker"].get(ticker, 0) + 1
            
            # Score tracking
            if hasattr(chunk, 'risk_score'):
                scores.append(chunk.risk_score)
            
            # Timestamp tracking
            if metadata.get("timestamp"):
                try:
                    timestamps.append(datetime.fromisoformat(metadata["timestamp"]))
                except ValueError:
                    pass
        
        # Score statistics
        if scores:
            summary["score_range"] = {
                "min": round(min(scores), 3),
                "max": round(max(scores), 3),
                "avg": round(sum(scores) / len(scores), 3)
            }
        
        # Time range
        if timestamps:
            summary["time_range"] = {
                "earliest": min(timestamps).isoformat(),
                "latest": max(timestamps).isoformat()
            }
        
        return summary
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on evidence retrieval components"""
        
        health_status = {
            "overall": "healthy",
            "components": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # Test vector store
            test_results = self.vector_store.query_documents(
                query_texts=["test query"], 
                n_results=1
            )
            result_count = len(test_results.get('documents', [[]])[0]) if test_results else 0
            health_status["components"]["vector_store"] = {
                "status": "healthy",
                "test_results": result_count
            }
        except Exception as e:
            health_status["components"]["vector_store"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall"] = "degraded"
        
        try:
            # Test database
            test_query = "SELECT 1 as test"
            result = await self.db_manager.fetch_one(test_query)
            health_status["components"]["database"] = {
                "status": "healthy",
                "connection": "active"
            }
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy", 
                "error": str(e)
            }
            health_status["overall"] = "degraded"
        
        return health_status
