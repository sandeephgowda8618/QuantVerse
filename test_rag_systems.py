#!/usr/bin/env python3
"""
Test script for the 3 RAG-based LLM systems in uRISK platform
Tests all member endpoints with sample queries

Usage: python test_rag_systems.py
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base URL for the uRISK API
BASE_URL = "http://localhost:8000"

async def test_member1_options_flow():
    """Test Member 1 - Options Flow Interpreter"""
    logger.info("🔍 Testing Member 1 - Options Flow Interpreter")
    
    test_cases = [
        {
            "ticker": "NVDA",
            "user_question": "Are institutional traders buying calls for NVDA?"
        },
        {
            "ticker": "TSLA", 
            "user_question": "What's the options flow showing for Tesla right now?"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            try:
                logger.info(f"  Test {i}: {test_case['ticker']} - {test_case['user_question']}")
                
                async with session.post(
                    f"{BASE_URL}/member1/options-flow",
                    json=test_case,
                    timeout=30
                ) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        logger.info(f"    ✅ Success - Confidence: {result.get('confidence', 'N/A')}")
                        logger.info(f"    📊 Insight: {result.get('insight', 'N/A')[:100]}...")
                    else:
                        logger.error(f"    ❌ Failed - Status: {response.status}")
                        logger.error(f"    Error: {result}")
                        
            except Exception as e:
                logger.error(f"    ❌ Exception: {str(e)}")

async def test_member2_market_move():
    """Test Member 2 - Sudden Market Move Explainer"""
    logger.info("🔍 Testing Member 2 - Sudden Market Move Explainer")
    
    # First, get recent moves to test with
    async with aiohttp.ClientSession() as session:
        try:
            # Get recent moves for NVDA
            async with session.get(f"{BASE_URL}/member2/detect-moves/NVDA?hours_back=48") as response:
                moves_data = await response.json()
                recent_moves = moves_data.get('recent_moves', [])
                
                if not recent_moves:
                    logger.warning("  No recent significant moves found, using sample timestamp")
                    test_timestamp = "2025-11-14T14:30:00Z"
                else:
                    test_timestamp = recent_moves[0]['timestamp']
                    logger.info(f"  Found recent move at {test_timestamp}")
                
        except Exception as e:
            logger.warning(f"  Could not get recent moves, using sample: {str(e)}")
            test_timestamp = "2025-11-14T14:30:00Z"
    
    test_cases = [
        {
            "ticker": "NVDA",
            "timestamp": test_timestamp
        },
        {
            "ticker": "BTC",
            "timestamp": "2025-11-14T10:00:00Z"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            try:
                logger.info(f"  Test {i}: Explaining {test_case['ticker']} move at {test_case['timestamp']}")
                
                async with session.post(
                    f"{BASE_URL}/member2/explain-move",
                    json=test_case,
                    timeout=30
                ) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        logger.info(f"    ✅ Success - Confidence: {result.get('confidence', 'N/A')}")
                        logger.info(f"    📊 Summary: {result.get('summary', 'N/A')[:100]}...")
                    elif response.status == 404:
                        logger.info(f"    ℹ️  No significant move detected (expected for some tests)")
                    else:
                        logger.error(f"    ❌ Failed - Status: {response.status}")
                        logger.error(f"    Error: {result}")
                        
            except Exception as e:
                logger.error(f"    ❌ Exception: {str(e)}")

async def test_member3_macro_gap():
    """Test Member 3 - Macro-Driven Gap Forecaster"""
    logger.info("🔍 Testing Member 3 - Macro-Driven Gap Forecaster")
    
    test_cases = [
        {
            "asset": "NASDAQ",
            "question": "Will NASDAQ gap up after the next FOMC meeting?"
        },
        {
            "asset": "NVDA",
            "question": "What's the overnight gap prediction for NVIDIA considering recent inflation data?"
        },
        {
            "asset": "BTC",
            "question": "How will Bitcoin gap based on regulatory announcements?"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            try:
                logger.info(f"  Test {i}: {test_case['asset']} - {test_case['question']}")
                
                async with session.post(
                    f"{BASE_URL}/member3/macro-gap",
                    json=test_case,
                    timeout=30
                ) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        logger.info(f"    ✅ Success - Confidence: {result.get('confidence', 'N/A')}")
                        gap_pred = result.get('gap_prediction', {})
                        direction = gap_pred.get('direction', 'N/A')
                        magnitude = gap_pred.get('magnitude_estimate', 'N/A')
                        logger.info(f"    📊 Prediction: {direction} ({magnitude})")
                    else:
                        logger.error(f"    ❌ Failed - Status: {response.status}")
                        logger.error(f"    Error: {result}")
                        
            except Exception as e:
                logger.error(f"    ❌ Exception: {str(e)}")

async def test_health_endpoints():
    """Test health endpoints for all services"""
    logger.info("🔍 Testing Health Endpoints")
    
    endpoints = [
        "/member1/options-flow/health",
        "/member2/explain-move/health", 
        "/member3/macro-gap/health",
        "/health"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            try:
                logger.info(f"  Testing {endpoint}")
                async with session.get(f"{BASE_URL}{endpoint}") as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        status = result.get('status', 'unknown')
                        logger.info(f"    ✅ {endpoint} - Status: {status}")
                    else:
                        logger.error(f"    ❌ {endpoint} - Failed with status {response.status}")
                        
            except Exception as e:
                logger.error(f"    ❌ {endpoint} - Exception: {str(e)}")

async def test_batch_functionality():
    """Test batch and advanced endpoints"""
    logger.info("🔍 Testing Batch and Advanced Functionality")
    
    async with aiohttp.ClientSession() as session:
        # Test batch gap prediction
        try:
            logger.info("  Testing batch gap prediction")
            batch_request = {
                "assets": ["NVDA", "TSLA", "AAPL"],
                "event_context": "Federal Reserve interest rate decision"
            }
            
            async with session.post(
                f"{BASE_URL}/member3/batch-gap-prediction",
                json=batch_request,
                timeout=45
            ) as response:
                result = await response.json()
                
                if response.status == 200:
                    logger.info(f"    ✅ Batch prediction success - {len(result)} results")
                else:
                    logger.error(f"    ❌ Batch prediction failed - Status: {response.status}")
                    
        except Exception as e:
            logger.error(f"    ❌ Batch prediction exception: {str(e)}")
        
        # Test recent options activity
        try:
            logger.info("  Testing recent options activity")
            async with session.get(f"{BASE_URL}/member1/options-flow/recent/NVDA?hours_back=24") as response:
                result = await response.json()
                
                if response.status == 200:
                    logger.info(f"    ✅ Recent activity success")
                else:
                    logger.error(f"    ❌ Recent activity failed - Status: {response.status}")
                    
        except Exception as e:
            logger.error(f"    ❌ Recent activity exception: {str(e)}")

async def main():
    """Main test function"""
    logger.info("🚀 Starting uRISK RAG-based LLM Systems Test Suite")
    logger.info(f"🎯 Target URL: {BASE_URL}")
    logger.info("=" * 60)
    
    # Run all tests
    try:
        await test_health_endpoints()
        logger.info("=" * 60)
        
        await test_member1_options_flow()
        logger.info("=" * 60)
        
        await test_member2_market_move()
        logger.info("=" * 60)
        
        await test_member3_macro_gap()
        logger.info("=" * 60)
        
        await test_batch_functionality()
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test suite failed: {str(e)}")
    
    logger.info("✅ Test suite completed!")
    logger.info("🎉 All 3 RAG-based LLM systems have been tested!")

if __name__ == "__main__":
    asyncio.run(main())
