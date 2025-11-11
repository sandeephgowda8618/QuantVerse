"""
Member 1: Options Flow Interpreter Route
REST API endpoint for analyzing unusual options activity and providing insights.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, validator

from ...services.member1.options_flow_service import OptionsFlowService

logger = logging.getLogger(__name__)

# Request/Response Models
class OptionsFlowRequest(BaseModel):
    ticker: str
    user_question: str
    
    @validator('ticker')
    def validate_ticker(cls, v):
        if not v or len(v) > 10:
            raise ValueError('Ticker must be provided and less than 10 characters')
        return v.upper()
    
    @validator('user_question') 
    def validate_question(cls, v):
        if not v or len(v) < 5:
            raise ValueError('Question must be at least 5 characters')
        return v

class OptionsFlowResponse(BaseModel):
    ticker: str
    insight: str
    reasons: list[str]
    confidence: float
    evidence: list[dict]
    timestamp: str

# Router setup
router = APIRouter(prefix="/member1", tags=["Member1-OptionsFlow"])

# Initialize service
options_service = OptionsFlowService()

@router.post("/options-flow", response_model=OptionsFlowResponse)
async def analyze_options_flow(request: OptionsFlowRequest):
    """
    Analyze options flow and provide insights
    
    **What this endpoint does:**
    - Analyzes unusual call/put volume and IV spikes
    - Identifies whale orders and institutional positioning
    - Provides plain English explanations with confidence scores
    
    **Example Request:**
    ```json
    {
        "ticker": "TSLA",
        "user_question": "Are big traders buying calls?"
    }
    ```
    """
    try:
        # Validate ticker exists
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
        logger.error(f"Options flow analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/options-flow/health")
async def options_flow_health():
    """Health check for options flow service"""
    return {
        "service": "options_flow",
        "status": "active",
        "message": "Options flow service is running"
    }

@router.get("/options-flow/recent/{ticker}")
async def get_recent_options_activity(ticker: str, hours_back: int = 6):
    """Get recent options activity for context"""
    try:
        if not await options_service.validate_ticker(ticker):
            raise HTTPException(status_code=400, detail=f"Ticker {ticker} not found")
        
        anomalies = await options_service.get_recent_anomalies(ticker, hours_back)
        
        return {
            "ticker": ticker,
            "hours_back": hours_back,
            "anomalies": anomalies
        }
        
    except Exception as e:
        logger.error(f"Error fetching recent activity for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
