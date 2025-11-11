# MEMBER-3: MACRO-DRIVEN GAP FORECASTER - COMPLETE IMPLEMENTATION GUIDE

## 🎯 MISSION
Use regulatory/macro evidence (FOMC statements, RBI releases, Fed decisions, SEC filings, economic news, etc.) to predict whether an asset will likely gap up, gap down, or stay neutral in the next trading session. Provide data-driven forecasts based on historical patterns and current macro sentiment.

## 📊 WHAT YOU'RE BUILDING
**Input**: Asset + Question about macro event impact
**Output**: Gap direction prediction + macro drivers + confidence + historical context

### Example Interaction
```json
Request:
POST /member3/macro-gap
{
  "asset": "NASDAQ",
  "question": "What happens after the FOMC announcement?"
}

Response:
{
  "asset": "NASDAQ",
  "expected_gap": "slight gap up",
  "drivers": [
    "dovish FOMC tone signals rate pause",
    "falling 10-year yields support tech valuations", 
    "strong futures reaction (+0.8% overnight)",
    "historical pattern: 73% gap up after dovish Fed"
  ],
  "confidence": 0.71,
  "evidence_used": [
    {
      "source": "fed",
      "snippet": "Federal Reserve signals slower pace of tightening ahead",
      "timestamp": "2025-11-10T14:00:00Z"
    },
    {
      "source": "sentiment_analysis", 
      "snippet": "Macro sentiment improved to +0.63 from neutral",
      "timestamp": "2025-11-10T14:15:00Z"
    }
  ],
  "historical_context": {
    "similar_events": 15,
    "gap_up_probability": 0.73,
    "average_gap_size": 1.2
  }
}
```

## 🏗️ ARCHITECTURE OVERVIEW
```
Frontend → POST /member3/macro-gap → macro_gap_routes.py
    ↓
macro_gap_service.py
    ↓
├── macro_queries.py (regulatory events, sentiment, gap history)
├── vector_store.py (retrieve macro-focused evidence)
├── gap_analyzer.py (historical pattern analysis)
└── llama_engine.py (generate prediction)
    ↓
Structured JSON Response with Historical Context
```

## 📁 FILES YOU NEED TO CREATE

### 1. `/backend/routes/member3/macro_gap_routes.py`
**Purpose**: REST API endpoint for macro-driven gap predictions

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import Optional, List
import logging
from ...services.member3.macro_gap_service import MacroGapService

# Request/Response Models
class MacroGapRequest(BaseModel):
    asset: str
    question: str
    
    @validator('asset')
    def validate_asset(cls, v):
        if not v or len(v) > 20:
            raise ValueError('Asset must be provided and less than 20 characters')
        return v.upper()
    
    @validator('question')
    def validate_question(cls, v):
        if not v or len(v) < 10:
            raise ValueError('Question must be at least 10 characters')
        return v

class HistoricalContext(BaseModel):
    similar_events: int
    gap_up_probability: float
    gap_down_probability: float
    average_gap_size: float
    confidence_from_history: float

class MacroGapResponse(BaseModel):
    asset: str
    expected_gap: str  # "gap up", "gap down", "neutral", "slight gap up", etc.
    drivers: List[str]
    confidence: float
    evidence_used: List[dict]
    historical_context: Optional[HistoricalContext] = None
    macro_sentiment: Optional[dict] = None

# Router Setup
router = APIRouter(prefix="/member3", tags=["Member3-MacroGap"])
gap_service = MacroGapService()

@router.post("/macro-gap", response_model=MacroGapResponse)
async def predict_macro_gap(request: MacroGapRequest):
    """
    Predict overnight gap direction based on macro events and historical patterns
    
    Analyzes:
    - Recent regulatory/FOMC/RBI announcements
    - Macro sentiment trends
    - Historical gap behavior after similar events
    - Futures market reactions
    """
    try:
        # Validate asset exists and is supported
        if not await gap_service.validate_asset(request.asset):
            raise HTTPException(
                status_code=400, 
                detail=f"Asset {request.asset} not tracked or not supported for gap analysis"
            )
        
        # Check for recent macro events
        macro_events = await gap_service.detect_recent_macro_events(request.asset)
        if not macro_events:
            raise HTTPException(
                status_code=404,
                detail=f"No recent macro events found for {request.asset}. Gap prediction requires macro catalyst."
            )
        
        # Generate gap prediction
        result = await gap_service.predict_gap(
            asset=request.asset,
            question=request.question
        )
        
        return MacroGapResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Macro gap prediction error for {request.asset}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during gap analysis")

