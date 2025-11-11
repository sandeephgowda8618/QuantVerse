# Alpha Vantage API - Complete Implementation Guide

## 🏆 Top 200 Global Companies by Market Cap (November 2025)

This implementation covers comprehensive data ingestion for the top 200 global companies using all Alpha Vantage API endpoints.

### Market Cap Tiers:
- **Mega Cap (1-25)**: NVDA, MSFT, AAPL, GOOG, GOOGL, AMZN, META, AVGO, TSM, TSLA, etc.
- **Large Cap (26-100)**: JNJ, SSNLF, WFC, MU, CAT, MS, AXP, etc.
- **Mid Cap (101-200)**: SYK, CRWD, LOW, DE, WELL, SPOT, HOOD, etc.

Total US Tradeable Symbols: **150+ companies**

## 📋 Index - Complete API Coverage

### 🏢 Core Stock APIs
- ✅ **Intraday** - TIME_SERIES_INTRADAY
- ✅ **Daily** - TIME_SERIES_DAILY
- ✅ **Daily Adjusted** - TIME_SERIES_DAILY_ADJUSTED
- ✅ **Weekly** - TIME_SERIES_WEEKLY
- ✅ **Weekly Adjusted** - TIME_SERIES_WEEKLY_ADJUSTED
- ✅ **Monthly** - TIME_SERIES_MONTHLY
- ✅ **Monthly Adjusted** - TIME_SERIES_MONTHLY_ADJUSTED
- ✅ **Quote Endpoint** - GLOBAL_QUOTE
- ⭐ **Realtime Bulk Quotes** (Premium)
- ✅ **Ticker Search** 🔧 Utility - SYMBOL_SEARCH
- ✅ **Global Market Status** 🔧 Utility - MARKET_STATUS

### 📊 Options Data APIs
- ⭐ **Realtime Options** (Premium) - REALTIME_OPTIONS
- ✅ **Historical Options** - HISTORICAL_OPTIONS

### 🧠 Alpha Intelligence™
- ✅ **News & Sentiments** - NEWS_SENTIMENT
- ✅ **Earnings Call Transcript** - EARNINGS_CALL_TRANSCRIPT
- ✅ **Top Gainers & Losers** - TOP_GAINERS_LOSERS
- ✅ **Insider Transactions** - INSIDER_TRANSACTIONS
- ✅ **Analytics (Fixed Window)** - ANALYTICS_FIXED_WINDOW
- ✅ **Analytics (Sliding Window)** - ANALYTICS_SLIDING_WINDOW

### 📈 Fundamental Data
- ✅ **Company Overview** - OVERVIEW
- ✅ **ETF Profile & Holdings** - ETF_PROFILE
- ✅ **Corporate Action - Dividends** - DIVIDENDS
- ✅ **Corporate Action - Splits** - SPLITS
- ✅ **Income Statement** - INCOME_STATEMENT
- ✅ **Balance Sheet** - BALANCE_SHEET
- ✅ **Cash Flow** - CASH_FLOW
- ✅ **Shares Outstanding** - SHARES_OUTSTANDING
- ✅ **Earnings History** - EARNINGS
- ✅ **Earnings Estimates** - EARNINGS_ESTIMATES
- ✅ **Listing & Delisting Status** - LISTING_STATUS
- ✅ **Earnings Calendar** - EARNINGS_CALENDAR
- ✅ **IPO Calendar** - IPO_CALENDAR

### 💱 Forex (FX)
- ✅ **Exchange Rates** - CURRENCY_EXCHANGE_RATE
- ⭐ **Intraday** (Premium) - FX_INTRADAY
- ✅ **Daily** - FX_DAILY
- ✅ **Weekly** - FX_WEEKLY
- ✅ **Monthly** - FX_MONTHLY

### ₿ Cryptocurrencies
- ✅ **Exchange Rates** - CURRENCY_EXCHANGE_RATE
- ⭐ **Intraday** (Premium) - DIGITAL_CURRENCY_INTRADAY
- ✅ **Daily** - DIGITAL_CURRENCY_DAILY
- ✅ **Weekly** - DIGITAL_CURRENCY_WEEKLY
- ✅ **Monthly** - DIGITAL_CURRENCY_MONTHLY

### 🛢️ Commodities
- ✅ **Crude Oil (WTI)** - WTI
- ✅ **Crude Oil (Brent)** - BRENT
- ✅ **Natural Gas** - NATURAL_GAS
- ✅ **Copper** - COPPER
- ✅ **Aluminum** - ALUMINUM
- ✅ **Wheat** - WHEAT
- ✅ **Corn** - CORN
- ✅ **Cotton** - COTTON
- ✅ **Sugar** - SUGAR
- ✅ **Coffee** - COFFEE
- ✅ **Global Commodities Index** - GLOBAL_COMMODITIES

### 🏛️ Economic Indicators
- ✅ **Real GDP** - REAL_GDP
- ✅ **Real GDP per Capita** - REAL_GDP_PER_CAPITA
- ✅ **Treasury Yield** - TREASURY_YIELD
- ✅ **Federal Funds (Interest) Rate** - FEDERAL_FUNDS_RATE
- ✅ **CPI** - CPI
- ✅ **Inflation** - INFLATION
- ✅ **Retail Sales** - RETAIL_SALES
- ✅ **Durable Goods Orders** - DURABLES
- ✅ **Unemployment Rate** - UNEMPLOYMENT
- ✅ **Nonfarm Payroll** - NONFARM_PAYROLL

### 📊 Technical Indicators
- ✅ **SMA** - Simple Moving Average
- ✅ **EMA** - Exponential Moving Average
- ✅ **WMA** - Weighted Moving Average
- ✅ **DEMA** - Double Exponential Moving Average
- ✅ **TEMA** - Triple Exponential Moving Average
- ✅ **TRIMA** - Triangular Moving Average
- ✅ **KAMA** - Kaufman Adaptive Moving Average
- ✅ **MAMA** - MESA Adaptive Moving Average
- ⭐ **VWAP** (Premium) - Volume Weighted Average Price
- ✅ **T3** - Triple Exponential Moving Average
- ⭐ **MACD** (Premium) - Moving Average Convergence Divergence
- ✅ **MACDEXT** - MACD with controllable MA type
- ✅ **STOCH** - Stochastic Oscillator
- ✅ **STOCHF** - Stochastic Fast
- ✅ **RSI** - Relative Strength Index
- ✅ **STOCHRSI** - Stochastic RSI
- ✅ **WILLR** - Williams %R
- ✅ **ADX** - Average Directional Index
- ✅ **ADXR** - Average Directional Index Rating
- ✅ **APO** - Absolute Price Oscillator
- ✅ **PPO** - Percentage Price Oscillator
- ✅ **MOM** - Momentum
- ✅ **BOP** - Balance of Power
- ✅ **CCI** - Commodity Channel Index
- ✅ **CMO** - Chande Momentum Oscillator
- ✅ **ROC** - Rate of Change
- ✅ **ROC** - Rate of Change
- ✅ **ROCR** - Rate of Change Ratio
- ✅ **AROON** - Aroon Indicator
- ✅ **AROONOSC** - Aroon Oscillator
- ✅ **MFI** - Money Flow Index
- ✅ **TRIX** - Triple Exponential Average
- ✅ **ULTOSC** - Ultimate Oscillator
- ✅ **DX** - Directional Movement Index
- ✅ **MINUS_DI** - Minus Directional Indicator
- ✅ **PLUS_DI** - Plus Directional Indicator
- ✅ **MINUS_DM** - Minus Directional Movement
- ✅ **PLUS_DM** - Plus Directional Movement
- ✅ **BBANDS** - Bollinger Bands
- ✅ **MIDPOINT** - Midpoint
- ✅ **MIDPRICE** - Midprice
- ✅ **SAR** - Parabolic SAR
- ✅ **TRANGE** - True Range
- ✅ **ATR** - Average True Range
- ✅ **NATR** - Normalized Average True Range
- ✅ **AD** - Accumulation/Distribution Line
- ✅ **ADOSC** - Accumulation/Distribution Oscillator
- ✅ **OBV** - On Balance Volume
- ✅ **HT_TRENDLINE** - Hilbert Transform - Instantaneous Trendline
- ✅ **HT_SINE** - Hilbert Transform - Sine Wave
- ✅ **HT_TRENDMODE** - Hilbert Transform - Trend vs Cycle Mode
- ✅ **HT_DCPERIOD** - Hilbert Transform - Dominant Cycle Period
- ✅ **HT_DCPHASE** - Hilbert Transform - Dominant Cycle Phase
- ✅ **HT_PHASOR** - Hilbert Transform - Phasor Components

## 🚀 Implementation Status

### ✅ Completed Components
1. **Enhanced Alpha Vantage Collector** - `enhanced_alpha_vantage_collector.py`
2. **Top 200 Companies Database** - `top_200_companies.py`
3. **Enhanced Database Schema** - `enhanced_alpha_vantage_schema.sql`
4. **Comprehensive Data Populator** - `populate_alpha_vantage_data.py`

### 🎯 Data Collection Strategy
- **Mega Cap (1-25)**: Real-time priority, all data types
- **Large Cap (26-100)**: Daily updates, core fundamentals + technicals
- **Mid Cap (101-200)**: Weekly updates, essential data

### 💾 Database Integration
- **PostgreSQL**: Structured data storage with 15+ specialized tables
- **ChromaDB**: Vector embeddings for semantic search and RAG
- **Metadata**: Rich metadata for each data point (source, timestamp, relevance)

### 📊 Supported Data Types
1. **Market Data**: OHLCV, intraday, daily, weekly, monthly
2. **Fundamental Data**: Company overviews, earnings, financial statements
3. **News & Sentiment**: Real-time news with sentiment analysis
4. **Technical Indicators**: 70+ technical analysis indicators
5. **Economic Data**: GDP, inflation, employment, interest rates
6. **Forex**: Major currency pairs with real-time rates
7. **Crypto**: Top cryptocurrencies with market data
8. **Commodities**: Oil, metals, agricultural products
9. **Options**: Options chains and Greeks (premium)
10. **Market Intelligence**: Top movers, insider transactions

## 🔧 Quick Start Guide

### 1. Environment Setup

## 🎯 Usage Instructions

