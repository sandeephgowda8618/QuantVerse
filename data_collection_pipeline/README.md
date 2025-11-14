# QuantVerse Data Collection Pipeline

A comprehensive multi-provider financial data ingestion system that efficiently collects market data, news, regulatory events, and technical indicators while respecting API rate limits and maintaining data quality.

## 🎯 Overview

This pipeline implements a robust data collection system with the following features:

- **Multi-Provider Support**: Integrates 10+ financial data providers
- **Rate Limit Compliance**: Maximum 10 API calls per provider per cycle
- **Bulk Data Processing**: Optimizes API usage with batch requests
- **Idempotent Operations**: Prevents duplicate data with upsert patterns
- **Session Tracking**: Full audit trail of all ingestion activities
- **Graceful Error Handling**: Retry logic with exponential backoff
- **Parallel Execution**: Concurrent collection from multiple providers
- **Flexible Scheduling**: Configurable intervals for different data types

## 📊 Data Sources & Coverage

### Market Data Providers
- **Yahoo Finance** (yfinance): Free OHLCV data with bulk endpoints
- **Tiingo**: High-quality financial data with date ranges
- **Polygon.io**: Comprehensive market data and aggregates
- **Alpaca**: Trading platform data with real-time feeds

### News & Sentiment Providers
- **Finnhub**: Real-time company news and historical articles
- **Perplexity AI**: AI-powered market news summaries
- **Google News RSS**: Broad news coverage with keyword filtering
- **Reddit**: Community sentiment from finance subreddits

### Technical & Economic Data
- **Alpha Vantage**: Technical indicators with key rotation (80+ API keys)
- **Federal Reserve**: Economic indicators and policy announcements
- **SEC EDGAR**: Regulatory filings and corporate events

### Infrastructure Monitoring
- **Coinbase/Binance**: Cryptocurrency exchange status
- **AWS/GitHub**: Cloud infrastructure health
- **NASDAQ**: Trading halts and market status

## 🏗️ Architecture

```
data_collection_pipeline/
├── __init__.py                 # Package initialization
├── config.py                   # Configuration and environment setup
├── utils.py                    # Shared utilities and database operations
├── market_collectors.py        # Market data collectors (OHLCV)
├── news_collectors.py          # News and sentiment collectors
├── regulatory_collectors.py    # Regulatory and infrastructure collectors
├── technical_collectors.py     # Technical indicators and economic data
├── orchestrator.py            # Main pipeline coordination
├── main.py                    # CLI interface
├── test_pipeline.py           # Test suite for pipeline verification
├── demo_error_handling.py     # Demo showcasing error handling capabilities
├── requirements.txt           # Python dependencies
├── logs/                      # Timestamped log files for all runs
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /Users/sandeeph/Documents/QuantVerse/urisk/data_collection_pipeline
pip install -r requirements.txt
```

### 2. Configure Environment

The pipeline uses the parent directory's `.env` file with all necessary API keys and database configuration already set up.

### 3. Run Single Collection Cycle

```bash
python main.py --single-cycle
```

### 4. Run Scheduled Pipeline

```bash
python main.py --scheduled
```

## 📋 Usage Examples

### Single Collection Cycle
```bash
# Full collection cycle for all priority tickers
python main.py --single-cycle

# Specific tickers only
python main.py --single-cycle --tickers AAPL MSFT GOOGL

# Market data only
python main.py --market-only --tickers TSLA NVDA

# News collection only
python main.py --news-only
```

### Scheduled Operations
```bash
# Continuous scheduled collection
python main.py --scheduled

# With custom log level
python main.py --scheduled --log-level DEBUG
```

### Dry Run Mode
```bash
# Preview what would be collected
python main.py --single-cycle --dry-run
```

## 📈 API Call Budget Management

Each provider is limited to **10 API calls per ingestion cycle**:

| Provider | Budget | Strategy |
|----------|--------|----------|
| Yahoo Finance | 10 calls | 50 tickers per call (bulk download) |
| Tiingo | 10 calls | Batch ticker requests with date ranges |
| Polygon | 10 calls | Individual ticker aggregates |
| Alpaca | 10 calls | 5 tickers per call (batch bars) |
| Finnhub | 9 calls | Company news per priority ticker |
| Perplexity | 3 calls | AI summaries for ticker batches |
| Google News | 10 calls | RSS searches per ticker |
| Reddit | 10 calls | Keyword searches across subreddits |
| Alpha Vantage | 10 calls | Technical indicators with key rotation |
| SEC | 6 calls | Major company filings |
| Fed | 3 calls | RSS feeds (press, testimony, speeches) |

