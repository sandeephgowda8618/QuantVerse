-- High-Impact Ticker Asset Universe SQL Insert
-- Ready-to-execute SQL for populating the assets table
-- Run this to add all 35 high-impact tickers to your asset universe

INSERT INTO assets (ticker, name, asset_type, exchange, priority_score)
VALUES
 -- US Tech (high liquidity, events, news-rich)
 ('AAPL','Apple Inc','stock','NASDAQ',100),
 ('MSFT','Microsoft Corp','stock','NASDAQ',100),
 ('NVDA','NVIDIA Corp','stock','NASDAQ',100),
 ('AMZN','Amazon.com','stock','NASDAQ',100),
 ('GOOGL','Alphabet Class A','stock','NASDAQ',98),
 ('META','Meta Platforms','stock','NASDAQ',98),
 ('TSLA','Tesla','stock','NASDAQ',97),
 ('AMD','Advanced Micro Devices','stock','NASDAQ',95),
 ('AVGO','Broadcom','stock','NASDAQ',95),
 ('NFLX','Netflix','stock','NASDAQ',94),
 
 -- Banks & Finance (rate-sensitive)
 ('JPM','JPMorgan Chase','stock','NYSE',100),
 ('BAC','Bank of America','stock','NYSE',95),
 ('GS','Goldman Sachs','stock','NYSE',92),
 ('WFC','Wells Fargo','stock','NYSE',90),
 ('MS','Morgan Stanley','stock','NYSE',90),
 
 -- Energy & Commodities (macro + oil shocks)
 ('XOM','Exxon Mobil','stock','NYSE',96),
 ('CVX','Chevron','stock','NYSE',94),
 ('COP','ConocoPhillips','stock','NYSE',90),
 
 -- Industrials & Defense (supply chain + geopolitical)
 ('BA','Boeing','stock','NYSE',90),
 ('LMT','Lockheed Martin','stock','NYSE',88),
 ('CAT','Caterpillar','stock','NYSE',88),
 ('GE','General Electric','stock','NYSE',87),
 
 -- Retail & Consumer (inflation, earnings sensitivity)
 ('WMT','Walmart','stock','NYSE',90),
 ('COST','Costco','stock','NASDAQ',89),
 ('MCD','McDonalds','stock','NYSE',88),
 ('HD','Home Depot','stock','NYSE',87),
 ('SBUX','Starbucks','stock','NASDAQ',85),
 
 -- Healthcare & Pharma (FDA + news-driven)
 ('JNJ','Johnson & Johnson','stock','NYSE',90),
 ('PFE','Pfizer','stock','NYSE',88),
 ('MRK','Merck','stock','NYSE',88),
 
 -- ETFs (broad market behavior)
 ('SPY','SPDR S&P 500 ETF','etf','NYSE',95),
 ('QQQ','Invesco QQQ ETF','etf','NASDAQ',95),
 ('IWM','Russell 2000 ETF','etf','NYSE',90),
 
 -- Crypto (for sudden-move explainer + infra outages)
 ('BTC-USD','Bitcoin','crypto','COINBASE',100),
 ('ETH-USD','Ethereum','crypto','COINBASE',100)
 
ON CONFLICT (ticker) DO UPDATE SET
    name = EXCLUDED.name,
    asset_type = EXCLUDED.asset_type,
    exchange = EXCLUDED.exchange,
    priority_score = EXCLUDED.priority_score;

-- Verify the insert
SELECT asset_type, COUNT(*) as count, 
       ROUND(AVG(priority_score), 1) as avg_priority
FROM assets 
WHERE ticker IN (
    'AAPL','MSFT','NVDA','AMZN','GOOGL','META','TSLA','AMD','AVGO','NFLX',
    'JPM','BAC','GS','WFC','MS',
    'XOM','CVX','COP',
    'BA','LMT','CAT','GE', 
    'WMT','COST','MCD','HD','SBUX',
    'JNJ','PFE','MRK',
    'SPY','QQQ','IWM',
    'BTC-USD','ETH-USD'
)
GROUP BY asset_type
ORDER BY avg_priority DESC;
