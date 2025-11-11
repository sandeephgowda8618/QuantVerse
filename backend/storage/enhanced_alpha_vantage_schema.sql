-- Enhanced Database Schema for Alpha Vantage Data Integration
-- Supports all Alpha Vantage API endpoints and data types

-- ============= FUNDAMENTAL DATA TABLES =============

-- Company overviews and fundamental data
CREATE TABLE IF NOT EXISTS fundamental_data (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    data JSONB NOT NULL,
    source VARCHAR(30) DEFAULT 'alpha_vantage',
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, data_type, source)
);

-- Earnings data
CREATE TABLE IF NOT EXISTS earnings_data (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    fiscal_date_ending DATE NOT NULL,
    reported_eps FLOAT,
    estimated_eps FLOAT,
    surprise FLOAT,
    surprise_percentage FLOAT,
    source VARCHAR(30) DEFAULT 'alpha_vantage',
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, fiscal_date_ending)
);

-- Dividends data
CREATE TABLE IF NOT EXISTS dividends_data (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    ex_date DATE NOT NULL,
    payment_date DATE,
    record_date DATE,
    declared_date DATE,
    amount FLOAT NOT NULL,
    adjusted_amount FLOAT,
    currency VARCHAR(3) DEFAULT 'USD',
    source VARCHAR(30) DEFAULT 'alpha_vantage',
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, ex_date)
);

-- Stock splits data
CREATE TABLE IF NOT EXISTS splits_data (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    split_date DATE NOT NULL,
    split_factor VARCHAR(20) NOT NULL,
    split_ratio FLOAT NOT NULL,
    source VARCHAR(30) DEFAULT 'alpha_vantage',
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, split_date)
);

-- ============= FOREX DATA TABLES =============

-- Forex prices
CREATE TABLE IF NOT EXISTS forex_prices (
    id SERIAL PRIMARY KEY,
    pair VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    source VARCHAR(30) DEFAULT 'alpha_vantage',
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(pair, timestamp)
);

-- ============= CRYPTOCURRENCY DATA TABLES =============

-- Crypto prices
CREATE TABLE IF NOT EXISTS crypto_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume FLOAT,
    market_cap FLOAT,
    source VARCHAR(30) DEFAULT 'alpha_vantage',
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, timestamp)
);

-- ============= COMMODITIES DATA TABLES =============

-- Commodities prices
CREATE TABLE IF NOT EXISTS commodities_prices (
    id SERIAL PRIMARY KEY,
    commodity VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    price FLOAT NOT NULL,
    unit VARCHAR(20),
    interval VARCHAR(20) DEFAULT 'daily',
    source VARCHAR(30) DEFAULT 'alpha_vantage',
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(commodity, timestamp)
);

-- ============= ECONOMIC INDICATORS TABLES =============

-- Economic indicators
CREATE TABLE IF NOT EXISTS economic_indicators (
    id SERIAL PRIMARY KEY,
    indicator VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(20),
    frequency VARCHAR(20),
    source VARCHAR(30) DEFAULT 'alpha_vantage',
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(indicator, date)
);

-- ============= TECHNICAL INDICATORS TABLES =============

-- Technical indicators
CREATE TABLE IF NOT EXISTS technical_indicators (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    indicator VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    value FLOAT,
    additional_data JSONB,
    time_period INTEGER,
    source VARCHAR(30) DEFAULT 'alpha_vantage',
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, indicator, timestamp, time_period)
);

-- ============= OPTIONS DATA TABLES =============

-- Options data (for premium users)
CREATE TABLE IF NOT EXISTS options_data (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    option_type VARCHAR(4) CHECK (option_type IN ('call', 'put')),
    expiration_date DATE NOT NULL,
    strike_price FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    bid FLOAT,
    ask FLOAT,
    last_price FLOAT,
    volume INTEGER,
    open_interest INTEGER,
    implied_volatility FLOAT,
    delta FLOAT,
    gamma FLOAT,
    theta FLOAT,
    vega FLOAT,
    source VARCHAR(30) DEFAULT 'alpha_vantage',
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, option_type, expiration_date, strike_price, timestamp)
);

-- ============= MARKET ANALYTICS TABLES =============

