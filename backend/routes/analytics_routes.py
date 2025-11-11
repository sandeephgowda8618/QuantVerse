"""
Analytics routes for sentiment, anomalies, and evidence retrieval
Provides /sentiment, /anomalies, /evidence endpoints for financial data analysis
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from ..db.postgres_handler import PostgresHandler

router = APIRouter()

# Initialize database handler
db_handler = PostgresHandler()

class SentimentResponse(BaseModel):
    ticker: str
    avg_sentiment: float
    summary: str
    latest_headlines: List[str]

class AnomalyResponse(BaseModel):
    metric: str
    severity: str
    anomaly_score: float
    explanation: str
    timestamp: datetime

class EvidenceResponse(BaseModel):
    text: str
    source: str
    timestamp: datetime

@router.get("/sentiment", response_model=SentimentResponse)
async def get_sentiment(ticker: str = Query(..., description="Ticker symbol")):
    """Get sentiment summary for an asset"""
    try:
        # Get average sentiment
        sentiment_query = """
        SELECT AVG(ns.sentiment_score) as avg_sentiment
        FROM news_sentiment ns
        JOIN news_headlines nh ON ns.headline_id = nh.id
        WHERE nh.ticker = $1
        AND ns.timestamp >= NOW() - INTERVAL '24 hours'
        """
        
        sentiment_result = await db_handler.async_execute_query(sentiment_query, (ticker,))
        avg_sentiment = sentiment_result[0]['avg_sentiment'] or 0.0
        
        # Get latest headlines
        headlines_query = """
        SELECT headline
        FROM news_headlines
        WHERE ticker = $1
        ORDER BY published_at DESC
        LIMIT 5
        """
        
        headlines_result = await db_handler.async_execute_query(headlines_query, (ticker,))
        headlines = [row['headline'] for row in headlines_result]
        
        # Generate summary
        if avg_sentiment > 0.2:
            summary = f"Sentiment is positive with an average score of {avg_sentiment:.2f}"
        elif avg_sentiment < -0.2:
            summary = f"Sentiment is negative with an average score of {avg_sentiment:.2f}"
        else:
            summary = f"Sentiment is neutral with an average score of {avg_sentiment:.2f}"
        
        return SentimentResponse(
            ticker=ticker,
            avg_sentiment=avg_sentiment,
            summary=summary,
            latest_headlines=headlines
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sentiment: {str(e)}")

@router.get("/anomalies", response_model=List[AnomalyResponse])
async def get_anomalies(
    ticker: str = Query(..., description="Ticker symbol"),
    limit: int = Query(10, le=50, description="Limit number of anomalies")
):
    """Get ML-detected anomalies for an asset"""
    try:
        query = """
        SELECT metric, severity, anomaly_score, explanation, timestamp
        FROM anomalies
        WHERE ticker = $1
        ORDER BY timestamp DESC
        LIMIT $2
        """
        
        result = await db_handler.async_execute_query(query, (ticker, limit))
        
        return [
            AnomalyResponse(
                metric=row['metric'],
                severity=row['severity'],
                anomaly_score=row['anomaly_score'],
                explanation=row['explanation'],
                timestamp=row['timestamp']
            )
            for row in result
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch anomalies: {str(e)}")

@router.get("/evidence", response_model=List[EvidenceResponse])
async def get_evidence(
    ticker: str = Query(..., description="Ticker symbol"),
    hours: int = Query(24, le=168, description="Hours to look back"),
    limit: int = Query(20, le=100, description="Limit number of evidence pieces")
):
    """Retrieve raw RAG evidence chunks"""
    try:
        # Get regulatory events
        reg_query = """
        SELECT title as text, source, published_at as timestamp
        FROM regulatory_events
        WHERE ticker = $1
        AND published_at >= NOW() - ($2 || ' hours')::INTERVAL
        ORDER BY published_at DESC
        LIMIT $3
        """
        
        reg_result = await db_handler.async_execute_query(reg_query, (ticker, hours, limit//2))
        
        # Get news headlines
        news_query = """
        SELECT headline as text, source, published_at as timestamp
        FROM news_headlines
        WHERE ticker = $1
        AND published_at >= NOW() - ($2 || ' hours')::INTERVAL
        ORDER BY published_at DESC
        LIMIT $3
        """
        
        news_result = await db_handler.async_execute_query(news_query, (ticker, hours, limit//2))
        
        # Combine results
        all_evidence = []
        
        for row in reg_result:
            all_evidence.append(EvidenceResponse(
                text=row['text'],
                source=row['source'],
                timestamp=row['timestamp']
            ))
        
        for row in news_result:
            all_evidence.append(EvidenceResponse(
                text=row['text'],
                source=row['source'],
                timestamp=row['timestamp']
            ))
        
        # Sort by timestamp descending
        all_evidence.sort(key=lambda x: x.timestamp, reverse=True)
        
        return all_evidence[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch evidence: {str(e)}")
