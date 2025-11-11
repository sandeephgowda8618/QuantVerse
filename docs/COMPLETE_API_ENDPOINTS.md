# 📊 QuantVerse uRISK - Complete API Endpoint Reference

*All 14 endpoints across 4 specialized financial analysis modules*

---

## 🎯 **COMPLETE ENDPOINT LIST**

### 🛡️ **Core Risk Module** (3 endpoints)
```http
1.  GET  /risk-alerts           # Get current risk alerts with filtering
2.  GET  /assets               # Get list of available asset tickers  
3.  GET  /assets/details       # Get detailed asset information
```

### 📈 **Member 1 - Options Flow Interpreter** (3 endpoints)
```http
4.  POST /member1/options-flow              # Analyze options flow activity
5.  GET  /member1/options-flow/health       # Module health check
6.  GET  /member1/options-flow/recent/{ticker}  # Recent options activity
```

### ⚡ **Member 2 - Sudden Market Move Explainer** (5 endpoints) 
```http
7.  POST /member2/explain-move              # Explain specific market movements
8.  GET  /member2/detect-moves/{ticker}     # Detect recent significant moves  
9.  GET  /member2/explain-move/health       # Module health check
10. GET  /member2/explain-move/anomalies/{ticker}  # Get movement anomalies
11. GET  /member2/explain-move/timeline/{ticker}   # Movement timeline analysis
```

### 📰 **Member 3 - Macro-Driven Gap Forecaster** (7 endpoints)
```http
12. POST /member3/macro-gap                 # Predict overnight gaps
13. GET  /member3/macro-events/{asset}      # Recent macro events affecting asset
14. GET  /member3/gap-history/{asset}       # Historical gap patterns
15. POST /member3/batch-gap-prediction      # Batch gap predictions for multiple assets
16. GET  /member3/macro-gap/health          # Module health check  
17. GET  /member3/macro-gap/sentiment/{asset}    # Macro sentiment analysis
18. GET  /member3/macro-gap/patterns/{asset}     # Gap pattern analysis
```

---

## 📋 **ENDPOINT SUMMARY BY MODULE**

| Module | Prefix | Count | Purpose |
|--------|--------|-------|---------|
| **Core Risk** | `/` | 3 | Risk alerts and asset management |
| **Member 1** | `/member1` | 3 | Options flow analysis |
| **Member 2** | `/member2` | 5 | Market movement explanation |
| **Member 3** | `/member3` | 7 | Macro gap forecasting |
| **TOTAL** | - | **18** | Complete financial analysis platform |

---

## 🔧 **ENDPOINT DETAILS**

### **Core Risk Module**

#### 1. `GET /risk-alerts`
**Purpose**: Retrieve current risk alerts  
**Parameters**: 
- `ticker` (optional): Filter by specific ticker
- `severity` (optional): Filter by severity level
- `limit` (default 50): Maximum alerts to return

#### 2. `GET /assets` 
**Purpose**: Get list of available asset tickers
**Returns**: Array of ticker symbols

#### 3. `GET /assets/details`
**Purpose**: Get detailed asset information
**Returns**: Complete asset metadata including sectors, exchanges

### **Member 1 - Options Flow**

#### 4. `POST /member1/options-flow`
**Purpose**: Analyze options flow activity
**Body**: `{"ticker": "TSLA", "user_question": "Are institutions buying calls?"}`

#### 5. `GET /member1/options-flow/health`
**Purpose**: Module health check
**Returns**: Health status and dependencies

#### 6. `GET /member1/options-flow/recent/{ticker}`
**Purpose**: Get recent options activity for specific ticker
**Parameters**: `ticker` - Asset ticker symbol

### **Member 2 - Market Move Explainer**

#### 7. `POST /member2/explain-move`
**Purpose**: Explain specific market movements
**Body**: `{"ticker": "BTC", "timestamp": "2025-11-10T14:30:00Z"}`

#### 8. `GET /member2/detect-moves/{ticker}`
**Purpose**: Detect recent significant price movements
**Parameters**: `ticker` - Asset ticker symbol

#### 9. `GET /member2/explain-move/health`
**Purpose**: Module health check

#### 10. `GET /member2/explain-move/anomalies/{ticker}`
**Purpose**: Get movement anomalies for ticker

#### 11. `GET /member2/explain-move/timeline/{ticker}`
**Purpose**: Movement timeline analysis

### **Member 3 - Macro Gap Forecaster**

#### 12. `POST /member3/macro-gap`
**Purpose**: Predict overnight gaps based on macro events
**Body**: `{"asset": "NASDAQ", "question": "Gap direction after FOMC?"}`

#### 13. `GET /member3/macro-events/{asset}`
**Purpose**: Get recent macro events affecting asset

#### 14. `GET /member3/gap-history/{asset}`
**Purpose**: Historical gap patterns for asset

#### 15. `POST /member3/batch-gap-prediction`
**Purpose**: Batch gap predictions for multiple assets
**Body**: `{"assets": ["NASDAQ", "SPY", "BTC"]}`

#### 16. `GET /member3/macro-gap/health`
**Purpose**: Module health check

#### 17. `GET /member3/macro-gap/sentiment/{asset}`
**Purpose**: Macro sentiment analysis for asset

#### 18. `GET /member3/macro-gap/patterns/{asset}`
**Purpose**: Gap pattern analysis for asset

---

## 🚀 **API USAGE EXAMPLES**

### **Risk Monitoring**
```bash
# Get high-severity alerts for AAPL
curl "http://localhost:8000/risk-alerts?ticker=AAPL&severity=high"
```

### **Options Flow Analysis**
```bash
# Analyze TSLA options flow
curl -X POST "http://localhost:8000/member1/options-flow" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "TSLA", "user_question": "Are big traders bullish?"}'
```

### **Market Move Explanation**
```bash
# Explain BTC movement at specific time
curl -X POST "http://localhost:8000/member2/explain-move" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "BTC", "timestamp": "2025-11-10T14:30:00Z"}'
```

### **Macro Gap Prediction**
```bash
# Predict NASDAQ gap after FOMC
curl -X POST "http://localhost:8000/member3/macro-gap" \
  -H "Content-Type: application/json" \
  -d '{"asset": "NASDAQ", "question": "Gap up or down after Fed announcement?"}'
```

---

## 📊 **TOTAL: 18 API ENDPOINTS**

Your QuantVerse uRISK platform provides **18 specialized financial analysis endpoints** across 4 modules, offering comprehensive coverage of:

- **Risk Monitoring** (3 endpoints)
- **Options Flow Analysis** (3 endpoints)  
- **Market Movement Explanation** (5 endpoints)
- **Macro Gap Forecasting** (7 endpoints)

**Complete institutional-grade financial intelligence platform! 🎯🚀**
