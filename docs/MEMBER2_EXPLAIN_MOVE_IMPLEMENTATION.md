# MEMBER-2: SUDDEN MARKET MOVE EXPLAINER - COMPLETE IMPLEMENTATION GUIDE

## 🎯 MISSION
Explain why a ticker suddenly moved up or down by analyzing evidence (news, sentiment, outages, anomalies) around a given timestamp and generating a concise, natural-language explanation.

## 📊 WHAT YOU'RE BUILDING
**Input**: Ticker + Timestamp when the move occurred
**Output**: Clear explanation of what caused the price movement + supporting evidence

### Example Interaction
```json
Request:
POST /member2/explain-move
{
  "ticker": "BTC",
  "timestamp": "2025-11-10T14:30:00Z"
}

Response:
{
  "ticker": "BTC",
  "summary": "BTC dropped 4.8% after Binance halted withdrawals and negative sentiment spiked on social media.",
  "primary_causes": [
    "exchange outage (Binance)",
    "liquidity shrinkage", 
    "whale selling pressure",
    "negative sentiment cascade"
  ],
  "confidence": 0.78,
  "evidence_used": [
    {
      "source": "finnhub", 
      "snippet": "Binance suspended withdrawals due to technical issues",
      "timestamp": "2025-11-10T14:25:00Z"
    },
    {
      "source": "news_sentiment",
      "snippet": "Sentiment score dropped to -0.62 from neutral",
      "timestamp": "2025-11-10T14:28:00Z"
    }
  ]
}
```

## 🏗️ ARCHITECTURE OVERVIEW
```
Frontend → POST /member2/explain-move → explain_move_routes.py
    ↓
explain_move_service.py
    ↓
├── move_queries.py (price changes, anomalies, sentiment, outages)
├── vector_store.py (retrieve timestamped evidence)
├── time_utils.py (timestamp window calculations)
└── llama_engine.py (generate explanation)
    ↓
Structured JSON Response
```

## 📁 FILES YOU NEED TO CREATE

### 1. `/backend/routes/member2/explain_move_routes.py`
**Purpose**: REST API endpoint that validates timestamp/ticker and calls service layer

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional
import logging
from ...services.member2.explain_move_service import ExplainMoveService

# Request/Response Models
class ExplainMoveRequest(BaseModel):
    ticker: str
    timestamp: str  # ISO format: "2025-11-10T14:30:00Z"
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError('Invalid timestamp format. Use ISO format: 2025-11-10T14:30:00Z')
    
    @validator('ticker')
    def validate_ticker(cls, v):
        if not v or len(v) > 10:
            raise ValueError('Ticker must be provided and less than 10 characters')
        return v.upper()

class ExplainMoveResponse(BaseModel):
    ticker: str
    summary: str
    primary_causes: list[str]
    confidence: float
    evidence_used: list[dict]
    price_movement: Optional[dict] = None

# Router Setup
router = APIRouter(prefix="/member2", tags=["Member2-ExplainMove"])
move_service = ExplainMoveService()

