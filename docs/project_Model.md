 QuantVerse
Unified Risk Intelligence & Surveillance Kernel
A local RAG-based LLM system that monitors multi-layered financial risks and exposes a REST chat API + React chatbot UI.

 1. FULL PROJECT DIRECTORY STRUCTURE
urisk/
│
├── backend/
│   ├── app.py                         # FastAPI entrypoint (mounts routes + health)
│   ├── config/
│   │   ├── settings.py                # API keys, env vars, secrets loader (DO NOT COMMIT)
│   │   ├── scheduler_config.py        # cron/poll frequencies
│   │
│   ├── routes/
│   │   ├── chat_routes.py             # POST /chat -> RAG + LLM
│   │   ├── risk_routes.py             # /risk-alerts, /health, /assets
│   │   ├── analytics_routes.py        # /sentiment, /anomalies, /retrieve
│   │   ├── ml_routes.py               # Internal ML inference proxies (see note)
│   │   ├── member1/
│   │   │   ├── options_flow_routes.py
│   │   ├── member2/
│   │   │   ├── explain_move_routes.py
│   │   ├── member3/
│   │   │   ├── macro_gap_routes.py
│   │   └── __init__.py
│   │
│   ├── services/
│   │   ├── rag_service.py             # shared retriever interface
│   │   ├── anomaly_service.py         # wrapper clients to your anomaly model
│   │   ├── sentiment_service.py       # wrapper clients to your sentiment model
│   │   ├── event_forecast_service.py  # wrapper to your event forecaster model
│   │   ├── member1/
│   │   │   ├── options_flow_service.py
│   │   │   ├── options_prompt.py
│   │   ├── member2/
│   │   │   ├── explain_move_service.py
│   │   │   ├── explain_move_prompt.py
│   │   ├── member3/
│   │   │   ├── macro_gap_service.py
│   │   │   ├── macro_gap_prompt.py
│   │
│   ├── db/
│   │   ├── postgres_handler.py
│   │   ├── redis_cache.py
│   │   ├── migrations/
│   │   │   ├── 001_init.sql
│   │   │   └── 002_add_price_gaps.sql
│   │   ├── queries/
│   │   │   ├── common_queries.py
│   │   │   ├── options_queries.py
│   │   │   ├── move_queries.py
│   │   │   ├── macro_queries.py
│   │   │   └── utils.py
│   │   └── seed/                       # seed_data for assets
│   │       └── seed_assets.sql
│   │
│   ├── data_ingestion/
│   │   ├── market_collector.py
│   │   ├── news_collector.py
│   │   ├── regulatory_collector.py
│   │   ├── infra_collector.py
│   │   ├── options_flow_collector.py
│   │   ├── price_jump_detector.py
│   │   ├── preprocess_pipeline.py     # chunking + summarization
│   │
│   ├── embeddings/
│   │   ├── embedder.py
│   │   ├── vector_store.py            # Chroma / Qdrant adapter
│   │
│   ├── rag_engine/
│   │   ├── retriever.py
│   │   ├── reranker.py
│   │   ├── llama_engine.py
│   │
│   ├── ml_models/                      # **OWNED BY YOU (team lead / ML owner)**
│   │   ├── README.md                   # short ownership + contact info
│   │   ├── anomaly_detector/           # Model A (Anomaly Detector)
│   │   │   ├── training/               # training code + config (only you modify)
│   │   │   │   ├── train.py
│   │   │   │   ├── config.yaml
│   │   │   │   ├── dataset_builder.py
│   │   │   │   └── experiments/        # hyperparams / runs
│   │   │   ├── serving/                # prediction wrapper + API adapter
│   │   │   │   ├── serve.py            # lightweight flask/fastapi model server (containerized)
│   │   │   │   └── predict.py
│   │   │   ├── notebooks/              # EDA, model analysis
│   │   │   ├── models/                 # serialized model artifacts (gitignored)
│   │   │   └── eval_reports/           # metrics + test-suite
│   │   │
│   │   ├── event_forecaster/           # Model B (Event / Volatility Forecaster)
│   │   │   ├── training/
│   │   │   │   ├── train.py
│   │   │   │   ├── config.yaml
│   │   │   │   └── experiments/
│   │   │   ├── serving/
│   │   │   │   ├── serve.py
│   │   │   │   └── predict.py
│   │   │   ├── notebooks/
│   │   │   ├── models/
│   │   │   └── eval_reports/
│   │   │
│   │   ├── common/                      # shared ML utilities
│   │   │   ├── feature_store_interface.py
│   │   │   ├── metrics.py
│   │   │   └── preprocessing.py
│   │   │
│   │   ├── model_registry/             # minimal on-repo registry (plus external recommended)
│   │   │   ├── registry.json           # maps version -> artifact (gitignored models)
│   │   │   └── deploy_notes.md
│   │   │
│   │   └── infra/                      # CI for training + monitoring config
│   │       ├── training_ci.yml
│   │       └── monitoring_config.yml   # alerts for model drift / perf drops
│   │
│   ├── alerting/
│   │   ├── alert_engine.py
│   │   ├── notifier.py
│   │
│   ├── storage/
│   │   ├── vector_db/                  # runtime pointers (not full data)
│   │   └── s3_adapter.py               # for large artifact storage (optional)
│   │
│   ├── scheduler/
│   │   ├── cron_tasks.py
│   │
│   └── utils/
│       ├── time_utils.py
│       ├── ticker_map.py
│       └── logging_utils.py
│
├── models/                             # local Llama / FinBERT weights (gitignored)
│
├── vector_db/                          # Chroma/Qdrant persisted store (gitignored)
│
├── frontend/
│   ├── src/
│   │   ├── pages/ChatBot.jsx
│   │   ├── components/AlertFeed.jsx
│   │   ├── components/EvidenceCard.jsx
│   │   ├── api/
│   │   │   ├── index.js                # axios wrappers; calls backend endpoints listed below
│   │
│   ├── public/
│   └── package.json
│
├── docs/
│   ├── architecture.md
│   ├── data_pipeline.md
│   ├── api_reference.md
│   ├── risk_rules.md
│   ├── member1_options_flow.md
│   ├── member2_explain_move.md
│   ├── member3_macro_gap.md
│   ├── ml_owner_guide.md                # **HOW YOU (ML owner) operate + endpoints**
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── Dockerfile.ml_anomaly            # container for anomaly model serving
│   ├── Dockerfile.ml_forecaster         # container for event forecaster serving
│   ├── docker-compose.yml
│
├── .env.example
├── requirements.txt
├── README.md
├── CONTRIBUTING.md
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   └── cd.yml
│   └── PULL_REQUEST_TEMPLATE.md
└── LICENSE




 2. DATA SOURCES & HOW THEY LINK (ALL 3 MEMBERS COVERED)
