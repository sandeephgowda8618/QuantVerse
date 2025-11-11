# QuantVerse uRISK - Data Collection & Preprocessing Pipeline

## Overview

This pipeline implements a comprehensive data collection and preprocessing system for the uRISK (Unified Risk Intelligence & Surveillance Kernel) platform. It collects, processes, and embeds financial data from multiple sources to support downstream ML and RAG workflows.

## Architecture

The pipeline consists of several interconnected components:

### 1. Data Collectors
- **Market Collector**: OHLCV data from yFinance and Tiingo
- **News Collector**: Financial news from Finnhub and Perplexity
- **Regulatory Collector**: SEC, RBI, and Fed regulatory events
- **Infrastructure Collector**: Exchange and service status monitoring
- **Options Flow Collector**: Options data with anomaly detection
- **Price Jump Detector**: Sudden price movement detection

### 2. Preprocessing Pipeline
- **Text Chunking**: Splits content into embedding-ready chunks
- **Content Cleaning**: Removes HTML, normalizes text
- **Metadata Extraction**: Preserves context and source information
- **Batch Processing**: Handles multiple content types efficiently

### 3. Embedding & Vector Storage
- **Embedding Generation**: Supports both local (sentence-transformers) and OpenAI models
- **Vector Database**: ChromaDB integration for semantic search
- **Content Organization**: Separate collections by content type

### 4. Scheduling & Orchestration
- **Automated Scheduling**: Configurable intervals for each collector
- **Manual Execution**: On-demand pipeline runs
- **Error Handling**: Robust error recovery and logging

## Quick Start

### 1. Environment Setup

```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Run database migrations
psql -d your_database -f backend/db/migrations/001_init.sql
psql -d your_database -f backend/db/seed/seed_assets.sql
```

### 3. Test the Pipeline

```bash
# Run comprehensive pipeline test
python test_pipeline.py
```

### 4. Start the Scheduler

```bash
# Run automated data collection
python backend/scheduler/data_scheduler.py
```

## Configuration

### Environment Variables (.env)

```bash
# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/urisk
REDIS_URL=redis://localhost:6379

# Required API Keys
FINNHUB_API_KEY=your_finnhub_key
TIINGO_API_KEY=your_tiingo_key
PERPLEXITY_API_KEY=your_perplexity_key
POLYGON_API_KEY=your_polygon_key

# Trading Data APIs (choose one or more)
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
TRADIER_API_KEY=your_tradier_key
TD_AMERITRADE_API_KEY=your_td_key
YAHOO_FINANCE_ENABLED=true

# Optional API Keys
OPENAI_API_KEY=your_openai_key  # For advanced embeddings

# Vector Database
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Logging
LOG_LEVEL=INFO
```

### Collection Schedules

Modify `backend/config/scheduler_config.py` to adjust collection frequencies:

```python
COLLECTION_SCHEDULES = {
    'market_data': {'interval_minutes': 5},
    'news': {'interval_minutes': 10},
    'regulatory': {'interval_minutes': 60},
    'infrastructure': {'interval_minutes': 15},
    'options_flow': {'interval_minutes': 30},
    'price_jumps': {'interval_minutes': 5},
    'preprocessing': {'interval_minutes': 15}
}
```

## Usage Examples

### Manual Data Collection

```python
from backend.scheduler.data_scheduler import run_manual_pipeline

# Run specific components
result = await run_manual_pipeline(['market', 'news', 'preprocessing'])

# Run all components
result = await run_manual_pipeline()
```

### Direct Component Usage

```python
from backend.data_ingestion.market_collector import market_collector
from backend.data_ingestion.preprocess_pipeline import preprocessing_pipeline

# Collect market data
market_result = await market_collector.run_collection_cycle(['AAPL', 'MSFT'])

# Run preprocessing
preprocess_result = await preprocessing_pipeline.run_preprocessing_cycle()
```

### Vector Search

```python
from backend.embeddings.vector_store import chroma_store

# Semantic search
results = chroma_store.search_similar(
    query="Apple earnings report impact on stock price",
    limit=10
)

# Ticker-specific search
ticker_results = chroma_store.search_by_ticker(
    ticker="AAPL",
    hours_back=24
)
```

## Data Flow

```
1. Data Sources (APIs) → Collectors → PostgreSQL
2. PostgreSQL → Preprocessing Pipeline → Text Chunks
3. Text Chunks → Embedding Generation → Vector Embeddings
4. Vector Embeddings → ChromaDB → Semantic Search Ready
```

## Supported Content Types

- **News**: Headlines, articles, sentiment analysis
- **Regulatory**: SEC filings, Fed announcements, RBI press releases  
- **Market**: OHLCV summaries, volume analysis, price changes
- **Infrastructure**: Exchange status, service outages, system alerts
- **Anomalies**: Price jumps, options flow spikes, unusual patterns

## Monitoring & Logging

The pipeline includes comprehensive logging and monitoring:

- **Structured Logging**: JSON-formatted logs with context
- **Error Tracking**: Detailed error collection and reporting
- **Performance Metrics**: Collection times, success rates, data volumes
- **Health Checks**: Component status and availability monitoring

## Integration with uRISK System

This pipeline serves as the foundation for:

- **RAG Retrieval**: Semantic search for relevant financial context
- **ML Feature Engineering**: Preprocessed data for anomaly detection
- **Risk Alerting**: Real-time risk event identification
- **Member Services**: Specialized analysis for options flow, price movements, etc.

## Development & Testing

### Running Tests

```bash
# Full pipeline integration test
python test_pipeline.py

# Individual component tests
python -m pytest backend/tests/
```

### Adding New Data Sources

1. Create a new collector in `backend/data_ingestion/`
2. Add database schema changes to migrations
3. Update the preprocessing pipeline to handle new content type
4. Add scheduling configuration
5. Update tests and documentation

### Customizing Embeddings

```python
# Use different embedding model
from backend.embeddings.embedder import financial_embedder

# Check current model
info = financial_embedder.get_embedding_info()

# The system automatically selects the best available model:
# 1. OpenAI (if API key provided)
# 2. Local sentence-transformers models
```

## Troubleshooting

### Common Issues

1. **API Rate Limits**: Collectors include rate limiting and backoff strategies
2. **Database Connections**: Check DATABASE_URL and connection pooling
3. **Embedding Failures**: Verify model availability and memory requirements
4. **Vector Store Issues**: Ensure ChromaDB persistence directory is writable

### Performance Optimization

- **Batch Processing**: All collectors use efficient batch operations
- **Parallel Collection**: Multiple tickers processed concurrently  
- **Chunking Strategy**: Optimized chunk sizes for embedding models
- **Database Indexing**: Proper indexes on timestamp and ticker columns

## API Reference

See the main README.md for complete API documentation and integration details with the broader uRISK system.

## Contributing

Follow the patterns established in existing collectors when adding new data sources. Ensure proper error handling, logging, and test coverage for all new components.
