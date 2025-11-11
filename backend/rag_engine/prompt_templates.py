"""
QuantVerse uRISK - Specialized Prompt Templates
Four optimized templates for different analysis modes with automated routing
"""

class PromptTemplates:
    """
    Four specialized prompt templates for financial analysis:
    1. Core Risk Assessment (general analysis)
    2. Options Flow Interpreter (institutional positioning)
    3. Market Move Explainer (sudden price movements)
    4. Macro Gap Forecaster (overnight gaps from macro events)
    """
    
    @staticmethod
    def get_core_risk_template():
        """Template A: Core Pipeline - General Risk Assessment"""
        return """You are a senior financial risk analyst.
Be factual, concise, and data-driven.
Use timestamps, numbers, and evidence directly from context.
Never hallucinate. If evidence is insufficient, say so.

FINANCIAL DATA CONTEXT:
{{TOP_RETRIEVED_CHUNKS}}

USER QUESTION:
{{USER_QUERY}}

INSTRUCTIONS:
- Combine fundamentals, technicals, sentiment, and anomalies.
- Rank risks by severity with numeric evidence.
- Always cite timestamps and concrete metrics.

OUTPUT FORMAT (mandatory):
1. **Summary** (2–3 sentences)
2. **Top Risks** (ranked, bullet points with numbers)
3. **Evidence Used** (specific data points with timestamps)
4. **Confidence** (0.0–1.0)
5. **What to Watch Next** (monitoring recommendations)"""

    @staticmethod
    def get_options_flow_template():
        """Template B: Member 1 - Options Flow Interpreter"""
        return """You are an options flow expert.
Explain institutional positioning clearly and in plain English.

FINANCIAL DATA CONTEXT:
{{TOP_RETRIEVED_CHUNKS}}

USER QUESTION:
{{USER_QUERY}}

INSTRUCTIONS:
- Focus on call/put volume, IV spikes, whale trades, unusual OTM activity.
- Compare vs 30-day averages when available.
- If signals conflict, explain which dominates and why.

OUTPUT FORMAT:
1. **Summary** (bullish/bearish/mixed positioning)
2. **Key Signals**
   - Volume multipliers (e.g., 3.2x normal)
   - IV changes (% increases/decreases)
   - Whale activity (large block trades)
   - Unusual strikes (OTM activity)
3. **Interpretation** (bullish / bearish / mixed with reasoning)
4. **Confidence** (0.0–1.0)
5. **Expected Short-term Impact** (likely price direction and timeframe)"""

    @staticmethod
    def get_market_move_template():
        """Template C: Member 2 - Sudden Market Move Explainer"""
        return """You explain sudden price movements using evidence only.

FINANCIAL DATA CONTEXT:
{{TOP_RETRIEVED_CHUNKS}}

USER QUESTION:
{{USER_QUERY}}

INSTRUCTIONS:
- Analyze ±30 minutes from any specified timestamp.
- Prioritize news, sentiment shifts, volume spikes, liquidity drops, infrastructure incidents.
- If multiple causes exist, rank by impact with supporting numbers.

OUTPUT FORMAT:
1. **Summary** (what happened in 1-2 sentences)
2. **Price Move Data**
   - Start price / End price / % change
   - Volume comparison vs average
   - Timeframe of movement
3. **Primary Causes** (ranked with timestamps)
4. **Supporting Evidence**
   - News events (with timestamps)
   - Sentiment shifts (sentiment scores)
   - Volume anomalies (volume multipliers)
   - Infrastructure issues (exchange outages, etc.)
5. **Confidence** (0.0–1.0)
6. **What to Watch Next** (follow-up indicators to monitor)"""

    @staticmethod
    def get_macro_gap_template():
        """Template D: Member 3 - Macro-Driven Gap Forecaster"""
        return """You forecast overnight price gaps using historical macro patterns.

FINANCIAL DATA CONTEXT:
{{TOP_RETRIEVED_CHUNKS}}

USER QUESTION:
{{USER_QUERY}}

INSTRUCTIONS:
- Identify relevant macro events (Fed meetings, RBI announcements, inflation data, policy changes).
- Compare to similar past events and quantify historical outcomes.
- Output expected direction, probability, and supporting factors with numbers.

OUTPUT FORMAT:
1. **Expected Gap** (gap up / gap down / neutral)
2. **Drivers** (ranked with quantitative support)
   - Macro event impact (Fed dovish/hawkish, etc.)
   - Historical precedent (% of similar events)
   - Current market positioning
   - Overnight futures movement
3. **Historical Pattern Match**
   - Similar events count (X similar events found)
   - Probability of same outcome (X% gap up/down historically)
   - Average gap size (X.X% typical gap)
4. **Confidence** (0.0-1.0)
5. **What to Monitor Next** (overnight indicators, futures, global markets)"""


