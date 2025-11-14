# QuantVerse Database Structure Documentation

This document provides a comprehensive overview of the QuantVerse database structure,
including all tables, their schemas, and sample data.

**Generated on:** 2025-11-12 22:02:38

## Database Overview

**Total Tables:** 55

### Table List

- `active_alerts` (VIEW)
- `alerts` (BASE TABLE)
- `alpha_analytics_data` (BASE TABLE)
- `alpha_commodities_data` (BASE TABLE)
- `alpha_crypto_data` (BASE TABLE)
- `alpha_economic_indicators` (BASE TABLE)
- `alpha_forex_data` (BASE TABLE)
- `alpha_fundamental_data` (BASE TABLE)
- `alpha_ingestion_logs` (BASE TABLE)
- `alpha_ingestion_overview` (VIEW)
- `alpha_ingestion_progress` (BASE TABLE)
- `alpha_ingestion_sequence` (BASE TABLE)
- `alpha_market_data` (BASE TABLE)
- `alpha_news_intelligence` (BASE TABLE)
- `alpha_technical_indicators` (BASE TABLE)
- `alpha_vantage_data` (BASE TABLE)
- `anomalies` (BASE TABLE)
- `assets` (BASE TABLE)
- `chroma_embeddings` (BASE TABLE)
- `commodities_prices` (BASE TABLE)
- `company_overviews` (VIEW)
- `crypto_prices` (BASE TABLE)
- `dividends_data` (BASE TABLE)
- `earnings_calendar` (BASE TABLE)
- `earnings_data` (BASE TABLE)
- `economic_indicators` (BASE TABLE)
- `economic_indicators_summary` (VIEW)
- `forecasts` (BASE TABLE)
- `forex_prices` (BASE TABLE)
- `fundamental_data` (BASE TABLE)
- `infra_incidents` (BASE TABLE)
- `infra_incidents_old` (BASE TABLE)
- `infrastructure_status` (BASE TABLE)
- `ingestion_progress` (BASE TABLE)
- `ingestion_sessions` (BASE TABLE)
- `insider_transactions` (BASE TABLE)
- `latest_commodities_prices` (VIEW)
- `latest_company_overview` (VIEW)
- `latest_crypto_prices` (VIEW)
- `latest_forex_rates` (VIEW)
- `latest_market_data` (VIEW)
- `listing_status` (BASE TABLE)
- `market_movers` (BASE TABLE)
- `market_prices` (BASE TABLE)
- `news_headlines` (BASE TABLE)
- `news_sentiment` (BASE TABLE)
- `options_data` (BASE TABLE)
- `price_gaps` (BASE TABLE)
- `query_performance_log` (BASE TABLE)
- `recent_market_activity` (VIEW)
- `regulatory_events` (BASE TABLE)
- `splits_data` (BASE TABLE)
- `technical_indicators` (BASE TABLE)
- `ticker_sentiment` (BASE TABLE)
- `vector_sync_state` (BASE TABLE)

---

## Table: `active_alerts` (VIEW)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | Yes | None | N/A |
| `ticker` | character varying | Yes | None | 20 |
| `risk_type` | character varying | Yes | None | 30 |
| `severity` | character varying | Yes | None | 10 |
| `message` | text | Yes | None | N/A |
| `triggered_at` | timestamp with time zone | Yes | None | N/A |
| `asset_type` | character varying | Yes | None | 25 |
| `exchange` | character varying | Yes | None | 50 |

**Total Records:** 2

### Sample Data

| id | ticker | risk_type | severity | message | triggered_at | asset_type | exchange |
|-----|--------|-----------|----------|---------|--------------|------------|----------|
| 1 | NVDA | technical | high | Price volatility spike detected | 2025-11-10 07:33:15.973884+00:00 | stock | NASDAQ |
| 2 | MSFT | liquidity | medium | Trading volume anomaly | 2025-11-10 09:33:15.973884+00:00 | stock | NASDAQ |

---

## Table: `alerts` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('alerts_id_seq'::regclass) | N/A |
| `ticker` | character varying | Yes | None | 20 |
| `risk_type` | character varying | Yes | None | 30 |
| `severity` | character varying | Yes | None | 10 |
| `message` | text | Yes | None | N/A |
| `triggered_at` | timestamp with time zone | Yes | now() | N/A |
| `read` | boolean | Yes | false | N/A |
| `resolved` | boolean | Yes | false | N/A |

**Total Records:** 3

### Sample Data

| id | ticker | risk_type | severity | message | triggered_at | read | resolved |
|-----|--------|-----------|----------|---------|--------------|------|----------|
| 1 | NVDA | technical | high | Price volatility spike detected | 2025-11-10 07:33:15.973884+00:00 | False | False |
| 2 | MSFT | liquidity | medium | Trading volume anomaly | 2025-11-10 09:33:15.973884+00:00 | False | False |
| 3 | AAPL | regulatory | high | Regulatory announcement pending | 2025-11-10 05:33:15.973884+00:00 | True | False |

---

