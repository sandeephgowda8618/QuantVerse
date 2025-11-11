# RAG LLM Pipeline Implementation Plan - RISK Mode Focus

**Project**: uRISK Financial Risk Analysis Pipeline  
**Focus**: RISK Mode Implementation (Multi-layered Risk Monitor)  
**Integration**: ML Signals + Vector Database + PostgreSQL  
**Date**: November 9, 2025  

---

## 🎯 **IMPLEMENTATION SCOPE**

### **Primary Responsibility: RISK Mode**
- Multi-layered risk monitoring and analysis
- Infrastructure, regulatory, sentiment, and liquidity risk detection
- ML-integrated anomaly detection and scoring
- Real-time risk assessment with evidence-based responses

### **Team Division:**
- **Our Implementation**: RISK mode (infra/systemic risk module)
- **Teammate 1**: MOVE mode (sudden move explainer)  
- **Teammate 2**: OPTIONS mode (options flow analysis)
- **Teammate 3**: MACRO mode (macro-driven gaps)

---

## 🏗️ **ARCHITECTURE OVERVIEW**

### **0) One-Liner for RISK Pipeline:**
"Query → Risk Filter → ML Anomaly Signals → Retrieve Evidence → Risk Assessment → JSON Response" with multi-layer risk detection (infra, regulatory, sentiment, liquidity) and severity classification.

### **1) RISK Mode Control Plane**

#### **1.1 Intent Router (RISK-Specific)**
```python
# Input Processing for RISK queries
Inputs: 
- text: risk-related query
- optional ticker/asset: specific asset focus
- optional timestamp: risk window analysis
- mode: "RISK" (or auto-detected)

# RISK Classification Logic
Sub-categories:
- infra_risk: infrastructure incidents, outages
- regulatory_risk: compliance, policy changes
- sentiment_risk: negative sentiment spikes
- liquidity_risk: spread anomalies, volume drops

# Output
Returns: {
    "mode": "RISK",
    "risk_types": ["infra", "regulatory", "sentiment", "liquidity"],
    "ticker": Optional[str],
    "time_window": "7d",  # default
    "severity_threshold": "medium"
}
```

#### **1.2 RISK Execution Orchestrator**
```python
# RISK Pipeline Components
Given RISK mode request:

1. ML Signals Fetcher:
   - Anomaly detector outputs (volume/liquidity/volatility)
   - Sentiment classifier scores
   - Infrastructure status feeds
   - Regulatory event flags

2. Vector Retriever (ChromaDB):
   - Filter: risk_type in ["infra","regulatory","sentiment","liquidity"]
   - Time window: timestamp >= now-7d
   - Severity: {med, high}
   - Ticker-specific if provided

3. Database Features (PostgreSQL):
   - Latest anomalies table queries
   - Unresolved incidents
   - Liquidity spreads
   - Status feed updates

4. Risk Assessment LLM:
   - Multi-risk prompt template
   - Evidence synthesis
   - Severity classification
   - Monitoring recommendations

5. Response Post-Processor:
   - Risk score calculation
   - Evidence ranking
   - Compliance checks
   - Alert generation
```

#### **1.3 RISK Response Contract**
```json
{
  "risk_summary": "Multi-layer risk assessment summary",
  "risk_level": "high|medium|low",
  "primary_risks": [
    {
      "type": "infra|regulatory|sentiment|liquidity",
      "severity": "high|medium|low",
      "description": "Risk description",
      "confidence": 0.85
    }
  ],
  "monitoring_recommendations": [
    "Monitor NVDA infrastructure status",
    "Watch for regulatory announcements"
  ],
  "evidence_used": [
    {
      "source": "anomaly_detector",
      "timestamp": "2025-11-09T21:00:00Z",
      "snippet": "Volume anomaly detected: 3.2σ above normal",
      "risk_type": "liquidity",
      "severity": "high"
    }
  ],
  "confidence": 0.78,
  "warnings": ["limited_sentiment_data", "infrastructure_status_stale"]
}
```

---

## 🗄️ **DATA PLANE INTEGRATION**

### **2) RISK-Specific Data Sources**

#### **PostgreSQL Tables (Source of Truth)**
```sql
-- Primary risk data tables
anomalies: volume, liquidity, volatility anomalies
infra_incidents: system outages, API failures
regulatory_events: policy announcements, compliance alerts
news_sentiment: sentiment scores, negative spikes
market_data: spreads, volumes, price gaps
alerts: active risk alerts and status

-- Risk-specific queries
SELECT * FROM anomalies 
WHERE ticker = ? AND severity IN ('medium', 'high')
AND timestamp >= NOW() - INTERVAL '7 days';

SELECT * FROM infra_incidents 
WHERE status = 'active' OR resolved_at >= NOW() - INTERVAL '1 day';
```

