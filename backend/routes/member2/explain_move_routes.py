"""
Member 2: Sudden Market Move Explainer Routes
REST API endpoints for explaining sudden price movements.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, validator
from datetime import datetime

from ...services.member2.explain_move_service import ExplainMoveService

logger = logging.getLogger(__name__)

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
    drivers: list[str]
    confidence: float
    evidence: dict  # Include evidence field
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
    - Analyzes price movements around a specific timestamp
    - Identifies news, sentiment, and market events that caused the move
    - Provides clear explanations with supporting evidence
    
    **Example Request:**
    ```json
    {
        "ticker": "BTC",
        "timestamp": "2025-11-10T14:30:00Z"
    }
    ```
    """
    try:
        # Parse and validate timestamp
        target_time = datetime.fromisoformat(request.timestamp.replace('Z', '+00:00'))
        
        # Validate ticker exists
        if not await move_service.validate_ticker(request.ticker):
            raise HTTPException(status_code=400, detail=f"Ticker {request.ticker} not found in our database")
        
        # Analyze the movement (don't require significant movement)
        result = await move_service.analyze_movement(
            ticker=request.ticker,
            timestamp=target_time
        )
        
        return ExplainMoveResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Move explanation error for {request.ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis")

@router.get("/detect-moves/{ticker}")
async def detect_recent_moves(ticker: str, hours_back: int = 24):
    """
    Helper endpoint to find recent significant moves for a ticker.
    Useful for frontend to suggest timestamps to analyze.
    """
    try:
        if not await move_service.validate_ticker(ticker):
            raise HTTPException(status_code=400, detail=f"Ticker {ticker} not found")
        
        moves = await move_service.find_recent_moves(ticker, hours_back)
        return {
            "ticker": ticker, 
            "recent_moves": moves,
            "hours_analyzed": hours_back,
            "total_moves_found": len(moves)
        }
        
    except Exception as e:
        logger.error(f"Error detecting moves for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error detecting moves")

@router.get("/explain-move/health")
async def explain_move_health():
    """Health check for explain move service"""
    return {
        "service": "explain_move", 
        "status": "active",
        "message": "Market move explanation service is running"
    }

@router.get("/explain-move/anomalies/{ticker}")
async def get_movement_anomalies(ticker: str, hours_back: int = 24):
    """Get anomalies and context around recent movements"""
    try:
        if not await move_service.validate_ticker(ticker):
            raise HTTPException(status_code=400, detail=f"Ticker {ticker} not found")
        
        # Get recent moves first
        moves = await move_service.find_recent_moves(ticker, hours_back)
        
        if not moves:
            return {
                "ticker": ticker,
                "anomalies": [],
                "message": "No significant moves found in the specified timeframe"
            }
        
        # Get context for the most recent significant move
        latest_move = moves[0]
        timestamp = datetime.fromisoformat(latest_move['timestamp'].replace('Z', '+00:00'))
        context = await move_service.get_movement_context(ticker, timestamp)
        
        return {
            "ticker": ticker,
            "latest_move": latest_move,
            "anomalies": context.get('anomalies', []),
            "sentiment_events": context.get('sentiment_events', []),
            "context_window": context.get('context_window', '')
        }
        
    except Exception as e:
        logger.error(f"Error getting anomalies for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving anomalies")

@router.get("/explain-move/timeline/{ticker}")
async def get_movement_timeline(ticker: str, timestamp: str, window_hours: int = 4):
    """Get detailed timeline of events around a movement"""
    try:
        # Validate timestamp
        target_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        if not await move_service.validate_ticker(ticker):
            raise HTTPException(status_code=400, detail=f"Ticker {ticker} not found")
        
        # Get context around the movement
        context = await move_service.get_movement_context(ticker, target_time)
        
        # Get movement data
        movement_data = await move_service.detect_movement(ticker, target_time)
        
        return {
            "ticker": ticker,
            "target_timestamp": timestamp,
            "movement_detected": movement_data,
            "timeline_events": {
                "anomalies": context.get('anomalies', []),
                "sentiment_shifts": context.get('sentiment_events', [])
            },
            "analysis_window": f"±{window_hours} hours from target time"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid timestamp: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating timeline for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating timeline")
