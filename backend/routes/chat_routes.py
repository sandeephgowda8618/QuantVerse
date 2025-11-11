"""
Chat routes for RAG + LLM interaction
Provides POST /chat endpoint with centralized LLM management
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..rag_engine.llm_manager import LLMManager

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
    reply: str
    confidence: float
    evidence: List[EvidenceItem]

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
        # For now, return LLM response with placeholder evidence
        
        return ChatResponse(
            reply=llm_response,
            confidence=0.8,
            evidence=[
                EvidenceItem(
                    source="llm_direct",
                    snippet="Response generated using centralized LLM manager with persistent session",
                    timestamp="2025-11-10T00:00:00Z"
                )
            ]
        )
        
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")
