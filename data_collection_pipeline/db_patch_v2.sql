-- QuantVerse Database Patch v2.1
-- Fixes schema mismatches and constraint issues

-- 1. Add missing metadata column to ingestion_sessions
ALTER TABLE ingestion_sessions ADD COLUMN IF NOT EXISTS metadata JSONB;

-- 2. Fix status constraint to accept both upper and lowercase
ALTER TABLE ingestion_sessions DROP CONSTRAINT IF EXISTS ingestion_sessions_status_check;
ALTER TABLE ingestion_sessions 
ADD CONSTRAINT ingestion_sessions_status_check 
CHECK (status IN ('RUNNING', 'COMPLETED', 'FAILED', 'running', 'completed', 'failed'));

-- 3. Ensure alpha_ingestion_logs has correct data types
ALTER TABLE alpha_ingestion_logs 
ALTER COLUMN status TYPE VARCHAR(20) USING status::text;

-- Add missing constraint if not exists
ALTER TABLE alpha_ingestion_logs DROP CONSTRAINT IF EXISTS alpha_ingestion_logs_status_check;
ALTER TABLE alpha_ingestion_logs 
ADD CONSTRAINT alpha_ingestion_logs_status_check 
CHECK (status IN ('SUCCESS', 'FAILED', 'RATE_LIMITED', 'success', 'failed', 'rate_limited'));

-- 4. Ensure response_code is properly typed
ALTER TABLE alpha_ingestion_logs 
ALTER COLUMN response_code TYPE INTEGER USING NULLIF(response_code::text, '')::int;

-- 5. Make duration nullable and properly typed
ALTER TABLE alpha_ingestion_logs 
ALTER COLUMN duration TYPE NUMERIC(8,3) USING duration::numeric;

-- 6. Add any missing indexes for performance
CREATE INDEX IF NOT EXISTS idx_alpha_logs_status ON alpha_ingestion_logs(status);
CREATE INDEX IF NOT EXISTS idx_alpha_logs_timestamp_desc ON alpha_ingestion_logs(timestamp DESC);

-- 7. Verify table structure
SELECT 'Database patch v2.1 applied successfully!' as status;

-- Show current table structures for verification
\d ingestion_sessions;
\d alpha_ingestion_logs;