@router.get("/macro-events/{asset}")
async def get_recent_macro_events(asset: str, days_back: int = 7):
    """
    Helper endpoint to show recent macro events for an asset
    Useful for frontend to display context before asking for prediction
    """
    try:
        events = await gap_service.get_macro_events_summary(asset, days_back)
        return {
            "asset": asset,
            "recent_events": events,
            "analysis_suitable": len(events) > 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving macro events")

@router.get("/gap-history/{asset}")
async def get_gap_history(asset: str, event_type: Optional[str] = None, limit: int = 20):
    """
    Get historical gap data for an asset after specific event types
    """
    try:
        history = await gap_service.get_historical_gaps(asset, event_type, limit)
        return {
            "asset": asset,
            "event_type": event_type or "all",
            "historical_gaps": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving gap history")

@router.post("/batch-gap-prediction")
async def predict_gaps_for_multiple_assets(assets: List[str], macro_event_description: str):
    """
    Predict gap impact across multiple assets for a single macro event
    Useful for broad market impact analysis
    """
    try:
        results = []
        for asset in assets[:10]:  # Limit to 10 assets
            try:
                prediction = await gap_service.predict_gap(
                    asset=asset,
                    question=f"Impact of: {macro_event_description}"
                )
                results.append({"asset": asset, "prediction": prediction})
            except Exception as e:
                results.append({"asset": asset, "error": str(e)})
        
        return {"predictions": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error in batch prediction")
```

### 2. `/backend/services/member3/macro_gap_service.py`
**Purpose**: Core business logic for macro event analysis and gap prediction

```python
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from ...db.queries.macro_queries import MacroQueries
from ...rag_engine.vector_store import VectorStore
from ...rag_engine.llama_engine import LlamaEngine
from .macro_gap_prompt import MacroGapPrompt
from .gap_analyzer import GapAnalyzer

class MacroGapService:
    def __init__(self):
        self.queries = MacroQueries()
        self.vector_store = VectorStore()
        self.llm = LlamaEngine()
        self.prompt_builder = MacroGapPrompt()
        self.gap_analyzer = GapAnalyzer()
        
        # Supported assets for gap analysis
        self.SUPPORTED_ASSETS = {
            "NASDAQ", "SPY", "QQQ", "AAPL", "MSFT", "NVDA", "TSLA", 
            "BTC", "ETH", "NIFTY", "SENSEX", "BANKNIFTY"
        }
        
        # Macro event lookback period
        self.MACRO_EVENT_WINDOW_DAYS = 7
    
    async def validate_asset(self, asset: str) -> bool:
        """Check if asset exists and is supported for gap analysis"""
        asset_exists = await self.queries.asset_exists(asset)
        return asset_exists and asset.upper() in self.SUPPORTED_ASSETS
    
    async def detect_recent_macro_events(self, asset: str) -> List[Dict]:
        """Check if there are recent macro events that could affect gaps"""
        cutoff_time = datetime.utcnow() - timedelta(days=self.MACRO_EVENT_WINDOW_DAYS)
        
        events = await self.queries.get_recent_macro_events(asset, cutoff_time)
        return events
    
    async def predict_gap(self, asset: str, question: str) -> Dict:
        """
        Main gap prediction function - analyzes macro events and predicts gap direction
        """
        # Gather all relevant data in parallel
        prediction_tasks = [
            self.queries.get_recent_macro_events(asset, datetime.utcnow() - timedelta(days=7)),
            self.queries.get_macro_sentiment(asset),
            self.queries.get_historical_gaps(asset),
            self.queries.get_futures_data(asset),
            self.vector_store.retrieve_macro_evidence(asset, question)
        ]
        
        macro_events, sentiment_data, gap_history, futures_data, vector_evidence = await asyncio.gather(*prediction_tasks)
        
        # Analyze historical patterns
        historical_context = await self.gap_analyzer.analyze_patterns(
            asset=asset,
            current_events=macro_events,
            gap_history=gap_history
        )
        
        # Build comprehensive context for LLM
        context = {
            "asset": asset,
            "question": question,
            "macro_events": macro_events,
            "sentiment_data": sentiment_data,
            "historical_context": historical_context,
            "futures_data": futures_data,
            "vector_evidence": vector_evidence
        }
        
        # Generate LLM prediction
        prompt = self.prompt_builder.build_gap_prediction_prompt(context)
        
        llm_response = await self.llm.generate_structured_response(
            prompt=prompt,
            response_format="gap_prediction"
        )
        
        # Format final response
        return self._format_gap_response(llm_response, context)
    
    async def get_macro_events_summary(self, asset: str, days_back: int) -> List[Dict]:
        """Get summary of recent macro events for display/context"""
        cutoff_time = datetime.utcnow() - timedelta(days=days_back)
        events = await self.queries.get_recent_macro_events(asset, cutoff_time)
        
        # Format for display
        return [
            {
                "type": event.get("event_type"),
                "source": event.get("source"),
                "title": event.get("title", "")[:100] + "..." if len(event.get("title", "")) > 100 else event.get("title"),
                "severity": event.get("severity"),
                "published_at": event.get("published_at").isoformat() if event.get("published_at") else None
            }
            for event in events
        ]
    
    async def get_historical_gaps(self, asset: str, event_type: Optional[str], limit: int) -> List[Dict]:
        """Get historical gap data for analysis"""
        return await self.queries.get_gap_history(asset, event_type, limit)
    
    def _format_gap_response(self, llm_response: Dict, context: Dict) -> Dict:
        """Format LLM output into standardized API response"""
        
        # Validate gap direction
        gap_direction = llm_response.get("expected_gap", "neutral").lower()
        valid_directions = ["gap up", "gap down", "neutral", "slight gap up", "slight gap down", "strong gap up", "strong gap down"]
        if gap_direction not in valid_directions:
            gap_direction = "neutral"
        
        return {
            "asset": llm_response.get("asset", context["asset"]),
            "expected_gap": gap_direction,
            "drivers": llm_response.get("drivers", [])[:5],  # Limit to 5 drivers
            "confidence": min(max(llm_response.get("confidence", 0.3), 0), 1),
            "evidence_used": self._format_evidence_list(context),
            "historical_context": self._format_historical_context(context.get("historical_context", {})),
            "macro_sentiment": self._format_sentiment_summary(context.get("sentiment_data", []))
        }
    
    def _format_evidence_list(self, context: Dict) -> List[Dict]:
        """Compile evidence from all sources"""
        evidence = []
        
        # Add macro event evidence
        for event in context.get("macro_events", [])[:2]:
            evidence.append({
                "source": event.get("source", "regulatory"),
                "snippet": f"{event.get('event_type', 'Event')}: {event.get('title', 'Announcement')}",
                "timestamp": event.get("published_at").isoformat() if event.get("published_at") else None
            })
        
        # Add sentiment evidence
        sentiment_data = context.get("sentiment_data", [])
        if sentiment_data:
            avg_sentiment = sum(s.get("sentiment_score", 0) for s in sentiment_data) / len(sentiment_data)
            evidence.append({
                "source": "sentiment_analysis",
                "snippet": f"Macro sentiment: {avg_sentiment:.2f} ({'positive' if avg_sentiment > 0.1 else 'negative' if avg_sentiment < -0.1 else 'neutral'})",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Add futures data
        futures = context.get("futures_data", {})
        if futures:
            evidence.append({
                "source": "futures_market",
                "snippet": f"Overnight futures: {futures.get('change_percent', 0):+.2f}% ({futures.get('direction', 'neutral')})",
                "timestamp": futures.get("timestamp")
            })
        
        # Add vector DB evidence
        for item in context.get("vector_evidence", [])[:3]:
            evidence.append({
                "source": item.get("source", "news"),
                "snippet": item.get("text", "")[:120] + "..." if len(item.get("text", "")) > 120 else item.get("text", ""),
                "timestamp": item.get("timestamp")
            })
        
        return evidence[:6]  # Limit to 6 pieces of evidence
    
    def _format_historical_context(self, historical_data: Dict) -> Dict:
        """Format historical analysis for response"""
        if not historical_data:
            return {
                "similar_events": 0,
                "gap_up_probability": 0.5,
                "gap_down_probability": 0.5,
                "average_gap_size": 0.0,
                "confidence_from_history": 0.0
            }
        
        return {
            "similar_events": historical_data.get("event_count", 0),
            "gap_up_probability": historical_data.get("gap_up_prob", 0.5),
            "gap_down_probability": historical_data.get("gap_down_prob", 0.5),
            "average_gap_size": historical_data.get("avg_gap_size", 0.0),
            "confidence_from_history": historical_data.get("pattern_confidence", 0.0)
        }
    
    def _format_sentiment_summary(self, sentiment_data: List) -> Dict:
        """Format sentiment analysis summary"""
        if not sentiment_data:
            return {"score": 0.0, "trend": "neutral", "sample_size": 0}
        
        scores = [s.get("sentiment_score", 0) for s in sentiment_data]
        avg_score = sum(scores) / len(scores)
        
        return {
            "score": round(avg_score, 2),
            "trend": "positive" if avg_score > 0.1 else "negative" if avg_score < -0.1 else "neutral",
            "sample_size": len(sentiment_data),
            "recent_headlines": [
                s.get("headline", "")[:60] + "..." if len(s.get("headline", "")) > 60 else s.get("headline", "")
                for s in sentiment_data[:3]
            ]
        }
```

### 3. `/backend/services/member3/gap_analyzer.py`
**Purpose**: Historical pattern analysis for gap predictions

```python
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics
from ...db.queries.macro_queries import MacroQueries

class GapAnalyzer:
    def __init__(self):
        self.queries = MacroQueries()
        
        # Event type mappings for pattern analysis
        self.EVENT_CATEGORIES = {
            "fed": ["rate", "monetary", "fomc", "powell"],
            "inflation": ["cpi", "pce", "inflation", "prices"],
            "employment": ["jobs", "unemployment", "nfp", "employment"],
            "regulatory": ["sec", "cftc", "regulatory", "compliance"],
            "geopolitical": ["war", "sanctions", "trade", "geopolitical"]
        }
    
    async def analyze_patterns(self, asset: str, current_events: List[Dict], gap_history: List[Dict]) -> Dict:
        """
        Analyze historical gap patterns after similar events
        """
        if not current_events or not gap_history:
            return self._empty_pattern_response()
        
        # Categorize current events
        current_event_types = self._categorize_events(current_events)
        
        # Find similar historical events
        similar_gaps = self._filter_similar_events(gap_history, current_event_types)
        
        if len(similar_gaps) < 3:  # Not enough data
            return self._low_confidence_response(len(similar_gaps))
        
        # Analyze patterns
        return self._calculate_gap_patterns(similar_gaps)
    
    def _categorize_events(self, events: List[Dict]) -> List[str]:
        """Categorize events into types for pattern matching"""
        categories = []
        
        for event in events:
            event_type = event.get("event_type", "").lower()
            title = event.get("title", "").lower()
            body = event.get("body", "").lower()
            
            text_to_analyze = f"{event_type} {title} {body}".lower()
            
            for category, keywords in self.EVENT_CATEGORIES.items():
                if any(keyword in text_to_analyze for keyword in keywords):
                    categories.append(category)
                    break
            else:
                categories.append("other")
        
        return list(set(categories))  # Remove duplicates
    
    def _filter_similar_events(self, gap_history: List[Dict], current_categories: List[str]) -> List[Dict]:
        """Filter gap history for events similar to current events"""
        similar_gaps = []
        
        for gap in gap_history:
            gap_reason = gap.get("reason", "").lower()
            
            # Check if gap reason matches any current event category
            for category in current_categories:
                if category in gap_reason or any(
                    keyword in gap_reason 
                    for keyword in self.EVENT_CATEGORIES.get(category, [])
                ):
                    similar_gaps.append(gap)
                    break
        
        return similar_gaps
    
    def _calculate_gap_patterns(self, similar_gaps: List[Dict]) -> Dict:
        """Calculate statistical patterns from similar historical gaps"""
        gap_directions = []
        gap_sizes = []
        
        for gap in similar_gaps:
            direction = gap.get("direction", "flat")
            gap_percent = abs(gap.get("gap_percent", 0))
            
            gap_directions.append(direction)
            gap_sizes.append(gap_percent)
        
        # Calculate probabilities
        total_events = len(gap_directions)
        gap_up_count = gap_directions.count("up")
        gap_down_count = gap_directions.count("down")
        
        gap_up_prob = gap_up_count / total_events if total_events > 0 else 0.5
        gap_down_prob = gap_down_count / total_events if total_events > 0 else 0.5
        
        # Calculate average gap size
        avg_gap_size = statistics.mean(gap_sizes) if gap_sizes else 0.0
        gap_size_std = statistics.stdev(gap_sizes) if len(gap_sizes) > 1 else 0.0
        
        # Calculate confidence based on sample size and consistency
        pattern_confidence = self._calculate_pattern_confidence(
            total_events, gap_up_prob, gap_down_prob, gap_size_std
        )
        
        return {
            "event_count": total_events,
            "gap_up_prob": round(gap_up_prob, 2),
            "gap_down_prob": round(gap_down_prob, 2),
            "avg_gap_size": round(avg_gap_size, 2),
            "gap_size_std": round(gap_size_std, 2),
            "pattern_confidence": round(pattern_confidence, 2),
            "sample_gaps": similar_gaps[:5]  # Include sample data
        }
    
    def _calculate_pattern_confidence(self, sample_size: int, up_prob: float, down_prob: float, volatility: float) -> float:
        """Calculate confidence in the historical pattern"""
        if sample_size == 0:
            return 0.0
        
        # Base confidence from sample size (more samples = higher confidence)
        size_confidence = min(sample_size / 20.0, 1.0)  # Max confidence at 20+ samples
        
        # Directional confidence (clearer patterns = higher confidence)
        directional_clarity = abs(up_prob - down_prob)  # 0 = no pattern, 1 = clear pattern
        
        # Volatility penalty (high volatility = lower confidence)
        volatility_penalty = min(volatility / 5.0, 0.5)  # Max 50% penalty
        
        # Combined confidence
        combined_confidence = size_confidence * directional_clarity * (1 - volatility_penalty)
        
        return max(min(combined_confidence, 1.0), 0.0)
    
    def _empty_pattern_response(self) -> Dict:
        """Return default response when no data available"""
        return {
            "event_count": 0,
            "gap_up_prob": 0.5,
            "gap_down_prob": 0.5,
            "avg_gap_size": 0.0,
            "gap_size_std": 0.0,
            "pattern_confidence": 0.0,
            "sample_gaps": []
        }
    
    def _low_confidence_response(self, sample_count: int) -> Dict:
        """Return low confidence response for insufficient data"""
        return {
            "event_count": sample_count,
            "gap_up_prob": 0.5,
            "gap_down_prob": 0.5,
            "avg_gap_size": 0.0,
            "gap_size_std": 0.0,
            "pattern_confidence": 0.1,  # Low confidence
            "sample_gaps": []
        }
    
    async def analyze_event_impact_strength(self, events: List[Dict]) -> str:
        """Classify the strength of macro events (weak/moderate/strong)"""
        if not events:
            return "none"
        
        severity_scores = []
        for event in events:
            severity = event.get("severity", "medium").lower()
            score = {"low": 1, "medium": 2, "high": 3}.get(severity, 2)
            severity_scores.append(score)
        
        avg_severity = sum(severity_scores) / len(severity_scores)
        
        if avg_severity >= 2.5:
            return "strong"
        elif avg_severity >= 1.5:
            return "moderate"
        else:
            return "weak"
    
    async def get_market_regime_context(self, asset: str) -> Dict:
        """Analyze current market regime (bull/bear/volatile) for context"""
        # This would analyze recent market trends, VIX levels, etc.
        # Simplified implementation for now
        recent_data = await self.queries.get_recent_market_context(asset)
        
        if not recent_data:
            return {"regime": "unknown", "confidence": 0.0}
        
        # Simple regime detection based on recent price trend and volatility
        price_trend = recent_data.get("price_trend_30d", 0)
        volatility = recent_data.get("volatility_30d", 0)
        
        if price_trend > 5 and volatility < 25:
            regime = "bull"
        elif price_trend < -5 and volatility < 25:
            regime = "bear"
        elif volatility > 35:
            regime = "volatile"
        else:
            regime = "neutral"
        
        return {
            "regime": regime,
            "price_trend_30d": price_trend,
            "volatility_30d": volatility,
            "confidence": 0.7 if abs(price_trend) > 3 or volatility > 30 else 0.4
        }
```

### 4. `/backend/services/member3/macro_gap_prompt.py`
**Purpose**: LLM prompt templates for gap prediction

```python
class MacroGapPrompt:
    def __init__(self):
        self.system_prompt = """You are an expert macro analyst specializing in predicting overnight gaps in financial markets.
        
        Your expertise includes:
        - Federal Reserve policy impact on equities and crypto
        - Central bank announcements (RBI, ECB, BoJ) effects
        - Regulatory announcements and market reactions
        - Geopolitical events and safe-haven flows
        - Historical pattern analysis for gap predictions
        
        Rules for gap prediction:
        - Base predictions on evidence and historical patterns
        - Consider futures market reactions and sentiment
        - Use specific gap categories: "gap up", "gap down", "slight gap up", "slight gap down", "strong gap up", "strong gap down", "neutral"
        - Provide confidence scores based on evidence quality and historical consistency
        - Include specific drivers with numbers/percentages when available
        - If historical data is limited, lower confidence accordingly
        """
    
    def build_gap_prediction_prompt(self, context: Dict) -> str:
        """Build complete prompt with macro context and historical patterns"""
        
        asset = context['asset']
        question = context['question']
        
        # Format all context sections
        macro_events_text = self._format_macro_events(context.get('macro_events', []))
        sentiment_text = self._format_sentiment_data(context.get('sentiment_data', []))
        historical_text = self._format_historical_context(context.get('historical_context', {}))
        futures_text = self._format_futures_data(context.get('futures_data', {}))
        evidence_text = self._format_vector_evidence(context.get('vector_evidence', []))
        
        user_prompt = f"""
GAP PREDICTION REQUEST:
Asset: {asset}
Question: {question}

RECENT MACRO EVENTS:
{macro_events_text}

CURRENT MARKET SENTIMENT:
{sentiment_text}

HISTORICAL PATTERN ANALYSIS:
{historical_text}

FUTURES MARKET REACTION:
{futures_text}

SUPPORTING EVIDENCE:
{evidence_text}

REQUIRED OUTPUT FORMAT (JSON):
{{
    "asset": "{asset}",
    "expected_gap": "gap up" | "gap down" | "slight gap up" | "slight gap down" | "strong gap up" | "strong gap down" | "neutral",
    "drivers": [
        "Primary driver with specific details/numbers",
        "Secondary driver with context",
        "Historical pattern supporting the prediction",
        "Market technical factor if relevant"
    ],
    "confidence": 0.75
}}

CONFIDENCE SCORING GUIDELINES:
- 0.8-1.0: Strong historical pattern + clear catalyst + supporting technicals
- 0.6-0.8: Good historical data + clear catalyst + some supporting factors  
- 0.4-0.6: Moderate evidence + some historical precedent
- 0.2-0.4: Limited evidence + weak historical patterns
- 0.0-0.2: Contradictory or very limited evidence

GAP DIRECTION DEFINITIONS:
- "strong gap up/down": >2% expected gap based on major catalyst
- "gap up/down": 1-2% expected gap based on clear catalyst
- "slight gap up/down": 0.5-1% expected gap based on moderate catalyst
- "neutral": <0.5% gap expected or unclear direction

Analyze the macro environment and predict the gap:
"""
        return self.system_prompt + "\n\n" + user_prompt
    
    def _format_macro_events(self, events: List) -> str:
        """Format macro events for prompt"""
        if not events:
            return "No significant macro events detected in the analysis window."
        
        formatted = []
        for event in events[:4]:  # Top 4 events
            event_type = event.get('event_type', 'Unknown')
            source = event.get('source', 'unknown')
            title = event.get('title', 'No title')
            severity = event.get('severity', 'medium')
            published_at = event.get('published_at', 'Unknown time')
            
            formatted.append(
                f"- {event_type.title()} ({source}): {title} "
                f"[{severity} impact] at {published_at}"
            )
        
        return "\n".join(formatted)
    
    def _format_sentiment_data(self, sentiment_data: List) -> str:
        """Format sentiment analysis for prompt"""
        if not sentiment_data:
            return "No sentiment data available for analysis period."
        
        scores = [s.get('sentiment_score', 0) for s in sentiment_data if s.get('sentiment_score') is not None]
        if not scores:
            return "No valid sentiment scores found."
        
        avg_sentiment = sum(scores) / len(scores)
        trend = "positive" if avg_sentiment > 0.1 else "negative" if avg_sentiment < -0.1 else "neutral"
        
        formatted = [
            f"- Average macro sentiment: {avg_sentiment:.2f} ({trend})",
            f"- Sample size: {len(sentiment_data)} headlines analyzed"
        ]
        
        # Add recent sentiment examples
        for item in sentiment_data[:3]:
            headline = item.get('headline', 'Unknown headline')[:100] + "..." if len(item.get('headline', '')) > 100 else item.get('headline', '')
            score = item.get('sentiment_score', 0)
            formatted.append(f"- \"{headline}\" (sentiment: {score:.2f})")
        
        return "\n".join(formatted)
    
    def _format_historical_context(self, historical_data: Dict) -> str:
        """Format historical pattern analysis for prompt"""
        if not historical_data or historical_data.get('event_count', 0) == 0:
            return "Insufficient historical data for pattern analysis."
        
        event_count = historical_data.get('event_count', 0)
        gap_up_prob = historical_data.get('gap_up_prob', 0.5)
        gap_down_prob = historical_data.get('gap_down_prob', 0.5)
        avg_gap_size = historical_data.get('avg_gap_size', 0)
        pattern_confidence = historical_data.get('pattern_confidence', 0)
        
        formatted = [
            f"- Historical events analyzed: {event_count}",
            f"- Gap up probability: {gap_up_prob:.0%}",
            f"- Gap down probability: {gap_down_prob:.0%}",
            f"- Average gap size: {avg_gap_size:.1f}%",
            f"- Pattern reliability: {pattern_confidence:.0%}"
        ]
        
        # Add interpretation
        if gap_up_prob > 0.7:
            formatted.append("- Historical bias: STRONGLY BULLISH after similar events")
        elif gap_down_prob > 0.7:
            formatted.append("- Historical bias: STRONGLY BEARISH after similar events")
        elif abs(gap_up_prob - gap_down_prob) < 0.2:
            formatted.append("- Historical bias: NEUTRAL/MIXED reactions to similar events")
        
        return "\n".join(formatted)
    
    def _format_futures_data(self, futures_data: Dict) -> str:
        """Format futures market data for prompt"""
        if not futures_data:
            return "No futures market data available."
        
        change_percent = futures_data.get('change_percent', 0)
        direction = futures_data.get('direction', 'neutral')
        volume = futures_data.get('volume', 'unknown')
        timestamp = futures_data.get('timestamp', 'unknown')
        
        return f"""- Overnight futures: {change_percent:+.2f}% ({direction})
- Futures volume: {volume}
- Last update: {timestamp}
- Market expectation: {'bullish' if change_percent > 0.2 else 'bearish' if change_percent < -0.2 else 'neutral'}"""
    
    def _format_vector_evidence(self, evidence: List) -> str:
        """Format vector DB evidence for prompt"""
        if not evidence:
            return "No relevant evidence found in knowledge base."
        
        formatted = []
        for item in evidence[:4]:  # Top 4 pieces of evidence
            source = item.get('source', 'unknown')
            text = item.get('text', '')[:150] + "..." if len(item.get('text', '')) > 150 else item.get('text', '')
            timestamp = item.get('timestamp', 'unknown time')
            formatted.append(f"- {source}: \"{text}\" ({timestamp})")
        
        return "\n".join(formatted)
```

### 5. `/backend/db/queries/macro_queries.py`
**Purpose**: SQL queries for macro events, sentiment, and gap history

```python
import asyncpg
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ..postgres_handler import PostgresHandler

class MacroQueries:
    def __init__(self):
        self.db = PostgresHandler()
    
    async def asset_exists(self, asset: str) -> bool:
        """Check if asset exists in assets table"""
        query = "SELECT 1 FROM assets WHERE ticker = $1 LIMIT 1"
        result = await self.db.fetch_one(query, asset)
        return result is not None
    
    async def get_recent_macro_events(self, asset: str, cutoff_time: datetime) -> List[Dict]:
        """
        Get recent regulatory/macro events that could affect gap direction
        """
        query = """
        SELECT 
            ticker,
            title,
            body,
            source,
            severity,
            event_type,
            published_at
        FROM regulatory_events 
        WHERE published_at >= $1
        AND (ticker = $2 OR ticker IS NULL)  -- Asset-specific or general events
        AND event_type IN ('rate', 'monetary', 'fomc', 'sec', 'rbi', 'fed', 'inflation', 'employment')
        ORDER BY published_at DESC, severity DESC
        LIMIT 20
        """
        
        results = await self.db.fetch_all(query, cutoff_time, asset)
        return [dict(row) for row in results]
    
    async def get_macro_sentiment(self, asset: str, hours_back: int = 24) -> List[Dict]:
        """
        Get macro-focused sentiment from news headlines
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        query = """
        SELECT 
            ns.sentiment_score,
            ns.sentiment_label,
            ns.confidence,
            ns.timestamp,
            nh.headline,
            nh.source
        FROM news_sentiment ns
        JOIN news_headlines nh ON ns.headline_id = nh.id
        WHERE (nh.ticker = $1 OR nh.ticker IS NULL)
        AND ns.timestamp >= $2
        AND (
            LOWER(nh.headline) LIKE '%fed%' OR
            LOWER(nh.headline) LIKE '%fomc%' OR
            LOWER(nh.headline) LIKE '%rate%' OR
            LOWER(nh.headline) LIKE '%inflation%' OR
            LOWER(nh.headline) LIKE '%rbi%' OR
            LOWER(nh.headline) LIKE '%powell%' OR
            LOWER(nh.headline) LIKE '%monetary%' OR
            LOWER(nh.headline) LIKE '%policy%'
        )
        ORDER BY ns.timestamp DESC
        LIMIT 50
        """
        
        results = await self.db.fetch_all(query, asset, cutoff_time)
        return [dict(row) for row in results]
    
    async def get_historical_gaps(self, asset: str, event_type: Optional[str] = None) -> List[Dict]:
        """
        Get historical gap data for pattern analysis
        """
        base_query = """
        SELECT 
            date,
            previous_close,
            next_open,
            gap_percent,
            direction,
            reason,
            inserted_at
        FROM price_gaps 
        WHERE ticker = $1
        """
        
        if event_type:
            query = base_query + " AND LOWER(reason) LIKE $2 ORDER BY date DESC LIMIT 50"
            results = await self.db.fetch_all(query, asset, f"%{event_type.lower()}%")
        else:
            query = base_query + " ORDER BY date DESC LIMIT 100"
            results = await self.db.fetch_all(query, asset)
        
        return [dict(row) for row in results]
    
    async def get_gap_history(self, asset: str, event_type: Optional[str], limit: int) -> List[Dict]:
        """
        Get gap history with optional event type filter
        """
        return await self.get_historical_gaps(asset, event_type)[:limit]
    
    async def get_futures_data(self, asset: str) -> Dict:
        """
        Get overnight futures data if available
        Note: This requires futures data ingestion - simplified for now
        """
        # In a real implementation, this would query futures/pre-market data
        # For now, return mock structure
        query = """
        SELECT 
            close as last_price,
            timestamp
        FROM market_prices 
        WHERE ticker = $1
        ORDER BY timestamp DESC 
        LIMIT 1
        """
        
        result = await self.db.fetch_one(query, asset)
        if not result:
            return {}
        
        # Mock futures calculation (in real implementation, use actual futures data)
        return {
            "change_percent": 0.0,  # Would be calculated from actual futures
            "direction": "neutral",
            "volume": "unknown",
            "timestamp": result['timestamp'].isoformat() if result['timestamp'] else None
        }
    
    async def get_recent_market_context(self, asset: str) -> Dict:
        """
        Get recent market context for regime analysis
        """
        query = """
        WITH recent_prices AS (
            SELECT 
                close,
                timestamp,
                LAG(close, 30) OVER (ORDER BY timestamp) as price_30d_ago
            FROM market_prices 
            WHERE ticker = $1
            AND timestamp >= NOW() - INTERVAL '35 days'
            ORDER BY timestamp DESC
        ),
        volatility_calc AS (
            SELECT 
                STDDEV(close) / AVG(close) * 100 as volatility_30d
            FROM market_prices 
            WHERE ticker = $1
            AND timestamp >= NOW() - INTERVAL '30 days'
        )
        SELECT 
            rp.close as current_price,
            rp.price_30d_ago,
            ((rp.close - rp.price_30d_ago) / rp.price_30d_ago * 100) as price_trend_30d,
            vc.volatility_30d
        FROM recent_prices rp
        CROSS JOIN volatility_calc vc
        WHERE rp.price_30d_ago IS NOT NULL
        LIMIT 1
        """
        
        result = await self.db.fetch_one(query, asset)
        return dict(result) if result else {}
    
    async def record_gap_prediction(self, asset: str, prediction: str, confidence: float, context: str) -> bool:
        """
        Store gap predictions for later accuracy tracking
        """
        query = """
        INSERT INTO gap_predictions (ticker, prediction, confidence, context, predicted_at)
        VALUES ($1, $2, $3, $4, NOW())
        """
        
        try:
            await self.db.execute(query, asset, prediction, confidence, context)
            return True
        except Exception:
            return False
    
    async def get_sector_macro_sensitivity(self, asset: str) -> Dict:
        """
        Get sector-specific macro sensitivity data
        """
        # This would analyze how different sectors react to macro events
        # Simplified implementation
        
        sector_sensitivities = {
            "NASDAQ": {"rate_sensitivity": "high", "inflation_sensitivity": "high"},
            "SPY": {"rate_sensitivity": "medium", "inflation_sensitivity": "medium"},
            "BTC": {"rate_sensitivity": "high", "inflation_sensitivity": "medium"},
            "NIFTY": {"rate_sensitivity": "medium", "inflation_sensitivity": "high"}
        }
        
        return sector_sensitivities.get(asset, {"rate_sensitivity": "medium", "inflation_sensitivity": "medium"})
```

## 🔧 INTEGRATION WITH EXISTING SYSTEM

### Vector Store Integration
Add this method to retrieve macro-focused evidence:

```python
# In vector_store.py, add this method:
async def retrieve_macro_evidence(self, asset: str, question: str, limit: int = 5):
    """Retrieve macro/regulatory evidence from vector DB"""
    
    # Enhanced search for macro content
    macro_query = f"macro economic federal reserve FOMC RBI regulatory {asset} {question}"
    
    filter_conditions = {
        "$or": [
            {"ticker": asset},
            {"risk_type": {"$in": ["regulatory", "macro", "sentiment"]}},
            {"source": {"$in": ["fed", "rbi", "sec", "treasury", "perplexity"]}}
        ]
    }
    
    results = await self.collection.query(
        query_texts=[macro_query],
        where=filter_conditions,
        n_results=limit
    )
    
    return self._format_results(results)
```

### LLM Engine Integration
Add this response format:

```python
# In llama_engine.py, add this response format:
RESPONSE_FORMATS = {
    "gap_prediction": {
        "asset": "string",
        "expected_gap": "string - one of: gap up, gap down, slight gap up, slight gap down, strong gap up, strong gap down, neutral",
        "drivers": "array of strings - specific reasons for gap prediction",
        "confidence": "float between 0 and 1"
    }
}
```

## 📝 TESTING YOUR IMPLEMENTATION

### 1. Unit Tests (`tests/test_member3_macro_gap.py`)
```python
import pytest
from datetime import datetime
from backend.services.member3.macro_gap_service import MacroGapService

@pytest.mark.asyncio
async def test_macro_gap_valid_request():
    service = MacroGapService()
    
    result = await service.predict_gap(
        asset="NASDAQ",
        question="What happens after FOMC announcement?"
    )
    
    assert "asset" in result
    assert "expected_gap" in result
    assert "drivers" in result
    assert "confidence" in result
    assert 0 <= result["confidence"] <= 1

@pytest.mark.asyncio
async def test_historical_pattern_analysis():
    from backend.services.member3.gap_analyzer import GapAnalyzer
    
    analyzer = GapAnalyzer()
    
    # Mock data
    mock_events = [{"event_type": "fomc", "severity": "high"}]
    mock_history = [
        {"direction": "up", "gap_percent": 1.5, "reason": "fomc dovish"},
        {"direction": "up", "gap_percent": 2.1, "reason": "fed rate cut"}
    ]
    
    result = await analyzer.analyze_patterns("NASDAQ", mock_events, mock_history)
    
    assert "gap_up_prob" in result
    assert "pattern_confidence" in result
```

### 2. API Tests (Postman/curl)
```bash
# Test gap prediction
curl -X POST "http://localhost:8000/member3/macro-gap" \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "NASDAQ",
    "question": "What happens after FOMC announcement?"
  }'

# Test recent macro events
curl -X GET "http://localhost:8000/member3/macro-events/NASDAQ?days_back=7"

# Test gap history
curl -X GET "http://localhost:8000/member3/gap-history/NASDAQ?event_type=fomc&limit=10"
```

## 🚀 DEPLOYMENT CHECKLIST

- [ ] Create all 5 files listed above
- [ ] Add route to main app.py: `app.include_router(macro_gap_routes.router)`
- [ ] Add gap_predictions table to database schema
- [ ] Test with real macro events and gap data
- [ ] Add comprehensive logging for prediction tracking
- [ ] Create unit tests for each component
- [ ] Test all API endpoints with various scenarios
- [ ] Add monitoring for prediction accuracy
- [ ] Submit PR for code review

## 🔍 EXAMPLE DATA FLOW

**Input**: `{"asset": "NASDAQ", "question": "What happens after FOMC announcement?"}`

**Macro Events Detected**: Fed rate pause announcement (dovish tone)

**Historical Analysis**: 
- 15 similar FOMC events found
- 73% resulted in gap up
- Average gap size: +1.2%

**Current Context**:
- Macro sentiment: +0.63 (positive)
- Futures: +0.8% overnight
- No major conflicting events

**LLM Prediction**:
```json
{
  "expected_gap": "gap up",
  "drivers": [
    "dovish FOMC tone signals rate pause",
    "73% historical gap up after similar Fed announcements", 
    "positive overnight futures (+0.8%)",
    "improved macro sentiment (+0.63)"
  ],
  "confidence": 0.71
}
```

This comprehensive implementation provides a robust macro-driven gap prediction system with historical pattern analysis and high-quality evidence integration!
