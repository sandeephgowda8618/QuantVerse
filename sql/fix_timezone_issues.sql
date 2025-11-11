-- Fix timestamp columns to be timezone-aware
-- This prevents offset-naive vs offset-aware comparison issues

-- Update alpha_vantage_data timestamp column to TIMESTAMPTZ
ALTER TABLE alpha_vantage_data 
ALTER COLUMN timestamp TYPE TIMESTAMPTZ 
USING timestamp AT TIME ZONE 'UTC';

-- Update vector_sync_state table  
ALTER TABLE vector_sync_state
ALTER COLUMN last_synced_at TYPE TIMESTAMPTZ
USING last_synced_at AT TIME ZONE 'UTC';

ALTER TABLE vector_sync_state
ALTER COLUMN created_at TYPE TIMESTAMPTZ
USING created_at AT TIME ZONE 'UTC';

ALTER TABLE vector_sync_state
ALTER COLUMN updated_at TYPE TIMESTAMPTZ
USING updated_at AT TIME ZONE 'UTC';

-- Update other tables that may have timestamp issues
ALTER TABLE news_headlines 
ALTER COLUMN published_at TYPE TIMESTAMPTZ
USING published_at AT TIME ZONE 'UTC';

ALTER TABLE anomalies
ALTER COLUMN timestamp TYPE TIMESTAMPTZ  
USING timestamp AT TIME ZONE 'UTC';

ALTER TABLE market_prices
ALTER COLUMN timestamp TYPE TIMESTAMPTZ
USING timestamp AT TIME ZONE 'UTC';

-- Set default timezone for new connections
ALTER DATABASE urisk_core SET timezone TO 'UTC';

-- Create helper function to ensure UTC timestamps
CREATE OR REPLACE FUNCTION ensure_utc_timestamp(input_ts TIMESTAMP)
RETURNS TIMESTAMPTZ AS $$
BEGIN
    IF input_ts IS NULL THEN
        RETURN NULL;
    END IF;
    
    -- Convert to UTC if no timezone info
    RETURN input_ts AT TIME ZONE 'UTC';
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION ensure_utc_timestamp(TIMESTAMP) IS 'Converts naive timestamp to UTC timezone-aware timestamp';