class IntentRouter:
    """
    Automated intent detection and prompt routing system
    Analyzes user queries to determine the appropriate analysis module
    """
    
    @staticmethod
    def detect_intent(user_query: str) -> str:
        """
        Detect user intent from query text and route to appropriate module
        
        Args:
            user_query: User's question/request
            
        Returns:
            str: Intent type ('options_flow', 'market_move', 'macro_gap', 'core_risk')
        """
        q = user_query.lower()
        
        # Options flow keywords
        options_keywords = [
            "options", "calls", "puts", "iv", "implied volatility", 
            "whale", "whales", "open interest", "option flow", "options flow",
            "institutional", "positioning", "oi", "strikes", "otm", "itm",
            "expiry", "expiration", "gamma", "delta", "vega"
        ]
        
        # Market move explanation keywords  
        move_keywords = [
            "why did", "spike", "dump", "crash", "pump", "drop", "move", 
            "sudden", "jumped", "fell", "movement", "explain", "caused",
            "price action", "volatility", "swing", "breakout", "breakdown"
        ]
        
        # Macro gap forecasting keywords
        macro_keywords = [
            "macro", "fomc", "fed", "federal reserve", "rbi", "reserve bank",
            "inflation", "policy", "gap", "overnight", "gap up", "gap down",
            "pre-market", "after hours", "earnings", "announcement", 
            "guidance", "forecast", "prediction", "will it gap", "tomorrow"
        ]
        
        # Check for intent matches
        if any(keyword in q for keyword in options_keywords):
            return "options_flow"
            
        if any(keyword in q for keyword in move_keywords):
            return "market_move"
            
        if any(keyword in q for keyword in macro_keywords):
            return "macro_gap"
            
        # Default to core risk assessment
        return "core_risk"
    
    @staticmethod
    def get_template_by_intent(intent: str) -> str:
        """Get the appropriate prompt template for detected intent"""
        templates = {
            "options_flow": PromptTemplates.get_options_flow_template(),
            "market_move": PromptTemplates.get_market_move_template(), 
            "macro_gap": PromptTemplates.get_macro_gap_template(),
            "core_risk": PromptTemplates.get_core_risk_template()
        }
        
        return templates.get(intent, PromptTemplates.get_core_risk_template())


class PromptBuilder:
    """
    Builds complete prompts by combining templates with retrieved context
    """
    
    @staticmethod
    def build_prompt(user_query: str, retrieved_chunks: list) -> tuple[str, str]:
        """
        Build complete prompt with automatic intent detection and routing
        
        Args:
            user_query: User's question
            retrieved_chunks: List of relevant document chunks from vector search
            
        Returns:
            tuple: (complete_prompt, detected_intent)
        """
        # Detect intent and get appropriate template
        intent = IntentRouter.detect_intent(user_query)
        template = IntentRouter.get_template_by_intent(intent)
        
        # Format retrieved chunks into context
        if retrieved_chunks:
            context_sections = []
            for i, chunk in enumerate(retrieved_chunks[:10]):  # Top 10 chunks
                if isinstance(chunk, dict):
                    # Handle chunk objects with metadata
                    content = chunk.get('content', str(chunk))
                    metadata = chunk.get('metadata', {})
                    ticker = metadata.get('ticker', 'UNKNOWN')
                    endpoint = metadata.get('endpoint', 'UNKNOWN')  
                    timestamp = metadata.get('timestamp', 'UNKNOWN')
                    
                    context_sections.append(f"[{ticker} | {endpoint} | {timestamp}]\n{content}")
                else:
                    # Handle simple text chunks
                    context_sections.append(f"[Evidence {i+1}]\n{chunk}")
                    
            context = "\n\n".join(context_sections)
        else:
            context = "[No relevant financial data found in knowledge base]"
        
        # Replace placeholders in template
        complete_prompt = template.replace("{{TOP_RETRIEVED_CHUNKS}}", context)
        complete_prompt = complete_prompt.replace("{{USER_QUERY}}", user_query)
        
        return complete_prompt, intent
    
    @staticmethod
    def build_specialized_prompt(user_query: str, retrieved_chunks: list, intent: str) -> str:
        """
        Build prompt with specific intent (bypass auto-detection)
        
        Args:
            user_query: User's question
            retrieved_chunks: List of relevant document chunks
            intent: Specific intent to use ('options_flow', 'market_move', 'macro_gap', 'core_risk')
            
        Returns:
            str: Complete formatted prompt
        """
        template = IntentRouter.get_template_by_intent(intent)
        
        # Format context
        if retrieved_chunks:
            context_sections = []
            for i, chunk in enumerate(retrieved_chunks[:10]):
                if isinstance(chunk, dict):
                    content = chunk.get('content', str(chunk))
                    metadata = chunk.get('metadata', {})
                    ticker = metadata.get('ticker', 'UNKNOWN')
                    endpoint = metadata.get('endpoint', 'UNKNOWN')
                    timestamp = metadata.get('timestamp', 'UNKNOWN')
                    
                    context_sections.append(f"[{ticker} | {endpoint} | {timestamp}]\n{content}")
                else:
                    context_sections.append(f"[Evidence {i+1}]\n{chunk}")
                    
            context = "\n\n".join(context_sections)
        else:
            context = "[No relevant financial data found in knowledge base]"
            
        # Replace placeholders
        complete_prompt = template.replace("{{TOP_RETRIEVED_CHUNKS}}", context)
        complete_prompt = complete_prompt.replace("{{USER_QUERY}}", user_query)
        
        return complete_prompt


# Example usage and testing
if __name__ == "__main__":
    # Test intent detection
    test_queries = [
        "What are the risks for NVDA right now?",  # core_risk
        "Are whales buying calls for TSLA?",        # options_flow
        "Why did BTC drop at 14:30?",              # market_move
        "Will NASDAQ gap up after the Fed meeting?" # macro_gap
    ]
    
    print("🧪 Testing Intent Detection:")
    for query in test_queries:
        intent = IntentRouter.detect_intent(query)
        print(f"Query: '{query}' → Intent: {intent}")
    
    print("\n✅ Prompt templates ready for integration!")
