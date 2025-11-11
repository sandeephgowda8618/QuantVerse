-- PostgreSQL to ChromaDB Sync State Table
-- Tracks incremental sync progress for each data source

CREATE TABLE IF NOT EXISTS vector_sync_state (
    table_name VARCHAR(100) PRIMARY KEY,
    last_synced_at TIMESTAMP,
    records_synced BIGINT DEFAULT 0,
    last_chunk_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_vector_sync_last_synced 
ON vector_sync_state(last_synced_at);

CREATE INDEX IF NOT EXISTS idx_vector_sync_updated 
ON vector_sync_state(updated_at);

-- Insert initial states for known tables
INSERT INTO vector_sync_state (table_name, last_synced_at, records_synced) 
VALUES 
    ('alpha_vantage_data', '2020-01-01 00:00:00', 0),
    ('news_headlines', '2020-01-01 00:00:00', 0),
    ('news_sentiment', '2020-01-01 00:00:00', 0),
    ('anomalies', '2020-01-01 00:00:00', 0),
    ('market_prices', '2020-01-01 00:00:00', 0)
ON CONFLICT (table_name) DO NOTHING;

-- Function to update sync state
CREATE OR REPLACE FUNCTION update_vector_sync_state(
    p_table_name VARCHAR(100),
    p_last_synced_at TIMESTAMP,
    p_records_synced BIGINT,
    p_last_chunk_id VARCHAR(255) DEFAULT NULL
) RETURNS void AS $$
BEGIN
    INSERT INTO vector_sync_state (
        table_name, 
        last_synced_at, 
        records_synced, 
        last_chunk_id, 
        updated_at
    )
    VALUES (
        p_table_name, 
        p_last_synced_at, 
        p_records_synced, 
        p_last_chunk_id, 
        NOW()
    )
    ON CONFLICT (table_name) 
    DO UPDATE SET 
        last_synced_at = EXCLUDED.last_synced_at,
        records_synced = EXCLUDED.records_synced,
        last_chunk_id = EXCLUDED.last_chunk_id,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- View for monitoring sync progress
CREATE OR REPLACE VIEW vector_sync_progress AS
SELECT 
    table_name,
    last_synced_at,
    records_synced,
    EXTRACT(EPOCH FROM (NOW() - last_synced_at)) / 3600 AS hours_since_sync,
    CASE 
        WHEN last_synced_at > NOW() - INTERVAL '1 hour' THEN 'CURRENT'
        WHEN last_synced_at > NOW() - INTERVAL '24 hours' THEN 'RECENT' 
        WHEN last_synced_at > NOW() - INTERVAL '7 days' THEN 'STALE'
        ELSE 'VERY_STALE'
    END AS sync_status,
    updated_at
FROM vector_sync_state
ORDER BY last_synced_at DESC;

COMMENT ON TABLE vector_sync_state IS 'Tracks incremental sync state for PostgreSQL to ChromaDB pipeline';
COMMENT ON VIEW vector_sync_progress IS 'Monitoring view for sync progress and staleness';
