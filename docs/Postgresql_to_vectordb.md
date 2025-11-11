# PostgreSQL → ChromaDB Incremental Sync Pipeline

## 🎯 Core Objective

Take only new/updated rows from PostgreSQL, convert financial records into semantic chunks, embed them, and upsert to ChromaDB with no duplicates while tracking sync state for crash recovery.

## ✅ What Goes Into ChromaDB?

| Dataset | Goes to Chroma? | Reason |
|---------|----------------|--------|
| ✅ Technical Indicators (RSI, EMA, BBANDS…) | ✅ YES | Used as evidence in /chat, anomaly explanation, forecasting |
| ✅ Time Series (Daily/Weekly/Monthly OHLCV) | ✅ YES (summarized) | Useful for moves explanation + market trend evidence |
| ✅ Fundamentals (Company overview, earnings, balance sheet) | ✅ YES | Supports macro/gap forecasting, sentiment reasoning |
| ✅ Market Intelligence (top gainers, market status) | ✅ YES | Evidence for broad market impact explanations |
| ✅ News Sentiment | ✅ YES | Core RAG evidence |
| ✅ Options Metrics | ✅ YES | Member-1 options explainer |
| ✅ Foreign Assets, Crypto, Indices | ✅ YES | Cross-asset risk reasoning |
| ❌ Raw JSON payloads | ❌ No | Too noisy, not useful to LLM |
| ❌ Market prices raw OHLCV | ❌ No direct | Only summarized features go |

## ✅ ChromaDB Collection Structure

**Collection Name:** `urisk_chunks`

| Field | Type | Purpose |
|-------|------|---------|
| id | string | unique: table_rowid_chunkindex |
| text | string | chunked summary or sentence |
| embedding | vector | SentenceTransformer/Llama |
| ticker | string | NVDA, MSFT, BTC, etc |
| asset_type | string | stock, crypto, index, forex |
| source | string | alpha_vantage, finnhub, sec |
| endpoint | string | RSI, EMA, BBANDS, EARNINGS… |
| risk_type | string | sentiment, technical, regulatory, macro |
| timestamp | datetime | recency filter |
| sector | string | tech, energy, finance… |
| severity | optional | used for anomaly/incidents |
| anomaly_flag | bool | for sudden-move explanations |

## ✅ Sync State Tracking

```sql
CREATE TABLE IF NOT EXISTS vector_sync_state (
  table_name VARCHAR(100) PRIMARY KEY,
  last_synced_at TIMESTAMP,
  records_synced BIGINT DEFAULT 0,
  last_chunk_id VARCHAR(255)
);
```

## ✅ Data Selection Logic

### 1. Technical Indicators
```sql
SELECT id, ticker, endpoint, timestamp, parsed_values
FROM alpha_vantage_data
WHERE endpoint IN ('RSI','EMA','BBANDS','MFI','ADX','TRIX')
  AND timestamp > :last_synced
ORDER BY timestamp ASC
LIMIT 1000;
```

**Chunk Format:**
```
"On 2025-11-07, NVDA RSI was 74.44, indicating overbought momentum."
```

### 2. Fundamentals
```sql
SELECT id, ticker, endpoint, timestamp, parsed_values
FROM alpha_vantage_data
WHERE endpoint IN ('OVERVIEW','EARNINGS','BALANCE_SHEET','CASH_FLOW')
  AND timestamp > :last_synced;
```

**Chunk Format:**
```
"Microsoft reported $56B revenue, +9% YoY. EPS: $2.98. PE: 35.1."
```

### 3. Time Series (Summarized)
**Chunk Format:**
```
"Between Oct 1 and Nov 7, MSFT gained 7.2% with rising volume. Trend bullish."
```

### 4. News & Sentiment
```sql
SELECT h.headline, h.published_at, s.sentiment_score
FROM news_headlines h
LEFT JOIN news_sentiment s ON s.headline_id = h.id
WHERE h.published_at > :last_synced
ORDER BY h.published_at ASC;
```

**Chunk Format:**
```
"Negative sentiment for BTC on Nov 6: 'Binance pauses withdrawals'. score -0.61."
```

### 5. Incidents / Anomalies
```sql
SELECT ticker, explanation, severity, timestamp
FROM anomalies
WHERE timestamp > :last_synced;
```

**Chunk Format:**
```
"High-severity anomaly: BTC liquidity spike +4x on Nov 5. Market-wide panic."
```

## ✅ Chunk Structure Before Embedding

```json
{
  "text": "On 2025-11-07, NVDA RSI was 71.47, indicating strong bullish momentum.",
  "metadata": {
    "ticker": "NVDA",
    "asset_type": "stock",
    "endpoint": "RSI",
    "risk_type": "technical",
    "timestamp": "2025-11-07T10:32:00Z",
    "severity": "low",
    "source": "alpha_vantage"
  },
  "id": "alpha_rsi_394923_0"
}
```

## ✅ Full Pipeline Flow

1. **Connect** to Postgres & ChromaDB
2. **Read** vector_sync_state for each table
3. **Pull** only rows where timestamp > last_synced
4. **Convert** data → human-readable chunks
5. **Chunk** long text (fundamentals, transcripts)
6. **Embed** (batch 64-128 for speed)
7. **Upsert** to ChromaDB with unique chunk_id
8. **Write** new last_synced timestamp
9. **Log** summary (#chunks added, #skipped)

## ✅ Run Schedule Options

| Mode | Frequency | Why |
|------|-----------|-----|
| Manual script | run anytime | testing |
| Cron job | every 30 min or hourly | near-real-time ChromaDB |
| On-demand API trigger | when ingest completes | automation |

## ✅ Continuous RAG Operation

After sync pipeline, the RAG engine becomes a real-time evidence retrieval system:

### Real-time Query Flow:
```
POST /chat → rag_service.query() → retriever.search_in_chroma() → reranker.rank_results() → llama_engine.generate_reply() → JSON response
```

### Retrieval Logic:
```python
results = chroma_collection.query(
    query_texts=[user_message],
    n_results=40,
    where={
        "ticker": ticker_if_detected,
        "timestamp": {"$gte": cutoff_time},
        "severity": {"$in": ["medium","high"]}
    }
)
```

### Output Benefits:
- ✅ `/chat` can retrieve accurate evidence ("RSI high", "earnings positive", "market outage")
- ✅ Member-1 gets options flow evidence (RAG + anomalies)
- ✅ Member-2 explains sudden moves using news, sentiment, anomalies
- ✅ Member-3 predicts macro-driven gaps using regulatory chunks

## ✅ Implementation Components

### Core Files:
- `backend/rag_engine/retriever.py` - Vector DB semantic search + metadata filters
- `backend/rag_engine/reranker.py` - Cross-encoder re-ranking
- `backend/rag_engine/llama_engine.py` - Local Llama with system prompt
- `backend/rag_engine/rag_service.py` - Orchestrates everything
- `backend/rag_engine/vector_store.py` - ChromaDB adapter
- `backend/services/postgres_to_vectordb.py` - Main sync pipeline

This turns PostgreSQL into a searchable knowledge graph for the LLM, enabling real-time market intelligence and risk analysis.