1. Market Prices, Liquidity, Volume
Sources
yfinance


OHLCV for equities, crypto, indices


Spreads, liquidity metrics


Historical backfill


Tiingo API


High-accuracy equities & ETF pricing


Fundamentals + attached news tagging


Used by
Core anomaly detector (volume/liquidity spikes)


Member-2 sudden move explainer


Member-3 gap statistics


Pipeline
market_collector.py
   → normalize
   → store in Postgres (market_prices)
   → summary chunks
   → embed
   → Chroma (vector_db)


2. News & Sentiment
Sources
Finnhub WebSocket


Real-time headlines


Trade halts


Earnings alerts


Perplexity Finance Search


Summarized market + macro news


Panic / rumor detection


Regulatory coverage


Used by
Core sentiment classifier


Member-1 options flow explanation


Member-2 sudden move explainer


Member-3 macro gap forecaster


Pipeline
WebSocket stream / Perplexity fetch
   → news_collector.py
   → sentiment_model (FinBERT/DistilBERT)
   → Postgres (news_headlines, news_sentiment)
   → embed → vector DB → RAG


3. Regulatory & Macro Risk
Sources
U.S. SEC Filings API


RBI Press Releases


Federal Reserve RSS Feeds


(Optional) Monetary policy calendars


Used by
Alerts for regulatory shocks


Member-2 sudden moves


Member-3 macro gap forecaster (primary)


Pipeline
regulatory_collector.py
   → fetch + classify by impacted ticker/asset
   → chunk + embed
   → store in regulatory_events + vector DB


4. Infrastructure / Systemic Risk
Sources
Coinbase Status


Binance Status


Solana Explorer (congestion)


Cloudflare/RSS security outages


Finnhub exchange halts


Used by
Core infra alerting


Member-2 sudden move explainer (outage-based moves)


Pipeline
infra_collector.py
   → detect outage
   → store in infra_incidents
   → alert_engine → alerts table


5. Options Flow (Member-1 Only)
Sources
Polygon.io / Tradier / OPRA feed
 (whichever your team selects)


Data Collected
Call/put volume


Open interest change


IV spikes


Whale block trades


Used by
Member-1 Options Flow Interpreter


Anomaly detector tags (“call_skew / iv_spike”)


Pipeline
options_flow_collector.py
   → normalize + detect spikes
   → store anomalies (metric = call_skew/iv_spike)
   → embed key summaries → vector DB


6. Price Jump / Sudden Move Detection (Member-2 Only)
Inputs
Minute-level price changes from market_prices


News sentiment swing near timestamp


Infra outages from infra_incidents


Pipeline
price_jump_detector.py
   → threshold check (|Δprice| > X%)
   → anomalies table (metric = price_jump)
   → retrieve sentiment + outage evidence


7. Macro Gap Forecasting (Member-3 Only)
Inputs
regulatory_events


macro-tagged news sentiment


historical price gaps (price_gaps table)


futures reaction (optional, if stored)


Pipeline
gap_detector.py
   → daily gap calculation (prev_close → next_open)
   → store in price_gaps
   → macro_gap_service queries history + macro evidence


How All Data Links Together
Source Type
Collector File
Stored In
Used By
Sent to Vector DB
yfinance, Tiingo
market_collector.py
market_prices
Core, Member-2, Member-3
✅
Finnhub / Perplexity
news_collector.py
news_headlines, news_sentiment
Core, Member-1, Member-2, Member-3
✅
SEC / RBI / FED
regulatory_collector.py
regulatory_events
Core, Member-2, Member-3
✅
Status Outages
infra_collector.py
infra_incidents
Core, Member-2
✅
Options Flow Feed
options_flow_collector.py
anomalies
Member-1
✅
Price Jump
price_jump_detector.py
anomalies
Member-2
optional


Unified Data Flow Summary
Ingestion (all sources)
 → normalize + preprocess
 → Postgres (raw + structured tables)
 → summarize/chunk
 → generate embeddings
 → Chroma vector DB
 → RAG retrieval for chat + member endpoints


 3. ML PIPELINE INTEGRATION
 Anomaly Detector
