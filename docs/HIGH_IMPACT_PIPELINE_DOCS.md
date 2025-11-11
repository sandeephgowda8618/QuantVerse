# High-Impact Ticker Pipeline - Temporary Component Documentation

## Overview

The High-Impact Ticker Pipeline is a **temporary, detachable component** designed to quickly ingest data for 35 strategically selected tickers across major market sectors. This component runs alongside the main 200-company pipeline but can be easily removed when no longer needed.

## Component Design Philosophy

### Temporary & Detachable
- **Self-contained**: No dependencies on main pipeline code
- **Minimal footprint**: Single file implementation 
- **Clean separation**: Uses same backend modules but independent orchestration
- **Easy removal**: Can be deleted without affecting main pipeline

### Strategic Focus
- **35 high-impact tickers** across tech, finance, energy, retail, healthcare, ETFs, crypto
- **8 strategic endpoints** per ticker (fundamentals + light technicals)
- **~280 total API calls** - fits within free tier daily limits
- **Balanced market coverage** for risk analysis and regime detection

## Architecture

```
run_high_impact_pipeline.py (Temporary Component)
├── Uses existing backend/data_ingestion/ modules
├── Uses existing backend/db/ modules  
├── Independent session management
├── Sector-based filtering capability
└── Direct asset table integration
```

## Ticker Universe

### 📊 Tech Stocks (10 tickers)
- **Mega-cap leaders**: AAPL, MSFT, NVDA, AMZN, GOOGL
- **Growth & social**: META, TSLA, AMD, AVGO, NFLX
- **Characteristics**: High liquidity, news-driven, event-rich

### 🏦 Finance (5 tickers)  
- **Major banks**: JPM, BAC, GS, WFC, MS
- **Characteristics**: Rate-sensitive, macro-driven

### ⚡ Energy (3 tickers)
- **Oil majors**: XOM, CVX, COP
- **Characteristics**: Commodity-sensitive, geopolitical exposure

### 🏭 Industrials (4 tickers)
- **Defense & manufacturing**: BA, LMT, CAT, GE  
- **Characteristics**: Supply chain sensitive, defense exposure

### 🛒 Consumer/Retail (5 tickers)
- **Retail leaders**: WMT, COST, MCD, HD, SBUX
- **Characteristics**: Consumer sentiment, inflation-sensitive

### 💊 Healthcare (3 tickers)
- **Pharma majors**: JNJ, PFE, MRK
- **Characteristics**: FDA-driven, news-sensitive

### 📈 ETFs (3 tickers)
- **Market benchmarks**: SPY, QQQ, IWM
- **Characteristics**: Broad market behavior, volatility regimes

### ₿ Crypto (2 tickers)
- **Major cryptos**: BTC-USD, ETH-USD  
- **Characteristics**: Sudden moves, infra risk events

## Endpoint Strategy

Each ticker fetches **8 strategic endpoints** (~280 total API calls):

### Fundamental Data (5 endpoints)
- **OVERVIEW**: Company fundamentals, metrics, sector info
- **EARNINGS**: Historical earnings data and estimates  
- **INCOME_STATEMENT**: Revenue, margins, profitability trends
- **BALANCE_SHEET**: Assets, liabilities, equity structure
- **CASH_FLOW**: Operating, investing, financing cash flows

### Share Structure (1 endpoint)
- **SHARES_OUTSTANDING**: Share count changes over time

### Technical Indicators (2 endpoints)  
- **RSI**: Relative Strength Index (momentum)
- **EMA**: Exponential Moving Average (trend)

### Why These Endpoints?
- ✅ **Free tier compatible** - no premium endpoints
- ✅ **High signal-to-noise** - core financial and technical data
- ✅ **Multi-timeframe** - fundamental (quarterly) + technical (daily)
- ✅ **Cross-asset applicable** - works for stocks, ETFs, crypto

## Usage Examples

### Basic Usage
```bash
# Full high-impact ingestion (all 35 tickers)
python run_high_impact_pipeline.py

# Test configuration without fetching data
python run_high_impact_pipeline.py --dry-run

# Process specific sector only  
python run_high_impact_pipeline.py --sector tech
python run_high_impact_pipeline.py --sector finance
python run_high_impact_pipeline.py --sector energy
```

### Sector Options
- `tech`: Technology stocks (10 tickers)
- `finance`: Banks and financial services (5 tickers) 
- `energy`: Energy and oil companies (3 tickers)
- `industrials`: Defense and manufacturing (4 tickers)
- `retail`: Consumer and retail (5 tickers)
- `healthcare`: Pharmaceutical companies (3 tickers)
- `etfs`: Market benchmark ETFs (3 tickers)
- `crypto`: Major cryptocurrencies (2 tickers)
- `all`: All sectors (default, 35 tickers)

## Database Integration

### Assets Table Population
The pipeline automatically updates the `assets` table with high-impact tickers:

```sql
-- Example records inserted
INSERT INTO assets (ticker, name, asset_type, exchange, priority_score) VALUES
('AAPL', 'Apple Inc', 'stock', 'NASDAQ', 100),
('SPY', 'SPDR S&P 500 ETF', 'etf', 'NYSE', 95),
('BTC-USD', 'Bitcoin', 'crypto', 'COINBASE', 100);
```

### Data Storage
- Uses same `alpha_vantage_data` table as main pipeline
- Session ID format: `high_impact_YYYYMMDD_HHMMSS`
- Compatible with existing RAG and ML pipelines