#### **ChromaDB Semantic Search (urisk_chunks)**
```python
# RISK-focused vector search
risk_filters = {
    "risk_type": {"$in": ["infra", "regulatory", "sentiment", "liquidity"]},
    "timestamp": {"$gte": seven_days_ago},
    "severity": {"$in": ["medium", "high"]}
}

if ticker:
    risk_filters["ticker"] = ticker

# Vector similarity search with risk context
risk_chunks = vector_store.similarity_search(
    query=risk_query,
    filter=risk_filters,
    k=15,  # Get more candidates for re-ranking
    score_threshold=0.7
)
```

#### **ML Signal Integration**
```python
# Real-time ML signals for RISK assessment
ml_signals = {
    "anomaly_scores": get_anomaly_signals(ticker, window="1h"),
    "sentiment_trend": get_sentiment_trend(ticker, window="24h"), 
    "liquidity_health": get_liquidity_metrics(ticker),
    "infra_status": get_infrastructure_status(),
    "regulatory_calendar": get_upcoming_events(window="7d")
}

# Risk signal weighting
risk_weight = (
    0.3 * anomaly_scores.max() +
    0.25 * abs(sentiment_trend) +
    0.2 * (1 - liquidity_health) +
    0.15 * infra_incident_count +
    0.1 * regulatory_event_proximity
)
```

---

## 🔍 **RISK RETRIEVAL STRATEGY**

### **3) Multi-Layer Risk Detection**

#### **3.1 Filter-First Approach**
```python
def risk_filter_strategy(query, params):
    """Apply progressive filtering for risk detection"""
    
    # Base risk filters
    base_filters = {
        "risk_type": {"$in": ["infra", "regulatory", "sentiment", "liquidity"]},
        "timestamp": {"$gte": datetime.now() - timedelta(days=7)},
        "severity": {"$in": ["medium", "high"]}
    }
    
    # Asset-specific filtering
    if params.get("ticker"):
        base_filters["ticker"] = params["ticker"]
    
    # Severity escalation
    if params.get("high_priority"):
        base_filters["severity"] = "high"
        base_filters["timestamp"]["$gte"] = datetime.now() - timedelta(days=3)
    
    return base_filters
```

#### **3.2 Risk Ranking Algorithm**
```python
def risk_ranking_boost(chunks, ml_signals):
    """Apply risk-specific ranking boosts"""
    
    ranking_weights = {
        "infra": 1.0,      # Infrastructure incidents = highest priority
        "regulatory": 0.85, # Regulatory changes = high priority  
        "sentiment": 0.7,   # Negative sentiment = medium priority
        "liquidity": 0.6    # Liquidity issues = medium priority
    }
    
    for chunk in chunks:
        base_score = chunk.similarity_score
        
        # Risk type boost
        risk_boost = ranking_weights.get(chunk.metadata["risk_type"], 0.5)
        
        # ML signal boost
        ml_boost = 1.0
        if chunk.metadata["risk_type"] == "infra":
            ml_boost += ml_signals.get("infra_severity", 0) * 0.3
        elif chunk.metadata["risk_type"] == "sentiment":
            ml_boost += abs(ml_signals.get("sentiment_score", 0)) * 0.2
        
        # Recency boost (more recent = higher priority)
        hours_old = (datetime.now() - chunk.timestamp).total_seconds() / 3600
        recency_boost = max(0.1, 1.0 - (hours_old / 168))  # 168h = 7 days
        
        # Final risk score
        chunk.risk_score = base_score * risk_boost * ml_boost * recency_boost
    
    return sorted(chunks, key=lambda x: x.risk_score, reverse=True)[:10]
```

