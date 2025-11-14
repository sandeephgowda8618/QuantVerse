"""
Chat routes for RAG + LLM interaction
Provides POST /chat endpoint with centralized LLM management
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..rag_engine.llm_manager import LLMManager
from ..db.postgres_handler import PostgresHandler

# from ..services.rag_service import RAGService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services (will be implemented)
# rag_service = RAGService()

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class EvidenceItem(BaseModel):
    source: str
    snippet: str
    timestamp: str

class ChatResponse(BaseModel):
    answer: str
    confidence: float
    evidence: List[EvidenceItem]
    timestamp: str

@router.post("/", response_model=ChatResponse)
async def chat_with_rag(request: ChatRequest):
    """Chat with RAG + LLM, retrieve evidence using centralized LLM manager"""
    try:
        # Get the centralized LLM manager
        llm_manager = LLMManager.get_instance()
        
        # Create a system prompt for financial risk analysis
        system_prompt = """You are a financial risk analyst AI assistant. 
        Analyze the user's question and provide helpful insights about financial risks, 
        market conditions, and investment considerations. 
        Be concise, factual, and avoid giving specific trading advice."""
        
        # Generate response using persistent LLM session
        logger.info(f"Processing chat request: {request.message[:50]}...")
        llm_response = await llm_manager.generate(
            prompt=request.message,
            system_prompt=system_prompt
        )
        
        # TODO: Implement full RAG pipeline with vector search
        # Get evidence from database for the mentioned ticker/company
        evidence_items = await _gather_risk_evidence(request.message)
        
        return ChatResponse(
            answer=llm_response,
            confidence=0.8,
            evidence=evidence_items,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

async def _gather_risk_evidence(message: str) -> List[EvidenceItem]:
    """Gather evidence for risk assessment from database"""
    try:
        db = PostgresHandler()
        evidence_items = []
        
        # Extract ticker from message (simple pattern matching)
        import re
        ticker_matches = re.findall(r'\b([A-Z]{1,5})\b', message.upper())
        tickers = ['AAPL', 'BTC', 'NVDA', 'TSLA', 'AMZN']  # Known tickers with data
        
        found_ticker = None
        for match in ticker_matches:
            if match in tickers:
                found_ticker = match
                break
        
        if found_ticker:
            # Get news evidence
            news_query = """
            SELECT headline, sentiment, published_at
            FROM news_headlines 
            WHERE ticker = $1 
            AND published_at >= NOW() - INTERVAL '14 days'
            ORDER BY published_at DESC
            LIMIT 3
            """
            
            news_result = await db.async_execute_query(news_query, (found_ticker,))
            for row in news_result:
                evidence_items.append(EvidenceItem(
                    source="news_headlines",
                    snippet=f"{row['headline']} (Sentiment: {row.get('sentiment', 'neutral')})",
                    timestamp=str(row['published_at'])
                ))
            
            # Get anomaly evidence
            anomaly_query = """
            SELECT anomaly_type, description, detected_at, confidence_score
            FROM anomalies 
            WHERE ticker = $1 
            AND detected_at >= NOW() - INTERVAL '30 days'
            ORDER BY confidence_score DESC
            LIMIT 2
            """
            
            anomaly_result = await db.async_execute_query(anomaly_query, (found_ticker,))
            for row in anomaly_result:
                evidence_items.append(EvidenceItem(
                    source="market_anomalies",
                    snippet=f"{row['anomaly_type']}: {row['description']} (Confidence: {row.get('confidence_score', 0):.2f})",
                    timestamp=str(row['detected_at'])
                ))
        
        # Add fallback evidence if none found
        if not evidence_items:
            evidence_items.append(EvidenceItem(
                source="llm_analysis", 
                snippet="Risk analysis based on general market knowledge and current conditions",
                timestamp=datetime.now().isoformat()
            ))
        
        return evidence_items
        
    except Exception as e:
        logger.error(f"Error gathering risk evidence: {e}")
        return [EvidenceItem(
            source="system",
            snippet="Evidence gathering encountered an error, analysis based on available data",
            timestamp=datetime.now().isoformat()
        )]