### Prerequisites
1. **Alpha Vantage API Key** (Free at https://www.alphavantage.co/support/#api-key)
2. **PostgreSQL Database** (running locally or cloud)
3. **Python 3.8+** with required dependencies

### Installation & Setup


TIME_SERIES_INTRADAY Trending

This API returns current and 20+ years of historical intraday OHLCV time series of the equity specified, covering pre-market and post-market hours where applicable (e.g., 4:00am to 8:00pm Eastern Time for the US market). You can query both raw (as-traded) and split/dividend-adjusted intraday data from this endpoint. The OHLCV data is sometimes called "candles" in finance literature.


API Parameters
❚ Required: function

The time series of your choice. In this case, function=TIME_SERIES_INTRADAY

❚ Required: symbol

The name of the equity of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min

❚ Optional: adjusted

By default, adjusted=true and the output time series is adjusted by historical split and dividend events. Set adjusted=false to query raw (as-traded) intraday values.

❚ Optional: extended_hours

By default, extended_hours=true and the output time series will include both the regular trading hours and the extended (pre-market and post-market) trading hours (4:00am to 8:00pm Eastern Time for the US market). Set extended_hours=false to query regular trading hours (9:30am to 4:00pm US Eastern Time) only.

❚ Optional: month

By default, this parameter is not set and the API will return intraday data for the most recent days of trading. You can use the month parameter (in YYYY-MM format) to query a specific month in history. For example, month=2009-01. Any month in the last 20+ years since 2000-01 (January 2000) is supported.

❚ Optional: outputsize

By default, outputsize=compact. Strings compact and full are accepted with the following specifications: compact returns only the latest 100 data points in the intraday time series; full returns trailing 30 days of the most recent intraday data if the month parameter (see above) is not specified, or the full intraday data for a specific month in history if the month parameter is specified. The "compact" option is recommended if you would like to reduce the data size of each API call.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the intraday time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.




Examples (click for JSON output)
The API will return the most recent 100 intraday OHLCV bars by default when the outputsize parameter is not set
https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=demo

Query the most recent full 30 days of intraday data by setting outputsize=full
https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&outputsize=full&apikey=demo

Query intraday data for a given month in history (e.g., 2009-01). Any month in the last 20+ years (since 2000-01) is supported
https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&month=2009-01&outputsize=full&apikey=demo

Downloadable CSV file:
https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=demo&datatype=csv

1.Query the most recent full 30 days of intraday data by setting outputsize=full
{
    "Meta Data": {
        "1. Information": "Intraday (5min) open, high, low, close prices and volume",
        "2. Symbol": "IBM",
        "3. Last Refreshed": "2025-11-06 19:55:00",
        "4. Interval": "5min",
        "5. Output Size": "Full size",
        "6. Time Zone": "US/Eastern"
    },
    "Time Series (5min)": {
        "2025-11-06 19:55:00": {
            "1. open": "313.0800",
            "2. high": "313.6500",
            "3. low": "313.0800",
            "4. close": "313.4000",
            "5. volume": "57"
        },
        "2025-11-06 19:50:00": {
            "1. open": "313.0100",
            "2. high": "313.9000",
            "3. low": "312.5350",
            "4. close": "312.5350",
            "5. volume": "13"
        },
        "2025-11-06 19:45:00": {
            "1. open": "312.5000",
            "2. high": "313.9300",
            "3. low": "312.5000",
            "4. close": "313.9300",
            "5. volume": "61"
        },
        "2025-11-06 19:40:00": {
            "1. open": "313.2500",
            "2. high": "313.2500",
            "3. low": "313.0100",
            "4. close": "313.0100",
            "5. volume": "19"
        },
        "2025-11-06 19:35:00": {
            "1. open": "313.2500",
            "2. high": "314.0000",
            "3. low": "313.2500",
            "4. close": "313.7000",
            "5. volume": "1124"
        },
        "2025-11-06 19:30:00": {
            "1. open": "313.7000",
            "2. high": "313.7000",
            "3. low": "313.2500",
            "4. close": "313.6800",
            "5. volume": "32"
        },
        "2025-11-06 19:25:00": {
            "1. open": "313.2300",
            "2. high": "313.2500",
            "3. low": "313.2300",
            "4. close": "313.2500",
            "5. volume": "42"
        },
        "2025-11-06 19:20:00": {
            "1. open": "313.5000",
            "2. high": "313.5000",
            "3. low": "313.2300",
            "4. close": "313.2300",
            "5. volume": "128"
        },
        "2025-11-06 19:15:00": {
            "1. open": "314.0000",
            "2. high": "314.0000",
            "3. low": "313.2300",
            "4. close": "313.2301",
            "5. volume": "71"
        },
        "2025-11-06 19:10:00": {
            "1. open": "313.2400",
            "2. high": "314.0000",
            "3. low": "313.2400",
            "4. close": "313.5620",
            "5. volume": "19"
        },
        "2025-11-06 19:05:00": {
            "1. open": "313.2300",
            "2. high": "314.0000",
            "3. low": "313.2300",
            "4. close": "313.2400",
            "5. volume": "252"
        },
        "2025-11-06 19:00:00": {
            "1. open": "312.4200",
            "2. high": "313.2600",
            "3. low": "312.4200",
            "4. close": "313.2600",
            "5. volume": "690073"
        },
        "2025-11-06 18:55:00": {
            "1. open": "312.4600",
            "2. high": "314.0000",
            "3. low": "312.4600",
            "4. close": "313.2400",
            "5. volume": "754"
        },
        "2025-11-06 18:50:00": {
            "1. open": "313.0800",
            "2. high": "313.5000",
            "3. low": "313.0100",
            "4. close": "313.2500",
            "5. volume": "1567"
        },
        "2025-11-06 18:45:00": {
            "1. open": "313.0500",
            "2. high": "313.2500",
            "3. low": "313.0500",
            "4. close": "313.0800",
            "5. volume": "187"
        },
        "2025-11-06 18:40:00": {
            "1. open": "312.9600",
            "2. high": "313.1827",
            "3. low": "312.9600",
            "4. close": "313.0535",
            "5. volume": "98"
        },
        "2025-11-06 18:35:00": {
            "1. open": "312.7500",
            "2. high": "313.0000",
            "3. low": "312.7500",
            "4. close": "312.9887",
            "5. volume": "56"
        },
        "2025-11-06 18:30:00": {
            "1. open": "312.4200",
            "2. high": "312.9514",
            "3. low": "312.4200",
            "4. close": "312.7500",
            "5. volume": "689880"
        },
        "2025-11-06 18:25:00": {
            "1. open": "312.9400",
            "2. high": "312.9400",
            "3. low": "312.9400",
            "4. close": "312.9400",
            "5. volume": "16"
        },
        "2025-11-06 18:20:00": {
            "1. open": "312.7500",
            "2. high": "313.0000",
            "3. low": "312.4735",
            "4. close": "312.9999",
            "5. volume": "41"
        },
        "2025-11-06 18:15:00": {
            "1. open": "312.4300",
            "2. high": "312.7500",
            "3. low": "312.4300",
            "4. close": "312.7500",
            "5. volume": "36"
        },
        "2025-11-06 18:10:00": {
            "1. open": "312.9400",
            "2. high": "313.0000",
            "3. low": "312.4200",
            "4. close": "312.4200",
            "5. volume": "206"
        },
        "2025-11-06 18:05:00": {
            "1. open": "312.4300",
            "2. high": "313.0000",
            "3. low": "312.4200",
            "4. close": "313.0000",
            "5. volume": "228"
        },
        "2025-11-06 18:00:00": {
            "1. open": "312.9300",
            "2. high": "313.0000",
            "3. low": "312.4300",
            "4. close": "313.0000",
            "5. volume": "42"
        },
        "2025-11-06 17:55:00": {
            "1. open": "312.4200",
            "2. high": "312.9600",
            "3. low": "312.4200",
            "4. close": "312.4600",
            "5. volume": "578"
        },
        "2025-11-06 17:50:00": {
            "1. open": "312.4300",
            "2. high": "312.9860",
            "3. low": "312.4200",
            "4. close": "312.4500",
            "5. volume": "149"
        },
        "2025-11-06 17:45:00": {
            "1. open": "312.7000",
            "2. high": "313.0000",
            "3. low": "312.4600",
            "4. close": "312.7800",
            "5. volume": "144"
        },
        "2025-11-06 17:40:00": {
            "1. open": "312.6600",
            "2. high": "313.0000",
            "3. low": "312.6600",
            "4. close": "313.0000",
            "5. volume": "121"
        },
        "2025-11-06 17:35:00": {
            "1. open": "312.5000",
            "2. high": "312.6600",
            "3. low": "312.5000",
            "4. close": "312.6600",
            "5. volume": "12"
        },
        "2025-11-06 17:30:00": {
            "1. open": "312.4600",
            "2. high": "312.4600",
            "3. low": "312.4500",
            "4. close": "312.4600",
            "5. volume": "45"
        },
        "2025-11-06 17:25:00": {
            "1. open": "312.4500",
            "2. high": "312.7100",
            "3. low": "312.4200",
            "4. close": "312.5000",
            "5. volume": "116"
        },
        "2025-11-06 17:20:00": {
            "1. open": "312.7400",
            "2. high": "312.9800",
            "3. low": "312.4200",
            "4. close": "312.4200",
            "5. volume": "50"
        },
        "2025-11-06 17:15:00": {
            "1. open": "312.7800",
            "2. high": "312.8500",
            "3. low": "312.3801",
            "4. close": "312.8500",
            "5. volume": "120"
        },
        "2025-11-06 17:10:00": {
            "1. open": "312.6400",
            "2. high": "312.6600",
            "3. low": "312.3800",
            "4. close": "312.5000",
            "5. volume": "148"
        },
        "2025-11-06 17:05:00": {
            "1. open": "312.3800",
            "2. high": "312.6500",
            "3. low": "312.3087",
            "4. close": "312.4700",
            "5. volume": "795"
        },
        "2025-11-06 17:00:00": {
            "1. open": "312.7200",
            "2. high": "312.7300",
            "3. low": "312.3000",
            "4. close": "312.3000",
            "5. volume": "43"
        },
        "2025-11-06 16:55:00": {
            "1. open": "312.6500",
            "2. high": "313.0000",
            "3. low": "312.4200",
            "4. close": "312.6500",
            "5. volume": "1117113"
        },
        "2025-11-06 16:50:00": {
            "1. open": "312.5000",
            "2. high": "312.7800",
            "3. low": "312.3000",
            "4. close": "312.3000",
            "5. volume": "156"
        },
        "2025-11-06 16:45:00": {
            "1. open": "312.5800",
            "2. high": "313.0000",
            "3. low": "312.2600",
            "4. close": "312.2700",
            "5. volume": "183"
        },
        "2025-11-06 16:40:00": {
            "1. open": "312.4000",
            "2. high": "312.6000",
            "3. low": "312.2740",
            "4. close": "312.3500",
            "5. volume": "329"
        },
        "2025-11-06 16:35:00": {
            "1. open": "312.2600",
            "2. high": "312.6100",
            "3. low": "312.2600",
            "4. close": "312.4200",
            "5. volume": "418"
        },
        "2025-11-06 16:30:00": {
            "1. open": "312.5300",
            "2. high": "312.7000",
            "3. low": "312.2800",
            "4. close": "312.3300",
            "5. volume": "451"
        },
        "2025-11-06 16:25:00": {
            "1. open": "312.9800",
            "2. high": "313.0000",
            "3. low": "312.2600",
            "4. close": "312.5400",
            "5. volume": "43"
        },
        "2025-11-06 16:20:00": {
            "1. open": "312.4200",
            "2. high": "313.2500",
            "3. low": "312.4200",
            "4. close": "312.5100",
            "5. volume": "2119"
        },
        "2025-11-06 16:15:00": {
            "1. open": "312.4200",
            "2. high": "313.2500",
            "3. low": "312.2600",
            "4. close": "312.2600",
            "5. volume": "2151"
        },
        "2025-11-06 16:10:00": {
            "1. open": "312.4200",
            "2. high": "313.2500",
            "3. low": "312.2622",
            "4. close": "312.2622",
            "5. volume": "695201"
        },
        "2025-11-06 16:05:00": {
            "1. open": "312.4200",
            "2. high": "313.2499",
            "3. low": "312.4200",
            "4. close": "313.0000",
            "5. volume": "2409"
        },
        "2025-11-06 16:00:00": {
            "1. open": "312.6100",
            "2. high": "315.0000",
            "3. low": "306.7700",
            "4. close": "312.4200",
            "5. volume": "1490971"
        },
        "2025-11-06 15:55:00": {
            "1. open": "312.4500",
            "2. high": "312.9500",
            "3. low": "312.2900",
            "4. close": "312.4800",
            "5. volume": "313904"
        },
        "2025-11-06 15:50:00": {
            "1. open": "312.1800",
            "2. high": "312.7900",
            "3. low": "311.9500",
            "4. close": "312.4500",
            "5. volume": "86197"
        },
        "2025-11-06 15:45:00": {
            "1. open": "313.6500",
            "2. high": "313.6900",
            "3. low": "312.0500",
            "4. close": "312.1700",
            "5. volume": "93451"
        }
        #it continues.. it is some 20k+ readings
    }
}

2.Query intraday data for a given month in history (e.g., 2009-01). Any month in the last 20+ years (since 2000-01) is supported




## TIME_SERIES_DAILY
API Parameters
❚ Required: function

The time series of your choice. In this case, function=TIME_SERIES_DAILY

❚ Required: symbol

The name of the equity of your choice. For example: symbol=IBM

❚ Optional: outputsize

By default, outputsize=compact. Strings compact and full are accepted with the following specifications: compact returns only the latest 100 data points; full returns the full-length time series of 20+ years of historical data. The "compact" option is recommended if you would like to reduce the data size of each API call.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.

Examples (click for JSON output)
Sample ticker traded in the United States
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey=demo

https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&outputsize=full&apikey=demo

Sample ticker traded in UK - London Stock Exchange
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TSCO.LON&outputsize=full&apikey=demo

Sample ticker traded in Canada - Toronto Stock Exchange
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=SHOP.TRT&outputsize=full&apikey=demo

Sample ticker traded in Canada - Toronto Venture Exchange
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=GPV.TRV&outputsize=full&apikey=demo

Sample ticker traded in Germany - XETRA
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MBG.DEX&outputsize=full&apikey=demo

Sample ticker traded in India - BSE
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=RELIANCE.BSE&outputsize=full&apikey=demo

Sample ticker traded in China - Shanghai Stock Exchange
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=600104.SHH&outputsize=full&apikey=demo

Sample ticker traded in China - Shenzhen Stock Exchange
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=000002.SHZ&outputsize=full&apikey=demo

1.Sample ticker traded in the United States:
{
    "Meta Data": {
        "1. Information": "Daily Prices (open, high, low, close) and Volumes",
        "2. Symbol": "IBM",
        "3. Last Refreshed": "2025-11-06",
        "4. Output Size": "Compact",
        "5. Time Zone": "US/Eastern"
    },
    "Time Series (Daily)": {
        "2025-11-06": {
            "1. open": "306.7500",
            "2. high": "315.4400",
            "3. low": "301.0900",
            "4. close": "312.4200",
            "5. volume": "5687955"
        },
        "2025-11-05": {
            "1. open": "301.3800",
            "2. high": "307.2000",
            "3. low": "299.7100",
            "4. close": "306.7700",
            "5. volume": "4633195"
        },
        "2025-11-04": {
            "1. open": "300.0000",
            "2. high": "303.1700",
            "3. low": "296.0000",
            "4. close": "300.8500",
            "5. volume": "5677330"
        },
        "2025-11-03": {
            "1. open": "308.0000",
            "2. high": "312.1411",
            "3. low": "304.2300",
            "4. close": "304.7300",
            "5. volume": "4957958"
        },
        "2025-10-31": {
            "1. open": "312.0000",
            "2. high": "313.5000",
            "3. low": "301.6300",
            "4. close": "307.4100",
            "5. volume": "7697499"
        },
        "2025-10-30": {
            "1. open": "306.6500",
            "2. high": "313.7500",
            "3. low": "305.0200",
            "4. close": "310.0600",
            "5. volume": "4694275"
        },
        "2025-10-29": {
            "1. open": "312.7900",
            "2. high": "314.3300",
            "3. low": "307.5200",
            "4. close": "308.2100",
            "5. volume": "4135948"
        },
        "2025-10-28": {
            "1. open": "312.6000",
            "2. high": "319.3500",
            "3. low": "311.4100",
            "4. close": "312.5700",
            "5. volume": "6044770"
        },
        "2025-10-27": {
            "1. open": "307.8000",
            "2. high": "313.5000",
            "3. low": "302.8800",
            "4. close": "313.0900",
            "5. volume": "9868151"
        },
        "2025-10-24": {
            "1. open": "283.7700",
            "2. high": "310.7500",
            "3. low": "282.2100",
            "4. close": "307.4600",
            "5. volume": "16914243"
        },
        "2025-10-23": {
            "1. open": "264.9500",
            "2. high": "285.5791",
            "3. low": "263.5623",
            "4. close": "285.0000",
            "5. volume": "16676394"
        },
        "2025-10-22": {
            "1. open": "281.9900",
            "2. high": "289.1700",
            "3. low": "281.3500",
            "4. close": "287.5100",
            "5. volume": "10538480"
        },
        "2025-10-21": {
            "1. open": "283.3100",
            "2. high": "285.3100",
            "3. low": "281.6000",
            "4. close": "282.0500",
            "5. volume": "4080981"
        },
        "2025-10-20": {
            "1. open": "281.2500",
            "2. high": "285.5000",
            "3. low": "280.9600",
            "4. close": "283.6500",
            "5. volume": "3494336"
        },
        "2025-10-17": {
            "1. open": "276.1500",
            "2. high": "283.4000",
            "3. low": "275.3500",
            "4. close": "281.2800",
            "5. volume": "5309565"
        },
        "2025-10-16": {
            "1. open": "281.1100",
            "2. high": "282.5600",
            "3. low": "275.6000",
            "4. close": "275.9700",
            "5. volume": "2956923"
        }
        #it continues...
    }
}



## TIME_SERIES_DAILY_ADJUSTED
This API returns raw (as-traded) daily open/high/low/close/volume values, adjusted close values, and historical split/dividend events of the global equity specified, covering 20+ years of historical data. The OHLCV data is sometimes called "candles" in finance literature.


API Parameters
❚ Required: function

The time series of your choice. In this case, function=TIME_SERIES_DAILY_ADJUSTED

❚ Required: symbol

The name of the equity of your choice. For example: symbol=IBM

❚ Optional: outputsize

By default, outputsize=compact. Strings compact and full are accepted with the following specifications: compact returns only the latest 100 data points; full returns the full-length time series of 20+ years of historical data. The "compact" option is recommended if you would like to reduce the data size of each API call.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
Sample ticker traded in the United States
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=IBM&apikey=demo

https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=IBM&outputsize=full&apikey=demo

Sample ticker traded in UK - London Stock Exchange
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=TSCO.LON&outputsize=full&apikey=demo

Sample ticker traded in Canada - Toronto Stock Exchange
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=SHOP.TRT&outputsize=full&apikey=demo

Sample ticker traded in Canada - Toronto Venture Exchange
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=GPV.TRV&outputsize=full&apikey=demo

Sample ticker traded in Germany - XETRA
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MBG.DEX&outputsize=full&apikey=demo

Sample ticker traded in India - BSE
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=RELIANCE.BSE&outputsize=full&apikey=demo

Sample ticker traded in China - Shanghai Stock Exchange
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=600104.SHH&outputsize=full&apikey=demo

Sample ticker traded in China - Shenzhen Stock Exchange
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=000002.SHZ&outputsize=full&apikey=demo

The above is just a small sample of the 100,000+ symbols we support. Please refer to our Search Endpoint to look up any supported global stock, ETF, or mutual fund symbols of your interest.



## TIME_SERIES_WEEKLY
This API returns weekly time series (last trading day of each week, weekly open, weekly high, weekly low, weekly close, weekly volume) of the global equity specified, covering 20+ years of historical data.


API Parameters
❚ Required: function
The time series of your choice. In this case, function=TIME_SERIES_WEEKLY
❚ Required: symbol
The name of the equity of your choice. For example: symbol=IBM
❚ Optional: datatype
By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the weekly time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
❚ Required: apikey
Your API key. Claim your free API key here.

Example (click for JSON output)
https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol=IBM&apikey=demo

https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol=TSCO.LON&apikey=demo

Downloadable CSV file:
https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol=IBM&apikey=demo&datatype=csv



## TIME_SERIES_WEEKLY_ADJUSTED
This API returns weekly adjusted time series (last trading day of each week, weekly open, weekly high, weekly low, weekly close, weekly adjusted close, weekly volume, weekly dividend) of the global equity specified, covering 20+ years of historical data.


API Parameters
❚ Required: function
The time series of your choice. In this case, function=TIME_SERIES_WEEKLY_ADJUSTED
❚ Required: symbol
The name of the equity of your choice. For example: symbol=IBM
❚ Optional: datatype
By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the weekly time series in JSON format; csv returns the time series as a CSV (comma separated value) file
❚ Required: apikey
Your API key. Claim your free API key here.

{
    "Meta Data": {
        "1. Information": "Weekly Adjusted Prices and Volumes",
        "2. Symbol": "IBM",
        "3. Last Refreshed": "2025-11-06",
        "4. Time Zone": "US/Eastern"
    },
    "Weekly Adjusted Time Series": {
        "2025-11-06": {
            "1. open": "308.0000",
            "2. high": "315.4400",
            "3. low": "296.0000",
            "4. close": "312.4200",
            "5. adjusted close": "312.4200",
            "6. volume": "20956438",
            "7. dividend amount": "0.0000"
        },
        "2025-10-31": {
            "1. open": "307.8000",
            "2. high": "319.3500",
            "3. low": "301.6300",
            "4. close": "307.4100",
            "5. adjusted close": "307.4100",
            "6. volume": "32440643",
            "7. dividend amount": "0.0000"
        },
        "2025-10-24": {
            "1. open": "281.2500",
            "2. high": "310.7500",
            "3. low": "263.5623",
            "4. close": "307.4600",
            "5. adjusted close": "307.4600",
            "6. volume": "51704434",
            "7. dividend amount": "0.0000"
        },
        "2025-10-17": {
            "1. open": "279.7900",
            "2. high": "285.4500",
            "3. low": "272.5469",
            "4. close": "281.2800",
            "5. adjusted close": "281.2800",
            "6. volume": "19005226",
            "7. dividend amount": "0.0000"

            #it continues...
        }
    }
}

## TIME_SERIES_MONTHLY

This API returns monthly time series (last trading day of each month, monthly open, monthly high, monthly low, monthly close, monthly volume) of the global equity specified, covering 20+ years of historical data.


API Parameters
❚ Required: function

The time series of your choice. In this case, function=TIME_SERIES_MONTHLY

❚ Required: symbol

The name of the equity of your choice. For example: symbol=IBM

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the monthly time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=IBM&apikey=demo

https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=TSCO.LON&apikey=demo

Downloadable CSV file:
https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=IBM&apikey=demo&datatype=csv

Ex:

{
    "Meta Data": {
        "1. Information": "Monthly Prices (open, high, low, close) and Volumes",
        "2. Symbol": "IBM",
        "3. Last Refreshed": "2025-11-06",
        "4. Time Zone": "US/Eastern"
    },
    "Monthly Time Series": {
        "2025-11-06": {
            "1. open": "308.0000",
            "2. high": "315.4400",
            "3. low": "296.0000",
            "4. close": "312.4200",
            "5. volume": "20956438"
        },
        "2025-10-31": {
            "1. open": "280.2000",
            "2. high": "319.3500",
            "3. low": "263.5623",
            "4. close": "307.4100",
            "5. volume": "140510939"
        },
        "2025-09-30": {
            "1. open": "240.9000",
            "2. high": "288.8500",
            "3. low": "238.2500",
            "4. close": "282.1600",
            "5. volume": "110277863"
        },
        "2025-08-29": {
            "1. open": "251.4050",
            "2. high": "255.0000",
            "3. low": "233.3600",
            "4. close": "243.4900",
            "5. volume": "104957357"
        },
        "2025-07-31": {
            "1. open": "294.5500",
            "2. high": "295.6100",
            "3. low": "252.2200",
            "4. close": "253.1500",
            "5. volume": "109055173"
        },
        "2025-06-30": {
            "1. open": "257.8500",
            "2. high": "296.1600",
            "3. low": "257.2200",
            "4. close": "294.7800",
            "5. volume": "74395935"
        }
        #it continues...
    }
}

## TIME_SERIES_MONTHLY_ADJUSTED

This API returns monthly adjusted time series (last trading day of each month, monthly open, monthly high, monthly low, monthly close, monthly adjusted close, monthly volume, monthly dividend) of the equity specified, covering 20+ years of historical data.


API Parameters
❚ Required: function

The time series of your choice. In this case, function=TIME_SERIES_MONTHLY_ADJUSTED

❚ Required: symbol

The name of the equity of your choice. For example: symbol=IBM

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the monthly time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol=IBM&apikey=demo

https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol=TSCO.LON&apikey=demo

Downloadable CSV file:
https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol=IBM&apikey=demo&datatype=csv







## Quote Endpoint Trending

This endpoint returns the latest price and volume information for a ticker of your choice. You can specify one ticker per API request.

If you would like to query a large universe of tickers in bulk, you may want to try out our Realtime Bulk Quotes API, which accepts up to 100 tickers per API request.


API Parameters
❚ Required: function

The API function of your choice.

❚ Required: symbol

The symbol of the global ticker of your choice. For example: symbol=IBM.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the quote data in JSON format; csv returns the quote data as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=demo

https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=300135.SHZ&apikey=demo

Ex: {
    "Global Quote": {
        "01. symbol": "IBM",
        "02. open": "306.7500",
        "03. high": "315.4400",
        "04. low": "301.0900",
        "05. price": "312.4200",
        "06. volume": "5687955",
        "07. latest trading day": "2025-11-06",
        "08. previous close": "306.7700",
        "09. change": "5.6500",
        "10. change percent": "1.8418%"
    }
}



## Global Market Open & Close Status Utility

This endpoint returns the current market status (open vs. closed) of major trading venues for equities, forex, and cryptocurrencies around the world.


API Parameters
❚ Required: function

The API function of your choice. In this case, function=MARKET_STATUS

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=MARKET_STATUS&apikey=demo


{
    "endpoint": "Global Market Open & Close Status",
    "markets": [
        {
            "market_type": "Equity",
            "region": "United States",
            "primary_exchanges": "NASDAQ, NYSE, AMEX, BATS",
            "local_open": "09:30",
            "local_close": "16:15",
            "current_status": "closed",
            "notes": ""
        },
        {
            "market_type": "Equity",
            "region": "Canada",
            "primary_exchanges": "Toronto, Toronto Ventures",
            "local_open": "09:30",
            "local_close": "16:00",
            "current_status": "closed",
            "notes": ""
        },
        {
            "market_type": "Equity",
            "region": "United Kingdom",
            "primary_exchanges": "London",
            "local_open": "08:00",
            "local_close": "16:30",
            "current_status": "open",
            "notes": ""
        },
        {
            "market_type": "Equity",
            "region": "Germany",
            "primary_exchanges": "XETRA, Berlin, Frankfurt, Munich, Stuttgart",
            "local_open": "08:00",
            "local_close": "20:00",
            "current_status": "open",
            "notes": ""
        }
        #it continues for other markets...
    ]
}




# Options Data APIs
This suite of APIs provide realtime and historical US options data, spanning 15+ years of history with full market/volume coverage.
## Realtime Options Trending Premium
This API returns realtime US options data with full market coverage. Option chains are sorted by expiration dates in chronological order. Within the same expiration date, contracts are sorted by strike prices from low to high.


API Parameters
❚ Required: function

The time series of your choice. In this case, function=REALTIME_OPTIONS

❚ Required: symbol

The name of the equity of your choice. For example: symbol=IBM

❚ Optional: require_greeks
Enable greeks & implied volatility (IV) fields. By default, require_greeks=false. Set require_greeks=true to enable greeks & IVs in the API response.
❚ Optional: contract
The US options contract ID you would like to specify. By default, the contract parameter is not set and the entire option chain for a given symbol will be returned.
❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the options data in JSON format; csv returns the data as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
By default, the entire realtime option chain is returned
https://www.alphavantage.co/query?function=REALTIME_OPTIONS&symbol=IBM&apikey=demo

Set require_greeks=true to enable greeks & implied volatility (IV) fields in the API response
https://www.alphavantage.co/query?function=REALTIME_OPTIONS&symbol=IBM&require_greeks=true&apikey=demo

Query a specific contract (instead of the entire option chain) with greeks & IVs enabled
https://www.alphavantage.co/query?function=REALTIME_OPTIONS&symbol=IBM&require_greeks=true&contract=IBM270115C00390000&apikey=demo


💡 Tip: this is a premium API function. Subscribe to either the 600 requests per minute or the 1200 requests per minute premium membership plan to unlock realtime options data.


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=REALTIME_OPTIONS&symbol=IBM&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)


## Historical Options Trending

This API returns the full historical options chain for a specific symbol on a specific date, covering 15+ years of history. Implied volatility (IV) and common Greeks (e.g., delta, gamma, theta, vega, rho) are also returned. Option chains are sorted by expiration dates in chronological order. Within the same expiration date, contracts are sorted by strike prices from low to high.


API Parameters
❚ Required: function
The time series of your choice. In this case, function=HISTORICAL_OPTIONS
❚ Required: symbol
The name of the equity of your choice. For example: symbol=IBM
❚ Optional: date
By default, the date parameter is not set and the API will return data for the previous trading session. Any date later than 2008-01-01 is accepted. For example, date=2017-11-15.
❚ Optional: datatype
By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the options data in JSON format; csv returns the data as a CSV (comma separated value) file.
❚ Required: apikey
Your API key. Claim your free API key here.


Example (click for JSON output)
When the date parameter is not set, data from the previous trading session is returned
https://www.alphavantage.co/query?function=HISTORICAL_OPTIONS&symbol=IBM&apikey=demo

Specify a date to retrieve options data for any trading day in the past 15+ years (since 2008-01-01)
https://www.alphavantage.co/query?function=HISTORICAL_OPTIONS&symbol=IBM&date=2017-11-15&apikey=demo

Downloadable CSV file:
https://www.alphavantage.co/query?function=HISTORICAL_OPTIONS&symbol=IBM&date=2017-11-15&apikey=demo&datatype=csv


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=HISTORICAL_OPTIONS&symbol=IBM&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)






# Alpha Intelligence™
The APIs in this section contain advanced market intelligence built with our decades of expertise in AI, machine learning, and quantitative finance. We hope these highly differentiated alternative datasets can help turbocharge your trading strategy, market research, and financial software application to the next level.


Market News & Sentiment Trending
Looking for market news data to train your LLM models or to augment your trading strategy? You have just found it. This API returns live and historical market news & sentiment data from a large & growing selection of premier news outlets around the world, covering stocks, cryptocurrencies, forex, and a wide range of topics such as fiscal policy, mergers & acquisitions, IPOs, etc. This API, combined with our core stock API, fundamental data, and technical indicator APIs, can provide you with a 360-degree view of the financial market and the broader economy.


API Parameters
❚ Required: function

The function of your choice. In this case, function=NEWS_SENTIMENT

❚ Optional: tickers

The stock/crypto/forex symbols of your choice. For example: tickers=IBM will filter for articles that mention the IBM ticker; tickers=COIN,CRYPTO:BTC,FOREX:USD will filter for articles that simultaneously mention Coinbase (COIN), Bitcoin (CRYPTO:BTC), and US Dollar (FOREX:USD) in their content.

❚ Optional: topics

The news topics of your choice. For example: topics=technology will filter for articles that write about the technology sector; topics=technology,ipo will filter for articles that simultaneously cover technology and IPO in their content. Below is the full list of supported topics:

Blockchain: blockchain
Earnings: earnings
IPO: ipo
Mergers & Acquisitions: mergers_and_acquisitions
Financial Markets: financial_markets
Economy - Fiscal Policy (e.g., tax reform, government spending): economy_fiscal
Economy - Monetary Policy (e.g., interest rates, inflation): economy_monetary
Economy - Macro/Overall: economy_macro
Energy & Transportation: energy_transportation
Finance: finance
Life Sciences: life_sciences
Manufacturing: manufacturing
Real Estate & Construction: real_estate
Retail & Wholesale: retail_wholesale
Technology: technology
❚ Optional: time_from and time_to

The time range of the news articles you are targeting, in YYYYMMDDTHHMM format. For example: time_from=20220410T0130. If time_from is specified but time_to is missing, the API will return articles published between the time_from value and the current time.

❚ Optional: sort

By default, sort=LATEST and the API will return the latest articles first. You can also set sort=EARLIEST or sort=RELEVANCE based on your use case.

❚ Optional: limit

By default, limit=50 and the API will return up to 50 matching results. You can also set limit=1000 to output up to 1000 results.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
Querying news articles that mention the AAPL ticker.
https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey=demo

Querying news articles that simultaneously mention the Coinbase stock (COIN), Bitcoin (CRYPTO:BTC), and US Dollar (FOREX:USD) and are published on or after 2022-04-10, 1:30am UTC.
https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=COIN,CRYPTO:BTC,FOREX:USD&time_from=20220410T0130&limit=1000&apikey=demo

ex:{
    "items": "50",
    "sentiment_score_definition": "x <= -0.35: Bearish; -0.35 < x <= -0.15: Somewhat-Bearish; -0.15 < x < 0.15: Neutral; 0.15 <= x < 0.35: Somewhat_Bullish; x >= 0.35: Bullish",
    "relevance_score_definition": "0 < x <= 1, with a higher score indicating higher relevance.",
    "feed": [
        {
            "title": "Qualcomm Faces Long-Term Squeeze From Apple, Samsung Despite iPhone 17 Share, Meta Partnership: Analysts - Qualcomm  ( NASDAQ:QCOM ) ",
            "url": "https://www.benzinga.com/analyst-stock-ratings/reiteration/25/11/48696428/qualcomm-faces-long-term-squeeze-from-apple-samsung-despite-iphone-17-share-met",
            "time_published": "20251106T173834",
            "authors": [
                "Anusuya Lahiri"
            ],
            "summary": "Qualcomm Inc ( NASDAQ:QCOM ) delivered a strong quarter, driven by double-digit growth across its core chip business signaling continued demand in premium Android devices and emerging artificial intelligence-driven technologies.",
            "banner_image": "https://cdn.benzinga.com/files/images/story/2025/11/06/Timisoara--Romania---April-05--2020-Clos.jpeg?width=1200&height=800&fit=crop",
            "source": "Benzinga",
            "category_within_source": "Trading",
            "source_domain": "www.benzinga.com",
            "topics": [
                {
                    "topic": "Financial Markets",
                    "relevance_score": "0.650727"
                },
                {
                    "topic": "Manufacturing",
                    "relevance_score": "0.333333"
                },
                {
                    "topic": "Earnings",
                    "relevance_score": "0.999999"
                },
                {
                    "topic": "Technology",
                    "relevance_score": "0.333333"
                },
                {
                    "topic": "Finance",
                    "relevance_score": "0.333333"
                }
            ],
            "overall_sentiment_score": 0.278571,
            "overall_sentiment_label": "Somewhat-Bullish",
            "ticker_sentiment": [
                {
                    "ticker": "SSNLF",
                    "relevance_score": "0.100729",
                    "ticker_sentiment_score": "0.08422",
                    "ticker_sentiment_label": "Neutral"
                },
                {
                    "ticker": "META",
                    "relevance_score": "0.050465",
                    "ticker_sentiment_score": "0.193331",
                    "ticker_sentiment_label": "Somewhat-Bullish"
                },
                {
                    "ticker": "AAPL",
                    "relevance_score": "0.050465",
                    "ticker_sentiment_score": "-0.009982",
                    "ticker_sentiment_label": "Neutral"
                },
                {
                    "ticker": "BAC",
                    "relevance_score": "0.050465",
                    "ticker_sentiment_score": "0.202348",
                    "ticker_sentiment_label": "Somewhat-Bullish"
                },
                {
                    "ticker": "XIACY",
                    "relevance_score": "0.050465",
                    "ticker_sentiment_score": "-0.009982",
                    "ticker_sentiment_label": "Neutral"
                },
                {
                    "ticker": "QCOM",
                    "relevance_score": "0.431065",
                    "ticker_sentiment_score": "0.290905",
                    "ticker_sentiment_label": "Somewhat-Bullish"
                }
            ]
        },
        {
            "title": "Investigating Apple's Standing In Technology Hardware, Storage & Peripherals Industry Compared To Competitors - Apple  ( NASDAQ:AAPL ) ",
            "url": "https://www.benzinga.com/insights/news/25/11/48688455/investigating-apples-standing-in-technology-hardware-storage-amp-peripherals-industry-compared-to-c",
            "time_published": "20251106T150118",
            "authors": [
                "Benzinga Insights"
            ],
            "summary": "In the dynamic and cutthroat world of business, conducting thorough company analysis is essential for investors and industry experts. In this article, we will undertake a comprehensive industry comparison, evaluating Apple ( NASDAQ:AAPL ) and its primary competitors in the Technology Hardware, ...",
            "banner_image": "https://www.benzinga.com/next-assets/images/benzinga-schema-image-default.png",
            "source": "Benzinga",
            "category_within_source": "Markets",
            "source_domain": "www.benzinga.com",
            "topics": [
                {
                    "topic": "Earnings",
                    "relevance_score": "0.875462"
                },
                {
                    "topic": "Technology",
                    "relevance_score": "1.0"
                },
                {
                    "topic": "Financial Markets",
                    "relevance_score": "0.5855"
                }
            ],
            "overall_sentiment_score": 0.249276,
            "overall_sentiment_label": "Somewhat-Bullish",
            "ticker_sentiment": [
                {
                    "ticker": "AAPL",
                    "relevance_score": "0.480056",
                    "ticker_sentiment_score": "0.303491",
                    "ticker_sentiment_label": "Somewhat-Bullish"
                }
            ]
        },
        {
            "title": "How To Trade SPY, Top Tech Stocks Using Technical Analysis",
            "url": "https://www.benzinga.com/Opinion/25/11/48685405/how-to-trade-spy-top-tech-stocks-using-technical-analysis-55",
            "time_published": "20251106T134709",
            "authors": [
                "RIPS"
            ],
            "summary": "Thursday brings another session with limited scheduled economic data due to the ongoing US government shutdown. At 11AM ET, New York Fed President John Williams will speak on the natural rate of interest. At 11:30AM ET, the Treasury will hold a 4 and 8 Week Bill Auction.",
            "banner_image": "https://www.benzinga.com/next-assets/images/benzinga-schema-image-default.png",
            "source": "Benzinga",
            "category_within_source": "Trading",
            "source_domain": "www.benzinga.com",
            "topics": [
                {
                    "topic": "Technology",
                    "relevance_score": "0.5"
                },
                {
                    "topic": "Financial Markets",
                    "relevance_score": "0.266143"
                },
                {
                    "topic": "Manufacturing",
                    "relevance_score": "0.5"
                }
            ],
            "overall_sentiment_score": 0.154578,
            "overall_sentiment_label": "Somewhat-Bullish",
            "ticker_sentiment": [
                {
                    "ticker": "MSFT",
                    "relevance_score": "0.175859",
                    "ticker_sentiment_score": "0.109722",
                    "ticker_sentiment_label": "Neutral"
                },
                {
                    "ticker": "NVDA",
                    "relevance_score": "0.10607",
                    "ticker_sentiment_score": "0.070253",
                    "ticker_sentiment_label": "Neutral"
                },
                {
                    "ticker": "AAPL",
                    "relevance_score": "0.141102",
                    "ticker_sentiment_score": "0.144517",
                    "ticker_sentiment_label": "Neutral"
                },
                {
                    "ticker": "TSLA",
                    "relevance_score": "0.141102",
                    "ticker_sentiment_score": "0.075603",
                    "ticker_sentiment_label": "Neutral"
                }
            ]
        },
        {
            "title": "Take Your Big Tech Investing To The Next Level With The Magnificent 10 Index From Cboe - Learn How At This Webinar - Apple  ( NASDAQ:AAPL ) , Advanced Micro Devices  ( NASDAQ:AMD ) ",
            "url": "https://www.benzinga.com/partner/news/25/11/48684880/take-your-big-tech-investing-to-the-next-level-with-the-magnificent-10-index-from-cboe-learn-how-at",
            "time_published": "20251106T133140",
            "authors": [
                "Meg Flippin"
            ],
            "summary": "Cboe and Benzinga will host an exclusive pre-launch webinar on Nov. 13 at 11 a.m. ET to introduce the Cboe Magnificent 10 Index ( MGTN ) - a new innovative benchmark capturing the pulse of U.S. large-cap technology stocks driving overall growth.",
            "banner_image": "https://cdn.benzinga.com/files/images/story/2025/11/06/Screenshot-2025-11-06-at-6-56-41PM.png?width=1200&height=800&fit=crop",
            "source": "Benzinga",
            "category_within_source": "Markets",
            "source_domain": "www.benzinga.com",
            "topics": [
                {
                    "topic": "Technology",
                    "relevance_score": "0.5"
                },
                {
                    "topic": "Financial Markets",
                    "relevance_score": "0.360215"
                },
                {
                    "topic": "Manufacturing",
                    "relevance_score": "0.5"
                }
            ],
            "overall_sentiment_score": 0.282805,
            "overall_sentiment_label": "Somewhat-Bullish",
            "ticker_sentiment": [
                {
                    "ticker": "MSFT",
                    "relevance_score": "0.07913",
                    "ticker_sentiment_score": "0.0",
                    "ticker_sentiment_label": "Neutral"
                },
                {
                    "ticker": "GOOG",
                    "relevance_score": "0.07913",
                    "ticker_sentiment_score": "0.0",
                    "ticker_sentiment_label": "Neutral"
                },
                {
                    "ticker": "META",
                    "relevance_score": "0.07913",
                    "ticker_sentiment_score": "0.0",
                    "ticker_sentiment_label": "Neutral"
                },
                {
                    "ticker": "NVDA",
                    "relevance_score": "0.07913",
                    "ticker_sentiment_score": "0.0",
                    "ticker_sentiment_label": "Neutral"
                },
                {
                    "ticker": "AAPL",
                    "relevance_score": "0.07913",
                    "ticker_sentiment_score": "-0.028397",
                    "ticker_sentiment_label": "Neutral"
                },
                {
                    "ticker": "AVGO",
                    "relevance_score": "0.07913",
                    "ticker_sentiment_score": "0.234486",
                    "ticker_sentiment_label": "Somewhat-Bullish"
                },
                {
                    "ticker": "TSLA",
                    "relevance_score": "0.07913",
                    "ticker_sentiment_score": "0.111932",
                    "ticker_sentiment_label": "Neutral"
                },
                {
                    "ticker": "AMD",
                    "relevance_score": "0.07913",
                    "ticker_sentiment_score": "0.234486",
                    "ticker_sentiment_label": "Somewhat-Bullish"
                },
                {
                    "ticker": "PLTR",
                    "relevance_score": "0.07913",
                    "ticker_sentiment_score": "0.234486",
                    "ticker_sentiment_label": "Somewhat-Bullish"
                }
            ]
        },
        {
            "title": "Apple's Q4 Earnings Beat, $1 Billion Google AI Deal Fuel Surge In Growth Rankings - Alphabet  ( NASDAQ:GOOG ) , Apple  ( NASDAQ:AAPL ) ",
            "url": "https://www.benzinga.com/markets/equities/25/11/48683559/apples-q4-earnings-beat-1-billion-google-ai-deal-fuel-surge-in-growth-rankings",
            "time_published": "20251106T125121",
            "authors": [
                "Rishabh Mishra"
            ],
            "summary": "Apple Inc. ( NASDAQ:AAPL ) is navigating a pivotal moment in its growth story, as its latest growth percentile ranking shows both dramatic improvement and underlying volatility.",
            "banner_image": "https://cdn.benzinga.com/files/images/story/2025/11/06/Bangkok--Thailand---October-22--2023---A.jpeg?width=1200&height=800&fit=crop",
            "source": "Benzinga",
            "category_within_source": "General",
            "source_domain": "www.benzinga.com",
            "topics": [
                {
                    "topic": "Earnings",
                    "relevance_score": "0.77141"
                },
                {
                    "topic": "Technology",
                    "relevance_score": "1.0"
                },
                {
                    "topic": "Financial Markets",
                    "relevance_score": "0.214378"
                }
            ],
            "overall_sentiment_score": 0.279154,
            "overall_sentiment_label": "Somewhat-Bullish",
            "ticker_sentiment": [
                {
                    "ticker": "GOOG",
                    "relevance_score": "0.191929",
                    "ticker_sentiment_score": "0.0",
                    "ticker_sentiment_label": "Neutral"
                },
                {
                    "ticker": "AAPL",
                    "relevance_score": "0.533842",
                    "ticker_sentiment_score": "0.438922",
                    "ticker_sentiment_label": "Bullish"
                }
            ]
        }, ...
    ]
}







# Earnings Call Transcript Trending
This API returns the earnings call transcript for a given company in a specific quarter, covering over 15 years of history and enriched with LLM-based sentiment signals.


API Parameters
❚ Required: function

The function of your choice. In this case, function=EARNINGS_CALL_TRANSCRIPT

❚ Required: symbol

The symbol of the ticker of your choice. For example: symbol=IBM.

❚ Required: quarter

Fiscal quarter in YYYYQM format. For example: quarter=2024Q1. Any quarter since 2010Q1 is supported.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=EARNINGS_CALL_TRANSCRIPT&symbol=IBM&quarter=2024Q1&apikey=demo

Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=EARNINGS_CALL_TRANSCRIPT&symbol=IBM&quarter=2024Q1&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

{
    "symbol": "IBM",
    "quarter": "2024Q1",
    "transcript": [
        {
            "speaker": "Olympia McNerney",
            "title": "Global Head of Investor Relations",
            "content": "Thank you. I'd like to welcome you to IBM's First Quarter 2024 Earnings Presentation. I'm Olympia McNerney, and I'm here today with Arvind Krishna, IBM's Chairman and Chief Executive Officer; and Jim Kavanaugh, IBM's Senior Vice President and Chief Financial Officer. We'll post today's prepared remarks on the IBM investor website within a couple of hours, and a replay will be available by this time tomorrow. To provide additional information to our investors, our presentation includes certain non-GAAP measures. For example, all of our references to revenue and signings growth are at constant currency. We provided reconciliation charts for these and other non-GAAP financial measures at the end of the presentation, which is posted to our investor website. Finally, some comments made in this presentation may be considered forward-looking under the Private Securities Litigation Reform Act of 1995. These statements involve factors that could cause our actual results to differ materially. Additional information about these factors is included in the company's SEC filings. So with that, I'll turn the call over to Arvind.",
            "sentiment": "0.6"
        },
        {
            "speaker": "Arvind Krishna",
            "title": "CEO",
            "content": "Thank you for joining us. In the first quarter, we had solid performance across revenue and cash flow. These results are further proof of the quality of our portfolio and our hybrid cloud and AI strategy. We had good performance in Software, at the high end of our model; continued strength in Infrastructure, above our model; while Consulting was below model. On a relative basis, Consulting outperformed the market. Our cash flow generation is the strongest first quarter level we have reported in many years. This performance speaks to the strength of our diversified business model. Before we get into more detail on the quarter, let me address the announcement of our agreement to acquire HashiCorp, a company we have partnered with for a long time and believe is a tremendous strategic fit with IBM. Enterprise clients are wrestling with an unprecedented expansion in infrastructure applications across public and private cloud as well as on-prem environments, making this the ideal time to pursue this acquisition. As generative AI deployment accelerates alongside traditional workloads, developers are working with increasingly heterogeneous, dynamic, and complex infrastructure strategies. HashiCorp has a proven track record of helping clients manage the complexity of today's infrastructure by automating, orchestrating, and securing hybrid and multi-cloud environments. HashiCorp is a great strategic addition to our portfolio, extending Red Hat's hybrid cloud capabilities to provide end-to-end automated infrastructure and security lifecycle management. HashiCorp's technology is foundational to enabling the transition to hybrid and multi-cloud, and Terraform is the industry standard for infrastructure automation for these environments. With security top of mind for every enterprise, Vault is a powerful secrets management offering to automate identity security across applications. The combination will also bolster our leading IT automation platform to address the sprawling complexity of AI-driven application and infrastructure growth. HashiCorp's products have wide-scale adoption in the developer community, highlighting the pervasive nature of their technology used by over 85% of the Fortune 500 and downloaded over 0.5 billion times. The acquisition of HashiCorp builds on IBM's commitment to industry collaboration, the developer community, and open source hybrid cloud and AI innovation. Today's acquisition is consistent with our M&A strategy. We have taken a disciplined approach to M&A, and HashiCorp aligns well across all our key criteria to continue to focus and strengthen our portfolio on hybrid cloud and AI, deliver synergies with the rest of IBM, and be near-term accretive to free cash flow. I will now turn it to Jim to discuss the financial implications.",
            "sentiment": "0.7"
        },
        {
            "speaker": "James Kavanaugh",
            "title": "CFO",
            "content": "Thank you, Arvind. Let me start with the details of the transaction. We have agreed to acquire HashiCorp for $6.4 billion in enterprise value to be funded by cash on hand. The transaction was approved by HashiCorp's Board of Directors. Closing is anticipated by the end of 2024, subject to approval by HashiCorp's shareholders, regulatory approvals, and other customary closing conditions. We have been executing a disciplined capital allocation strategy, and the acquisition of HashiCorp meets all of our criteria, including strategic fit, as Arvind just walked through, synergies across IBM, and financial accretion. Let me start by addressing synergies. We see multiple drivers of product synergies within IBM and accelerating growth for HashiCorp. Product synergies span across multiple strategic growth areas for IBM, including Red Hat, watsonx, data security, IT automation, and consulting. For example, the powerful combination of Red Hat's Ansible automation platform's configuration management and Terraform's automation will simplify provisioning and configuration of applications across hybrid cloud environments. We are well positioned to drive growth for HashiCorp by leveraging IBM's enterprise incumbency and global reach. With 70% of the revenue today coming from the U.S., the opportunity to scale HashiCorp across IBM's operations in 175 countries is significant. We also believe we can accelerate HashiCorp's adoption with IBM clients. To put this in perspective, only about 20% of the Forbes Global 2000 are HashiCorp customers and just 25% of HashiCorp customers result in more than $100,000 in annual recurring revenue, underscoring the opportunity to better monetize and upsell their products. Bringing it all together, the acquisition allows us to deliver a more comprehensive hybrid cloud offering to enterprise clients, enhancing IBM's ability to capture global cloud opportunities. This will drive a higher growth profile over time. Finally, we expect to realize operating efficiencies and expect the transaction to be accretive to adjusted EBITDA within the first full year post-close and to free cash flow in year two. Significant near-term cost synergies underpin the financial profile of the transaction, while product synergies represent further upside. We are very comfortable with our strong balance sheet, liquidity profile, and solid investment-grade rating and remain committed to our dividend policy. I'll now turn it back to Arvind.",
            "sentiment": "0.5"
        },
        ...
    ]
}





# Top Gainers, Losers, and Most Actively Traded Tickers (US Market)

This endpoint returns the top 20 gainers, losers, and the most active traded tickers in the US market.


API Parameters
❚ Required: function

The API function of your choice. In this case, function=TOP_GAINERS_LOSERS

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey=demo

{
    "metadata": "Top gainers, losers, and most actively traded US tickers",
    "last_updated": "2025-11-06 16:16:00 US/Eastern",
    "top_gainers": [
        {
            "ticker": "JGH^",
            "price": "0.0108",
            "change_amount": "0.0062",
            "change_percentage": "134.7826%",
            "volume": "393947"
        },
        {
            "ticker": "BLLN",
            "price": "108.94",
            "change_amount": "48.94",
            "change_percentage": "81.5667%",
            "volume": "1423738"
        },
        {
            "ticker": "BIYA",
            "price": "0.4782",
            "change_amount": "0.2031",
            "change_percentage": "73.8277%",
            "volume": "375866495"
        },
        {
            "ticker": "FRGE",
            "price": "44.06",
            "change_amount": "17.94",
            "change_percentage": "68.683%",
            "volume": "4511544"
        },
        {
            "ticker": "OPP^",
            "price": "0.0149",
            "change_amount": "0.0059",
            "change_percentage": "65.5556%",
            "volume": "1960588"
        },
        {
            "ticker": "MSPRZ",
            "price": "0.0347",
            "change_amount": "0.0135",
            "change_percentage": "63.6792%",
            "volume": "22323"
        }
        #it continues...
    ]
}

## Insider Transactions Trending
This API returns the latest and historical insider transactions made by key stakeholders (e.g., founders, executives, board members, etc.) of a specific company.


