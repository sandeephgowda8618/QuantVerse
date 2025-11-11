"""
RAG LLM Risk Assessment Pipeline - Main Entry Point

This is the main runner for the RISK mode RAG pipeline.
Usage:
    python3 run_risk_assessment.py <query> [--ticker TICKER] [--mode MODE]
    
Examples:
    python3 run_risk_assessment.py "What infrastructure risks affect NVDA?"
    python3 run_risk_assessment.py "Are there regulatory risks?" --ticker NVDA
    python3 run_risk_assessment.py "Current market risks" --mode high_priority
"""

import asyncio
import json
import argparse
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import our risk assessment components
try:
    from backend.rag_engine.risk_mode.risk_pipeline import RiskAssessmentPipeline
    from backend.rag_engine.risk_mode.risk_cache import RiskCacheManager  
    from backend.rag_engine.vector_store import VectorStore
    from backend.db.database import DatabaseManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Note: This is expected if running outside full environment")
    print("Creating mock implementations for demonstration...")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RiskAssessmentRunner:
    """Main runner for risk assessment pipeline"""
    
    def __init__(self):
        self.pipeline = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize the risk assessment pipeline"""
        
        try:
            # Initialize components
            logger.info("Initializing RAG Risk Assessment Pipeline...")
            
            # Vector store (ChromaDB)
            vector_store = VectorStore()
            logger.info("✅ Vector store initialized")
            
            # Database manager
            db_manager = DatabaseManager()
            await db_manager.initialize()
            logger.info("✅ Database manager initialized")
            
            # Cache manager (Redis)
            cache_manager = RiskCacheManager()
            logger.info("✅ Cache manager initialized")
            
            # Risk assessment pipeline
            self.pipeline = RiskAssessmentPipeline(
                vector_store=vector_store,
                db_manager=db_manager,
                cache_manager=cache_manager,
                llm_model="gpt-4"  # Configure as needed
            )
            
            # Health check
            health_status = await self.pipeline.health_check()
            if health_status["overall"] != "healthy":
                logger.warning(f"Pipeline health check: {health_status['overall']}")
                for component, status in health_status.get("components", {}).items():
                    if status.get("status") != "healthy":
                        logger.warning(f"  - {component}: {status}")
            else:
                logger.info("✅ All components healthy")
            
            self.initialized = True
            logger.info("🎯 Risk Assessment Pipeline ready!")
            
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {str(e)}")
            # Create mock pipeline for demonstration
            self.pipeline = MockRiskPipeline()
            self.initialized = True
            logger.info("📋 Using mock pipeline for demonstration")
    
    async def assess_risk(self, query: str, **params) -> dict:
        """Run risk assessment for given query"""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            logger.info(f"🔍 Assessing risk for query: {query}")
            
            # Execute risk assessment
            result = await self.pipeline.assess_risk(query, params)
            
            logger.info(f"✅ Risk assessment completed in {result.get('processing_time_ms', 0):.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {str(e)}")
            return {
                "error": str(e),
                "risk_summary": "Risk assessment failed",
                "risk_level": "unknown",
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat()
            }
    
    async def batch_assess(self, queries: list) -> list:
        """Run batch risk assessments"""
        
        results = []
        for query_info in queries:
            if isinstance(query_info, str):
                query = query_info
                params = {}
            else:
                query = query_info.get("query", "")
                params = {k: v for k, v in query_info.items() if k != "query"}
            
            result = await self.assess_risk(query, **params)
            results.append({"query": query, "params": params, "result": result})
        
        return results
    
    async def status_check(self) -> dict:
        """Get pipeline status and health"""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            health_status = await self.pipeline.health_check()
            
            # Add additional status info
            status = {
                "pipeline_status": "operational" if self.initialized else "not_initialized",
                "health_check": health_status,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
            # Add cache stats if available
            if hasattr(self.pipeline, 'cache_manager'):
                try:
                    cache_stats = self.pipeline.cache_manager.get_cache_stats()
                    status["cache_stats"] = cache_stats
                except:
                    status["cache_stats"] = {"error": "cache stats unavailable"}
            
            return status
            
        except Exception as e:
            return {
                "pipeline_status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

class MockRiskPipeline:
    """Mock pipeline for demonstration when full environment not available"""
    
    async def assess_risk(self, query: str, params: dict) -> dict:
        """Mock risk assessment"""
        
        await asyncio.sleep(0.5)  # Simulate processing time
        
        # Generate mock response based on query content
        query_lower = query.lower()
        
        # Determine risk type from query
        if "infrastructure" in query_lower or "outage" in query_lower:
            primary_risk_type = "infra"
            risk_level = "medium"
        elif "regulatory" in query_lower or "policy" in query_lower:
            primary_risk_type = "regulatory"
            risk_level = "high"
        elif "sentiment" in query_lower or "news" in query_lower:
            primary_risk_type = "sentiment"
            risk_level = "medium"
        elif "liquidity" in query_lower or "volume" in query_lower:
            primary_risk_type = "liquidity"
            risk_level = "low"
        else:
            primary_risk_type = "infra"
            risk_level = "medium"
        
        return {
            "risk_summary": f"Mock risk assessment for query: {query[:50]}...",
            "risk_level": risk_level,
            "primary_risks": [
                {
                    "type": primary_risk_type,
                    "severity": risk_level,
                    "description": f"Mock {primary_risk_type} risk detected based on query analysis",
                    "confidence": 0.7
                }
            ],
            "confidence": 0.7,
            "evidence_used": [
                {
                    "source": "mock_vector_database",
                    "risk_type": primary_risk_type,
                    "snippet": f"Mock evidence for {primary_risk_type} risk assessment",
                    "timestamp": datetime.now().isoformat(),
                    "confidence": 0.7
                }
            ],
            "monitoring_recommendations": [
                f"Monitor {primary_risk_type} indicators closely",
                "Review risk assessment periodically"
            ],
            "warnings": ["mock_response_generated"],
            "processing_time_ms": 500,
            "cached": False,
            "timestamp": datetime.now().isoformat()
        }
    
    async def health_check(self) -> dict:
        """Mock health check"""
        return {
            "overall": "healthy",
            "components": {
                "mock_vector_store": {"status": "healthy"},
                "mock_database": {"status": "healthy"},
                "mock_cache": {"status": "healthy"},
                "mock_llm": {"status": "healthy"}
            },
            "timestamp": datetime.now().isoformat()
        }

# Command line interface functions
async def run_single_assessment(args):
    """Run single risk assessment"""
    
    runner = RiskAssessmentRunner()
    
    # Build parameters
    params = {}
    if args.ticker:
        params["ticker"] = args.ticker.upper()
    if args.mode:
        if args.mode == "high_priority":
            params["high_priority"] = True
            params["severity_threshold"] = "high"
        params["mode"] = args.mode
    if args.time_window:
        params["time_window"] = args.time_window
    
    # Run assessment
    result = await runner.assess_risk(args.query, **params)
    
    # Output results
    print("\n" + "="*80)
    print("🎯 RISK ASSESSMENT RESULTS")
    print("="*80)
    print(f"Query: {args.query}")
    if params:
        print(f"Parameters: {params}")
    print("-"*80)
    
    print(f"Risk Level: {result.get('risk_level', 'unknown').upper()}")
    print(f"Confidence: {result.get('confidence', 0):.2f}")
    print(f"Processing Time: {result.get('processing_time_ms', 0):.2f}ms")
    print()
    
    print("Risk Summary:")
    print(f"  {result.get('risk_summary', 'No summary available')}")
    print()
    
    primary_risks = result.get("primary_risks", [])
    if primary_risks:
        print("Primary Risks:")
        for i, risk in enumerate(primary_risks, 1):
            print(f"  {i}. {risk.get('type', 'unknown').upper()}: {risk.get('severity', 'unknown')} severity")
            print(f"     {risk.get('description', 'No description')}")
            print(f"     Confidence: {risk.get('confidence', 0):.2f}")
        print()
    
    recommendations = result.get("monitoring_recommendations", [])
    if recommendations:
        print("Monitoring Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        print()
    
    evidence = result.get("evidence_used", [])
    if evidence:
        print("Evidence Used:")
        for i, ev in enumerate(evidence[:3], 1):  # Show top 3
            print(f"  {i}. {ev.get('source', 'unknown')} ({ev.get('risk_type', 'unknown')})")
            print(f"     {ev.get('snippet', 'No snippet')}")
        if len(evidence) > 3:
            print(f"     ... and {len(evidence) - 3} more evidence items")
        print()
    
    warnings = result.get("warnings", [])
    if warnings:
        print("⚠️  Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print()
    
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
    
    print("="*80)

async def run_status_check():
    """Run pipeline status check"""
    
    runner = RiskAssessmentRunner()
    status = await runner.status_check()
    
    print("\n" + "="*60)
    print("📊 RISK ASSESSMENT PIPELINE STATUS")
    print("="*60)
    
    print(f"Pipeline Status: {status.get('pipeline_status', 'unknown').upper()}")
    print(f"Timestamp: {status.get('timestamp', 'unknown')}")
    print()
    
    health_check = status.get("health_check", {})
    overall_health = health_check.get("overall", "unknown")
    print(f"Overall Health: {overall_health.upper()}")
    
    components = health_check.get("components", {})
    if components:
        print("\nComponent Health:")
        for component, health in components.items():
            status_icon = "✅" if health.get("status") == "healthy" else "❌"
            print(f"  {status_icon} {component}: {health.get('status', 'unknown')}")
            if health.get("error"):
                print(f"    Error: {health['error']}")
    
    cache_stats = status.get("cache_stats", {})
    if cache_stats and not cache_stats.get("error"):
        print("\nCache Statistics:")
        cache_counts = cache_stats.get("cache_counts", {})
        for cache_type, count in cache_counts.items():
            print(f"  {cache_type}: {count} entries")
    
    print("="*60)

async def run_batch_demo():
    """Run batch demo with sample queries"""
    
    sample_queries = [
        "What infrastructure risks affect NVDA trading?",
        "Are there any regulatory risks for tech stocks?",
        "Current sentiment risks in the market",
        {"query": "Liquidity risks for AAPL", "ticker": "AAPL"},
        {"query": "High priority risk assessment", "mode": "high_priority", "time_window": "24h"}
    ]
    
    runner = RiskAssessmentRunner()
    
    print("\n" + "="*80)
    print("🎯 BATCH RISK ASSESSMENT DEMO")
    print("="*80)
    
    results = await runner.batch_assess(sample_queries)
    
    for i, item in enumerate(results, 1):
        query = item["query"]
        params = item["params"]
        result = item["result"]
        
        print(f"\n{i}. Query: {query}")
        if params:
            print(f"   Parameters: {params}")
        
        risk_level = result.get("risk_level", "unknown")
        confidence = result.get("confidence", 0)
        processing_time = result.get("processing_time_ms", 0)
        
        print(f"   Risk Level: {risk_level.upper()} (confidence: {confidence:.2f})")
        print(f"   Processing Time: {processing_time:.2f}ms")
        
        primary_risks = result.get("primary_risks", [])
        if primary_risks:
            risk_types = [risk.get("type", "unknown") for risk in primary_risks]
            print(f"   Risk Types: {', '.join(risk_types)}")
    
    print("\n" + "="*80)

def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description="RAG LLM Risk Assessment Pipeline")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Single assessment command
    assess_parser = subparsers.add_parser("assess", help="Run risk assessment")
    assess_parser.add_argument("query", help="Risk assessment query")
    assess_parser.add_argument("--ticker", help="Specific ticker/asset")
    assess_parser.add_argument("--mode", help="Assessment mode (high_priority, etc.)")
    assess_parser.add_argument("--time_window", help="Time window (24h, 7d, etc.)")
    
    # Status command
    subparsers.add_parser("status", help="Check pipeline status")
    
    # Demo command
    subparsers.add_parser("demo", help="Run batch demo")
    
    # If no command specified, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    # Route to appropriate handler
    if args.command == "assess":
        asyncio.run(run_single_assessment(args))
    elif args.command == "status":
        asyncio.run(run_status_check())
    elif args.command == "demo":
        asyncio.run(run_batch_demo())
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