-- Top gainers and losers
CREATE TABLE IF NOT EXISTS market_movers (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    company_name TEXT,
    price FLOAT,
    change_amount FLOAT,
    change_percentage VARCHAR(10),
    volume BIGINT,
    mover_type VARCHAR(10) CHECK (mover_type IN ('gainer', 'loser', 'active')),
    date DATE NOT NULL,
    source VARCHAR(30) DEFAULT 'alpha_vantage',
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, mover_type, date)
);

-- Insider transactions
CREATE TABLE IF NOT EXISTS insider_transactions (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    insider_name TEXT,
    transaction_date DATE,
    transaction_type VARCHAR(50),
    shares_traded BIGINT,
    price_per_share FLOAT,
    total_value FLOAT,
    shares_owned_after BIGINT,
    source VARCHAR(30) DEFAULT 'alpha_vantage',
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============= ENHANCED NEWS AND SENTIMENT =============

-- Enhanced news headlines with Alpha Vantage data
ALTER TABLE news_headlines ADD COLUMN IF NOT EXISTS category VARCHAR(50);
ALTER TABLE news_headlines ADD COLUMN IF NOT EXISTS topics TEXT[];
ALTER TABLE news_headlines ADD COLUMN IF NOT EXISTS relevance_score FLOAT;
ALTER TABLE news_headlines ADD COLUMN IF NOT EXISTS overall_sentiment_score FLOAT;
ALTER TABLE news_headlines ADD COLUMN IF NOT EXISTS overall_sentiment_label VARCHAR(20);

-- Ticker-specific sentiment scores
CREATE TABLE IF NOT EXISTS ticker_sentiment (
    id SERIAL PRIMARY KEY,
    headline_id INTEGER REFERENCES news_headlines(id),
    ticker VARCHAR(20) NOT NULL,
    relevance_score FLOAT,
    sentiment_score FLOAT,
    sentiment_label VARCHAR(20),
    source VARCHAR(30) DEFAULT 'alpha_vantage',
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(headline_id, ticker)
);

-- ============= IPO AND EARNINGS CALENDAR =============

-- IPO calendar
CREATE TABLE IF NOT EXISTS ipo_calendar (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20),
    company_name TEXT NOT NULL,
    ipo_date DATE NOT NULL,
    price_range_low FLOAT,
    price_range_high FLOAT,
    shares_offered BIGINT,
    exchange VARCHAR(50),
    source VARCHAR(30) DEFAULT 'alpha_vantage',
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, ipo_date) WHERE ticker IS NOT NULL
);

-- Earnings calendar
CREATE TABLE IF NOT EXISTS earnings_calendar (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    company_name TEXT,
    report_date DATE NOT NULL,
    fiscal_date_ending DATE,
    estimate FLOAT,
    currency VARCHAR(3) DEFAULT 'USD',
    source VARCHAR(30) DEFAULT 'alpha_vantage',
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, report_date)
);

-- ============= LISTING STATUS =============

-- Stock listing and delisting status
CREATE TABLE IF NOT EXISTS listing_status (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    company_name TEXT,
    exchange VARCHAR(50),
    asset_type VARCHAR(50),
    ipo_date DATE,
    delisting_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    source VARCHAR(30) DEFAULT 'alpha_vantage',
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, exchange)
);

-- ============= INDEXES FOR PERFORMANCE =============

-- Fundamental data indexes
CREATE INDEX IF NOT EXISTS idx_fundamental_data_ticker ON fundamental_data(ticker);
CREATE INDEX IF NOT EXISTS idx_fundamental_data_type ON fundamental_data(data_type);
CREATE INDEX IF NOT EXISTS idx_fundamental_data_updated ON fundamental_data(updated_at DESC);

-- Earnings data indexes
CREATE INDEX IF NOT EXISTS idx_earnings_data_ticker ON earnings_data(ticker);
CREATE INDEX IF NOT EXISTS idx_earnings_data_date ON earnings_data(fiscal_date_ending DESC);

-- Forex indexes
CREATE INDEX IF NOT EXISTS idx_forex_prices_pair ON forex_prices(pair);
CREATE INDEX IF NOT EXISTS idx_forex_prices_timestamp ON forex_prices(timestamp DESC);

-- Crypto indexes
CREATE INDEX IF NOT EXISTS idx_crypto_prices_symbol ON crypto_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_crypto_prices_timestamp ON crypto_prices(timestamp DESC);

