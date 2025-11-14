-- QuantVerse Unified Database Schema (v2.1)
-- Clean version for PostgreSQL execution

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- 1. INGESTION & SESSION TRACKING LAYER
-- =============================================================================

-- Tracks each full collection cycle
CREATE TABLE IF NOT EXISTS ingestion_sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    status VARCHAR(20) NOT NULL CHECK (status IN ('RUNNING', 'COMPLETED', 'FAILED')),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    total_api_calls INTEGER DEFAULT 0,
    total_records INTEGER DEFAULT 0,
    duration_seconds NUMERIC(8,2),
    errors_count INTEGER DEFAULT 0,
    log_file_path TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Detailed per-call log for every API provider request
CREATE TABLE IF NOT EXISTS alpha_ingestion_logs (
    log_id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) REFERENCES ingestion_sessions(session_id) ON DELETE CASCADE,
    api_provider VARCHAR(50) NOT NULL,
    endpoint TEXT,
    call_number SMALLINT DEFAULT 1,
    duration NUMERIC(8,3),
    records_ingested INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL CHECK (status IN ('SUCCESS', 'FAILED', 'RATE_LIMITED')),
    error_message TEXT,
    response_code INTEGER,
    retry_attempts SMALLINT DEFAULT 0,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tracks provider budgets and rate limit states