## 🗃️ Database Schema Integration

The pipeline populates these PostgreSQL tables:

### Core Tables
- `market_prices` - OHLCV data with unique constraints on (ticker, timestamp)
- `assets` - Asset metadata and registry
- `news_headlines` - News articles with sentiment scores
- `news_sentiment` - Detailed sentiment analysis results
- `alpha_vantage_data` - Raw technical indicator data
- `technical_indicators` - Processed technical analysis

### Regulatory & Infrastructure
- `regulatory_events` - SEC filings, Fed announcements
- `infra_incidents` - Service outages and status updates
- `infrastructure_status` - Real-time service health

### Audit & Tracking
- `ingestion_sessions` - Session tracking with metadata
- `alpha_ingestion_logs` - Detailed API call logs
- `anomalies` - Detected market anomalies (populated by separate ML pipeline)

## 🔄 Scheduling & Intervals

Default collection intervals (configurable via environment):

- **Market Data**: Every 5 minutes (300 seconds)
- **News Data**: Every 10 minutes (600 seconds)  
- **Technical Indicators**: Every 10 minutes (600 seconds)
- **Regulatory Events**: Every 12 hours (43,200 seconds)
- **Infrastructure Status**: Every 5 minutes (300 seconds)

## 🛡️ Comprehensive Error Handling & Resilience

### Advanced Rate Limit Management
- **Automatic Rate Limit Detection**: Detects 429 responses and quota exceeded errors
- **Provider Rate Limit Tracking**: Maintains rate limit status per provider with reset times  
- **Automatic Provider Switching**: Seamlessly switches to next available provider when rate limited
- **Smart Backoff Strategy**: Respects `Retry-After` headers and implements exponential backoff

### Multi-Level Fallback System
- **Primary → Fallback → Emergency**: Each collector can have multiple fallback providers
- **Budget-Aware Switching**: Only switches if API budget allows
- **Graceful Degradation**: Continues collecting from available providers when others fail

### ResilientCollector Base Class
All collectors inherit from `ResilientCollector` which provides:
- **API Budget Management**: Enforces call limits per collector (≤10 calls per cycle)
- **Safe API Calls**: `safe_api_call()` method with comprehensive error handling
- **Session Tracking**: Automatic session management and logging
- **Error Collection**: Detailed error tracking with timestamps and provider info

### Error Types & Handling
- **`RateLimitExceeded`**: Automatically sets provider as rate limited
- **`APIError`**: Handles 4xx/5xx responses with provider-specific logic
- **Connection Errors**: Retry with exponential backoff and jitter
- **Timeout Handling**: Configurable timeouts with retry logic

### Data Quality & Integrity
- **Idempotent Upserts**: Prevent duplicate data with unique constraints
- **Atomic Sessions**: All operations tracked in ingestion sessions
- **Quality Flags**: Track data completeness and processing status
- **Raw Payloads**: Preserve original responses for debugging

### Comprehensive Logging
- **Per-Provider Tracking**: API calls, successes, failures logged per provider
- **Rate Limit Events**: Detailed logging of rate limit encounters and resets
- **Error Details**: Full error messages, stack traces, and recovery actions
- **Performance Metrics**: Response times, retry counts, success rates

### Demo Error Handling
See `demo_error_handling.py` for a complete example showing:
- Rate limit detection and provider switching
- Fallback provider utilization
- API budget management
- Comprehensive error logging

```bash
# Run error handling demo
python3 demo_error_handling.py
```

### Session Management
- **Atomic ingestion sessions** with unique session IDs
- **Full audit trail** of all operations and API calls
- **Graceful shutdown** handling with proper cleanup
- **Status tracking** (RUNNING → COMPLETED/FAILED)

## 📊 Monitoring & Observability

### Logging
- Structured logging with multiple levels
- Timestamped log files in `logs/` directory
- Both file and console output
- Separate log files for tests, pipeline runs, etc.
- Per-provider operation tracking

### Metrics
- Records collected per provider
- API calls made per session
- Error rates and failure patterns
- Collection duration and performance

### Database Insights
```sql
-- View recent ingestion sessions
SELECT session_id, status, total_records, total_api_calls, start_time, end_time
FROM ingestion_sessions 
ORDER BY start_time DESC LIMIT 10;

-- Check provider performance
SELECT api_provider, COUNT(*) as calls, AVG(duration) as avg_duration, 
       SUM(records_ingested) as total_records
FROM alpha_ingestion_logs 
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY api_provider;

-- Market data freshness
SELECT ticker, MAX(timestamp) as latest_data, COUNT(*) as records
FROM market_prices 
GROUP BY ticker 
ORDER BY latest_data DESC;
```

