"""
Risk Assessment LLM - Language Model Integration for Risk Analysis

This module handles LLM integration for risk assessment, including:
- Risk-specific prompt templates and system prompts
- JSON schema validation and enforcement
- Confidence scoring and post-processing
- Fallback handling for LLM failures
"""

import json
import logging
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import pandas as pd

logger = logging.getLogger(__name__)

# Risk-specific prompt templates
RISK_SYSTEM_PROMPT = """
You are a financial risk assessment specialist. Analyze the provided evidence to identify and classify multi-layer risks.

INSTRUCTIONS:
1. Use ONLY the provided evidence - never make assumptions
2. Classify risks into: infrastructure, regulatory, sentiment, liquidity
3. Assign severity levels: high, medium, low based on evidence strength
4. Provide monitoring recommendations - NEVER trading advice
5. Cite specific evidence for each risk identified
6. Output ONLY valid JSON matching the schema

RISK ASSESSMENT PRINCIPLES:
- Infrastructure incidents = immediate high-priority risks
- Regulatory changes = systemic risks affecting multiple assets
- Sentiment risks = market perception and confidence issues
- Liquidity risks = trading and execution concerns

If evidence is insufficient, explicitly state "insufficient evidence" for that risk type.

JSON SCHEMA:
{
  "risk_summary": "string - comprehensive risk overview",
  "risk_level": "high|medium|low - overall risk classification",
  "primary_risks": [
    {
      "type": "infra|regulatory|sentiment|liquidity",
      "severity": "high|medium|low",
      "description": "string - detailed risk description",
      "confidence": 0.0-1.0
    }
  ],
  "monitoring_recommendations": ["string array of monitoring suggestions"],
  "evidence_used": [
    {
      "source": "string - evidence source",
      "risk_type": "string - type of risk",
      "snippet": "string - relevant excerpt",
      "confidence": 0.0-1.0
    }
  ],
  "confidence": 0.0-1.0,
  "warnings": ["string array of data quality warnings"]
}
"""

RISK_USER_PROMPT_TEMPLATE = """
    RISK ASSESSMENT REQUEST:
    Query: {query}
    Asset: {ticker}
    Time Window: {time_window}

    EVIDENCE PROVIDED:

    Vector Evidence ({vector_count} items):
    {vector_evidence}

    Database Features:
    {db_features}

    Risk Summary from Evidence:
    {risk_summary}

    TASK: Provide comprehensive multi-layer risk assessment in JSON format following the exact schema.
    Focus on the query context and use evidence to support your analysis.
    """