CREATE TABLE IF NOT EXISTS provider_status (
    provider VARCHAR(50) PRIMARY KEY,
    remaining_calls INTEGER DEFAULT 10,
    last_reset TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    rate_limited_until TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- 2. MARKET DATA LAYER
-- =============================================================================

-- Registry of all tracked assets
CREATE TABLE IF NOT EXISTS assets (
    ticker VARCHAR(32) PRIMARY KEY,
    asset_name VARCHAR(120),
    exchange VARCHAR(50),
    asset_type VARCHAR(20) CHECK (asset_type IN ('STOCK', 'CRYPTO', 'ETF', 'BOND', 'COMMODITY', 'INDEX', 'OPTION')),
    currency VARCHAR(10) DEFAULT 'USD',
    sector VARCHAR(50),
    country VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- OHLCV table with deduplication per ticker-timestamp-source
CREATE TABLE IF NOT EXISTS market_prices (
    ticker VARCHAR(32) REFERENCES assets(ticker) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    open NUMERIC(12,4),
    high NUMERIC(12,4),
    low NUMERIC(12,4),
    close NUMERIC(12,4),
    volume BIGINT,
    source VARCHAR(30) NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    raw_payload JSONB,
    UNIQUE(ticker, timestamp, source)
);

-- Options data
CREATE TABLE IF NOT EXISTS options_data (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(32) REFERENCES assets(ticker) ON DELETE CASCADE,
    option_symbol VARCHAR(64) NOT NULL,
    type VARCHAR(10) CHECK (type IN ('CALL', 'PUT')),
    strike_price NUMERIC(10,2),
    expiry_date DATE,
    volume BIGINT,
    open_interest BIGINT,
    source VARCHAR(30) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    raw_payload JSONB,
    UNIQUE(option_symbol, timestamp)
);

-- =============================================================================
-- 3. NEWS & SENTIMENT LAYER
-- =============================================================================

-- All ingested headlines
CREATE TABLE IF NOT EXISTS news_headlines (
    news_id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(32) REFERENCES assets(ticker) ON DELETE SET NULL,
    headline TEXT NOT NULL,
    summary TEXT,
    url TEXT,
    source VARCHAR(50) NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    raw_payload JSONB,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(url)
);

-- Derived sentiment analysis
CREATE TABLE IF NOT EXISTS news_sentiment (
    headline_id BIGINT REFERENCES news_headlines(news_id) ON DELETE CASCADE,
    sentiment_score NUMERIC(5,3) CHECK (sentiment_score BETWEEN -1 AND 1),
    sentiment_label VARCHAR(10) CHECK (sentiment_label IN ('positive', 'neutral', 'negative')),
    provider VARCHAR(30) NOT NULL,
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(headline_id)
);

-- =============================================================================
-- 4. REGULATORY & ECONOMIC LAYER
-- =============================================================================

-- Regulatory events
CREATE TABLE IF NOT EXISTS regulatory_events (
    event_id BIGSERIAL PRIMARY KEY,
    source VARCHAR(30) NOT NULL,
    title TEXT NOT NULL,
    category VARCHAR(50),
    summary TEXT,
    url TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    raw_payload JSONB,
    UNIQUE(source, url)
);

-- Economic indicators
CREATE TABLE IF NOT EXISTS economic_indicators (
    indicator_id BIGSERIAL PRIMARY KEY,
    indicator_name VARCHAR(100) NOT NULL,
    value NUMERIC(12,4),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    source VARCHAR(50) NOT NULL,
    unit VARCHAR(20),
    raw_payload JSONB,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(indicator_name, timestamp, source)
);

-- =============================================================================
-- 5. TECHNICAL ANALYSIS LAYER
-- =============================================================================

-- Raw Alpha Vantage data
CREATE TABLE IF NOT EXISTS alpha_vantage_data (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(32) REFERENCES assets(ticker) ON DELETE CASCADE,
    function_name VARCHAR(50) NOT NULL,
    interval VARCHAR(20),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    data JSONB NOT NULL,
    source_key VARCHAR(50),
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(ticker, function_name, interval, timestamp)
);

-- Processed technical indicators
CREATE TABLE IF NOT EXISTS technical_indicators (
    ticker VARCHAR(32) REFERENCES assets(ticker) ON DELETE CASCADE,
    indicator_name VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    value NUMERIC(12,4),
    raw_payload JSONB,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(ticker, indicator_name, timestamp)
);

-- =============================================================================
-- 6. INFRASTRUCTURE & STATUS LAYER
-- =============================================================================

-- Infrastructure incidents
CREATE TABLE IF NOT EXISTS infra_incidents (
    incident_id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('operational', 'degraded', 'outage', 'maintenance')),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE,
    description TEXT,
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    source VARCHAR(50) NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    raw_payload JSONB,
    UNIQUE(platform, started_at)
);

-- Current infrastructure status
CREATE TABLE IF NOT EXISTS infrastructure_status (
    platform VARCHAR(50) PRIMARY KEY,
    status VARCHAR(20) CHECK (status IN ('operational', 'degraded', 'outage', 'maintenance')),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source VARCHAR(50) NOT NULL,
    raw_payload JSONB
);

-- =============================================================================
-- 7. ANALYTICS & ML LAYER
-- =============================================================================

-- Anomalies detected by ML
CREATE TABLE IF NOT EXISTS anomalies (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(32) REFERENCES assets(ticker) ON DELETE CASCADE,
    metric VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    severity NUMERIC(3,2) CHECK (severity BETWEEN 0 AND 10),
    description TEXT,
    detected_by VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    raw_payload JSONB,
    UNIQUE(ticker, metric, timestamp)
);

-- Price gaps
CREATE TABLE IF NOT EXISTS price_gaps (
    ticker VARCHAR(32) REFERENCES assets(ticker) ON DELETE CASCADE,
    gap_date DATE NOT NULL,
    previous_close NUMERIC(12,4),
    next_open NUMERIC(12,4),
    gap_percent NUMERIC(6,3),
    direction VARCHAR(10) CHECK (direction IN ('up', 'down')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(ticker, gap_date)
);

-- =============================================================================
-- 8. PERFORMANCE INDEXES
-- =============================================================================

-- Market data indexes
CREATE INDEX IF NOT EXISTS idx_market_prices_ticker_time ON market_prices(ticker, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_market_prices_source ON market_prices(source);
CREATE INDEX IF NOT EXISTS idx_market_prices_ingested ON market_prices(ingested_at DESC);

-- News indexes
CREATE INDEX IF NOT EXISTS idx_news_published ON news_headlines(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_ticker ON news_headlines(ticker);
CREATE INDEX IF NOT EXISTS idx_news_source ON news_headlines(source);

-- Sentiment indexes
CREATE INDEX IF NOT EXISTS idx_sentiment_score ON news_sentiment(sentiment_score DESC);
CREATE INDEX IF NOT EXISTS idx_sentiment_label ON news_sentiment(sentiment_label);

-- Technical analysis indexes
CREATE INDEX IF NOT EXISTS idx_alpha_vantage_ticker_func ON alpha_vantage_data(ticker, function_name);
CREATE INDEX IF NOT EXISTS idx_technical_indicators_ticker ON technical_indicators(ticker, indicator_name);

-- Anomaly indexes
CREATE INDEX IF NOT EXISTS idx_anomalies_metric_time ON anomalies(metric, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_anomalies_ticker_time ON anomalies(ticker, timestamp DESC);

-- Session tracking indexes
CREATE INDEX IF NOT EXISTS idx_ingestion_sessions_start ON ingestion_sessions(start_time DESC);
CREATE INDEX IF NOT EXISTS idx_alpha_logs_session ON alpha_ingestion_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_alpha_logs_provider ON alpha_ingestion_logs(api_provider, timestamp DESC);

-- Regulatory indexes
CREATE INDEX IF NOT EXISTS idx_regulatory_source_published ON regulatory_events(source, published_at DESC);

-- Infrastructure indexes
CREATE INDEX IF NOT EXISTS idx_infra_incidents_platform ON infra_incidents(platform, started_at DESC);

-- =============================================================================
-- 9. SAMPLE DATA INSERTS
-- =============================================================================

-- Insert priority tickers as assets
INSERT INTO assets (ticker, asset_name, exchange, asset_type, currency, sector, country) VALUES
('AAPL', 'Apple Inc.', 'NASDAQ', 'STOCK', 'USD', 'Technology', 'USA'),
('MSFT', 'Microsoft Corporation', 'NASDAQ', 'STOCK', 'USD', 'Technology', 'USA'),
('GOOGL', 'Alphabet Inc.', 'NASDAQ', 'STOCK', 'USD', 'Technology', 'USA'),
('AMZN', 'Amazon.com Inc.', 'NASDAQ', 'STOCK', 'USD', 'Consumer Discretionary', 'USA'),
('TSLA', 'Tesla Inc.', 'NASDAQ', 'STOCK', 'USD', 'Consumer Discretionary', 'USA'),
('META', 'Meta Platforms Inc.', 'NASDAQ', 'STOCK', 'USD', 'Technology', 'USA'),
('NVDA', 'NVIDIA Corporation', 'NASDAQ', 'STOCK', 'USD', 'Technology', 'USA'),
('NFLX', 'Netflix Inc.', 'NASDAQ', 'STOCK', 'USD', 'Communication Services', 'USA'),
('AMD', 'Advanced Micro Devices Inc.', 'NASDAQ', 'STOCK', 'USD', 'Technology', 'USA'),
('AVGO', 'Broadcom Inc.', 'NASDAQ', 'STOCK', 'USD', 'Technology', 'USA'),
('CRM', 'Salesforce Inc.', 'NYSE', 'STOCK', 'USD', 'Technology', 'USA'),
('ORCL', 'Oracle Corporation', 'NYSE', 'STOCK', 'USD', 'Technology', 'USA'),
('JPM', 'JPMorgan Chase & Co.', 'NYSE', 'STOCK', 'USD', 'Financials', 'USA'),
('BAC', 'Bank of America Corporation', 'NYSE', 'STOCK', 'USD', 'Financials', 'USA'),
('GS', 'Goldman Sachs Group Inc.', 'NYSE', 'STOCK', 'USD', 'Financials', 'USA'),
('WFC', 'Wells Fargo & Company', 'NYSE', 'STOCK', 'USD', 'Financials', 'USA'),
('MS', 'Morgan Stanley', 'NYSE', 'STOCK', 'USD', 'Financials', 'USA'),
('SPY', 'SPDR S&P 500 ETF Trust', 'NYSE', 'ETF', 'USD', 'ETF', 'USA'),
('QQQ', 'Invesco QQQ Trust', 'NASDAQ', 'ETF', 'USD', 'ETF', 'USA'),
('IWM', 'iShares Russell 2000 ETF', 'NYSE', 'ETF', 'USD', 'ETF', 'USA'),
('BTC-USD', 'Bitcoin USD', 'CRYPTO', 'CRYPTO', 'USD', 'Cryptocurrency', 'Global'),
('ETH-USD', 'Ethereum USD', 'CRYPTO', 'CRYPTO', 'USD', 'Cryptocurrency', 'Global')
ON CONFLICT (ticker) DO NOTHING;

-- Initialize provider status for all providers
INSERT INTO provider_status (provider, remaining_calls, last_reset, is_active) VALUES
('yfinance', 10, NOW(), TRUE),
('tiingo', 10, NOW(), TRUE),
('polygon', 10, NOW(), TRUE),
('alpaca', 10, NOW(), TRUE),
('finnhub', 10, NOW(), TRUE),
('perplexity', 10, NOW(), TRUE),
('google_news', 10, NOW(), TRUE),
('reddit', 10, NOW(), TRUE),
('alpha_vantage', 10, NOW(), TRUE),
('sec', 10, NOW(), TRUE),
('fed', 10, NOW(), TRUE),
('coinbase', 10, NOW(), TRUE),
('binance', 10, NOW(), TRUE),
('aws', 10, NOW(), TRUE),
('github', 10, NOW(), TRUE),
('nasdaq', 10, NOW(), TRUE)
ON CONFLICT (provider) DO NOTHING;
