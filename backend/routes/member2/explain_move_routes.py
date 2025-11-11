"""
Member 2: Sudden Market Move Explainer Route
REST API endpoint for explaining sudden price movements with timestamp analysis.
"""

import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, validator

from ...services.member2.explain_move_service import ExplainMoveService

logger = logging.getLogger(__name__)

# Request/Response Models
class ExplainMoveRequest(BaseModel):
    ticker: str
    timestamp: str  # ISO format: "2025-11-10T14:30:00Z"
    
    @validator('ticker')
    def validate_ticker(cls, v):
        if not v or len(v) > 10:
            raise ValueError('Ticker must be provided and less than 10 characters')
        return v.upper()
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError('Invalid timestamp format. Use ISO format: 2025-11-10T14:30:00Z')

class ExplainMoveResponse(BaseModel):
    ticker: str
    summary: str
    primary_causes: list[str]
    confidence: float
    evidence_used: list[dict]
    price_movement: Optional[dict] = None
    timestamp: str

# Router setup
router = APIRouter(prefix="/member2", tags=["Member2-ExplainMove"])

# Initialize service
move_service = ExplainMoveService()

@router.post("/explain-move", response_model=ExplainMoveResponse)
async def explain_sudden_move(request: ExplainMoveRequest):
    """
    Explain why a ticker suddenly moved at a specific timestamp
    
    **What this endpoint does:**
    - Analyzes price movements in a ±30 minute window around timestamp
    - Gathers evidence from news, sentiment, anomalies, and infrastructure events
    - Provides clear explanations for sudden market movements
    
    **Example Request:**
    ```json
    {
        "ticker": "BTC",
        "timestamp": "2025-11-10T14:30:00Z"
    }
    ```
    """
    try:
        # Parse timestamp
        target_time = datetime.fromisoformat(request.timestamp.replace('Z', '+00:00'))
        
        # Validate ticker exists
        if not await move_service.validate_ticker(request.ticker):
            raise HTTPException(status_code=400, detail=f"Ticker {request.ticker} not found")
        
        # Analyze the movement
        result = await move_service.analyze_movement(
            ticker=request.ticker,
            timestamp=target_time
        )
        
        return ExplainMoveResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Movement explanation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/detect-moves/{ticker}")
async def detect_recent_moves(ticker: str, hours_back: int = 24):
    """
    Helper endpoint to find recent significant moves for a ticker
    Useful for frontend to suggest timestamps to analyze
    """
    try:
        if not await move_service.validate_ticker(ticker):
            raise HTTPException(status_code=400, detail=f"Ticker {ticker} not found")
        
        moves = await move_service.find_recent_moves(ticker, hours_back)
        
        return {
            "ticker": ticker.upper(),
            "recent_moves": moves,
            "hours_back": hours_back,
            "move_count": len(moves)
        }
        
    except Exception as e:
        logger.error(f"Move detection error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error detecting moves")

@router.get("/explain-move/health")
async def explain_move_health():
    """Health check for movement explanation service"""
    return {
        "service": "explain_move",
        "status": "active", 
        "message": "Movement explanation service is running"
    }

# TODO: Add these endpoints when implementing
"""
Additional endpoints to consider:

@router.get("/explain-move/anomalies/{ticker}")
async def get_recent_anomalies(ticker: str, hours_back: int = 6):
    \"\"\"Get recent anomalies that might cause movements\"\"\"
    pass

@router.get("/explain-move/timeline/{ticker}")
async def get_movement_timeline(ticker: str, start_time: str, end_time: str):
    \"\"\"Get detailed timeline of events around movement\"\"\"
    pass
"""
