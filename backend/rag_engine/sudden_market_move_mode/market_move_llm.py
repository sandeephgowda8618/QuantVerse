"""
Market Move LLM - Language Model Integration for Move Explanation

This module handles LLM integration for market move causation analysis
"""

import json
import logging
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import pandas as pd

logger = logging.getLogger(__name__)

# Move explanation system prompt
MOVE_EXPLANATION_SYSTEM_PROMPT = """
You are a financial market analyst specializing in explaining sudden price movements and their underlying causes.

INSTRUCTIONS:
1. Analyze the provided evidence to identify the most likely cause of a market move
2. Consider timing correlation between news events and price movements
3. Distinguish between fundamental drivers (news, earnings, announcements) and technical/momentum factors
4. Assess whether moves are isolated to one asset or part of broader market trends
5. Provide confidence levels based on evidence quality and correlation strength
6. Never provide trading advice - only explain what likely caused past movements

ANALYSIS FRAMEWORK:
- Primary cause: The most likely single factor driving the move
- Contributing factors: Additional elements that amplified or supported the move
- Move classification: fundamental, technical, momentum, liquidity, or algorithmic
- Timing analysis: How well news events correlate with price action timing
- Cross-asset context: Whether similar moves occurred in related assets

OUTPUT FORMAT:
Always respond with valid JSON matching the exact schema provided.
"""