Takes yfinance/Tiingo price + volume series


Computes rolling z-score / ML anomaly score


Stores anomalies table


DB Table: anomalies
 | id | ticker | metric | severity | timestamp | explanation |

 Sentiment Classifier
Every headline from Finnhub/Perplexity → sentiment score


Store in news_sentiment table


DB Table: news_sentiment
 | id | ticker | headline | sentiment_score | source | timestamp |

 Event Impact Forecaster
Looks at sentiment + volume + price jumps


Predicts short-term volatility window


DB Table: forecasts
 | ticker | prediction | horizon | confidence |


5. REST API — EXACT ENDPOINTS 
All core system + all 3 member modules

CORE SYSTEM ENDPOINTS
1) POST /chat
Chat with RAG + LLM, retrieve evidence.
Request
{
  "user_message": "Why did BTC fall?",
  "user_id": "user_12"
}

Response
{
  "reply": "BTC dropped because Binance halted withdrawals.",
  "retrieved_evidence": [
    { "source": "finnhub", "snippet": "...", "timestamp": "..." }
  ],
  "confidence": 0.83
}


2) GET /risk-alerts
Returns real-time system alerts.
Response
[
  {
    "ticker": "ETH",
    "risk_type": "liquidity",
    "severity": "high",
    "explanation": "Exchange outage",
    "timestamp": "2025-11-05T10:32:00Z"
  }
]


3) GET /sentiment?ticker=ETH
Latest sentiment + explanations.
Response
{
  "ticker": "ETH",
  "average_score": -0.41,
  "summary": "Sentiment is negative due to FUD and exchange delays.",
  "latest_headlines": [
    "FUD about withdrawals",
    "Bearish social media chatter"
  ]
}


4) GET /anomalies?ticker=BTC
ML-detected anomalies.
Response
[
  {
    "metric": "liquidity",
    "severity": "high",
    "anomaly_score": 0.92,
    "explanation": "4x volume spike + widening spread",
    "timestamp": "2025-11-05T14:22:00Z"
  }
]


5) GET /evidence?ticker=AAPL
Raw RAG evidence chunks.
Response
[
  {
    "text": "SEC starts inquiry on disclosure practices",
    "source": "sec",
    "timestamp": "2025-11-04T09:00:00Z"
  }
]


6) GET /assets
List of tracked assets.
Response
[
  "BTC", "ETH", "AAPL", "TSLA", "NIFTY", "NASDAQ"
]


MEMBER MODULE ENDPOINTS
All 3 mini-projects included.

MEMBER-1 — OPTIONS FLOW INTERPRETER
POST /member1/options-flow
Explains unusual options activity.
Request
{
  "ticker": "TSLA",
  "user_question": "Are big traders buying calls?"
}

Response
{
  "ticker": "TSLA",
  "insight": "Unusual call volume suggests bullish whale positioning.",
  "reasons": [
    "3.2x call volume vs 30-day avg",
    "IV rising",
    "Strong bullish sentiment"
  ],
  "confidence": 0.84,
  "evidence": [
    { "source": "finnhub", "snippet": "...", "timestamp": "..." }
  ]
}

Error cases
400 missing ticker or question


404 no options evidence available



MEMBER-2 — SUDDEN MARKET MOVE EXPLAINER
POST /member2/explain-move
Explains why a ticker suddenly moved.
Request
{
  "ticker": "BTC",
  "timestamp": "2025-11-05T14:30:00Z"
}

Response
{
  "ticker": "BTC",
  "summary": "BTC dropped 4.8% after a Binance outage and negative sentiment.",
  "primary_causes": [
    "exchange outage",
    "liquidity shrink",
    "whale selling"
  ],
  "confidence": 0.78,
  "evidence_used": [
    { "source": "finnhub", "snippet": "withdrawals halted", "timestamp": "..." },
    { "source": "news_sentiment", "score": -0.62 }
  ]
}

Error cases
400 invalid or missing timestamp


404 no movement detected



MEMBER-3 — MACRO-DRIVEN GAP FORECASTER
POST /member3/macro-gap
Predicts likely gap direction after macro/regulatory events.
Request
{
  "asset": "NASDAQ",
  "question": "What happens after the FOMC announcement?"
}

Response
{
  "asset": "NASDAQ",
  "expected_gap": "slight gap up",
  "drivers": [
    "dovish FOMC tone",
    "falling yields",
    "strong futures"
  ],
  "confidence": 0.71,
  "evidence_used": [
    { "source": "fed", "snippet": "cut pace of tightening", "timestamp": "..." },
    { "source": "sentiment", "score": 0.63 }
  ]
}

Error cases
400 asset not tracked


404 no macro evidence found


 6. SCHEDULER / CRON TIMELINE
Task
Frequency
yfinance historical + latest prices
Every 5 min
Tiingo fundamentals/news
Hourly
Finnhub websocket
Real-time listener
SEC/RBI/FED scrapers
Every 12 hours
Anomaly detector
Every 10 min
Sentiment classifier
Real-time
Alert engine
Every 1–5 min

All scheduled in scheduler/cron_tasks.py

 7. FRONTEND FLOW (React)
ChatBot.jsx
User message → POST /chat


Display reply + evidence tags (“show source”)


AlertFeed.jsx
GET /risk-alerts