## 🔧 Configuration

Key configuration options in `config.py`:

```python
# API rate limiting
MAX_CONCURRENT_REQUESTS = 3
REQUEST_TIMEOUT = 30
RETRY_ATTEMPTS = 3

# Collection intervals (seconds)
MARKET_DATA_INTERVAL = 300      # 5 minutes
NEWS_DATA_INTERVAL = 600        # 10 minutes
REGULATORY_INTERVAL = 43200     # 12 hours

# Priority tickers (adjust as needed)
PRIORITY_TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA',
    'JPM', 'BAC', 'GS', 'WFC', 'MS',
    'SPY', 'QQQ', 'IWM', 'BTC-USD', 'ETH-USD'
]
```

## � Logging System

All pipeline activities are automatically logged to timestamped files in the `logs/` directory:

### Log File Types
- `pipeline_YYYYMMDD_HHMMSS.log` - Main pipeline execution logs
- `test_YYYYMMDD_HHMMSS.log` - Test suite execution logs

### Log Contents
- Startup/shutdown information with configuration details
- Database connection and pool management
- HTTP client operations and retries
- API call tracking with provider details
- Data ingestion results and error handling
- Session management and audit trails

### Example Log Entries
```
2025-11-12 22:51:22,988 - __main__ - INFO - QuantVerse Data Collection Pipeline Starting
2025-11-12 22:51:22,988 - __main__ - INFO - Log file: /path/to/logs/pipeline_20251112_225122.log
2025-11-12 22:51:22,988 - __main__ - INFO - Environment: development
2025-11-12 22:51:22,988 - __main__ - INFO - Database: localhost:5432/urisk_core
```

### Viewing Logs
```bash
# View latest pipeline log
tail -f logs/pipeline_*.log

# View all recent logs
ls -la logs/

# Search for errors in logs
grep "ERROR\|FAIL" logs/*.log
```

## �🚨 Important Notes

### API Key Management
- Alpha Vantage uses key rotation across 80+ keys
- All other API keys configured in parent `.env` file
- Keys are automatically rotated to prevent rate limiting

### Database Requirements
- PostgreSQL with existing QuantVerse schema
- Asyncpg for high-performance async operations
- Connection pooling for concurrent access

### Production Deployment
- Use `--scheduled` mode for continuous operation
- Monitor log files for errors and performance
- Set appropriate log levels for production
- Consider running as systemd service

## 🤝 Integration with Existing System

This pipeline integrates seamlessly with the existing QuantVerse system:

- Uses existing database schema and tables
- Follows established ingestion patterns
- Compatible with current high-impact pipeline
- Maintains audit trail consistency
- Supports vector database population for RAG

## 📝 Example Output

```
🚀 QuantVerse Data Collection Pipeline
============================================================
Environment: development
Database: localhost:5432/urisk_core
Target tickers: 32 (AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA, NFLX, AMD, AVGO...)

Starting collection cycle pipeline_20241112_220245...

Market data - yfinance: 156 records, 3 calls
Market data - tiingo: 89 records, 4 calls  
Market data - polygon: 45 records, 5 calls
News - finnhub: 23 records, 5 calls
News - perplexity: 8 records, 2 calls
Technical - alpha_vantage: 67 records, 7 calls
Regulatory - sec: 12 records, 3 calls

============================================================
📊 COLLECTION CYCLE SUMMARY
============================================================
Session ID: pipeline_20241112_220245
Duration: 45.3 seconds
Total Records: 400
Total API Calls: 29
Errors: 0

📈 BY COLLECTOR:
  MARKET_DATA:
    Records: 290
    API Calls: 12
    Errors: 0
  NEWS:
    Records: 31
    API Calls: 7
    Errors: 0
  TECHNICAL:
    Records: 67
    API Calls: 7
    Errors: 0
  REGULATORY:
    Records: 12
    API Calls: 3
    Errors: 0
```

## 🎯 Success Metrics

The pipeline achieves:
- ✅ **Rate Limit Compliance**: All providers stay within 10 calls/cycle
- ✅ **High Throughput**: 400+ records per 45-second cycle
- ✅ **Multi-Provider Coverage**: 10+ data sources integrated
- ✅ **Data Quality**: Idempotent upserts with deduplication
- ✅ **Observability**: Complete audit trail and error tracking
- ✅ **Scalability**: Async/parallel execution patterns