API Parameters
❚ Required: function

The function of your choice. In this case, function=INSIDER_TRANSACTIONS

❚ Required: symbol

The symbol of the ticker of your choice. For example: symbol=IBM.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=INSIDER_TRANSACTIONS&symbol=IBM&apikey=demo

Ex:
{
    "data": [
        {
            "transaction_date": "2025-09-30",
            "ticker": "IBM",
            "executive": "GORSKY, ALEX",
            "executive_title": "Director",
            "security_type": "Promised Fee Share",
            "acquisition_or_disposal": "A",
            "shares": "381.0",
            "share_price": "282.16"
        },
        {
            "transaction_date": "2025-09-30",
            "ticker": "IBM",
            "executive": "POLLACK, MARTHA E",
            "executive_title": "Director",
            "security_type": "Promised Fee Share",
            "acquisition_or_disposal": "A",
            "shares": "209.0",
            "share_price": "282.16"
        },
        {
            "transaction_date": "2025-09-30",
            "ticker": "IBM",
            "executive": "MIEBACH, MICHAEL",
            "executive_title": "Director",
            "security_type": "Promised Fee Share",
            "acquisition_or_disposal": "A",
            "shares": "324.0",
            "share_price": "282.16"
        },
        {
            "transaction_date": "2025-09-30",
            "ticker": "IBM",
            "executive": "MCNABB, FREDERICK WILLIAM III",
            "executive_title": "Director",
            "security_type": "Promised Fee Share",
            "acquisition_or_disposal": "A",
            "shares": "324.0",
            "share_price": "282.16"
        },
        ...
    ]
}   






## Advanced Analytics (Fixed Window)
This endpoint returns a rich set of advanced analytics metrics (e.g., total return, variance, auto-correlation, etc.) for a given time series over a fixed temporal window.


API Parameters
❚ Required: function

The function of your choice. In this case, function=ANALYTICS_FIXED_WINDOW

❚ Required: SYMBOLS

A list of symbols for the calculation. It can be a comma separated list of symbols as a string. Free API keys can specify up to 5 symbols per API request. Premium API keys can specify up to 50 symbols per API request.

❚ Required: RANGE

This is the date range for the series being requested. By default, the date range is the full set of data for the equity history. This can be further modified by the LIMIT variable.

RANGE can take certain text values as inputs. They are:

full
{N}day
{N}week
{N}month
{N}year
For intraday time series, the following RANGE values are also accepted:

{N}minute
{N}hour
Aside from the “full” value which represents the entire time series, the other values specify an interval to return the series for as measured backwards from the current date/time.

To specify start & end dates for your analytics calcuation, simply add two RANGE parameters in your API request. For example: RANGE=2023-07-01&RANGE=2023-08-31 or RANGE=2020-12-01T00:04:00&RANGE=2020-12-06T23:59:59 with minute-level precision for intraday analytics. If the end date is missing, the end date is assumed to be the last trading date. In addition, you can request a full month of data by using YYYY-MM format like 2020-12. One day of intraday data can be requested by using YYYY-MM-DD format like 2020-12-06

❚ Optional: OHLC

This allows you to choose which open, high, low, or close field the calculation will be performed on. By default, OHLC=close. Valid values for these fields are open, high, low, close.

❚ Required: INTERVAL

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, DAILY, WEEKLY, MONTHLY.

❚ Required: CALCULATIONS

A comma separated list of the analytics metrics you would like to calculate:

MIN: The minimum return (largest negative or smallest positive) for all values in the series
MAX: The maximum return for all values in the series
MEAN: The mean of all returns in the series
MEDIAN: The median of all returns in the series
CUMULATIVE_RETURN: The total return from the beginning to the end of the series range
VARIANCE: The population variance of returns in the series range. Optionally, you can use VARIANCE(annualized=True)to normalize the output to an annual value. By default, the variance is not annualized.
STDDEV: The population standard deviation of returns in the series range for each symbol. Optionally, you can use STDDEV(annualized=True)to normalize the output to an annual value. By default, the standard deviation is not annualized.
MAX_DRAWDOWN: Largest peak to trough interval for each symbol in the series range
HISTOGRAM: For each symbol, place the observed total returns in bins. By default, bins=10. Use HISTOGRAM(bins=20) to specify a custom bin value (e.g., 20).
AUTOCORRELATION: For each symbol place, calculate the autocorrelation for the given lag (e.g., the lag in neighboring points for the autocorrelation calculation). By default, lag=1. Use AUTOCORRELATION(lag=2) to specify a custom lag value (e.g., 2).
COVARIANCE: Returns a covariance matrix for the input symbols. Optionally, you can use COVARIANCE(annualized=True)to normalize the output to an annual value. By default, the covariance is not annualized.
CORRELATION: Returns a correlation matrix for the input symbols, using the PEARSON method as default. You can also specify the KENDALL or SPEARMAN method through CORRELATION(method=KENDALL) or CORRELATION(method=SPEARMAN), respectively.
❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
For AAPL, MSFT, and IBM, calculate the mean & standard deviation of their returns based on daily close prices between 2023-07-01 and 2023-08-31, along with a correlation matrix among the three tickers.
https://www.alphavantage.co/query?function=ANALYTICS_FIXED_WINDOW&SYMBOLS=AAPL,MSFT,IBM&RANGE=2023-07-01&RANGE=2023-08-31&INTERVAL=DAILY&OHLC=close&CALCULATIONS=MEAN,STDDEV,CORRELATION&apikey=demo

Ex:
{
    "meta_data": {
        "symbols": "MSFT,AAPL,IBM",
        "min_dt": "2023-07-03",
        "max_dt": "2023-08-31",
        "ohlc": "Close",
        "interval": "DAILY"
    },
    "payload": {
        "RETURNS_CALCULATIONS": {
            "MEAN": {
                "MSFT": -0.0005772663739571029,
                "AAPL": -0.0004591101507972854,
                "IBM": 0.0025422876074108706
            },
            "STDDEV": {
                "MSFT": 0.014401849168320926,
                "AAPL": 0.012845925557901618,
                "IBM": 0.007436311891614325
            },
            "CORRELATION": {
                "index": [
                    "MSFT",
                    "AAPL",
                    "IBM"
                ],
                "correlation": [
                    [
                        1.0
                    ],
                    [
                        0.3810754257,
                        1.0
                    ],
                    [
                        -0.0583508133,
                        0.0342698827,
                        1.0
                    ]
                ]
            }
        }
    }
}





## Advanced Analytics (Sliding Window) Trending
This endpoint returns a rich set of advanced analytics metrics (e.g., total return, variance, auto-correlation, etc.) for a given time series over sliding time windows. For example, we can calculate a moving variance over 5 years with a window of 100 points to see how the variance changes over time.


API Parameters
❚ Required: function

The function of your choice. In this case, function=ANALYTICS_SLIDING_WINDOW

❚ Required: SYMBOLS

A list of symbols for the calculation. It can be a comma separated list of symbols as a string. Free API keys can specify up to 5 symbols per API request. Premium API keys can specify up to 50 symbols per API request.

❚ Required: RANGE

This is the date range for the series being requested. By default, the date range is the full set of data for the equity history. This can be further modified by the LIMIT variable.

RANGE can take certain text values as inputs. They are:

full
{N}day
{N}week
{N}month
{N}year
For intraday time series, the following RANGE values are also accepted:

{N}minute
{N}hour
Aside from the “full” value which represents the entire time series, the other values specify an interval to return the series for as measured backwards from the current date/time.

To specify start & end dates for your analytics calcuation, simply add two RANGE parameters in your API request. For example: RANGE=2023-07-01&RANGE=2023-08-31 or RANGE=2020-12-01T00:04:00&RANGE=2020-12-06T23:59:59 with minute-level precision for intraday analytics. If the end date is missing, the end date is assumed to be the last trading date. In addition, you can request a full month of data by using YYYY-MM format like 2020-12. One day of intraday data can be requested by using YYYY-MM-DD format like 2020-12-06

❚ Optional: OHLC

This allows you to choose which open, high, low, or close field the calculation will be performed on. By default, OHLC=close. Valid values for these fields are open, high, low, close.

❚ Required: INTERVAL

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, DAILY, WEEKLY, MONTHLY.

❚ Required: WINDOW_SIZE

An integer representing the size of the moving window. A hard lower boundary of 10 has been set though it is recommended to make this window larger to make sure the running calculations are statistically significant.

❚ Required: CALCULATIONS

A comma separated list of the analytics metrics you would like to calculate. Free API keys can specify 1 metric to be calculated per API request. Premium API keys can specify multiple metrics to be calculated simultaneously per API request.

MEAN: The mean of all returns in the series
MEDIAN: The median of all returns in the series
CUMULATIVE_RETURN: The total return from the beginning to the end of the series range
VARIANCE: The population variance of returns in the series range. Optionally, you can use VARIANCE(annualized=True)to normalize the output to an annual value. By default, the variance is not annualized.
STDDEV: The population standard deviation of returns in the series range for each symbol. Optionally, you can use STDDEV(annualized=True)to normalize the output to an annual value. By default, the standard deviation is not annualized.
COVARIANCE: Returns a covariance matrix for the input symbols. Optionally, you can use COVARIANCE(annualized=True)to normalize the output to an annual value. By default, the covariance is not annualized.
CORRELATION: Returns a correlation matrix for the input symbols, using the PEARSON method as default. You can also specify the KENDALL or SPEARMAN method through CORRELATION(method=KENDALL) or CORRELATION(method=SPEARMAN), respectively.
❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
For AAPL and IBM, calculate the running mean & annualized standard deviation of their returns based on daily close prices in the trailing 2 months, with a sliding window size of 20.
https://www.alphavantage.co/query?function=ANALYTICS_SLIDING_WINDOW&SYMBOLS=AAPL,IBM&RANGE=2month&INTERVAL=DAILY&OHLC=close&WINDOW_SIZE=20&CALCULATIONS=MEAN,STDDEV(annualized=True)&apikey=demo

Ex:
{
    "meta_data": {
        "symbols": "IBM,AAPL",
        "window_size": 20,
        "min_dt": "2025-09-08",
        "max_dt": "2025-11-06",
        "ohlc": "Close",
        "interval": "DAILY"
    },
    "payload": {
        "RETURNS_CALCULATIONS": {
            "MEAN": {
                "RUNNING_MEAN": {
                    "IBM": {
                        "2025-10-06": 0.0062452633585444615,
                        "2025-10-07": 0.006424405839795711,
                        "2025-10-08": 0.006104393229902194,
                        "2025-10-09": 0.0058666249969423715,
                        "2025-10-10": 0.004755301006591728,
                        "2025-10-13": 0.00409491843019788,
                        "2025-10-14": 0.003652165066739088,
                        "2025-10-15": 0.004182156651535973,
                        "2025-10-16": 0.002188361221415469,
                        "2025-10-17": 0.002886271371616378,
                        "2025-10-20": 0.002374751959713006,
                        "2025-10-21": 0.0019324164887061014,
                        "2025-10-22": 0.0037653755272678115,
                        "2025-10-23": 0.00072916052706129,
                        "2025-10-24": 0.004159633632793214,
                        "2025-10-27": 0.005868348209326385,
                        "2025-10-28": 0.0053635751879101915,
                        "2025-10-29": 0.0038988362636282635,
                        "2025-10-30": 0.004158815294508994,
                        "2025-10-31": 0.003443741484810009,
                        "2025-11-03": 0.0028257837736167524,
                        "2025-11-04": 0.001420375689318204,
                        "2025-11-05": 0.003154586478149579,
                        "2025-11-06": 0.004287936421232863
                    },
                    "AAPL": {
                        "2025-10-06": 0.003939477557949883,
                        "2025-10-07": 0.00464054292726136,
                        "2025-10-08": 0.0065615311972016645,
                        "2025-10-09": 0.005068325356897119,
                        "2025-10-10": 0.0024640729031377095,
                        "2025-10-13": 0.0023894933180622357,
                        "2025-10-14": 0.0021054062956405275,
                        "2025-10-15": 0.002245872947022426,
                        "2025-10-16": 0.0020990996753848744,
                        "2025-10-17": 0.0014754271342478531,
                        "2025-10-20": 0.0012925780400969145,
                        "2025-10-21": 0.0017157954595694359,
                        "2025-10-22": 0.001310401351644569,
                        "2025-10-23": 0.0006253620300467444,
                        "2025-10-24": 0.001523904987519753,
                        "2025-10-27": 0.0028650653055901864,
                        "2025-10-28": 0.0028611027114785028,
                        "2025-10-29": 0.0028301962880318164,
                        "2025-10-30": 0.002816529812308266,
                        "2025-10-31": 0.002453708787035269,
                        "2025-11-03": 0.0024673308223599035,
                        "2025-11-04": 0.0026922168673361945,
                        "2025-11-05": 0.0024027164231886,
                        "2025-11-06": 0.0031131220449293895
                    }
                },
                "window_start": {
                    "2025-10-06": "2025-09-08",
                    "2025-10-07": "2025-09-09",
                    "2025-10-08": "2025-09-10",
                    "2025-10-09": "2025-09-11",
                    "2025-10-10": "2025-09-12",
                    "2025-10-13": "2025-09-15",
                    "2025-10-14": "2025-09-16",
                    "2025-10-15": "2025-09-17",
                    "2025-10-16": "2025-09-18",
                    "2025-10-17": "2025-09-19",
                    "2025-10-20": "2025-09-22",
                    "2025-10-21": "2025-09-23",
                    "2025-10-22": "2025-09-24",
                    "2025-10-23": "2025-09-25",
                    "2025-10-24": "2025-09-26",
                    "2025-10-27": "2025-09-29",
                    "2025-10-28": "2025-09-30",
                    "2025-10-29": "2025-10-01",
                    "2025-10-30": "2025-10-02",
                    "2025-10-31": "2025-10-03",
                    "2025-11-03": "2025-10-06",
                    "2025-11-04": "2025-10-07",
                    "2025-11-05": "2025-10-08",
                    "2025-11-06": "2025-10-09"
                }
            },
            "STDDEV(ANNUALIZED=TRUE)": {
                "RUNNING_STDDEV": {
                    "IBM": {
                        "2025-10-06": 0.2362675820673905,
                        "2025-10-07": 0.23764868084304774,
                        "2025-10-08": 0.24370368598215958,
                        "2025-10-09": 0.24562786049872481,
                        "2025-10-10": 0.2780513219432814,
                        "2025-10-13": 0.27803992350227913,
                        "2025-10-14": 0.27936333232838284,
                        "2025-10-15": 0.2828981373416878,
                        "2025-10-16": 0.28338280709905667,
                        "2025-10-17": 0.28935528896670276,
                        "2025-10-20": 0.28445334599116445,
                        "2025-10-21": 0.28577127805057145,
                        "2025-10-22": 0.28281387273198877,
                        "2025-10-23": 0.22432147884879985,
                        "2025-10-24": 0.3507655469875887,
                        "2025-10-27": 0.346081945405431,
                        "2025-10-28": 0.3469002845045554,
                        "2025-10-29": 0.3510598700140042,
                        "2025-10-30": 0.3509429864266524,
                        "2025-10-31": 0.3536015588559145,
                        "2025-11-03": 0.35609125173753486,
                        "2025-11-04": 0.35688760213116505,
                        "2025-11-05": 0.3569463641865348,
                        "2025-11-06": 0.359627098430681
                    },
                    "AAPL": {
                        "2025-10-06": 0.2540154553224411,
                        "2025-10-07": 0.24544213548655017,
                        "2025-10-08": 0.20538925022017476,
                        "2025-10-09": 0.21690289746277663,
                        "2025-10-10": 0.25123695006877644,
                        "2025-10-13": 0.2506330345448446,
                        "2025-10-14": 0.25033648909375883,
                        "2025-10-15": 0.2507259152699788,
                        "2025-10-16": 0.2519451121477427,
                        "2025-10-17": 0.2364943492986267,
                        "2025-10-20": 0.22859155848154616,
                        "2025-10-21": 0.22685153469372638,
                        "2025-10-22": 0.23302687220133264,
                        "2025-10-23": 0.22530196797420543,
                        "2025-10-24": 0.22772275577657466,
                        "2025-10-27": 0.23814792802424387,
                        "2025-10-28": 0.23815680309962461,
                        "2025-10-29": 0.23815465630078628,
                        "2025-10-30": 0.23810235091969925,
                        "2025-10-31": 0.2391759113407558,
                        "2025-11-03": 0.23906854638185782,
                        "2025-11-04": 0.23879601524730135,
                        "2025-11-05": 0.23857660446336254,
                        "2025-11-06": 0.22999428597963406
                    }
                },
                "window_start": {
                    "2025-10-06": "2025-09-08",
                    "2025-10-07": "2025-09-09",
                    "2025-10-08": "2025-09-10",
                    "2025-10-09": "2025-09-11",
                    "2025-10-10": "2025-09-12",
                    "2025-10-13": "2025-09-15",
                    "2025-10-14": "2025-09-16",
                    "2025-10-15": "2025-09-17",
                    "2025-10-16": "2025-09-18",
                    "2025-10-17": "2025-09-19",
                    "2025-10-20": "2025-09-22",
                    "2025-10-21": "2025-09-23",
                    "2025-10-22": "2025-09-24",
                    "2025-10-23": "2025-09-25",
                    "2025-10-24": "2025-09-26",
                    "2025-10-27": "2025-09-29",
                    "2025-10-28": "2025-09-30",
                    "2025-10-29": "2025-10-01",
                    "2025-10-30": "2025-10-02",
                    "2025-10-31": "2025-10-03",
                    "2025-11-03": "2025-10-06",
                    "2025-11-04": "2025-10-07",
                    "2025-11-05": "2025-10-08",
                    "2025-11-06": "2025-10-09"
                },
                "params": {
                    "annualized": "true"
                }
            }
        }
    }
}

## Fundamental Data
We offer the following set of fundamental data APIs in various temporal dimensions covering key financial metrics, income statements, balance sheets, cash flow, and other fundamental data points.


Company Overview Trending
This API returns the company information, financial ratios, and other key metrics for the equity specified. Data is generally refreshed on the same day a company reports its latest earnings and financials.


API Parameters
❚ Required: function

The function of your choice. In this case, function=OVERVIEW

❚ Required: symbol

The symbol of the ticker of your choice. For example: symbol=IBM.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=OVERVIEW&symbol=IBM&apikey=demo


Ex:
{
    "Symbol": "IBM",
    "AssetType": "Common Stock",
    "Name": "International Business Machines",
    "Description": "International Business Machines Corporation (IBM) is a prominent American multinational technology company headquartered in Armonk, New York, with operations spanning over 170 countries. Established in 1911, IBM has established itself as a leader in innovation through its diverse offerings in hardware, software, and consulting services, with an increasing emphasis on artificial intelligence, quantum computing, and cloud solutions. The company is recognized for its strong research capabilities, having achieved the distinction of securing the most annual U.S. patents for 28 consecutive years, reflecting its dedication to pioneering technology. With a legacy that includes groundbreaking inventions like the ATM and relational database, IBM continues to evolve and play a critical role in advancing technological solutions across various sectors, adapting to the ever-changing digital landscape.",
    "CIK": "51143",
    "Exchange": "NYSE",
    "Currency": "USD",
    "Country": "USA",
    "Sector": "TECHNOLOGY",
    "Industry": "INFORMATION TECHNOLOGY SERVICES",
    "Address": "ONE NEW ORCHARD ROAD, ARMONK, NY, UNITED STATES, 10504",
    "OfficialSite": "https://www.ibm.com",
    "FiscalYearEnd": "December",
    "LatestQuarter": "2025-09-30",
    "MarketCapitalization": "286748705000",
    "EBITDA": "17767000000",
    "PERatio": "36.56",
    "PEGRatio": "1.735",
    "BookValue": "29.85",
    "DividendPerShare": "6.7",
    "DividendYield": "0.0223",
    "EPS": "8.39",
    "RevenuePerShareTTM": "70.35",
    "ProfitMargin": "0.121",
    "OperatingMarginTTM": "0.172",
    "ReturnOnAssetsTTM": "0.0635",
    "ReturnOnEquityTTM": "0.302",
    "RevenueTTM": "65401999000",
    "GrossProfitTTM": "37808001000",
    "DilutedEPSTTM": "8.39",
    "QuarterlyEarningsGrowthYOY": "0.177",
    "QuarterlyRevenueGrowthYOY": "0.091",
    "AnalystTargetPrice": "287.09",
    "AnalystRatingStrongBuy": "1",
    "AnalystRatingBuy": "7",
    "AnalystRatingHold": "8",
    "AnalystRatingSell": "2",
    "AnalystRatingStrongSell": "2",
    "TrailingPE": "36.56",
    "ForwardPE": "23.92",
    "PriceToSalesRatioTTM": "4.384",
    "PriceToBookRatio": "9.71",
    "EVToRevenue": "4.987",
    "EVToEBITDA": "24.76",
    "Beta": "0.688",
    "52WeekHigh": "319.35",
    "52WeekLow": "200.03",
    "50DayMovingAverage": "275.56",
    "200DayMovingAverage": "261.31",
    "SharesOutstanding": "934735000",
    "SharesFloat": "932604000",
    "PercentInsiders": "0.119",
    "PercentInstitutions": "64.448",
    "DividendDate": "2025-12-10",
    "ExDividendDate": "2025-11-10"
}