Sort by severity


Red for critical → Yellow for medium → Blue info


EvidenceCard.jsx
Touchable cards → news snippets, sentiment, timestamps



 8. HOW DATA MOVES (PIPELINE SUMMARY)
 Ingestion
yfinance / Tiingo / Finnhub / Perplexity / SEC data
 → normalized & preprocessed
 → stored raw in Postgres
 → summarized into chunks
 → embeddings generated
 → saved to Chroma
 ML Stage
Market data → anomaly detector → alerts table
 News → sentiment classifier → sentiment table
 Combined → volatility forecasts
 RAG Stage
User query → retriever → top-k chunks & ML signals
 → local Llama → structured explanation
 Output
Human-readable insight


Evidence list


Alert trigger if risk high

✅ 1. MASTER DATABASE DESIGN (POSTGRES)
DB Name: urisk_core
Owner: only you (team lead)
 Tables that ALL modules will use
Table
Purpose
assets
master list of tracked tickers & asset metadata
market_prices
price, volume, spreads with minute granularity
news_headlines
raw news feed from Finnhub/Perplexity/Tiingo
news_sentiment
sentiment score per headline
regulatory_events
SEC/RBI/FED releases
infra_incidents
exchange outages / blockchain problems
anomalies
ML anomalies from price/volume/liquidity
forecasts
volatility predictions
alerts
merged alerts triggered by ML + RAG
price_gaps
gap up/gap down history (needed for macro forecaster)


 COMPLETE SCHEMA (PRODUCTION-LEVEL)
-- MASTER ASSETS TABLE
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) UNIQUE NOT NULL,
    name TEXT,
    asset_type VARCHAR(25),      -- stock / crypto / index / fx
    exchange VARCHAR(50),
    sector VARCHAR(50),
    country VARCHAR(50),
    added_at TIMESTAMP DEFAULT NOW()
);


-- MARKET PRICES (1m – 5m interval supported)
CREATE TABLE market_prices (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) REFERENCES assets(ticker),
    timestamp TIMESTAMP NOT NULL,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    bid_ask_spread FLOAT,
    source VARCHAR(20),
    UNIQUE (ticker, timestamp)
);


-- NEWS HEADLINES
CREATE TABLE news_headlines (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20),
    headline TEXT,
    url TEXT,
    source VARCHAR(30),
    published_at TIMESTAMP,
    inserted_at TIMESTAMP DEFAULT NOW()
);


-- SENTIMENT RESULTS
CREATE TABLE news_sentiment (
    id SERIAL PRIMARY KEY,
    headline_id INT REFERENCES news_headlines(id),
    sentiment_score FLOAT,              -- -1 to +1
    sentiment_label VARCHAR(10),
    confidence FLOAT,
    model_version VARCHAR(20),
    timestamp TIMESTAMP DEFAULT NOW()
);


-- REGULATORY / MACRO EVENTS
CREATE TABLE regulatory_events (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20),
    title TEXT,
    body TEXT,
    source VARCHAR(30),                 -- sec, rbi, fed
    severity VARCHAR(10),
    event_type VARCHAR(30),             -- rate, inflation, enforcement, etc
    published_at TIMESTAMP,
    inserted_at TIMESTAMP DEFAULT NOW()
);


-- INFRA OUTAGES
CREATE TABLE infra_incidents (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50),
    incident_type VARCHAR(50),
    description TEXT,
    severity VARCHAR(10),
    started_at TIMESTAMP,
    resolved_at TIMESTAMP,
    source VARCHAR(30)
);


-- ML ANOMALIES
CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20),
    metric VARCHAR(50),                  -- volume / liquidity / volatility
    anomaly_score FLOAT,
    severity VARCHAR(10),
    explanation TEXT,
    timestamp TIMESTAMP
);


-- FORECASTS (VOLATILITY, MACRO EFFECTS)
CREATE TABLE forecasts (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20),
    forecast_window VARCHAR(20),
    predicted_impact VARCHAR(30),
    confidence FLOAT,
    reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);


-- MERGED ALERTS
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20),
    risk_type VARCHAR(30),              -- sentiment, infra, regulatory
    severity VARCHAR(10),
    message TEXT,
    triggered_at TIMESTAMP DEFAULT NOW(),
    read BOOLEAN DEFAULT FALSE
);


-- PRICE GAPS (IMPORTANT FOR MEMBER-3)
CREATE TABLE price_gaps (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) REFERENCES assets(ticker),
    date DATE,
    previous_close FLOAT,
    next_open FLOAT,
    gap_percent FLOAT,
    direction VARCHAR(10),              -- up/down/flat
    reason TEXT,
    inserted_at TIMESTAMP DEFAULT NOW()
);

 This single schema covers ALL 3 features
  Member-1, Member-2, Member-3 never need new tables
  Everything used by API, RAG, LLM, dashboards

2. CHROMADB STRUCTURE (VECTOR DB)
Collection Name: urisk_chunks
Fields stored per record
field
purpose
text_chunk
cleaned summary/news paragraph
embedding
768-dim (SentenceTransformer or Llama)
ticker
BTC, TSLA, NIFTY, etc
risk_type
sentiment, regulatory, infra, options
source
finnhub, sec, perplexity, etc
timestamp
recency filter
sentiment_score
optional
anomaly_flag
boolean
severity
low/med/high
chunk_id
unique string ID

 You keep ~200–1000 chunks per day
  Retriever filters by ticker + time + risk_type