## Table: `alpha_analytics_data` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('alpha_analytics_data_id_seq'::regclass) | N/A |
| `symbols` | text | No | None | N/A |
| `endpoint` | character varying | No | None | 100 |
| `api_function` | character varying | No | None | 100 |
| `calculation_type` | character varying | No | None | 50 |
| `range_start` | date | Yes | None | N/A |
| `range_end` | date | Yes | None | N/A |
| `interval_type` | character varying | Yes | None | 20 |
| `window_size` | integer | Yes | None | N/A |
| `results` | jsonb | No | None | N/A |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 50 |
| `raw_payload` | jsonb | No | None | N/A |
| `quality_flag` | character varying | Yes | 'complete'::character varying | 20 |
| `ingestion_epoch` | integer | No | None | N/A |
| `ingestion_sequence` | bigint | No | None | N/A |
| `ingestion_time` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `alpha_commodities_data` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('alpha_commodities_data_id_seq'::regclass) | N/A |
| `commodity` | character varying | No | None | 50 |
| `endpoint` | character varying | No | None | 100 |
| `api_function` | character varying | No | None | 100 |
| `timestamp` | timestamp with time zone | No | None | N/A |
| `interval_type` | character varying | Yes | None | 20 |
| `price` | numeric | Yes | None | N/A |
| `unit` | character varying | Yes | None | 20 |
| `currency` | character varying | Yes | 'USD'::character varying | 10 |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 50 |
| `raw_payload` | jsonb | No | None | N/A |
| `quality_flag` | character varying | Yes | 'complete'::character varying | 20 |
| `ingestion_epoch` | integer | No | None | N/A |
| `ingestion_sequence` | bigint | No | None | N/A |
| `ingestion_time` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `alpha_crypto_data` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('alpha_crypto_data_id_seq'::regclass) | N/A |
| `symbol` | character varying | No | None | 20 |
| `market` | character varying | No | None | 20 |
| `endpoint` | character varying | No | None | 100 |
| `api_function` | character varying | No | None | 100 |
| `timestamp` | timestamp with time zone | No | None | N/A |
| `interval_type` | character varying | Yes | None | 20 |
| `open_price_usd` | numeric | Yes | None | N/A |
| `high_price_usd` | numeric | Yes | None | N/A |
| `low_price_usd` | numeric | Yes | None | N/A |
| `close_price_usd` | numeric | Yes | None | N/A |
| `open_price_market` | numeric | Yes | None | N/A |
| `high_price_market` | numeric | Yes | None | N/A |
| `low_price_market` | numeric | Yes | None | N/A |
| `close_price_market` | numeric | Yes | None | N/A |
| `volume` | numeric | Yes | None | N/A |
| `market_cap_usd` | numeric | Yes | None | N/A |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 50 |
| `raw_payload` | jsonb | No | None | N/A |
| `quality_flag` | character varying | Yes | 'complete'::character varying | 20 |
| `ingestion_epoch` | integer | No | None | N/A |
| `ingestion_sequence` | bigint | No | None | N/A |
| `ingestion_time` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `alpha_economic_indicators` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('alpha_economic_indicators_id_seq'::reg... | N/A |
| `indicator` | character varying | No | None | 50 |
| `endpoint` | character varying | No | None | 100 |
| `api_function` | character varying | No | None | 100 |
| `timestamp` | timestamp with time zone | No | None | N/A |
| `interval_type` | character varying | Yes | None | 20 |
| `value` | numeric | Yes | None | N/A |
| `unit` | character varying | Yes | None | 50 |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 50 |
| `raw_payload` | jsonb | No | None | N/A |
| `quality_flag` | character varying | Yes | 'complete'::character varying | 20 |
| `ingestion_epoch` | integer | No | None | N/A |
| `ingestion_sequence` | bigint | No | None | N/A |
| `ingestion_time` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `alpha_forex_data` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('alpha_forex_data_id_seq'::regclass) | N/A |
| `from_currency` | character varying | No | None | 10 |
| `to_currency` | character varying | No | None | 10 |
| `currency_pair` | character varying | No | None | 20 |
| `endpoint` | character varying | No | None | 100 |
| `api_function` | character varying | No | None | 100 |
| `timestamp` | timestamp with time zone | No | None | N/A |
| `interval_type` | character varying | Yes | None | 20 |
| `exchange_rate` | numeric | Yes | None | N/A |
| `open_rate` | numeric | Yes | None | N/A |
| `high_rate` | numeric | Yes | None | N/A |
| `low_rate` | numeric | Yes | None | N/A |
| `close_rate` | numeric | Yes | None | N/A |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 50 |
| `raw_payload` | jsonb | No | None | N/A |
| `quality_flag` | character varying | Yes | 'complete'::character varying | 20 |
| `ingestion_epoch` | integer | No | None | N/A |
| `ingestion_sequence` | bigint | No | None | N/A |
| `ingestion_time` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `alpha_fundamental_data` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('alpha_fundamental_data_id_seq'::regclass) | N/A |
| `ticker` | character varying | No | None | 20 |
| `endpoint` | character varying | No | None | 100 |
| `api_function` | character varying | No | None | 100 |
| `data_type` | character varying | No | None | 50 |
| `fiscal_date_ending` | date | Yes | None | N/A |
| `reported_currency` | character varying | Yes | None | 10 |
| `period_type` | character varying | Yes | None | 20 |
| `financial_data` | jsonb | No | None | N/A |
| `total_revenue` | numeric | Yes | None | N/A |
| `net_income` | numeric | Yes | None | N/A |
| `total_assets` | numeric | Yes | None | N/A |
| `total_liabilities` | numeric | Yes | None | N/A |
| `shareholders_equity` | numeric | Yes | None | N/A |
| `eps` | numeric | Yes | None | N/A |
| `pe_ratio` | numeric | Yes | None | N/A |
| `market_cap` | numeric | Yes | None | N/A |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 50 |
| `raw_payload` | jsonb | No | None | N/A |
| `quality_flag` | character varying | Yes | 'complete'::character varying | 20 |
| `ingestion_epoch` | integer | No | None | N/A |
| `ingestion_sequence` | bigint | No | None | N/A |
| `ingestion_time` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `alpha_ingestion_logs` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('alpha_ingestion_logs_id_seq'::regclass) | N/A |
| `ticker` | character varying | Yes | None | 20 |
| `endpoint` | character varying | No | None | 100 |
| `api_function` | character varying | No | None | 100 |
| `epoch` | integer | No | None | N/A |
| `started_at` | timestamp with time zone | Yes | now() | N/A |
| `completed_at` | timestamp with time zone | Yes | None | N/A |
| `duration_seconds` | numeric | Yes | None | N/A |
| `status` | character varying | No | None | 20 |
| `api_response_time_ms` | integer | Yes | None | N/A |
| `data_points_count` | integer | Yes | None | N/A |
| `error_message` | text | Yes | None | N/A |
| `http_status_code` | integer | Yes | None | N/A |
| `rate_limit_remaining` | integer | Yes | None | N/A |
| `rate_limit_reset_time` | timestamp with time zone | Yes | None | N/A |
| `missing_fields` | jsonb | Yes | None | N/A |
| `data_quality_score` | numeric | Yes | None | N/A |
| `ingestion_sequence` | bigint | No | None | N/A |
| `raw_request_params` | jsonb | Yes | None | N/A |

**Total Records:** 0

*No data available*

---

## Table: `alpha_ingestion_overview` (VIEW)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `epoch` | integer | Yes | None | N/A |
| `ticker` | character varying | Yes | None | 20 |
| `status` | character varying | Yes | None | 20 |
| `progress_percentage` | numeric | Yes | None | N/A |
| `completed_endpoints` | integer | Yes | None | N/A |
| `total_endpoints` | integer | Yes | None | N/A |
| `last_completed_endpoint` | character varying | Yes | None | 100 |
| `started_at` | timestamp without time zone | Yes | None | N/A |
| `updated_at` | timestamp without time zone | Yes | None | N/A |
| `runtime_minutes` | numeric | Yes | None | N/A |

**Total Records:** 0

*No data available*

---

## Table: `alpha_ingestion_progress` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('alpha_ingestion_progress_id_seq'::regc... | N/A |
| `ticker` | character varying | No | None | 20 |
| `last_completed_endpoint` | character varying | Yes | None | 100 |
| `last_completed_function` | character varying | Yes | None | 100 |
| `epoch` | integer | No | None | N/A |
| `total_endpoints` | integer | Yes | 0 | N/A |
| `completed_endpoints` | integer | Yes | 0 | N/A |
| `started_at` | timestamp without time zone | Yes | now() | N/A |
| `updated_at` | timestamp without time zone | Yes | now() | N/A |
| `status` | character varying | Yes | 'in_progress'::character varying | 20 |
| `error_message` | text | Yes | None | N/A |
| `retry_count` | integer | Yes | 0 | N/A |

**Total Records:** 0

*No data available*

---

## Table: `alpha_ingestion_sequence` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('alpha_ingestion_sequence_id_seq'::regc...) | N/A |
| `current_sequence` | bigint | Yes | 0 | N/A |
| `last_updated` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 1

### Sample Data

| id | current_sequence | last_updated |
|-----|------------------|--------------|
| 1 | 0 | 2025-11-07 20:45:25.051782+00:00 |

---

## Table: `alpha_market_data` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('alpha_market_data_id_seq'::regclass) | N/A |
| `ticker` | character varying | No | None | 20 |
| `endpoint` | character varying | No | None | 100 |
| `api_function` | character varying | No | None | 100 |
| `timestamp` | timestamp with time zone | No | None | N/A |
| `interval_type` | character varying | Yes | None | 20 |
| `open_price` | numeric | Yes | None | N/A |
| `high_price` | numeric | Yes | None | N/A |
| `low_price` | numeric | Yes | None | N/A |
| `close_price` | numeric | Yes | None | N/A |
| `adjusted_close` | numeric | Yes | None | N/A |
| `volume` | bigint | Yes | None | N/A |
| `dividend_amount` | numeric | Yes | None | N/A |
| `split_coefficient` | numeric | Yes | None | N/A |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 50 |
| `raw_payload` | jsonb | No | None | N/A |
| `parsed_values` | jsonb | Yes | None | N/A |
| `quality_flag` | character varying | Yes | 'complete'::character varying | 20 |
| `ingestion_epoch` | integer | No | None | N/A |
| `ingestion_sequence` | bigint | No | None | N/A |
| `ingestion_time` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `alpha_news_intelligence` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('alpha_news_intelligence_id_seq'::regcl... | N/A |
| `ticker` | character varying | Yes | None | 20 |
| `endpoint` | character varying | No | None | 100 |
| `api_function` | character varying | No | None | 100 |
| `title` | text | Yes | None | N/A |
| `url` | text | Yes | None | N/A |
| `published_at` | timestamp with time zone | Yes | None | N/A |
| `source_name` | character varying | Yes | None | 100 |
| `summary` | text | Yes | None | N/A |
| `overall_sentiment_score` | numeric | Yes | None | N/A |
| `overall_sentiment_label` | character varying | Yes | None | 20 |
| `ticker_sentiment_score` | numeric | Yes | None | N/A |
| `ticker_sentiment_label` | character varying | Yes | None | 20 |
| `relevance_score` | numeric | Yes | None | N/A |
| `topics` | jsonb | Yes | None | N/A |
| `category` | character varying | Yes | None | 100 |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 50 |
| `raw_payload` | jsonb | No | None | N/A |
| `quality_flag` | character varying | Yes | 'complete'::character varying | 20 |
| `ingestion_epoch` | integer | No | None | N/A |
| `ingestion_sequence` | bigint | No | None | N/A |
| `ingestion_time` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `alpha_technical_indicators` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('alpha_technical_indicators_id_seq'::re... | N/A |
| `ticker` | character varying | No | None | 20 |
| `endpoint` | character varying | No | None | 100 |
| `api_function` | character varying | No | None | 100 |
| `indicator_name` | character varying | No | None | 50 |
| `timestamp` | timestamp with time zone | No | None | N/A |
| `interval_type` | character varying | Yes | None | 20 |
| `value_1` | numeric | Yes | None | N/A |
| `value_2` | numeric | Yes | None | N/A |
| `value_3` | numeric | Yes | None | N/A |
| `value_4` | numeric | Yes | None | N/A |
| `value_5` | numeric | Yes | None | N/A |
| `indicator_values` | jsonb | Yes | None | N/A |
| `time_period` | integer | Yes | None | N/A |
| `series_type` | character varying | Yes | None | 20 |
| `parameters` | jsonb | Yes | None | N/A |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 50 |
| `raw_payload` | jsonb | No | None | N/A |
| `quality_flag` | character varying | Yes | 'complete'::character varying | 20 |
| `ingestion_epoch` | integer | No | None | N/A |
| `ingestion_sequence` | bigint | No | None | N/A |
| `ingestion_time` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `alpha_vantage_data` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('alpha_vantage_data_id_seq'::regclass) | N/A |
| `ticker` | character varying | No | None | 20 |
| `endpoint` | character varying | No | None | 50 |
| `timestamp` | timestamp with time zone | No | None | N/A |
| `raw_payload` | jsonb | No | None | N/A |
| `parsed_values` | jsonb | Yes | None | N/A |
| `quality_flag` | character varying | Yes | 'success'::character varying | 20 |
| `ingestion_epoch` | integer | Yes | None | N/A |
| `ingestion_sequence` | bigint | Yes | None | N/A |
| `ingestion_session_id` | character varying | Yes | None | 100 |
| `ingestion_time` | timestamp with time zone | Yes | now() | N/A |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 20 |
| `data_type` | character varying | Yes | None | 30 |
| `interval_period` | character varying | Yes | None | 10 |
| `metadata` | jsonb | Yes | None | N/A |

**Total Records:** 235,596

### Sample Data

| id | ticker | endpoint | timestamp | raw_payload | parsed_values | quality_flag | ingestion_epoch | ingestion_sequence | ingestion_session_id | ingestion_time | source | data_type | interval_period | metadata |
|-----|--------|----------|-----------|-------------|---------------|--------------|-----------------|--------------------|----------------------|----------------|--------|-----------|-----------------|----------|
| 156512 | NVDA | ATR | 2010-04-14 18:30:00+00:00 | {"Meta Data": {"1: Symbol": "NVDA", "4: Interva... | {"atr": 0.012, "meta_data": {"1: Symbol": "NVDA... | success | 1 | 1762617130004770 | alpha_ingestion_20251108_212207 | 2025-11-08 15:52:13.370977+00:00 | alpha_vantage | technical_indicator | daily | {"symbol": "NVDA", "indicator": "Average True R... |
| 156513 | NVDA | ATR | 2010-04-13 18:30:00+00:00 | {"Meta Data": {"1: Symbol": "NVDA", "4: Interva... | {"atr": 0.0122, "meta_data": {"1: Symbol": "NVD... | success | 1 | 1762617130004770 | alpha_ingestion_20251108_212207 | 2025-11-08 15:52:13.371824+00:00 | alpha_vantage | technical_indicator | daily | {"symbol": "NVDA", "indicator": "Average True R... |
| 156514 | NVDA | ATR | 2010-04-12 18:30:00+00:00 | {"Meta Data": {"1: Symbol": "NVDA", "4: Interva... | {"atr": 0.0122, "meta_data": {"1: Symbol": "NVD... | success | 1 | 1762617130004770 | alpha_ingestion_20251108_212207 | 2025-11-08 15:52:13.372665+00:00 | alpha_vantage | technical_indicator | daily | {"symbol": "NVDA", "indicator": "Average True R... |
| 156515 | NVDA | ATR | 2010-04-11 18:30:00+00:00 | {"Meta Data": {"1: Symbol": "NVDA", "4: Interva... | {"atr": 0.0123, "meta_data": {"1: Symbol": "NVD... | success | 1 | 1762617130004770 | alpha_ingestion_20251108_212207 | 2025-11-08 15:52:13.373514+00:00 | alpha_vantage | technical_indicator | daily | {"symbol": "NVDA", "indicator": "Average True R... |
| 156516 | NVDA | ATR | 2010-04-08 18:30:00+00:00 | {"Meta Data": {"1: Symbol": "NVDA", "4: Interva... | {"atr": 0.0125, "meta_data": {"1: Symbol": "NVD... | success | 1 | 1762617130004770 | alpha_ingestion_20251108_212207 | 2025-11-08 15:52:13.374352+00:00 | alpha_vantage | technical_indicator | daily | {"symbol": "NVDA", "indicator": "Average True R... |

---

## Table: `anomalies` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('anomalies_id_seq'::regclass) | N/A |
| `ticker` | character varying | Yes | None | 20 |
| `metric` | character varying | Yes | None | 50 |
| `anomaly_score` | double precision | Yes | None | N/A |
| `severity` | character varying | Yes | None | 10 |
| `explanation` | text | Yes | None | N/A |
| `timestamp` | timestamp with time zone | Yes | None | N/A |
| `detected_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 2,763

### Sample Data

| id | ticker | metric | anomaly_score | severity | explanation | timestamp | detected_at |
|-----|--------|--------|---------------|----------|-------------|-----------|-------------|
| 1 | AAPL | price_jump | 0.85 | high | Unusual 5% price increase in 10 minutes | 2025-11-06 20:45:08.485812+00:00 | 2025-11-06 23:45:08.485859+00:00 |
| 2 | TSLA | volume_spike | 0.72 | medium | Trading volume 3x above average | 2025-11-06 17:45:08.485815+00:00 | 2025-11-06 23:45:08.488671+00:00 |
| 3 | BTC | volatility | 0.91 | high | Extreme volatility detected | 2025-11-06 22:45:08.485816+00:00 | 2025-11-06 23:45:08.489038+00:00 |
| 4 | NVDA | price_drop | 0.68 | medium | Significant price drop detected | 2025-11-06 21:45:08.485817+00:00 | 2025-11-06 23:45:08.489613+00:00 |
| 5 | AAPL | price_jump | 0.85 | high | Unusual 5% price increase in 10 minutes | 2025-11-06 20:45:37.193557+00:00 | 2025-11-06 23:45:37.193625+00:00 |

---

## Table: `assets` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('assets_id_seq'::regclass) | N/A |
| `ticker` | character varying | No | None | 20 |
| `name` | text | Yes | None | N/A |
| `asset_type` | character varying | Yes | None | 25 |
| `exchange` | character varying | Yes | None | 50 |
| `sector` | character varying | Yes | None | 50 |
| `country` | character varying | Yes | None | 50 |
| `added_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 163

### Sample Data

| id | ticker | name | asset_type | exchange | sector | country | added_at |
|-----|--------|------|------------|----------|--------|---------|----------|
| 4 | GOOGL | Alphabet Inc. | stock | NASDAQ | Technology | US | 2025-11-06 21:52:03.394158+00:00 |
| 5 | AMZN | Amazon.com Inc. | stock | NASDAQ | Technology | US | 2025-11-06 21:52:03.394338+00:00 |
| 6 | NVDA | NVIDIA Corporation | stock | NASDAQ | Technology | US | 2025-11-06 21:52:03.394509+00:00 |
| 9 | BTC | Bitcoin | crypto | CRYPTO | Cryptocurrency | Global | 2025-11-06 21:52:03.394926+00:00 |
| 10 | ETH | Ethereum | crypto | CRYPTO | Cryptocurrency | Global | 2025-11-06 21:52:03.395052+00:00 |

---

## Table: `chroma_embeddings` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('chroma_embeddings_id_seq'::regclass) | N/A |
| `collection_name` | character varying | No | None | 100 |
| `document_id` | character varying | No | None | 100 |
| `ticker` | character varying | Yes | None | 20 |
| `endpoint` | character varying | Yes | None | 50 |
| `timestamp` | timestamp with time zone | Yes | None | N/A |
| `chunk_index` | integer | Yes | 0 | N/A |
| `embedding_model` | character varying | Yes | None | 100 |
| `text_content` | text | Yes | None | N/A |
| `metadata` | jsonb | Yes | None | N/A |
| `ingestion_session_id` | character varying | Yes | None | 100 |
| `created_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `commodities_prices` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('commodities_prices_id_seq'::regclass) | N/A |
| `commodity` | character varying | No | None | 50 |
| `timestamp` | timestamp without time zone | No | None | N/A |
| `price` | double precision | No | None | N/A |
| `unit` | character varying | Yes | None | 20 |
| `interval` | character varying | Yes | 'daily'::character varying | 20 |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 30 |
| `updated_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `company_overviews` (VIEW)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `ticker` | character varying | Yes | None | 20 |
| `company_name` | text | Yes | None | N/A |
| `sector` | text | Yes | None | N/A |
| `industry` | text | Yes | None | N/A |
| `market_cap` | text | Yes | None | N/A |
| `pe_ratio` | text | Yes | None | N/A |
| `eps` | text | Yes | None | N/A |
| `revenue_ttm` | text | Yes | None | N/A |
| `profit_margin` | text | Yes | None | N/A |
| `country` | text | Yes | None | N/A |
| `exchange` | text | Yes | None | N/A |
| `updated_at` | timestamp without time zone | Yes | None | N/A |

**Total Records:** 0

*No data available*

---

## Table: `crypto_prices` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('crypto_prices_id_seq'::regclass) | N/A |
| `symbol` | character varying | No | None | 20 |
| `timestamp` | timestamp without time zone | No | None | N/A |
| `open` | double precision | Yes | None | N/A |
| `high` | double precision | Yes | None | N/A |
| `low` | double precision | Yes | None | N/A |
| `close` | double precision | Yes | None | N/A |
| `volume` | double precision | Yes | None | N/A |
| `market_cap` | double precision | Yes | None | N/A |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 30 |
| `updated_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `dividends_data` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('dividends_data_id_seq'::regclass) | N/A |
| `ticker` | character varying | No | None | 20 |
| `ex_date` | date | No | None | N/A |
| `payment_date` | date | Yes | None | N/A |
| `record_date` | date | Yes | None | N/A |
| `declared_date` | date | Yes | None | N/A |
| `amount` | double precision | No | None | N/A |
| `adjusted_amount` | double precision | Yes | None | N/A |
| `currency` | character varying | Yes | 'USD'::character varying | 3 |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 30 |
| `updated_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `earnings_calendar` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('earnings_calendar_id_seq'::regclass) | N/A |
| `ticker` | character varying | No | None | 20 |
| `company_name` | text | Yes | None | N/A |
| `report_date` | date | No | None | N/A |
| `fiscal_date_ending` | date | Yes | None | N/A |
| `estimate` | double precision | Yes | None | N/A |
| `currency` | character varying | Yes | 'USD'::character varying | 3 |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 30 |
| `updated_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `earnings_data` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('earnings_data_id_seq'::regclass) | N/A |
| `ticker` | character varying | No | None | 20 |
| `fiscal_date_ending` | date | No | None | N/A |
| `reported_eps` | double precision | Yes | None | N/A |
| `estimated_eps` | double precision | Yes | None | N/A |
| `surprise` | double precision | Yes | None | N/A |
| `surprise_percentage` | double precision | Yes | None | N/A |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 30 |
| `updated_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `economic_indicators` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('economic_indicators_id_seq'::regclass) | N/A |
| `indicator` | character varying | No | None | 50 |
| `date` | date | No | None | N/A |
| `value` | double precision | No | None | N/A |
| `unit` | character varying | Yes | None | 20 |
| `frequency` | character varying | Yes | None | 20 |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 30 |
| `updated_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `economic_indicators_summary` (VIEW)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `indicator` | character varying | Yes | None | 50 |
| `latest_date` | date | Yes | None | N/A |
| `latest_value` | double precision | Yes | None | N/A |
| `unit` | character varying | Yes | None | 20 |
| `frequency` | character varying | Yes | None | 20 |

**Total Records:** 0

*No data available*

---

## Table: `forecasts` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('forecasts_id_seq'::regclass) | N/A |
| `ticker` | character varying | Yes | None | 20 |
| `forecast_window` | character varying | Yes | None | 20 |
| `predicted_impact` | character varying | Yes | None | 30 |
| `confidence` | double precision | Yes | None | N/A |
| `reason` | text | Yes | None | N/A |
| `created_at` | timestamp with time zone | Yes | now() | N/A |
| `expires_at` | timestamp with time zone | Yes | None | N/A |

**Total Records:** 0

*No data available*

---

## Table: `forex_prices` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('forex_prices_id_seq'::regclass) | N/A |
| `pair` | character varying | No | None | 10 |
| `timestamp` | timestamp without time zone | No | None | N/A |
| `open` | double precision | Yes | None | N/A |
| `high` | double precision | Yes | None | N/A |
| `low` | double precision | Yes | None | N/A |
| `close` | double precision | Yes | None | N/A |
| `volume` | bigint | Yes | None | N/A |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 30 |
| `updated_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `fundamental_data` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('fundamental_data_id_seq'::regclass) | N/A |
| `ticker` | character varying | No | None | 20 |
| `data_type` | character varying | No | None | 50 |
| `data` | jsonb | No | None | N/A |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 30 |
| `updated_at` | timestamp without time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `infra_incidents` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('infra_incidents_id_seq1'::regclass) | N/A |
| `ticker` | character varying | No | None | 20 |
| `description` | text | No | None | N/A |
| `severity` | character varying | Yes | None | 20 |
| `status` | character varying | Yes | 'active'::character varying | 20 |
| `occurred_at` | timestamp with time zone | No | None | N/A |
| `resolved_at` | timestamp with time zone | Yes | None | N/A |

**Total Records:** 3

### Sample Data

| id | ticker | description | severity | status | occurred_at | resolved_at |
|-----|--------|-------------|----------|--------|-------------|-------------|
| 1 | NVDA | API outage in data provider | high | active | 2025-11-10 03:02:54.586124+00:00 | NULL |
| 2 | MSFT | Trading system latency spike | medium | active | 2025-11-10 04:02:54.586124+00:00 | NULL |
| 3 | AAPL | Market data feed interruption | high | resolved | 2025-11-09 23:02:54.586124+00:00 | NULL |

---

## Table: `infra_incidents_old` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('infra_incidents_id_seq'::regclass) | N/A |
| `platform` | character varying | Yes | None | 50 |
| `incident_type` | character varying | Yes | None | 50 |
| `description` | text | Yes | None | N/A |
| `severity` | character varying | Yes | None | 10 |
| `started_at` | timestamp with time zone | Yes | None | N/A |
| `resolved_at` | timestamp with time zone | Yes | None | N/A |
| `source` | character varying | Yes | None | 30 |

**Total Records:** 56

### Sample Data

| id | platform | incident_type | description | severity | started_at | resolved_at | source |
|-----|----------|---------------|-------------|----------|------------|-------------|--------|
| 1 | coinbase | status_check | Status: unknown. Active incidents: 0 | low | 2025-11-06 21:51:19.943373+00:00 | 2025-11-06 21:51:19.943376+00:00 | coinbase_status_api |
| 2 | binance | api_error | Failed to fetch status: 403 Client Error: Forbi... | medium | 2025-11-06 21:51:20.572736+00:00 | NULL | binance_status_api |
| 3 | solana | slow_slots | Solana TPS: 3040.0, Slot time: 60s - Slow slot ... | medium | 2025-11-06 21:51:21.267389+00:00 | NULL | solana_rpc |
| 4 | general_infrastructure | health_check | General infrastructure monitoring - no issues d... | low | 2025-11-06 21:51:21.267885+00:00 | 2025-11-06 21:51:21.267889+00:00 | infrastructure_monitor |
| 5 | coinbase | status_check | Status: unknown. Active incidents: 0 | low | 2025-11-06 21:52:29.626184+00:00 | 2025-11-06 21:52:29.626188+00:00 | coinbase_status_api |

---

## Table: `infrastructure_status` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('infrastructure_status_id_seq'::regclass) | N/A |
| `ticker` | character varying | Yes | None | 20 |
| `service_name` | character varying | Yes | None | 100 |
| `status` | character varying | Yes | None | 50 |
| `description` | text | Yes | None | N/A |
| `source` | character varying | Yes | None | 50 |
| `severity` | character varying | Yes | None | 20 |
| `timestamp` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 462

### Sample Data

| id | ticker | service_name | status | description | source | severity | timestamp |
|-----|--------|--------------|--------|-------------|--------|----------|-----------|
| 1 | SYSTEM | market_data_api | healthy | All market data feeds operational | internal | low | 2025-11-06 23:45:37.196229+00:00 |
| 2 | SYSTEM | news_api | healthy | News collection running normally | internal | low | 2025-11-06 23:45:37.198600+00:00 |
| 3 | SYSTEM | database | healthy | PostgreSQL performance optimal | internal | low | 2025-11-06 23:45:37.199071+00:00 |
| 4 | SYSTEM | vector_store | warning | ChromaDB latency slightly elevated | internal | medium | 2025-11-06 23:45:37.199526+00:00 |
| 5 | SYSTEM | coinbase_exchange | healthy | Exchange operations normal | internal | healthy | 2025-10-31 00:22:19.933334+00:00 |

---

## Table: `ingestion_progress` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `ticker` | character varying | No | None | 20 |
| `last_completed_endpoint` | character varying | Yes | None | 50 |
| `epoch` | integer | Yes | None | N/A |
| `total_endpoints_completed` | integer | Yes | 0 | N/A |
| `total_records_inserted` | integer | Yes | 0 | N/A |
| `ingestion_session_id` | character varying | Yes | None | 100 |
| `updated_at` | timestamp with time zone | Yes | now() | N/A |
| `created_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 2

### Sample Data

| ticker | last_completed_endpoint | epoch | total_endpoints_completed | total_records_inserted | ingestion_session_id | updated_at | created_at |
|--------|-------------------------|-------|---------------------------|------------------------|----------------------|------------|------------|
| NVDA | HT_PHASOR | 1 | 84 | 65158 | alpha_ingestion_20251108_212207 | 2025-11-08 15:58:31.685000+00:00 | 2025-11-07 21:03:32.763431+00:00 |
| MSFT | INSIDER_TRANSACTIONS | 2 | 22 | 254 | alpha_ingestion_20251109_142442 | 2025-11-09 08:54:59.550679+00:00 | 2025-11-08 15:58:34.573913+00:00 |

---

## Table: `ingestion_sessions` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `session_id` | character varying | No | None | 100 |
| `start_time` | timestamp with time zone | Yes | now() | N/A |
| `end_time` | timestamp with time zone | Yes | None | N/A |
| `status` | character varying | Yes | 'running'::character varying | 20 |
| `total_tickers` | integer | Yes | None | N/A |
| `completed_tickers` | integer | Yes | 0 | N/A |
| `total_records` | integer | Yes | 0 | N/A |
| `total_api_calls` | integer | Yes | 0 | N/A |
| `total_errors` | integer | Yes | 0 | N/A |
| `metadata` | jsonb | Yes | None | N/A |

**Total Records:** 17

### Sample Data

| session_id | start_time | end_time | status | total_tickers | completed_tickers | total_records | total_api_calls | total_errors | metadata |
|------------|------------|----------|--------|---------------|-------------------|---------------|-----------------|--------------|----------|
| alpha_ingestion_20251107_210331 | 2025-11-07 21:03:31.942415+00:00 | 2025-11-07 21:05:40.315612+00:00 | failed | 200 | 0 | 0 | 0 | 0 | {"error_info": {"failed_at": "2025-11-07T21:05:... |
| alpha_ingestion_20251107_214540 | 2025-11-07 21:45:40.379583+00:00 | 2025-11-07 21:46:54.876049+00:00 | failed | 200 | 0 | 0 | 0 | 0 | {"error_info": {"failed_at": "2025-11-07T21:46:... |
| alpha_ingestion_20251107_220729 | 2025-11-07 22:07:29.649805+00:00 | 2025-11-07 22:08:59.552378+00:00 | completed | 200 | 1 | 0 | 0 | 58 | {"system_info": {"platform": "macOS Darwin 25.0... |
| alpha_ingestion_20251108_100121 | 2025-11-08 10:01:21.262393+00:00 | NULL | running | 200 | 0 | 0 | 0 | 0 | {"system_info": {"platform": "macOS Darwin 25.0... |
| alpha_ingestion_20251108_111853 | 2025-11-08 11:18:53.860480+00:00 | NULL | running | 200 | 0 | 0 | 0 | 0 | {"system_info": {"platform": "macOS Darwin 25.0... |

---

## Table: `insider_transactions` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('insider_transactions_id_seq'::regclass) | N/A |
| `ticker` | character varying | No | None | 20 |
| `insider_name` | text | Yes | None | N/A |
| `transaction_date` | date | Yes | None | N/A |
| `transaction_type` | character varying | Yes | None | 50 |
| `shares_traded` | bigint | Yes | None | N/A |
| `price_per_share` | double precision | Yes | None | N/A |
| `total_value` | double precision | Yes | None | N/A |
| `shares_owned_after` | bigint | Yes | None | N/A |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 30 |
| `updated_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `latest_commodities_prices` (VIEW)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `commodity` | character varying | Yes | None | 50 |
| `timestamp` | timestamp without time zone | Yes | None | N/A |
| `price` | double precision | Yes | None | N/A |
| `unit` | character varying | Yes | None | 20 |

**Total Records:** 0

*No data available*

---

## Table: `latest_company_overview` (VIEW)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `ticker` | character varying | Yes | None | 20 |
| `company_name` | text | Yes | None | N/A |
| `market_cap` | numeric | Yes | None | N/A |
| `pe_ratio` | numeric | Yes | None | N/A |
| `dividend_yield` | numeric | Yes | None | N/A |
| `fiscal_date_ending` | date | Yes | None | N/A |
| `ingestion_time` | timestamp with time zone | Yes | None | N/A |

**Total Records:** 0

*No data available*

---

## Table: `latest_crypto_prices` (VIEW)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `symbol` | character varying | Yes | None | 20 |
| `timestamp` | timestamp without time zone | Yes | None | N/A |
| `price` | double precision | Yes | None | N/A |
| `volume` | double precision | Yes | None | N/A |
| `market_cap` | double precision | Yes | None | N/A |
| `open` | double precision | Yes | None | N/A |
| `high` | double precision | Yes | None | N/A |
| `low` | double precision | Yes | None | N/A |

**Total Records:** 0

*No data available*

---

## Table: `latest_forex_rates` (VIEW)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `pair` | character varying | Yes | None | 10 |
| `timestamp` | timestamp without time zone | Yes | None | N/A |
| `rate` | double precision | Yes | None | N/A |
| `open` | double precision | Yes | None | N/A |
| `high` | double precision | Yes | None | N/A |
| `low` | double precision | Yes | None | N/A |
| `volume` | bigint | Yes | None | N/A |

**Total Records:** 0

*No data available*

---

## Table: `latest_market_data` (VIEW)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `ticker` | character varying | Yes | None | 20 |
| `timestamp` | timestamp with time zone | Yes | None | N/A |
| `open_price` | numeric | Yes | None | N/A |
| `high_price` | numeric | Yes | None | N/A |
| `low_price` | numeric | Yes | None | N/A |
| `close_price` | numeric | Yes | None | N/A |
| `volume` | bigint | Yes | None | N/A |
| `quality_flag` | character varying | Yes | None | 20 |

**Total Records:** 0

*No data available*

---

## Table: `listing_status` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('listing_status_id_seq'::regclass) | N/A |
| `ticker` | character varying | No | None | 20 |
| `company_name` | text | Yes | None | N/A |
| `exchange` | character varying | Yes | None | 50 |
| `asset_type` | character varying | Yes | None | 50 |
| `ipo_date` | date | Yes | None | N/A |
| `delisting_date` | date | Yes | None | N/A |
| `status` | character varying | Yes | 'active'::character varying | 20 |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 30 |
| `updated_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `market_movers` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('market_movers_id_seq'::regclass) | N/A |
| `ticker` | character varying | No | None | 20 |
| `company_name` | text | Yes | None | N/A |
| `price` | double precision | Yes | None | N/A |
| `change_amount` | double precision | Yes | None | N/A |
| `change_percentage` | character varying | Yes | None | 10 |
| `volume` | bigint | Yes | None | N/A |
| `mover_type` | character varying | Yes | None | 10 |
| `date` | date | No | None | N/A |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 30 |
| `updated_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `market_prices` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('market_prices_id_seq'::regclass) | N/A |
| `ticker` | character varying | Yes | None | 20 |
| `timestamp` | timestamp without time zone | No | None | N/A |
| `open` | double precision | Yes | None | N/A |
| `high` | double precision | Yes | None | N/A |
| `low` | double precision | Yes | None | N/A |
| `close` | double precision | Yes | None | N/A |
| `volume` | bigint | Yes | None | N/A |
| `bid_ask_spread` | double precision | Yes | None | N/A |
| `source` | character varying | Yes | None | 20 |

**Total Records:** 2,285

### Sample Data

| id | ticker | timestamp | open | high | low | close | volume | bid_ask_spread | source |
|-----|--------|-----------|------|------|-----|-------|--------|----------------|--------|
| 1888 | AAPL | 2025-11-07 00:28:36.622640 | 496.5341686271317 | 502.7724615675795 | 487.2637871666244 | 494.7012785879316 | 4058209 | NULL | synthetic |
| 1889 | AAPL | 2025-11-06 20:28:36.692925 | 489.04508647037255 | 495.6177414905073 | 486.06237103264954 | 487.84391880369026 | 2534066 | NULL | synthetic |
| 1890 | AAPL | 2025-11-06 16:28:36.693562 | 493.0250068016367 | 506.4858931049138 | 493.4552945523263 | 497.8324376874387 | 1118148 | NULL | synthetic |
| 1891 | AAPL | 2025-11-06 12:28:36.694062 | 490.0308400737355 | 500.2331549789954 | 483.41272669682803 | 492.8024481109806 | 4513222 | NULL | synthetic |
| 1892 | AAPL | 2025-11-06 08:28:36.694542 | 491.9139656272491 | 496.4241220745883 | 489.7971595372333 | 493.5928864963406 | 3444062 | NULL | synthetic |

---

## Table: `news_headlines` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('news_headlines_id_seq'::regclass) | N/A |
| `ticker` | character varying | Yes | None | 20 |
| `headline` | text | Yes | None | N/A |
| `url` | text | Yes | None | N/A |
| `source` | character varying | Yes | None | 30 |
| `published_at` | timestamp with time zone | Yes | None | N/A |
| `inserted_at` | timestamp with time zone | Yes | now() | N/A |
| `category` | character varying | Yes | None | 50 |
| `topics` | ARRAY | Yes | None | N/A |
| `relevance_score` | double precision | Yes | None | N/A |
| `overall_sentiment_score` | double precision | Yes | None | N/A |
| `overall_sentiment_label` | character varying | Yes | None | 20 |

**Total Records:** 737

### Sample Data

| id | ticker | headline | url | source | published_at | inserted_at | category | topics | relevance_score | overall_sentiment_score | overall_sentiment_label |
|-----|--------|----------|-----|--------|--------------|-------------|----------|--------|-----------------|-------------------------|-------------------------|
| 1 |  | Schwab muscles its way into private markets, bu... | https://www.marketwatch.com/story/schwab-muscle... | finnhub_general | 2025-11-06 21:01:00+00:00 | 2025-11-06 21:51:16.652067+00:00 | NULL | NULL | NULL | NULL | NULL |
| 2 |  | High income is ‘central’ to aging, this new stu... | https://www.marketwatch.com/story/high-income-i... | finnhub_general | 2025-11-06 20:31:00+00:00 | 2025-11-06 21:51:16.657610+00:00 | NULL | NULL | NULL | NULL | NULL |
| 3 |  | Judge tosses Boeing criminal case over 737 Max ... | https://www.cnbc.com/2025/11/06/boeing-criminal... | finnhub_general | 2025-11-06 20:28:08+00:00 | 2025-11-06 21:51:16.658031+00:00 | NULL | NULL | NULL | NULL | NULL |
| 4 |  | Global shipping plays Maersk and DHL sail unruf... | https://www.marketwatch.com/story/global-shippi... | finnhub_general | 2025-11-06 19:59:00+00:00 | 2025-11-06 21:51:16.658400+00:00 | NULL | NULL | NULL | NULL | NULL |
| 5 |  | Younger consumers are eating less Chipotle and ... | https://www.cnbc.com/2025/11/06/tapestry-tpr-q1... | finnhub_general | 2025-11-06 19:57:41+00:00 | 2025-11-06 21:51:16.658828+00:00 | NULL | NULL | NULL | NULL | NULL |

---

## Table: `news_sentiment` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('news_sentiment_id_seq'::regclass) | N/A |
| `headline_id` | integer | Yes | None | N/A |
| `sentiment_score` | double precision | Yes | None | N/A |
| `sentiment_label` | character varying | Yes | None | 10 |
| `confidence` | double precision | Yes | None | N/A |
| `model_version` | character varying | Yes | None | 20 |
| `timestamp` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 742

### Sample Data

| id | headline_id | sentiment_score | sentiment_label | confidence | model_version | timestamp |
|-----|-------------|-----------------|-----------------|------------|---------------|-----------|
| 1 | 1 | 0.8 | NULL | NULL | NULL | 2025-11-06 21:45:08.477900+00:00 |
| 2 | 2 | 0.6 | NULL | NULL | NULL | 2025-11-06 18:45:08.477908+00:00 |
| 3 | 3 | 0.7 | NULL | NULL | NULL | 2025-11-06 20:45:08.477909+00:00 |
| 4 | 4 | 0.9 | NULL | NULL | NULL | 2025-11-06 22:45:08.477910+00:00 |
| 5 | 5 | 0.5 | NULL | NULL | NULL | 2025-11-06 19:45:08.477912+00:00 |

---

## Table: `options_data` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('options_data_id_seq'::regclass) | N/A |
| `ticker` | character varying | No | None | 20 |
| `option_type` | character varying | Yes | None | 4 |
| `expiration_date` | date | No | None | N/A |
| `strike_price` | double precision | No | None | N/A |
| `timestamp` | timestamp with time zone | No | None | N/A |
| `bid` | double precision | Yes | None | N/A |
| `ask` | double precision | Yes | None | N/A |
| `last_price` | double precision | Yes | None | N/A |
| `volume` | integer | Yes | None | N/A |
| `open_interest` | integer | Yes | None | N/A |
| `implied_volatility` | double precision | Yes | None | N/A |
| `delta` | double precision | Yes | None | N/A |
| `gamma` | double precision | Yes | None | N/A |
| `theta` | double precision | Yes | None | N/A |
| `vega` | double precision | Yes | None | N/A |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 30 |
| `updated_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `price_gaps` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('price_gaps_id_seq'::regclass) | N/A |
| `ticker` | character varying | Yes | None | 20 |
| `date` | date | Yes | None | N/A |
| `previous_close` | double precision | Yes | None | N/A |
| `next_open` | double precision | Yes | None | N/A |
| `gap_percent` | double precision | Yes | None | N/A |
| `direction` | character varying | Yes | None | 10 |
| `reason` | text | Yes | None | N/A |
| `inserted_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `query_performance_log` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('query_performance_log_id_seq'::regclass) | N/A |
| `query_name` | character varying | Yes | None | 100 |
| `execution_time_ms` | numeric | Yes | None | N/A |
| `rows_affected` | bigint | Yes | None | N/A |
| `timestamp` | timestamp without time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `recent_market_activity` (VIEW)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `ticker` | character varying | Yes | None | 20 |
| `timestamp` | timestamp without time zone | Yes | None | N/A |
| `close` | double precision | Yes | None | N/A |
| `volume` | bigint | Yes | None | N/A |
| `asset_type` | character varying | Yes | None | 25 |
| `exchange` | character varying | Yes | None | 50 |

**Total Records:** 0

*No data available*

---

## Table: `regulatory_events` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('regulatory_events_id_seq'::regclass) | N/A |
| `ticker` | character varying | Yes | None | 20 |
| `title` | text | Yes | None | N/A |
| `body` | text | Yes | None | N/A |
| `source` | character varying | Yes | None | 30 |
| `severity` | character varying | Yes | None | 10 |
| `event_type` | character varying | Yes | None | 30 |
| `published_at` | timestamp with time zone | Yes | None | N/A |
| `inserted_at` | timestamp with time zone | Yes | now() | N/A |
| `timestamp` | timestamp with time zone | Yes | None | N/A |

**Total Records:** 1,963

### Sample Data

| id | ticker | title | body | source | severity | event_type | published_at | inserted_at | timestamp |
|-----|--------|-------|------|--------|----------|------------|--------------|-------------|-----------|
| 774 | INTC | Interest Rate Maintained by 0.69% | NULL | rbi | low | rate_decision | 2025-06-05 15:28:39.592209+00:00 | 2025-11-07 00:28:39.592233+00:00 | 2025-06-05 15:28:39.592209+00:00 |
| 1 | NULL | Federal Reserve Board issues enforcement action... | Federal Reserve Board issues enforcement action... | fed | low | press_release | 2025-11-06 16:00:00+00:00 | 2025-11-06 21:51:19.030326+00:00 | 2025-11-06 16:00:00+00:00 |
| 2 | NULL | Federal Reserve Board finalizes changes to its ... | Federal Reserve Board finalizes changes to its ... | fed | low | press_release | 2025-11-05 22:00:00+00:00 | 2025-11-06 21:51:19.034760+00:00 | 2025-11-05 22:00:00+00:00 |
| 3 | NULL | Federal Reserve Board announces termination of ... | Federal Reserve Board announces termination of ... | fed | low | press_release | 2025-11-04 16:00:00+00:00 | 2025-11-06 21:51:19.035544+00:00 | 2025-11-04 16:00:00+00:00 |
| 4 | NULL | Federal Reserve Board announces approval of app... | Federal Reserve Board announces approval of app... | fed | low | press_release | 2025-10-31 20:45:00+00:00 | 2025-11-06 21:51:19.036119+00:00 | 2025-10-31 20:45:00+00:00 |

---

## Table: `splits_data` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('splits_data_id_seq'::regclass) | N/A |
| `ticker` | character varying | No | None | 20 |
| `split_date` | date | No | None | N/A |
| `split_factor` | character varying | No | None | 20 |
| `split_ratio` | double precision | No | None | N/A |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 30 |
| `updated_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `technical_indicators` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('technical_indicators_id_seq'::regclass) | N/A |
| `ticker` | character varying | No | None | 20 |
| `indicator` | character varying | No | None | 50 |
| `timestamp` | timestamp with time zone | No | None | N/A |
| `value` | double precision | Yes | None | N/A |
| `additional_data` | jsonb | Yes | None | N/A |
| `time_period` | integer | Yes | None | N/A |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 30 |
| `updated_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `ticker_sentiment` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `id` | integer | No | nextval('ticker_sentiment_id_seq'::regclass) | N/A |
| `headline_id` | integer | Yes | None | N/A |
| `ticker` | character varying | No | None | 20 |
| `relevance_score` | double precision | Yes | None | N/A |
| `sentiment_score` | double precision | Yes | None | N/A |
| `sentiment_label` | character varying | Yes | None | 20 |
| `source` | character varying | Yes | 'alpha_vantage'::character varying | 30 |
| `updated_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 0

*No data available*

---

## Table: `vector_sync_state` (BASE TABLE)

### Schema

| Column | Type | Nullable | Default | Max Length |
|--------|------|----------|---------|------------|
| `table_name` | character varying | No | None | 100 |
| `last_synced_at` | timestamp with time zone | Yes | None | N/A |
| `records_synced` | bigint | Yes | 0 | N/A |
| `last_chunk_id` | character varying | Yes | None | 255 |
| `created_at` | timestamp with time zone | Yes | now() | N/A |
| `updated_at` | timestamp with time zone | Yes | now() | N/A |

**Total Records:** 1

### Sample Data

| table_name | last_synced_at | records_synced | last_chunk_id | created_at | updated_at |
|------------|----------------|----------------|---------------|------------|------------|
| alpha_vantage_data | 2000-05-09 00:00:00+00:00 | 5000 | NULL | 2025-11-11 06:38:00.269934+00:00 | 2025-11-11 06:38:00.269934+00:00 |

---

