-- Alpha Vantage Database Performance Optimization
-- Run these commands to optimize the database for Alpha Vantage ingestion

-- ==========================================
-- STEP 1: ENHANCED INDEXING STRATEGY
-- ==========================================

-- Drop existing indexes if they exist (to recreate optimally)
DROP INDEX IF EXISTS idx_alpha_market_ticker;
DROP INDEX IF EXISTS idx_alpha_market_timestamp;
DROP INDEX IF EXISTS idx_alpha_market_endpoint;

-- Create optimized compound indexes for common query patterns
-- Ticker + Time queries (most common pattern)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alpha_market_ticker_time_desc 
ON alpha_market_data(ticker, timestamp DESC);

-- Ticker + Time + Endpoint for specific endpoint queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alpha_market_ticker_time_endpoint 
ON alpha_market_data(ticker, timestamp DESC, endpoint);

-- Covering index for price queries (avoid table lookups)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alpha_market_price_summary
ON alpha_market_data(ticker, timestamp DESC) 
INCLUDE (open_price, high_price, low_price, close_price, volume, quality_flag);

-- Partial index for recent data (90 days) - faster for real-time queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alpha_market_recent_90d
ON alpha_market_data(ticker, timestamp DESC, close_price, volume) 
WHERE timestamp > (NOW() - INTERVAL '90 days');

-- Ingestion epoch index for batch operations
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alpha_market_epoch_sequence 
ON alpha_market_data(ingestion_epoch, ingestion_sequence);

-- ==========================================
-- FUNDAMENTAL DATA INDEXES
-- ==========================================

-- Enhanced fundamental data indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alpha_fund_ticker_type_date 
ON alpha_fundamental_data(ticker, data_type, fiscal_date_ending DESC);

-- JSONB GIN index for financial data searches
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alpha_fund_financial_data_gin 
ON alpha_fundamental_data USING gin (financial_data);

-- Specific indexes for common financial metrics
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alpha_fund_market_cap 
ON alpha_fundamental_data((financial_data->>'MarketCap')) 
WHERE data_type = 'overview';

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alpha_fund_pe_ratio 
ON alpha_fundamental_data((financial_data->>'PERatio')) 
WHERE data_type = 'overview';

-- ==========================================
-- TECHNICAL INDICATORS INDEXES
-- ==========================================

-- Technical indicators optimized indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alpha_tech_ticker_indicator_time 
ON alpha_technical_indicators(ticker, indicator_name, timestamp DESC);

-- Covering index for indicator values
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alpha_tech_values 
ON alpha_technical_indicators(ticker, indicator_name, timestamp DESC) 
INCLUDE (value_1, value_2, value_3);

-- ==========================================
-- NEWS & INTELLIGENCE INDEXES
-- ==========================================

-- News intelligence optimized indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alpha_news_ticker_published 
ON alpha_news_intelligence(ticker, published_at DESC);

-- Sentiment analysis indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alpha_news_sentiment_score 
ON alpha_news_intelligence(ticker, overall_sentiment_score) 
WHERE overall_sentiment_score IS NOT NULL;

-- URL uniqueness for deduplication
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_alpha_news_url_unique 
ON alpha_news_intelligence(url, published_at);

-- ==========================================
-- INGESTION PROGRESS INDEXES
-- ==========================================

-- Progress tracking indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alpha_progress_status_ticker 
ON alpha_ingestion_progress(status, ticker);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alpha_progress_updated_at 
ON alpha_ingestion_progress(updated_at DESC);

-- ==========================================
-- STEP 2: TABLE OPTIMIZATION
-- ==========================================

-- Set storage parameters for large tables
ALTER TABLE alpha_market_data SET (fillfactor = 85);
ALTER TABLE alpha_fundamental_data SET (fillfactor = 90);
ALTER TABLE alpha_technical_indicators SET (fillfactor = 85);

-- Enable compression for JSONB columns
ALTER TABLE alpha_market_data ALTER COLUMN raw_payload SET STORAGE EXTENDED;
ALTER TABLE alpha_market_data ALTER COLUMN parsed_values SET STORAGE EXTENDED;
ALTER TABLE alpha_fundamental_data ALTER COLUMN financial_data SET STORAGE EXTENDED;
ALTER TABLE alpha_fundamental_data ALTER COLUMN raw_payload SET STORAGE EXTENDED;

-- ==========================================
-- STEP 3: PERFORMANCE FUNCTIONS
-- ==========================================