✅ 4. DATA COLLECTION PIPELINES
✅ COMMON FOR ALL TEAMS (10 sources)
Source
What you collect
Table filled


yfinance API | OHLC, spreads, volume | market_prices |


Tiingo API | high-accuracy equities & news | market_prices + news_headlines |


Finnhub Websocket | real-time headlines, trade halts | news_headlines |


Perplexity Finance | summarized headlines | news_headlines |


SEC API | US regulatory filings | regulatory_events |


RBI Press Releases | Indian regulation | regulatory_events |


Federal Reserve RSS | macro + rate decisions | regulatory_events |


Coinbase Status | crypto outages | infra_incidents |


Binance Status | halts, downtime | infra_incidents |


Solana Explorer | congestion | infra_incidents |


 All this is shared across teams.

5. MEMBER-WISE ADDITIONAL DATA
MEMBER-1 (Options Flow Interpreter)
Needs special data:
 1️⃣ Options flow feed
provider: Tradier / Opra / polygon.io


collect:


call volume


put volume


open interest change


IV spikes


whale block orders


2️⃣ Custom anomaly tagging
metric: "call_skew", "put_skew", "iv_spike"


stored in anomalies table


3️⃣ Vector chunks tagged as:
risk_type = "options"

✅ No new DB tables — only new ingestion pipeline + metadata tags

MEMBER-2 (Sudden Move Explainer)
Additional data required:
1️⃣ Price Jump Detector
You store price change vs previous minute


If abs(Δ) > threshold → insert into anomalies


2️⃣ Sentiment window
compute average sentiment around timestamp


store in news_sentiment


3️⃣ Infra spikes
if exchange goes DOWN → insert infra_incidents


 Already covered by your schema

 MEMBER-3 (Macro Gap Forecaster)
Uses these inputs:
1️⃣ regulatory_events (already stored)
 2️⃣ price_gaps table (you add daily)
 3️⃣ macro sentiment
average sentiment from headlines tagged “macro”, “fed”, “inflation”, “rb


 6. DAILY INGESTION SCHEDULER
Task
Frequency
Tables updated
yfinance prices
1–5 min
market_prices
Tiingo
hourly
market_prices + news_headlines
Finnhub Websocket
realtime
news_headlines
Perplexity
5–10 min
news_headlines
SEC/RBI/FED scrapers
6–12 hours
regulatory_events
Anomaly Detector
10 min
anomalies
Sentiment Classifier
realtime
news_sentiment
Infra monitoring
1–5 min
infra_incidents
Gap detector
daily (market open)
price_gaps





 COMPLETE OPENAPI / SWAGGER SPEC
Format below is fully usable for Swagger UI.

 API Metadata
openapi: 3.0.0
info:
  title: uRISK - Unified Risk Intelligence API
  version: 1.0.0
  description: Local RAG + ML risk monitoring assistant
servers:
  - url: http://localhost:8000


 POST /chat
paths:
  /chat:
    post:
      summary: Chat with LLM using RAG
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      responses:
        200:
          description: LLM response with retrieved evidence
          content:
            application/json:
              schema:
                type: object
                properties:
                  reply:
                    type: string
                  confidence:
                    type: number
                  evidence:
                    type: array
                    items:
                      type: object
                      properties:
                        source:
                          type: string
                        snippet:
                          type: string
                        timestamp:
                          type: string


 GET /risk-alerts
 /risk-alerts:
    get:
      summary: Get current risk alerts
      responses:
        200:
          description: List of alerts
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    ticker:
                      type: string
                    risk_type:
                      type: string
                    severity:
                      type: string
                    message:
                      type: string
                    triggered_at:
                      type: string


 GET /sentiment?ticker=BTC
 /sentiment:
    get:
      summary: Sentiment summary for an asset
      parameters:
        - in: query
          name: ticker
          schema:
            type: string
      responses:
        200:
          description: Sentiment data
          content:
            application/json:
              schema:
                type: object
                properties:
                  ticker:
                    type: string
                  avg_sentiment:
                    type: number
                  latest_headlines:
                    type: array
                    items:
                      type: string


 GET /anomalies?ticker=ETH
 /anomalies:
    get:
      summary: ML anomaly detection results
      parameters:
        - in: query
          name: ticker
          schema: { type: string }
      responses:
        200:
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    metric:
                      type: string
                    severity:
                      type: string
                    anomaly_score:
                      type: number
                    explanation:
                      type: string
                    timestamp:
                      type: string


 GET /evidence?ticker=AAPL
 /evidence:
    get:
      summary: Retrieve raw RAG evidence chunks
      parameters:
        - in: query
          name: ticker
          schema: { type: string }
      responses:
        200:
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    text:
                      type: string
                    source:
                      type: string
                    timestamp:
                      type: string


 GET /assets
 /assets:
    get:
      summary: List all tracked tickers/assets
      responses:
        200:
          content:
            application/json:
              schema:
                type: array
                items:
                  type: string


RESULT
You now have:
✔ Professional Postgres schemas
 ✔ Vector DB metadata model
 ✔ Full OpenAPI swagger-compliant specification
 ✔ Fully aligned with yfinance, Tiingo, Finnhub, Perplexity, SEC, RBI, FED
This is enough for:
  Backend dev to build DB + API
  ML team to log outputs
  Frontend to integrate cleanly



