# MEMBER-1: OPTIONS FLOW INTERPRETER - COMPLETE IMPLEMENTATION GUIDE

## 🎯 MISSION
Convert raw options flow data + related anomalies into human-readable insights with evidence and confidence scores. Your system will explain unusual call/put volume, IV spikes, whale orders, and open interest changes in simple language.

## 📊 WHAT YOU'RE BUILDING
**Input**: Ticker + User Question about options activity
**Output**: Plain English explanation + reasons + confidence score + evidence

### Example Interaction
```json
Request:
POST /member1/options-flow
{
  "ticker": "TSLA",
  "user_question": "Are big traders buying calls?"
}

Response:
{
  "ticker": "TSLA",
  "insight": "TSLA shows unusually high call volume indicating bullish whale positioning.",
  "reasons": [
    "3.2x call volume vs 30-day average",
    "IV rising by 15% in last hour",
    "Strong bullish sentiment from recent news"
  ],
  "confidence": 0.84,
  "evidence": [
    {
      "source": "options_flow",
      "snippet": "Call volume spike detected at 2:30 PM",
      "timestamp": "2025-11-10T14:30:00Z"
    }
  ]
}
```

## 🏗️ ARCHITECTURE OVERVIEW
```
Frontend → POST /member1/options-flow → options_flow_routes.py
    ↓
options_flow_service.py
    ↓
├── options_queries.py (fetch DB data)
├── vector_store.py (retrieve evidence)
└── llama_engine.py (generate explanation)
    ↓
Structured JSON Response
```

## 📁 FILES YOU NEED TO CREATE

### 1. `/backend/routes/member1/options_flow_routes.py`
**Purpose**: REST API endpoint that validates input and calls service layer

**Implementation Steps**:
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from ...services.member1.options_flow_service import OptionsFlowService

# Request/Response Models
class OptionsFlowRequest(BaseModel):
    ticker: str
    user_question: str

class OptionsFlowResponse(BaseModel):
    ticker: str
    insight: str
    reasons: list[str]
    confidence: float
    evidence: list[dict]

# Router Setup
router = APIRouter(prefix="/member1", tags=["Member1-OptionsFlow"])
options_service = OptionsFlowService()

@router.post("/options-flow", response_model=OptionsFlowResponse)
async def analyze_options_flow(request: OptionsFlowRequest):
    """
    Analyze options flow and provide insights
    """
    try:
        # Validate ticker exists in assets table
        if not await options_service.validate_ticker(request.ticker):
            raise HTTPException(status_code=400, detail=f"Ticker {request.ticker} not found")
        
        # Call service layer
        result = await options_service.analyze_flow(
            ticker=request.ticker,
            user_question=request.user_question
        )
        
        return OptionsFlowResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Options flow analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

**Key Responsibilities**:
- ✅ Input validation (ticker format, question length)
- ✅ Error handling (400 for bad input, 500 for server errors)
- ✅ Call service layer and return formatted response

### 2. `/backend/services/member1/options_flow_service.py`
**Purpose**: Core business logic that fetches data, retrieves evidence, and calls LLM