class MarketMoveLLM:
    """LLM integration for market move explanation and causation analysis"""
    
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        self.max_retries = 3
        self.timeout_seconds = 30
        
        # Move type classifications
        self.move_types = [
            "fundamental",  # News, earnings, announcements
            "technical",    # Chart patterns, support/resistance breaks
            "momentum",     # Follow-through buying/selling
            "liquidity",    # Low liquidity causing exaggerated moves
            "algorithmic",  # Algo trading patterns
            "unknown"       # Unable to determine primary driver
        ]
        
        logger.info("MarketMoveLLM initialized")
    
    async def explain_market_move(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to explain a market move using LLM analysis
        """
        try:
            # Build the analysis prompt
            prompt = self._build_move_explanation_prompt(context)
            
            # Get LLM response
            llm_response = await self._query_llm_with_retry(prompt)
            
            # Validate and format response
            explanation = self._validate_move_explanation(llm_response)
            
            # Calculate confidence based on evidence quality
            confidence = self._calculate_explanation_confidence(context, explanation)
            explanation['confidence'] = confidence
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error explaining market move: {str(e)}")
            return self._create_fallback_explanation(context, str(e))
    
    def _build_move_explanation_prompt(self, context: Dict[str, Any]) -> str:
        """Build comprehensive prompt for move explanation"""
        
        move_data = context.get('move_data', {})
        news_data = context.get('news_data', [])
        sentiment_data = context.get('sentiment_data', [])
        cross_asset_data = context.get('cross_asset_data', {})
        price_data = context.get('price_data', [])
        
        # Format move characteristics
        move_summary = self._format_move_summary(move_data)
        
        # Format news evidence
        news_summary = self._format_news_evidence(news_data)
        
        # Format sentiment analysis
        sentiment_summary = self._format_sentiment_evidence(sentiment_data)
        
        # Format cross-asset context
        cross_asset_summary = self._format_cross_asset_evidence(cross_asset_data)
        
        # Format price action context
        price_summary = self._format_price_action(price_data, move_data)
        
        prompt = f"""
MARKET MOVE ANALYSIS REQUEST

MOVE CHARACTERISTICS:
{move_summary}

PRICE ACTION CONTEXT:
{price_summary}

NEWS EVIDENCE:
{news_summary}

SENTIMENT ANALYSIS:
{sentiment_summary}

CROSS-ASSET CONTEXT:
{cross_asset_summary}

REQUIRED ANALYSIS:
Analyze the above evidence to explain the market move. Consider:
1. Which factor(s) most likely caused the price movement?
2. How well does the timing of news/events correlate with the price move?
3. Is this an isolated move or part of broader market activity?
4. What type of move is this (fundamental, technical, momentum, etc.)?

REQUIRED JSON RESPONSE FORMAT:
{{
    "move_explanation": "Clear, concise explanation of the primary cause",
    "move_type": "fundamental|technical|momentum|liquidity|algorithmic|unknown",
    "contributing_factors": [
        "Secondary factor 1",
        "Secondary factor 2",
        "Secondary factor 3"
    ],
    "timing_analysis": {{
        "primary_catalyst_timing": "immediate|close|lagged|weak",
        "timing_confidence": 0.8
    }},
    "evidence_quality": {{
        "news_correlation": 0.7,
        "sentiment_correlation": 0.6,
        "cross_asset_confirmation": 0.4
    }},
    "alternative_explanations": [
        "Other possible cause 1",
        "Other possible cause 2"
    ]
}}

Analyze the evidence and provide the JSON response:
"""
        
        return prompt
    
    def _format_move_summary(self, move_data: Dict) -> str:
        """Format move characteristics for prompt"""
        if not move_data:
            return "No move data available"
        
        magnitude = move_data.get('magnitude', 0)
        direction = move_data.get('direction', 'unknown')
        duration = move_data.get('duration_minutes', 0)
        volume_ratio = move_data.get('volume_ratio', 1)
        pattern = move_data.get('price_pattern', 'unknown')
        timestamp = move_data.get('timestamp', datetime.utcnow())
        
        return f"""
- Magnitude: {magnitude:+.2f}%
- Direction: {direction}
- Duration: {duration:.0f} minutes
- Volume: {volume_ratio:.1f}x average {'(spike)' if volume_ratio > 1.5 else '(normal)'}
- Pattern: {pattern}
- Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    def _format_price_action(self, price_data: List[Dict], move_data: Dict) -> str:
        """Format price action context"""
        if not price_data:
            return "No price data available"
        
        # Analyze price action patterns
        if len(price_data) >= 2:
            start_price = price_data[0].get('close', 0)
            end_price = price_data[-1].get('close', 0)
            high_price = max([p.get('high', 0) for p in price_data])
            low_price = min([p.get('low', 0) for p in price_data])
            
            return f"""
- Price range: ${low_price:.2f} - ${high_price:.2f}
- Start price: ${start_price:.2f}
- End price: ${end_price:.2f}
- Volatility: {((high_price - low_price) / start_price * 100):.1f}%
- Data points: {len(price_data)} intervals
"""
        
        return "Limited price action data"
    
    def _format_news_evidence(self, news_data: List[Dict]) -> str:
        """Format news evidence for prompt"""
        if not news_data:
            return "No relevant news found during move period"
        
        formatted_news = []
        for i, news in enumerate(news_data[:5]):  # Top 5 news items
            headline = news.get('headline', 'Unknown headline')
            source = news.get('source', 'Unknown source')
            timestamp = news.get('timestamp', datetime.utcnow())
            relevance = news.get('relevance_score', 0)
            sentiment = news.get('sentiment_score', 0)
            timing_score = news.get('timing_score', 0)
            
            formatted_news.append(
                f"{i+1}. [{source}] {headline}\n"
                f"   Time: {timestamp.strftime('%H:%M:%S')} | "
                f"Relevance: {relevance:.2f} | "
                f"Sentiment: {sentiment:+.2f} | "
                f"Timing: {timing_score:.2f}"
            )
        
        return "\n".join(formatted_news)
    
    def _format_sentiment_evidence(self, sentiment_data: List[Dict]) -> str:
        """Format sentiment analysis for prompt"""
        if not sentiment_data:
            return "No sentiment data available"
        
        # Calculate sentiment shifts
        before_sentiment = [s for s in sentiment_data if s.get('sentiment_period') == 'before']
        after_sentiment = [s for s in sentiment_data if s.get('sentiment_period') == 'after']
        
        before_avg = sum(s.get('sentiment_score', 0) for s in before_sentiment) / len(before_sentiment) if before_sentiment else 0
        after_avg = sum(s.get('sentiment_score', 0) for s in after_sentiment) / len(after_sentiment) if after_sentiment else 0
        
        sentiment_shift = after_avg - before_avg
        
        return f"""
- Sample size: {len(sentiment_data)} articles
- Before move sentiment: {before_avg:+.2f} (n={len(before_sentiment)})
- After move sentiment: {after_avg:+.2f} (n={len(after_sentiment)})
- Sentiment shift: {sentiment_shift:+.2f} {'(positive shift)' if sentiment_shift > 0.1 else '(negative shift)' if sentiment_shift < -0.1 else '(minimal shift)'}
- Overall trend: {'improving' if sentiment_shift > 0.1 else 'declining' if sentiment_shift < -0.1 else 'stable'}
"""
    
    def _format_cross_asset_evidence(self, cross_asset_data: Dict) -> str:
        """Format cross-asset correlation evidence"""
        if not cross_asset_data or not cross_asset_data.get('correlated_moves'):
            return "No significant cross-asset correlations detected"
        
        moves = cross_asset_data.get('correlated_moves', [])
        correlation_strength = cross_asset_data.get('correlation_strength', 0)
        market_wide = cross_asset_data.get('market_wide_event', False)
        
        move_details = []
        for move in moves[:5]:  # Top 5 correlated moves
            ticker = move.get('ticker', 'Unknown')
            magnitude = move.get('magnitude', 0)
            direction = move.get('direction', 'unknown')
            move_details.append(f"- {ticker}: {magnitude:+.2f}% ({direction})")
        
        summary = f"""
- Correlation strength: {correlation_strength:.2f}
- Market-wide event: {'Yes' if market_wide else 'No'}
- Correlated assets: {len(moves)}
"""
        
        if move_details:
            summary += "\nCorrelated moves:\n" + "\n".join(move_details)
        
        return summary
    
    async def _query_llm_with_retry(self, prompt: str) -> Dict[str, Any]:
        """Query LLM with retry logic"""
        for attempt in range(self.max_retries):
            try:
                # Use the LLM manager to get response
                response = await self.llm_manager.generate_response(
                    system_prompt=MOVE_EXPLANATION_SYSTEM_PROMPT,
                    user_prompt=prompt,
                    response_format="json"
                )
                
                # Parse JSON response
                if isinstance(response, str):
                    return json.loads(response)
                else:
                    return response
                    
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error on attempt {attempt + 1}: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
            except Exception as e:
                logger.warning(f"LLM query error on attempt {attempt + 1}: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                
                # Wait before retry
                await asyncio.sleep(1)
        
        raise Exception("Failed to get valid LLM response after all retries")
    
    def _validate_move_explanation(self, llm_response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize LLM response"""
        
        # Required fields with defaults
        validated = {
            'move_explanation': llm_response.get('move_explanation', 'Unable to determine primary cause'),
            'move_type': llm_response.get('move_type', 'unknown'),
            'contributing_factors': llm_response.get('contributing_factors', []),
            'timing_analysis': llm_response.get('timing_analysis', {
                'primary_catalyst_timing': 'unknown',
                'timing_confidence': 0.3
            }),
            'evidence_quality': llm_response.get('evidence_quality', {
                'news_correlation': 0.3,
                'sentiment_correlation': 0.3,
                'cross_asset_confirmation': 0.3
            }),
            'alternative_explanations': llm_response.get('alternative_explanations', [])
        }
        
        # Validate move_type
        if validated['move_type'] not in self.move_types:
            validated['move_type'] = 'unknown'
        
        # Limit array lengths
        validated['contributing_factors'] = validated['contributing_factors'][:5]
        validated['alternative_explanations'] = validated['alternative_explanations'][:3]
        
        # Validate timing analysis
        timing = validated['timing_analysis']
        if not isinstance(timing.get('timing_confidence'), (int, float)):
            timing['timing_confidence'] = 0.3
        timing['timing_confidence'] = max(0, min(1, timing['timing_confidence']))
        
        # Validate evidence quality scores
        evidence = validated['evidence_quality']
        for key in ['news_correlation', 'sentiment_correlation', 'cross_asset_confirmation']:
            if not isinstance(evidence.get(key), (int, float)):
                evidence[key] = 0.3
            evidence[key] = max(0, min(1, evidence[key]))
        
        return validated
    
    def _calculate_explanation_confidence(self, context: Dict, explanation: Dict) -> float:
        """Calculate overall confidence in the explanation"""
        
        # Base confidence from evidence quality
        evidence_quality = explanation.get('evidence_quality', {})
        news_correlation = evidence_quality.get('news_correlation', 0.3)
        sentiment_correlation = evidence_quality.get('sentiment_correlation', 0.3)
        cross_asset_confirmation = evidence_quality.get('cross_asset_confirmation', 0.3)
        
        # Timing confidence
        timing_confidence = explanation.get('timing_analysis', {}).get('timing_confidence', 0.3)
        
        # Calculate weighted confidence
        base_confidence = (
            news_correlation * 0.4 +
            timing_confidence * 0.3 +
            sentiment_correlation * 0.2 +
            cross_asset_confirmation * 0.1
        )
        
        # Boost for high-quality moves
        move_data = context.get('move_data', {})
        magnitude = abs(move_data.get('magnitude', 0))
        
        if magnitude > 5:  # Large moves are easier to explain
            magnitude_boost = 0.1
        elif magnitude > 2:
            magnitude_boost = 0.05
        else:
            magnitude_boost = 0
        
        # Penalize for lack of evidence
        news_count = len(context.get('news_data', []))
        if news_count == 0:
            evidence_penalty = 0.2
        elif news_count < 3:
            evidence_penalty = 0.1
        else:
            evidence_penalty = 0
        
        final_confidence = base_confidence + magnitude_boost - evidence_penalty
        
        return round(max(0.1, min(0.95, final_confidence)), 2)
    
    def _create_fallback_explanation(self, context: Dict, error: str) -> Dict[str, Any]:
        """Create fallback explanation when LLM fails"""
        move_data = context.get('move_data', {})
        magnitude = move_data.get('magnitude', 0)
        direction = move_data.get('direction', 'unknown')
        
        return {
            'move_explanation': f'Price {direction} movement of {magnitude:+.1f}% detected, but analysis failed',
            'move_type': 'unknown',
            'contributing_factors': ['Analysis system error', 'Insufficient data processing'],
            'timing_analysis': {
                'primary_catalyst_timing': 'unknown',
                'timing_confidence': 0.0
            },
            'evidence_quality': {
                'news_correlation': 0.0,
                'sentiment_correlation': 0.0,
                'cross_asset_confirmation': 0.0
            },
            'alternative_explanations': ['Technical trading', 'Random market movement'],
            'confidence': 0.1,
            'error': error
        }