What You Deliver to Team Members
Shared resources they don’t need to build:
✔ Postgres DB
 ✔ Vector DB (Chroma/Qdrant)
 ✔ Ingestion pipelines (yfinance, SEC, Tiingo, Finnhub…)
 ✔ Embeddings stored in DB
 ✔ REST APIs that give them raw data
You expose these existing API endpoints to them:
GET    /assets
GET    /evidence?ticker=XYZ
GET    /sentiment?ticker=XYZ
GET    /anomalies?ticker=XYZ
GET    /risk-alerts
POST   /chat      (optional)

 Query → Retrieve → LLM → Explanation



 


3 Mini-Projects (One per Member)

MEMBER-1 — OPTIONS FLOW INTERPRETER
Goal
Convert raw options flow + related anomalies into human-readable insights with evidence and confidence scores.
What this feature must do:
✔ Accept a ticker + user question
 ✔ Fetch relevant anomalies, volume spikes, sentiment, or evidence from DB & vector DB
 ✔ If available, apply RAG retrieval of specific “options flow” chunks
 ✔ Use LLM to summarize in plain English
 ✔ Return JSON with insight + reasons + confidence

FILE-BY-FILE EXPLANATION
 backend/routes/member1/options_flow_routes.py
Defines a new REST API endpoint


Example:

 POST /member1/options-flow
{
  "ticker": "AAPL",
  "user_question": "Are big traders buying calls?"
}


Calls the service layer to fetch DB data + RAG evidence + LLM summary


Returns JSON: {ticker, insight, reasons[], confidence}


Responsibilities
Task
Done Here?
Validate incoming JSON
✅
Call service function
✅
Format success/error response
✅


 backend/services/member1/options_flow_service.py
This is the core business logic.
What it does:
Validate ticker


Call PostgreSQL:


anomalies table → volume spike, call/put imbalance


market_prices table → high volume


Call vector DB:


retrieve chunks containing “options”, “call volume”, “IV spike”


Build prompt → send to llama_engine


Return JSON with:


insight


reasons


confidence score



 backend/services/member1/options_prompt.py
Contains the reusable LLM prompt:
SYSTEM:
You are a financial options-flow analyst.
Explain unusual call/put volume, whale orders, IV spikes, and open interest changes in simple language.

USER PROMPT TEMPLATE:
Ticker: {ticker}
User question: {user_question}

Data Observed:
- Volume: {volume_info}
- Anomalies: {anomaly_info}
- Evidence: {rag_snippets}

Write:
1. Short explanation (2–4 sentences)
2. Reasons list
3. Confidence score between 0 and 1


 backend/db/queries/options_queries.py
SQL queries to fetch:
latest anomaly rows related to volume, liquidity, call/put spikes


timestamps


severity


explanation text


Example output (Python dict):
{
  "metric": "volume",
  "severity": "high",
  "anomaly_score": 0.91,
  "explanation": "3.8x call volume vs 30-day average",
  "timestamp": "2025-11-05T14:32:00"
}


 backend/rag_engine/retriever.py
Search vector DB for:
news chunks where “options”, “OI”, “calls”, “puts” appear


boost recent/high severity chunks


Returns:
 list of {source, text, timestamp}

 backend/rag_engine/llama_engine.py
Takes the prepared prompt and runs it through local Llama.
 Returns: structured JSON

 NEW API ENDPOINT — FULL SPEC
POST /member1/options-flow
Request
{
  "ticker": "TSLA",
  "user_question": "Is smart money buying calls?"
}

Response
{
  "ticker": "TSLA",
  "insight": "TSLA saw unusually high call volume...",
  "reasons": [
    "3.2x call volume vs 30-day avg",
    "IV rising",
    "Ongoing bullish news sentiment"
  ],
  "confidence": 0.84,
  "evidence": [
    { "source":"finnhub", "snippet":"...", "timestamp":"..." }
  ]
}


 END-TO-END FLOW 
Frontend → /member1/options-flow → options_flow_service
 → queries Postgres (anomalies + market_prices)
 → RAG retriever (vector DB chunks)
 → Build LLM prompt
 → llama_engine inference
 → Format final JSON
 → return to frontend


 WHAT DEVELOPER MUST IMPLEMENT
Component
Responsibility
New Route
Input validation + integration
Service
Core logic, calling DB + RAG + LLM
Prompt
High-quality template to produce clean finance explanations
Queries
SQL to pull anomaly + volume data
Docs
A markdown doc explaining input/output


 DOCUMENT FILE FOR TEAM (/docs/member1_options_flow.md)
This markdown explains:
API contract


Dependencies (DB + vector DB)


Example payloads


Error formats


Testing steps (Postman / curl)


MEMBER-2 — SUDDEN MARKET MOVE EXPLAINER
Mission
Explain why a ticker suddenly moved up or down by pulling evidence (news, sentiment, outages, anomalies) around a given timestamp and generating a concise LLM summary.
Input:
POST /member2/explain-move
{
  "ticker": "BTC",
  "timestamp": "2025-11-05T14:30:00"
}

Output:
Brief explanation of what caused the price move


Evidence + timestamps


Confidence score


JSON structured format




 EXPLANATION OF EACH FILE
 routes/member2/explain_move_routes.py
Defines the REST endpoint


Example:

 POST /member2/explain-move


Validates:


ticker exists in assets table


timestamp format is valid


Calls: explain_move_service.run(ticker, timestamp)