**Implementation Steps**:
```python
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from ...db.queries.options_queries import OptionsQueries
from ...rag_engine.vector_store import VectorStore
from ...rag_engine.llama_engine import LlamaEngine
from .options_prompt import OptionsPrompt

class OptionsFlowService:
    def __init__(self):
        self.queries = OptionsQueries()
        self.vector_store = VectorStore()
        self.llm = LlamaEngine()
        self.prompt_builder = OptionsPrompt()
    
    async def validate_ticker(self, ticker: str) -> bool:
        """Check if ticker exists in assets table"""
        return await self.queries.ticker_exists(ticker)
    
    async def analyze_flow(self, ticker: str, user_question: str) -> Dict:
        """
        Main analysis function - orchestrates all data gathering and LLM call
        """
        # Step 1: Fetch options-related anomalies from DB
        anomalies = await self.queries.get_options_anomalies(ticker)
        
        # Step 2: Get recent volume/price data
        market_data = await self.queries.get_recent_market_data(ticker)
        
        # Step 3: Retrieve relevant evidence from vector DB
        evidence = await self.vector_store.retrieve_options_evidence(
            ticker=ticker,
            query_text=user_question,
            limit=5
        )
        
        # Step 4: Build structured prompt
        prompt = self.prompt_builder.build_prompt(
            ticker=ticker,
            user_question=user_question,
            anomalies=anomalies,
            market_data=market_data,
            evidence=evidence
        )
        
        # Step 5: Get LLM response
        llm_response = await self.llm.generate_structured_response(
            prompt=prompt,
            response_format="options_flow_analysis"
        )
        
        # Step 6: Format final response
        return self._format_response(llm_response, evidence)
    
    def _format_response(self, llm_response: Dict, evidence: List) -> Dict:
        """Format LLM output into standardized response"""
        return {
            "ticker": llm_response.get("ticker"),
            "insight": llm_response.get("insight"),
            "reasons": llm_response.get("reasons", []),
            "confidence": min(max(llm_response.get("confidence", 0.5), 0), 1),
            "evidence": [
                {
                    "source": item.get("source"),
                    "snippet": item.get("text")[:200] + "..." if len(item.get("text", "")) > 200 else item.get("text"),
                    "timestamp": item.get("timestamp")
                }
                for item in evidence
            ]
        }
```

**Key Responsibilities**:
- ✅ Orchestrate data gathering from multiple sources
- ✅ Call vector DB for relevant evidence
- ✅ Build and execute LLM prompt
- ✅ Format response with confidence scoring

### 3. `/backend/services/member1/options_prompt.py`
**Purpose**: Reusable LLM prompt templates for consistent options analysis

```python
class OptionsPrompt:
    def __init__(self):
        self.system_prompt = """You are an expert options flow analyst. 
        Explain unusual call/put volume, whale orders, IV spikes, and open interest changes in simple, clear language.
        
        Rules:
        - Be concise (2-4 sentences for insight)
        - List specific reasons with numbers/percentages
        - Give honest confidence scores (0.0 to 1.0)
        - Don't give trading advice, only explain what's happening
        - If data is limited, lower confidence accordingly
        """
    
    def build_prompt(self, ticker: str, user_question: str, anomalies: List, market_data: Dict, evidence: List) -> str:
        """Build complete prompt with all context"""
        
        # Format anomalies data
        anomaly_text = self._format_anomalies(anomalies)
        
        # Format market data
        market_text = self._format_market_data(market_data)
        
        # Format evidence
        evidence_text = self._format_evidence(evidence)
        
        user_prompt = f"""
ANALYSIS REQUEST:
Ticker: {ticker}
User Question: {user_question}

CURRENT DATA:
{market_text}

DETECTED ANOMALIES:
{anomaly_text}

SUPPORTING EVIDENCE:
{evidence_text}

REQUIRED OUTPUT FORMAT (JSON):
{{
    "ticker": "{ticker}",
    "insight": "Brief 2-4 sentence explanation of what's happening",
    "reasons": ["Specific reason 1 with numbers", "Specific reason 2", "Reason 3"],
    "confidence": 0.75
}}

Analyze the options flow and provide insights:
"""
        return self.system_prompt + "\n\n" + user_prompt
    
    def _format_anomalies(self, anomalies: List) -> str:
        """Convert anomaly data to readable text"""
        if not anomalies:
            return "No significant anomalies detected."
        
        formatted = []
        for anomaly in anomalies[:3]:  # Top 3 anomalies
            formatted.append(
                f"- {anomaly.get('metric', 'unknown')}: {anomaly.get('explanation', 'N/A')} "
                f"(severity: {anomaly.get('severity', 'unknown')}, score: {anomaly.get('anomaly_score', 0):.2f})"
            )
        return "\n".join(formatted)
    
    def _format_market_data(self, market_data: Dict) -> str:
        """Format market data into readable text"""
        if not market_data:
            return "No recent market data available."
        
        return f"""- Latest Price: ${market_data.get('close', 'N/A')}
- Volume: {market_data.get('volume', 'N/A'):,} vs avg {market_data.get('avg_volume', 'N/A'):,}
- Volume Ratio: {market_data.get('volume_ratio', 'N/A'):.2f}x
- Volatility: {market_data.get('volatility', 'N/A'):.2f}%"""
    
    def _format_evidence(self, evidence: List) -> str:
        """Format vector DB evidence into readable text"""
        if not evidence:
            return "No relevant evidence found."
        
        formatted = []
        for item in evidence[:3]:  # Top 3 pieces of evidence
            formatted.append(f"- {item.get('source', 'unknown')}: {item.get('text', 'N/A')[:100]}...")
        return "\n".join(formatted)
```

