# QuantVerse uRISK - System Configuration Checklist
**Date:** November 6, 2025  
**Status:** Configuration Required Before Production

## 🎯 Critical Configuration Tasks

### 1. PostgreSQL Database Configuration
**Status**: ❌ CRITICAL - Authentication Failed

**Required Actions**:
```bash
# 1. Update .env file with correct database credentials
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/urisk_core
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=urisk_core
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# 2. Ensure PostgreSQL is running
brew services start postgresql
# OR
sudo service postgresql start

# 3. Create database and user (if needed)
psql postgres
CREATE DATABASE urisk_core;
CREATE USER your_username WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE urisk_core TO your_username;
```

### 2. API Keys Configuration
**Status**: ❌ CRITICAL - All Keys Missing

**Required API Keys**:

#### Essential Data Providers
```bash
# Market Data
FINNHUB_API_KEY=your_finnhub_key_here
TIINGO_API_KEY=your_tiingo_key_here
POLYGON_API_KEY=your_polygon_key_here

# Trading Data
ALPACA_API_KEY=your_alpaca_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_here

# AI/ML Services
PERPLEXITY_API_KEY=your_perplexity_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional for advanced embeddings
```

#### How to Obtain Each Key:

**Finnhub** (Market Data & News):
- Visit: https://finnhub.io/register
- Free tier: 60 API calls/minute
- Documentation: https://finnhub.io/docs/api

**Tiingo** (Financial Data):
- Visit: https://api.tiingo.com/
- Free tier: 500 requests/day
- Documentation: https://api.tiingo.com/docs/

**Polygon** (Options & Derivatives):
- Visit: https://polygon.io/
- Free tier: 5 requests/minute
- Documentation: https://polygon.io/docs

**Alpaca** (Trading Data):
- Visit: https://alpaca.markets/
- Paper trading account available
- Documentation: https://alpaca.markets/docs/

**Perplexity** (AI News Analysis):
- Visit: https://www.perplexity.ai/
- API access required
- Documentation: https://docs.perplexity.ai/

**OpenAI** (Advanced Embeddings - Optional):
- Visit: https://platform.openai.com/
- Pay-per-use pricing
- Documentation: https://platform.openai.com/docs

## 3. Network Configuration
**Status**: ⚠️ MEDIUM - DNS/Connectivity Issues

**Issues Detected**:
- Yahoo Finance DNS resolution failures
- SEC website connection timeouts
- Some API endpoints returning 403/404 errors

**Recommended Actions**:
```bash
# Test DNS resolution
nslookup query1.finance.yahoo.com
nslookup www.sec.gov

# Test API endpoints manually
curl -I "https://finnhub.io/api/v1/quote?symbol=AAPL&token=YOUR_TOKEN"
curl -I "https://api.tiingo.com/tiingo/daily/AAPL/prices"

# Check firewall/proxy settings if needed
```

## 🧪 Validation Steps After Configuration

### Step 1: Test Database Connection
```bash
cd /Users/sandeeph/Documents/QuantVerse/urisk
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
from backend.database.handler import DatabaseHandler
db = DatabaseHandler()
print('Database connection successful!')
"
```

### Step 2: Test API Keys
```bash
cd /Users/sandeeph/Documents/QuantVerse/urisk
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
from backend.data_ingestion.market_data.finnhub_collector import FinnhubCollector
collector = FinnhubCollector()
data = collector.get_quote('AAPL')
print('API key working!', data)
"
```

### Step 3: Run Full Integration Test
```bash
cd /Users/sandeeph/Documents/QuantVerse/urisk
python test_data_integration.py
```

## 📋 Configuration File Template

Create or update your `.env` file:

```bash
# Database Configuration
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/urisk_core
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=urisk_core
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# ChromaDB Configuration (Working - No Changes Needed)
CHROMA_DB_PATH=./data/chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Essential API Keys
FINNHUB_API_KEY=your_finnhub_key_here
TIINGO_API_KEY=your_tiingo_key_here
POLYGON_API_KEY=your_polygon_key_here
ALPACA_API_KEY=your_alpaca_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_here
PERPLEXITY_API_KEY=your_perplexity_key_here

# Optional API Keys
OPENAI_API_KEY=your_openai_key_here
TRADIER_API_KEY=your_tradier_key_here

# Application Configuration
DEBUG=True
LOG_LEVEL=INFO
DATA_UPDATE_INTERVAL=300
MAX_RETRIES=3
TIMEOUT_SECONDS=30
```

## ✅ Success Criteria

After completing configuration, you should see:

1. **Database Connection**: ✅ PostgreSQL authentication successful
2. **API Keys**: ✅ All 6 essential keys working
3. **Data Collection**: ✅ Real market data being collected
4. **Vector Storage**: ✅ Embeddings being stored in ChromaDB
5. **Pipeline Flow**: ✅ End-to-end data processing working

## 🚨 Common Issues & Solutions

### Issue: PostgreSQL Connection Failed
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql
# Start if not running
brew services start postgresql
```

### Issue: API Rate Limits
```bash
# Implement delays between requests
# Most free tiers have rate limits
# Consider upgrading to paid tiers for production
```

### Issue: Network Timeouts
```bash
# Increase timeout values in .env
TIMEOUT_SECONDS=60
# Check internet connectivity
# Consider using VPN if region-blocked
```

## 📞 Support Resources

- **PostgreSQL Setup**: https://www.postgresql.org/docs/
- **API Documentation**: See individual provider docs above
- **Python Environment**: Already configured and working ✅
- **ChromaDB**: Already working ✅

---

**Next Step**: Complete this configuration, then rerun the integration test to achieve 100% success rate!
