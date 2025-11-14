
"""
Comprehensive Test Suite for All 4 RAG-Enabled LLM Systems
Tests all pipelines to ensure correct responses with:
- Suggestions/recommendations
- Co        # Test market move explanation with NVDA
        move_payload = {
            "ticker": "NVDA",
            "timestamp": "2024-11-07T10:00:00Z"
        }nce scores
- Top evidence chunks
- Proper analysis structure
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Any

class RAGSystemTester:
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
                    if 'evidence' in data:
                        evidence_count = len(data.get('evidence', []))
                    elif 'evidence_used' in data:
                        evidence_count = len(data.get('evidence_used', []))
                    elif 'vector_evidence' in data:
                        evidence_count = len(data.get('vector_evidence', []))
                    
                    result = {
                        'status': '✅ SUCCESS',
                        'response_time': f"{response_time:.2f}s",
                        'evidence_chunks': evidence_count,
                        'missing_fields': missing_fields,
                        'confidence': data.get('confidence', data.get('confidence_score', 'N/A')),
                        'response_size': len(str(data)),
                        'raw_response': data
                    }
                    
                    print(f"✅ SUCCESS - Response time: {response_time:.2f}s")
                    print(f"📊 Evidence chunks: {evidence_count}")
                    print(f"🎯 Confidence: {result['confidence']}")
                    
                    if missing_fields:
                        print(f"⚠️  Missing fields: {missing_fields}")
                    
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
        """Test Core Risk Assessment Module"""
        print("\n" + "="*60)
        print("🛡️  TESTING CORE RISK MODULE")
        print("="*60)
        
        # Test risk assessment with NVDA (ticker we have data for)
        risk_payload = {
            "message": "What are the current risk factors for NVIDIA stock?",
            "user_id": "test_user"
        }
        
        expected_fields = [
            'answer', 'confidence', 'evidence', 'timestamp'
        ]
        
        result = await self.test_endpoint("/chat/", risk_payload, expected_fields)
        self.test_results['core_risk'] = result
        return result

    async def test_options_flow_module(self):
        """Test Options Flow Analysis Module"""
        print("\n" + "="*60)
        print("📈 TESTING OPTIONS FLOW MODULE")
        print("="*60)
        
        # Test options flow analysis with NVDA (ticker we have news data for)
        options_payload = {
            "ticker": "NVDA",
            "user_question": "Analyze unusual options activity for NVIDIA"
        }
        
        expected_fields = [
            'ticker', 'insight', 'reasons', 
            'confidence', 'evidence', 'timestamp'
        ]
        
        result = await self.test_endpoint("/member1/member1/options-flow", options_payload, expected_fields)
        self.test_results['options_flow'] = result
        return result

    async def test_market_move_module(self):
        """Test Sudden Market Move Explainer Module"""
        print("\n" + "="*60)
        print("⚡ TESTING MARKET MOVE EXPLAINER MODULE")
        print("="*60)
        
        # Test market move explanation with NVDA
        move_payload = {
            "ticker": "NVDA", 
            "timestamp": "2025-11-07T10:00:00Z"
        }
        
        expected_fields = [
            'ticker', 'summary', 'drivers', 
            'confidence', 'timestamp'
        ]
        
        result = await self.test_endpoint("/member2/member2/explain-move", move_payload, expected_fields)
        self.test_results['market_move'] = result
        return result

    async def test_macro_gap_module(self):
        """Test Macro-Driven Gap Forecaster Module"""
        print("\n" + "="*60)
        print("📰 TESTING MACRO GAP FORECASTER MODULE")
        print("="*60)
        
        # Test gap prediction with NVDA
        gap_payload = {
            "asset": "NVDA",
            "question": "Will NVDA gap up or down tomorrow based on AI developments?"
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
        """Run comprehensive tests on all RAG systems"""
        print("🚀 STARTING COMPREHENSIVE RAG SYSTEM TEST SUITE")
        print("="*80)
        
        start_time = time.time()
        
        # Test all modules
        await self.test_core_risk_module()
        await self.test_options_flow_module() 
        await self.test_market_move_module()
        await self.test_macro_gap_module()
        await self.test_health_endpoints()
        
        total_time = time.time() - start_time
        
        # Generate comprehensive report
        self.generate_test_report(total_time)

    def generate_test_report(self, total_time: float):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE RAG SYSTEMS TEST REPORT")
        print("="*80)
        
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
        print("\n🔍 MODULE RESULTS:")
        print("-" * 50)
        
        module_names = {
            'core_risk': '🛡️  Core Risk Assessment',
            'options_flow': '📈 Options Flow Analysis', 
            'market_move': '⚡ Market Move Explainer',
            'macro_gap': '📰 Macro Gap Forecaster'
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
                print()
        
        # Health check summary
        print("🩺 HEALTH CHECK SUMMARY:")
        print("-" * 30)
        if 'health_checks' in self.test_results:
            for endpoint, health in self.test_results['health_checks'].items():
                status = health.get('status', 'UNKNOWN')
                print(f"  {endpoint}: {status}")
        
        print("\n🎯 KEY FINDINGS:")
        print("-" * 20)
        
        # Analyze results for key findings
        findings = []
        
        # Check response times
        avg_response_time = 0
        response_count = 0
        for module, result in self.test_results.items():
            if isinstance(result, dict) and 'response_time' in result:
                try:
                    time_val = float(result['response_time'].replace('s', ''))
                    avg_response_time += time_val
                    response_count += 1
                except:
                    pass
        
        if response_count > 0:
            avg_response_time = avg_response_time / response_count
            findings.append(f"Average response time: {avg_response_time:.2f}s")
        
        # Check evidence quality
        total_evidence = 0
        evidence_count = 0
        for module, result in self.test_results.items():
            if isinstance(result, dict) and 'evidence_chunks' in result:
                total_evidence += result['evidence_chunks']
                evidence_count += 1
        
        if evidence_count > 0:
            avg_evidence = total_evidence / evidence_count
            findings.append(f"Average evidence chunks per response: {avg_evidence:.1f}")
        
        # Check confidence scores
        confidence_scores = []
        for module, result in self.test_results.items():
            if isinstance(result, dict) and 'confidence' in result:
                conf = result['confidence']
                if isinstance(conf, (int, float)):
                    confidence_scores.append(conf)
        
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            findings.append(f"Average confidence score: {avg_confidence:.2f}")
        
        for finding in findings:
            print(f"  • {finding}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 25)
        
        recommendations = []
        
        if success_count < total_tests:
            recommendations.append("Fix failed endpoints before production deployment")
        
        if avg_response_time > 5.0:
            recommendations.append("Optimize response times - currently averaging over 5 seconds")
        
        if evidence_count > 0 and total_evidence / evidence_count < 3:
            recommendations.append("Increase evidence retrieval - aim for 3+ chunks per response")
        
        if not recommendations:
            recommendations.append("All systems operational - ready for production!")
            recommendations.append("Consider implementing the 3-stage agent system with real-time tools")
            recommendations.append("Monitor performance and add caching for improved response times")
        
        for rec in recommendations:
            print(f"  • {rec}")
        
        print("\n" + "="*80)
        print("🎉 RAG SYSTEMS TEST COMPLETE!")
        print("="*80)

async def main():
    """Main test execution"""
    print("🔧 Initializing RAG Systems Test Suite...")
    
    async with RAGSystemTester() as tester:
        await tester.run_full_test_suite()

if __name__ == "__main__":
    asyncio.run(main())
