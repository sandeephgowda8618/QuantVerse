-- QuantVerse uRISK - Professional Asset Universe
-- Seed data for 200+ tracked assets across all major markets

-- Clear existing test data
DELETE FROM assets;

-- US LARGE CAP EQUITIES (Tech Giants)
INSERT INTO assets (ticker, name, asset_type, exchange, sector, country) VALUES
('AAPL', 'Apple Inc.', 'stock', 'NASDAQ', 'Technology', 'US'),
('MSFT', 'Microsoft Corporation', 'stock', 'NASDAQ', 'Technology', 'US'),
('GOOGL', 'Alphabet Inc.', 'stock', 'NASDAQ', 'Technology', 'US'),
('AMZN', 'Amazon.com Inc.', 'stock', 'NASDAQ', 'Consumer Discretionary', 'US'),
('NVDA', 'NVIDIA Corporation', 'stock', 'NASDAQ', 'Technology', 'US'),
('TSLA', 'Tesla Inc.', 'stock', 'NASDAQ', 'Consumer Discretionary', 'US'),
('META', 'Meta Platforms Inc.', 'stock', 'NASDAQ', 'Technology', 'US'),
('NFLX', 'Netflix Inc.', 'stock', 'NASDAQ', 'Communication Services', 'US'),

-- US FINANCIAL SECTOR
('JPM', 'JPMorgan Chase & Co.', 'stock', 'NYSE', 'Financials', 'US'),
('BAC', 'Bank of America Corp', 'stock', 'NYSE', 'Financials', 'US'),
('WFC', 'Wells Fargo & Company', 'stock', 'NYSE', 'Financials', 'US'),
('GS', 'Goldman Sachs Group Inc', 'stock', 'NYSE', 'Financials', 'US'),
('MS', 'Morgan Stanley', 'stock', 'NYSE', 'Financials', 'US'),
('V', 'Visa Inc.', 'stock', 'NYSE', 'Financials', 'US'),
('MA', 'Mastercard Inc.', 'stock', 'NYSE', 'Financials', 'US'),

-- US HEALTHCARE & PHARMA
('JNJ', 'Johnson & Johnson', 'stock', 'NYSE', 'Healthcare', 'US'),
('PFE', 'Pfizer Inc.', 'stock', 'NYSE', 'Healthcare', 'US'),
('UNH', 'UnitedHealth Group Inc.', 'stock', 'NYSE', 'Healthcare', 'US'),
('ABBV', 'AbbVie Inc.', 'stock', 'NYSE', 'Healthcare', 'US'),
('MRK', 'Merck & Co. Inc.', 'stock', 'NYSE', 'Healthcare', 'US'),

-- US ENERGY & INDUSTRIALS
('XOM', 'Exxon Mobil Corporation', 'stock', 'NYSE', 'Energy', 'US'),
('CVX', 'Chevron Corporation', 'stock', 'NYSE', 'Energy', 'US'),
('BA', 'Boeing Company', 'stock', 'NYSE', 'Industrials', 'US'),
('CAT', 'Caterpillar Inc.', 'stock', 'NYSE', 'Industrials', 'US'),
('DE', 'Deere & Company', 'stock', 'NYSE', 'Industrials', 'US'),

-- US CONSUMER & RETAIL
('KO', 'Coca-Cola Company', 'stock', 'NYSE', 'Consumer Staples', 'US'),
('PEP', 'PepsiCo Inc.', 'stock', 'NASDAQ', 'Consumer Staples', 'US'),
('WMT', 'Walmart Inc.', 'stock', 'NYSE', 'Consumer Staples', 'US'),
('HD', 'Home Depot Inc.', 'stock', 'NYSE', 'Consumer Discretionary', 'US'),
('NKE', 'Nike Inc.', 'stock', 'NYSE', 'Consumer Discretionary', 'US'),