Returns JSON with explanation + evidence + confidence


Core Responsibilities
Part
Done Here?
JSON validation
✅
Error handling
✅


services/member2/explain_move_service.py
This is the engine for the feature.
What it does:
Convert timestamp to ±30 minute window


Query Postgres for:


price jumps (market_prices)


anomalies (volume/liquidity spikes)


negative sentiment (news_sentiment)


infra outages (infra_incidents)


Query vector DB:


Retrieve news chunks around timestamp window


Build combined summary:


sentiment text


anomaly explanations


outage info


price % change


Send structured context into LLM


Return structured JSON



services/member2/explain_move_prompt.py
Prompt template used by the LLM:
SYSTEM:
You are a financial market move explainer.
Use evidence to explain sudden price jumps or drops in simple English.
Do not give trade advice. Only explain reasons and uncertainty.

INPUT:
Ticker: {ticker}
Time Window: {start_time} → {end_time}

Observed Data:
- Price Movement: {price_change_percent}%
- Anomalies: {anomaly_info}
- Sentiment: {sentiment_info}
- Incidents: {incident_info}
- RAG Evidence: {rag_snippets}

OUTPUT FORMAT (STRICT JSON):
{
  "ticker": "...",
  "summary": "...",
  "primary_causes": [...],
  "confidence": 0.00,
  "evidence_used": [...]
}


 db/queries/move_queries.py
Contains SQL queries like:
price before and after timestamp → compute % move


anomalies for ticker in ±30 min


sentiment around timestamp


infra incidents (exchange outages, blockchain halts)


Example result from database:
{
  "price_move": -4.7,
  "anomaly": "liquidity drop",
  "severity": "high",
  "sentiment_score": -0.64,
  "incident": "Binance outage"
}


rag_engine/retriever.py
Filters vector DB chunks by:
ticker


timestamp window


risk_type: sentiment, regulatory, infra


Returns evidence list:
[
  {"source": "finnhub", "snippet": "Binance faced withdrawal issues", "timestamp": "..."},
  {"source": "perplexity", "snippet": "FUD spreading on Twitter about outage", "timestamp": "..."}
]


utils/time_utils.py
Convert supplied timestamp into:


start_time = timestamp - 20 minutes


end_time = timestamp + 20 minutes


Used by DB queries and vector DB calls



NEW ENDPOINT — OPENAPI STYLE
POST /member2/explain-move
Request
{
  "ticker": "BTC",
  "timestamp": "2025-11-05T14:30:00"
}

Success Response
{
  "ticker": "BTC",
  "summary": "BTC dropped 4.8% after Binance outage & negative sentiment spike.",
  "primary_causes": [
    "exchange outage",
    "whale selling",
    "liquidity shrink"
  ],
  "confidence": 0.78,
  "evidence_used": [
    { "source": "finnhub", "snippet": "Binance paused withdrawals", "timestamp": "..." },
    { "source": "news_sentiment", "score": -0.62 }
  ]
}

Error Examples
400 Bad Request - Unknown ticker
400 Bad Request - Invalid timestamp format
404 Not Enough Data - No movement detected


END-TO-END SYSTEM FLOW 
Frontend → POST /member2/explain-move
          ↓
validate ticker + timestamp
          ↓
explain_move_service
          ↓
Postgres: price, anomalies, sentiment, incidents
          ↓
Vector DB: retrieve timestamp-focused chunks
          ↓
Build prompt → llama_engine
          ↓
Return JSON (summary, causes, evidence, confidence)
          ↓
Frontend renders: timeline chart + explanation



MEMBER-3 — MACRO-DRIVEN GAP FORECASTER
Mission
Use regulatory/macro evidence (FOMC statements, RBI releases, Fed decisions, SEC filings, economic news, etc.) to predict whether an asset will likely gap up, gap down, or stay neutral in the next trading session.
Input:
POST /member3/macro-gap
{
  "asset": "NASDAQ",
  "question": "What happens after the FOMC announcement?"
}

Output:
Expected gap direction (up / down / flat)


Drivers (macro reasons)


Confidence score


Evidence list


FILE-BY-FILE EXPLANATION
routes/member3/macro_gap_routes.py
Defines the new endpoint:
POST /member3/macro-gap
Validates:
asset exists (stocks / crypto / indices / FX)


question is provided


Calls service layer → returns structured JSON.

services/member3/macro_gap_service.py
This file contains the brain of the macro forecaster:
Steps:
Validate asset name


Query Postgres:
  regulatory_events
  macro news sentiment
  historical gap behavior after similar events


Query vector DB for macro-related chunks:


“FOMC”, “RBI”, “SEC”, “rate cuts”, “inflation prints”


Combine:


sentiment trend


macro event severity


futures reaction (if stored)


volatility forecasts


Feed structured evidence into prompt → llama_engine


Return JSON result



 services/member3/macro_gap_prompt.py
Prompt structure:
SYSTEM:
You are a macro and regulatory event analyst.
Predict if the next trading session opens with a gap up,
gap down, or flat movement, based on macro evidence.
Be concise and avoid financial advice.

INPUT:
Asset: {asset}
User question: {question}

Recent Macro Evidence:
{macro_events}

Sentiment:
{sentiment_info}

Historical Behavior:
{historical_stats}

RAG Evidence:
{rag_snippets}

