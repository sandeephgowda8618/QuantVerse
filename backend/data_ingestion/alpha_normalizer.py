"""
Alpha Vantage Data Normalizer - Data Processing and Enrichment
Transforms raw API responses into structured, normalized data
Part of the 200-Batch, Epoch-Based Ingestion System
"""

import logging
from datetime import datetime, timezone
import pytz
from dateutil import parser as date_parser
from typing import Dict, List, Optional, Any, Tuple
import json
import pandas as pd
import numpy as np
from decimal import Decimal

from ..config.settings import settings

logger = logging.getLogger(__name__)

def to_aware(dt):
    """
    Convert datetime to timezone-aware UTC if it's naive.
    This fixes the PostgreSQL timezone-aware vs naive datetime mismatch.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=pytz.UTC)
    return dt

class AlphaNormalizer:
    """
    Normalizes and enriches Alpha Vantage API responses
    Handles all endpoint types with appropriate transformations
    """
    
    def __init__(self):
        # Keep track of processing statistics
        self.processed_records = 0
        self.processed_endpoints = 0
        self.normalization_errors = 0
        
        # Data quality flags
        self.quality_flags = {
            'success': 'Successful normalization',
            'partial': 'Partial data available',
            'empty': 'No data returned',
            'error': 'Normalization error',
            'invalid_format': 'Invalid data format'
        }
    
    def normalize_endpoint_data(
        self, 
        endpoint: str, 
        raw_data: Dict, 
        ticker: str, 
        metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Main normalization entry point for any endpoint
        
        Returns:
            List of normalized records ready for database insertion
        """
        if not raw_data or not isinstance(raw_data, dict):
            logger.warning(f"⚠️ Invalid data format for {endpoint}")
            return []
        
        try:
            # Route to appropriate normalizer based on endpoint type
            if endpoint in self._get_time_series_endpoints():
                return self._normalize_time_series(endpoint, raw_data, ticker, metadata)
            elif endpoint in self._get_fundamental_endpoints():
                return self._normalize_fundamental(endpoint, raw_data, ticker, metadata)
            elif endpoint in self._get_intelligence_endpoints():
                return self._normalize_intelligence(endpoint, raw_data, ticker, metadata)
            elif endpoint in self._get_technical_endpoints():
                return self._normalize_technical(endpoint, raw_data, ticker, metadata)
            elif endpoint in self._get_economic_endpoints():
                return self._normalize_economic(endpoint, raw_data, ticker, metadata)
            elif endpoint in self._get_commodities_endpoints():
                return self._normalize_commodities(endpoint, raw_data, ticker, metadata)
            elif endpoint in self._get_forex_endpoints():
                return self._normalize_forex(endpoint, raw_data, ticker, metadata)
            elif endpoint in self._get_crypto_endpoints():
                return self._normalize_crypto(endpoint, raw_data, ticker, metadata)
            elif endpoint in self._get_options_endpoints():
                return self._normalize_options(endpoint, raw_data, ticker, metadata)
            else:
                # Generic normalization for unknown endpoints
                return self._normalize_generic(endpoint, raw_data, ticker, metadata)
                
        except Exception as e:
            logger.error(f"❌ Normalization error for {endpoint}: {str(e)}")
            self.normalization_errors += 1
            return self._create_error_record(endpoint, raw_data, ticker, str(e), metadata)
    
    def _get_time_series_endpoints(self) -> List[str]:
        """Get all time series endpoints"""
        return [
            "TIME_SERIES_INTRADAY", "TIME_SERIES_DAILY", "TIME_SERIES_DAILY_ADJUSTED",
            "TIME_SERIES_WEEKLY", "TIME_SERIES_WEEKLY_ADJUSTED", 
            "TIME_SERIES_MONTHLY", "TIME_SERIES_MONTHLY_ADJUSTED",
            "GLOBAL_QUOTE"
        ]
    
    def _get_fundamental_endpoints(self) -> List[str]:
        """Get all fundamental analysis endpoints"""
        return [
            "COMPANY_OVERVIEW", "INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW",
            "EARNINGS", "LISTING_STATUS", "IPO_CALENDAR", "EARNINGS_CALENDAR",
            "INSIDER_TRANSACTIONS"
        ]
    
    def _get_intelligence_endpoints(self) -> List[str]:
        """Get all market intelligence endpoints"""
        return [
            "NEWS_SENTIMENT", "TOP_GAINERS_LOSERS", "ANALYTICS_SENTIMENT",
            "ANALYTICS_FIXED_WINDOW"
        ]
    
    def _get_technical_endpoints(self) -> List[str]:
        """Get all technical indicator endpoints"""
        return [
            "SMA", "EMA", "WMA", "DEMA", "TEMA", "TRIMA", "KAMA", "MAMA", "T3",
            "MACD", "MACDEXT", "STOCH", "STOCHF", "RSI", "STOCHRSI", "WILLR",
            "ADX", "ADXR", "APO", "PPO", "MOM", "BOP", "CCI", "CMO", "ROC",
            "ROCR", "AROON", "AROONOSC", "MFI", "TRIX", "ULTOSC", "DX",
            "MINUS_DI", "PLUS_DI", "MINUS_DM", "PLUS_DM", "BBANDS",
            "MIDPOINT", "MIDPRICE", "SAR", "TRANGE", "ATR", "NATR",
            "AD", "ADOSC", "OBV", "HT_TRENDLINE", "HT_SINE", "HT_TRENDMODE",
            "HT_DCPERIOD", "HT_DCPHASE", "HT_PHASOR"
        ]
    
    def _get_economic_endpoints(self) -> List[str]:
        """Get all economic indicator endpoints"""
        return [
            "REAL_GDP", "REAL_GDP_PER_CAPITA", "TREASURY_YIELD",
            "FEDERAL_FUNDS_RATE", "CPI", "INFLATION", "RETAIL_SALES",
            "DURABLES", "UNEMPLOYMENT", "NONFARM_PAYROLL"
        ]
    
    def _get_commodities_endpoints(self) -> List[str]:
        """Get all commodities endpoints"""
        return [
            "WTI", "BRENT", "NATURAL_GAS", "COPPER", "ALUMINUM",
            "WHEAT", "CORN", "COTTON", "SUGAR", "COFFEE"
        ]
    
    def _get_forex_endpoints(self) -> List[str]:
        """Get all forex endpoints"""
        return [
            "FX_INTRADAY", "FX_DAILY", "FX_WEEKLY", "FX_MONTHLY",
            "CURRENCY_EXCHANGE_RATE"
        ]
    
    def _get_crypto_endpoints(self) -> List[str]:
        """Get all cryptocurrency endpoints"""
        return [
            "CRYPTO_INTRADAY", "DIGITAL_CURRENCY_DAILY",
            "DIGITAL_CURRENCY_WEEKLY", "DIGITAL_CURRENCY_MONTHLY"
        ]
    
    def _get_options_endpoints(self) -> List[str]:
        """Get all options endpoints"""
        return ["HISTORICAL_OPTIONS", "REALTIME_OPTIONS"]
    
    def _normalize_time_series(self, endpoint: str, data: Dict, ticker: str, metadata: Dict) -> List[Dict]:
        """Normalize time series data (OHLCV)"""
        records = []
        
        try:
            # Handle different time series response formats
            time_series_key = self._find_time_series_key(data)
            if not time_series_key or time_series_key not in data:
                logger.warning(f"⚠️ No time series data found in {endpoint} response")
                return self._create_empty_record(endpoint, data, ticker, metadata)
            
            time_series_data = data[time_series_key]
            meta_data = data.get("Meta Data", {})
            
            for timestamp_str, values in time_series_data.items():
                try:
                    # Parse timestamp
                    timestamp = self._parse_timestamp(timestamp_str, endpoint)
                    
                    # Extract OHLCV values
                    parsed_values = self._extract_ohlcv_values(values, endpoint)
                    
                    record = {
                        'ticker': ticker,
                        'endpoint': endpoint,
                        'timestamp': timestamp,
                        'raw_payload': data,
                        'parsed_values': {
                            **parsed_values,
                            'meta_data': meta_data,
                            'data_point_timestamp': timestamp_str
                        },
                        'quality_flag': 'success',
                        'data_type': 'time_series',
                        'interval_period': meta_data.get("4. Interval", "unknown"),
                        'metadata': {
                            **(metadata or {}),
                            'symbol': meta_data.get("2. Symbol", ticker),
                            'last_refreshed': meta_data.get("3. Last Refreshed"),
                            'output_size': meta_data.get("4. Output Size"),
                            'time_zone': meta_data.get("5. Time Zone", "US/Eastern")
                        }
                    }
                    records.append(record)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing time series point {timestamp_str}: {str(e)}")
                    continue
            
            self.processed_records += len(records)
            logger.debug(f"✅ Normalized {len(records)} time series records for {endpoint}")
            
        except Exception as e:
            logger.error(f"❌ Error normalizing time series {endpoint}: {str(e)}")
            return self._create_error_record(endpoint, data, ticker, str(e), metadata)
        
        return records
    
    def _normalize_fundamental(self, endpoint: str, data: Dict, ticker: str, metadata: Dict) -> List[Dict]:
        """Normalize fundamental data"""
        records = []
        
        try:
            if endpoint == "COMPANY_OVERVIEW":
                # Single record with company overview data
                record = {
                    'ticker': ticker,
                    'endpoint': endpoint,
                    'timestamp': self._make_timezone_aware(datetime.now()),
                    'raw_payload': data,
                    'parsed_values': {
                        'market_cap': self._safe_float(data.get("MarketCapitalization")),
                        'pe_ratio': self._safe_float(data.get("PERatio")),
                        'peg_ratio': self._safe_float(data.get("PEGRatio")),
                        'book_value': self._safe_float(data.get("BookValue")),
                        'dividend_yield': self._safe_float(data.get("DividendYield")),
                        'eps': self._safe_float(data.get("EPS")),
                        'revenue_ttm': self._safe_float(data.get("RevenueTTM")),
                        'gross_profit_ttm': self._safe_float(data.get("GrossProfitTTM")),
                        'sector': data.get("Sector"),
                        'industry': data.get("Industry"),
                        'country': data.get("Country"),
                        'exchange': data.get("Exchange")
                    },
                    'quality_flag': 'success' if data.get("Symbol") else 'partial',
                    'data_type': 'fundamental_overview',
                    'metadata': {
                        **(metadata or {}),
                        'name': data.get("Name"),
                        'description': data.get("Description"),
                        'fiscal_year_end': data.get("FiscalYearEnd"),
                        'latest_quarter': data.get("LatestQuarter")
                    }
                }
                records.append(record)
                
            elif endpoint in ["INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW"]:
                # Multiple quarterly/annual records
                records = self._normalize_financial_statements(endpoint, data, ticker, metadata)
                
            elif endpoint == "EARNINGS":
                records = self._normalize_earnings(data, ticker, metadata)
                
            elif endpoint in ["EARNINGS_CALENDAR", "IPO_CALENDAR"]:
                records = self._normalize_calendar_data(endpoint, data, ticker, metadata)
                
            else:
                # Generic fundamental data handling
                records = [self._create_generic_record(endpoint, data, ticker, metadata)]
            
            self.processed_records += len(records)
            logger.debug(f"✅ Normalized {len(records)} fundamental records for {endpoint}")
            
        except Exception as e:
            logger.error(f"❌ Error normalizing fundamental {endpoint}: {str(e)}")
            return self._create_error_record(endpoint, data, ticker, str(e), metadata)
        
        return records
    
    def _normalize_earnings(self, data: Dict, ticker: str, metadata: Dict) -> List[Dict]:
        """Normalize earnings data"""
        records = []
        
        try:
            # Handle annual earnings
            if 'annualEarnings' in data:
                for earning in data['annualEarnings']:
                    record = {
                        'ticker': ticker,
                        'endpoint': 'EARNINGS',
                        'timestamp': self._make_timezone_aware(datetime.now()),
                        'date': self._safe_date(earning.get('fiscalDateEnding')),
                        'raw_payload': earning,
                        'parsed_values': {
                            'reported_eps': self._safe_float(earning.get('reportedEPS')),
                            'estimated_eps': self._safe_float(earning.get('estimatedEPS')),
                            'surprise': self._safe_float(earning.get('surprise')),
                            'surprise_percentage': self._safe_float(earning.get('surprisePercentage')),
                            'fiscal_date_ending': earning.get('fiscalDateEnding')
                        },
                        'quality_flag': 'success',
                        'data_type': 'earnings_annual',
                        'metadata': metadata or {}
                    }
                    records.append(record)
            
            # Handle quarterly earnings
            if 'quarterlyEarnings' in data:
                for earning in data['quarterlyEarnings']:
                    record = {
                        'ticker': ticker,
                        'endpoint': 'EARNINGS',
                        'timestamp': self._make_timezone_aware(datetime.now()),
                        'date': self._safe_date(earning.get('fiscalDateEnding')),
                        'raw_payload': earning,
                        'parsed_values': {
                            'reported_eps': self._safe_float(earning.get('reportedEPS')),
                            'estimated_eps': self._safe_float(earning.get('estimatedEPS')),
                            'surprise': self._safe_float(earning.get('surprise')),
                            'surprise_percentage': self._safe_float(earning.get('surprisePercentage')),
                            'fiscal_date_ending': earning.get('fiscalDateEnding'),
                            'reported_date': earning.get('reportedDate')
                        },
                        'quality_flag': 'success',
                        'data_type': 'earnings_quarterly',
                        'metadata': metadata or {}
                    }
                    records.append(record)
                    
        except Exception as e:
            logger.error(f"❌ Error normalizing earnings data: {str(e)}")
            return self._create_error_record('EARNINGS', data, ticker, str(e), metadata)
        
        return records
    
    def _normalize_financial_statements(self, endpoint: str, data: Dict, ticker: str, metadata: Dict) -> List[Dict]:
        """Normalize financial statements (income, balance sheet, cash flow)"""
        records = []
        
        try:
            # Handle annual reports
            if 'annualReports' in data:
                for report in data['annualReports']:
                    record = {
                        'ticker': ticker,
                        'endpoint': endpoint,
                        'timestamp': self._make_timezone_aware(datetime.now()),
                        'date': self._safe_date(report.get('fiscalDateEnding')),
                        'raw_payload': report,
                        'parsed_values': self._extract_financial_values(endpoint, report),
                        'quality_flag': 'success',
                        'data_type': f'{endpoint.lower()}_annual',
                        'metadata': metadata or {}
                    }
                    records.append(record)
            
            # Handle quarterly reports  
            if 'quarterlyReports' in data:
                for report in data['quarterlyReports']:
                    record = {
                        'ticker': ticker,
                        'endpoint': endpoint,
                        'timestamp': self._make_timezone_aware(datetime.now()),
                        'date': self._safe_date(report.get('fiscalDateEnding')),
                        'raw_payload': report,
                        'parsed_values': self._extract_financial_values(endpoint, report),
                        'quality_flag': 'success',
                        'data_type': f'{endpoint.lower()}_quarterly',
                        'metadata': metadata or {}
                    }
                    records.append(record)
                    
        except Exception as e:
            logger.error(f"❌ Error normalizing {endpoint} data: {str(e)}")
            return self._create_error_record(endpoint, data, ticker, str(e), metadata)
        
        return records
    
    def _extract_financial_values(self, endpoint: str, report: Dict) -> Dict:
        """Extract key financial values based on statement type"""
        if endpoint == 'INCOME_STATEMENT':
            return {
                'total_revenue': self._safe_float(report.get('totalRevenue')),
                'cost_of_revenue': self._safe_float(report.get('costOfRevenue')),
                'gross_profit': self._safe_float(report.get('grossProfit')),
                'operating_income': self._safe_float(report.get('operatingIncome')),
                'net_income': self._safe_float(report.get('netIncome')),
                'eps': self._safe_float(report.get('reportedEPS')),
                'fiscal_date_ending': report.get('fiscalDateEnding')
            }
        elif endpoint == 'BALANCE_SHEET':
            return {
                'total_assets': self._safe_float(report.get('totalAssets')),
                'total_current_assets': self._safe_float(report.get('totalCurrentAssets')),
                'total_liabilities': self._safe_float(report.get('totalLiabilities')),
                'total_current_liabilities': self._safe_float(report.get('totalCurrentLiabilities')),
                'total_shareholder_equity': self._safe_float(report.get('totalShareholderEquity')),
                'retained_earnings': self._safe_float(report.get('retainedEarnings')),
                'fiscal_date_ending': report.get('fiscalDateEnding')
            }
        elif endpoint == 'CASH_FLOW':
            return {
                'operating_cashflow': self._safe_float(report.get('operatingCashflow')),
                'capital_expenditures': self._safe_float(report.get('capitalExpenditures')),
                'dividend_payout': self._safe_float(report.get('dividendPayout')),
                'fiscal_date_ending': report.get('fiscalDateEnding')
            }
        else:
            return {key: self._safe_float(value) if isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit() 
                   else value for key, value in report.items()}
    
    def _normalize_calendar_data(self, endpoint: str, data: Dict, ticker: str, metadata: Dict) -> List[Dict]:
        """Normalize calendar data (earnings, IPO calendars)"""
        records = []
        
        try:
            # Calendar data is typically a list of events
            if isinstance(data, list):
                for event in data:
                    record = {
                        'ticker': ticker,
                        'endpoint': endpoint,
                        'timestamp': self._make_timezone_aware(datetime.now()),
                        'date': self._safe_date(event.get('reportDate') or event.get('ipoDate')),
                        'raw_payload': event,
                        'parsed_values': {
                            key: self._safe_float(value) if isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit() 
                            else value for key, value in event.items()
                        },
                        'quality_flag': 'success',
                        'data_type': f'{endpoint.lower()}_event',
                        'metadata': metadata or {}
                    }
                    records.append(record)
            elif isinstance(data, dict):
                # Single calendar event
                record = {
                    'ticker': ticker,
                    'endpoint': endpoint,
                    'timestamp': self._make_timezone_aware(datetime.now()),
                    'date': self._safe_date(data.get('reportDate') or data.get('ipoDate')),
                    'raw_payload': data,
                    'parsed_values': {
                        key: self._safe_float(value) if isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit() 
                        else value for key, value in data.items()
                    },
                    'quality_flag': 'success',
                    'data_type': f'{endpoint.lower()}_event',
                    'metadata': metadata or {}
                }
                records.append(record)
                
        except Exception as e:
            logger.error(f"❌ Error normalizing {endpoint} calendar data: {str(e)}")
            return self._create_error_record(endpoint, data, ticker, str(e), metadata)
        
        return records
    
    def _normalize_intelligence(self, endpoint: str, data: Dict, ticker: str, metadata: Dict) -> List[Dict]:
        """Normalize market intelligence data"""
        records = []
        
        try:
            if endpoint == "NEWS_SENTIMENT":
                records = self._normalize_news_sentiment(data, ticker, metadata)
            elif endpoint == "TOP_GAINERS_LOSERS":
                records = self._normalize_top_movers(data, ticker, metadata)
            else:
                records = [self._create_generic_record(endpoint, data, ticker, metadata)]
            
            self.processed_records += len(records)
            logger.debug(f"✅ Normalized {len(records)} intelligence records for {endpoint}")
            
        except Exception as e:
            logger.error(f"❌ Error normalizing intelligence {endpoint}: {str(e)}")
            return self._create_error_record(endpoint, data, ticker, str(e), metadata)
        
        return records
    
    def _normalize_technical(self, endpoint: str, data: Dict, ticker: str, metadata: Dict) -> List[Dict]:
        """Normalize technical indicator data"""
        records = []
        
        try:
            # Technical indicators usually have a "Technical Analysis" key
            tech_key = f"Technical Analysis: {endpoint}"
            if tech_key in data:
                tech_data = data[tech_key]
                meta_data = data.get("Meta Data", {})
                
                for timestamp_str, values in tech_data.items():
                    timestamp = self._parse_timestamp(timestamp_str, endpoint)
                    
                    record = {
                        'ticker': ticker,
                        'endpoint': endpoint,
                        'timestamp': timestamp,
                        'raw_payload': data,
                        'parsed_values': {
                            **self._extract_technical_values(values, endpoint),
                            'meta_data': meta_data
                        },
                        'quality_flag': 'success',
                        'data_type': 'technical_indicator',
                        'interval_period': meta_data.get("3: Interval", "daily"),
                        'metadata': {
                            **(metadata or {}),
                            'symbol': meta_data.get("1: Symbol", ticker),
                            'indicator': meta_data.get("2: Indicator"),
                            'series_type': meta_data.get("4: Series Type"),
                            'time_period': meta_data.get("5: Time Period")
                        }
                    }
                    records.append(record)
            
            self.processed_records += len(records)
            logger.debug(f"✅ Normalized {len(records)} technical records for {endpoint}")
            
        except Exception as e:
            logger.error(f"❌ Error normalizing technical {endpoint}: {str(e)}")
            return self._create_error_record(endpoint, data, ticker, str(e), metadata)
        
        return records
    
    def _normalize_economic(self, endpoint: str, data: Dict, ticker: str, metadata: Dict) -> List[Dict]:
        """Normalize economic indicator data"""
        return self._normalize_time_series_like(endpoint, data, ticker, metadata, 'economic_indicator')
    
    def _normalize_commodities(self, endpoint: str, data: Dict, ticker: str, metadata: Dict) -> List[Dict]:
        """Normalize commodities data"""
        return self._normalize_time_series_like(endpoint, data, ticker, metadata, 'commodities')
    
    def _normalize_forex(self, endpoint: str, data: Dict, ticker: str, metadata: Dict) -> List[Dict]:
        """Normalize forex data"""
        return self._normalize_time_series_like(endpoint, data, ticker, metadata, 'forex')
    
    def _normalize_crypto(self, endpoint: str, data: Dict, ticker: str, metadata: Dict) -> List[Dict]:
        """Normalize cryptocurrency data"""
        return self._normalize_time_series_like(endpoint, data, ticker, metadata, 'crypto')
    
    def _normalize_options(self, endpoint: str, data: Dict, ticker: str, metadata: Dict) -> List[Dict]:
        """Normalize options data"""
        records = []
        
        try:
            if "data" in data and isinstance(data["data"], list):
                for option_data in data["data"]:
                    record = {
                        'ticker': ticker,
                        'endpoint': endpoint,
                        'timestamp': self._parse_timestamp(option_data.get("date", ""), endpoint),
                        'raw_payload': data,
                        'parsed_values': {
                            'strike': self._safe_float(option_data.get("strike")),
                            'expiration': option_data.get("expiration"),
                            'option_type': option_data.get("type"),
                            'last_price': self._safe_float(option_data.get("last")),
                            'bid': self._safe_float(option_data.get("bid")),
                            'ask': self._safe_float(option_data.get("ask")),
                            'volume': self._safe_int(option_data.get("volume")),
                            'open_interest': self._safe_int(option_data.get("open_interest")),
                            'implied_volatility': self._safe_float(option_data.get("implied_volatility"))
                        },
                        'quality_flag': 'success',
                        'data_type': 'options',
                        'metadata': {
                            **(metadata or {}),
                            'underlying_symbol': option_data.get("underlying_symbol", ticker)
                        }
                    }
                    records.append(record)
            
            self.processed_records += len(records)
            logger.debug(f"✅ Normalized {len(records)} options records for {endpoint}")
            
        except Exception as e:
            logger.error(f"❌ Error normalizing options {endpoint}: {str(e)}")
            return self._create_error_record(endpoint, data, ticker, str(e), metadata)
        
        return records
    
    def _normalize_generic(self, endpoint: str, data: Dict, ticker: str, metadata: Dict) -> List[Dict]:
        """Generic normalization for unknown endpoint types"""
        return [self._create_generic_record(endpoint, data, ticker, metadata)]
    
    # Helper methods
    
    def _find_time_series_key(self, data: Dict) -> Optional[str]:
        """Find the key containing time series data"""
        possible_keys = [
            "Time Series (5min)", "Time Series (1min)", "Time Series (15min)",
            "Time Series (30min)", "Time Series (60min)",
            "Time Series (Daily)", "Weekly Time Series", "Monthly Time Series",
            "Weekly Adjusted Time Series", "Monthly Adjusted Time Series",
            "Global Quote"
        ]
        
        for key in possible_keys:
            if key in data:
                return key
        
        # Look for any key containing "Time Series"
        for key in data.keys():
            if "Time Series" in key or "Global Quote" in key:
                return key
        
        return None
    
    def _parse_timestamp(self, timestamp_str: str, endpoint: str) -> datetime:
        """Parse timestamp string to timezone-aware datetime object for PostgreSQL"""
        try:
            # Try using dateutil.parser first (handles many formats automatically)
            try:
                dt = date_parser.parse(timestamp_str)
                return self._make_timezone_aware(dt)
            except:
                pass
            
            # Try different timestamp formats
            formats = [
                "%Y-%m-%d %H:%M:%S",  # 2023-01-01 09:30:00
                "%Y-%m-%d",           # 2023-01-01
                "%Y-%m-%d %H:%M",     # 2023-01-01 09:30
                "%m/%d/%Y",           # 01/01/2023
                "%Y%m%d"              # 20230101
            ]
            
            for fmt in formats:
                try:
                    # Parse to naive datetime then make timezone-aware
                    naive_dt = datetime.strptime(timestamp_str, fmt)
                    return self._make_timezone_aware(naive_dt)
                except ValueError:
                    continue
            
            # If all fails, return current time (timezone-aware)
            logger.warning(f"⚠️ Could not parse timestamp '{timestamp_str}' for {endpoint}")
            return self._make_timezone_aware(datetime.now())
            
        except Exception as e:
            logger.error(f"❌ Error parsing timestamp '{timestamp_str}': {e}")
            return self._make_timezone_aware(datetime.now())
    
    def _extract_ohlcv_values(self, values: Dict, endpoint: str) -> Dict:
        """Extract OHLCV values from time series data point"""
        result = {}
        
        # Map Alpha Vantage keys to standard names
        key_mapping = {
            "1. open": "open",
            "2. high": "high", 
            "3. low": "low",
            "4. close": "close",
            "5. adjusted close": "adjusted_close",
            "5. volume": "volume",
            "6. volume": "volume",
            "7. dividend amount": "dividend_amount",
            "8. split coefficient": "split_coefficient"
        }
        
        for av_key, std_key in key_mapping.items():
            if av_key in values:
                result[std_key] = self._safe_float(values[av_key])
        
        return result
    
    def _extract_technical_values(self, values: Dict, endpoint: str) -> Dict:
        """Extract values from technical indicator data"""
        result = {}
        
        # Common technical indicator keys
        common_keys = {
            endpoint: f"{endpoint.lower()}_value",
            f"{endpoint}": f"{endpoint.lower()}_value"
        }
        
        for key, value in values.items():
            clean_key = key.lower().replace(" ", "_")
            result[clean_key] = self._safe_float(value)
        
        return result
    
    def _normalize_time_series_like(self, endpoint: str, data: Dict, ticker: str, metadata: Dict, data_type: str) -> List[Dict]:
        """Generic normalization for time series-like data"""
        records = []
        
        try:
            # Look for data key
            data_key = None
            for key in data.keys():
                if "data" in key.lower() or endpoint.lower() in key.lower():
                    data_key = key
                    break
            
            if not data_key:
                return self._create_empty_record(endpoint, data, ticker, metadata)
            
            series_data = data[data_key]
            meta_data = data.get("Meta Data", {})
            
            for timestamp_str, values in series_data.items():
                timestamp = self._parse_timestamp(timestamp_str, endpoint)
                
                # Extract all numeric values
                parsed_values = {}
                for key, value in values.items():
                    clean_key = key.lower().replace(" ", "_").replace(".", "")
                    parsed_values[clean_key] = self._safe_float(value)
                
                record = {
                    'ticker': ticker or endpoint,  # Use endpoint name if no ticker
                    'endpoint': endpoint,
                    'timestamp': timestamp,
                    'raw_payload': data,
                    'parsed_values': {**parsed_values, 'meta_data': meta_data},
                    'quality_flag': 'success',
                    'data_type': data_type,
                    'metadata': {
                        **(metadata or {}),
                        'unit': meta_data.get("Unit"),
                        'interval': meta_data.get("Interval")
                    }
                }
                records.append(record)
            
        except Exception as e:
            logger.error(f"❌ Error in time series normalization for {endpoint}: {str(e)}")
            return self._create_error_record(endpoint, data, ticker, str(e), metadata)
        
        return records
    
    def _safe_float(self, value: Any) -> Optional[float]:
        """Safely convert value to float"""
        if value is None or value == "":
            return None
        try:
            if isinstance(value, str):
                # Remove common non-numeric characters
                cleaned = value.replace(",", "").replace("$", "").strip()
                if cleaned == "None" or cleaned == "N/A":
                    return None
                return float(cleaned)
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value: Any) -> Optional[int]:
        """Safely convert value to int"""
        float_val = self._safe_float(value)
        return int(float_val) if float_val is not None else None
    
    def _safe_date(self, value: Any) -> Optional[datetime]:
        """Safely convert value to datetime"""
        if value is None or value == "" or value == "None":
            return None
        try:
            if isinstance(value, str):
                # Handle common date formats
                return self._make_timezone_aware(date_parser.parse(value))
            elif isinstance(value, datetime):
                return self._make_timezone_aware(value)
            else:
                return None
        except (ValueError, TypeError):
            return None
    
    def _create_generic_record(self, endpoint: str, data: Dict, ticker: str, metadata: Dict) -> Dict:
        """Create a generic record for unknown data formats"""
        return {
            'ticker': ticker,
            'endpoint': endpoint,
            'timestamp': self._make_timezone_aware(datetime.now()),
            'raw_payload': data,
            'parsed_values': {'raw_response': data},
            'quality_flag': 'success' if data else 'empty',
            'data_type': 'generic',
            'metadata': metadata or {}
        }
    
    def _create_empty_record(self, endpoint: str, data: Dict, ticker: str, metadata: Dict) -> List[Dict]:
        """Create an empty record for endpoints with no data"""
        return [{
            'ticker': ticker,
            'endpoint': endpoint,
            'timestamp': self._make_timezone_aware(datetime.now()),
            'raw_payload': data,
            'parsed_values': {},
            'quality_flag': 'empty',
            'data_type': 'empty',
            'metadata': metadata or {}
        }]
    
    def _create_error_record(self, endpoint: str, data: Dict, ticker: str, error: str, metadata: Dict) -> List[Dict]:
        """Create an error record for failed normalizations"""
        return [{
            'ticker': ticker,
            'endpoint': endpoint,
            'timestamp': self._make_timezone_aware(datetime.now()),
            'raw_payload': data,
            'parsed_values': {'error': error},
            'quality_flag': 'error',
            'data_type': 'error',
            'metadata': {**(metadata or {}), 'error_message': error}
        }]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get normalization statistics"""
        return {
            'processed_records': self.processed_records,
            'processed_endpoints': self.processed_endpoints,
            'normalization_errors': self.normalization_errors,
            'quality_flags': self.quality_flags
        }
    
    def reset_statistics(self):
        """Reset normalization statistics"""
        self.processed_records = 0
        self.processed_endpoints = 0
        self.normalization_errors = 0
    
    def _make_timezone_aware(self, dt: datetime) -> datetime:
        """Convert naive datetime to timezone-aware UTC datetime for PostgreSQL compatibility"""
        if dt.tzinfo is None:
            # Convert naive datetime to UTC timezone-aware
            return pytz.UTC.localize(dt)
        return dt
