"""
Member 3: Macro-Driven Gap Forecaster Routes
REST API endpoints for predicting overnight gaps based on macro events.
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, validator

from ...services.member3.macro_gap_service import MacroGapService

logger = logging.getLogger(__name__)

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

class BatchGapRequest(BaseModel):
    assets: List[str]
    event_context: Optional[str] = ""
    
    @validator('assets')
    def validate_assets(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one asset must be provided')
        if len(v) > 10:
            raise ValueError('Maximum 10 assets allowed per batch request')
        return [asset.upper() for asset in v]

class MacroGapResponse(BaseModel):
    asset: str
    gap_prediction: str
    primary_catalyst: str
    supporting_factors: List[str]
    confidence: float
    risk_scenarios: List[str]
    macro_events: List[dict]
    historical_context: Optional[dict] = None
    evidence: Optional[dict] = None  # Include evidence field
    timestamp: str

# Router setup
router = APIRouter(prefix="/member3", tags=["Member3-MacroGap"])

# Initialize service
gap_service = MacroGapService()

@router.post("/macro-gap", response_model=MacroGapResponse)
async def predict_macro_gap(request: MacroGapRequest):
    """
    Predict overnight gap direction based on macro events and historical patterns
    
    **What this endpoint does:**
    - Analyzes recent regulatory/FOMC/RBI announcements
    - Reviews historical gap behavior after similar events
    - Provides gap direction predictions with confidence scores
    
    **Example Request:**
    ```json
    {
        "asset": "NASDAQ",
        "question": "What happens after the FOMC announcement?"
    }
    ```
    """
    try:
        # Validate asset exists
        if not await gap_service.validate_asset(request.asset):
            raise HTTPException(status_code=400, detail=f"Asset {request.asset} not supported")
        
        # Generate gap prediction
        result = await gap_service.predict_gap(
            asset=request.asset,
            question=request.question
        )
        
        return MacroGapResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Gap prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/macro-events/{asset}")
async def get_recent_macro_events(asset: str, days_ahead: int = 7):
    """
    Get upcoming macro events that could affect gaps
    """
    try:
        if not await gap_service.validate_asset(asset):
            raise HTTPException(status_code=400, detail=f"Asset {asset} not supported")
        
        events = await gap_service.get_macro_events(asset, days_ahead)
        return {
            "asset": asset.upper(),
            "upcoming_events": events,
            "days_ahead": days_ahead,
            "total_events": len(events)
        }
        
    except Exception as e:
        logger.error(f"Macro events error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving macro events")

@router.get("/gap-history/{asset}")
async def get_gap_history(asset: str, days_back: int = 90):
    """
    Get historical gap data for an asset
    """
    try:
        if not await gap_service.validate_asset(asset):
            raise HTTPException(status_code=400, detail=f"Asset {asset} not supported")
        
        history = await gap_service.get_gap_history(asset, days_back)
        return {
            "asset": asset.upper(),
            "historical_gaps": history,
            "days_analyzed": days_back,
            "total_gaps": len(history)
        }
        
    except Exception as e:
        logger.error(f"Gap history error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving gap history")

@router.post("/batch-gap-prediction", response_model=List[dict])
async def predict_gaps_for_multiple_assets(request: BatchGapRequest):
    """
    Predict gap impact across multiple assets
    """
    try:
        results = await gap_service.batch_gap_prediction(
            assets=request.assets,
            event_context=request.event_context or ""
        )
        return results
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error in batch prediction")

@router.get("/macro-gap/health")
async def macro_gap_health():
    """Health check for macro gap service"""
    return {
        "service": "macro_gap",
        "status": "active",
        "message": "Macro gap forecasting service is running",
        "supported_assets": list(gap_service.SUPPORTED_ASSETS)
    }

@router.get("/macro-gap/sentiment/{asset}")
async def get_sentiment_analysis(asset: str, hours_back: int = 24):
    """Get sentiment analysis that could affect gap formation"""
    try:
        if not await gap_service.validate_asset(asset):
            raise HTTPException(status_code=400, detail=f"Asset {asset} not supported")
        
        sentiment = await gap_service.get_sentiment_analysis(asset, hours_back)
        return {
            "asset": asset.upper(),
            "sentiment_analysis": sentiment,
            "hours_analyzed": hours_back
        }
        
    except Exception as e:
        logger.error(f"Sentiment analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving sentiment")

@router.get("/macro-gap/patterns/{asset}")
async def get_gap_patterns(asset: str, event_type: str = "FOMC"):
    """Get historical gap patterns for specific macro event types"""
    try:
        if not await gap_service.validate_asset(asset):
            raise HTTPException(status_code=400, detail=f"Asset {asset} not supported")
        
        patterns = await gap_service.analyze_gap_patterns(asset, event_type)
        return {
            "asset": asset.upper(),
            "event_type": event_type,
            "pattern_analysis": patterns
        }
        
    except Exception as e:
        logger.error(f"Pattern analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error analyzing patterns")

# TODO: Add these endpoints when implementing
"""
Additional endpoints to consider:

@router.get("/macro-gap/sentiment/{asset}")
async def get_macro_sentiment(asset: str, hours_back: int = 24):
    \"\"\"Get current macro sentiment for asset\"\"\"
    pass

@router.get("/macro-gap/patterns/{asset}")
async def get_gap_patterns(asset: str):
    \"\"\"Get gap patterns and statistics for asset\"\"\"
    pass
"""