#### **3.3 Multi-Source Evidence Gathering**
```python
def gather_risk_evidence(ranked_chunks, ml_signals, db_features):
    """Compile comprehensive risk evidence"""
    
    evidence = {
        "vector_evidence": [],
        "ml_signals": ml_signals,
        "db_features": db_features,
        "risk_summary": {
            "infra": {"count": 0, "max_severity": "low"},
            "regulatory": {"count": 0, "max_severity": "low"},
            "sentiment": {"count": 0, "max_severity": "low"},
            "liquidity": {"count": 0, "max_severity": "low"}
        }
    }
    
    for chunk in ranked_chunks:
        risk_type = chunk.metadata["risk_type"]
        severity = chunk.metadata["severity"]
        
        # Add to evidence
        evidence["vector_evidence"].append({
            "source": chunk.metadata["source"],
            "risk_type": risk_type,
            "severity": severity,
            "snippet": chunk.text[:200],
            "timestamp": chunk.metadata["timestamp"],
            "confidence": chunk.risk_score
        })
        
        # Update risk summary
        evidence["risk_summary"][risk_type]["count"] += 1
        if severity == "high":
            evidence["risk_summary"][risk_type]["max_severity"] = "high"
        elif severity == "medium" and evidence["risk_summary"][risk_type]["max_severity"] == "low":
            evidence["risk_summary"][risk_type]["max_severity"] = "medium"
    
    return evidence
```

---

## 🤖 **RISK REASONING STRATEGY**

### **4) LLM Integration for Risk Assessment**

#### **4.1 Risk-Specific Prompt Template**
```python
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
"""

RISK_USER_PROMPT_TEMPLATE = """
RISK ASSESSMENT REQUEST:
Query: {query}
Asset: {ticker}
Time Window: {time_window}

EVIDENCE PROVIDED:
Vector Evidence: {vector_evidence}
ML Signals: {ml_signals}
Database Features: {db_features}

TASK: Provide comprehensive multi-layer risk assessment in JSON format.
"""
```

#### **4.2 Risk Assessment LLM Pipeline**
```python
import json
from typing import Dict, List, Any
import openai  # or local LLM

class RiskAssessmentLLM:
    def __init__(self, model_name="gpt-4", temperature=0.1):
        self.model = model_name
        self.temperature = temperature
        
    def assess_risk(self, evidence: Dict, query: str, params: Dict) -> Dict:
        """Generate risk assessment using LLM"""
        
        # Build context prompt
        context = self._build_risk_context(evidence, query, params)
        
        # LLM call with JSON schema enforcement
        response = self._call_llm_with_schema_validation(context)
        
        # Post-process and validate
        risk_assessment = self._post_process_risk_response(response, evidence)
        
        return risk_assessment
    
    def _build_risk_context(self, evidence: Dict, query: str, params: Dict) -> str:
        """Build comprehensive context for risk assessment"""
        
        context = RISK_USER_PROMPT_TEMPLATE.format(
            query=query,
            ticker=params.get("ticker", "GENERAL"),
            time_window=params.get("time_window", "7d"),
            vector_evidence=json.dumps(evidence["vector_evidence"], indent=2),
            ml_signals=json.dumps(evidence["ml_signals"], indent=2),
            db_features=json.dumps(evidence["db_features"], indent=2)
        )
        
        return context
    
    def _call_llm_with_schema_validation(self, context: str) -> Dict:
        """Call LLM with strict JSON schema validation"""
        
        messages = [
            {"role": "system", "content": RISK_SYSTEM_PROMPT},
            {"role": "user", "content": context}
        ]
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=1500,
                    response_format={"type": "json_object"}  # Ensure JSON output
                )
                
                result = json.loads(response.choices[0].message.content)
                
                # Validate schema
                if self._validate_risk_schema(result):
                    return result
                else:
                    raise ValueError("Schema validation failed")
                    
            except (json.JSONDecodeError, ValueError) as e:
                if attempt == max_retries - 1:
                    # Fallback response
                    return self._generate_fallback_response()
                else:
                    # Retry with stricter temperature
                    self.temperature = max(0.0, self.temperature - 0.05)
        
        return self._generate_fallback_response()
    
    def _validate_risk_schema(self, response: Dict) -> bool:
        """Validate risk assessment response schema"""
        required_fields = ["risk_summary", "risk_level", "primary_risks", 
                          "confidence", "evidence_used"]
        
        return all(field in response for field in required_fields)
    
    def _post_process_risk_response(self, response: Dict, evidence: Dict) -> Dict:
        """Post-process and enrich risk assessment"""
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(response, evidence)
        response["confidence"] = confidence_score
        
        # Add warnings
        warnings = self._generate_warnings(evidence)
        if warnings:
            response["warnings"] = warnings
        
        # Add monitoring recommendations
        if "monitoring_recommendations" not in response:
            response["monitoring_recommendations"] = self._generate_monitoring_recommendations(response)
        
        return response
    
    def _calculate_confidence(self, response: Dict, evidence: Dict) -> float:
        """Calculate composite confidence score"""
        
        # Evidence density (40%)
        evidence_count = len(evidence["vector_evidence"])
        evidence_density = min(1.0, evidence_count / 10)  # Normalize to max 10 pieces
        
        # Signal strength (30%)
        ml_signals = evidence["ml_signals"]
        signal_strength = 0.0
        if ml_signals:
            anomaly_strength = ml_signals.get("max_anomaly_score", 0)
            sentiment_strength = abs(ml_signals.get("sentiment_score", 0))
            signal_strength = (anomaly_strength + sentiment_strength) / 2
        
        # Cross-source agreement (30%)
        risk_types_found = set()
        for ev in evidence["vector_evidence"]:
            risk_types_found.add(ev.get("risk_type", "unknown"))
        
        agreement_score = len(risk_types_found) / 4.0  # 4 risk types max
        
        # Composite confidence
        confidence = (
            0.4 * evidence_density +
            0.3 * min(1.0, signal_strength) +
            0.3 * agreement_score
        )
        
        return round(confidence, 2)
    
    def _generate_warnings(self, evidence: Dict) -> List[str]:
        """Generate warnings based on evidence quality"""
        warnings = []
        
        if len(evidence["vector_evidence"]) < 3:
            warnings.append("limited_evidence_available")
        
        if not evidence["ml_signals"]:
            warnings.append("ml_signals_unavailable")
        
        # Check evidence freshness
        fresh_evidence = 0
        for ev in evidence["vector_evidence"]:
            if ev.get("timestamp"):
                timestamp = pd.to_datetime(ev["timestamp"])
                if (datetime.now() - timestamp).total_seconds() < 86400:  # 24 hours
                    fresh_evidence += 1
        
        if fresh_evidence < 2:
            warnings.append("stale_evidence_warning")
        
        return warnings
    
    def _generate_monitoring_recommendations(self, response: Dict) -> List[str]:
        """Generate monitoring recommendations based on identified risks"""
        recommendations = []
        
        for risk in response.get("primary_risks", []):
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
    
    def _generate_fallback_response(self) -> Dict:
        """Generate minimal fallback response when LLM fails"""
        return {
            "risk_summary": "Risk assessment temporarily unavailable",
            "risk_level": "unknown",
            "primary_risks": [],
            "confidence": 0.0,
            "evidence_used": [],
            "warnings": ["llm_processing_error", "fallback_response_generated"],
            "monitoring_recommendations": ["Manual risk assessment recommended"]
        }
```

