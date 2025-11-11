"""
RAG Service for uRISK
Orchestrates retrieval-augmented generation for financial intelligence.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..rag_engine.retriever import financial_rag_retriever
from ..rag_engine.vector_store import vector_store
# from ..rag_engine.llama_engine import llama_engine  # TODO: Create this
from .postgres_to_vectordb import postgres_to_vectordb_pipeline

logger = logging.getLogger(__name__)

class RAGService:
    """Orchestrates the RAG pipeline for financial data."""
    
    def __init__(self):
        self.retriever = financial_rag_retriever
        self.vector_store = vector_store
        self.llama_engine = None  # Will be initialized
        self.pipeline = postgres_to_vectordb_pipeline
        
    async def initialize(self):
        """Initialize all RAG components."""
        try:
            logger.info("Initializing RAG Service...")
            
            # Initialize vector store
            self.vector_store.initialize()
            
            # Initialize retriever
            await self.retriever.initialize()
            
            # Initialize sync pipeline
            await self.pipeline.initialize()
            
            # TODO: Initialize LLM engine
            # await self.llama_engine.initialize()
            
            logger.info("RAG Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Service: {e}")
            raise
    
    async def query(
        self,
        user_message: str,
        ticker: Optional[str] = None,
        context_type: str = "comprehensive",
        max_context_chunks: int = 15
    ) -> Dict[str, Any]:
        """Main RAG query interface."""
        try:
            logger.info(f"Processing RAG query: '{user_message[:100]}...'")
            
            # Extract ticker if not provided
            if not ticker:
                ticker = self.retriever.extract_ticker_from_query(user_message)
            
            # Retrieve relevant context
            if ticker:
                context_results = await self.retriever.get_context_for_ticker(
                    ticker=ticker,
                    context_type=context_type,
                    max_chunks=max_context_chunks
                )
            else:
                context_results = await self.retriever.semantic_search(
                    query=user_message,
                    n_results=max_context_chunks
                )
            
            # Format context for LLM
            formatted_context = self.retriever.format_context_for_llm(context_results)
            
            # Generate response using LLM (TODO: Implement)
            # if self.llama_engine:
            #     llm_response = await self.llama_engine.generate_response(
            #         query=user_message,
            #         context=formatted_context,
            #         ticker=ticker
            #     )
            # else:
            
            # Fallback response structure for now
            llm_response = {
                "reply": f"RAG pipeline retrieved {len(context_results)} relevant chunks for your query about {ticker or 'the market'}. Context includes {formatted_context[:200]}...",
                "confidence": 0.8 if context_results else 0.2,
                "reasoning": f"Successfully retrieved context from {len(context_results)} sources"
            }
            
            # Build response
            response = {
                "reply": llm_response.get("reply", "Unable to generate response"),
                "confidence": llm_response.get("confidence", 0.0),
                "ticker": ticker,
                "context_chunks_used": len(context_results),
                "evidence_sources": self.extract_evidence_sources(context_results),
                "timestamp": datetime.now().isoformat(),
                "reasoning": llm_response.get("reasoning", "")
            }
            
            logger.info(f"RAG query completed successfully for ticker: {ticker}")
            return response
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return {
                "reply": "I encountered an error processing your request. Please try again.",
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def extract_evidence_sources(self, context_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract evidence sources from context results."""
        sources = []
        
        for result in context_results[:5]:  # Top 5 sources
            metadata = result.get('metadata', {})
            
            source = {
                "source": metadata.get('source', 'unknown'),
                "endpoint": metadata.get('endpoint', 'unknown'),
                "risk_type": metadata.get('risk_type', 'general'),
                "timestamp": metadata.get('timestamp', ''),
                "ticker": metadata.get('ticker', ''),
                "snippet": result.get('text', '')[:150] + "..." if len(result.get('text', '')) > 150 else result.get('text', ''),
                "relevance_score": result.get('enhanced_score', 0.0)
            }
            
            sources.append(source)
        
        return sources
    
    async def sync_data(self) -> Dict[str, Any]:
        """Trigger data sync from PostgreSQL to vector store."""
        try:
            logger.info("Starting data sync to vector store...")
            
            sync_results = await self.pipeline.run_full_sync()
            
            logger.info("Data sync completed")
            return {
                "success": sync_results.get("success", False),
                "stats": sync_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Data sync failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_ticker_intelligence(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive intelligence for a specific ticker."""
        try:
            # Get different types of context
            contexts = {}
            
            contexts["recent"] = await self.retriever.get_context_for_ticker(
                ticker, "recent_activity", max_chunks=5
            )
            
            contexts["technical"] = await self.retriever.get_context_for_ticker(
                ticker, "technical", max_chunks=5
            )
            
            contexts["comprehensive"] = await self.retriever.get_context_for_ticker(
                ticker, "comprehensive", max_chunks=10
            )
            
            return {
                "ticker": ticker,
                "contexts": contexts,
                "summary": {
                    "total_chunks": sum(len(context) for context in contexts.values()),
                    "recent_activity_count": len(contexts["recent"]),
                    "technical_analysis_count": len(contexts["technical"]),
                    "comprehensive_count": len(contexts["comprehensive"])
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get ticker intelligence: {e}")
            return {
                "ticker": ticker,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get RAG system status and statistics."""
        try:
            retriever_stats = await self.retriever.get_stats()
            vector_stats = self.vector_store.get_collection_stats()
            
            return {
                "status": "operational" if vector_stats.get("count", 0) > 0 else "empty",
                "retriever": retriever_stats,
                "vector_store": vector_stats,
                "pipeline_ready": hasattr(self.pipeline, 'postgres') and self.pipeline.postgres.async_pool is not None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global RAG service instance
rag_service = RAGService()