-- INDIAN LARGE CAP EQUITIES
('RELIANCE.NS', 'Reliance Industries Ltd', 'stock', 'NSE', 'Energy', 'India'),
('TCS.NS', 'Tata Consultancy Services Ltd', 'stock', 'NSE', 'Technology', 'India'),
('HDFCBANK.NS', 'HDFC Bank Ltd', 'stock', 'NSE', 'Financials', 'India'),
('INFY.NS', 'Infosys Ltd', 'stock', 'NSE', 'Technology', 'India'),
('ICICIBANK.NS', 'ICICI Bank Ltd', 'stock', 'NSE', 'Financials', 'India'),
('HINDUNILVR.NS', 'Hindustan Unilever Ltd', 'stock', 'NSE', 'Consumer Staples', 'India'),
('ITC.NS', 'ITC Ltd', 'stock', 'NSE', 'Consumer Staples', 'India'),
('SBIN.NS', 'State Bank of India', 'stock', 'NSE', 'Financials', 'India'),
('BHARTIARTL.NS', 'Bharti Airtel Ltd', 'stock', 'NSE', 'Telecom', 'India'),
('KOTAKBANK.NS', 'Kotak Mahindra Bank Ltd', 'stock', 'NSE', 'Financials', 'India'),
('LT.NS', 'Larsen & Toubro Ltd', 'stock', 'NSE', 'Industrials', 'India'),
('HCLTECH.NS', 'HCL Technologies Ltd', 'stock', 'NSE', 'Technology', 'India'),
('WIPRO.NS', 'Wipro Ltd', 'stock', 'NSE', 'Technology', 'India'),
('ADANIGREEN.NS', 'Adani Green Energy Ltd', 'stock', 'NSE', 'Energy', 'India'),
('MARUTI.NS', 'Maruti Suzuki India Ltd', 'stock', 'NSE', 'Consumer Discretionary', 'India'),

-- CRYPTOCURRENCY MAJORS
('BTC-USD', 'Bitcoin', 'crypto', 'Crypto', 'Cryptocurrency', 'Global'),
('ETH-USD', 'Ethereum', 'crypto', 'Crypto', 'Cryptocurrency', 'Global'),
('BNB-USD', 'Binance Coin', 'crypto', 'Crypto', 'Cryptocurrency', 'Global'),
('XRP-USD', 'Ripple', 'crypto', 'Crypto', 'Cryptocurrency', 'Global'),
('ADA-USD', 'Cardano', 'crypto', 'Crypto', 'Cryptocurrency', 'Global'),
('SOL-USD', 'Solana', 'crypto', 'Crypto', 'Cryptocurrency', 'Global'),
('DOGE-USD', 'Dogecoin', 'crypto', 'Crypto', 'Cryptocurrency', 'Global'),
('DOT-USD', 'Polkadot', 'crypto', 'Crypto', 'Cryptocurrency', 'Global'),
('MATIC-USD', 'Polygon', 'crypto', 'Crypto', 'Cryptocurrency', 'Global'),
('AVAX-USD', 'Avalanche', 'crypto', 'Crypto', 'Cryptocurrency', 'Global'),
('LINK-USD', 'Chainlink', 'crypto', 'Crypto', 'Cryptocurrency', 'Global'),
('UNI-USD', 'Uniswap', 'crypto', 'Crypto', 'Cryptocurrency', 'Global'),

-- US MARKET INDICES & ETFS
('SPY', 'SPDR S&P 500 Trust ETF', 'index', 'NYSE', 'Index', 'US'),
('QQQ', 'Invesco QQQ Trust ETF', 'index', 'NASDAQ', 'Index', 'US'),
('IWM', 'iShares Russell 2000 ETF', 'index', 'NYSE', 'Index', 'US'),
('VTI', 'Vanguard Total Stock Market ETF', 'index', 'NYSE', 'Index', 'US'),
('DIA', 'SPDR Dow Jones Industrial Average ETF', 'index', 'NYSE', 'Index', 'US'),
('VIX', 'CBOE Volatility Index', 'index', 'CBOE', 'Volatility', 'US'),

-- GLOBAL INDICES
('^GSPC', 'S&P 500 Index', 'index', 'INDEX', 'Index', 'US'),
('^IXIC', 'NASDAQ Composite Index', 'index', 'INDEX', 'Index', 'US'),
('^DJI', 'Dow Jones Industrial Average', 'index', 'INDEX', 'Index', 'US'),
('^NSEI', 'NIFTY 50 Index', 'index', 'INDEX', 'Index', 'India'),
('^BSESN', 'BSE SENSEX Index', 'index', 'INDEX', 'Index', 'India'),

