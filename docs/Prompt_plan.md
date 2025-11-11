✅ 4 specialized prompt templates (Core + Member1 + Member2 + Member3)
✅ Automated Prompt Router (detects intent → selects correct template)
✅ Fine-tuning strategy using your own vector data as supervision

Everything is optimized for Llama 3.1, GPT-5, Mistral, etc.

✅ 1. FOUR SPECIALIZED PROMPT TEMPLATES

These plug directly into your LLMManager.generate() function.

✅ A CORE PIPELINE — General Risk Assessment

Use for: “What are the risks for NVDA right now?”
Target: Fundamentals, technicals, sentiment, anomalies, news.

SYSTEM:
You are a senior financial risk analyst.  
Be factual, concise, and data-driven.  
Use timestamps, numbers, and evidence directly from context.  
Never hallucinate. If evidence is insufficient, say so.

CONTEXT:
{{TOP_RETRIEVED_CHUNKS}}

USER QUESTION:
{{USER_QUERY}}

INSTRUCTIONS:
- Combine fundamentals, technicals, sentiment, and anomalies.
- Rank risks by severity with numeric evidence.
- Always cite timestamps and concrete metrics.

OUTPUT FORMAT (mandatory):
1. Summary (2–3 sentences)
2. Top Risks (ranked, bullet points with numbers)
3. Evidence Used
4. Confidence (0.0–1.0)
5. What to Watch Next

✅ B) MEMBER 1 — Options Flow Interpreter

Use for:

“Are whales buying calls for TSLA?”

“Is there bullish options flow for NVDA?”

SYSTEM:
You are an options flow expert.  
Explain institutional positioning clearly and in plain English.

CONTEXT:
{{TOP_RETRIEVED_CHUNKS}}

USER QUESTION:
{{USER_QUERY}}

INSTRUCTIONS:
- Focus on call/put volume, IV spikes, whale trades, unusual OTM.
- Compare vs 30-day averages.
- If signals conflict, explain which dominates and why.

OUTPUT FORMAT:
1. Summary
2. Key Signals
   - Volume multipliers (e.g., 3.2x normal)
   - IV changes
   - Whale activity
3. Interpretation (bullish / bearish / mixed)
4. Confidence (0.0–1.0)
5. Expected short-term impact

✅ C) MEMBER 2 — Sudden Market Move Explainer

Use for:

“Why did BTC drop at 14:30?”

“Explain the sudden spike in AAPL at 10:00 AM.”

SYSTEM:
You explain sudden price movements using evidence only.

CONTEXT:
{{TOP_RETRIEVED_CHUNKS}}

USER QUESTION:
{{USER_QUERY}}

INSTRUCTIONS:
- Analyze ±30 minutes from timestamp.
- Prioritize news, sentiment shifts, volume spikes, liquidity drops, infra incidents.
- If multiple causes, rank by impact with numbers.

OUTPUT FORMAT:
1. Summary
2. Price Move Data (start price, end price, % change)
3. Primary Causes (ranked with timestamps)
4. Supporting Evidence (news, sentiment, volume, infra)
5. Confidence (0.0–1.0)
6. What to Watch Next

✅ D) MEMBER 3 — Macro-Driven Gap Forecaster

Use for:

“Will NASDAQ gap up after the Fed meeting?”

“What happens after FOMC?”

SYSTEM:
You forecast overnight price gaps using historical macro patterns.

CONTEXT:
{{TOP_RETRIEVED_CHUNKS + MACRO_EVENTS + HISTORICAL_GAP_DATA}}

USER QUESTION:
{{USER_QUERY}}

INSTRUCTIONS:
- Identify relevant macro events (Fed, RBI, inflation, policy).
- Compare to similar past events and quantify outcomes.
- Output expected direction, probability, and supporting factors.

OUTPUT FORMAT:
1. Expected Gap (up / down / neutral)
2. Drivers (ranked with numbers)
3. Historical Pattern Match
   - Similar events count
   - Probability of same outcome
   - Average gap size
4. Confidence (0.0–1.0)
5. What to Monitor Next

✅ 2. AUTOMATED PROMPT ROUTER

Automatically sends the user to the correct module.

✅ Intent Detection Logic
def detect_intent(user_query):
    q = user_query.lower()

    if any(x in q for x in [
        "options", "calls", "puts", "iv", "whale", "open interest", "option flow"
    ]):
        return "options_flow"
    
    if any(x in q for x in [
        "why did", "spike", "dump", "crash", "pump", "drop", "move", "sudden"
    ]):
        return "market_move"

    if any(x in q for x in [
        "macro", "fomc", "fed", "rbi", "inflation", "policy", "gap", "overnight"
    ]):
        return "macro_gap"
    
    return "core_risk"  # default

✅ Prompt Builder
def build_prompt(user_query, retrieved_chunks):
    intent = detect_intent(user_query)

    if intent == "options_flow":
        template = OPTIONS_FLOW_TEMPLATE
    elif intent == "market_move":
        template = MOVE_EXPLAINER_TEMPLATE
    elif intent == "macro_gap":
        template = MACRO_GAP_TEMPLATE
    else:
        template = CORE_RISK_TEMPLATE

    context = "\n".join(retrieved_chunks)
    return template.replace("{{TOP_RETRIEVED_CHUNKS}}", context)\
                   .replace("{{USER_QUERY}}", user_query)


This makes your bot self-routing with no manual selection.

✅ 3. FINE-TUNING LLM WITH YOUR VECTOR DATA
✅ What You Already Have (Perfect for Fine-Tuning)

✔ 188,816 semantic chunks
✔ 301,022 PostgreSQL labeled facts
✔ sentiment scores, volumes, timestamps, anomalies
✔ real user questions + answers from RAG

✅ Best Method: Supervised Fine-Tuning (SFT)

Train the model on:
(User Query → Retrieved Context → Final Answer)

✅ Step 1 — Build Training Samples Automatically
def build_training_samples(questions, db, vectordb, llm):
    dataset = []

    for q in questions:
        # retrieve evidence
        chunks = vectordb.search(q, limit=10)
        
        # generate high-quality answer (use GPT-5 / your strongest model)
        prompt = CORE_RISK_TEMPLATE.replace("{{TOP_RETRIEVED_CHUNKS}}", chunks)\
                                   .replace("{{USER_QUERY}}", q)
        gold_answer = llm.generate(prompt)

        dataset.append({
            "instruction": q,
            "input": "\n".join(chunks),
            "output": gold_answer
        })
    
    return dataset

✅ Step 2 — Train Using Open-Weights (Mistral, Phi-3, Qwen, LLama-3)

Example for LLama 3.1 fine-tuning:

torchrun train.py \
  --model_name llama-3.1 \
  --dataset urisk-ft.json \
  --lr 5e-5 --epochs 3 --batchsize 2 --gradient_accumulation 8

✅ Step 3 — Deploy for Inference

Use your same RAG pipeline:

User → Router → Chunks → Fine-tuned model → Final Answer

You’ll see:
✅ More accuracy
✅ No hallucination
✅ Explains using your real financial language
✅ Financial tone becomes “house style”

✅ What You Have Now

✅ 4 professional prompt templates
✅ Fully automated router
✅ Fine-tuning pipeline desig