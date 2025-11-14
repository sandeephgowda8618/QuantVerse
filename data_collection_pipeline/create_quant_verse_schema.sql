-- QuantVerse Unified Database Schema (v2.1)
-- Complete schema for multi-provider financial data pipeline
-- Created: November 12, 2025

-- Create the database (run this separately if needed)
-- CREATE DATABASE quant_verse;

-- Connect to the database
\c quant_verse;

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- 1️⃣ INGESTION & SESSION TRACKING LAYER
-- ============================================================================

-- Tracks each full collection cycle (like a pipeline_20251112_220245 run)
CREATE TABLE ingestion_sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    status VARCHAR(20) NOT NULL CHECK (status IN ('RUNNING', 'COMPLETED', 'FAILED')),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    total_api_calls INTEGER DEFAULT 0,
    total_records INTEGER DEFAULT 0,
    duration_seconds NUMERIC(8,2),
    errors_count INTEGER DEFAULT 0,
    log_file_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Detailed per-call log for every API provider request
CREATE TABLE alpha_ingestion_logs (
    log_id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) REFERENCES ingestion_sessions(session_id),
    api_provider VARCHAR(50) NOT NULL,
    endpoint TEXT,
    call_number SMALLINT,
    duration NUMERIC(8,3),
    records_ingested INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL CHECK (status IN ('SUCCESS', 'FAILED', 'RATE_LIMITED')),
    error_message TEXT,
    response_code INTEGER,
    retry_attempts SMALLINT DEFAULT 0,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tracks provider budgets and rate limit states