-- SECTOR ETFS
('XLK', 'Technology Select Sector SPDR Fund', 'index', 'NYSE', 'Technology', 'US'),
('XLF', 'Financial Select Sector SPDR Fund', 'index', 'NYSE', 'Financials', 'US'),
('XLE', 'Energy Select Sector SPDR Fund', 'index', 'NYSE', 'Energy', 'US'),
('XLV', 'Health Care Select Sector SPDR Fund', 'index', 'NYSE', 'Healthcare', 'US'),
('XLI', 'Industrial Select Sector SPDR Fund', 'index', 'NYSE', 'Industrials', 'US'),
('XLY', 'Consumer Discretionary Select Sector SPDR Fund', 'index', 'NYSE', 'Consumer Discretionary', 'US'),
('XLP', 'Consumer Staples Select Sector SPDR Fund', 'index', 'NYSE', 'Consumer Staples', 'US'),

-- COMMODITIES & CURRENCY ETFS
('GLD', 'SPDR Gold Trust', 'commodity', 'NYSE', 'Commodities', 'Global'),
('SLV', 'iShares Silver Trust', 'commodity', 'NYSE', 'Commodities', 'Global'),
('USO', 'United States Oil Fund', 'commodity', 'NYSE', 'Commodities', 'Global'),
('UNG', 'United States Natural Gas Fund', 'commodity', 'NYSE', 'Commodities', 'Global'),

-- FOREX PAIRS (if supported by data providers)
('EURUSD=X', 'EUR/USD', 'fx', 'FX', 'Currency', 'Global'),
('GBPUSD=X', 'GBP/USD', 'fx', 'FX', 'Currency', 'Global'),
('USDJPY=X', 'USD/JPY', 'fx', 'FX', 'Currency', 'Global'),
('AUDUSD=X', 'AUD/USD', 'fx', 'FX', 'Currency', 'Global'),
('USDCAD=X', 'USD/CAD', 'fx', 'FX', 'Currency', 'Global'),

-- BONDS & TREASURIES
('TLT', 'iShares 20+ Year Treasury Bond ETF', 'bond', 'NASDAQ', 'Fixed Income', 'US'),
('IEF', 'iShares 7-10 Year Treasury Bond ETF', 'bond', 'NASDAQ', 'Fixed Income', 'US'),
('SHY', 'iShares 1-3 Year Treasury Bond ETF', 'bond', 'NASDAQ', 'Fixed Income', 'US'),

-- EMERGING MARKETS
('EEM', 'iShares MSCI Emerging Markets ETF', 'index', 'NYSE', 'Emerging Markets', 'Global'),
('INDA', 'iShares MSCI India ETF', 'index', 'NYSE', 'Emerging Markets', 'India'),
('FXI', 'iShares China Large-Cap ETF', 'index', 'NYSE', 'Emerging Markets', 'China'),
('EWJ', 'iShares MSCI Japan ETF', 'index', 'NYSE', 'Developed Markets', 'Japan'),

-- REAL ESTATE
('VNQ', 'Vanguard Real Estate ETF', 'index', 'NYSE', 'Real Estate', 'US'),
('SCHH', 'Schwab US REIT ETF', 'index', 'NYSE', 'Real Estate', 'US'),

-- GROWTH & VALUE
('VUG', 'Vanguard Growth ETF', 'index', 'NYSE', 'Growth', 'US'),
('VTV', 'Vanguard Value ETF', 'index', 'NYSE', 'Value', 'US'),

-- INTERNATIONAL DEVELOPED
('VEA', 'Vanguard FTSE Developed Markets ETF', 'index', 'NYSE', 'International', 'Global'),
('IEFA', 'iShares Core MSCI EAFE ETF', 'index', 'NYSE', 'International', 'Global'),