## ETF Profile & Holdings
This API returns key ETF metrics (e.g., net assets, expense ratio, and turnover), along with the corresponding ETF holdings / constituents with allocation by asset types and sectors.


API Parameters
❚ Required: function

The function of your choice. In this case, function=ETF_PROFILE

❚ Required: symbol

The symbol of the ticker of your choice. For example: symbol=QQQ.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=ETF_PROFILE&symbol=QQQ&apikey=demo

Ex:
{
    "net_assets": "385800000000",
    "net_expense_ratio": "0.002",
    "portfolio_turnover": "0.08",
    "dividend_yield": "0.0046",
    "inception_date": "1999-03-10",
    "leveraged": "NO",
    "sectors": [
        {
            "sector": "INFORMATION TECHNOLOGY",
            "weight": "0.533"
        },
        {
            "sector": "COMMUNICATION SERVICES",
            "weight": "0.158"
        },
        {
            "sector": "CONSUMER DISCRETIONARY",
            "weight": "0.118"
        },
        {
            "sector": "CONSUMER STAPLES",
            "weight": "0.044"
        },
        {
            "sector": "HEALTHCARE",
            "weight": "0.041"
        },
        {
            "sector": "INDUSTRIALS",
            "weight": "0.037"
        },
        {
            "sector": "UTILITIES",
            "weight": "0.015"
        },
        {
            "sector": "MATERIALS",
            "weight": "0.011"
        },
        {
            "sector": "ENERGY",
            "weight": "0.005"
        },
        {
            "sector": "FINANCIALS",
            "weight": "0.004"
        }
    ],
    "holdings": [
        {
            "symbol": "NVDA",
            "description": "NVIDIA CORP",
            "weight": "0.0948"
        },
        {
            "symbol": "AAPL",
            "description": "APPLE INC",
            "weight": "0.0831"
        },
        {
            "symbol": "MSFT",
            "description": "MICROSOFT CORP",
            "weight": "0.0821"
        },
        {
            "symbol": "AVGO",
            "description": "BROADCOM INC",
            "weight": "0.058"
        },
        {
            "symbol": "AMZN",
            "description": "AMAZON.COM INC",
            "weight": "0.0493"
        },
        {
            "symbol": "TSLA",
            "description": "TESLA INC",
            "weight": "0.0348"
        },
        {
            "symbol": "META",
            "description": "META PLATFORMS INC CLASS A",
            "weight": "0.0339"
        },
        {
            "symbol": "GOOGL",
            "description": "ALPHABET INC CLASS A",
            "weight": "0.0319"
        },
        {
            "symbol": "GOOG",
            "description": "ALPHABET INC CLASS C",
            "weight": "0.0298"
        },
        {
            "symbol": "NFLX",
            "description": "NETFLIX INC",
            "weight": "0.0277"
        },
        {
            "symbol": "COST",
            "description": "COSTCO WHOLESALE CORP",
            "weight": "0.0218"
        },
        {
            "symbol": "PLTR",
            "description": "n/a",
            "weight": "0.0217"
        },
        {
            "symbol": "AMD",
            "description": "ADVANCED MICRO DEVICES INC",
            "weight": "0.0205"
        },
        {
            "symbol": "CSCO",
            "description": "CISCO SYSTEMS INC",
            "weight": "0.0147"
        },
        {
            "symbol": "TMUS",
            "description": "T-MOBILE US INC",
            "weight": "0.0136"
        },
        {
            "symbol": "MU",
            "description": "MICRON TECHNOLOGY INC",
            "weight": "0.0122"
        },
        {
            "symbol": "LIN",
            "description": "LINDE PLC",
            "weight": "0.0111"
        },
        {
            "symbol": "PEP",
            "description": "PEPSICO INC",
            "weight": "0.0111"
        },
        {
            "symbol": "SHOP",
            "description": "n/a",
            "weight": "0.0106"
        },
        {
            "symbol": "INTU",
            "description": "INTUIT INC",
            "weight": "0.0097"
        },
        {
            "symbol": "AMAT",
            "description": "APPLIED MATERIALS INC",
            "weight": "0.0096"
        },
        {
            "symbol": "LRCX",
            "description": "LAM RESEARCH CORP",
            "weight": "0.0096"
        },
        {
            "symbol": "QCOM",
            "description": "QUALCOMM INC",
            "weight": "0.0095"
        },
        {
            "symbol": "APP",
            "description": "APPLOVIN CORP ORDINARY SHARES CLASS A",
            "weight": "0.0091"
        },
        {
            "symbol": "BKNG",
            "description": "BOOKING HOLDINGS INC",
            "weight": "0.0088"
        },
        {
            "symbol": "INTC",
            "description": "INTEL CORP",
            "weight": "0.0088"
        },
        {
            "symbol": "ISRG",
            "description": "INTUITIVE SURGICAL INC",
            "weight": "0.0086"
        },
        {
            "symbol": "AMGN",
            "description": "AMGEN INC",
            "weight": "0.0086"
        },
        {
            "symbol": "TXN",
            "description": "TEXAS INSTRUMENTS INC",
            "weight": "0.0086"
        },
        {
            "symbol": "KLAC",
            "description": "KLA CORP",
            "weight": "0.008"
        },
        {
            "symbol": "GILD",
            "description": "GILEAD SCIENCES INC",
            "weight": "0.008"
        },
        {
            "symbol": "ADBE",
            "description": "ADOBE INC",
            "weight": "0.0077"
        },
        {
            "symbol": "PANW",
            "description": "PALO ALTO NETWORKS INC",
            "weight": "0.0074"
        },
        {
            "symbol": "HON",
            "description": "HONEYWELL INTERNATIONAL INC",
            "weight": "0.0069"
        },
        {
            "symbol": "CRWD",
            "description": "CROWDSTRIKE HOLDINGS INC CLASS A",
            "weight": "0.0066"
        },
        {
            "symbol": "ADI",
            "description": "ANALOG DEVICES INC",
            "weight": "0.0064"
        },
        {
            "symbol": "CEG",
            "description": "CONSTELLATION ENERGY CORP",
            "weight": "0.0061"
        },
        {
            "symbol": "ADP",
            "description": "AUTOMATIC DATA PROCESSING INC",
            "weight": "0.006"
        },
        {
            "symbol": "CMCSA",
            "description": "COMCAST CORP CLASS A",
            "weight": "0.0057"
        },
        {
            "symbol": "DASH",
            "description": "DOORDASH INC ORDINARY SHARES CLASS A",
            "weight": "0.0056"
        },
        {
            "symbol": "MELI",
            "description": "MERCADOLIBRE INC",
            "weight": "0.0056"
        },
        {
            "symbol": "VRTX",
            "description": "VERTEX PHARMACEUTICALS INC",
            "weight": "0.0056"
        },
        {
            "symbol": "SBUX",
            "description": "STARBUCKS CORP",
            "weight": "0.005"
        },
        {
            "symbol": "CDNS",
            "description": "CADENCE DESIGN SYSTEMS INC",
            "weight": "0.0047"
        },
        {
            "symbol": "ASML",
            "description": "ASML HOLDING NV ADR",
            "weight": "0.0046"
        },
        {
            "symbol": "PDD",
            "description": "PDD HOLDINGS INC ADR",
            "weight": "0.0046"
        },
        {
            "symbol": "ORLY",
            "description": "O'REILLY AUTOMOTIVE INC",
            "weight": "0.0045"
        },
        {
            "symbol": "SNPS",
            "description": "SYNOPSYS INC",
            "weight": "0.0044"
        },
        {
            "symbol": "MDLZ",
            "description": "MONDELEZ INTERNATIONAL INC CLASS A",
            "weight": "0.0043"
        },
        {
            "symbol": "CTAS",
            "description": "CINTAS CORP",
            "weight": "0.0041"
        },
        {
            "symbol": "MSTR",
            "description": "STRATEGY INC CLASS A",
            "weight": "0.0041"
        },
        {
            "symbol": "MRVL",
            "description": "MARVELL TECHNOLOGY INC",
            "weight": "0.0039"
        },
        {
            "symbol": "TRI",
            "description": "THOMSON REUTERS CORP",
            "weight": "0.0038"
        },
        {
            "symbol": "MAR",
            "description": "MARRIOTT INTERNATIONAL INC CLASS A",
            "weight": "0.0037"
        },
        {
            "symbol": "CSX",
            "description": "CSX CORP",
            "weight": "0.0036"
        },
        {
            "symbol": "MNST",
            "description": "MONSTER BEVERAGE CORP",
            "weight": "0.0036"
        },
        {
            "symbol": "PYPL",
            "description": "PAYPAL HOLDINGS INC",
            "weight": "0.0035"
        },
        {
            "symbol": "ADSK",
            "description": "AUTODESK INC",
            "weight": "0.0035"
        },
        {
            "symbol": "FTNT",
            "description": "FORTINET INC",
            "weight": "0.0034"
        },
        {
            "symbol": "AEP",
            "description": "AMERICAN ELECTRIC POWER CO INC",
            "weight": "0.0033"
        },
        {
            "symbol": "REGN",
            "description": "REGENERON PHARMACEUTICALS INC",
            "weight": "0.0032"
        },
        {
            "symbol": "NXPI",
            "description": "NXP SEMICONDUCTORS NV",
            "weight": "0.0029"
        },
        {
            "symbol": "ROP",
            "description": "ROPER TECHNOLOGIES INC",
            "weight": "0.0029"
        },
        {
            "symbol": "ABNB",
            "description": "AIRBNB INC ORDINARY SHARES CLASS A",
            "weight": "0.0029"
        },
        {
            "symbol": "AXON",
            "description": "AXON ENTERPRISE INC",
            "weight": "0.0028"
        },
        {
            "symbol": "WDAY",
            "description": "WORKDAY INC CLASS A",
            "weight": "0.0028"
        },
        {
            "symbol": "PCAR",
            "description": "PACCAR INC",
            "weight": "0.0027"
        },
        {
            "symbol": "ROST",
            "description": "ROSS STORES INC",
            "weight": "0.0027"
        },
        {
            "symbol": "IDXX",
            "description": "IDEXX LABORATORIES INC",
            "weight": "0.0027"
        },
        {
            "symbol": "DDOG",
            "description": "DATADOG INC CLASS A",
            "weight": "0.0027"
        },
        {
            "symbol": "FAST",
            "description": "FASTENAL CO",
            "weight": "0.0026"
        },
        {
            "symbol": "EA",
            "description": "ELECTRONIC ARTS INC",
            "weight": "0.0026"
        },
        {
            "symbol": "EXC",
            "description": "EXELON CORP",
            "weight": "0.0026"
        },
        {
            "symbol": "AZN",
            "description": "ASTRAZENECA PLC ADR",
            "weight": "0.0026"
        },
        {
            "symbol": "XEL",
            "description": "XCEL ENERGY INC",
            "weight": "0.0025"
        },
        {
            "symbol": "TTWO",
            "description": "TAKE-TWO INTERACTIVE SOFTWARE INC",
            "weight": "0.0025"
        },
        {
            "symbol": "ZS",
            "description": "ZSCALER INC",
            "weight": "0.0025"
        },
        {
            "symbol": "PAYX",
            "description": "PAYCHEX INC",
            "weight": "0.0024"
        },
        {
            "symbol": "BKR",
            "description": "BAKER HUGHES CO CLASS A",
            "weight": "0.0024"
        },
        {
            "symbol": "WBD",
            "description": "WARNER BROS. DISCOVERY INC ORDINARY SHARES CLASS A",
            "weight": "0.0024"
        },
        {
            "symbol": "CPRT",
            "description": "COPART INC",
            "weight": "0.0023"
        },
        {
            "symbol": "CCEP",
            "description": "COCA-COLA EUROPACIFIC PARTNERS PLC",
            "weight": "0.0022"
        },
        {
            "symbol": "FANG",
            "description": "DIAMONDBACK ENERGY INC",
            "weight": "0.0021"
        },
        {
            "symbol": "KDP",
            "description": "KEURIG DR PEPPER INC",
            "weight": "0.002"
        },
        {
            "symbol": "MCHP",
            "description": "MICROCHIP TECHNOLOGY INC",
            "weight": "0.0019"
        },
        {
            "symbol": "CHTR",
            "description": "CHARTER COMMUNICATIONS INC CLASS A",
            "weight": "0.0018"
        },
        {
            "symbol": "n/a",
            "description": "CASH",
            "weight": "0.0018"
        },
        {
            "symbol": "GEHC",
            "description": "GE HEALTHCARE TECHNOLOGIES INC COMMON STOCK",
            "weight": "0.0018"
        },
        {
            "symbol": "VRSK",
            "description": "VERISK ANALYTICS INC",
            "weight": "0.0017"
        },
        {
            "symbol": "CSGP",
            "description": "COSTAR GROUP INC",
            "weight": "0.0017"
        },
        {
            "symbol": "CTSH",
            "description": "COGNIZANT TECHNOLOGY SOLUTIONS CORP CLASS A",
            "weight": "0.0017"
        },
        {
            "symbol": "KHC",
            "description": "THE KRAFT HEINZ CO",
            "weight": "0.0016"
        },
        {
            "symbol": "ODFL",
            "description": "OLD DOMINION FREIGHT LINE INC ORDINARY SHARES",
            "weight": "0.0016"
        },
        {
            "symbol": "TEAM",
            "description": "ATLASSIAN CORP CLASS A",
            "weight": "0.0014"
        },
        {
            "symbol": "DXCM",
            "description": "DEXCOM INC",
            "weight": "0.0014"
        },
        {
            "symbol": "ON",
            "description": "ON SEMICONDUCTOR CORP",
            "weight": "0.0012"
        },
        {
            "symbol": "ARM",
            "description": "ARM HOLDINGS PLC ADR",
            "weight": "0.0012"
        },
        {
            "symbol": "TTD",
            "description": "THE TRADE DESK INC CLASS A",
            "weight": "0.0012"
        },
        {
            "symbol": "CDW",
            "description": "CDW CORP",
            "weight": "0.0011"
        },
        {
            "symbol": "BIIB",
            "description": "BIOGEN INC",
            "weight": "0.0011"
        },
        {
            "symbol": "LULU",
            "description": "LULULEMON ATHLETICA INC",
            "weight": "0.001"
        },
        {
            "symbol": "GFS",
            "description": "GLOBALFOUNDRIES INC",
            "weight": "0.001"
        }
    ]
}

## Corporate Action - Dividends
This API returns historical and future (declared) dividend distributions.


API Parameters
❚ Required: function

The function of your choice. In this case, function=DIVIDENDS

❚ Required: symbol

The symbol of the ticker of your choice. For example: symbol=IBM.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the options data in JSON format; csv returns the data as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=DIVIDENDS&symbol=IBM&apikey=demo

Ex:
{
    "symbol": "IBM",
    "data": [
        {
            "ex_dividend_date": "2025-11-10",
            "declaration_date": "2025-10-22",
            "record_date": "2025-11-10",
            "payment_date": "2025-12-10",
            "amount": "1.68"
        },
        {
            "ex_dividend_date": "2025-08-08",
            "declaration_date": "2025-07-23",
            "record_date": "2025-08-08",
            "payment_date": "2025-09-10",
            "amount": "1.68"
        },
        {
            "ex_dividend_date": "2025-05-09",
            "declaration_date": "2025-04-29",
            "record_date": "2025-05-09",
            "payment_date": "2025-06-10",
            "amount": "1.68"
        },
        {
            "ex_dividend_date": "2025-02-10",
            "declaration_date": "2025-01-28",
            "record_date": "2025-02-10",
            "payment_date": "2025-03-10",
            "amount": "1.67"
        },
        {
            "ex_dividend_date": "2024-11-12",
            "declaration_date": "2024-10-30",
            "record_date": "2024-11-12",
            "payment_date": "2024-12-10",
            "amount": "1.67"
        },
        {
            "ex_dividend_date": "2024-08-09",
            "declaration_date": "2024-07-29",
            "record_date": "2024-08-09",
            "payment_date": "2024-09-10",
            "amount": "1.67"
        },
        ...
    ]
}   

## Corporate Action - Splits
This API returns historical split events.


API Parameters
❚ Required: function

The function of your choice. In this case, function=SPLITS

❚ Required: symbol

The symbol of the ticker of your choice. For example: symbol=IBM.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the options data in JSON format; csv returns the data as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=SPLITS&symbol=IBM&apikey=demo

Ex:
{
    "symbol": "IBM",
    "data": [
        {
            "effective_date": "2021-11-04",
            "split_factor": "1.0460"
        },
        {
            "effective_date": "1999-05-27",
            "split_factor": "2.0000"
        }
    ]
}

## INCOME_STATEMENT
This API returns the annual and quarterly income statements for the company of interest, with normalized fields mapped to GAAP and IFRS taxonomies of the SEC. Data is generally refreshed on the same day a company reports its latest earnings and financials.


API Parameters
❚ Required: function

The function of your choice. In this case, function=INCOME_STATEMENT

❚ Required: symbol

The symbol of the ticker of your choice. For example: symbol=IBM.

❚ Required: apikey

Your API key. Claim your free API key here.


Example - annual & quarterly income statements for IBM (click for JSON output)
https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol=IBM&apikey=demo

Ex:
{
    "symbol": "IBM",
    "annualReports": [
        {
            "fiscalDateEnding": "2024-12-31",
            "reportedCurrency": "USD",
            "grossProfit": "35551000000",
            "totalRevenue": "62753000000",
            "costOfRevenue": "27201000000",
            "costofGoodsAndServicesSold": "27201000000",
            "operatingIncome": "10074000000",
            "sellingGeneralAndAdministrative": "16737000000",
            "researchAndDevelopment": "7479000000",
            "operatingExpenses": "25478000000",
            "investmentIncomeNet": "None",
            "netInterestIncome": "-965000000",
            "interestIncome": "747000000",
            "interestExpense": "1712000000",
            "nonInterestIncome": "None",
            "otherNonOperatingIncome": "None",
            "depreciation": "None",
            "depreciationAndAmortization": "4667000000",
            "incomeBeforeTax": "5797000000",
            "incomeTaxExpense": "-218000000",
            "interestAndDebtExpense": "None",
            "netIncomeFromContinuingOperations": "6015000000",
            "comprehensiveIncomeNetOfTax": "None",
            "ebit": "7509000000",
            "ebitda": "12176000000",
            "netIncome": "6023000000"
        },
        {
            "fiscalDateEnding": "2023-12-31",
            "reportedCurrency": "USD",
            "grossProfit": "34300000000",
            "totalRevenue": "61860000000",
            "costOfRevenue": "27560000000",
            "costofGoodsAndServicesSold": "27560000000",
            "operatingIncome": "7514000000",
            "sellingGeneralAndAdministrative": "17952000000",
            "researchAndDevelopment": "6631000000",
            "operatingExpenses": "26786000000",
            "investmentIncomeNet": "None",
            "netInterestIncome": "-924000000",
            "interestIncome": "591000000",
            "interestExpense": "1607000000",
            "nonInterestIncome": "None",
            "otherNonOperatingIncome": "None",
            "depreciation": "None",
            "depreciationAndAmortization": "4395000000",
            "incomeBeforeTax": "8690000000",
            "incomeTaxExpense": "1176000000",
            "interestAndDebtExpense": "None",
            "netIncomeFromContinuingOperations": "7099000000",
            "comprehensiveIncomeNetOfTax": "None",
            "ebit": "7514000000",
            "ebitda": "7514000000",
            "netIncome": "7502000000"
        },
        {
            "fiscalDateEnding": "2022-12-31",
            "reportedCurrency": "USD",
            "grossProfit": "32687000000",
            "totalRevenue": "60530000000",
            "costOfRevenue": "27842000000",
            "costofGoodsAndServicesSold": "27842000000",
            "operatingIncome": "8174000000",
            "sellingGeneralAndAdministrative": "16103000000",
            "researchAndDevelopment": "6567000000",
            "operatingExpenses": "24514000000",
            "investmentIncomeNet": "None",
            "netInterestIncome": "-1216000000",
            "interestIncome": "162000000",
            "interestExpense": "1216000000",
            "nonInterestIncome": "None",
            "otherNonOperatingIncome": "None",
            "depreciation": "None",
            "depreciationAndAmortization": "4802000000",
            "incomeBeforeTax": "1156000000",
            "incomeTaxExpense": "-626000000",
            "interestAndDebtExpense": "None",
            "netIncomeFromContinuingOperations": "1782000000",
            "comprehensiveIncomeNetOfTax": "None",
            "ebit": "2372000000",
            "ebitda": "7174000000",
            "netIncome": "1640000000"
        }
    ], ...
}


##  BALANCE_SHEET
This API returns the annual and quarterly balance sheets for the company of interest, with normalized fields mapped to GAAP and IFRS taxonomies of the SEC. Data is generally refreshed on the same day a company reports its latest earnings and financials.


API Parameters
❚ Required: function