### 4. `/backend/db/queries/options_queries.py`
**Purpose**: SQL queries to fetch options-related anomalies and market data

```python
import asyncpg
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ..postgres_handler import PostgresHandler

class OptionsQueries:
    def __init__(self):
        self.db = PostgresHandler()
    
    async def ticker_exists(self, ticker: str) -> bool:
        """Check if ticker exists in assets table"""
        query = "SELECT 1 FROM assets WHERE ticker = $1 LIMIT 1"
        result = await self.db.fetch_one(query, ticker)
        return result is not None
    
    async def get_options_anomalies(self, ticker: str, hours_back: int = 24) -> List[Dict]:
        """
        Fetch options-related anomalies for the ticker
        Focus on: volume spikes, liquidity changes, IV spikes
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        query = """
        SELECT 
            metric,
            anomaly_score,
            severity,
            explanation,
            timestamp
        FROM anomalies 
        WHERE ticker = $1 
        AND timestamp >= $2
        AND metric IN ('volume', 'liquidity', 'iv_spike', 'call_skew', 'put_skew')
        ORDER BY anomaly_score DESC, timestamp DESC
        LIMIT 10
        """
        
        results = await self.db.fetch_all(query, ticker, cutoff_time)
        return [dict(row) for row in results]
    
    async def get_recent_market_data(self, ticker: str, hours_back: int = 6) -> Dict:
        """
        Get recent price/volume data for context
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Latest price data
        latest_query = """
        SELECT close, volume, timestamp
        FROM market_prices 
        WHERE ticker = $1 AND timestamp >= $2
        ORDER BY timestamp DESC 
        LIMIT 1
        """
        
        # Average volume calculation
        avg_volume_query = """
        SELECT AVG(volume) as avg_volume
        FROM market_prices 
        WHERE ticker = $1 
        AND timestamp >= $2
        """
        
        latest_data = await self.db.fetch_one(latest_query, ticker, cutoff_time)
        avg_volume_data = await self.db.fetch_one(avg_volume_query, ticker, cutoff_time - timedelta(days=7))
        
        if not latest_data:
            return {}
        
        latest = dict(latest_data)
        avg_volume = dict(avg_volume_data).get('avg_volume', 1) if avg_volume_data else 1
        
        return {
            "close": latest.get("close"),
            "volume": latest.get("volume"),
            "avg_volume": avg_volume,
            "volume_ratio": latest.get("volume", 0) / max(avg_volume, 1),
            "timestamp": latest.get("timestamp")
        }
    
    async def get_call_put_ratios(self, ticker: str) -> Dict:
        """
        Get call/put volume ratios if available in anomalies
        """
        query = """
        SELECT explanation, anomaly_score, timestamp
        FROM anomalies 
        WHERE ticker = $1 
        AND metric IN ('call_skew', 'put_skew')
        AND timestamp >= NOW() - INTERVAL '24 hours'
        ORDER BY timestamp DESC
        LIMIT 5
        """
        
        results = await self.db.fetch_all(query, ticker)
        return [dict(row) for row in results]
```

## 🔧 INTEGRATION WITH EXISTING SYSTEM