-- Commodities indexes
CREATE INDEX IF NOT EXISTS idx_commodities_prices_commodity ON commodities_prices(commodity);
CREATE INDEX IF NOT EXISTS idx_commodities_prices_timestamp ON commodities_prices(timestamp DESC);

-- Economic indicators indexes
CREATE INDEX IF NOT EXISTS idx_economic_indicators_indicator ON economic_indicators(indicator);
CREATE INDEX IF NOT EXISTS idx_economic_indicators_date ON economic_indicators(date DESC);

-- Technical indicators indexes
CREATE INDEX IF NOT EXISTS idx_technical_indicators_ticker ON technical_indicators(ticker);
CREATE INDEX IF NOT EXISTS idx_technical_indicators_indicator ON technical_indicators(indicator);
CREATE INDEX IF NOT EXISTS idx_technical_indicators_timestamp ON technical_indicators(timestamp DESC);

-- Options data indexes
CREATE INDEX IF NOT EXISTS idx_options_data_ticker ON options_data(ticker);
CREATE INDEX IF NOT EXISTS idx_options_data_expiration ON options_data(expiration_date);
CREATE INDEX IF NOT EXISTS idx_options_data_timestamp ON options_data(timestamp DESC);

-- Market movers indexes
CREATE INDEX IF NOT EXISTS idx_market_movers_ticker ON market_movers(ticker);
CREATE INDEX IF NOT EXISTS idx_market_movers_type ON market_movers(mover_type);
CREATE INDEX IF NOT EXISTS idx_market_movers_date ON market_movers(date DESC);

-- Ticker sentiment indexes
CREATE INDEX IF NOT EXISTS idx_ticker_sentiment_ticker ON ticker_sentiment(ticker);
CREATE INDEX IF NOT EXISTS idx_ticker_sentiment_headline ON ticker_sentiment(headline_id);

-- Calendar indexes
CREATE INDEX IF NOT EXISTS idx_ipo_calendar_date ON ipo_calendar(ipo_date DESC);
CREATE INDEX IF NOT EXISTS idx_ipo_calendar_ticker ON ipo_calendar(ticker) WHERE ticker IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_earnings_calendar_ticker ON earnings_calendar(ticker);
CREATE INDEX IF NOT EXISTS idx_earnings_calendar_date ON earnings_calendar(report_date DESC);

-- Listing status indexes
CREATE INDEX IF NOT EXISTS idx_listing_status_ticker ON listing_status(ticker);
CREATE INDEX IF NOT EXISTS idx_listing_status_exchange ON listing_status(exchange);
CREATE INDEX IF NOT EXISTS idx_listing_status_status ON listing_status(status);

-- ============= UTILITY VIEWS =============

-- Latest forex rates view
CREATE OR REPLACE VIEW latest_forex_rates AS
WITH latest_dates AS (
    SELECT pair, MAX(timestamp) as latest_timestamp
    FROM forex_prices
    GROUP BY pair
)
SELECT 
    f.pair,
    f.timestamp,
    f.close as rate,
    f.open,
    f.high,
    f.low,
    f.volume
FROM forex_prices f
JOIN latest_dates ld ON f.pair = ld.pair AND f.timestamp = ld.latest_timestamp;

-- Latest crypto prices view
CREATE OR REPLACE VIEW latest_crypto_prices AS
WITH latest_dates AS (
    SELECT symbol, MAX(timestamp) as latest_timestamp
    FROM crypto_prices
    GROUP BY symbol
)
SELECT 
    c.symbol,
    c.timestamp,
    c.close as price,
    c.volume,
    c.market_cap,
    c.open,
    c.high,
    c.low
FROM crypto_prices c
JOIN latest_dates ld ON c.symbol = ld.symbol AND c.timestamp = ld.latest_timestamp;

-- Latest commodities prices view
CREATE OR REPLACE VIEW latest_commodities_prices AS
WITH latest_dates AS (
    SELECT commodity, MAX(timestamp) as latest_timestamp
    FROM commodities_prices
    GROUP BY commodity
)
SELECT 
    cp.commodity,
    cp.timestamp,
    cp.price,
    cp.unit
FROM commodities_prices cp
JOIN latest_dates ld ON cp.commodity = ld.commodity AND cp.timestamp = ld.latest_timestamp;