The function of your choice. In this case, function=BALANCE_SHEET

❚ Required: symbol

The symbol of the ticker of your choice. For example: symbol=IBM.

❚ Required: apikey

Your API key. Claim your free API key here.


Example - annual & quarterly balance sheets for IBM (click for JSON output)
https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol=IBM&apikey=demo

Ex:
{
    "symbol": "IBM",
    "annualReports": [
        {
            "fiscalDateEnding": "2024-12-31",
            "reportedCurrency": "USD",
            "totalAssets": "137175000000",
            "totalCurrentAssets": "34482000000",
            "cashAndCashEquivalentsAtCarryingValue": "13947000000",
            "cashAndShortTermInvestments": "13947000000",
            "inventory": "1289000000",
            "currentNetReceivables": "14010000000",
            "totalNonCurrentAssets": "102694000000",
            "propertyPlantEquipment": "8928000000",
            "accumulatedDepreciationAmortizationPPE": "None",
            "intangibleAssets": "10661000000",
            "intangibleAssetsExcludingGoodwill": "10661000000",
            "goodwill": "60706000000",
            "investments": "None",
            "longTermInvestments": "None",
            "shortTermInvestments": "644000000",
            "otherCurrentAssets": "4592000000",
            "otherNonCurrentAssets": "None",
            "totalLiabilities": "109782000000",
            "totalCurrentLiabilities": "33142000000",
            "currentAccountsPayable": "4032000000",
            "deferredRevenue": "None",
            "currentDebt": "None",
            "shortTermDebt": "5857000000",
            "totalNonCurrentLiabilities": "76640000000",
            "capitalLeaseObligations": "3423000000",
            "longTermDebt": "49884000000",
            "currentLongTermDebt": "5089000000",
            "longTermDebtNoncurrent": "None",
            "shortLongTermDebtTotal": "58396000000",
            "otherCurrentLiabilities": "7313000000",
            "otherNonCurrentLiabilities": "981000000",
            "totalShareholderEquity": "27307000000",
            "treasuryStock": "None",
            "retainedEarnings": "151163000000",
            "commonStock": "61380000000",
            "commonStockSharesOutstanding": "937200000"
        },
        {
            "fiscalDateEnding": "2023-12-31",
            "reportedCurrency": "USD",
            "totalAssets": "135241000000",
            "totalCurrentAssets": "32908000000",
            "cashAndCashEquivalentsAtCarryingValue": "13068000000",
            "cashAndShortTermInvestments": "13068000000",
            "inventory": "1161000000",
            "currentNetReceivables": "13956000000",
            "totalNonCurrentAssets": "102333000000",
            "propertyPlantEquipment": "8721000000",
            "accumulatedDepreciationAmortizationPPE": "None",
            "intangibleAssets": "11036000000",
            "intangibleAssetsExcludingGoodwill": "11036000000",
            "goodwill": "60178000000",
            "investments": "None",
            "longTermInvestments": "None",
            "shortTermInvestments": "373000000",
            "otherCurrentAssets": "4350000000",
            "otherNonCurrentAssets": "None",
            "totalLiabilities": "112628000000",
            "totalCurrentLiabilities": "34122000000",
            "currentAccountsPayable": "4132000000",
            "deferredRevenue": "None",
            "currentDebt": "None",
            "shortTermDebt": "7246000000",
            "totalNonCurrentLiabilities": "78506000000",
            "capitalLeaseObligations": "3388000000",
            "longTermDebt": "50121000000",
            "currentLongTermDebt": "6426000000",
            "longTermDebtNoncurrent": "None",
            "shortLongTermDebtTotal": "59935000000",
            "otherCurrentLiabilities": "7023000000",
            "otherNonCurrentLiabilities": "1164000000",
            "totalShareholderEquity": "22533000000",
            "treasuryStock": "None",
            "retainedEarnings": "151276000000",
            "commonStock": "59643000000",
            "commonStockSharesOutstanding": "922073828"
        },
        {
            "fiscalDateEnding": "2022-12-31",
            "reportedCurrency": "USD",
            "totalAssets": "127243000000",
            "totalCurrentAssets": "29118000000",
            "cashAndCashEquivalentsAtCarryingValue": "7886000000",
            "cashAndShortTermInvestments": "7886000000",
            "inventory": "1552000000",
            "currentNetReceivables": "7005000000",
            "totalNonCurrentAssets": "98126000000",
            "propertyPlantEquipment": "8212000000",
            "accumulatedDepreciationAmortizationPPE": "None",
            "intangibleAssets": "11184000000",
            "intangibleAssetsExcludingGoodwill": "11184000000",
            "goodwill": "55949000000",
            "investments": "None",
            "longTermInvestments": "1617000000",
            "shortTermInvestments": "852000000",
            "otherCurrentAssets": "11823000000",
            "otherNonCurrentAssets": "None",
            "totalLiabilities": "105222000000",
            "totalCurrentLiabilities": "31505000000",
            "currentAccountsPayable": "4051000000",
            "deferredRevenue": "None",
            "currentDebt": "None",
            "shortTermDebt": "5634000000",
            "totalNonCurrentLiabilities": "73717000000",
            "capitalLeaseObligations": "3064000000",
            "longTermDebt": "46189000000",
            "currentLongTermDebt": "4760000000",
            "longTermDebtNoncurrent": "None",
            "shortLongTermDebtTotal": "54013000000",
            "otherCurrentLiabilities": "7592000000",
            "otherNonCurrentLiabilities": "12243000000",
            "totalShareholderEquity": "21944000000",
            "treasuryStock": "None",
            "retainedEarnings": "149825000000",
            "commonStock": "58343000000",
            "commonStockSharesOutstanding": "912269062"
        }
    ], ...
}   

## CASH_FLOW
This API returns the annual and quarterly cash flow for the company of interest, with normalized fields mapped to GAAP and IFRS taxonomies of the SEC. Data is generally refreshed on the same day a company reports its latest earnings and financials.


API Parameters
❚ Required: function

The function of your choice. In this case, function=CASH_FLOW

❚ Required: symbol

The symbol of the ticker of your choice. For example: symbol=IBM.

❚ Required: apikey

Your API key. Claim your free API key here.


Example - annual & quarterly cash flows for IBM (click for JSON output)
https://www.alphavantage.co/query?function=CASH_FLOW&symbol=IBM&apikey=demo

Ex:
{
    "symbol": "IBM",
    "annualReports": [
        {
            "fiscalDateEnding": "2024-12-31",
            "reportedCurrency": "USD",
            "operatingCashflow": "13445000000",
            "paymentsForOperatingActivities": "None",
            "proceedsFromOperatingActivities": "None",
            "changeInOperatingLiabilities": "None",
            "changeInOperatingAssets": "None",
            "depreciationDepletionAndAmortization": "4667000000",
            "capitalExpenditures": "1685000000",
            "changeInReceivables": "None",
            "changeInInventory": "-166000000",
            "profitLoss": "None",
            "cashflowFromInvestment": "-4937000000",
            "cashflowFromFinancing": "-7079000000",
            "proceedsFromRepaymentsOfShortTermDebt": "None",
            "paymentsForRepurchaseOfCommonStock": "None",
            "paymentsForRepurchaseOfEquity": "None",
            "paymentsForRepurchaseOfPreferredStock": "None",
            "dividendPayout": "6147000000",
            "dividendPayoutCommonStock": "6147000000",
            "dividendPayoutPreferredStock": "None",
            "proceedsFromIssuanceOfCommonStock": "None",
            "proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet": "None",
            "proceedsFromIssuanceOfPreferredStock": "None",
            "proceedsFromRepurchaseOfEquity": "-651000000",
            "proceedsFromSaleOfTreasuryStock": "None",
            "changeInCashAndCashEquivalents": "None",
            "changeInExchangeRate": "None",
            "netIncome": "6023000000"
        },
        {
            "fiscalDateEnding": "2023-12-31",
            "reportedCurrency": "USD",
            "operatingCashflow": "13432000000",
            "paymentsForOperatingActivities": "None",
            "proceedsFromOperatingActivities": "None",
            "changeInOperatingLiabilities": "None",
            "changeInOperatingAssets": "None",
            "depreciationDepletionAndAmortization": "4381000000",
            "capitalExpenditures": "1918000000",
            "changeInReceivables": "None",
            "changeInInventory": "390000000",
            "profitLoss": "None",
            "cashflowFromInvestment": "-7070000000",
            "cashflowFromFinancing": "-6016000000",
            "proceedsFromRepaymentsOfShortTermDebt": "None",
            "paymentsForRepurchaseOfCommonStock": "None",
            "paymentsForRepurchaseOfEquity": "None",
            "paymentsForRepurchaseOfPreferredStock": "None",
            "dividendPayout": "6016000000",
            "dividendPayoutCommonStock": "6016000000",
            "dividendPayoutPreferredStock": "None",
            "proceedsFromIssuanceOfCommonStock": "None",
            "proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet": "None",
            "proceedsFromIssuanceOfPreferredStock": "None",
            "proceedsFromRepurchaseOfEquity": "-416000000",
            "proceedsFromSaleOfTreasuryStock": "None",
            "changeInCashAndCashEquivalents": "None",
            "changeInExchangeRate": "None",
            "netIncome": "6925000000"
        },
        {
            "fiscalDateEnding": "2022-12-31",
            "reportedCurrency": "USD",
            "operatingCashflow": "10435000000",
            "paymentsForOperatingActivities": "None",
            "proceedsFromOperatingActivities": "None",
            "changeInOperatingLiabilities": "None",
            "changeInOperatingAssets": "None",
            "depreciationDepletionAndAmortization": "4802000000",
            "capitalExpenditures": "1860000000",
            "changeInReceivables": "None",
            "changeInInventory": "71000000",
            "profitLoss": "None",
            "cashflowFromInvestment": "-4202000000",
            "cashflowFromFinancing": "-4958000000",
            "proceedsFromRepaymentsOfShortTermDebt": "None",
            "paymentsForRepurchaseOfCommonStock": "None",
            "paymentsForRepurchaseOfEquity": "None",
            "paymentsForRepurchaseOfPreferredStock": "None",
            "dividendPayout": "5948000000",
            "dividendPayoutCommonStock": "5948000000",
            "dividendPayoutPreferredStock": "None",
            "proceedsFromIssuanceOfCommonStock": "None",
            "proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet": "None",
            "proceedsFromIssuanceOfPreferredStock": "None",
            "proceedsFromRepurchaseOfEquity": "-407000000",
            "proceedsFromSaleOfTreasuryStock": "None",
            "changeInCashAndCashEquivalents": "None",
            "changeInExchangeRate": "None",
            "netIncome": "1639000000"
        },
        {
            "fiscalDateEnding": "2021-12-31",
            "reportedCurrency": "USD",
            "operatingCashflow": "12796000000",
            "paymentsForOperatingActivities": "None",
            "proceedsFromOperatingActivities": "None",
            "changeInOperatingLiabilities": "None",
            "changeInOperatingAssets": "None",
            "depreciationDepletionAndAmortization": "6416000000",
            "capitalExpenditures": "2381000000",
            "changeInReceivables": "1372000000",
            "changeInInventory": "138000000",
            "profitLoss": "None",
            "cashflowFromInvestment": "-5975000000",
            "cashflowFromFinancing": "-13354000000",
            "proceedsFromRepaymentsOfShortTermDebt": "None",
            "paymentsForRepurchaseOfCommonStock": "None",
            "paymentsForRepurchaseOfEquity": "None",
            "paymentsForRepurchaseOfPreferredStock": "None",
            "dividendPayout": "5869000000",
            "dividendPayoutCommonStock": "5869000000",
            "dividendPayoutPreferredStock": "None",
            "proceedsFromIssuanceOfCommonStock": "None",
            "proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet": "None",
            "proceedsFromIssuanceOfPreferredStock": "None",
            "proceedsFromRepurchaseOfEquity": "-319000000",
            "proceedsFromSaleOfTreasuryStock": "None",
            "changeInCashAndCashEquivalents": "-6533000000",
            "changeInExchangeRate": "None",
            "netIncome": "5743000000"
        }
    ], ...
}

## SHARES_OUTSTANDING
This API returns the quarterly numbers of shares outstanding for the company of interest, with both diluted and basic shares outstanding values returned. Data is generally refreshed on the same day a company reports its latest earnings and financials.


API Parameters
❚ Required: function

The function of your choice. In this case, function=SHARES_OUTSTANDING

❚ Required: symbol

The symbol of the ticker of your choice. For example: symbol=MSFT.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the options data in JSON format; csv returns the data as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=SHARES_OUTSTANDING&symbol=MSFT&apikey=demo

EX:
{
    "symbol": "MSFT",
    "status": "success",
    "data": [
        {
            "date": "2025-06-30",
            "shares_outstanding_diluted": "7462000000",
            "shares_outstanding_basic": "7430000000"
        },
        {
            "date": "2025-03-31",
            "shares_outstanding_diluted": "7461000000",
            "shares_outstanding_basic": "7434000000"
        },
        {
            "date": "2024-12-31",
            "shares_outstanding_diluted": "7468000000",
            "shares_outstanding_basic": "7435000000"
        },
        {
            "date": "2024-09-30",
            "shares_outstanding_diluted": "7470000000",
            "shares_outstanding_basic": "7433000000"
        },
        {
            "date": "2024-06-30",
            "shares_outstanding_diluted": "7475000000",
            "shares_outstanding_basic": "7431000000"
        },
        {
            "date": "2024-03-31",
            "shares_outstanding_diluted": "7472000000",
            "shares_outstanding_basic": "7431000000"
        },
        {
            "date": "2023-12-31",
            "shares_outstanding_diluted": "7468000000",
            "shares_outstanding_basic": "7432000000"
        },
        {
            "date": "2023-09-30",
            "shares_outstanding_diluted": "7462000000",
            "shares_outstanding_basic": "7429000000"
        },
        {
            "date": "2023-06-30",
            "shares_outstanding_diluted": "7466000000",
            "shares_outstanding_basic": "7434000000"
        },
        ...
    ]
}

## Earnings History
This API returns the annual and quarterly earnings (EPS) for the company of interest. Quarterly data also includes analyst estimates and surprise metrics.


API Parameters
❚ Required: function

The function of your choice. In this case, function=EARNINGS

❚ Required: symbol

The symbol of the ticker of your choice. For example: symbol=IBM.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=EARNINGS&symbol=IBM&apikey=demo

Ex:
{
    "symbol": "IBM",
    "annualEarnings": [
        {
            "fiscalDateEnding": "2025-09-30",
            "reportedEPS": "7.05"
        },
        {
            "fiscalDateEnding": "2024-12-31",
            "reportedEPS": "10.33"
        },
        {
            "fiscalDateEnding": "2023-12-31",
            "reportedEPS": "9.61"
        },
        {
            "fiscalDateEnding": "2022-12-31",
            "reportedEPS": "9.12"
        },
        {
            "fiscalDateEnding": "2021-12-31",
            "reportedEPS": "9.97"
        },
        {
            "fiscalDateEnding": "2020-12-31",
            "reportedEPS": "8.67"
        },
        {
            "fiscalDateEnding": "2019-12-31",
            "reportedEPS": "12.81"
        },
        {
            "fiscalDateEnding": "2018-12-31",
            "reportedEPS": "13.82"
        },
        {
            "fiscalDateEnding": "2017-12-31",
            "reportedEPS": "13.83"
        }
    ], ...
}


## Earnings Estimates Trending
This API returns the annual and quarterly EPS and revenue estimates for the company of interest, along with analyst count and revision history.


API Parameters
❚ Required: function

The function of your choice. In this case, function=EARNINGS_ESTIMATES

❚ Required: symbol

The symbol of the ticker of your choice. For example: symbol=IBM.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=EARNINGS_ESTIMATES&symbol=IBM&apikey=demo

Ex:
{
    "symbol": "IBM",
    "estimates": [
        {
            "date": "2026-12-31",
            "horizon": "next fiscal year",
            "eps_estimate_average": "12.1003",
            "eps_estimate_high": "12.5800",
            "eps_estimate_low": "11.2700",
            "eps_estimate_analyst_count": "20.0000",
            "eps_estimate_average_7_days_ago": "12.0768",
            "eps_estimate_average_30_days_ago": "11.9406",
            "eps_estimate_average_60_days_ago": "11.8656",
            "eps_estimate_average_90_days_ago": "11.8796",
            "eps_estimate_revision_up_trailing_7_days": "14.0000",
            "eps_estimate_revision_down_trailing_7_days": null,
            "eps_estimate_revision_up_trailing_30_days": "13.0000",
            "eps_estimate_revision_down_trailing_30_days": "4.0000",
            "revenue_estimate_average": "70054493620.00",
            "revenue_estimate_high": "71275226300.00",
            "revenue_estimate_low": "69183610000.00",
            "revenue_estimate_analyst_count": "20.00"
        },
        {
            "date": "2026-03-31",
            "horizon": "next fiscal quarter",
            "eps_estimate_average": "1.9339",
            "eps_estimate_high": "2.2800",
            "eps_estimate_low": "1.6700",
            "eps_estimate_analyst_count": "13.0000",
            "eps_estimate_average_7_days_ago": "1.9347",
            "eps_estimate_average_30_days_ago": "1.8555",
            "eps_estimate_average_60_days_ago": "1.8625",
            "eps_estimate_average_90_days_ago": "1.8625",
            "eps_estimate_revision_up_trailing_7_days": "0.0000",
            "eps_estimate_revision_down_trailing_7_days": null,
            "eps_estimate_revision_up_trailing_30_days": "5.0000",
            "eps_estimate_revision_down_trailing_30_days": "3.0000",
            "revenue_estimate_average": "15528858120.00",
            "revenue_estimate_high": "15954433000.00",
            "revenue_estimate_low": "15320908970.00",
            "revenue_estimate_analyst_count": "11.00"
        },
        {
            "date": "2025-12-31",
            "horizon": "historical fiscal year",
            "eps_estimate_average": "11.3553",
            "eps_estimate_high": "11.5000",
            "eps_estimate_low": "11.0900",
            "eps_estimate_analyst_count": "18.0000",
            "eps_estimate_average_7_days_ago": "11.3481",
            "eps_estimate_average_30_days_ago": "11.1516",
            "eps_estimate_average_60_days_ago": "11.0987",
            "eps_estimate_average_90_days_ago": "11.0997",
            "eps_estimate_revision_up_trailing_7_days": "16.0000",
            "eps_estimate_revision_down_trailing_7_days": null,
            "eps_estimate_revision_up_trailing_30_days": "15.0000",
            "eps_estimate_revision_down_trailing_30_days": "2.0000",
            "revenue_estimate_average": "67027266670.00",
            "revenue_estimate_high": "67531727000.00",
            "revenue_estimate_low": "66319358700.00",
            "revenue_estimate_analyst_count": "19.00"
        }
    ]
}

Listing & Delisting Status

This API returns a list of active or delisted US stocks and ETFs, either as of the latest trading day or at a specific time in history. The endpoint is positioned to facilitate equity research on asset lifecycle and survivorship.


API Parameters
❚ Required: function

The API function of your choice. In this case, function=LISTING_STATUS

❚ Optional: date

If no date is set, the API endpoint will return a list of active or delisted symbols as of the latest trading day. If a date is set, the API endpoint will "travel back" in time and return a list of active or delisted symbols on that particular date in history. Any YYYY-MM-DD date later than 2010-01-01 is supported. For example, date=2013-08-03

❚ Optional: state

By default, state=active and the API will return a list of actively traded stocks and ETFs. Set state=delisted to query a list of delisted assets.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples
To ensure optimal API response time, this endpoint uses the CSV format which is more memory-efficient than JSON.

Querying all active stocks and ETFs as of the latest trading day:
https://www.alphavantage.co/query?function=LISTING_STATUS&apikey=demo

Querying all delisted stocks and ETFs as of 2014-07-10:
https://www.alphavantage.co/query?function=LISTING_STATUS&date=2014-07-10&state=delisted&apikey=demo

Ex: .csv output
symbol	name	exchange	assetType	ipoDate	delistingDate	status
AACC	Asset Acceptance Capital Corp	NASDAQ	Stock	05/02/2004	17/10/2013	Delisted
AAI	AIRTRAN HOLDINGS INC	NYSE	Stock	17/09/2001	30/11/2011	Delisted
AAMRQ	Amr Corp	NYSE	Stock	02/01/2001	17/12/2013	Delisted
AATI	Advanced Analogic Technologies Incorp.	NASDAQ	Stock	04/08/2005	27/01/2012	Delisted
ABBC	ABINGTON BANCORP INC.PA	NASDAQ	Stock	17/12/2004	10/10/2011	Delisted
ABFS	Arkansas Best Corp	NASDAQ	Stock	13/05/1992	13/05/2014	Delisted
ABII	Abraxis BioScience Inc	NASDAQ	Stock	15/11/2007	25/10/2010	Delisted
ABVA	ALLIANCE BANKSHARES CORP	NASDAQ	Stock	05/12/2001	07/01/2013	Delisted
ABVT	ABOVENET INC	NYSE	Stock	02/12/2010	10/07/2013	Delisted

and 

