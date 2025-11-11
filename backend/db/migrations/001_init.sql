-- uRISK Database Initialization Script
-- Creates all core tables for the Unified Risk Intelligence & Surveillance Kernel

-- Enable UUID extension for unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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

-- Create index for efficient time-based queries
CREATE INDEX idx_market_prices_ticker_timestamp ON market_prices(ticker, timestamp DESC);
CREATE INDEX idx_market_prices_timestamp ON market_prices(timestamp DESC);

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

-- Create index for news queries
CREATE INDEX idx_news_headlines_ticker ON news_headlines(ticker);
CREATE INDEX idx_news_headlines_source ON news_headlines(source);
CREATE INDEX idx_news_headlines_published_at ON news_headlines(published_at DESC);

-- SENTIMENT RESULTS
CREATE TABLE news_sentiment (
    id SERIAL PRIMARY KEY,
    headline_id INT REFERENCES news_headlines(id),
    sentiment_score FLOAT,              -- -1 to +1
    sentiment_label VARCHAR(10),        -- positive, negative, neutral
    confidence FLOAT,
    model_version VARCHAR(20),
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create index for sentiment queries
CREATE INDEX idx_news_sentiment_headline_id ON news_sentiment(headline_id);
CREATE INDEX idx_news_sentiment_score ON news_sentiment(sentiment_score);

-- REGULATORY / MACRO EVENTS
CREATE TABLE regulatory_events (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20),
    title TEXT,
    body TEXT,
    source VARCHAR(30),                 -- sec, rbi, fed
    severity VARCHAR(10),               -- low, medium, high
    event_type VARCHAR(30),             -- rate, inflation, enforcement, etc
    published_at TIMESTAMP,
    inserted_at TIMESTAMP DEFAULT NOW()
);

-- Create index for regulatory events
CREATE INDEX idx_regulatory_events_ticker ON regulatory_events(ticker);
CREATE INDEX idx_regulatory_events_source ON regulatory_events(source);
CREATE INDEX idx_regulatory_events_severity ON regulatory_events(severity);
CREATE INDEX idx_regulatory_events_published_at ON regulatory_events(published_at DESC);

-- INFRA OUTAGES
CREATE TABLE infra_incidents (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50),              -- coinbase, binance, solana
    incident_type VARCHAR(50),          -- outage, maintenance, congestion
    description TEXT,
    severity VARCHAR(10),               -- low, medium, high, critical
    started_at TIMESTAMP,
    resolved_at TIMESTAMP,
    source VARCHAR(30)
);

-- Create index for infra incidents
CREATE INDEX idx_infra_incidents_platform ON infra_incidents(platform);
CREATE INDEX idx_infra_incidents_severity ON infra_incidents(severity);
CREATE INDEX idx_infra_incidents_started_at ON infra_incidents(started_at DESC);

-- ML ANOMALIES
CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20),
    metric VARCHAR(50),                  -- volume / liquidity / volatility / call_skew / iv_spike
    anomaly_score FLOAT,                 -- 0 to 1
    severity VARCHAR(10),                -- low, medium, high
    explanation TEXT,
    timestamp TIMESTAMP,
    detected_at TIMESTAMP DEFAULT NOW()
);

-- Create index for anomaly queries
CREATE INDEX idx_anomalies_ticker ON anomalies(ticker);
CREATE INDEX idx_anomalies_metric ON anomalies(metric);
CREATE INDEX idx_anomalies_severity ON anomalies(severity);
CREATE INDEX idx_anomalies_timestamp ON anomalies(timestamp DESC);

-- FORECASTS (VOLATILITY, MACRO EFFECTS)
CREATE TABLE forecasts (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20),
    forecast_window VARCHAR(20),         -- 1h, 4h, 1d, 1w
    predicted_impact VARCHAR(30),        -- bullish, bearish, neutral, volatile
    confidence FLOAT,                    -- 0 to 1
    reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- Create index for forecasts
CREATE INDEX idx_forecasts_ticker ON forecasts(ticker);
CREATE INDEX idx_forecasts_window ON forecasts(forecast_window);
CREATE INDEX idx_forecasts_created_at ON forecasts(created_at DESC);

-- MERGED ALERTS
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20),
    risk_type VARCHAR(30),              -- sentiment, infra, regulatory, anomaly
    severity VARCHAR(10),               -- low, medium, high, critical
    message TEXT,
    triggered_at TIMESTAMP DEFAULT NOW(),
    read BOOLEAN DEFAULT FALSE,
    resolved BOOLEAN DEFAULT FALSE
);

-- Create index for alerts
CREATE INDEX idx_alerts_ticker ON alerts(ticker);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_triggered_at ON alerts(triggered_at DESC);
CREATE INDEX idx_alerts_unread ON alerts(read) WHERE read = FALSE;

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

-- Create index for price gaps
CREATE INDEX idx_price_gaps_ticker ON price_gaps(ticker);
CREATE INDEX idx_price_gaps_date ON price_gaps(date DESC);
CREATE INDEX idx_price_gaps_gap_percent ON price_gaps(gap_percent);

-- Create a view for recent market activity (last 24 hours)
CREATE VIEW recent_market_activity AS
SELECT 
    mp.ticker,
    mp.timestamp,
    mp.close,
    mp.volume,
    a.asset_type,
    a.exchange
FROM market_prices mp
JOIN assets a ON mp.ticker = a.ticker
WHERE mp.timestamp >= NOW() - INTERVAL '24 hours'
ORDER BY mp.timestamp DESC;

-- Create a view for active alerts
CREATE VIEW active_alerts AS
SELECT 
    a.id,
    a.ticker,
    a.risk_type,
    a.severity,
    a.message,
    a.triggered_at,
    ast.asset_type,
    ast.exchange
FROM alerts a
LEFT JOIN assets ast ON a.ticker = ast.ticker
WHERE a.read = FALSE AND a.resolved = FALSE
ORDER BY 
    CASE a.severity
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    a.triggered_at DESC;

-- Function to calculate percentage change
CREATE OR REPLACE FUNCTION calculate_percentage_change(old_value FLOAT, new_value FLOAT)
RETURNS FLOAT AS $$
BEGIN
    IF old_value = 0 OR old_value IS NULL THEN
        RETURN NULL;
    END IF;
    RETURN ((new_value - old_value) / old_value) * 100;
END;
$$ LANGUAGE plpgsql;

-- Function to get latest price for a ticker
CREATE OR REPLACE FUNCTION get_latest_price(ticker_symbol VARCHAR(20))
RETURNS TABLE(
    ticker VARCHAR(20),
    price FLOAT,
    timestamp TIMESTAMP,
    volume BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT mp.ticker, mp.close, mp.timestamp, mp.volume
    FROM market_prices mp
    WHERE mp.ticker = ticker_symbol
    ORDER BY mp.timestamp DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;