@router.post("/explain-move", response_model=ExplainMoveResponse)
async def explain_sudden_move(request: ExplainMoveRequest):
    """
    Explain why a ticker suddenly moved at a specific timestamp
    
    Returns analysis of price movement with supporting evidence:
    - News sentiment changes
    - Infrastructure outages  
    - Market anomalies
    - Regulatory events
    """
    try:
        # Parse and validate timestamp
        target_time = datetime.fromisoformat(request.timestamp.replace('Z', '+00:00'))
        
        # Validate ticker exists
        if not await move_service.validate_ticker(request.ticker):
            raise HTTPException(status_code=400, detail=f"Ticker {request.ticker} not found in our database")
        
        # Check if significant movement occurred
        movement_data = await move_service.detect_movement(request.ticker, target_time)
        if not movement_data.get('significant_move'):
            raise HTTPException(
                status_code=404, 
                detail=f"No significant price movement detected for {request.ticker} around {request.timestamp}"
            )
        
        # Analyze the movement
        result = await move_service.analyze_movement(
            ticker=request.ticker,
            timestamp=target_time
        )
        
        # Add movement data to response
        result['price_movement'] = movement_data
        
        return ExplainMoveResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Move explanation error for {request.ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis")

@router.get("/detect-moves/{ticker}")
async def detect_recent_moves(ticker: str, hours_back: int = 24):
    """
    Helper endpoint to find recent significant moves for a ticker
    Useful for frontend to suggest timestamps to analyze
    """
    try:
        moves = await move_service.find_recent_moves(ticker, hours_back)
        return {"ticker": ticker, "recent_moves": moves}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error detecting moves")
```

**Key Responsibilities**:
- ✅ Validate timestamp format and ticker existence
- ✅ Check if significant movement actually occurred
- ✅ Handle edge cases (no movement, invalid times)
- ✅ Provide helper endpoint to detect recent moves

### 2. `/backend/services/member2/explain_move_service.py`
**Purpose**: Core orchestration logic - detects movement, gathers evidence, calls LLM

```python
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from ...db.queries.move_queries import MoveQueries
from ...rag_engine.vector_store import VectorStore
from ...rag_engine.llama_engine import LlamaEngine
from ...utils.time_utils import TimeUtils
from .explain_move_prompt import ExplainMovePrompt

class ExplainMoveService:
    def __init__(self):
        self.queries = MoveQueries()
        self.vector_store = VectorStore()
        self.llm = LlamaEngine()
        self.time_utils = TimeUtils()
        self.prompt_builder = ExplainMovePrompt()
        
        # Movement detection thresholds
        self.SIGNIFICANT_MOVE_THRESHOLD = 2.0  # 2% price change
        self.ANALYSIS_WINDOW_MINUTES = 30      # ±30 minutes around timestamp
    
    async def validate_ticker(self, ticker: str) -> bool:
        """Check if ticker exists in assets table"""
        return await self.queries.ticker_exists(ticker)
    
    async def detect_movement(self, ticker: str, timestamp: datetime) -> Dict:
        """
        Detect if significant price movement occurred around timestamp
        Returns movement data or indicates no significant move
        """
        # Define time window for movement detection  
        start_time = timestamp - timedelta(minutes=15)
        end_time = timestamp + timedelta(minutes=15)
        
        # Get price data around the timestamp
        price_data = await self.queries.get_price_movement(ticker, start_time, end_time)
        
        if not price_data:
            return {"significant_move": False, "reason": "No price data available"}
        
        # Calculate price change percentage
        price_change = self._calculate_price_change(price_data)
        
        is_significant = abs(price_change.get('percent_change', 0)) >= self.SIGNIFICANT_MOVE_THRESHOLD
        
        return {
            "significant_move": is_significant,
            "price_change": price_change,
            "threshold_used": self.SIGNIFICANT_MOVE_THRESHOLD,
            "window_minutes": 15
        }
    
    async def analyze_movement(self, ticker: str, timestamp: datetime) -> Dict:
        """
        Main analysis function - gathers all evidence and generates explanation
        """
        # Define analysis window
        start_time = timestamp - timedelta(minutes=self.ANALYSIS_WINDOW_MINUTES)
        end_time = timestamp + timedelta(minutes=self.ANALYSIS_WINDOW_MINUTES)
        
        # Gather all evidence in parallel
        evidence_tasks = [
            self.queries.get_price_movement(ticker, start_time, end_time),
            self.queries.get_anomalies_in_window(ticker, start_time, end_time),
            self.queries.get_sentiment_in_window(ticker, start_time, end_time),
            self.queries.get_infrastructure_incidents(start_time, end_time),
            self.vector_store.retrieve_timestamped_evidence(ticker, timestamp, self.ANALYSIS_WINDOW_MINUTES)
        ]
        
        price_data, anomalies, sentiment_data, infra_incidents, vector_evidence = await asyncio.gather(*evidence_tasks)
        
        # Build comprehensive context
        context = {
            "ticker": ticker,
            "timestamp": timestamp,
            "price_data": price_data,
            "anomalies": anomalies,
            "sentiment_data": sentiment_data,
            "infra_incidents": infra_incidents,
            "vector_evidence": vector_evidence,
            "time_window": f"{start_time.isoformat()} to {end_time.isoformat()}"
        }
        
        # Generate LLM explanation
        prompt = self.prompt_builder.build_explanation_prompt(context)
        
        llm_response = await self.llm.generate_structured_response(
            prompt=prompt,
            response_format="movement_explanation"
        )
        
        # Format and validate response
        return self._format_movement_response(llm_response, context)
    
    async def find_recent_moves(self, ticker: str, hours_back: int) -> List[Dict]:
        """
        Find recent significant movements for a ticker
        Useful for suggesting timestamps to analyze
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        movements = await self.queries.find_significant_movements(
            ticker, 
            cutoff_time, 
            self.SIGNIFICANT_MOVE_THRESHOLD
        )
        
        return movements
    
    def _calculate_price_change(self, price_data: List[Dict]) -> Dict:
        """Calculate price movement metrics from price data"""
        if len(price_data) < 2:
            return {"percent_change": 0, "absolute_change": 0}
        
        # Sort by timestamp to get before/after prices
        sorted_prices = sorted(price_data, key=lambda x: x['timestamp'])
        start_price = sorted_prices[0]['close']
        end_price = sorted_prices[-1]['close']
        
        absolute_change = end_price - start_price
        percent_change = (absolute_change / start_price) * 100 if start_price > 0 else 0
        
        return {
            "start_price": start_price,
            "end_price": end_price,
            "absolute_change": absolute_change,
            "percent_change": round(percent_change, 2),
            "direction": "up" if percent_change > 0 else "down" if percent_change < 0 else "flat"
        }
    
    def _format_movement_response(self, llm_response: Dict, context: Dict) -> Dict:
        """Format LLM output into standardized API response"""
        
        # Extract price movement info
        price_change = self._calculate_price_change(context.get('price_data', []))
        
        return {
            "ticker": llm_response.get("ticker", context["ticker"]),
            "summary": llm_response.get("summary", "Unable to determine cause of movement"),
            "primary_causes": llm_response.get("primary_causes", []),
            "confidence": min(max(llm_response.get("confidence", 0.3), 0), 1),
            "evidence_used": self._format_evidence_list(context),
            "price_movement": price_change
        }
    
    def _format_evidence_list(self, context: Dict) -> List[Dict]:
        """Compile evidence from all sources into unified format"""
        evidence = []
        
        # Add sentiment evidence
        for sentiment in context.get('sentiment_data', [])[:2]:
            evidence.append({
                "source": "sentiment_analysis", 
                "snippet": f"Sentiment score: {sentiment.get('sentiment_score', 0):.2f} ({sentiment.get('sentiment_label', 'neutral')})",
                "timestamp": sentiment.get('timestamp', '').isoformat() if sentiment.get('timestamp') else None
            })
        
        # Add anomaly evidence  
        for anomaly in context.get('anomalies', [])[:2]:
            evidence.append({
                "source": "anomaly_detection",
                "snippet": f"{anomaly.get('metric', 'unknown')}: {anomaly.get('explanation', 'Anomaly detected')}",
                "timestamp": anomaly.get('timestamp', '').isoformat() if anomaly.get('timestamp') else None
            })
        
        # Add infrastructure incidents
        for incident in context.get('infra_incidents', [])[:2]:
            evidence.append({
                "source": "infrastructure_monitoring",
                "snippet": f"{incident.get('platform', 'Unknown platform')}: {incident.get('description', 'Incident reported')}",
                "timestamp": incident.get('started_at', '').isoformat() if incident.get('started_at') else None
            })
        
        # Add vector DB evidence
        for item in context.get('vector_evidence', [])[:3]:
            evidence.append({
                "source": item.get('source', 'news'),
                "snippet": item.get('text', '')[:150] + "..." if len(item.get('text', '')) > 150 else item.get('text', ''),
                "timestamp": item.get('timestamp')
            })
        
        return evidence[:6]  # Limit to top 6 pieces of evidence
```

### 3. `/backend/services/member2/explain_move_prompt.py`
**Purpose**: LLM prompt templates for generating movement explanations

```python
class ExplainMovePrompt:
    def __init__(self):
        self.system_prompt = """You are an expert financial market analyst specializing in explaining sudden price movements.
        
        Your job is to analyze price movements and provide clear, factual explanations based on available evidence.
        
        Rules:
        - Be precise and factual, avoid speculation
        - Prioritize evidence with timestamps close to the movement
        - List primary causes in order of likely impact
        - Give honest confidence scores (low confidence for limited evidence)
        - Use simple language that any investor can understand
        - Focus on what happened, not what might happen next
        """
    
    def build_explanation_prompt(self, context: Dict) -> str:
        """Build complete prompt with movement context and evidence"""
        
        ticker = context['ticker']
        timestamp = context['timestamp'].isoformat()
        
        # Format all evidence sections
        price_info = self._format_price_context(context.get('price_data', []))
        anomaly_info = self._format_anomaly_context(context.get('anomalies', []))
        sentiment_info = self._format_sentiment_context(context.get('sentiment_data', []))
        incident_info = self._format_incident_context(context.get('infra_incidents', []))
        news_info = self._format_news_context(context.get('vector_evidence', []))
        
        user_prompt = f"""
MOVEMENT ANALYSIS REQUEST:
Ticker: {ticker}
Target Timestamp: {timestamp}
Analysis Window: {context.get('time_window', 'Unknown')}

OBSERVED PRICE MOVEMENT:
{price_info}

DETECTED ANOMALIES:
{anomaly_info}

SENTIMENT ANALYSIS:
{sentiment_info}

INFRASTRUCTURE INCIDENTS:
{incident_info}

RELEVANT NEWS & EVENTS:
{news_info}

REQUIRED OUTPUT FORMAT (JSON):
{{
    "ticker": "{ticker}",
    "summary": "2-3 sentence explanation of what caused the movement",
    "primary_causes": [
        "Most likely cause with specific details",
        "Second most likely cause", 
        "Third cause if applicable"
    ],
    "confidence": 0.75
}}

IMPORTANT:
- Base confidence on quality and timing of evidence
- If evidence is weak or contradictory, use confidence < 0.5
- If multiple strong pieces of evidence align, confidence can be > 0.8
- Include specific numbers/percentages when available
- Order causes by likely impact on price

Analyze the movement and provide explanation:
"""
        return self.system_prompt + "\n\n" + user_prompt
    
    def _format_price_context(self, price_data: List) -> str:
        """Format price movement data for the prompt"""
        if not price_data:
            return "No price data available for analysis."
        
        sorted_prices = sorted(price_data, key=lambda x: x['timestamp'])
        if len(sorted_prices) >= 2:
            start_price = sorted_prices[0]['close']
            end_price = sorted_prices[-1]['close']
            change = ((end_price - start_price) / start_price) * 100
            
            return f"""- Price moved from ${start_price:.2f} to ${end_price:.2f}
- Change: {change:+.2f}% ({'up' if change > 0 else 'down'})
- Volume during period: {sorted_prices[-1].get('volume', 'N/A'):,}"""
        
        return f"- Latest price: ${price_data[0].get('close', 'N/A')}"
    
    def _format_anomaly_context(self, anomalies: List) -> str:
        """Format anomaly data for the prompt"""
        if not anomalies:
            return "No significant anomalies detected during this period."
        
        formatted = []
        for anomaly in anomalies[:3]:
            formatted.append(
                f"- {anomaly.get('metric', 'unknown').title()}: {anomaly.get('explanation', 'Anomaly detected')} "
                f"(severity: {anomaly.get('severity', 'unknown')}, score: {anomaly.get('anomaly_score', 0):.2f}) "
                f"at {anomaly.get('timestamp', 'unknown time')}"
            )
        return "\n".join(formatted)
    
    def _format_sentiment_context(self, sentiment_data: List) -> str:
        """Format sentiment analysis data for the prompt"""
        if not sentiment_data:
            return "No sentiment data available for this period."
        
        # Calculate average sentiment and trend
        scores = [s.get('sentiment_score', 0) for s in sentiment_data if s.get('sentiment_score') is not None]
        if not scores:
            return "No valid sentiment scores found."
        
        avg_score = sum(scores) / len(scores)
        trend = "positive" if avg_score > 0.1 else "negative" if avg_score < -0.1 else "neutral"
        
        formatted = [f"- Average sentiment: {avg_score:.2f} ({trend})"]
        
        # Add recent headlines
        for item in sentiment_data[:3]:
            headline = item.get('headline', 'Unknown headline')[:80] + "..." if len(item.get('headline', '')) > 80 else item.get('headline', '')
            formatted.append(f"- \"{headline}\" (score: {item.get('sentiment_score', 0):.2f})")
        
        return "\n".join(formatted)
    
    def _format_incident_context(self, incidents: List) -> str:
        """Format infrastructure incident data for the prompt"""
        if not incidents:
            return "No infrastructure incidents reported during this period."
        
        formatted = []
        for incident in incidents[:3]:
            formatted.append(
                f"- {incident.get('platform', 'Unknown platform')}: {incident.get('description', 'Incident occurred')} "
                f"(severity: {incident.get('severity', 'unknown')}) "
                f"started at {incident.get('started_at', 'unknown time')}"
            )
        return "\n".join(formatted)
    
    def _format_news_context(self, news_evidence: List) -> str:
        """Format vector DB news evidence for the prompt"""
        if not news_evidence:
            return "No relevant news or events found in the knowledge base."
        
        formatted = []
        for item in news_evidence[:4]:
            source = item.get('source', 'unknown')
            text = item.get('text', '')[:120] + "..." if len(item.get('text', '')) > 120 else item.get('text', '')
            timestamp = item.get('timestamp', 'unknown time')
            formatted.append(f"- {source}: \"{text}\" ({timestamp})")
        
        return "\n".join(formatted)
```

### 4. `/backend/db/queries/move_queries.py`
**Purpose**: SQL queries to fetch price movements, anomalies, sentiment, and incidents

```python
import asyncpg
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ..postgres_handler import PostgresHandler

class MoveQueries:
    def __init__(self):
        self.db = PostgresHandler()
    
    async def ticker_exists(self, ticker: str) -> bool:
        """Check if ticker exists in assets table"""
        query = "SELECT 1 FROM assets WHERE ticker = $1 LIMIT 1"
        result = await self.db.fetch_one(query, ticker)
        return result is not None
    
    async def get_price_movement(self, ticker: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """
        Get price data in a specific time window for movement analysis
        """
        query = """
        SELECT 
            timestamp,
            open,
            high, 
            low,
            close,
            volume
        FROM market_prices 
        WHERE ticker = $1 
        AND timestamp BETWEEN $2 AND $3
        ORDER BY timestamp ASC
        """
        
        results = await self.db.fetch_all(query, ticker, start_time, end_time)
        return [dict(row) for row in results]
    
    async def get_anomalies_in_window(self, ticker: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """
        Get anomalies detected during the time window
        Focus on volume, liquidity, and volatility anomalies
        """
        query = """
        SELECT 
            metric,
            anomaly_score,
            severity, 
            explanation,
            timestamp
        FROM anomalies 
        WHERE ticker = $1
        AND timestamp BETWEEN $2 AND $3
        AND metric IN ('volume', 'liquidity', 'volatility', 'price_spike')
        ORDER BY anomaly_score DESC, timestamp DESC
        """
        
        results = await self.db.fetch_all(query, ticker, start_time, end_time)
        return [dict(row) for row in results]
    
    async def get_sentiment_in_window(self, ticker: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """
        Get news sentiment during the time window
        """
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
        WHERE nh.ticker = $1 OR nh.ticker IS NULL
        AND ns.timestamp BETWEEN $2 AND $3
        ORDER BY ns.timestamp DESC
        LIMIT 10
        """
        
        results = await self.db.fetch_all(query, ticker, start_time, end_time)
        return [dict(row) for row in results]
    
    async def get_infrastructure_incidents(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """
        Get infrastructure incidents (exchange outages, blockchain issues) during time window
        """
        query = """
        SELECT 
            platform,
            incident_type,
            description,
            severity,
            started_at,
            resolved_at,
            source
        FROM infra_incidents 
        WHERE started_at BETWEEN $1 AND $2
        OR (resolved_at IS NOT NULL AND resolved_at BETWEEN $1 AND $2)
        ORDER BY started_at DESC
        """
        
        results = await self.db.fetch_all(query, start_time, end_time)
        return [dict(row) for row in results]
    
    async def find_significant_movements(self, ticker: str, cutoff_time: datetime, threshold_percent: float) -> List[Dict]:
        """
        Find timestamps where significant price movements occurred
        Used for the helper endpoint to suggest analysis targets
        """
        query = """
        WITH price_changes AS (
            SELECT 
                timestamp,
                close,
                LAG(close) OVER (ORDER BY timestamp) as prev_close,
                volume
            FROM market_prices 
            WHERE ticker = $1 
            AND timestamp >= $2
            ORDER BY timestamp
        )
        SELECT 
            timestamp,
            close,
            prev_close,
            ((close - prev_close) / prev_close * 100) as percent_change,
            volume
        FROM price_changes
        WHERE prev_close IS NOT NULL
        AND ABS((close - prev_close) / prev_close * 100) >= $3
        ORDER BY ABS((close - prev_close) / prev_close * 100) DESC
        LIMIT 20
        """
        
        results = await self.db.fetch_all(query, ticker, cutoff_time, threshold_percent)
        return [dict(row) for row in results]
    
    async def get_volume_spike_context(self, ticker: str, target_time: datetime, window_hours: int = 2) -> Dict:
        """
        Get volume context around a movement to detect volume spikes
        """
        start_time = target_time - timedelta(hours=window_hours)
        end_time = target_time + timedelta(hours=window_hours)
        
        query = """
        SELECT 
            AVG(volume) as avg_volume,
            MAX(volume) as max_volume,
            MIN(volume) as min_volume,
            COUNT(*) as data_points
        FROM market_prices 
        WHERE ticker = $1
        AND timestamp BETWEEN $2 AND $3
        """
        
        result = await self.db.fetch_one(query, ticker, start_time, end_time)
        return dict(result) if result else {}
    
    async def get_regulatory_events_in_window(self, start_time: datetime, end_time: datetime, tickers: List[str] = None) -> List[Dict]:
        """
        Get regulatory events that might have caused market movements
        """
        base_query = """
        SELECT 
            ticker,
            title,
            body,
            source,
            severity,
            event_type,
            published_at
        FROM regulatory_events 
        WHERE published_at BETWEEN $1 AND $2
        """
        
        if tickers:
            ticker_filter = " AND (ticker = ANY($3) OR ticker IS NULL)"
            query = base_query + ticker_filter
            results = await self.db.fetch_all(query, start_time, end_time, tickers)
        else:
            results = await self.db.fetch_all(base_query, start_time, end_time)
        
        return [dict(row) for row in results]
```

### 5. `/backend/utils/time_utils.py`
**Purpose**: Time manipulation utilities for window calculations

```python
from datetime import datetime, timedelta
from typing import Tuple
import pytz

class TimeUtils:
    def __init__(self):
        self.utc = pytz.UTC
    
    def create_analysis_window(self, timestamp: datetime, window_minutes: int = 30) -> Tuple[datetime, datetime]:
        """
        Create start/end times for analysis window around a target timestamp
        """
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=self.utc)
        
        start_time = timestamp - timedelta(minutes=window_minutes)
        end_time = timestamp + timedelta(minutes=window_minutes)
        
        return start_time, end_time
    
    def format_time_window(self, start_time: datetime, end_time: datetime) -> str:
        """
        Format time window for display/logging
        """
        return f"{start_time.isoformat()} to {end_time.isoformat()}"
    
    def is_market_hours(self, timestamp: datetime, exchange: str = "NYSE") -> bool:
        """
        Check if timestamp falls within market hours (basic implementation)
        """
        # Convert to EST for US markets
        if exchange in ["NYSE", "NASDAQ"]:
            est = pytz.timezone('US/Eastern')
            local_time = timestamp.astimezone(est)
            
            # Check if weekday and within 9:30 AM - 4:00 PM EST
            if local_time.weekday() >= 5:  # Weekend
                return False
            
            market_open = local_time.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = local_time.replace(hour=16, minute=0, second=0, microsecond=0)
            
            return market_open <= local_time <= market_close
        
        # For crypto/24-7 markets
        return True
    
    def find_market_session(self, timestamp: datetime) -> str:
        """
        Determine which market session the timestamp falls into
        """
        est = pytz.timezone('US/Eastern')
        local_time = timestamp.astimezone(est)
        hour = local_time.hour
        
        if 4 <= hour < 9:
            return "pre_market"
        elif 9 <= hour < 16:
            return "regular_hours"
        elif 16 <= hour < 20:
            return "after_hours"
        else:
            return "overnight"
    
    def time_until_market_open(self, timestamp: datetime) -> timedelta:
        """
        Calculate time until next market open
        """
        est = pytz.timezone('US/Eastern')
        local_time = timestamp.astimezone(est)
        
        # If it's weekend, find next Monday
        if local_time.weekday() >= 5:
            days_ahead = 7 - local_time.weekday()
            next_monday = local_time + timedelta(days=days_ahead)
            market_open = next_monday.replace(hour=9, minute=30, second=0, microsecond=0)
        else:
            # Same day or next day
            market_open = local_time.replace(hour=9, minute=30, second=0, microsecond=0)
            if local_time.hour >= 16:  # After market close
                market_open += timedelta(days=1)
        
        return market_open - local_time
```

## 🔧 INTEGRATION WITH EXISTING SYSTEM

### Vector Store Integration
Add this method to retrieve timestamped evidence:

```python
# In vector_store.py, add this method:
async def retrieve_timestamped_evidence(self, ticker: str, timestamp: datetime, window_minutes: int = 30):
    """Retrieve evidence around a specific timestamp"""
    start_time = timestamp - timedelta(minutes=window_minutes)
    end_time = timestamp + timedelta(minutes=window_minutes)
    
    filter_conditions = {
        "ticker": ticker,
        "timestamp": {
            "$gte": start_time.isoformat(),
            "$lte": end_time.isoformat()
        }
    }
    
    results = await self.collection.query(
        query_texts=[f"price movement {ticker}"],
        where=filter_conditions,
        n_results=5
    )
    
    return self._format_results(results)
```

### LLM Engine Integration
Add this response format for movement explanations:

```python
# In llama_engine.py, add this response format:
RESPONSE_FORMATS = {
    "movement_explanation": {
        "ticker": "string",
        "summary": "string",
        "primary_causes": "array of strings", 
        "confidence": "float between 0 and 1"
    }
}
```

## 📝 TESTING YOUR IMPLEMENTATION

### 1. Unit Tests (`tests/test_member2_explain_move.py`)
```python
import pytest
from datetime import datetime
from backend.services.member2.explain_move_service import ExplainMoveService

@pytest.mark.asyncio
async def test_movement_detection():
    service = ExplainMoveService()
    
    # Test with known significant move
    timestamp = datetime(2025, 11, 10, 14, 30, 0)
    movement = await service.detect_movement("BTC", timestamp)
    
    assert "significant_move" in movement
    assert "price_change" in movement

@pytest.mark.asyncio
async def test_explain_move_valid_request():
    service = ExplainMoveService()
    
    # Mock a timestamp with known movement
    timestamp = datetime(2025, 11, 10, 14, 30, 0)
    
    result = await service.analyze_movement("BTC", timestamp)
    
    assert "ticker" in result
    assert "summary" in result
    assert "primary_causes" in result
    assert "confidence" in result
    assert 0 <= result["confidence"] <= 1
```

### 2. API Tests (Postman/curl)
```bash
# Test valid movement explanation
curl -X POST "http://localhost:8000/member2/explain-move" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "BTC",
    "timestamp": "2025-11-10T14:30:00Z"
  }'