symbol	name	exchange	assetType	ipoDate	delistingDate	status
#NAME?	Presurance Holdings Inc	NASDAQ	Stock	30/08/2023	null	Active
A	Agilent Technologies Inc	NYSE	Stock	18/11/1999	null	Active
AA	Alcoa Corp	NYSE	Stock	18/10/2016	null	Active
AAA	ALTERNATIVE ACCESS FIRST PRIORITY CLO BOND ETF 	NYSE ARCA	ETF	09/09/2020	null	Active
AAAU	Goldman Sachs Physical Gold ETF	BATS	ETF	15/08/2018	null	Active
AACBR	Artius II Acquisition Inc Rights	NASDAQ	Stock	07/04/2025	null	Active
AACBU	Artius II Acquisition Inc - Units (1 Ord Shs & 1 Rts)	NASDAQ	Stock	13/02/2025	null	Active
AACG	ATA Creativity Global	NASDAQ	Stock	29/01/2008	null	Active

## Earnings Calendar

This API returns a list of company earnings expected in the next 3, 6, or 12 months.


API Parameters
❚ Required: function

The API function of your choice. In this case, function=EARNINGS_CALENDAR

❚ Optional: symbol

By default, no symbol will be set for this API. When no symbol is set, the API endpoint will return the full list of company earnings scheduled. If a symbol is set, the API endpoint will return the expected earnings for that specific symbol. For example, symbol=IBM

❚ Optional: horizon

By default, horizon=3month and the API will return a list of expected company earnings in the next 3 months. You may set horizon=6month or horizon=12month to query the earnings scheduled for the next 6 months or 12 months, respectively.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples
To ensure optimal API response time, this endpoint uses the CSV format which is more memory-efficient than JSON.

Querying all the company earnings expected in the next 3 months:
https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&horizon=3month&apikey=demo

Querying all the earnings events for IBM in the next 12 months:
https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&symbol=IBM&horizon=12month&apikey=demo

Ex:
symbol	name	reportDate	fiscalDateEnding	estimate	currency
IBM	International Business Machines Corp	28/01/2026	31/12/2025	4.31	USD
IBM	International Business Machines Corp	21/04/2026	31/03/2026		USD

##  IPO Calendar

This API returns a list of IPOs expected in the next 3 months.


API Parameters
❚ Required: function

The API function of your choice. In this case, function=IPO_CALENDAR

❚ Required: apikey

Your API key. Claim your free API key here.


Examples
To ensure optimal API response time, this endpoint uses the CSV format which is more memory-efficient than JSON.

Querying all the IPOs expected in the next 3 months:
https://www.alphavantage.co/query?function=IPO_CALENDAR&apikey=demo

Ex: .csv output
symbol	name	ipoDate	priceRangeLow	priceRangeHigh	currency	exchange
AERO	Aerogrow International Inc	07/11/2025	18	20	USD	NYSE
TDWDU	Tailwind 2.0 Acquisition Corp. Unit	07/11/2025	0	0	USD	NASDAQ
CRACU	Crown Reserve Acquisition Corp. I Unit	07/11/2025	0	0	USD	NASDAQ
WSHP	Wasatch Pharmaceutical Inc	10/11/2025	0	0	USD	NASDAQ
DTDT	DT House Ltd	11/11/2025	4	5	USD	NASDAQ
CBC	Rbc Centura Banks Inc	20/11/2025	21	24	USD	NASDAQ


Foreign Exchange Rates (FX)
APIs under this section provide a wide range of data feed for realtime and historical forex (FX) rates.


CURRENCY_EXCHANGE_RATE Trending

This API returns the realtime exchange rate for a pair of cryptocurrency (e.g., Bitcoin) and physical currency (e.g., USD).


API Parameters
❚ Required: function

The function of your choice. In this case, function=CURRENCY_EXCHANGE_RATE

❚ Required: from_currency

The currency you would like to get the exchange rate for. It can either be a physical currency or cryptocurrency. For example: from_currency=USD or from_currency=BTC.

❚ Required: to_currency

The destination currency for the exchange rate. It can either be a physical currency or cryptocurrency. For example: to_currency=USD or to_currency=BTC.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
US Dollar to Japanese Yen:
https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=JPY&apikey=demo

Bitcoin to Euro:
https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=BTC&to_currency=EUR&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=JPY&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

FX_INTRADAY Premium Trending

This API returns intraday time series (timestamp, open, high, low, close) of the FX currency pair specified, updated realtime.


API Parameters
❚ Required: function

The time series of your choice. In this case, function=FX_INTRADAY

❚ Required: from_symbol

A three-letter symbol from the forex currency list. For example: from_symbol=EUR

❚ Required: to_symbol

A three-letter symbol from the forex currency list. For example: to_symbol=USD

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min

❚ Optional: outputsize

By default, outputsize=compact. Strings compact and full are accepted with the following specifications: compact returns only the latest 100 data points in the intraday time series; full returns the full-length intraday time series. The "compact" option is recommended if you would like to reduce the data size of each API call.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the intraday time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=EUR&to_symbol=USD&interval=5min&apikey=demo

https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=EUR&to_symbol=USD&interval=5min&outputsize=full&apikey=demo

Downloadable CSV file:
https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=EUR&to_symbol=USD&interval=5min&apikey=demo&datatype=csv


💡 Tip: this is a premium API function. Subscribe to a premium membership plan to instantly unlock all premium APIs.


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=EUR&to_symbol=USD&interval=5min&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

FX_DAILY

This API returns the daily time series (timestamp, open, high, low, close) of the FX currency pair specified, updated realtime.


API Parameters
❚ Required: function

The time series of your choice. In this case, function=FX_DAILY

❚ Required: from_symbol

A three-letter symbol from the forex currency list. For example: from_symbol=EUR

❚ Required: to_symbol

A three-letter symbol from the forex currency list. For example: to_symbol=USD

❚ Optional: outputsize

By default, outputsize=compact. Strings compact and full are accepted with the following specifications: compact returns only the latest 100 data points in the daily time series; full returns the full-length daily time series. The "compact" option is recommended if you would like to reduce the data size of each API call.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=EUR&to_symbol=USD&apikey=demo

https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=EUR&to_symbol=USD&outputsize=full&apikey=demo

Downloadable CSV file:
https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=EUR&to_symbol=USD&apikey=demo&datatype=csv


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=EUR&to_symbol=USD&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

FX_WEEKLY

This API returns the weekly time series (timestamp, open, high, low, close) of the FX currency pair specified, updated realtime.

The latest data point is the price information for the week (or partial week) containing the current trading day, updated realtime.


API Parameters
❚ Required: function

The time series of your choice. In this case, function=FX_WEEKLY

❚ Required: from_symbol

A three-letter symbol from the forex currency list. For example: from_symbol=EUR

❚ Required: to_symbol

A three-letter symbol from the forex currency list. For example: to_symbol=USD

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the weekly time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=FX_WEEKLY&from_symbol=EUR&to_symbol=USD&apikey=demo

Downloadable CSV file:
https://www.alphavantage.co/query?function=FX_WEEKLY&from_symbol=EUR&to_symbol=USD&apikey=demo&datatype=csv


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=FX_WEEKLY&from_symbol=EUR&to_symbol=USD&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

FX_MONTHLY

This API returns the monthly time series (timestamp, open, high, low, close) of the FX currency pair specified, updated realtime.

The latest data point is the prices information for the month (or partial month) containing the current trading day, updated realtime.


API Parameters
❚ Required: function

The time series of your choice. In this case, function=FX_MONTHLY

❚ Required: from_symbol

A three-letter symbol from the forex currency list. For example: from_symbol=EUR

❚ Required: to_symbol

A three-letter symbol from the forex currency list. For example: to_symbol=USD

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the monthly time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=FX_MONTHLY&from_symbol=EUR&to_symbol=USD&apikey=demo

Downloadable CSV file:
https://www.alphavantage.co/query?function=FX_MONTHLY&from_symbol=EUR&to_symbol=USD&apikey=demo&datatype=csv


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=FX_MONTHLY&from_symbol=EUR&to_symbol=USD&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

Digital & Crypto Currencies
APIs under this section provide a wide range of data feed for digital and crypto currencies such as Bitcoin.


CURRENCY_EXCHANGE_RATE Trending

This API returns the realtime exchange rate for any pair of cryptocurrency (e.g., Bitcoin) or physical currency (e.g., USD).


API Parameters
❚ Required: function

The function of your choice. In this case, function=CURRENCY_EXCHANGE_RATE

❚ Required: from_currency

The currency you would like to get the exchange rate for. It can either be a physical currency or cryptocurrency. For example: from_currency=USD or from_currency=BTC.

❚ Required: to_currency

The destination currency for the exchange rate. It can either be a physical currency or cryptocurrency. For example: to_currency=USD or to_currency=BTC.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
Bitcoin to Euro:
https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=BTC&to_currency=EUR&apikey=demo

US Dollar to Japanese Yen:
https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=JPY&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=BTC&to_currency=EUR&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

CRYPTO_INTRADAY Trending Premium

This API returns intraday time series (timestamp, open, high, low, close, volume) of the cryptocurrency specified, updated realtime.


API Parameters
❚ Required: function

The time series of your choice. In this case, function=CRYPTO_INTRADAY

❚ Required: symbol

The cryptocurrency of your choice. It can be any of the "from" currencies in the cryptocurrency list. For example: symbol=ETH.

❚ Required: market

The exchange market of your choice. It can be any of the "to" currencies in the cryptocurrency list. For example: market=USD.

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min

❚ Optional: outputsize

By default, outputsize=compact. Strings compact and full are accepted with the following specifications: compact returns only the latest 100 data points in the intraday time series; full returns the full-length intraday time series. The "compact" option is recommended if you would like to reduce the data size of each API call.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the intraday time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=CRYPTO_INTRADAY&symbol=ETH&market=USD&interval=5min&apikey=demo

https://www.alphavantage.co/query?function=CRYPTO_INTRADAY&symbol=ETH&market=USD&interval=5min&outputsize=full&apikey=demo

Downloadable CSV file:
https://www.alphavantage.co/query?function=CRYPTO_INTRADAY&symbol=ETH&market=USD&interval=5min&apikey=demo&datatype=csv


💡 Tip: this is a premium API function. Subscribe to a premium membership plan to instantly unlock all premium APIs.


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=CRYPTO_INTRADAY&symbol=ETH&market=USD&interval=5min&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

DIGITAL_CURRENCY_DAILY

This API returns the daily historical time series for a cryptocurrency (e.g., BTC) traded on a specific market (e.g., EUR/Euro), refreshed daily at midnight (UTC). Prices and volumes are quoted in both the market-specific currency and USD.


API Parameters
❚ Required: function

The time series of your choice. In this case, function=DIGITAL_CURRENCY_DAILY

❚ Required: symbol

The cryptocurrency of your choice. It can be any of the "from" currencies in the cryptocurrency list. For example: symbol=BTC.

❚ Required: market

The exchange market of your choice. It can be any of the "to" currencies in the cryptocurrency list. For example: market=EUR.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=BTC&market=EUR&apikey=demo

Downloadable CSV file:
https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=BTC&market=EUR&apikey=demo&datatype=csv


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=BTC&market=EUR&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

DIGITAL_CURRENCY_WEEKLY Trending

This API returns the weekly historical time series for a cryptocurrency (e.g., BTC) traded on a specific market (e.g., EUR/Euro), refreshed daily at midnight (UTC). Prices and volumes are quoted in both the market-specific currency and USD.


API Parameters
❚ Required: function

The time series of your choice. In this case, function=DIGITAL_CURRENCY_WEEKLY

❚ Required: symbol

The cryptocurrency of your choice. It can be any of the "from" currencies in the cryptocurrency list. For example: symbol=BTC.

❚ Required: market

The exchange market of your choice. It can be any of the "to" currencies in the cryptocurrency list. For example: market=EUR.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_WEEKLY&symbol=BTC&market=EUR&apikey=demo

Downloadable CSV file:
https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_WEEKLY&symbol=BTC&market=EUR&apikey=demo&datatype=csv


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_WEEKLY&symbol=BTC&market=EUR&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

DIGITAL_CURRENCY_MONTHLY Trending

This API returns the monthly historical time series for a cryptocurrency (e.g., BTC) traded on a specific market (e.g., EUR/Euro), refreshed daily at midnight (UTC). Prices and volumes are quoted in both the market-specific currency and USD.


API Parameters
❚ Required: function

The time series of your choice. In this case, function=DIGITAL_CURRENCY_MONTHLY

❚ Required: symbol

The cryptocurrency of your choice. It can be any of the "from" currencies in the cryptocurrency list. For example: symbol=BTC.

❚ Required: market

The exchange market of your choice. It can be any of the "to" currencies in the cryptocurrency list. For example: market=EUR.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_MONTHLY&symbol=BTC&market=EUR&apikey=demo

Downloadable CSV file:
https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_MONTHLY&symbol=BTC&market=EUR&apikey=demo&datatype=csv


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_MONTHLY&symbol=BTC&market=EUR&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

Commodities
APIs under this section provide historical data for major commodities such as crude oil, natural gas, copper, wheat, etc., spanning across various temporal horizons (daily, weekly, monthly, quarterly, etc.)


Crude Oil Prices: West Texas Intermediate (WTI) Trending

This API returns the West Texas Intermediate (WTI) crude oil prices in daily, weekly, and monthly horizons.

Source: U.S. Energy Information Administration, Crude Oil Prices: West Texas Intermediate (WTI) - Cushing, Oklahoma, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=WTI

❚ Optional: interval

By default, interval=monthly. Strings daily, weekly, and monthly are accepted.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=WTI&interval=monthly&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=WTI&interval=monthly&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)


Crude Oil Prices (Brent) Trending

This API returns the Brent (Europe) crude oil prices in daily, weekly, and monthly horizons.

Source: U.S. Energy Information Administration, Crude Oil Prices: Brent - Europe, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=BRENT

❚ Optional: interval

By default, interval=monthly. Strings daily, weekly, and monthly are accepted.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=BRENT&interval=monthly&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=BRENT&interval=monthly&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)


Natural Gas

This API returns the Henry Hub natural gas spot prices in daily, weekly, and monthly horizons.

Source: U.S. Energy Information Administration, Henry Hub Natural Gas Spot Price, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=NATURAL_GAS

❚ Optional: interval

By default, interval=monthly. Strings daily, weekly, and monthly are accepted.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=NATURAL_GAS&interval=monthly&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=NATURAL_GAS&interval=monthly&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)


Global Price of Copper Trending

This API returns the global price of copper in monthly, quarterly, and annual horizons.

Source: International Monetary Fund (IMF Terms of Use), Global price of Copper, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=COPPER

❚ Optional: interval

By default, interval=monthly. Strings monthly, quarterly, and annual are accepted.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=COPPER&interval=monthly&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=COPPER&interval=monthly&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)


Global Price of Aluminum

This API returns the global price of aluminum in monthly, quarterly, and annual horizons.

Source: International Monetary Fund (IMF Terms of Use), Global price of Aluminum, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=ALUMINUM

❚ Optional: interval

By default, interval=monthly. Strings monthly, quarterly, and annual are accepted.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=ALUMINUM&interval=monthly&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=ALUMINUM&interval=monthly&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)


Global Price of Wheat

This API returns the global price of wheat in monthly, quarterly, and annual horizons.

Source: International Monetary Fund (IMF Terms of Use), Global price of Wheat, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=WHEAT

❚ Optional: interval

By default, interval=monthly. Strings monthly, quarterly, and annual are accepted.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=WHEAT&interval=monthly&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=WHEAT&interval=monthly&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)


Global Price of Corn

This API returns the global price of corn in monthly, quarterly, and annual horizons.

Source: International Monetary Fund (IMF Terms of Use), Global price of Corn, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=CORN

❚ Optional: interval

By default, interval=monthly. Strings monthly, quarterly, and annual are accepted.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=CORN&interval=monthly&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=CORN&interval=monthly&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)


Global Price of Cotton

This API returns the global price of cotton in monthly, quarterly, and annual horizons.

Source: International Monetary Fund (IMF Terms of Use), Global price of Cotton, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=COTTON

❚ Optional: interval

By default, interval=monthly. Strings monthly, quarterly, and annual are accepted.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=COTTON&interval=monthly&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=COTTON&interval=monthly&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)


Global Price of Sugar

This API returns the global price of sugar in monthly, quarterly, and annual horizons.

Source: International Monetary Fund (IMF Terms of Use), Global price of Sugar, No. 11, World, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=SUGAR

❚ Optional: interval

By default, interval=monthly. Strings monthly, quarterly, and annual are accepted.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=SUGAR&interval=monthly&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=SUGAR&interval=monthly&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)


Global Price of Coffee

This API returns the global price of coffee in monthly, quarterly, and annual horizons.

Source: International Monetary Fund (IMF Terms of Use), Global price of Coffee, Other Mild Arabica, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=COFFEE

❚ Optional: interval

By default, interval=monthly. Strings monthly, quarterly, and annual are accepted.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=COFFEE&interval=monthly&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=COFFEE&interval=monthly&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)


Global Price Index of All Commodities

This API returns the global price index of all commodities in monthly, quarterly, and annual temporal dimensions.

Source: International Monetary Fund (IMF Terms of Use), Global Price Index of All Commodities, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=ALL_COMMODITIES

❚ Optional: interval

By default, interval=monthly. Strings monthly, quarterly, and annual are accepted.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=ALL_COMMODITIES&interval=monthly&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=ALL_COMMODITIES&interval=monthly&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

Economic Indicators
APIs under this section provide key US economic indicators frequently used for investment strategy formulation and application development.


REAL_GDP Trending

This API returns the annual and quarterly Real GDP of the United States.

Source: U.S. Bureau of Economic Analysis, Real Gross Domestic Product, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=REAL_GDP

❚ Optional: interval

By default, interval=annual. Strings quarterly and annual are accepted.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=REAL_GDP&interval=annual&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=REAL_GDP&interval=annual&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

REAL_GDP_PER_CAPITA
This API returns the quarterly Real GDP per Capita data of the United States.

Source: U.S. Bureau of Economic Analysis, Real gross domestic product per capita, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.



API Parameters
❚ Required: function

The function of your choice. In this case, function=REAL_GDP_PER_CAPITA

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=REAL_GDP_PER_CAPITA&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=REAL_GDP_PER_CAPITA&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

TREASURY_YIELD Trending

This API returns the daily, weekly, and monthly US treasury yield of a given maturity timeline (e.g., 5 year, 30 year, etc).

Source: Board of Governors of the Federal Reserve System (US), Market Yield on U.S. Treasury Securities at 3-month, 2-year, 5-year, 7-year, 10-year, and 30-year Constant Maturities, Quoted on an Investment Basis, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=TREASURY_YIELD

❚ Optional: interval

By default, interval=monthly. Strings daily, weekly, and monthly are accepted.

❚ Optional: maturity

By default, maturity=10year. Strings 3month, 2year, 5year, 7year, 10year, and 30year are accepted.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=TREASURY_YIELD&interval=monthly&maturity=10year&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=TREASURY_YIELD&interval=monthly&maturity=10year&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

FEDERAL_FUNDS_RATE

This API returns the daily, weekly, and monthly federal funds rate (interest rate) of the United States.

Source: Board of Governors of the Federal Reserve System (US), Federal Funds Effective Rate, retrieved from FRED, Federal Reserve Bank of St. Louis (https://fred.stlouisfed.org/series/FEDFUNDS). This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=FEDERAL_FUNDS_RATE

❚ Optional: interval

By default, interval=monthly. Strings daily, weekly, and monthly are accepted.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=FEDERAL_FUNDS_RATE&interval=monthly&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=FEDERAL_FUNDS_RATE&interval=monthly&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

CPI

This API returns the monthly and semiannual consumer price index (CPI) of the United States. CPI is widely regarded as the barometer of inflation levels in the broader economy.

Source: U.S. Bureau of Labor Statistics, Consumer Price Index for All Urban Consumers: All Items in U.S. City Average, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=CPI

❚ Optional: interval

By default, interval=monthly. Strings monthly and semiannual are accepted.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=CPI&interval=monthly&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=CPI&interval=monthly&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

INFLATION

This API returns the annual inflation rates (consumer prices) of the United States.

Source: World Bank, Inflation, consumer prices for the United States, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=INFLATION

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=INFLATION&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=INFLATION&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)


RETAIL_SALES

This API returns the monthly Advance Retail Sales: Retail Trade data of the United States.

