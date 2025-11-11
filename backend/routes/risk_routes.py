"""
Risk alerts and asset management routes
Provides /risk-alerts, /assets endpoints
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from ..db.postgres_handler import PostgresHandler

router = APIRouter()

# Initialize database handler
db_handler = PostgresHandler()

class RiskAlert(BaseModel):
    ticker: str
    risk_type: str
    severity: str
    message: str
    triggered_at: datetime

class Asset(BaseModel):
    ticker: str
    name: str
    asset_type: str
    exchange: str
    sector: str
    country: str

@router.get("/risk-alerts", response_model=List[RiskAlert])
async def get_risk_alerts(
    ticker: Optional[str] = Query(None, description="Filter by ticker"),
    severity: Optional[str] = Query(None, description="Filter by severity (low/medium/high)"),
    limit: int = Query(50, le=100, description="Limit number of alerts")
):
    """Get current risk alerts"""
    try:
        # Build the query with proper parameter substitution
        query = """
        SELECT ticker, risk_type, severity, message, triggered_at
        FROM alerts
        WHERE 1=1
        """
        params = []
        param_index = 1
        
        if ticker:
            query += f" AND ticker = ${param_index}"
            params.append(ticker)
            param_index += 1
        
        if severity:
            query += f" AND severity = ${param_index}"
            params.append(severity)
            param_index += 1
        
        query += f" ORDER BY triggered_at DESC LIMIT ${param_index}"
        params.append(limit)
        
        # Execute query
        result = await db_handler.async_execute_query(query, tuple(params))
        
        return [
            RiskAlert(
                ticker=row['ticker'],
                risk_type=row['risk_type'],
                severity=row['severity'],
                message=row['message'],
                triggered_at=row['triggered_at']
            )
            for row in result
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch risk alerts: {str(e)}")

@router.get("/assets", response_model=List[str])
async def get_assets():
    """List all tracked tickers/assets"""
    try:
        query = "SELECT ticker FROM assets ORDER BY ticker"
        result = await db_handler.async_execute_query(query)
        
        return [row['ticker'] for row in result]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch assets: {str(e)}")

@router.get("/assets/details", response_model=List[Asset])
async def get_assets_details():
    """Get detailed asset information"""
    try:
        query = """
        SELECT ticker, name, asset_type, exchange, sector, country
        FROM assets
        ORDER BY ticker
        """
        result = await db_handler.async_execute_query(query)
        
        return [
            Asset(
                ticker=row['ticker'],
                name=row['name'] or '',
                asset_type=row['asset_type'] or '',
                exchange=row['exchange'] or '',
                sector=row['sector'] or '',
                country=row['country'] or ''
            )
            for row in result
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch asset details: {str(e)}")