# Test invalid timestamp
curl -X POST "http://localhost:8000/member2/explain-move" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "BTC", 
    "timestamp": "invalid-timestamp"
  }'

# Test recent moves detection
curl -X GET "http://localhost:8000/member2/detect-moves/BTC?hours_back=24"
```

## 🚀 DEPLOYMENT CHECKLIST

- [ ] Create all 5 files listed above
- [ ] Add route to main app.py: `app.include_router(explain_move_routes.router)`
- [ ] Test movement detection with real data
- [ ] Test timestamp validation and error handling
- [ ] Add comprehensive logging for debugging
- [ ] Create unit tests for each component
- [ ] Test API endpoints with various scenarios
- [ ] Add performance monitoring for analysis speed
- [ ] Submit PR for code review

## 🔍 EXAMPLE DATA FLOW

**Input**: `{"ticker": "BTC", "timestamp": "2025-11-10T14:30:00Z"}`

**Movement Detection**: `4.8% drop detected from $67,500 to $64,260`

**Evidence Gathering**:
```json
{
  "anomalies": [{"metric": "liquidity", "explanation": "Bid-ask spread widened 300%"}],
  "sentiment": [{"score": -0.62, "headline": "Binance halts withdrawals"}],
  "incidents": [{"platform": "Binance", "description": "Technical maintenance"}],
  "vector_evidence": [{"text": "Exchange outage causing panic selling"}]
}
```

**LLM Analysis**:
```json
{
  "summary": "BTC dropped 4.8% after Binance halted withdrawals due to technical issues, causing liquidity concerns and panic selling.",
  "primary_causes": ["exchange outage", "liquidity shrinkage", "negative sentiment cascade"],
  "confidence": 0.78
}
```

This implementation gives you a complete system to explain any sudden market movement with evidence-backed analysis!