Source: U.S. Census Bureau, Advance Retail Sales: Retail Trade, retrieved from FRED, Federal Reserve Bank of St. Louis (https://fred.stlouisfed.org/series/RSXFSN). This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=RETAIL_SALES

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=RETAIL_SALES&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=RETAIL_SALES&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

DURABLES

This API returns the monthly manufacturers' new orders of durable goods in the United States.

Source: U.S. Census Bureau, Manufacturers' New Orders: Durable Goods, retrieved from FRED, Federal Reserve Bank of St. Louis (https://fred.stlouisfed.org/series/UMDMNO). This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=DURABLES

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=DURABLES&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=DURABLES&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

UNEMPLOYMENT

This API returns the monthly unemployment data of the United States. The unemployment rate represents the number of unemployed as a percentage of the labor force. Labor force data are restricted to people 16 years of age and older, who currently reside in 1 of the 50 states or the District of Columbia, who do not reside in institutions (e.g., penal and mental facilities, homes for the aged), and who are not on active duty in the Armed Forces (source).

Source: U.S. Bureau of Labor Statistics, Unemployment Rate, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=UNEMPLOYMENT

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=UNEMPLOYMENT&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=UNEMPLOYMENT&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

NONFARM_PAYROLL

This API returns the monthly US All Employees: Total Nonfarm (commonly known as Total Nonfarm Payroll), a measure of the number of U.S. workers in the economy that excludes proprietors, private household employees, unpaid volunteers, farm employees, and the unincorporated self-employed.

Source: U.S. Bureau of Labor Statistics, All Employees, Total Nonfarm, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.


API Parameters
❚ Required: function

The function of your choice. In this case, function=NONFARM_PAYROLL

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=NONFARM_PAYROLL&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=NONFARM_PAYROLL&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

Technical Indicators
Technical indicator APIs for a given equity or currency exchange pair, derived from the underlying time series based stock API and forex data. All indicators are calculated from adjusted time series data to eliminate artificial price/volume perturbations from historical split and dividend events.


SMA Trending

This API returns the simple moving average (SMA) values. See also: SMA explainer and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=SMA

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each moving average value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
Equity:
https://www.alphavantage.co/query?function=SMA&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo

Forex (FX) or cryptocurrency pair:
https://www.alphavantage.co/query?function=SMA&symbol=USDEUR&interval=weekly&time_period=10&series_type=open&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=SMA&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

EMA Trending

This API returns the exponential moving average (EMA) values. See also: EMA explainer and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=EMA

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each moving average value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
Equity:
https://www.alphavantage.co/query?function=EMA&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo

Forex (FX) or cryptocurrency pair:
https://www.alphavantage.co/query?function=EMA&symbol=USDEUR&interval=weekly&time_period=10&series_type=open&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=EMA&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

WMA

This API returns the weighted moving average (WMA) values. See also: mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=WMA

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each moving average value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=WMA&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=WMA&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

DEMA

This API returns the double exponential moving average (DEMA) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=DEMA

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each moving average value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=DEMA&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=DEMA&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

TEMA

This API returns the triple exponential moving average (TEMA) values. See also: mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=TEMA

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each moving average value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=TEMA&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=TEMA&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

TRIMA

This API returns the triangular moving average (TRIMA) values. See also: mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=TRIMA

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each moving average value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=TRIMA&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=TRIMA&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

KAMA

This API returns the Kaufman adaptive moving average (KAMA) values.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=KAMA

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each moving average value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=KAMA&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=KAMA&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

MAMA

This API returns the MESA adaptive moving average (MAMA) values.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=MAMA

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: fastlimit

Positive floats are accepted. By default, fastlimit=0.01.

❚ Optional: slowlimit

Positive floats are accepted. By default, slowlimit=0.01.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=MAMA&symbol=IBM&interval=daily&series_type=close&fastlimit=0.02&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=MAMA&symbol=IBM&interval=daily&series_type=close&fastlimit=0.02&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

VWAP Trending Premium

This API returns the volume weighted average price (VWAP) for intraday time series. See also: Investopedia article.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=VWAP

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. In keeping with mainstream investment literatures on VWAP, the following intraday intervals are supported: 1min, 5min, 15min, 30min, 60min

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=VWAP&symbol=IBM&interval=15min&apikey=demo


💡 Tip: this is a premium API function. Subscribe to a premium membership plan to instantly unlock all premium APIs.


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=VWAP&symbol=IBM&interval=15min&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

T3

This API returns the Tilson moving average (T3) values. See also: mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=T3

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each moving average value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=T3&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=T3&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

MACD Trending Premium

This API returns the moving average convergence / divergence (MACD) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=MACD

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: fastperiod

Positive integers are accepted. By default, fastperiod=12.

❚ Optional: slowperiod

Positive integers are accepted. By default, slowperiod=26.

❚ Optional: signalperiod

Positive integers are accepted. By default, signalperiod=9.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
Equity:
https://www.alphavantage.co/query?function=MACD&symbol=IBM&interval=daily&series_type=open&apikey=demo

Forex (FX) or cryptocurrency pair:
https://www.alphavantage.co/query?function=MACD&symbol=USDEUR&interval=weekly&series_type=open&apikey=demo


💡 Tip: this is a premium API function. Subscribe to a premium membership plan to instantly unlock all premium APIs.


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=MACD&symbol=IBM&interval=daily&series_type=open&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

MACDEXT

This API returns the moving average convergence / divergence values with controllable moving average type. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=MACDEXT

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: fastperiod

Positive integers are accepted. By default, fastperiod=12.

❚ Optional: slowperiod

Positive integers are accepted. By default, slowperiod=26.

❚ Optional: signalperiod

Positive integers are accepted. By default, signalperiod=9.

❚ Optional: fastmatype

Moving average type for the faster moving average. By default, fastmatype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).

❚ Optional: slowmatype

Moving average type for the slower moving average. By default, slowmatype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).

❚ Optional: signalmatype

Moving average type for the signal moving average. By default, signalmatype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=MACDEXT&symbol=IBM&interval=daily&series_type=open&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=MACDEXT&symbol=IBM&interval=daily&series_type=open&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

STOCH Trending

This API returns the stochastic oscillator (STOCH) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=STOCH

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Optional: fastkperiod

The time period of the fastk moving average. Positive integers are accepted. By default, fastkperiod=5.

❚ Optional: slowkperiod

The time period of the slowk moving average. Positive integers are accepted. By default, slowkperiod=3.

❚ Optional: slowdperiod

The time period of the slowd moving average. Positive integers are accepted. By default, slowdperiod=3.

❚ Optional: slowkmatype

Moving average type for the slowk moving average. By default, slowkmatype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).

❚ Optional: slowdmatype

Moving average type for the slowd moving average. By default, slowdmatype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
Equity:
https://www.alphavantage.co/query?function=STOCH&symbol=IBM&interval=daily&apikey=demo

Forex (FX) or cryptocurrency pair:
https://www.alphavantage.co/query?function=STOCH&symbol=USDEUR&interval=weekly&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=STOCH&symbol=IBM&interval=daily&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

STOCHF

This API returns the stochastic fast (STOCHF) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=STOCHF

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Optional: fastkperiod

The time period of the fastk moving average. Positive integers are accepted. By default, fastkperiod=5.

❚ Optional: fastdperiod

The time period of the fastd moving average. Positive integers are accepted. By default, fastdperiod=3.

❚ Optional: fastdmatype

Moving average type for the fastd moving average. By default, fastdmatype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=STOCHF&symbol=IBM&interval=daily&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=STOCHF&symbol=IBM&interval=daily&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

RSI Trending

This API returns the relative strength index (RSI) values. See also: RSI explainer and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=RSI

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each RSI value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
Equity:
https://www.alphavantage.co/query?function=RSI&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo

Forex (FX) or cryptocurrency pair:
https://www.alphavantage.co/query?function=RSI&symbol=USDEUR&interval=weekly&time_period=10&series_type=open&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=RSI&symbol=IBM&interval=weekly&time_period=10&series_type=open&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

STOCHRSI

This API returns the stochastic relative strength index (STOCHRSI) values. See also: mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=STOCHRSI

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each STOCHRSI value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: fastkperiod

The time period of the fastk moving average. Positive integers are accepted. By default, fastkperiod=5.

❚ Optional: fastdperiod

The time period of the fastd moving average. Positive integers are accepted. By default, fastdperiod=3.

❚ Optional: fastdmatype

Moving average type for the fastd moving average. By default, fastdmatype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=STOCHRSI&symbol=IBM&interval=daily&time_period=10&series_type=close&fastkperiod=6&fastdmatype=1&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=STOCHRSI&symbol=IBM&interval=daily&time_period=10&series_type=close&fastkperiod=6&fastdmatype=1&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

WILLR

This API returns the Williams' %R (WILLR) values. See also: mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=WILLR

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each WILLR value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=WILLR&symbol=IBM&interval=daily&time_period=10&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=WILLR&symbol=IBM&interval=daily&time_period=10&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

ADX Trending

This API returns the average directional movement index (ADX) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=ADX

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each ADX value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
Equity:
https://www.alphavantage.co/query?function=ADX&symbol=IBM&interval=daily&time_period=10&apikey=demo

Forex (FX) or cryptocurrency pair:
https://www.alphavantage.co/query?function=ADX&symbol=USDEUR&interval=weekly&time_period=10&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=ADX&symbol=IBM&interval=daily&time_period=10&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

ADXR

This API returns the average directional movement index rating (ADXR) values. See also: mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=ADXR

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each ADXR value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=ADXR&symbol=IBM&interval=daily&time_period=10&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=ADXR&symbol=IBM&interval=daily&time_period=10&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

APO

This API returns the absolute price oscillator (APO) values. See also: mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=APO

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: fastperiod

Positive integers are accepted. By default, fastperiod=12.

❚ Optional: slowperiod

Positive integers are accepted. By default, slowperiod=26.

❚ Optional: matype

Moving average type. By default, matype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=APO&symbol=IBM&interval=daily&series_type=close&fastperiod=10&matype=1&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=APO&symbol=IBM&interval=daily&series_type=close&fastperiod=10&matype=1&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

PPO

This API returns the percentage price oscillator (PPO) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=PPO

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: fastperiod

Positive integers are accepted. By default, fastperiod=12.

❚ Optional: slowperiod

Positive integers are accepted. By default, slowperiod=26.

❚ Optional: matype

Moving average type. By default, matype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=PPO&symbol=IBM&interval=daily&series_type=close&fastperiod=10&matype=1&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=PPO&symbol=IBM&interval=daily&series_type=close&fastperiod=10&matype=1&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

MOM

This API returns the momentum (MOM) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=MOM

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each MOM value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=MOM&symbol=IBM&interval=daily&time_period=10&series_type=close&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=MOM&symbol=IBM&interval=daily&time_period=10&series_type=close&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

BOP

This API returns the balance of power (BOP) values.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=BOP

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=BOP&symbol=IBM&interval=daily&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=BOP&symbol=IBM&interval=daily&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

CCI Trending

This API returns the commodity channel index (CCI) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=CCI

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each CCI value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
Equity:
https://www.alphavantage.co/query?function=CCI&symbol=IBM&interval=daily&time_period=10&apikey=demo

Forex (FX) or cryptocurrency pair:
https://www.alphavantage.co/query?function=CCI&symbol=USDEUR&interval=weekly&time_period=10&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=CCI&symbol=IBM&interval=daily&time_period=10&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

CMO

This API returns the Chande momentum oscillator (CMO) values. See also: mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=CMO

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each CMO value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=CMO&symbol=IBM&interval=weekly&time_period=10&series_type=close&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=CMO&symbol=IBM&interval=weekly&time_period=10&series_type=close&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

ROC

This API returns the rate of change (ROC) values. See also: Investopedia article.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=ROC

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each ROC value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=ROC&symbol=IBM&interval=weekly&time_period=10&series_type=close&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=ROC&symbol=IBM&interval=weekly&time_period=10&series_type=close&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

ROCR

This API returns the rate of change ratio (ROCR) values. See also: Investopedia article.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=ROCR

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each ROCR value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=ROCR&symbol=IBM&interval=daily&time_period=10&series_type=close&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=ROCR&symbol=IBM&interval=daily&time_period=10&series_type=close&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

AROON Trending

This API returns the Aroon (AROON) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=AROON

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each AROON value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
Equity:
https://www.alphavantage.co/query?function=AROON&symbol=IBM&interval=daily&time_period=14&apikey=demo

Forex (FX) or cryptocurrency pair:
https://www.alphavantage.co/query?function=AROON&symbol=USDEUR&interval=weekly&time_period=14&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=AROON&symbol=IBM&interval=daily&time_period=14&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

AROONOSC

This API returns the Aroon oscillator (AROONOSC) values. See also: mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=AROONOSC

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each AROONOSC value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=AROONOSC&symbol=IBM&interval=daily&time_period=10&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=AROONOSC&symbol=IBM&interval=daily&time_period=10&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

MFI

This API returns the money flow index (MFI) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=MFI

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each MFI value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=MFI&symbol=IBM&interval=weekly&time_period=10&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=MFI&symbol=IBM&interval=weekly&time_period=10&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

TRIX

This API returns the 1-day rate of change of a triple smooth exponential moving average (TRIX) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=TRIX

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each TRIX value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=TRIX&symbol=IBM&interval=daily&time_period=10&series_type=close&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=TRIX&symbol=IBM&interval=daily&time_period=10&series_type=close&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

ULTOSC

This API returns the ultimate oscillator (ULTOSC) values. See also: mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=ULTOSC

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Optional: timeperiod1

The first time period for the indicator. Positive integers are accepted. By default, timeperiod1=7.

❚ Optional: timeperiod2

The second time period for the indicator. Positive integers are accepted. By default, timeperiod2=14.

❚ Optional: timeperiod3

The third time period for the indicator. Positive integers are accepted. By default, timeperiod3=28.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Examples (click for JSON output)
https://www.alphavantage.co/query?function=ULTOSC&symbol=IBM&interval=daily&timeperiod1=8&apikey=demo

https://www.alphavantage.co/query?function=ULTOSC&symbol=IBM&interval=daily&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=ULTOSC&symbol=IBM&interval=daily&timeperiod1=8&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

DX

This API returns the directional movement index (DX) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=DX

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each DX value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=DX&symbol=IBM&interval=daily&time_period=10&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=DX&symbol=IBM&interval=daily&time_period=10&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

MINUS_DI

This API returns the minus directional indicator (MINUS_DI) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=MINUS_DI

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each MINUS_DI value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=MINUS_DI&symbol=IBM&interval=weekly&time_period=10&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=MINUS_DI&symbol=IBM&interval=weekly&time_period=10&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

PLUS_DI

This API returns the plus directional indicator (PLUS_DI) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=PLUS_DI

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each PLUS_DI value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=PLUS_DI&symbol=IBM&interval=daily&time_period=10&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=PLUS_DI&symbol=IBM&interval=daily&time_period=10&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

MINUS_DM

This API returns the minus directional movement (MINUS_DM) values. See also: Investopedia article


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=MINUS_DM

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each MINUS_DM value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=MINUS_DM&symbol=IBM&interval=daily&time_period=10&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=MINUS_DM&symbol=IBM&interval=daily&time_period=10&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

PLUS_DM

This API returns the plus directional movement (PLUS_DM) values. See also: Investopedia article


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=PLUS_DM

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each PLUS_DM value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=PLUS_DM&symbol=IBM&interval=daily&time_period=10&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=PLUS_DM&symbol=IBM&interval=daily&time_period=10&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

BBANDS Trending

This API returns the Bollinger bands (BBANDS) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=BBANDS

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each BBANDS value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: nbdevup

The standard deviation multiplier of the upper band. Positive integers are accepted. By default, nbdevup=2.

❚ Optional: nbdevdn

The standard deviation multiplier of the lower band. Positive integers are accepted. By default, nbdevdn=2.

❚ Optional: matype

Moving average type of the time series. By default, matype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
Equity:
https://www.alphavantage.co/query?function=BBANDS&symbol=IBM&interval=weekly&time_period=5&series_type=close&nbdevup=3&nbdevdn=3&apikey=demo

Forex (FX) or cryptocurrency pair:
https://www.alphavantage.co/query?function=BBANDS&symbol=USDEUR&interval=weekly&time_period=5&series_type=close&nbdevup=3&nbdevdn=3&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=BBANDS&symbol=IBM&interval=weekly&time_period=5&series_type=close&nbdevup=3&nbdevdn=3&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

MIDPOINT

This API returns the midpoint (MIDPOINT) values. MIDPOINT = (highest value + lowest value)/2.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=MIDPOINT

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each MIDPOINT value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=MIDPOINT&symbol=IBM&interval=daily&time_period=10&series_type=close&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=MIDPOINT&symbol=IBM&interval=daily&time_period=10&series_type=close&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

MIDPRICE

This API returns the midpoint price (MIDPRICE) values. MIDPRICE = (highest high + lowest low)/2.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=MIDPRICE

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each MIDPRICE value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=MIDPRICE&symbol=IBM&interval=daily&time_period=10&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=MIDPRICE&symbol=IBM&interval=daily&time_period=10&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

SAR

This API returns the parabolic SAR (SAR) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=SAR

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Optional: acceleration

The acceleration factor. Positive floats are accepted. By default, acceleration=0.01.

❚ Optional: maximum

The acceleration factor maximum value. Positive floats are accepted. By default, maximum=0.20.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=SAR&symbol=IBM&interval=weekly&acceleration=0.05&maximum=0.25&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=SAR&symbol=IBM&interval=weekly&acceleration=0.05&maximum=0.25&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

TRANGE

This API returns the true range (TRANGE) values. See also: mathematical reference


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=TRANGE

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=TRANGE&symbol=IBM&interval=daily&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=TRANGE&symbol=IBM&interval=daily&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

ATR

This API returns the average true range (ATR) values. See also: Investopedia article and mathematical reference


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=ATR

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each ATR value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=ATR&symbol=IBM&interval=daily&time_period=14&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=ATR&symbol=IBM&interval=daily&time_period=14&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

NATR

This API returns the normalized average true range (NATR) values.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=NATR

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required:time_period

Number of data points used to calculate each NATR value. Positive integers are accepted (e.g., time_period=60, time_period=200)

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=NATR&symbol=IBM&interval=weekly&time_period=14&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=NATR&symbol=IBM&interval=weekly&time_period=14&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

AD Trending

This API returns the Chaikin A/D line (AD) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=AD

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=AD&symbol=IBM&interval=daily&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=AD&symbol=IBM&interval=daily&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

ADOSC

This API returns the Chaikin A/D oscillator (ADOSC) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=ADOSC

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Optional: fastperiod

The time period of the fast EMA. Positive integers are accepted. By default, fastperiod=3.

❚ Optional: slowperiod

The time period of the slow EMA. Positive integers are accepted. By default, slowperiod=10.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example(click for JSON output)
https://www.alphavantage.co/query?function=ADOSC&symbol=IBM&interval=daily&fastperiod=5&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=ADOSC&symbol=IBM&interval=daily&fastperiod=5&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

OBV Trending

This API returns the on balance volume (OBV) values. See also: Investopedia article and mathematical reference.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=OBV

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=OBV&symbol=IBM&interval=weekly&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=OBV&symbol=IBM&interval=weekly&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

HT_TRENDLINE

This API returns the Hilbert transform, instantaneous trendline (HT_TRENDLINE) values.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=HT_TRENDLINE

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=HT_TRENDLINE&symbol=IBM&interval=daily&series_type=close&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=HT_TRENDLINE&symbol=IBM&interval=daily&series_type=close&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

HT_SINE

This API returns the Hilbert transform, sine wave (HT_SINE) values.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=HT_SINE

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=HT_SINE&symbol=IBM&interval=daily&series_type=close&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=HT_SINE&symbol=IBM&interval=daily&series_type=close&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

HT_TRENDMODE

This API returns the Hilbert transform, trend vs cycle mode (HT_TRENDMODE) values.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=HT_TRENDMODE

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=HT_TRENDMODE&symbol=IBM&interval=weekly&series_type=close&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=HT_TRENDMODE&symbol=IBM&interval=weekly&series_type=close&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

HT_DCPERIOD

This API returns the Hilbert transform, dominant cycle period (HT_DCPERIOD) values.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=HT_DCPERIOD

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=HT_DCPERIOD&symbol=IBM&interval=daily&series_type=close&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=HT_DCPERIOD&symbol=IBM&interval=daily&series_type=close&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

HT_DCPHASE

This API returns the Hilbert transform, dominant cycle phase (HT_DCPHASE) values.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=HT_DCPHASE

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=HT_DCPHASE&symbol=IBM&interval=daily&series_type=close&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=HT_DCPHASE&symbol=IBM&interval=daily&series_type=close&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

## HT_PHASOR

This API returns the Hilbert transform, phasor components (HT_PHASOR) values.


API Parameters
❚ Required: function

The technical indicator of your choice. In this case, function=HT_PHASOR

❚ Required: symbol

The name of the ticker of your choice. For example: symbol=IBM

❚ Required: interval

Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly

❚ Optional: month

By default, this parameter is not set and the technical indicator values will be calculated based on the default length of the underlying intraday, daily, weekly, or monthly time series data. You can use the month parameter (in YYYY-MM format) to return technical indicators for a specific month in history. For example, month=2009-01.

❚ Required: series_type

The desired price type in the time series. Four types are supported: close, open, high, low

❚ Optional: datatype

By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.

❚ Required: apikey

Your API key. Claim your free API key here.


Example (click for JSON output)
https://www.alphavantage.co/query?function=HT_PHASOR&symbol=IBM&interval=weekly&series_type=close&apikey=demo


Language-specific guides
Python NodeJS PHP C#/.NET ✨MCP & Other
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=HT_PHASOR&symbol=IBM&interval=weekly&series_type=close&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

Copyright © Alpha Vantage Inc. 2017-2025