---

## ⚡ **PERFORMANCE & CACHING**

### **5) RISK-Optimized Performance**

#### **5.1 Redis Caching Strategy**
```python
import redis
from datetime import timedelta

class RiskCacheManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.risk_cache_ttl = 300  # 5 minutes for risk data
        self.ml_signals_ttl = 60   # 1 minute for ML signals
        
    def cache_risk_assessment(self, cache_key: str, assessment: Dict):
        """Cache complete risk assessment"""
        self.redis.setex(
            f"risk_assessment:{cache_key}",
            self.risk_cache_ttl,
            json.dumps(assessment)
        )
    
    def get_cached_risk_assessment(self, cache_key: str) -> Optional[Dict]:
        """Retrieve cached risk assessment"""
        cached = self.redis.get(f"risk_assessment:{cache_key}")
        return json.loads(cached) if cached else None
    
    def cache_ml_signals(self, ticker: str, signals: Dict):
        """Cache ML signals per ticker"""
        self.redis.setex(
            f"ml_signals:{ticker}",
            self.ml_signals_ttl,
            json.dumps(signals)
        )
    
    def get_cached_ml_signals(self, ticker: str) -> Optional[Dict]:
        """Get cached ML signals"""
        cached = self.redis.get(f"ml_signals:{ticker}")
        return json.loads(cached) if cached else None
    
    def cache_risk_evidence(self, query_hash: str, evidence: List):
        """Cache vector search results"""
        self.redis.setex(
            f"risk_evidence:{query_hash}",
            120,  # 2 minutes TTL
            json.dumps([chunk.__dict__ for chunk in evidence])
        )
    
    def generate_cache_key(self, query: str, params: Dict) -> str:
        """Generate consistent cache key"""
        key_data = {
            "query": query,
            "ticker": params.get("ticker", ""),
            "time_window": params.get("time_window", "7d"),
            "risk_types": sorted(params.get("risk_types", []))
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
```

