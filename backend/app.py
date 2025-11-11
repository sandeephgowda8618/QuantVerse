"""
FastAPI entrypoint for uRISK - Unified Risk Intelligence & Surveillance Kernel
Mounts all routes and provides health checks
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config.settings import settings
from .db.postgres_handler import PostgresHandler
from .rag_engine.llm_manager import LLMManager
from .routes import (
    chat_routes,
    risk_routes
)
# Member routes
from .routes.member1 import options_flow_routes
from .routes.member2 import explain_move_routes  
from .routes.member3 import macro_gap_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global database handler and LLM manager
db_handler = PostgresHandler()
llm_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown"""
    global llm_manager
    
    # Startup
    logger.info("🚀 Starting uRISK application...")
    
    try:
        # Initialize database connections
        db_handler.initialize_sync_pool()
        await db_handler.initialize_async_pool()
        logger.info("✅ Database connections initialized")
        
        # Test database connection
        await test_database_connection()
        
        # Initialize LLM Manager with full startup sequence
        logger.info("🧠 Initializing LLM Manager...")
        llm_manager = await LLMManager.initialize()
        logger.info("✅ LLM Manager ready and warmed up")
        
        # System ready
        logger.info("🎯 uRISK system fully initialized and ready!")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise
    finally:
        # Shutdown
        logger.info("🛑 Shutting down uRISK application...")
        
        # Shutdown LLM Manager
        if llm_manager:
            await llm_manager.shutdown()
            logger.info("✅ LLM Manager shutdown completed")
        
        # Shutdown database connections
        if db_handler.async_pool:
            await db_handler.async_pool.close()
        if db_handler.pool:
            db_handler.pool.closeall()
        logger.info("✅ Database connections closed")
        
        logger.info("✅ uRISK shutdown completed")

async def test_database_connection():
    """Test database connectivity on startup"""
    try:
        result = await db_handler.async_execute_query("SELECT 1 as test")
        if result and result[0]['test'] == 1:
            logger.info("Database connection test successful")
        else:
            raise Exception("Database connection test failed")
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        raise

# Create FastAPI app
app = FastAPI(
    title="uRISK - Unified Risk Intelligence API",
    description="Local RAG + ML risk monitoring assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount core routes
app.include_router(chat_routes.router, prefix="/chat", tags=["Chat"])
app.include_router(risk_routes.router, prefix="", tags=["Risk"])

# Mount member routes
app.include_router(options_flow_routes.router, prefix="/member1", tags=["Member 1 - Options Flow"])
app.include_router(explain_move_routes.router, prefix="/member2", tags=["Member 2 - Move Explainer"])
app.include_router(macro_gap_routes.router, prefix="/member3", tags=["Member 3 - Macro Gap"])

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "service": "uRISK - Unified Risk Intelligence & Surveillance Kernel",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check including database and LLM connectivity"""
    global llm_manager
    
    try:
        # Test database connection
        db_result = await db_handler.async_execute_query("SELECT NOW() as current_time")
        db_status = "healthy" if db_result else "unhealthy"
        
        # Test LLM health
        llm_health = {"status": "not_initialized"}
        if llm_manager and llm_manager.is_ready:
            llm_health = await llm_manager.health_check()
        
        overall_status = "healthy"
        if db_status != "healthy" or llm_health.get("status") != "healthy":
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": db_result[0]['current_time'] if db_result else None,
            "components": {
                "database": db_status,
                "llm": llm_health,
                "api": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "components": {
                    "database": "unhealthy",
                    "llm": "unhealthy",
                    "api": "healthy"
                }
            }
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting uRISK server...")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
