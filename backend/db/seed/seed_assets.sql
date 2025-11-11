-- Seed data for tracked assets
-- Insert core assets that the system will monitor

-- Insert tracked cryptocurrencies
INSERT INTO assets (ticker, name, asset_type, exchange, sector, country) VALUES
('BTC', 'Bitcoin', 'crypto', 'Multiple', 'Cryptocurrency', 'Global'),
('ETH', 'Ethereum', 'crypto', 'Multiple', 'Cryptocurrency', 'Global'),
('SOL', 'Solana', 'crypto', 'Multiple', 'Cryptocurrency', 'Global'),
('ADA', 'Cardano', 'crypto', 'Multiple', 'Cryptocurrency', 'Global'),
('DOT', 'Polkadot', 'crypto', 'Multiple', 'Cryptocurrency', 'Global')
ON CONFLICT (ticker) DO NOTHING;

-- Insert tracked US stocks
INSERT INTO assets (ticker, name, asset_type, exchange, sector, country) VALUES
('AAPL', 'Apple Inc.', 'stock', 'NASDAQ', 'Technology', 'US'),
('TSLA', 'Tesla Inc.', 'stock', 'NASDAQ', 'Automotive', 'US'),
('MSFT', 'Microsoft Corporation', 'stock', 'NASDAQ', 'Technology', 'US'),
('GOOGL', 'Alphabet Inc.', 'stock', 'NASDAQ', 'Technology', 'US'),
('AMZN', 'Amazon.com Inc.', 'stock', 'NASDAQ', 'E-commerce', 'US'),
('NVDA', 'NVIDIA Corporation', 'stock', 'NASDAQ', 'Technology', 'US')
ON CONFLICT (ticker) DO NOTHING;

-- Insert tracked indices and ETFs
INSERT INTO assets (ticker, name, asset_type, exchange, sector, country) VALUES
('SPY', 'SPDR S&P 500 ETF Trust', 'index', 'NYSE', 'Index Fund', 'US'),
('QQQ', 'Invesco QQQ Trust', 'index', 'NASDAQ', 'Index Fund', 'US'),
('NIFTY', 'Nifty 50', 'index', 'NSE', 'Index', 'India'),
('NASDAQ', 'NASDAQ Composite', 'index', 'NASDAQ', 'Index', 'US')
ON CONFLICT (ticker) DO NOTHING;

-- Insert tracked forex pairs
INSERT INTO assets (ticker, name, asset_type, exchange, sector, country) VALUES
('EURUSD', 'Euro to US Dollar', 'fx', 'Forex', 'Currency', 'Global'),
('GBPUSD', 'British Pound to US Dollar', 'fx', 'Forex', 'Currency', 'Global'),
('USDJPY', 'US Dollar to Japanese Yen', 'fx', 'Forex', 'Currency', 'Global')
ON CONFLICT (ticker) DO NOTHING;

-- Verify seed data insertion
SELECT 
    asset_type,
    COUNT(*) as count,
    STRING_AGG(ticker, ', ' ORDER BY ticker) as tickers
FROM assets 
GROUP BY asset_type
ORDER BY asset_type;