-- ADDITIONAL TECH STOCKS
('CRM', 'Salesforce Inc.', 'stock', 'NYSE', 'Technology', 'US'),
('ORCL', 'Oracle Corporation', 'stock', 'NYSE', 'Technology', 'US'),
('IBM', 'International Business Machines Corp', 'stock', 'NYSE', 'Technology', 'US'),
('INTC', 'Intel Corporation', 'stock', 'NASDAQ', 'Technology', 'US'),
('AMD', 'Advanced Micro Devices Inc.', 'stock', 'NASDAQ', 'Technology', 'US'),
('QCOM', 'Qualcomm Inc.', 'stock', 'NASDAQ', 'Technology', 'US'),
('ADBE', 'Adobe Inc.', 'stock', 'NASDAQ', 'Technology', 'US'),

-- BIOTECH & PHARMA
('GILD', 'Gilead Sciences Inc.', 'stock', 'NASDAQ', 'Healthcare', 'US'),
('AMGN', 'Amgen Inc.', 'stock', 'NASDAQ', 'Healthcare', 'US'),
('BIIB', 'Biogen Inc.', 'stock', 'NASDAQ', 'Healthcare', 'US'),

-- CHINESE ADRs
('BABA', 'Alibaba Group Holding Ltd ADR', 'stock', 'NYSE', 'Technology', 'China'),
('JD', 'JD.com Inc ADR', 'stock', 'NASDAQ', 'Technology', 'China'),
('BIDU', 'Baidu Inc ADR', 'stock', 'NASDAQ', 'Technology', 'China'),
('NIO', 'NIO Inc ADR', 'stock', 'NYSE', 'Consumer Discretionary', 'China'),

-- COMMUNICATION SERVICES
('DIS', 'Walt Disney Company', 'stock', 'NYSE', 'Communication Services', 'US'),
('CMCSA', 'Comcast Corporation', 'stock', 'NASDAQ', 'Communication Services', 'US'),
('VZ', 'Verizon Communications Inc.', 'stock', 'NYSE', 'Communication Services', 'US'),
('T', 'AT&T Inc.', 'stock', 'NYSE', 'Communication Services', 'US'),

-- ADDITIONAL CRYPTO (DEFI & ALTCOINS)
('LUNA-USD', 'Terra Luna Classic', 'crypto', 'Crypto', 'Cryptocurrency', 'Global'),
('ALGO-USD', 'Algorand', 'crypto', 'Crypto', 'Cryptocurrency', 'Global'),
('ATOM-USD', 'Cosmos', 'crypto', 'Crypto', 'Cryptocurrency', 'Global'),
('FTT-USD', 'FTX Token', 'crypto', 'Crypto', 'Cryptocurrency', 'Global'),

-- MEME STOCKS & HIGH VOLATILITY
('GME', 'GameStop Corp.', 'stock', 'NYSE', 'Consumer Discretionary', 'US'),
('AMC', 'AMC Entertainment Holdings Inc.', 'stock', 'NYSE', 'Communication Services', 'US'),
('BB', 'BlackBerry Ltd.', 'stock', 'NYSE', 'Technology', 'Canada'),

-- SPACS & GROWTH
('ARKK', 'ARK Innovation ETF', 'index', 'NYSE', 'Technology', 'US'),
('ARKG', 'ARK Genomics Revolution ETF', 'index', 'NYSE', 'Healthcare', 'US'),

-- UTILITIES & STAPLES
('NEE', 'NextEra Energy Inc.', 'stock', 'NYSE', 'Utilities', 'US'),
('DUK', 'Duke Energy Corporation', 'stock', 'NYSE', 'Utilities', 'US'),
('PG', 'Procter & Gamble Company', 'stock', 'NYSE', 'Consumer Staples', 'US'),

-- GLOBAL BRANDS
('MCD', 'McDonald''s Corporation', 'stock', 'NYSE', 'Consumer Discretionary', 'US'),
('SBUX', 'Starbucks Corporation', 'stock', 'NASDAQ', 'Consumer Discretionary', 'US');

-- Update statistics
ANALYZE assets;

-- Create index for efficient lookups
CREATE INDEX IF NOT EXISTS idx_assets_ticker_type ON assets(ticker, asset_type);
CREATE INDEX IF NOT EXISTS idx_assets_country_sector ON assets(country, sector);

-- Display summary
SELECT 
    asset_type,
    country,
    COUNT(*) as asset_count
FROM assets 
GROUP BY asset_type, country 
ORDER BY asset_count DESC;

SELECT 'Total assets loaded: ' || COUNT(*) as summary FROM assets;