#### **5.2 Latency Optimization**
```python
class RiskLatencyOptimizer:
    def __init__(self):
        self.vector_search_timeout = 60  # 60ms
        self.db_query_timeout = 40       # 40ms  
        self.llm_timeout = 900          # 900ms
        self.total_timeout = 1600       # 1.6s total
    
    async def optimized_risk_pipeline(self, query: str, params: Dict):
        """Execute risk pipeline with timeout controls"""
        start_time = time.time()
        
        # Parallel execution of independent operations
        tasks = []
        
        # 1. Vector search (can run in parallel)
        tasks.append(
            asyncio.wait_for(
                self.vector_search(query, params),
                timeout=self.vector_search_timeout/1000
            )
        )
        
        # 2. ML signals (can run in parallel)
        tasks.append(
            asyncio.wait_for(
                self.get_ml_signals(params.get("ticker")),
                timeout=self.db_query_timeout/1000
            )
        )
        
        # 3. DB features (can run in parallel)
        tasks.append(
            asyncio.wait_for(
                self.get_db_features(params),
                timeout=self.db_query_timeout/1000
            )
        )
        
        try:
            # Execute parallel operations
            vector_results, ml_signals, db_features = await asyncio.gather(*tasks)
            
            # Sequential LLM processing (depends on above results)
            evidence = self.gather_risk_evidence(vector_results, ml_signals, db_features)
            
            risk_assessment = await asyncio.wait_for(
                self.llm_risk_assessment(evidence, query, params),
                timeout=self.llm_timeout/1000
            )
            
            total_time = (time.time() - start_time) * 1000
            risk_assessment["processing_time_ms"] = round(total_time, 2)
            
            return risk_assessment
            
        except asyncio.TimeoutError as e:
            return self.handle_timeout_fallback(query, params, str(e))
        except Exception as e:
            return self.handle_error_fallback(query, params, str(e))
    
    def handle_timeout_fallback(self, query: str, params: Dict, error: str):
        """Handle timeout with graceful degradation"""
        return {
            "risk_summary": "Risk assessment partially available due to timeout",
            "risk_level": "unknown",
            "primary_risks": [],
            "confidence": 0.3,
            "evidence_used": [],
            "warnings": ["timeout_occurred", f"error: {error}"],
            "monitoring_recommendations": ["Retry risk assessment", "Check system performance"]
        }
    
    def handle_error_fallback(self, query: str, params: Dict, error: str):
        """Handle errors with basic response"""
        return {
            "risk_summary": "Risk assessment temporarily unavailable",
            "risk_level": "unknown", 
            "primary_risks": [],
            "confidence": 0.0,
            "evidence_used": [],
            "warnings": ["processing_error", f"error: {error}"],
            "monitoring_recommendations": ["Manual risk review recommended"]
        }
```

---

## 📊 **QUALITY & EVALUATION**

### **6) Risk Assessment Quality Framework**

#### **6.1 Risk-Specific KPIs**
```python
class RiskQualityMetrics:
    def __init__(self):
        self.metrics = {
            "risk_detection_accuracy": 0.0,
            "severity_classification_precision": 0.0,
            "evidence_relevance_score": 0.0,
            "confidence_calibration": 0.0,
            "response_latency_p95": 0.0,
            "false_positive_rate": 0.0
        }
    
    def evaluate_risk_assessment(self, assessment: Dict, ground_truth: Dict = None):
        """Evaluate quality of risk assessment"""
        
        scores = {}
        
        # Evidence quality (can be measured without ground truth)
        scores["evidence_relevance"] = self._score_evidence_relevance(assessment)
        scores["confidence_consistency"] = self._score_confidence_consistency(assessment)
        scores["response_completeness"] = self._score_response_completeness(assessment)
        
        # If ground truth available (for labeled evaluation set)
        if ground_truth:
            scores["risk_detection_accuracy"] = self._score_risk_detection(assessment, ground_truth)
            scores["severity_accuracy"] = self._score_severity_classification(assessment, ground_truth)
        
        return scores
    
    def _score_evidence_relevance(self, assessment: Dict) -> float:
        """Score evidence relevance and quality"""
        evidence = assessment.get("evidence_used", [])
        
        if not evidence:
            return 0.0
        
        relevance_scores = []
        for item in evidence:
            # Check if evidence contains risk-relevant keywords
            snippet = item.get("snippet", "").lower()
            risk_keywords = ["risk", "incident", "outage", "regulatory", "sentiment", 
                           "liquidity", "anomaly", "alert", "warning", "volatility"]
            
            relevance_score = sum(1 for keyword in risk_keywords if keyword in snippet) / len(risk_keywords)
            relevance_scores.append(relevance_score)
        
        return sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
    
    def _score_confidence_consistency(self, assessment: Dict) -> float:
        """Check if confidence aligns with evidence quality"""
        confidence = assessment.get("confidence", 0.0)
        evidence_count = len(assessment.get("evidence_used", []))
        risk_count = len(assessment.get("primary_risks", []))
        
        # Expected confidence based on evidence
        expected_confidence = min(0.9, (evidence_count * 0.1) + (risk_count * 0.1))
        
        # Score consistency (closer to expected = higher score)
        consistency = 1.0 - abs(confidence - expected_confidence)
        return max(0.0, consistency)
    
    def _score_response_completeness(self, assessment: Dict) -> float:
        """Check completeness of risk assessment response"""
        required_fields = ["risk_summary", "risk_level", "primary_risks", 
                          "confidence", "evidence_used"]
        
        present_fields = sum(1 for field in required_fields if field in assessment and assessment[field])
        completeness = present_fields / len(required_fields)
        
        # Bonus for monitoring recommendations
        if "monitoring_recommendations" in assessment and assessment["monitoring_recommendations"]:
            completeness = min(1.0, completeness + 0.1)
        
        return completeness
```

