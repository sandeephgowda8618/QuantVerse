#!/usr/bin/env python3
"""
Interactive Real-Time Risk Assessment Demo
QuantVerse uRISK - Production LLM Query Interface
"""

import asyncio
import sys
from pathlib import Path
import time

# Add project path
sys.path.append(str(Path(__file__).parent))

from backend.rag_engine.risk_mode.risk_pipeline import RiskAssessmentPipeline
from backend.rag_engine.vector_store import ChromaVectorStore
from backend.rag_engine.risk_mode.risk_cache import RiskCacheManager
from backend.db.postgres_handler import PostgresHandler

class InteractiveRiskDemo:
    """Interactive demo for real-time risk assessment"""
    
    def __init__(self):
        self.pipeline = None
        self.available_tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META"]
        
    async def initialize(self):
        """Initialize all components"""
        print("🔧 Initializing QuantVerse uRISK Real-Time System...")
        
        # Initialize components
        db_handler = PostgresHandler()
        db_handler.initialize_sync_pool()
        
        vector_store = ChromaVectorStore()
        vector_store.initialize("./vector_db")
        
        cache_manager = RiskCacheManager()
        
        self.pipeline = RiskAssessmentPipeline(
            vector_store=vector_store,
            db_manager=db_handler,
            cache_manager=cache_manager,
            llm_model="llama3.1"
        )
        
        # Check system status
        stats = vector_store.get_collection_stats()
        print(f"✅ System Ready: {stats.get('count', 0)} documents in vector store")
        
    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "="*60)
        print("🎯 QUANTVERSE uRISK - REAL-TIME RISK ASSESSMENT DEMO")
        print("="*60)
        print("💡 Ask natural language questions about financial risks!")
        print("📊 Supported tickers:", ", ".join(self.available_tickers))
        print("📝 Example queries:")
        print("   • What risks should I monitor for AAPL?")
        print("   • Is NVDA facing infrastructure issues?") 
        print("   • Are there regulatory risks for MSFT?")
        print("   • Should I worry about AMZN liquidity?")
        print("\n💬 Type 'quit' or 'exit' to end the demo")
        print("="*60 + "\n")
    
    async def process_query(self, query: str, ticker: str = None):
        """Process a risk query and return formatted results"""
        
        if not self.pipeline:
            print("❌ System not initialized")
            return
            
        if not ticker:
            # Try to extract ticker from query
            for t in self.available_tickers:
                if t.lower() in query.lower():
                    ticker = t
                    break
        
        params = {}
        if ticker:
            params["ticker"] = ticker
            params["time_window_hours"] = 24  # Default to 24 hours
        
        print(f"🔍 Processing query: {query}")
        if ticker:
            print(f"📊 Analyzing ticker: {ticker}")
        else:
            print("📊 General market analysis (no specific ticker)")
        
        start_time = time.time()
        
        try:
            result = await self.pipeline.assess_risk(query, params)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            self.display_results(result, response_time, query)
            
        except Exception as e:
            print(f"❌ Error processing query: {str(e)}")
    
    def display_results(self, result: dict, response_time: float, query: str):
        """Display formatted risk assessment results"""
        
        print("\n" + "-"*50)
        print("📈 RISK ASSESSMENT RESULTS")
        print("-"*50)
        
        # Performance metrics
        print(f"⏱️  Response Time: {response_time:.2f}s")
        print(f"⚠️  Risk Score: {result.get('risk_score', 'N/A')}/10")
        print(f"🎯 Confidence: {result.get('confidence', 'N/A')}")
        
        # Primary risks
        primary_risks = result.get('primary_risks', [])
        if primary_risks:
            print(f"\n🚨 PRIMARY RISKS ({len(primary_risks)}):")
            for i, risk in enumerate(primary_risks, 1):
                risk_type = risk.get('type', 'Unknown').upper()
                severity = risk.get('severity', 'unknown')
                confidence = risk.get('confidence', 'N/A')
                description = risk.get('description', 'No description')
                
                print(f"   {i}. {risk_type}")
                print(f"      • Severity: {severity}")
                print(f"      • Confidence: {confidence}")
                print(f"      • Details: {description[:100]}{'...' if len(description) > 100 else ''}")
        else:
            print("\n🟢 NO HIGH-PRIORITY RISKS IDENTIFIED")
        
        # Secondary risks
        secondary_risks = result.get('secondary_risks', [])
        if secondary_risks:
            print(f"\n⚠️  SECONDARY RISKS ({len(secondary_risks)}):")
            for i, risk in enumerate(secondary_risks[:3], 1):
                risk_type = risk.get('type', 'Unknown').upper()
                severity = risk.get('severity', 'unknown')
                print(f"   {i}. {risk_type} - {severity} severity")
        
        # Warnings
        warnings = result.get('warnings', [])
        if warnings:
            print(f"\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"   • {warning}")
        
        # Recommendations
        recommendations = result.get('recommendations', [])
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"   {i}. {rec}")
        
        print("-"*50 + "\n")
    
    async def run_interactive_demo(self):
        """Run the interactive demo loop"""
        
        await self.initialize()
        self.print_banner()
        
        while True:
            try:
                # Get user input
                user_input = input("🎤 Enter your risk query: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Thank you for using QuantVerse uRISK!")
                    break
                
                # Process the query
                print()
                await self.process_query(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 Demo interrupted. Thank you for using QuantVerse uRISK!")
                break
            except EOFError:
                print("\n👋 Demo ended. Thank you for using QuantVerse uRISK!")
                break

async def main():
    """Main demo function"""
    demo = InteractiveRiskDemo()
    await demo.run_interactive_demo()

if __name__ == "__main__":
    asyncio.run(main())