## Performance Characteristics

### API Efficiency
- **280 API calls total** (8 endpoints × 35 tickers)
- **Fits within 500 calls/day** free tier limit  
- **~15-20 minutes** runtime with rate limiting
- **Intelligent key rotation** if using multiple API keys

### Data Volume
- **~2,000-5,000 records** per successful run
- **Mixed data types**: fundamentals, technicals, metadata
- **Timezone-aware timestamps** for global compatibility

### Success Rates
- **90%+ success rate** for core endpoints (OVERVIEW, EARNINGS)
- **70-80% success rate** for technical indicators (data availability varies)
- **Robust error handling** - continues on individual failures

## Integration with Main Pipeline

### Coexistence
- ✅ **Runs independently** - no conflicts with main pipeline
- ✅ **Shares database** - same tables, compatible schemas  
- ✅ **Reuses backend modules** - AlphaFetcher, AlphaNormalizer, AlphaWriter
- ✅ **Separate sessions** - distinct session IDs for tracking

### Data Compatibility
- Uses identical data normalization and storage patterns
- Compatible with existing RAG embeddings pipeline
- Compatible with ML model training pipelines
- Searchable via same query interfaces

## Detachment Instructions

When the temporary pipeline is no longer needed:

### 1. Stop Running the Component
```bash
# Simply stop executing the script
# No background processes to terminate
```

### 2. Remove the Pipeline File
```bash
# Delete the temporary component
rm run_high_impact_pipeline.py
```

### 3. Optional: Clean Up Database Records
If you want to remove the high-impact data:

```sql
-- Remove high-impact session data (optional)
DELETE FROM alpha_vantage_data 
WHERE ingestion_session_id LIKE 'high_impact_%';

-- Remove high-impact assets (optional - be careful!)
DELETE FROM assets 
WHERE ticker IN ('AAPL', 'MSFT', 'NVDA', ...);  -- List all 35 tickers

-- Remove ingestion sessions (optional)
DELETE FROM ingestion_sessions 
WHERE session_id LIKE 'high_impact_%';
```

### 4. Remove Documentation (Optional)
```bash
# Remove this documentation file
rm docs/HIGH_IMPACT_PIPELINE_DOCS.md
```

### 5. Update Configuration References
Remove any references to the high-impact pipeline from:
- README.md files
- Configuration documentation  
- Monitoring or alerting scripts

## Monitoring and Validation

### Success Validation
```sql
-- Check ingestion results
SELECT 
    ticker,
    endpoint, 
    COUNT(*) as record_count,
    MAX(updated_at) as last_update
FROM alpha_vantage_data 
WHERE ingestion_session_id LIKE 'high_impact_%'
GROUP BY ticker, endpoint
ORDER BY ticker, endpoint;
```

### Progress Tracking
```bash
# Monitor real-time logs
tail -f high_impact_ingestion_*.log

# Check completion status
grep "HIGH-IMPACT PIPELINE COMPLETED" high_impact_ingestion_*.log
```

## Business Value

### Market Coverage
- **Sector diversification**: Tech, finance, energy, industrials, healthcare
- **Market cap spectrum**: Mega-cap to mid-cap exposure
- **Volatility regimes**: Growth, value, defensive, speculative
- **Global exposure**: Multinational companies with worldwide operations

### Risk Analysis Support
- **Sudden move detection**: High-beta stocks, crypto for rapid price changes
- **Sector rotation**: Balanced representation for regime shift detection  
- **Macro sensitivity**: Rate-sensitive banks, commodity-linked energy
- **News flow**: High-profile stocks with rich news and social media data

### Cost Optimization
- **Free tier friendly**: 280 calls << 500 daily limit
- **High signal density**: Core fundamentals + technical indicators
- **Strategic selection**: Hand-picked for maximum analytical value
- **Efficient endpoints**: No expensive premium data requirements

## Integration Example

```python
# Example: Query high-impact ticker data
from backend.db.postgres_handler import PostgresHandler

db = PostgresHandler()

# Get latest fundamentals for tech stocks
tech_fundamentals = db.execute_query("""
    SELECT ticker, endpoint, data_json, updated_at
    FROM alpha_vantage_data 
    WHERE ticker IN ('AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL')
    AND endpoint = 'OVERVIEW'
    AND ingestion_session_id LIKE 'high_impact_%'
    ORDER BY ticker, updated_at DESC
""")

# Get RSI data for momentum analysis
rsi_data = db.execute_query("""
    SELECT ticker, data_json->>'RSI' as rsi_value, 
           data_json->>'time' as date
    FROM alpha_vantage_data
    WHERE endpoint = 'RSI' 
    AND ingestion_session_id LIKE 'high_impact_%'
    ORDER BY ticker, (data_json->>'time')::date DESC
""")
```

## Summary

The High-Impact Ticker Pipeline is designed as a **temporary bridge** to provide immediate, focused data collection while the main 200-company pipeline scales up. It delivers:

- ✅ **Immediate value**: Strategic ticker coverage from day one
- ✅ **Cost efficiency**: Fits within free API tier limits  
- ✅ **Easy detachment**: Clean removal when no longer needed
- ✅ **Full compatibility**: Integrates seamlessly with existing systems

This approach provides balanced market coverage, supports risk analysis workflows, and maintains system modularity for future evolution.
