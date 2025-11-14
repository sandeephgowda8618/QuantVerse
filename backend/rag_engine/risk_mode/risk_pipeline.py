"""
Risk Assessment Pipeline - Main Orchestrator

This is the main pipeline that orchestrates the RISK mode RAG process:
Query → Risk Filter → Retrieve Evidence → Risk Assessment → JSON Response
"""

import asyncio
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
import logging

from ..vector_store import ChromaVectorStore
from ...db.postgres_handler import PostgresHandler
from ..llm_manager import LLMManager
from .risk_llm import RiskAssessmentLLM
from .risk_retriever import RiskEvidenceRetriever
from .risk_cache import RiskCacheManager

logger = logging.getLogger(__name__)

class RiskAssessmentPipeline:
    """Main orchestrator for RISK mode RAG pipeline"""
    
    def __init__(self, 
                 vector_store: ChromaVectorStore,
                 db_manager: PostgresHandler,
                 cache_manager: RiskCacheManager,
                 llm_model: str = "llama3.1"):
        
        self.vector_store = vector_store
        self.db_manager = db_manager
        self.cache_manager = cache_manager
        
        # Initialize components - use centralized LLM manager
        try:
            self.llm_manager = LLMManager.get_instance()
            logger.info("RiskAssessmentPipeline using centralized LLM manager")
        except RuntimeError:
            # Fallback to local LLM instance if centralized manager not available
            self.risk_llm = RiskAssessmentLLM(model_name=llm_model)
            self.llm_manager = None
            logger.warning("Using local RiskAssessmentLLM instance (centralized manager not available)")
        
        self.evidence_retriever = RiskEvidenceRetriever(vector_store, db_manager)
        
        # Performance settings (adjusted for real-world performance)
        self.vector_search_timeout = 5000  # 5 seconds
        self.db_query_timeout = 2000       # 2 seconds  
        self.llm_timeout = 30000           # 30 seconds
        self.total_timeout = 40000         # 40 seconds total
        
        logger.info("RiskAssessmentPipeline initialized")
        
        logger.info("RiskAssessmentPipeline initialized")
    
    async def assess_risk(self, query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main entry point for risk assessment
        
        Args:
            query: Risk-related query text
            params: Optional parameters (ticker, timestamp, mode, etc.)
            
        Returns:
            Risk assessment response in JSON format
        """
        start_time = time.time()
        
        if params is None:
            params = {}
        
        try:
            # Normalize and validate inputs
            normalized_params = self._normalize_risk_params(query, params)
            
            # Check cache first
            cache_key = self.cache_manager.generate_cache_key(query, normalized_params)
            cached_assessment = self.cache_manager.get_cached_risk_assessment(cache_key)
            
            if cached_assessment:
                logger.info(f"Returning cached risk assessment for query: {query[:50]}...")
                cached_assessment["cached"] = True
                return cached_assessment
            
            # Execute risk assessment pipeline
            assessment = await self._execute_risk_pipeline(query, normalized_params)
            
            # Cache the result
            self.cache_manager.cache_risk_assessment(cache_key, assessment)
            
            # Add metadata
            total_time = (time.time() - start_time) * 1000
            assessment["processing_time_ms"] = round(total_time, 2)
            assessment["cached"] = False
            assessment["timestamp"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Risk assessment completed in {total_time:.2f}ms for query: {query[:50]}...")
            return assessment
            
        except asyncio.TimeoutError as e:
            logger.error(f"Risk assessment timeout: {str(e)}")
            return self._handle_timeout_fallback(query, params, str(e))
        except Exception as e:
            logger.error(f"Risk assessment error: {str(e)}")
            return self._handle_error_fallback(query, params, str(e))
    
    def _normalize_risk_params(self, query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and validate risk assessment parameters"""
        
        normalized = {
            "mode": "RISK",
            "ticker": params.get("ticker"),
            "time_window": params.get("time_window", "7d"),
            "severity_threshold": params.get("severity_threshold", "medium"),
            "risk_types": params.get("risk_types", ["technical", "infra", "regulatory", "sentiment", "liquidity"]),
            "high_priority": params.get("high_priority", False)
        }
        
        # Validate risk types
        valid_risk_types = {"technical", "infra", "regulatory", "sentiment", "liquidity"}
        normalized["risk_types"] = [rt for rt in normalized["risk_types"] if rt in valid_risk_types]
        
        if not normalized["risk_types"]:
            normalized["risk_types"] = ["technical", "infra", "regulatory", "sentiment", "liquidity"]
        
        # Parse time window
        normalized["time_window_hours"] = self._parse_time_window(normalized["time_window"])
        
        logger.debug(f"Normalized risk params: {normalized}")
        return normalized
    
    def _parse_time_window(self, time_window: str) -> int:
        """Parse time window string to hours"""
        if time_window.endswith("h"):
            return int(time_window[:-1])
        elif time_window.endswith("d"):
            return int(time_window[:-1]) * 24
        elif time_window.endswith("w"):
            return int(time_window[:-1]) * 24 * 7
        else:
            return 168  # Default 7 days
    
    async def _execute_risk_pipeline(self, query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the main risk assessment pipeline with parallel operations"""
        
        # Create parallel tasks for independent operations
        tasks = []
        
        # 1. Vector search for risk evidence
        tasks.append(
            asyncio.wait_for(
                self.evidence_retriever.retrieve_risk_evidence(query, params),
                timeout=self.vector_search_timeout/1000
            )
        )
        
        # 2. Database features (current anomalies, incidents, etc.)
        tasks.append(
            asyncio.wait_for(
                self._get_database_features(params),
                timeout=self.db_query_timeout/1000
            )
        )

        # Execute parallel operations
        vector_evidence, db_features = await asyncio.gather(*tasks)
        
        # Compile comprehensive evidence
        evidence = self._compile_risk_evidence(vector_evidence, {}, db_features, params)
        
        # LLM risk assessment (sequential, depends on evidence)
        if self.llm_manager:
            # Use centralized LLM manager with risk-specific prompts
            risk_assessment = await asyncio.wait_for(
                self._assess_risk_with_centralized_llm(evidence, query, params),
                timeout=self.llm_timeout/1000
            )
        else:
            # Fallback to local RiskAssessmentLLM
            risk_assessment = await asyncio.wait_for(
                self.risk_llm.assess_risk(evidence, query, params),
                timeout=self.llm_timeout/1000
            )
        
        return risk_assessment
    
    async def _get_database_features(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gather database features for risk assessment"""
        
        ticker = params.get("ticker")
        time_window_hours = params.get("time_window_hours", 168)
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        
        features = {}
        
        try:
            # Current anomalies (using actual schema)
            try:
                anomalies_query = """
                    SELECT * FROM anomalies 
                    WHERE timestamp >= $1 
                    AND severity IN ('medium', 'high')
                """
                if ticker:
                    anomalies_query += " AND ticker = $2"
                    features["current_anomalies"] = await self.db_manager.fetch_all(
                        anomalies_query, (cutoff_time, ticker)
                    )
                else:
                    features["current_anomalies"] = await self.db_manager.fetch_all(
                        anomalies_query, (cutoff_time,)
                    )
            except Exception as e:
                logger.debug(f"Anomalies table query failed: {e}")
                features["current_anomalies"] = []
            
            # Active incidents (using correct schema)
            try:
                incidents_query = """
                    SELECT * FROM infra_incidents 
                    WHERE occurred_at >= $1 
                    AND (status = 'active' OR resolved_at >= $1)
                    ORDER BY occurred_at DESC
                    LIMIT 10
                """
                features["active_incidents"] = await self.db_manager.fetch_all(
                    incidents_query, (cutoff_time,)
                )
            except Exception as e:
                logger.debug(f"Incidents table query failed: {e}")
                features["active_incidents"] = []
            
            # Recent regulatory events (if table exists)
            try:
                regulatory_query = """
                    SELECT * FROM regulatory_events 
                    WHERE published_at >= $1
                    ORDER BY published_at DESC
                    LIMIT 10
                """
                features["regulatory_events"] = await self.db_manager.fetch_all(
                    regulatory_query, (cutoff_time,)
                )
            except Exception as e:
                logger.debug(f"Regulatory events table query failed: {e}")
                features["regulatory_events"] = []
            
            # Risk alerts (using actual schema)
            try:
                alerts_query = """
                    SELECT * FROM alerts 
                    WHERE triggered_at >= $1
                    AND resolved = false
                """
                if ticker:
                    alerts_query += " AND ticker = $2"
                    features["active_alerts"] = await self.db_manager.fetch_all(
                        alerts_query, (cutoff_time, ticker)
                    )
                else:
                    features["active_alerts"] = await self.db_manager.fetch_all(
                        alerts_query, (cutoff_time,)
                    )
            except Exception as e:
                logger.debug(f"Alerts table query failed: {e}")
                features["active_alerts"] = []
            
            logger.debug(f"Database features retrieved: {len(features)} feature types")
            
        except Exception as e:
            logger.error(f"Error getting database features: {str(e)}")
            features = {"error": str(e)}
        
        return features
    
    def _compile_risk_evidence(self, vector_evidence: List, ml_signals: Dict, 
                              db_features: Dict, params: Dict) -> Dict[str, Any]:
        """Compile all evidence sources into structured format for LLM"""
        
        evidence = {
            "vector_evidence": vector_evidence,
            "db_features": db_features,
            "query_params": params,
            "risk_summary": {
                "technical": {"count": 0, "max_severity": "low"},
                "infra": {"count": 0, "max_severity": "low"},
                "regulatory": {"count": 0, "max_severity": "low"},
                "sentiment": {"count": 0, "max_severity": "low"},
                "liquidity": {"count": 0, "max_severity": "low"}
            }
        }
        
        # Analyze vector evidence for risk summary
        for chunk in vector_evidence:
            if hasattr(chunk, 'metadata') and 'risk_type' in chunk.metadata:
                risk_type = chunk.metadata["risk_type"]
                severity = chunk.metadata.get("severity", "low")
                
                if risk_type in evidence["risk_summary"]:
                    evidence["risk_summary"][risk_type]["count"] += 1
                    
                    # Update max severity
                    current_max = evidence["risk_summary"][risk_type]["max_severity"]
                    if severity == "high" or (severity == "medium" and current_max == "low"):
                        evidence["risk_summary"][risk_type]["max_severity"] = severity
        
        # Add DB feature summaries
        if db_features and not db_features.get("error"):
            evidence["db_summary"] = {
                "active_incidents": len(db_features.get("active_incidents", [])),
                "current_anomalies": len(db_features.get("current_anomalies", [])),
                "regulatory_events": len(db_features.get("regulatory_events", [])),
                "active_alerts": len(db_features.get("active_alerts", []))
            }
        
        logger.debug(f"Compiled evidence: {evidence['risk_summary']}")
        return evidence
    
    def _get_max_severity(self, items: List[Dict]) -> str:
        """Get maximum severity from list of items"""
        severities = [item.get("severity", "low") for item in items]
        if "high" in severities:
            return "high"
        elif "medium" in severities:
            return "medium"
        else:
            return "low"
    
    def _handle_timeout_fallback(self, query: str, params: Dict, error: str) -> Dict[str, Any]:
        """Handle timeout with graceful degradation"""
        logger.warning(f"Risk assessment timeout for query: {query[:50]}...")
        
        return {
            "risk_summary": "Risk assessment partially available due to timeout",
            "risk_level": "unknown",
            "primary_risks": [],
            "confidence": 0.3,
            "evidence_used": [],
            "warnings": ["timeout_occurred", f"error: {error}"],
            "monitoring_recommendations": ["Retry risk assessment", "Check system performance"],
            "processing_time_ms": self.total_timeout,
            "cached": False,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _handle_error_fallback(self, query: str, params: Dict, error: str) -> Dict[str, Any]:
        """Handle errors with basic response"""
        logger.error(f"Risk assessment error for query: {query[:50]}... Error: {error}")
        
        return {
            "risk_summary": "Risk assessment temporarily unavailable",
            "risk_level": "unknown", 
            "primary_risks": [],
            "confidence": 0.0,
            "evidence_used": [],
            "warnings": ["processing_error", f"error: {error}"],
            "monitoring_recommendations": ["Manual risk review recommended"],
            "processing_time_ms": 0,
            "cached": False,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    # Status and health check methods
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all pipeline components"""
        health_status = {
            "overall": "healthy",
            "components": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # Check vector store
            health_status["components"]["vector_store"] = await self._check_vector_store()
            
            # Check database
            health_status["components"]["database"] = await self._check_database()
            
            # Check cache
            health_status["components"]["cache"] = self._check_cache()
            
            # Check LLM
            health_status["components"]["llm"] = await self._check_llm()
            
            # Overall health
            unhealthy_components = [name for name, status in health_status["components"].items() 
                                  if status.get("status") != "healthy"]
            
            if unhealthy_components:
                health_status["overall"] = "degraded"
                health_status["unhealthy_components"] = unhealthy_components
            
        except Exception as e:
            health_status["overall"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status
    
    async def _check_vector_store(self) -> Dict[str, Any]:
        """Check vector store health"""
        try:
            # Simple test query
            test_results = self.vector_store.query_documents(
                query_texts=["test"], 
                n_results=1
            )
            result_count = len(test_results.get('documents', [[]])[0]) if test_results else 0
            return {"status": "healthy", "document_count": result_count}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            result = await self.db_manager.async_execute_query("SELECT 1 as test")
            return {"status": "healthy", "connection": "active"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def _check_cache(self) -> Dict[str, Any]:
        """Check cache connectivity"""
        try:
            # Since we're using no-cache implementation, just return healthy status
            return {"status": "healthy", "connection": "n/a", "cache_type": "no_cache"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def _check_llm(self) -> Dict[str, Any]:
        """Check LLM availability"""
        try:
            # Simple test assessment
            test_evidence = {"vector_evidence": [], "db_features": {}}
            test_result = await asyncio.wait_for(
                self.risk_llm.assess_risk(test_evidence, "test query", {}),
                timeout=2.0
            )
            return {"status": "healthy", "model": self.risk_llm.model}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def close(self):
        """Close underlying resources (LLM sessions, etc.).

        Call this at application shutdown to ensure aiohttp sessions are closed
        and avoid "Unclosed client session" warnings.
        """
        try:
            if hasattr(self, 'risk_llm') and self.risk_llm is not None:
                await self.risk_llm.close()
                logger.info("RiskAssessmentPipeline closed LLM resources")
        except Exception as e:
            logger.warning(f"Error closing pipeline resources: {e}")
    
    async def _assess_risk_with_centralized_llm(self, evidence: Dict[str, Any], query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk using centralized LLM manager with risk-specific prompts"""
        
        # Import risk system prompt from risk_llm module
        from .risk_llm import RISK_SYSTEM_PROMPT, RISK_USER_PROMPT_TEMPLATE
        
        try:
            # Build context prompt using the same logic as RiskAssessmentLLM
            context = self._build_risk_context_for_centralized_llm(evidence, query, params)
            
            # Generate response using centralized LLM
            response_text = await self.llm_manager.generate(
                prompt=context,
                system_prompt=RISK_SYSTEM_PROMPT
            )
            
            # Parse and validate the JSON response
            risk_assessment = self._parse_risk_response(response_text, evidence)
            
            logger.info(f"Risk assessment completed using centralized LLM for query: {query[:50]}...")
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Centralized LLM risk assessment error: {str(e)}")
            return self._generate_fallback_risk_response(evidence, str(e))
    
    def _build_risk_context_for_centralized_llm(self, evidence: Dict[str, Any], query: str, params: Dict[str, Any]) -> str:
        """Build comprehensive context for risk assessment using centralized LLM"""
        
        # Format vector evidence
        vector_evidence = evidence.get("vector_evidence", [])
        vector_evidence_text = self._format_vector_evidence_for_llm(vector_evidence)
        
        # Format database features
        db_features = evidence.get("db_features", {})
        db_features_text = self._format_db_features_for_llm(db_features)
        
        # Format risk summary
        risk_summary = evidence.get("risk_summary", {})
        risk_summary_text = self._format_risk_summary_for_llm(risk_summary)
        
        # Import the template from risk_llm
        from .risk_llm import RISK_USER_PROMPT_TEMPLATE
        
        context = RISK_USER_PROMPT_TEMPLATE.format(
            query=query,
            ticker=params.get("ticker", "GENERAL"),
            time_window=params.get("time_window", "7d"),
            vector_count=len(vector_evidence),
            vector_evidence=vector_evidence_text,
            db_features=db_features_text,
            risk_summary=risk_summary_text
        )
        
        return context
    
    def _format_vector_evidence_for_llm(self, vector_evidence: List) -> str:
        """Format vector evidence for LLM context"""
        if not vector_evidence:
            return "No vector evidence available."
        
        formatted = []
        for i, item in enumerate(vector_evidence[:10], 1):  # Limit to top 10
            if hasattr(item, 'page_content') and hasattr(item, 'metadata'):
                risk_type = item.metadata.get("risk_type", "unknown")
                severity = item.metadata.get("severity", "low")
                timestamp = item.metadata.get("timestamp", "unknown")
                ticker = item.metadata.get("ticker", "general")
                
                formatted.append(f"{i}. Risk Type: {risk_type} | Severity: {severity} | Asset: {ticker} | Time: {timestamp}")
                formatted.append(f"   Content: {item.page_content[:200]}...")
                formatted.append("")
        
        return "\n".join(formatted) if formatted else "No relevant vector evidence found."
    
    def _format_db_features_for_llm(self, db_features: Dict[str, Any]) -> str:
        """Format database features for LLM context"""
        if not db_features or db_features.get("error"):
            return f"Database features unavailable: {db_features.get('error', 'Unknown error')}"
        
        formatted = []
        
        # Current anomalies
        current_anomalies = db_features.get("current_anomalies", [])
        if current_anomalies:
            formatted.append(f"Current Anomalies: {len(current_anomalies)} active")
            for anomaly in current_anomalies[:3]:  # Top 3
                ticker = anomaly.get("ticker", "unknown")
                severity = anomaly.get("severity", "low") 
                timestamp = anomaly.get("timestamp", "unknown")
                formatted.append(f"  - {ticker}: {severity} severity at {timestamp}")
        
        # Active incidents
        incidents = db_features.get("active_incidents", [])
        if incidents:
            formatted.append(f"Active Incidents: {len(incidents)} ongoing")
            for incident in incidents[:3]:  # Top 3
                incident_type = incident.get("incident_type", "unknown")
                status = incident.get("status", "unknown")
                formatted.append(f"  - {incident_type}: {status}")
        
        # Regulatory events
        regulatory = db_features.get("regulatory_events", [])
        if regulatory:
            formatted.append(f"Regulatory Events: {len(regulatory)} recent")
            for event in regulatory[:3]:  # Top 3
                event_type = event.get("event_type", "unknown")
                impact = event.get("impact_level", "low")
                formatted.append(f"  - {event_type}: {impact} impact")
        
        # Active alerts
        alerts = db_features.get("active_alerts", [])
        if alerts:
            formatted.append(f"Active Alerts: {len(alerts)} current")
        
        return "\n".join(formatted) if formatted else "No database features available."
    
    def _format_risk_summary_for_llm(self, risk_summary: Dict[str, Any]) -> str:
        """Format risk summary for LLM context"""
        if not risk_summary:
            return "No risk summary available."
        
        formatted = []
        for risk_type, data in risk_summary.items():
            count = data.get("count", 0)
            max_severity = data.get("max_severity", "low")
            if count > 0:
                formatted.append(f"{risk_type.upper()}: {count} items, max severity: {max_severity}")
        
        return "\n".join(formatted) if formatted else "No risk patterns detected in evidence."
    
    def _parse_risk_response(self, response_text: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate LLM response for risk assessment"""
        import json
        from datetime import datetime, timezone
        
        try:
            # Try to parse as JSON
            response = json.loads(response_text)
        except json.JSONDecodeError:
            # If not valid JSON, try to extract JSON from text
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    response = json.loads(json_match.group())
                except json.JSONDecodeError:
                    response = self._create_fallback_response(response_text)
            else:
                response = self._create_fallback_response(response_text)
        
        # Validate and clean the response
        response = self._validate_and_clean_risk_response(response, evidence)
        
        # Add metadata
        response["assessment_timestamp"] = datetime.now(timezone.utc).isoformat()
        response["model_used"] = "centralized_llm_manager"
        
        return response
    
    def _validate_and_clean_risk_response(self, response: Dict[str, Any], evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the risk response structure"""
        
        # Ensure required fields exist
        required_fields = {
            "risk_summary": "Risk assessment using available evidence",
            "risk_level": "medium", 
            "primary_risks": [],
            "confidence": 0.5,
            "monitoring_recommendations": ["Continue regular monitoring"],
            "evidence_used": [],
            "warnings": []
        }
        
        for field, default_value in required_fields.items():
            if field not in response:
                response[field] = default_value
        
        # Validate risk_level
        valid_levels = {"high", "medium", "low", "unknown"}
        if response.get("risk_level") not in valid_levels:
            response["risk_level"] = "medium"
        
        # Ensure primary_risks is a list
        if not isinstance(response.get("primary_risks"), list):
            response["primary_risks"] = []
        
        # Validate confidence range
        confidence = response.get("confidence", 0.5)
        if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
            response["confidence"] = 0.5
        
        # Calculate risk score
        response["risk_score"] = self._calculate_risk_score_from_response(response, evidence)
        
        return response
    
    def _calculate_risk_score_from_response(self, response: Dict[str, Any], evidence: Dict[str, Any]) -> float:
        """Calculate numerical risk score from response and evidence"""
        
        score = 0
        
        # Score based on risk level
        risk_level = response.get("risk_level", "medium").lower()
        level_scores = {"high": 7, "medium": 4, "low": 2, "unknown": 3}
        score += level_scores.get(risk_level, 3)
        
        # Score based on primary risks
        primary_risks = response.get("primary_risks", [])
        for risk in primary_risks:
            if isinstance(risk, dict):
                severity = risk.get("severity", "low").lower()
                risk_points = {"high": 2, "medium": 1, "low": 0.5}
                score += risk_points.get(severity, 0.5)
        
        # Score based on evidence strength
        vector_evidence = evidence.get("vector_evidence", [])
        score += min(len(vector_evidence) * 0.1, 1.0)  # Cap evidence boost at 1.0
        
        # Confidence adjustment
        confidence = response.get("confidence", 0.5)
        score *= (0.6 + confidence * 0.4)  # Scale by confidence
        
        return round(min(score, 10.0), 1)  # Cap at 10.0
    
    def _create_fallback_response(self, response_text: str) -> Dict[str, Any]:
        """Create a fallback response when JSON parsing fails"""
        return {
            "risk_summary": response_text[:200] + "..." if len(response_text) > 200 else response_text,
            "risk_level": "medium",
            "primary_risks": [
                {
                    "type": "general",
                    "severity": "medium", 
                    "description": "Risk assessment based on available evidence",
                    "confidence": 0.6
                }
            ],
            "confidence": 0.6,
            "monitoring_recommendations": ["Continue monitoring based on available evidence"],
            "evidence_used": [],
            "warnings": ["text_response_parsed"]
        }
    
    def _generate_fallback_risk_response(self, evidence: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Generate fallback response when LLM fails"""
        return {
            "risk_summary": "Risk assessment temporarily unavailable due to processing error",
            "risk_level": "unknown",
            "primary_risks": [],
            "confidence": 0.0,
            "evidence_used": [],
            "warnings": ["llm_processing_error", f"error: {error}"],
            "monitoring_recommendations": ["Manual risk assessment recommended"],
            "assessment_timestamp": datetime.now(timezone.utc).isoformat(),
            "model_used": "centralized_llm_manager"
        }