-- Function to analyze table bloat
CREATE OR REPLACE FUNCTION analyze_table_bloat()
RETURNS TABLE(
    table_name text,
    table_size text,
    bloat_pct numeric,
    recommendation text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        schemaname||'.'||tablename as table_name,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size,
        CASE 
            WHEN pg_stat_user_tables.n_dead_tup > 0 
            THEN round((pg_stat_user_tables.n_dead_tup::numeric / (pg_stat_user_tables.n_live_tup + pg_stat_user_tables.n_dead_tup)) * 100, 2)
            ELSE 0 
        END as bloat_pct,
        CASE 
            WHEN pg_stat_user_tables.n_dead_tup::numeric / (pg_stat_user_tables.n_live_tup + pg_stat_user_tables.n_dead_tup) > 0.1 
            THEN 'VACUUM ANALYZE ' || schemaname||'.'||tablename
            ELSE 'No action needed'
        END as recommendation
    FROM pg_stat_user_tables 
    WHERE tablename LIKE 'alpha_%'
    ORDER BY bloat_pct DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get ingestion statistics
CREATE OR REPLACE FUNCTION get_ingestion_stats()
RETURNS TABLE(
    table_name text,
    total_records bigint,
    records_today bigint,
    avg_records_per_hour numeric,
    last_insert timestamp
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'alpha_market_data' as table_name,
        COUNT(*) as total_records,
        COUNT(*) FILTER (WHERE ingestion_time::date = CURRENT_DATE) as records_today,
        CASE 
            WHEN COUNT(*) FILTER (WHERE ingestion_time > NOW() - INTERVAL '1 hour') > 0
            THEN COUNT(*) FILTER (WHERE ingestion_time > NOW() - INTERVAL '1 hour')
            ELSE 0
        END as avg_records_per_hour,
        MAX(ingestion_time) as last_insert
    FROM alpha_market_data
    
    UNION ALL
    
    SELECT 
        'alpha_fundamental_data' as table_name,
        COUNT(*) as total_records,
        COUNT(*) FILTER (WHERE ingestion_time::date = CURRENT_DATE) as records_today,
        CASE 
            WHEN COUNT(*) FILTER (WHERE ingestion_time > NOW() - INTERVAL '1 hour') > 0
            THEN COUNT(*) FILTER (WHERE ingestion_time > NOW() - INTERVAL '1 hour')
            ELSE 0
        END as avg_records_per_hour,
        MAX(ingestion_time) as last_insert
    FROM alpha_fundamental_data
    
    UNION ALL
    
    SELECT 
        'alpha_technical_indicators' as table_name,
        COUNT(*) as total_records,
        COUNT(*) FILTER (WHERE ingestion_time::date = CURRENT_DATE) as records_today,
        CASE 
            WHEN COUNT(*) FILTER (WHERE ingestion_time > NOW() - INTERVAL '1 hour') > 0
            THEN COUNT(*) FILTER (WHERE ingestion_time > NOW() - INTERVAL '1 hour')
            ELSE 0
        END as avg_records_per_hour,
        MAX(ingestion_time) as last_insert
    FROM alpha_technical_indicators;
END;
$$ LANGUAGE plpgsql;

-- ==========================================
-- STEP 4: MAINTENANCE PROCEDURES
-- ==========================================

-- Auto-vacuum settings for Alpha Vantage tables
ALTER TABLE alpha_market_data SET (
    autovacuum_vacuum_scale_factor = 0.05,  -- More frequent vacuuming
    autovacuum_analyze_scale_factor = 0.02, -- More frequent analyzing
    autovacuum_vacuum_cost_delay = 10       -- Faster vacuum
);

ALTER TABLE alpha_fundamental_data SET (
    autovacuum_vacuum_scale_factor = 0.1,   -- Less frequent (slower growth)
    autovacuum_analyze_scale_factor = 0.05,
    autovacuum_vacuum_cost_delay = 20
);

-- ==========================================
-- STEP 5: QUERY OPTIMIZATION VIEWS
-- ==========================================

-- View for latest market data per ticker
CREATE OR REPLACE VIEW latest_market_data AS
SELECT DISTINCT ON (ticker) 
    ticker,
    timestamp,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
    quality_flag
FROM alpha_market_data 
WHERE api_function = 'GLOBAL_QUOTE'
ORDER BY ticker, timestamp DESC;

-- View for recent fundamental overview
CREATE OR REPLACE VIEW latest_company_overview AS
SELECT DISTINCT ON (ticker)
    ticker,
    financial_data->>'Name' as company_name,
    (financial_data->>'MarketCapitalization')::numeric as market_cap,
    (financial_data->>'PERatio')::numeric as pe_ratio,
    (financial_data->>'DividendYield')::numeric as dividend_yield,
    fiscal_date_ending,
    ingestion_time
FROM alpha_fundamental_data 
WHERE data_type = 'overview'
ORDER BY ticker, ingestion_time DESC;

-- ==========================================
-- STEP 6: PERFORMANCE MONITORING
-- ==========================================

-- Create monitoring table for query performance
CREATE TABLE IF NOT EXISTS query_performance_log (
    id SERIAL PRIMARY KEY,
    query_name VARCHAR(100),
    execution_time_ms NUMERIC,
    rows_affected BIGINT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Function to log slow queries
CREATE OR REPLACE FUNCTION log_slow_query(
    query_name TEXT,
    execution_time_ms NUMERIC,
    rows_affected BIGINT DEFAULT NULL
)
RETURNS void AS $$
BEGIN
    INSERT INTO query_performance_log (query_name, execution_time_ms, rows_affected)
    VALUES (query_name, execution_time_ms, rows_affected);
END;
$$ LANGUAGE plpgsql;

-- ==========================================
-- STEP 7: CLEANUP AND ANALYZE
-- ==========================================

-- Analyze all Alpha Vantage tables to update statistics
ANALYZE alpha_market_data;
ANALYZE alpha_fundamental_data;
ANALYZE alpha_technical_indicators;
ANALYZE alpha_news_intelligence;
ANALYZE alpha_ingestion_progress;

-- Vacuum if needed (check bloat first)
-- VACUUM ANALYZE alpha_market_data;

-- ==========================================
-- VERIFICATION QUERIES
-- ==========================================

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE tablename LIKE 'alpha_%'
ORDER BY idx_scan DESC;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as data_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables 
WHERE tablename LIKE 'alpha_%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Success message
SELECT 'Alpha Vantage database optimization completed successfully!' as status;