OUTPUT FORMAT (STRICT JSON):
{
  "asset": "...",
  "expected_gap": "slight gap up" | "gap down" | "neutral",
  "drivers": ["...", "...", "..."],
  "confidence": 0.00,
  "evidence_used": [...]
}


 db/queries/macro_queries.py
Contains SQL queries for:
regulatory_events table → Fed/RBI/SEC statements


news_sentiment → macro sentiment


optional: historical price gaps from market_prices


Example DB output:
{
  "event": "Fed signals rate cuts ahead",
  "severity": "medium",
  "sentiment": "positive",
  "timestamp": "2025-11-05T10:06:00"
}


 rag_engine/retriever.py
Filter chunks where:
risk_type = "regulatory" or "macro"


ticker/asset matches


timestamp recent


Returns news/snippets used in explanation.

NEW ENDPOINT — API SPEC
POST /member3/macro-gap
Input
{
  "asset": "NASDAQ",
  "question": "What happens after the FOMC announcement?"
}

Response
{
  "asset": "NASDAQ",
  "expected_gap": "slight gap up",
  "drivers": [
    "dovish FOMC tone",
    "falling yields",
    "strong futures"
  ],
  "confidence": 0.71,
  "evidence_used": [
    { "source": "fed", "snippet": "cut pace of tightening", "timestamp": "..." },
    { "source": "sentiment", "score": 0.63 }
  ]
}

Error cases
400 - asset not tracked
400 - invalid JSON
404 - no macro evidence available


END-TO-END FLOW 
Frontend
   ↓ POST /member3/macro-gap
   ↓
macro_gap_routes.py
   ↓
macro_gap_service.run(asset, question)
   ↓
Postgres: regulatory_events + sentiment + price history
Vector DB: macro-tagged chunks
   ↓
Build prompt
   ↓
llama_engine.generate()
   ↓
Return JSON → Frontend


 MEMBER-3 MUST DELIVER:
Deliverable
Status
New API route
✅
Service logic (macro_gap_service.py)
✅
Prompt builder
✅
SQL queries (macro_queries.py)
✅
Markdown doc (member3_macro_gap.md)
✅
Postman tests + example payload
✅
Unit tests for invalid asset / no data
✅


TEAM DOCUMENT (/docs/member3_macro_gap.md) MUST CONTAIN
Purpose of the endpoint


Example request and response


Data sources it relies on (SEC/RBI/FED, sentiment, futures, volatility)


Error handling and edge cases


Testing using Postman or curl


Key clarifications & responsibilities (so there’s zero ambiguity)
You (ML owner) exclusively own backend/ml_models/* — training code, notebooks, model artifacts, model_registry, and monitoring. Other members must not change these folders. Put a clear README.md in that folder describing contact + change rules (included above).


Serving / inference:


The ML models expose inference via containers (Dockerfile.ml_anomaly, Dockerfile.ml_forecaster) and internal HTTP endpoints (e.g., POST /predict), or you can expose them via internal RPC.


The backend services/anomaly_service.py, sentiment_service.py, event_forecast_service.py are thin wrappers that call these ML servers (HTTP or gRPC). Members call the service wrappers rather than touching model code.


Database / contracts:


ML training code reads from market_prices, news_headlines, news_sentiment, anomalies (same DB all members share).


Define and freeze input schema for model training and inference in ml_models/common/feature_store_interface.py. This prevents schema drift and clarifies who owns which fields.


Versioning & model registry:


Store model binaries outside Git (S3 / artifact storage). Use ml_models/model_registry/registry.json to map versions to artifact names. Add deploy notes for how to update a model (bump registry, CI triggers deployment).


Monitoring & alerting:


Add model-monitoring config in ml_models/infra/monitoring_config.yml. Monitor data drift, input distribution, and accuracy (if labels are available). Tie alerts to alert_engine.py so ops get notified.


Security & access:


Put model training credentials & large-data access secrets in centralized secrets manager (DO NOT commit). Document these in ml_owner_guide.md.


How members consume ML outputs (very important):


Member services (member1, member2, member3) should query services/*_service.py wrappers. Example: explain_move_service calls anomaly_service.get_anomalies(ticker, window) and event_forecast_service.predict(...).


This enforces separation of concerns and prevents accidental model edits.



Suggested minimal internal API for ML (examples for service wrappers)
GET /internal/ml/anomalies?ticker=BTC&start=...&end=... → returns anomalies list (from model or anomalies table)


POST /internal/ml/forecast body { "ticker":"BTC", "window":"1h" } → returns { prediction, confidence, meta }
 (Implement these in backend/routes/ml_routes.py as internal endpoints protected by API key or internal network.)



Quick Git + team workflow I recommend (so members can start now)
Branches: main (prod), develop (integration), feature/<member>-<task>


PRs: open to develop, require at least 1 reviewer + passing CI.


Files only ML-owner can change: backend/ml_models/**, models/** (add protection rules).


Members should create PRs under backend/routes/memberX and backend/services/memberX only.



Short checklist to push repo and onboard members (priority list — do these first)
Initialize repo with this folder layout (push skeleton).


Add .gitignore, .env.example, README.md (with brief architecture + owner list).


Add backend/ml_models/README.md explaining you own it + how to request changes.


Implement services/*_service.py wrappers for ML endpoints (stubs are fine at first).


Push DB schema + migrations.


Run docker-compose up to smoke-test core services (chat, basic ingestion).


Share repo + CONTRIBUTING.md with team and assign members their folders.