-- Economic indicators summary view
CREATE OR REPLACE VIEW economic_indicators_summary AS
WITH latest_values AS (
    SELECT 
        indicator,
        MAX(date) as latest_date
    FROM economic_indicators
    GROUP BY indicator
)
SELECT 
    ei.indicator,
    ei.date as latest_date,
    ei.value as latest_value,
    ei.unit,
    ei.frequency
FROM economic_indicators ei
JOIN latest_values lv ON ei.indicator = lv.indicator AND ei.date = lv.latest_date;

-- Company overview summary (from fundamental data)
CREATE OR REPLACE VIEW company_overviews AS
SELECT 
    ticker,
    data->>'Name' as company_name,
    data->>'Sector' as sector,
    data->>'Industry' as industry,
    data->>'MarketCapitalization' as market_cap,
    data->>'PERatio' as pe_ratio,
    data->>'EPS' as eps,
    data->>'RevenueTTM' as revenue_ttm,
    data->>'ProfitMargin' as profit_margin,
    data->>'Country' as country,
    data->>'Exchange' as exchange,
    updated_at
FROM fundamental_data
WHERE data_type = 'company_overview';

-- ============= DATA QUALITY FUNCTIONS =============

-- Function to calculate forex rate change
CREATE OR REPLACE FUNCTION calculate_forex_change(pair_name VARCHAR(10), days_back INTEGER DEFAULT 1)
RETURNS TABLE(
    pair VARCHAR(10),
    current_rate FLOAT,
    previous_rate FLOAT,
    change_amount FLOAT,
    change_percentage FLOAT
) AS $$
BEGIN
    RETURN QUERY
    WITH current_rate AS (
        SELECT f.pair, f.close
        FROM forex_prices f
        WHERE f.pair = pair_name
        ORDER BY f.timestamp DESC
        LIMIT 1
    ),
    previous_rate AS (
        SELECT f.pair, f.close
        FROM forex_prices f
        WHERE f.pair = pair_name
          AND f.timestamp <= NOW() - INTERVAL '1 day' * days_back
        ORDER BY f.timestamp DESC
        LIMIT 1
    )
    SELECT 
        pair_name,
        cr.close,
        pr.close,
        cr.close - pr.close,
        CASE 
            WHEN pr.close > 0 THEN ((cr.close - pr.close) / pr.close) * 100
            ELSE NULL
        END
    FROM current_rate cr
    CROSS JOIN previous_rate pr;
END;
$$ LANGUAGE plpgsql;

-- Function to get latest technical indicator value
CREATE OR REPLACE FUNCTION get_latest_indicator(ticker_symbol VARCHAR(20), indicator_name VARCHAR(50))
RETURNS TABLE(
    ticker VARCHAR(20),
    indicator VARCHAR(50),
    timestamp TIMESTAMP,
    value FLOAT,
    additional_data JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ti.ticker, 
        ti.indicator, 
        ti.timestamp, 
        ti.value, 
        ti.additional_data
    FROM technical_indicators ti
    WHERE ti.ticker = ticker_symbol 
      AND ti.indicator = indicator_name
    ORDER BY ti.timestamp DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- ============= DATA CLEANUP PROCEDURES =============

-- Procedure to clean old data
CREATE OR REPLACE FUNCTION cleanup_old_data(days_to_keep INTEGER DEFAULT 365)
RETURNS VOID AS $$
BEGIN
    -- Clean old market prices (keep 1 year by default)
    DELETE FROM market_prices 
    WHERE timestamp < NOW() - INTERVAL '1 day' * days_to_keep;
    
    -- Clean old forex prices
    DELETE FROM forex_prices 
    WHERE timestamp < NOW() - INTERVAL '1 day' * days_to_keep;
    
    -- Clean old crypto prices
    DELETE FROM crypto_prices 
    WHERE timestamp < NOW() - INTERVAL '1 day' * days_to_keep;
    
    -- Clean old technical indicators
    DELETE FROM technical_indicators 
    WHERE timestamp < NOW() - INTERVAL '1 day' * days_to_keep;
    
    -- Clean old news (keep 6 months)
    DELETE FROM news_headlines 
    WHERE published_at < NOW() - INTERVAL '6 months';
    
    RAISE NOTICE 'Data cleanup completed. Kept data from last % days.', days_to_keep;
END;
$$ LANGUAGE plpgsql;

-- ============= GRANT PERMISSIONS =============

-- Grant permissions for application user (if needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO urisk_app;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO urisk_app;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO urisk_app;