CREATE TABLE provider_status (
    provider VARCHAR(50) PRIMARY KEY,
    remaining_calls INTEGER DEFAULT 10,
    last_reset TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    rate_limited_until TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 2️⃣ MARKET DATA LAYER
-- ============================================================================

-- Registry of all tracked assets (tickers, cryptos, ETFs, etc.)
CREATE TABLE assets (
    ticker VARCHAR(32) PRIMARY KEY,
    asset_name VARCHAR(120),
    exchange VARCHAR(50),
    asset_type VARCHAR(20) CHECK (asset_type IN ('STOCK', 'CRYPTO', 'ETF', 'OPTION', 'FOREX', 'INDEX')),
    currency VARCHAR(10) DEFAULT 'USD',
    sector VARCHAR(50),
    country VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- OHLCV table with deduplication per ticker-timestamp-source
CREATE TABLE market_prices (
    ticker VARCHAR(32) REFERENCES assets(ticker),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    open NUMERIC(12,4),
    high NUMERIC(12,4),
    low NUMERIC(12,4),
    close NUMERIC(12,4) NOT NULL,
    volume BIGINT,
    source VARCHAR(30) NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    raw_payload JSONB,
    UNIQUE(ticker, timestamp, source)
);

-- Stores aggregated or individual option trades (Polygon, Tradier, etc.)
CREATE TABLE options_data (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(32) REFERENCES assets(ticker),
    option_symbol VARCHAR(64) NOT NULL,
    type VARCHAR(10) CHECK (type IN ('CALL', 'PUT')),
    strike_price NUMERIC(10,2),
    expiry_date DATE,
    volume BIGINT,
    open_interest BIGINT,
    source VARCHAR(30),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    raw_payload JSONB,
    UNIQUE(option_symbol, timestamp)
);

-- ============================================================================
-- 3️⃣ NEWS & SENTIMENT LAYER
-- ============================================================================

-- All ingested headlines from Finnhub, Reddit, Perplexity, etc.
CREATE TABLE news_headlines (
    news_id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(32) REFERENCES assets(ticker),
    headline TEXT NOT NULL,
    summary TEXT,
    url TEXT,
    source VARCHAR(50) NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    raw_payload JSONB,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(url)
);

-- Derived table after analysis (links to news_headlines)
CREATE TABLE news_sentiment (
    headline_id BIGINT REFERENCES news_headlines(news_id),
    sentiment_score NUMERIC(5,3) CHECK (sentiment_score BETWEEN -1 AND 1),
    sentiment_label VARCHAR(10) CHECK (sentiment_label IN ('positive', 'neutral', 'negative')),
    provider VARCHAR(30),
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(headline_id)
);

-- ============================================================================
-- 4️⃣ REGULATORY & ECONOMIC LAYER
-- ============================================================================

-- For SEC, Fed, RBI, etc.
CREATE TABLE regulatory_events (
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

-- For AlphaVantage or Fed macroeconomic data
CREATE TABLE economic_indicators (
    indicator_id BIGSERIAL PRIMARY KEY,
    indicator_name VARCHAR(100) NOT NULL,
    value NUMERIC(12,4),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    source VARCHAR(50),
    unit VARCHAR(20),
    raw_payload JSONB,
    UNIQUE(indicator_name, timestamp, source)
);

-- ============================================================================
-- 5️⃣ TECHNICAL ANALYSIS LAYER
-- ============================================================================

-- Raw data dumps per call
CREATE TABLE alpha_vantage_data (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(32) REFERENCES assets(ticker),
    function_name VARCHAR(50) NOT NULL,
    interval VARCHAR(20),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    data JSONB NOT NULL,
    source_key VARCHAR(50),
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(ticker, function_name, interval, timestamp)
);

-- Processed indicator values for easy queries
CREATE TABLE technical_indicators (
    ticker VARCHAR(32) REFERENCES assets(ticker),
    indicator_name VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    value NUMERIC(12,4),
    raw_payload JSONB,
    UNIQUE(ticker, indicator_name, timestamp)
);

-- ============================================================================
-- 6️⃣ INFRASTRUCTURE & STATUS LAYER
-- ============================================================================

-- Tracks outages or degradation events
CREATE TABLE infra_incidents (
    incident_id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('operational', 'degraded', 'outage', 'resolved')),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE,
    description TEXT,
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    source VARCHAR(50),
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    raw_payload JSONB,
    UNIQUE(platform, started_at)
);

-- Current operational states
CREATE TABLE infrastructure_status (
    platform VARCHAR(50) PRIMARY KEY,
    status VARCHAR(20) NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source VARCHAR(50),
    raw_payload JSONB
);

-- ============================================================================
-- 7️⃣ ANALYTICS & ML LAYER
-- ============================================================================

-- Populated by internal anomaly detection ML
CREATE TABLE anomalies (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(32) REFERENCES assets(ticker),
    metric VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    severity NUMERIC(3,2) CHECK (severity BETWEEN 0 AND 10),
    description TEXT,
    detected_by VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    raw_payload JSONB,
    UNIQUE(ticker, metric, timestamp)
);

-- Stores calculated price gap data
CREATE TABLE price_gaps (
    ticker VARCHAR(32) REFERENCES assets(ticker),
    gap_date DATE NOT NULL,
    previous_close NUMERIC(12,4),
    next_open NUMERIC(12,4),
    gap_percent NUMERIC(6,3),
    direction VARCHAR(10) CHECK (direction IN ('up', 'down')),
    UNIQUE(ticker, gap_date)
);

-- ============================================================================
-- 8️⃣ PERFORMANCE INDEXES
-- ============================================================================

-- Market data indexes
CREATE INDEX idx_market_prices_ticker_time ON market_prices(ticker, timestamp DESC);
CREATE INDEX idx_market_prices_source ON market_prices(source);
CREATE INDEX idx_market_prices_ingested ON market_prices(ingested_at DESC);

-- News indexes
CREATE INDEX idx_news_published ON news_headlines(published_at DESC);
CREATE INDEX idx_news_ticker ON news_headlines(ticker);
CREATE INDEX idx_news_source ON news_headlines(source);

-- Sentiment indexes
CREATE INDEX idx_sentiment_score ON news_sentiment(sentiment_score);
CREATE INDEX idx_sentiment_label ON news_sentiment(sentiment_label);

-- Technical indicators indexes
CREATE INDEX idx_technical_ticker_indicator ON technical_indicators(ticker, indicator_name);
CREATE INDEX idx_technical_timestamp ON technical_indicators(timestamp DESC);

-- Alpha Vantage indexes
CREATE INDEX idx_alpha_ticker_function ON alpha_vantage_data(ticker, function_name);
CREATE INDEX idx_alpha_timestamp ON alpha_vantage_data(timestamp DESC);

-- Anomalies indexes
CREATE INDEX idx_anomalies_metric_time ON anomalies(metric, timestamp DESC);
CREATE INDEX idx_anomalies_ticker ON anomalies(ticker);
CREATE INDEX idx_anomalies_severity ON anomalies(severity DESC);

-- Session tracking indexes
CREATE INDEX idx_sessions_start_time ON ingestion_sessions(start_time DESC);
CREATE INDEX idx_sessions_status ON ingestion_sessions(status);
CREATE INDEX idx_alpha_logs_session ON alpha_ingestion_logs(session_id);
CREATE INDEX idx_alpha_logs_provider ON alpha_ingestion_logs(api_provider);
CREATE INDEX idx_alpha_logs_timestamp ON alpha_ingestion_logs(timestamp DESC);

-- Regulatory events indexes
CREATE INDEX idx_regulatory_source ON regulatory_events(source);
CREATE INDEX idx_regulatory_published ON regulatory_events(published_at DESC);
CREATE INDEX idx_regulatory_category ON regulatory_events(category);

-- Economic indicators indexes
CREATE INDEX idx_economic_indicator_time ON economic_indicators(indicator_name, timestamp DESC);
CREATE INDEX idx_economic_source ON economic_indicators(source);

-- Infrastructure indexes
CREATE INDEX idx_infra_incidents_platform ON infra_incidents(platform);
CREATE INDEX idx_infra_incidents_status ON infra_incidents(status);
CREATE INDEX idx_infra_incidents_severity ON infra_incidents(severity);

-- Options data indexes
CREATE INDEX idx_options_ticker ON options_data(ticker);
CREATE INDEX idx_options_symbol ON options_data(option_symbol);
CREATE INDEX idx_options_timestamp ON options_data(timestamp DESC);

-- Assets indexes
CREATE INDEX idx_assets_type ON assets(asset_type);
CREATE INDEX idx_assets_exchange ON assets(exchange);
CREATE INDEX idx_assets_active ON assets(is_active);

-- ============================================================================
-- 9️⃣ PARTITIONING (Optional - for large datasets)
-- ============================================================================

-- Time-based partitioning for market_prices (monthly partitions)
-- This would be implemented separately for production environments
-- Example partition creation (commented out):
-- CREATE TABLE market_prices_2025_11 PARTITION OF market_prices
-- FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

-- ============================================================================
-- 🔟 MATERIALIZED VIEWS FOR PERFORMANCE
-- ============================================================================

-- Latest market prices per ticker
CREATE MATERIALIZED VIEW latest_market_prices AS
SELECT DISTINCT ON (ticker) 
    ticker,
    timestamp,
    close,
    volume,
    source,
    ingested_at
FROM market_prices
ORDER BY ticker, timestamp DESC;

CREATE UNIQUE INDEX idx_latest_prices_ticker ON latest_market_prices(ticker);

-- Recent sentiment summary (last 24 hours)
CREATE MATERIALIZED VIEW recent_sentiment_summary AS
SELECT 
    nh.ticker,
    COUNT(*) as total_articles,
    AVG(ns.sentiment_score) as avg_sentiment,
    COUNT(CASE WHEN ns.sentiment_label = 'positive' THEN 1 END) as positive_count,
    COUNT(CASE WHEN ns.sentiment_label = 'negative' THEN 1 END) as negative_count,
    COUNT(CASE WHEN ns.sentiment_label = 'neutral' THEN 1 END) as neutral_count
FROM news_headlines nh
LEFT JOIN news_sentiment ns ON nh.news_id = ns.headline_id
WHERE nh.published_at > NOW() - INTERVAL '24 hours'
GROUP BY nh.ticker;

CREATE INDEX idx_recent_sentiment_ticker ON recent_sentiment_summary(ticker);

-- Provider call stats (last 24 hours)
CREATE MATERIALIZED VIEW provider_call_stats_last_24h AS
SELECT 
    api_provider,
    COUNT(*) as total_calls,
    COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as successful_calls,
    COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed_calls,
    COUNT(CASE WHEN status = 'RATE_LIMITED' THEN 1 END) as rate_limited_calls,
    AVG(duration) as avg_duration_seconds,
    SUM(records_ingested) as total_records_ingested,
    MAX(timestamp) as last_call_time
FROM alpha_ingestion_logs
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY api_provider;

CREATE INDEX idx_provider_stats_provider ON provider_call_stats_last_24h(api_provider);

-- ============================================================================
-- 🎯 INITIAL DATA SEEDING
-- ============================================================================

-- Insert default provider status records
INSERT INTO provider_status (provider, remaining_calls, is_active) VALUES
('yfinance', 10, TRUE),
('tiingo', 10, TRUE),
('polygon', 10, TRUE),
('alpaca', 10, TRUE),
('finnhub', 10, TRUE),
('perplexity', 3, TRUE),
('google_news', 10, TRUE),
('reddit', 10, TRUE),
('alpha_vantage', 10, TRUE),
('sec', 6, TRUE),
('fed', 3, TRUE),
('coinbase', 5, TRUE),
('binance', 5, TRUE),
('aws', 5, TRUE),
('github', 5, TRUE),
('nasdaq', 5, TRUE)
ON CONFLICT (provider) DO NOTHING;

-- Insert priority assets
INSERT INTO assets (ticker, asset_name, exchange, asset_type, currency, sector, country) VALUES
-- Major Tech Stocks
('AAPL', 'Apple Inc.', 'NASDAQ', 'STOCK', 'USD', 'Technology', 'USA'),
('MSFT', 'Microsoft Corporation', 'NASDAQ', 'STOCK', 'USD', 'Technology', 'USA'),
('GOOGL', 'Alphabet Inc. Class A', 'NASDAQ', 'STOCK', 'USD', 'Technology', 'USA'),
('AMZN', 'Amazon.com Inc.', 'NASDAQ', 'STOCK', 'USD', 'Consumer Discretionary', 'USA'),
('TSLA', 'Tesla Inc.', 'NASDAQ', 'STOCK', 'USD', 'Consumer Discretionary', 'USA'),
('META', 'Meta Platforms Inc.', 'NASDAQ', 'STOCK', 'USD', 'Technology', 'USA'),
('NVDA', 'NVIDIA Corporation', 'NASDAQ', 'STOCK', 'USD', 'Technology', 'USA'),
('NFLX', 'Netflix Inc.', 'NASDAQ', 'STOCK', 'USD', 'Communication Services', 'USA'),
('AMD', 'Advanced Micro Devices Inc.', 'NASDAQ', 'STOCK', 'USD', 'Technology', 'USA'),
('AVGO', 'Broadcom Inc.', 'NASDAQ', 'STOCK', 'USD', 'Technology', 'USA'),

-- Major Financial Stocks
('JPM', 'JPMorgan Chase & Co.', 'NYSE', 'STOCK', 'USD', 'Financials', 'USA'),
('BAC', 'Bank of America Corporation', 'NYSE', 'STOCK', 'USD', 'Financials', 'USA'),
('GS', 'The Goldman Sachs Group Inc.', 'NYSE', 'STOCK', 'USD', 'Financials', 'USA'),
('WFC', 'Wells Fargo & Company', 'NYSE', 'STOCK', 'USD', 'Financials', 'USA'),
('MS', 'Morgan Stanley', 'NYSE', 'STOCK', 'USD', 'Financials', 'USA'),

-- Major ETFs
('SPY', 'SPDR S&P 500 ETF Trust', 'NYSE Arca', 'ETF', 'USD', 'Broad Market', 'USA'),
('QQQ', 'Invesco QQQ Trust Series 1', 'NASDAQ', 'ETF', 'USD', 'Technology', 'USA'),
('IWM', 'iShares Russell 2000 ETF', 'NYSE Arca', 'ETF', 'USD', 'Small Cap', 'USA'),

-- Cryptocurrencies
('BTC-USD', 'Bitcoin USD', 'CRYPTO', 'CRYPTO', 'USD', 'Cryptocurrency', 'Global'),
('ETH-USD', 'Ethereum USD', 'CRYPTO', 'CRYPTO', 'USD', 'Cryptocurrency', 'Global')

ON CONFLICT (ticker) DO UPDATE SET
    asset_name = EXCLUDED.asset_name,
    exchange = EXCLUDED.exchange,
    asset_type = EXCLUDED.asset_type,
    currency = EXCLUDED.currency,
    sector = EXCLUDED.sector,
    country = EXCLUDED.country;

-- ============================================================================
-- 📊 DATABASE STATISTICS AND MONITORING
-- ============================================================================

-- Function to refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY latest_market_prices;
    REFRESH MATERIALIZED VIEW CONCURRENTLY recent_sentiment_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY provider_call_stats_last_24h;
END;
$$ LANGUAGE plpgsql;

-- Function to get database statistics
CREATE OR REPLACE FUNCTION get_database_statistics()
RETURNS TABLE (
    table_name text,
    row_count bigint,
    table_size text,
    index_size text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        schemaname||'.'||tablename as table_name,
        n_tup_ins - n_tup_del as row_count,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size,
        pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) as index_size
    FROM pg_stat_user_tables
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ✅ SCHEMA CREATION COMPLETE
-- ============================================================================

ANALYZE;

-- Display schema creation summary
SELECT 'QuantVerse Database Schema v2.1 Created Successfully!' as status;
SELECT 'Tables created: ' || count(*) as table_count FROM information_schema.tables WHERE table_schema = 'public';
SELECT 'Indexes created: ' || count(*) as index_count FROM pg_indexes WHERE schemaname = 'public';
SELECT 'Materialized views created: 3' as materialized_views;
SELECT 'Functions created: 2' as functions;
