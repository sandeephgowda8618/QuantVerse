"""
Comprehensive Test Suite for All 4 RAG-Enabled LLM Systems
FOCUSED ON NVIDIA (NVDA) - the stock we have data for
Tests all pipelines to ensure correct responses with:
- Suggestions/recommendations
- Confidence scores
- Top evidence chunks
- Proper analysis structure
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Any

class NVDARAGSystemTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = None
        self.test_results = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, endpoint: str, payload: Dict, expected_fields: List[str]) -> Dict:
        """Test a single endpoint and validate response structure"""
        print(f"\n🧪 Testing {endpoint}")
        print(f"📤 Payload: {json.dumps(payload, indent=2)}")
        
        start_time = time.time()
        
        try:
            async with self.session.post(f"{self.base_url}{endpoint}", json=payload) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate expected fields
                    missing_fields = []
                    for field in expected_fields:
                        if field not in data:
                            missing_fields.append(field)
                    
                    # Check for evidence/chunks
                    evidence_count = 0
                    evidence_details = []
                    
                    if 'evidence' in data:
                        evidence_count = len(data.get('evidence', []))
                        evidence_details = data.get('evidence', [])
                    elif 'evidence_used' in data:
                        evidence_count = len(data.get('evidence_used', []))
                        evidence_details = data.get('evidence_used', [])
                    elif 'vector_evidence' in data:
                        evidence_count = len(data.get('vector_evidence', []))
                        evidence_details = data.get('vector_evidence', [])
                    
                    result = {
                        'status': '✅ SUCCESS',
                        'response_time': f"{response_time:.2f}s",
                        'evidence_chunks': evidence_count,
                        'missing_fields': missing_fields,
                        'confidence': data.get('confidence', data.get('confidence_score', 'N/A')),
                        'response_size': len(str(data)),
                        'raw_response': data,
                        'evidence_details': evidence_details
                    }
                    
                    print(f"✅ SUCCESS - Response time: {response_time:.2f}s")
                    print(f"📊 Evidence chunks: {evidence_count}")
                    print(f"🎯 Confidence: {result['confidence']}")
                    
                    if missing_fields:
                        print(f"⚠️  Missing fields: {missing_fields}")
                    
                    # Show evidence summary
                    if evidence_details:
                        print(f"\n📋 EVIDENCE SUMMARY:")
                        for i, ev in enumerate(evidence_details[:3]):  # Show first 3
                            if isinstance(ev, dict):
                                ev_type = ev.get('source', ev.get('type', 'unknown'))
                                content = str(ev.get('content', ev.get('text', '')))[:100]
                                print(f"  {i+1}. [{ev_type}] {content}...")
                    
                    # Display the complete response structure
                    print(f"\n📋 FULL RESPONSE STRUCTURE:")
                    print("=" * 50)
                    print(json.dumps(data, indent=2))
                    print("=" * 50)
                    
                    return result
                    
                else:
                    error_text = await response.text()
                    result = {
                        'status': '❌ ERROR',
                        'response_time': f"{response_time:.2f}s",
                        'error_code': response.status,
                        'error_message': error_text[:200] + "..." if len(error_text) > 200 else error_text
                    }
                    print(f"❌ ERROR {response.status}: {error_text[:100]}...")
                    return result
                    
        except Exception as e:
            response_time = time.time() - start_time
            result = {
                'status': '💥 EXCEPTION',
                'response_time': f"{response_time:.2f}s",
                'exception': str(e)
            }
            print(f"💥 EXCEPTION: {str(e)}")
            return result

    async def test_core_risk_module(self):
        """Test Core Risk Assessment Module with NVDA"""
        print("\n" + "="*60)
        print("🛡️  TESTING CORE RISK MODULE - NVDA")
        print("="*60)
        
        # Test risk assessment via chat endpoint - USING NVDA
        risk_payload = {
            "message": "What are the current risk factors for NVIDIA (NVDA) stock? Analyze market conditions, competitive threats, and regulatory risks.",
            "user_id": "test_user"
        }
        
        expected_fields = [
            'answer', 'confidence', 'evidence', 'timestamp'
        ]
        
        result = await self.test_endpoint("/chat/", risk_payload, expected_fields)
        self.test_results['core_risk'] = result
        return result

    async def test_options_flow_module(self):
        """Test Options Flow Analysis Module with NVDA"""
        print("\n" + "="*60)
        print("📈 TESTING OPTIONS FLOW MODULE - NVDA")
        print("="*60)
        
        # Test options flow analysis for NVDA
        options_payload = {
            "ticker": "NVDA",
            "user_question": "Analyze unusual options activity for NVIDIA. What are the major option flows indicating about market sentiment?"
        }
        
        expected_fields = [
            'ticker', 'insight', 'reasons', 
            'confidence', 'evidence', 'timestamp'
        ]
        
        result = await self.test_endpoint("/member1/member1/options-flow", options_payload, expected_fields)
        self.test_results['options_flow'] = result
        return result

    async def test_market_move_module(self):
        """Test Sudden Market Move Explainer Module with NVDA"""
        print("\n" + "="*60)
        print("⚡ TESTING MARKET MOVE EXPLAINER MODULE - NVDA")
        print("="*60)
        
        # Test market move explanation for NVDA
        move_payload = {
            "ticker": "NVDA",
            "timestamp": "2024-11-14T10:00:00Z"
        }
        
        expected_fields = [
            'ticker', 'summary', 'drivers', 
            'confidence', 'timestamp'
        ]
        
        result = await self.test_endpoint("/member2/member2/explain-move", move_payload, expected_fields)
        self.test_results['market_move'] = result
        return result

    async def test_macro_gap_module(self):
        """Test Macro-Driven Gap Forecaster Module with NVDA"""
        print("\n" + "="*60)
        print("📰 TESTING MACRO GAP FORECASTER MODULE - NVDA")
        print("="*60)
        
        # Test gap prediction for NVDA
        gap_payload = {
            "asset": "NVDA",
            "question": "Will NVIDIA gap up or down tomorrow based on recent AI developments and earnings expectations? Analyze macro factors affecting semiconductor stocks."
        }
        
        expected_fields = [
            'asset', 'gap_prediction', 'primary_catalyst', 
            'confidence', 'macro_events', 'timestamp'
        ]
        
        result = await self.test_endpoint("/member3/member3/macro-gap", gap_payload, expected_fields)
        self.test_results['macro_gap'] = result
        return result

    async def test_health_endpoints(self):
        """Test all health endpoints"""
        print("\n" + "="*60)
        print("🩺 TESTING HEALTH ENDPOINTS")
        print("="*60)
        
        health_endpoints = [
            "/health",
            "/member1/member1/options-flow/health", 
            "/member2/member2/explain-move/health",
            "/member3/member3/macro-gap/health"
        ]
        
        health_results = {}
        for endpoint in health_endpoints:
            print(f"\n🩺 Testing {endpoint}")
            try:
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    if response.status == 200:
                        data = await response.json()
                        health_results[endpoint] = {
                            'status': '✅ HEALTHY',
                            'response': data
                        }
                        print(f"✅ {endpoint} is healthy")
                    else:
                        health_results[endpoint] = {
                            'status': f'❌ UNHEALTHY ({response.status})',
                            'error': await response.text()
                        }
                        print(f"❌ {endpoint} returned {response.status}")
            except Exception as e:
                health_results[endpoint] = {
                    'status': '💥 ERROR',
                    'exception': str(e)
                }
                print(f"💥 {endpoint} threw exception: {e}")
        
        self.test_results['health_checks'] = health_results
        return health_results

    async def run_full_test_suite(self):
        """Run comprehensive tests on all RAG systems - NVDA FOCUSED"""
        print("🚀 STARTING COMPREHENSIVE RAG SYSTEM TEST SUITE")
        print("🎯 FOCUSED ON NVIDIA (NVDA) - OUR AVAILABLE DATA")
        print("="*80)
        
        start_time = time.time()
        
        # Test all modules with NVDA
        await self.test_core_risk_module()
        await self.test_options_flow_module() 
        await self.test_market_move_module()
        await self.test_macro_gap_module()
        await self.test_health_endpoints()
        
        total_time = time.time() - start_time
        
        # Generate comprehensive report
        self.generate_test_report(total_time)

    def generate_test_report(self, total_time: float):
        """Generate comprehensive test report focused on NVDA data quality"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE NVDA RAG SYSTEMS TEST REPORT")
        print("="*80)
        
        print(f"🎯 Test Focus: NVIDIA (NVDA) Stock Analysis")
        print(f"⏱️  Total Test Time: {total_time:.2f} seconds")
        print(f"📅 Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Count successes and failures
        success_count = 0
        total_tests = 0
        
        for module, result in self.test_results.items():
            if module != 'health_checks':
                total_tests += 1
                if isinstance(result, dict) and result.get('status') == '✅ SUCCESS':
                    success_count += 1
        
        print(f"\n📈 SUCCESS RATE: {success_count}/{total_tests} ({(success_count/total_tests*100):.1f}%)")
        
        # Module-by-module results
        print("\n🔍 MODULE RESULTS (NVDA FOCUSED):")
        print("-" * 50)
        
        module_names = {
            'core_risk': '🛡️  Core Risk Assessment (NVDA)',
            'options_flow': '📈 Options Flow Analysis (NVDA)', 
            'market_move': '⚡ Market Move Explainer (NVDA)',
            'macro_gap': '📰 Macro Gap Forecaster (NVDA)'
        }
        
        for module_key, module_name in module_names.items():
            if module_key in self.test_results:
                result = self.test_results[module_key]
                status = result.get('status', 'UNKNOWN')
                response_time = result.get('response_time', 'N/A')
                confidence = result.get('confidence', 'N/A')
                evidence_chunks = result.get('evidence_chunks', 0)
                
                print(f"{module_name}")
                print(f"  Status: {status}")
                print(f"  Response Time: {response_time}")
                print(f"  Confidence: {confidence}")
                print(f"  Evidence Chunks: {evidence_chunks}")
                
                if result.get('missing_fields'):
                    print(f"  Missing Fields: {result['missing_fields']}")
                
                # Show evidence quality
                if result.get('evidence_details'):
                    evidence_sources = [ev.get('source', 'unknown') for ev in result['evidence_details'] if isinstance(ev, dict)]
                    print(f"  Evidence Sources: {set(evidence_sources)}")
                print()
        
        # Health check summary
        print("🩺 HEALTH CHECK SUMMARY:")
        print("-" * 30)
        if 'health_checks' in self.test_results:
            for endpoint, health in self.test_results['health_checks'].items():
                status = health.get('status', 'UNKNOWN')
                print(f"  {endpoint}: {status}")
        
        print("\n🎯 NVDA DATA ANALYSIS:")
        print("-" * 25)
        
        # Analyze NVDA-specific results
        findings = []
        
        # Check evidence quality for NVDA
        total_evidence = 0
        evidence_modules = 0
        low_evidence_modules = []
        
        for module_key, result in self.test_results.items():
            if isinstance(result, dict) and 'evidence_chunks' in result and module_key != 'health_checks':
                evidence_count = result['evidence_chunks']
                total_evidence += evidence_count
                evidence_modules += 1
                
                if evidence_count < 3:
                    low_evidence_modules.append(module_key)
        
        if evidence_modules > 0:
            avg_evidence = total_evidence / evidence_modules
            findings.append(f"Average evidence chunks per NVDA query: {avg_evidence:.1f}")
            
            if low_evidence_modules:
                findings.append(f"Modules with low evidence (<3 chunks): {low_evidence_modules}")
        
        # Check response times for NVDA queries
        response_times = []
        for module, result in self.test_results.items():
            if isinstance(result, dict) and 'response_time' in result and module != 'health_checks':
                try:
                    time_val = float(result['response_time'].replace('s', ''))
                    response_times.append(time_val)
                except:
                    pass
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            findings.append(f"Average NVDA query response time: {avg_time:.2f}s")
        
        # Check confidence scores for NVDA
        confidence_scores = []
        for module, result in self.test_results.items():
            if isinstance(result, dict) and 'confidence' in result and module != 'health_checks':
                conf = result['confidence']
                if isinstance(conf, (int, float)):
                    confidence_scores.append(conf)
        
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            findings.append(f"Average NVDA analysis confidence: {avg_confidence:.2f}")
        
        for finding in findings:
            print(f"  • {finding}")
        
        # NVDA-specific recommendations
        print("\n💡 NVDA DATA RECOMMENDATIONS:")
        print("-" * 35)
        
        recommendations = []
        
        if success_count < total_tests:
            recommendations.append("Fix failed NVDA endpoints - some modules not retrieving NVIDIA data properly")
        
        if low_evidence_modules:
            recommendations.append(f"Improve evidence retrieval for NVDA in modules: {low_evidence_modules}")
            recommendations.append("Check vector embeddings and database connections for NVIDIA-related content")
        
        if avg_evidence < 3:
            recommendations.append("CRITICAL: Evidence retrieval below threshold - need 3+ chunks per NVDA query")
            recommendations.append("Verify news_headlines, anomalies, and market_data tables contain NVDA records")
        
        if response_times and max(response_times) > 10:
            recommendations.append("Some NVDA queries taking too long - optimize database queries")
        
        if not recommendations:
            recommendations.append("✅ All NVDA RAG systems operational and returning quality evidence!")
            recommendations.append("Ready to implement 3-stage agent system with NVIDIA data")
            recommendations.append("Consider expanding to other stocks with similar data quality")
        
        for rec in recommendations:
            print(f"  • {rec}")
        
        print("\n🎯 NEXT STEPS FOR NVDA:")
        print("-" * 25)
        print("  • Fix float(None) bug in options_flow_service.py for news evidence")
        print("  • Ensure all modules return 3+ evidence chunks for NVDA")
        print("  • Validate confidence scores are realistic (0.7-0.9 range)")
        print("  • Test with additional NVDA-specific queries")
        print("  • Deploy to production with NVDA as primary test case")
        
        print("\n" + "="*80)
        print("🎉 NVDA RAG SYSTEMS TEST COMPLETE!")
        print("="*80)

async def main():
    """Main test execution for NVDA-focused testing"""
    print("🔧 Initializing NVDA-Focused RAG Systems Test Suite...")
    print("🎯 Testing with NVIDIA data that we know exists in our database")
    
    async with NVDARAGSystemTester() as tester:
        await tester.run_full_test_suite()

if __name__ == "__main__":
    asyncio.run(main())
