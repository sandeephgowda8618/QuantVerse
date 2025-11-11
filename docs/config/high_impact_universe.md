# High-Impact Asset Universe Configuration

## Market Coverage Strategy

To ensure balanced market coverage, we collect Alpha Vantage fundamentals and light technical indicators for a curated list of high-impact assets across multiple sectors and market regimes. The universe includes mega-cap technology (AAPL, MSFT, NVDA, AMZN, GOOGL), banks and rate-sensitive financials (JPM, BAC, GS), commodities and energy majors (XOM, CVX), defensives and industrials (BA, CAT, LMT), consumer and retail leaders (WMT, COST, MCD), pharmaceutical majors (JNJ, PFE, MRK), and benchmark ETFs (SPY, QQQ, IWM). We also include crypto assets (BTC-USD, ETH-USD) to support the sudden-move explainer and infra-risk modules. This basket provides broad sector diversity, high liquidity, and strong news flow while minimizing API cost.

## Implementation

The high-impact ticker pipeline is implemented as a temporary, detachable component (`run_high_impact_pipeline.py`) that can operate independently of the main 200-company ingestion system. This design allows for immediate market coverage while the full-scale pipeline develops, with the ability to cleanly remove the component when no longer needed.

### Key Characteristics
- **35 strategically selected tickers** across 8 market sectors
- **8 endpoints per ticker** (fundamentals + technical indicators)
- **~280 total API calls** fitting within free-tier daily limits
- **Sector-based filtering** for targeted analysis
- **Direct asset table integration** for seamless workflow integration
- **Clean detachment capability** for future system evolution