### Vector Store Integration
Your options evidence will be retrieved from the existing ChromaDB with these filters:
```python
# In vector_store.py, add this method:
async def retrieve_options_evidence(self, ticker: str, query_text: str, limit: int = 5):
    """Retrieve options-related evidence from vector DB"""
    filter_conditions = {
        "ticker": ticker,
        "risk_type": {"$in": ["options", "sentiment", "volume"]}
    }
    
    results = await self.collection.query(
        query_texts=[query_text],
        where=filter_conditions,
        n_results=limit
    )
    
    return self._format_results(results)
```

### LLM Integration
Use the existing Llama engine with structured output:
```python
# In llama_engine.py, add this response format:
RESPONSE_FORMATS = {
    "options_flow_analysis": {
        "ticker": "string",
        "insight": "string", 
        "reasons": "array of strings",
        "confidence": "float between 0 and 1"
    }
}
```

## 🎯 DATA SOURCES YOU'LL USE

### 1. Anomalies Table
**What you get**: Volume spikes, liquidity changes, IV spikes
```sql
SELECT * FROM anomalies WHERE ticker = 'AAPL' AND metric IN ('volume', 'liquidity', 'iv_spike');
```

### 2. Market Prices Table  
**What you get**: Recent price/volume for context
```sql
SELECT close, volume FROM market_prices WHERE ticker = 'AAPL' ORDER BY timestamp DESC LIMIT 10;
```

### 3. Vector Database
**What you get**: News, sentiment, and evidence chunks tagged with "options"

## 📝 TESTING YOUR IMPLEMENTATION

### 1. Unit Tests (`tests/test_member1_options_flow.py`)
```python
import pytest
from backend.services.member1.options_flow_service import OptionsFlowService

@pytest.mark.asyncio
async def test_options_flow_valid_request():
    service = OptionsFlowService()
    
    result = await service.analyze_flow(
        ticker="AAPL",
        user_question="Are institutions buying calls?"
    )
    
    assert "ticker" in result
    assert "insight" in result
    assert "confidence" in result
    assert 0 <= result["confidence"] <= 1

@pytest.mark.asyncio 
async def test_invalid_ticker():
    service = OptionsFlowService()
    
    with pytest.raises(ValueError):
        await service.analyze_flow(
            ticker="INVALID",
            user_question="Test question"
        )
```

### 2. API Tests (Postman/curl)
```bash
# Test valid request
curl -X POST "http://localhost:8000/member1/options-flow" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "user_question": "Are big traders buying calls?"
  }'

# Test invalid ticker
curl -X POST "http://localhost:8000/member1/options-flow" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "INVALID",
    "user_question": "Test"
  }'
```

## 🚀 DEPLOYMENT CHECKLIST

- [ ] Create all 4 files listed above
- [ ] Add route to main app.py: `app.include_router(options_flow_routes.router)`
- [ ] Test with sample data in your local environment
- [ ] Add error logging for debugging
- [ ] Create unit tests for each component
- [ ] Test API endpoints with Postman
- [ ] Add your documentation to this file
- [ ] Submit PR for code review

## 🔍 EXAMPLE DATA FLOW

**Input**: `{"ticker": "TSLA", "user_question": "Why is call volume high?"}`

**DB Query Results**:
```json
{
  "anomalies": [
    {"metric": "volume", "anomaly_score": 0.89, "explanation": "3.2x normal call volume"}
  ],
  "market_data": {
    "volume": 45000000,
    "avg_volume": 28000000,
    "volume_ratio": 1.6
  }
}
```

**Vector DB Results**:
```json
{
  "evidence": [
    {"source": "finnhub", "text": "TSLA earnings beat expectations", "timestamp": "2025-11-10T10:00:00Z"}
  ]
}
```

**LLM Output**:
```json
{
  "ticker": "TSLA",
  "insight": "TSLA shows unusually high call volume indicating bullish positioning ahead of earnings.",
  "reasons": [
    "Call volume 3.2x higher than 30-day average",
    "Total volume up 60% vs typical trading",
    "Positive earnings sentiment driving optimism"
  ],
  "confidence": 0.84
}
```

This comprehensive guide gives you everything needed to implement the Options Flow Interpreter. The existing infrastructure handles data ingestion, vector storage, and LLM integration - you just need to create the 4 files and connect them together!