#### **6.2 Continuous Evaluation Set**
```python
# Risk assessment evaluation dataset
RISK_EVALUATION_QUERIES = [
    {
        "query": "What infrastructure risks affect NVDA trading?",
        "ticker": "NVDA",
        "expected_risk_types": ["infra"],
        "expected_severity": "medium",
        "ground_truth": {
            "should_find_evidence": True,
            "min_evidence_count": 2,
            "expected_confidence": 0.7
        }
    },
    {
        "query": "Are there any regulatory risks for tech stocks?",
        "ticker": None,
        "expected_risk_types": ["regulatory"],
        "expected_severity": "high",
        "ground_truth": {
            "should_find_evidence": True,
            "min_evidence_count": 3,
            "expected_confidence": 0.8
        }
    },
    {
        "query": "What liquidity risks exist for AAPL?",
        "ticker": "AAPL", 
        "expected_risk_types": ["liquidity"],
        "expected_severity": "low",
        "ground_truth": {
            "should_find_evidence": False,  # Limited AAPL data
            "min_evidence_count": 0,
            "expected_confidence": 0.3
        }
    }
    # ... 47 more evaluation queries covering different scenarios
]

class RiskEvaluationRunner:
    def __init__(self, risk_pipeline):
        self.pipeline = risk_pipeline
        
    async def run_evaluation_suite(self) -> Dict:
        """Run complete evaluation suite"""
        results = []
        
        for test_case in RISK_EVALUATION_QUERIES:
            result = await self._evaluate_single_query(test_case)
            results.append(result)
        
        # Aggregate results
        aggregated = self._aggregate_evaluation_results(results)
        return aggregated
    
    async def _evaluate_single_query(self, test_case: Dict) -> Dict:
        """Evaluate single risk query"""
        
        # Execute risk assessment
        assessment = await self.pipeline.assess_risk(
            query=test_case["query"],
            ticker=test_case["ticker"]
        )
        
        # Compare against ground truth
        evaluation = {
            "query": test_case["query"],
            "assessment": assessment,
            "ground_truth": test_case["ground_truth"],
            "scores": {}
        }
        
        # Score individual metrics
        evaluation["scores"]["risk_detection"] = self._score_risk_detection(
            assessment, test_case["expected_risk_types"]
        )
        evaluation["scores"]["severity_accuracy"] = self._score_severity(
            assessment, test_case["expected_severity"]
        )
        evaluation["scores"]["evidence_count"] = self._score_evidence_count(
            assessment, test_case["ground_truth"]["min_evidence_count"]
        )
        evaluation["scores"]["confidence_appropriate"] = self._score_confidence(
            assessment, test_case["ground_truth"]["expected_confidence"]
        )
        
        return evaluation
```

---

## 🔧 **IMPLEMENTATION FILES**

I'll now create the actual implementation files for the RISK mode pipeline:

```bash
# Create the directory structure
mkdir -p backend/rag_engine/risk_mode
mkdir -p backend/ml_integration 
mkdir -p tests/risk_assessment
```

Let me start implementing the core files:
