-- Alpha Vantage Enhanced Database Schema
-- Supports 200-company epoch-based ingestion with full metadata
-- All tables have unique constraints to prevent duplicates

-- ==========================================
-- CHECKPOINT TABLE FOR FAULT TOLERANCE
-- ==========================================

CREATE TABLE IF NOT EXISTS alpha_ingestion_progress (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    last_completed_endpoint VARCHAR(100),
    last_completed_function VARCHAR(100),
    epoch INT NOT NULL,
    total_endpoints INT DEFAULT 0,
    completed_endpoints INT DEFAULT 0,
    started_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'in_progress', -- in_progress, completed, failed, paused
    error_message TEXT,
    retry_count INT DEFAULT 0,
    UNIQUE(ticker)
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_alpha_progress_ticker ON alpha_ingestion_progress(ticker);
CREATE INDEX IF NOT EXISTS idx_alpha_progress_epoch ON alpha_ingestion_progress(epoch);
CREATE INDEX IF NOT EXISTS idx_alpha_progress_status ON alpha_ingestion_progress(status);

-- ==========================================
-- ENHANCED MARKET PRICES - ALPHA VANTAGE
-- ==========================================

CREATE TABLE IF NOT EXISTS alpha_market_data (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    endpoint VARCHAR(100) NOT NULL,
    api_function VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    interval_type VARCHAR(20), -- 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
    
    -- Price data
    open_price DECIMAL(15, 4),
    high_price DECIMAL(15, 4),
    low_price DECIMAL(15, 4),
    close_price DECIMAL(15, 4),
    adjusted_close DECIMAL(15, 4),
    volume BIGINT,
    dividend_amount DECIMAL(10, 4),
    split_coefficient DECIMAL(10, 4),
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'alpha_vantage',
    raw_payload JSONB NOT NULL,
    parsed_values JSONB,
    quality_flag VARCHAR(20) DEFAULT 'complete', -- complete, partial, missing, error
    ingestion_epoch INT NOT NULL,
    ingestion_sequence BIGINT NOT NULL,
    ingestion_time TIMESTAMP DEFAULT NOW(),
    
    -- Unique constraint prevents duplicates
    UNIQUE(ticker, timestamp, endpoint, interval_type)
);

-- Create indexes for market data
CREATE INDEX IF NOT EXISTS idx_alpha_market_ticker ON alpha_market_data(ticker);
CREATE INDEX IF NOT EXISTS idx_alpha_market_timestamp ON alpha_market_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_alpha_market_endpoint ON alpha_market_data(endpoint);
CREATE INDEX IF NOT EXISTS idx_alpha_market_epoch ON alpha_market_data(ingestion_epoch);
CREATE INDEX IF NOT EXISTS idx_alpha_market_ticker_time ON alpha_market_data(ticker, timestamp DESC);

-- ==========================================
-- TECHNICAL INDICATORS
-- ==========================================

CREATE TABLE IF NOT EXISTS alpha_technical_indicators (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    endpoint VARCHAR(100) NOT NULL,
    api_function VARCHAR(100) NOT NULL,
    indicator_name VARCHAR(50) NOT NULL, -- RSI, MACD, SMA, etc.
    timestamp TIMESTAMP NOT NULL,
    interval_type VARCHAR(20),
    
    -- Indicator values (flexible for different indicators)
    value_1 DECIMAL(15, 6), -- primary value (e.g., RSI value, SMA value)
    value_2 DECIMAL(15, 6), -- secondary value (e.g., MACD signal)
    value_3 DECIMAL(15, 6), -- tertiary value (e.g., MACD histogram)
    value_4 DECIMAL(15, 6), -- quaternary value (e.g., Bollinger upper band)
    value_5 DECIMAL(15, 6), -- additional value (e.g., Bollinger lower band)
    
    -- Named values for specific indicators
    indicator_values JSONB, -- stores all indicator values with proper names
    
    -- Parameters used
    time_period INT,
    series_type VARCHAR(20), -- close, open, high, low
    parameters JSONB, -- stores all parameters used for the indicator
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'alpha_vantage',
    raw_payload JSONB NOT NULL,
    quality_flag VARCHAR(20) DEFAULT 'complete',
    ingestion_epoch INT NOT NULL,
    ingestion_sequence BIGINT NOT NULL,
    ingestion_time TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(ticker, timestamp, endpoint, indicator_name, interval_type)
);

-- Create indexes for technical indicators
CREATE INDEX IF NOT EXISTS idx_alpha_tech_ticker ON alpha_technical_indicators(ticker);
CREATE INDEX IF NOT EXISTS idx_alpha_tech_indicator ON alpha_technical_indicators(indicator_name);
CREATE INDEX IF NOT EXISTS idx_alpha_tech_timestamp ON alpha_technical_indicators(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_alpha_tech_epoch ON alpha_technical_indicators(ingestion_epoch);

-- ==========================================
-- FUNDAMENTAL DATA
-- ==========================================

CREATE TABLE IF NOT EXISTS alpha_fundamental_data (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    endpoint VARCHAR(100) NOT NULL,
    api_function VARCHAR(100) NOT NULL,
    data_type VARCHAR(50) NOT NULL, -- overview, income_statement, balance_sheet, etc.
    fiscal_date_ending DATE,
    reported_currency VARCHAR(10),
    period_type VARCHAR(20), -- annual, quarterly
    
    -- Financial metrics (flexible storage)
    financial_data JSONB NOT NULL, -- stores all financial data
    
    -- Common fields for quick access
    total_revenue DECIMAL(20, 2),
    net_income DECIMAL(20, 2),
    total_assets DECIMAL(20, 2),
    total_liabilities DECIMAL(20, 2),
    shareholders_equity DECIMAL(20, 2),
    eps DECIMAL(10, 4),
    pe_ratio DECIMAL(10, 2),
    market_cap DECIMAL(20, 2),
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'alpha_vantage',
    raw_payload JSONB NOT NULL,
    quality_flag VARCHAR(20) DEFAULT 'complete',
    ingestion_epoch INT NOT NULL,
    ingestion_sequence BIGINT NOT NULL,
    ingestion_time TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(ticker, endpoint, fiscal_date_ending, period_type, data_type)
);

-- Create indexes for fundamental data
CREATE INDEX IF NOT EXISTS idx_alpha_fund_ticker ON alpha_fundamental_data(ticker);
CREATE INDEX IF NOT EXISTS idx_alpha_fund_type ON alpha_fundamental_data(data_type);
CREATE INDEX IF NOT EXISTS idx_alpha_fund_date ON alpha_fundamental_data(fiscal_date_ending DESC);
CREATE INDEX IF NOT EXISTS idx_alpha_fund_epoch ON alpha_fundamental_data(ingestion_epoch);

-- ==========================================
-- NEWS & INTELLIGENCE
-- ==========================================

CREATE TABLE IF NOT EXISTS alpha_news_intelligence (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20),
    endpoint VARCHAR(100) NOT NULL,
    api_function VARCHAR(100) NOT NULL,
    
    -- News data
    title TEXT,
    url TEXT,
    published_at TIMESTAMP,
    source_name VARCHAR(100),
    summary TEXT,
    
    -- Sentiment analysis
    overall_sentiment_score DECIMAL(5, 4), -- -1 to +1
    overall_sentiment_label VARCHAR(20),
    ticker_sentiment_score DECIMAL(5, 4),
    ticker_sentiment_label VARCHAR(20),
    relevance_score DECIMAL(5, 4),
    
    -- Topics and categories
    topics JSONB, -- array of topics with relevance scores
    category VARCHAR(100),
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'alpha_vantage',
    raw_payload JSONB NOT NULL,
    quality_flag VARCHAR(20) DEFAULT 'complete',
    ingestion_epoch INT NOT NULL,
    ingestion_sequence BIGINT NOT NULL,
    ingestion_time TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(ticker, url, published_at, endpoint)
);

-- Create indexes for news intelligence
CREATE INDEX IF NOT EXISTS idx_alpha_news_ticker ON alpha_news_intelligence(ticker);
CREATE INDEX IF NOT EXISTS idx_alpha_news_published ON alpha_news_intelligence(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_alpha_news_sentiment ON alpha_news_intelligence(overall_sentiment_score);
CREATE INDEX IF NOT EXISTS idx_alpha_news_epoch ON alpha_news_intelligence(ingestion_epoch);

-- ==========================================
-- FOREX DATA
-- ==========================================

CREATE TABLE IF NOT EXISTS alpha_forex_data (
    id SERIAL PRIMARY KEY,
    from_currency VARCHAR(10) NOT NULL,
    to_currency VARCHAR(10) NOT NULL,
    currency_pair VARCHAR(20) NOT NULL, -- e.g., EURUSD
    endpoint VARCHAR(100) NOT NULL,
    api_function VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    interval_type VARCHAR(20),
    
    -- FX data
    exchange_rate DECIMAL(15, 8),
    open_rate DECIMAL(15, 8),
    high_rate DECIMAL(15, 8),
    low_rate DECIMAL(15, 8),
    close_rate DECIMAL(15, 8),
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'alpha_vantage',
    raw_payload JSONB NOT NULL,
    quality_flag VARCHAR(20) DEFAULT 'complete',
    ingestion_epoch INT NOT NULL,
    ingestion_sequence BIGINT NOT NULL,
    ingestion_time TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(currency_pair, timestamp, endpoint, interval_type)
);

-- Create indexes for forex data
CREATE INDEX IF NOT EXISTS idx_alpha_forex_pair ON alpha_forex_data(currency_pair);
CREATE INDEX IF NOT EXISTS idx_alpha_forex_timestamp ON alpha_forex_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_alpha_forex_epoch ON alpha_forex_data(ingestion_epoch);

-- ==========================================
-- CRYPTO DATA
-- ==========================================

CREATE TABLE IF NOT EXISTS alpha_crypto_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    market VARCHAR(20) NOT NULL, -- USD, EUR, etc.
    endpoint VARCHAR(100) NOT NULL,
    api_function VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    interval_type VARCHAR(20),
    
    -- Crypto data
    open_price_usd DECIMAL(20, 8),
    high_price_usd DECIMAL(20, 8),
    low_price_usd DECIMAL(20, 8),
    close_price_usd DECIMAL(20, 8),
    open_price_market DECIMAL(20, 8),
    high_price_market DECIMAL(20, 8),
    low_price_market DECIMAL(20, 8),
    close_price_market DECIMAL(20, 8),
    volume DECIMAL(25, 8),
    market_cap_usd DECIMAL(25, 2),
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'alpha_vantage',
    raw_payload JSONB NOT NULL,
    quality_flag VARCHAR(20) DEFAULT 'complete',
    ingestion_epoch INT NOT NULL,
    ingestion_sequence BIGINT NOT NULL,
    ingestion_time TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(symbol, market, timestamp, endpoint, interval_type)
);

-- Create indexes for crypto data
CREATE INDEX IF NOT EXISTS idx_alpha_crypto_symbol ON alpha_crypto_data(symbol);
CREATE INDEX IF NOT EXISTS idx_alpha_crypto_timestamp ON alpha_crypto_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_alpha_crypto_epoch ON alpha_crypto_data(ingestion_epoch);

-- ==========================================
-- COMMODITIES DATA
-- ==========================================

CREATE TABLE IF NOT EXISTS alpha_commodities_data (
    id SERIAL PRIMARY KEY,
    commodity VARCHAR(50) NOT NULL, -- WTI, BRENT, NATURAL_GAS, etc.
    endpoint VARCHAR(100) NOT NULL,
    api_function VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    interval_type VARCHAR(20),
    
    -- Commodities data
    price DECIMAL(15, 4),
    unit VARCHAR(20), -- barrel, ounce, pound, etc.
    currency VARCHAR(10) DEFAULT 'USD',
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'alpha_vantage',
    raw_payload JSONB NOT NULL,
    quality_flag VARCHAR(20) DEFAULT 'complete',
    ingestion_epoch INT NOT NULL,
    ingestion_sequence BIGINT NOT NULL,
    ingestion_time TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(commodity, timestamp, endpoint, interval_type)
);

-- Create indexes for commodities data
CREATE INDEX IF NOT EXISTS idx_alpha_commodity_name ON alpha_commodities_data(commodity);
CREATE INDEX IF NOT EXISTS idx_alpha_commodity_timestamp ON alpha_commodities_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_alpha_commodity_epoch ON alpha_commodities_data(ingestion_epoch);

-- ==========================================
-- ECONOMIC INDICATORS
-- ==========================================

CREATE TABLE IF NOT EXISTS alpha_economic_indicators (
    id SERIAL PRIMARY KEY,
    indicator VARCHAR(50) NOT NULL, -- REAL_GDP, CPI, UNEMPLOYMENT, etc.
    endpoint VARCHAR(100) NOT NULL,
    api_function VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    interval_type VARCHAR(20),
    
    -- Economic data
    value DECIMAL(20, 4),
    unit VARCHAR(50),
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'alpha_vantage',
    raw_payload JSONB NOT NULL,
    quality_flag VARCHAR(20) DEFAULT 'complete',
    ingestion_epoch INT NOT NULL,
    ingestion_sequence BIGINT NOT NULL,
    ingestion_time TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(indicator, timestamp, endpoint, interval_type)
);

-- Create indexes for economic indicators
CREATE INDEX IF NOT EXISTS idx_alpha_econ_indicator ON alpha_economic_indicators(indicator);
CREATE INDEX IF NOT EXISTS idx_alpha_econ_timestamp ON alpha_economic_indicators(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_alpha_econ_epoch ON alpha_economic_indicators(ingestion_epoch);

-- ==========================================
-- ANALYTICS DATA (FIXED & SLIDING WINDOW)
-- ==========================================

CREATE TABLE IF NOT EXISTS alpha_analytics_data (
    id SERIAL PRIMARY KEY,
    symbols TEXT NOT NULL, -- comma-separated list of symbols
    endpoint VARCHAR(100) NOT NULL,
    api_function VARCHAR(100) NOT NULL,
    calculation_type VARCHAR(50) NOT NULL, -- MEAN, VARIANCE, CORRELATION, etc.
    range_start DATE,
    range_end DATE,
    interval_type VARCHAR(20),
    window_size INT, -- for sliding window calculations
    
    -- Analytics results
    results JSONB NOT NULL, -- stores calculation results
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'alpha_vantage',
    raw_payload JSONB NOT NULL,
    quality_flag VARCHAR(20) DEFAULT 'complete',
    ingestion_epoch INT NOT NULL,
    ingestion_sequence BIGINT NOT NULL,
    ingestion_time TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(symbols, endpoint, calculation_type, range_start, range_end, window_size)
);

-- Create indexes for analytics data
CREATE INDEX IF NOT EXISTS idx_alpha_analytics_symbols ON alpha_analytics_data(symbols);
CREATE INDEX IF NOT EXISTS idx_alpha_analytics_calc ON alpha_analytics_data(calculation_type);
CREATE INDEX IF NOT EXISTS idx_alpha_analytics_epoch ON alpha_analytics_data(ingestion_epoch);

-- ==========================================
-- INGESTION LOGS & MONITORING
-- ==========================================

CREATE TABLE IF NOT EXISTS alpha_ingestion_logs (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20),
    endpoint VARCHAR(100) NOT NULL,
    api_function VARCHAR(100) NOT NULL,
    epoch INT NOT NULL,
    
    -- Execution details
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_seconds DECIMAL(10, 3),
    status VARCHAR(20) NOT NULL, -- success, failure, partial, timeout
    
    -- API response details
    api_response_time_ms INT,
    data_points_count INT,
    error_message TEXT,
    http_status_code INT,
    
    -- Rate limiting info
    rate_limit_remaining INT,
    rate_limit_reset_time TIMESTAMP,
    
    -- Quality metrics
    missing_fields JSONB, -- list of fields that were expected but missing
    data_quality_score DECIMAL(3, 2), -- 0.00 to 1.00
    
    -- Metadata
    ingestion_sequence BIGINT NOT NULL,
    raw_request_params JSONB,
    
    UNIQUE(ticker, endpoint, epoch, started_at)
);

-- Create indexes for ingestion logs
CREATE INDEX IF NOT EXISTS idx_alpha_logs_ticker ON alpha_ingestion_logs(ticker);
CREATE INDEX IF NOT EXISTS idx_alpha_logs_epoch ON alpha_ingestion_logs(epoch);
CREATE INDEX IF NOT EXISTS idx_alpha_logs_status ON alpha_ingestion_logs(status);
CREATE INDEX IF NOT EXISTS idx_alpha_logs_started ON alpha_ingestion_logs(started_at DESC);

-- ==========================================
-- SEQUENCE COUNTER TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS alpha_ingestion_sequence (
    id SERIAL PRIMARY KEY,
    current_sequence BIGINT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Insert initial sequence value
INSERT INTO alpha_ingestion_sequence (current_sequence) 
SELECT 0 WHERE NOT EXISTS (SELECT 1 FROM alpha_ingestion_sequence);

-- Function to get next sequence number
CREATE OR REPLACE FUNCTION get_next_alpha_sequence()
RETURNS BIGINT AS $$
DECLARE
    next_seq BIGINT;
BEGIN
    UPDATE alpha_ingestion_sequence 
    SET current_sequence = current_sequence + 1,
        last_updated = NOW()
    RETURNING current_sequence INTO next_seq;
    
    RETURN next_seq;
END;
$$ LANGUAGE plpgsql;

-- ==========================================
-- HELPER FUNCTIONS
-- ==========================================

-- Function to get ingestion progress for a ticker
CREATE OR REPLACE FUNCTION get_alpha_ingestion_progress(ticker_symbol VARCHAR(20))
RETURNS TABLE(
    ticker VARCHAR(20),
    last_endpoint VARCHAR(100),
    epoch INT,
    progress_pct DECIMAL(5,2),
    status VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.ticker,
        p.last_completed_endpoint,
        p.epoch,
        CASE 
            WHEN p.total_endpoints > 0 THEN 
                (p.completed_endpoints::DECIMAL / p.total_endpoints * 100)
            ELSE 0.00
        END as progress_pct,
        p.status
    FROM alpha_ingestion_progress p
    WHERE p.ticker = ticker_symbol;
END;
$$ LANGUAGE plpgsql;

-- Function to update ingestion progress
CREATE OR REPLACE FUNCTION update_alpha_progress(
    ticker_symbol VARCHAR(20),
    endpoint_name VARCHAR(100),
    function_name VARCHAR(100),
    epoch_num INT,
    total_eps INT DEFAULT NULL,
    completed_eps INT DEFAULT NULL,
    current_status VARCHAR(20) DEFAULT 'in_progress'
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO alpha_ingestion_progress (
        ticker, 
        last_completed_endpoint, 
        last_completed_function,
        epoch, 
        total_endpoints,
        completed_endpoints,
        status,
        updated_at
    )
    VALUES (
        ticker_symbol, 
        endpoint_name, 
        function_name,
        epoch_num, 
        COALESCE(total_eps, 0),
        COALESCE(completed_eps, 0),
        current_status,
        NOW()
    )
    ON CONFLICT (ticker) 
    DO UPDATE SET
        last_completed_endpoint = EXCLUDED.last_completed_endpoint,
        last_completed_function = EXCLUDED.last_completed_function,
        epoch = EXCLUDED.epoch,
        total_endpoints = COALESCE(EXCLUDED.total_endpoints, alpha_ingestion_progress.total_endpoints),
        completed_endpoints = COALESCE(EXCLUDED.completed_endpoints, alpha_ingestion_progress.completed_endpoints),
        status = EXCLUDED.status,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Create view for ingestion monitoring
CREATE OR REPLACE VIEW alpha_ingestion_overview AS
SELECT 
    p.epoch,
    p.ticker,
    p.status,
    CASE 
        WHEN p.total_endpoints > 0 THEN 
            ROUND((p.completed_endpoints::DECIMAL / p.total_endpoints * 100), 2)
        ELSE 0.00
    END as progress_percentage,
    p.completed_endpoints,
    p.total_endpoints,
    p.last_completed_endpoint,
    p.started_at,
    p.updated_at,
    EXTRACT(EPOCH FROM (NOW() - p.started_at))/60 as runtime_minutes
FROM alpha_ingestion_progress p
ORDER BY p.epoch, p.ticker;

-- Grant permissions (adjust as needed for your user)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO urisk_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO urisk_user;
-- GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO urisk_user;