class RiskAssessmentLLM:
    """Language Model integration for risk assessment"""
    
    def __init__(self, model_name: str = "llama3.1:latest", temperature: float = 0.1):
        self.model = model_name
        self.temperature = temperature
        self.max_tokens = 1500
        self.max_retries = 2
        
        # Initialize persistent HTTP session for faster requests
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=35))
        
        # Initialize local LLM client (Ollama)
        try:
            self.use_ollama = True
            self.ollama_url = "http://localhost:11434/api/chat"  # Use chat endpoint
            # Test connection with simple requests first
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                logger.info(f"RiskAssessmentLLM initialized with local model: {model_name}")
            else:
                raise Exception("Ollama not accessible")
        except Exception as e:
            logger.warning(f"Ollama not available ({e}), falling back to mock responses")
            self.use_ollama = False
    
    async def assess_risk(self, evidence: Dict[str, Any], query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate risk assessment using LLM
        
        Args:
            evidence: Compiled evidence from vector store, ML signals, and DB
            query: Original risk query
            params: Risk assessment parameters
            
        Returns:
            Risk assessment response in JSON format
        """
        try:
            # Build context prompt
            context = self._build_risk_context(evidence, query, params)
            
            # LLM call with JSON schema enforcement
            response = await self._call_llm_with_schema_validation(context)
            
            # Post-process and validate
            risk_assessment = self._post_process_risk_response(response, evidence)
            
            logger.info(f"Risk assessment completed for query: {query[:50]}...")
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Risk assessment LLM error: {str(e)}")
            return self._generate_fallback_response(evidence, str(e))
    
    def _build_risk_context(self, evidence: Dict[str, Any], query: str, params: Dict[str, Any]) -> str:
        """Build comprehensive context for risk assessment"""
        
        # Format vector evidence
        vector_evidence = evidence.get("vector_evidence", [])
        vector_evidence_text = self._format_vector_evidence(vector_evidence)
        
        # Format database features
        db_features = evidence.get("db_features", {})
        db_features_text = self._format_db_features(db_features)
        
        # Format risk summary
        risk_summary = evidence.get("risk_summary", {})
        risk_summary_text = self._format_risk_summary(risk_summary)
        
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
    
    def _format_vector_evidence(self, vector_evidence: List) -> str:
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
    
    def _format_db_features(self, db_features: Dict[str, Any]) -> str:
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
    
    def _format_risk_summary(self, risk_summary: Dict[str, Any]) -> str:
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
    
    async def _call_llm_with_schema_validation(self, context: str) -> Dict[str, Any]:
        """Call local LLM (Ollama) with schema validation using persistent session"""
        
        if not self.use_ollama:
            # Mock response for testing
            return self._generate_mock_response()
        
        # Initialize persistent session if needed
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        
        # Format for Ollama chat API with optimized keep-alive
        for attempt in range(self.max_retries):
            try:
                payload = {
                    "model": "llama3.1:latest",
                    "messages": [
                        {
                            "role": "system", 
                            "content": RISK_SYSTEM_PROMPT
                        },
                        {
                            "role": "user", 
                            "content": context
                        }
                    ],
                    "stream": False,
                    "keep_alive": "20m",  # Extended keep-alive for faster repeated queries
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens
                    }
                }
                
                # Use persistent aiohttp session for faster HTTP reuse
                async with self.session.post(self.ollama_url, json=payload) as response:
                    response.raise_for_status()
                    json_response = await response.json()
                    
                    # Parse Ollama chat response format
                    message = json_response.get("message", {})
                    result_text = message.get("content", "")
                    
                    if not result_text:
                        raise ValueError("No content received from LLM")
                    
                    logger.debug(f"LLM raw response: {result_text[:200]}...")
                
                # Try to parse JSON response
                try:
                    result = json.loads(result_text)
                except json.JSONDecodeError:
                    # If not valid JSON, try to extract JSON from text
                    import re
                    json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
                    else:
                        # Generate structured response from text
                        result = self._parse_text_to_json(result_text)
                
                # Validate schema
                if self._validate_risk_schema(result):
                    return result
                else:
                    logger.warning(f"Schema validation failed for result: {result}")
                    return self._generate_mock_response()
                    
            except Exception as e:
                logger.warning(f"LLM response error (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    # Return fallback response
                    return self._generate_mock_response()
                else:
                    # Brief delay before retry
                    await asyncio.sleep(0.5)
        
        return self._generate_mock_response()
    
    def _validate_risk_schema(self, response: Dict[str, Any]) -> bool:
        """Validate risk assessment response schema"""
        required_fields = ["risk_summary", "risk_level", "primary_risks", "confidence"]
        
        # Check required fields
        if not all(field in response for field in required_fields):
            return False
        
        # Validate risk_level values
        valid_levels = {"high", "medium", "low", "unknown", "insufficient"}
        if response.get("risk_level") not in valid_levels:
            # Fix common invalid values
            risk_level = response.get("risk_level", "unknown").lower()
            if "insufficient" in risk_level or "unavailable" in risk_level:
                response["risk_level"] = "low"  # Treat insufficient as low risk
            else:
                response["risk_level"] = "unknown"
        
        # Validate primary_risks structure
        primary_risks = response.get("primary_risks", [])
        if not isinstance(primary_risks, list):
            return False
        
        for risk in primary_risks:
            if not isinstance(risk, dict):
                return False
            required_risk_fields = ["type", "severity", "description"]
            if not all(field in risk for field in required_risk_fields):
                return False
        
        # Validate confidence range
        confidence = response.get("confidence", 0)
        if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
            return False
        
        return True
    
    def _post_process_risk_response(self, response: Dict[str, Any], evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process and enrich risk assessment"""
        
        # Calculate confidence score if not provided
        if "confidence" not in response or response["confidence"] == 0:
            response["confidence"] = self._calculate_confidence(response, evidence)
        
        # Calculate numerical risk score based on risk level and primary risks
        response["risk_score"] = self._calculate_risk_score(response, evidence)
        
        # Add warnings based on evidence quality
        warnings = self._generate_warnings(evidence, response)
        if warnings:
            existing_warnings = response.get("warnings", [])
            response["warnings"] = list(set(existing_warnings + warnings))
        
        # Ensure monitoring recommendations exist
        if "monitoring_recommendations" not in response or not response["monitoring_recommendations"]:
            response["monitoring_recommendations"] = self._generate_monitoring_recommendations(response)
        
        # Add evidence used summary
        if "evidence_used" not in response:
            response["evidence_used"] = self._generate_evidence_summary(evidence)
        
        # Add metadata
        response["assessment_timestamp"] = datetime.now(timezone.utc).isoformat()
        response["model_used"] = self.model
        
        return response
    
    def _calculate_confidence(self, response: Dict[str, Any], evidence: Dict[str, Any]) -> float:
        """Calculate composite confidence score"""
        
        # Evidence density (40%)
        vector_evidence = evidence.get("vector_evidence", [])
        evidence_density = min(1.0, len(vector_evidence) / 10)  # Normalize to max 10 pieces
        
        # Signal strength (30%) - simplified without ML
        signal_strength = 0.5  # Default moderate signal strength based on database features
        
        # Cross-source agreement (30%)
        primary_risks = response.get("primary_risks", [])
        risk_types_found = set(risk.get("type") for risk in primary_risks)
        agreement_score = len(risk_types_found) / 4.0  # 4 risk types max
        
        # Composite confidence
        confidence = (
            0.4 * evidence_density +
            0.3 * signal_strength +
            0.3 * agreement_score
        )
        
        return round(min(1.0, max(0.1, confidence)), 2)  # Ensure 0.1-1.0 range
    
    def _calculate_risk_score(self, response: Dict[str, Any], evidence: Dict[str, Any]) -> float:
        """Calculate numerical risk score from 0.0 to 10.0 based on evidence severity"""
        
        # New evidence-based scoring system
        score = 0
        
        # Score based on vector evidence severity (main scoring component)
        vector_evidence = evidence.get("vector_evidence", [])
        for evidence_item in vector_evidence:
            if hasattr(evidence_item, 'metadata'):
                severity = evidence_item.metadata.get("severity", "low").lower()
                # High severity = +40 points, Medium = +20, Low = +10
                severity_points = {
                    'high': 40,
                    'critical': 50,
                    'medium': 20,
                    'low': 10
                }.get(severity, 5)
                score += severity_points
                
                # Recency boost for evidence < 7 days old
                timestamp_str = evidence_item.metadata.get("timestamp", "")
                if timestamp_str:
                    try:
                        import pandas as pd
                        evidence_time = pd.to_datetime(timestamp_str)
                        days_ago = (datetime.now(timezone.utc) - evidence_time).days
                        if days_ago < 7:
                            # Fresh evidence gets +5 bonus
                            score += 5
                    except:
                        pass
        
        # Score based on primary risks from LLM analysis
        primary_risks = response.get("primary_risks", [])
        for risk in primary_risks:
            severity = risk.get("severity", "low").lower()
            risk_points = {
                'high': 15,
                'critical': 20, 
                'medium': 8,
                'low': 3
            }.get(severity, 2)
            score += risk_points
        
        # Database features influence
        db_features = evidence.get("db_features", {})
        if db_features and not db_features.get("error"):
            # Active incidents are high-impact
            active_incidents = len(db_features.get("active_incidents", []))
            score += active_incidents * 12
            
            # Current anomalies add moderate risk
            current_anomalies = len(db_features.get("current_anomalies", []))
            score += current_anomalies * 6
            
            # Active alerts add minor risk
            active_alerts = len(db_features.get("active_alerts", []))
            score += active_alerts * 3
        
        # Convert to 0-10 scale (cap at 100 points = 10.0)
        normalized_score = min(score / 10.0, 10.0)
        
        # Confidence adjustment (low confidence reduces score)
        confidence = response.get("confidence", 0.5)
        confidence_factor = 0.6 + (confidence * 0.4)  # Range: 0.6 to 1.0
        
        final_score = normalized_score * confidence_factor
        
        # Ensure minimum score if any evidence exists
        if vector_evidence or primary_risks:
            final_score = max(final_score, 0.5)
        
        return round(max(0.0, min(10.0, final_score)), 1)

    def _generate_warnings(self, evidence: Dict[str, Any], response: Dict[str, Any]) -> List[str]:
        """Generate warnings based on evidence and response quality"""
        warnings = []
        
        # Evidence quality warnings
        vector_evidence = evidence.get("vector_evidence", [])
        if len(vector_evidence) < 3:
            warnings.append("limited_evidence_available")
        
        db_features = evidence.get("db_features", {})
        if db_features.get("error") or not db_features:
            warnings.append("database_features_unavailable")
        
        # Response quality warnings
        confidence = response.get("confidence", 0)
        if confidence < 0.5:
            warnings.append("low_confidence_assessment")
        
        primary_risks = response.get("primary_risks", [])
        if not primary_risks:
            warnings.append("no_specific_risks_identified")
        
        # Evidence freshness check
        fresh_evidence = 0
        for item in vector_evidence:
            if hasattr(item, 'metadata') and item.metadata.get("timestamp"):
                try:
                    timestamp = pd.to_datetime(item.metadata["timestamp"])
                    if (datetime.now(timezone.utc) - timestamp).total_seconds() < 86400:  # 24 hours
                        fresh_evidence += 1
                except:
                    pass
        
        if fresh_evidence < 2:
            warnings.append("stale_evidence_warning")
        
        return warnings
    
    def _generate_monitoring_recommendations(self, response: Dict[str, Any]) -> List[str]:
        """Generate monitoring recommendations based on identified risks"""
        recommendations = []
        
        primary_risks = response.get("primary_risks", [])
        for risk in primary_risks:
            risk_type = risk.get("type", "")
            severity = risk.get("severity", "low")
            
            if risk_type == "infra" and severity in ["high", "medium"]:
                recommendations.append("Monitor infrastructure status feeds and API health")
            elif risk_type == "regulatory" and severity in ["high", "medium"]:
                recommendations.append("Track regulatory announcements and policy changes")
            elif risk_type == "sentiment" and severity == "high":
                recommendations.append("Monitor news sentiment and social media indicators")
            elif risk_type == "liquidity" and severity in ["high", "medium"]:
                recommendations.append("Watch bid-ask spreads and trading volume patterns")
        
        if not recommendations:
            recommendations.append("Continue regular risk monitoring across all categories")
        
        return recommendations
    
    def _generate_evidence_summary(self, evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate evidence used summary for response"""
        evidence_summary = []
        
        # Vector evidence summary
        vector_evidence = evidence.get("vector_evidence", [])
        for item in vector_evidence[:5]:  # Top 5
            if hasattr(item, 'page_content') and hasattr(item, 'metadata'):
                evidence_summary.append({
                    "source": "vector_database",
                    "risk_type": item.metadata.get("risk_type", "unknown"),
                    "snippet": item.page_content[:100] + "..." if len(item.page_content) > 100 else item.page_content,
                    "timestamp": item.metadata.get("timestamp", "unknown"),
                    "confidence": item.metadata.get("score", 0.7)
                })
        
        # ML signals summary
        ml_signals = evidence.get("ml_signals", {})
        if ml_signals and not ml_signals.get("error"):
            anomalies = ml_signals.get("anomalies", [])
            if anomalies:
                evidence_summary.append({
                    "source": "anomaly_detector",
                    "risk_type": "technical",
                    "snippet": f"{len(anomalies)} anomalies detected in recent period",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "confidence": 0.8
                })
        
        return evidence_summary
    
    def _generate_mock_response(self) -> Dict[str, Any]:
        """Generate mock response for testing or LLM failures"""
        return {
            "risk_summary": "Risk assessment using available evidence",
            "risk_level": "medium",
            "primary_risks": [
                {
                    "type": "infra",
                    "severity": "medium", 
                    "description": "General infrastructure monitoring recommended",
                    "confidence": 0.5
                }
            ],
            "confidence": 0.5,
            "evidence_used": [],
            "monitoring_recommendations": ["Continue regular monitoring"],
            "warnings": ["mock_response_generated"]
        }
    
    def _generate_fallback_response(self, evidence: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Generate minimal fallback response when LLM fails"""
        return {
            "risk_summary": "Risk assessment temporarily unavailable due to processing error",
            "risk_level": "unknown",
            "primary_risks": [],
            "confidence": 0.0,
            "evidence_used": [],
            "warnings": ["llm_processing_error", f"error: {error}"],
            "monitoring_recommendations": ["Manual risk assessment recommended"],
            "assessment_timestamp": datetime.now(timezone.utc).isoformat(),
            "model_used": self.model
        }
    
    def _parse_text_to_json(self, text: str) -> Dict[str, Any]:
        """Parse plain text response into JSON structure"""
        try:
            # Simple fallback parsing for non-JSON responses
            return {
                "risk_summary": text[:200] + "..." if len(text) > 200 else text,
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
                "evidence_used": [],
                "monitoring_recommendations": ["Continue monitoring based on available evidence"],
                "warnings": ["text_response_parsed"]
            }
        except Exception:
            return self._generate_mock_response()

    async def close(self):
        """Close the underlying HTTP session used for Ollama requests.

        Call this at application shutdown or when the LLM will no longer be used to
        ensure the aiohttp client session is cleanly closed and the model can remain
        loaded in Ollama when using the keep_alive option.
        """
        try:
            if hasattr(self, 'session') and self.session is not None and not self.session.closed:
                await self.session.close()
                logger.info("RiskAssessmentLLM HTTP session closed")
        except Exception as e:
            logger.warning(f"Error closing RiskAssessmentLLM session: {e}")
