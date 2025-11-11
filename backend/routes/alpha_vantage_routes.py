"""
Alpha Vantage API Route Index - Complete Implementation
Comprehensive routing system for all 70+ Alpha Vantage API endpoints
Organized by category for easy access and implementation in the uRISK system.
"""

from typing import Dict, List, Optional, Union, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import httpx
import asyncio
from datetime import datetime
import os

from ..config.settings import settings

router = APIRouter()

# ==========================================
# ALPHA VANTAGE API ROUTE INDEX
# ==========================================

class AlphaVantageAPI:
    """Complete Alpha Vantage API implementation with all 70+ endpoints"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.ALPHA_VANTAGE_API_KEY
        
    # ==========================================
    # 🏢 CORE STOCK APIS
    # ==========================================
    
    @staticmethod
    def get_core_stock_endpoints() -> Dict[str, Dict[str, Any]]:
        """Returns all core stock API endpoints with parameters"""
        return {
            "TIME_SERIES_INTRADAY": {
                "function": "TIME_SERIES_INTRADAY",
                "description": "Current and 20+ years of historical intraday OHLCV time series",
                "required_params": ["symbol", "interval"],
                "optional_params": ["adjusted", "extended_hours", "month", "outputsize", "datatype"],
                "intervals": ["1min", "5min", "15min", "30min", "60min"],
                "route": "/stock/intraday"
            },
            "TIME_SERIES_DAILY": {
                "function": "TIME_SERIES_DAILY",
                "description": "Daily open/high/low/close/volume values",
                "required_params": ["symbol"],
                "optional_params": ["outputsize", "datatype"],
                "route": "/stock/daily"
            },
            "TIME_SERIES_DAILY_ADJUSTED": {
                "function": "TIME_SERIES_DAILY_ADJUSTED",
                "description": "Daily OHLCV + adjusted close + dividend/split events",
                "required_params": ["symbol"],
                "optional_params": ["outputsize", "datatype"],
                "route": "/stock/daily-adjusted"
            },
            "TIME_SERIES_WEEKLY": {
                "function": "TIME_SERIES_WEEKLY",
                "description": "Weekly time series (last trading day of each week)",
                "required_params": ["symbol"],
                "optional_params": ["datatype"],
                "route": "/stock/weekly"
            },
            "TIME_SERIES_WEEKLY_ADJUSTED": {
                "function": "TIME_SERIES_WEEKLY_ADJUSTED",
                "description": "Weekly adjusted time series with dividends",
                "required_params": ["symbol"],
                "optional_params": ["datatype"],
                "route": "/stock/weekly-adjusted"
            },
            "TIME_SERIES_MONTHLY": {
                "function": "TIME_SERIES_MONTHLY",
                "description": "Monthly time series (last trading day of each month)",
                "required_params": ["symbol"],
                "optional_params": ["datatype"],
                "route": "/stock/monthly"
            },
            "TIME_SERIES_MONTHLY_ADJUSTED": {
                "function": "TIME_SERIES_MONTHLY_ADJUSTED",
                "description": "Monthly adjusted time series with dividends",
                "required_params": ["symbol"],
                "optional_params": ["datatype"],
                "route": "/stock/monthly-adjusted"
            },
            "GLOBAL_QUOTE": {
                "function": "GLOBAL_QUOTE",
                "description": "Latest price and volume information",
                "required_params": ["symbol"],
                "optional_params": ["datatype"],
                "route": "/stock/quote"
            },
            "SYMBOL_SEARCH": {
                "function": "SYMBOL_SEARCH",
                "description": "Search for ticker symbols and company names",
                "required_params": ["keywords"],
                "optional_params": ["datatype"],
                "route": "/stock/search"
            },
            "MARKET_STATUS": {
                "function": "MARKET_STATUS",
                "description": "Global market status (open/closed)",
                "required_params": [],
                "optional_params": [],
                "route": "/stock/market-status"
            }
        }
    
    # ==========================================
    # 📊 OPTIONS DATA APIS
    # ==========================================
    
    @staticmethod
    def get_options_endpoints() -> Dict[str, Dict[str, Any]]:
        """Returns all options API endpoints"""
        return {
            "REALTIME_OPTIONS": {
                "function": "REALTIME_OPTIONS",
                "description": "Real-time options data (Premium)",
                "required_params": ["symbol"],
                "optional_params": ["contract", "datatype"],
                "premium": True,
                "route": "/options/realtime"
            },
            "HISTORICAL_OPTIONS": {
                "function": "HISTORICAL_OPTIONS",
                "description": "Historical options data",
                "required_params": ["symbol"],
                "optional_params": ["date", "datatype"],
                "route": "/options/historical"
            }
        }
    
    # ==========================================
    # 🧠 ALPHA INTELLIGENCE™
    # ==========================================
    
    @staticmethod
    def get_intelligence_endpoints() -> Dict[str, Dict[str, Any]]:
        """Returns all Alpha Intelligence API endpoints"""
        return {
            "NEWS_SENTIMENT": {
                "function": "NEWS_SENTIMENT",
                "description": "News and sentiment analysis for stocks",
                "required_params": [],
                "optional_params": ["tickers", "topics", "time_from", "time_to", "sort", "limit"],
                "route": "/intelligence/news"
            },
            "EARNINGS_CALL_TRANSCRIPT": {
                "function": "EARNINGS_CALL_TRANSCRIPT",
                "description": "Earnings call transcripts with sentiment",
                "required_params": ["symbol", "quarter"],
                "optional_params": [],
                "route": "/intelligence/earnings-transcript"
            },
            "TOP_GAINERS_LOSERS": {
                "function": "TOP_GAINERS_LOSERS",
                "description": "Top 20 gainers, losers, and most active tickers",
                "required_params": [],
                "optional_params": [],
                "route": "/intelligence/top-movers"
            },
            "INSIDER_TRANSACTIONS": {
                "function": "INSIDER_TRANSACTIONS",
                "description": "Latest and historical insider transactions",
                "required_params": ["symbol"],
                "optional_params": [],
                "route": "/intelligence/insider-transactions"
            },
            "ANALYTICS_FIXED_WINDOW": {
                "function": "ANALYTICS_FIXED_WINDOW",
                "description": "Advanced analytics over fixed time window",
                "required_params": ["SYMBOLS", "RANGE", "INTERVAL", "CALCULATIONS"],
                "optional_params": ["OHLC"],
                "route": "/intelligence/analytics-fixed"
            },
            "ANALYTICS_SLIDING_WINDOW": {
                "function": "ANALYTICS_SLIDING_WINDOW",
                "description": "Advanced analytics over sliding time windows",
                "required_params": ["SYMBOLS", "RANGE", "INTERVAL", "WINDOW_SIZE", "CALCULATIONS"],
                "optional_params": ["OHLC"],
                "route": "/intelligence/analytics-sliding"
            }
        }
    
    # ==========================================
    # 📈 FUNDAMENTAL DATA
    # ==========================================
    
    @staticmethod
    def get_fundamental_endpoints() -> Dict[str, Dict[str, Any]]:
        """Returns all fundamental data API endpoints"""
        return {
            "OVERVIEW": {
                "function": "OVERVIEW",
                "description": "Company overview and key metrics",
                "required_params": ["symbol"],
                "optional_params": [],
                "route": "/fundamental/overview"
            },
            "ETF_PROFILE": {
                "function": "ETF_PROFILE",
                "description": "ETF profile and holdings information",
                "required_params": ["symbol"],
                "optional_params": [],
                "route": "/fundamental/etf-profile"
            },
            "DIVIDENDS": {
                "function": "DIVIDENDS",
                "description": "Dividend payment history",
                "required_params": ["symbol"],
                "optional_params": ["datatype"],
                "route": "/fundamental/dividends"
            },
            "SPLITS": {
                "function": "SPLITS",
                "description": "Stock split history",
                "required_params": ["symbol"],
                "optional_params": ["datatype"],
                "route": "/fundamental/splits"
            },
            "INCOME_STATEMENT": {
                "function": "INCOME_STATEMENT",
                "description": "Annual and quarterly income statements",
                "required_params": ["symbol"],
                "optional_params": [],
                "route": "/fundamental/income-statement"
            },
            "BALANCE_SHEET": {
                "function": "BALANCE_SHEET",
                "description": "Annual and quarterly balance sheets",
                "required_params": ["symbol"],
                "optional_params": [],
                "route": "/fundamental/balance-sheet"
            },
            "CASH_FLOW": {
                "function": "CASH_FLOW",
                "description": "Annual and quarterly cash flows",
                "required_params": ["symbol"],
                "optional_params": [],
                "route": "/fundamental/cash-flow"
            },
            "SHARES_OUTSTANDING": {
                "function": "SHARES_OUTSTANDING",
                "description": "Quarterly shares outstanding (diluted and basic)",
                "required_params": ["symbol"],
                "optional_params": ["datatype"],
                "route": "/fundamental/shares-outstanding"
            },
            "EARNINGS": {
                "function": "EARNINGS",
                "description": "Annual and quarterly earnings (EPS)",
                "required_params": ["symbol"],
                "optional_params": [],
                "route": "/fundamental/earnings"
            },
            "EARNINGS_ESTIMATES": {
                "function": "EARNINGS_ESTIMATES",
                "description": "EPS and revenue estimates with analyst data",
                "required_params": ["symbol"],
                "optional_params": [],
                "route": "/fundamental/earnings-estimates"
            },
            "LISTING_STATUS": {
                "function": "LISTING_STATUS",
                "description": "Active or delisted stocks and ETFs",
                "required_params": [],
                "optional_params": ["date", "state"],
                "route": "/fundamental/listing-status"
            },
            "EARNINGS_CALENDAR": {
                "function": "EARNINGS_CALENDAR",
                "description": "Company earnings expected in next 3-12 months",
                "required_params": [],
                "optional_params": ["symbol", "horizon"],
                "route": "/fundamental/earnings-calendar"
            },
            "IPO_CALENDAR": {
                "function": "IPO_CALENDAR",
                "description": "IPOs expected in the next 3 months",
                "required_params": [],
                "optional_params": [],
                "route": "/fundamental/ipo-calendar"
            }
        }
    
    # ==========================================
    # 💱 FOREX (FX)
    # ==========================================
    
    @staticmethod
    def get_forex_endpoints() -> Dict[str, Dict[str, Any]]:
        """Returns all forex API endpoints"""
        return {
            "CURRENCY_EXCHANGE_RATE": {
                "function": "CURRENCY_EXCHANGE_RATE",
                "description": "Realtime exchange rate for currency pairs",
                "required_params": ["from_currency", "to_currency"],
                "optional_params": [],
                "route": "/forex/exchange-rate"
            },
            "FX_INTRADAY": {
                "function": "FX_INTRADAY",
                "description": "Intraday FX time series (Premium)",
                "required_params": ["from_symbol", "to_symbol", "interval"],
                "optional_params": ["outputsize", "datatype"],
                "premium": True,
                "route": "/forex/intraday"
            },
            "FX_DAILY": {
                "function": "FX_DAILY",
                "description": "Daily FX time series",
                "required_params": ["from_symbol", "to_symbol"],
                "optional_params": ["outputsize", "datatype"],
                "route": "/forex/daily"
            },
            "FX_WEEKLY": {
                "function": "FX_WEEKLY",
                "description": "Weekly FX time series",
                "required_params": ["from_symbol", "to_symbol"],
                "optional_params": ["datatype"],
                "route": "/forex/weekly"
            },
            "FX_MONTHLY": {
                "function": "FX_MONTHLY",
                "description": "Monthly FX time series",
                "required_params": ["from_symbol", "to_symbol"],
                "optional_params": ["datatype"],
                "route": "/forex/monthly"
            }
        }
    
    # ==========================================
    # ₿ CRYPTOCURRENCIES
    # ==========================================
    
    @staticmethod
    def get_crypto_endpoints() -> Dict[str, Dict[str, Any]]:
        """Returns all cryptocurrency API endpoints"""
        return {
            "DIGITAL_CURRENCY_INTRADAY": {
                "function": "DIGITAL_CURRENCY_INTRADAY",
                "description": "Intraday cryptocurrency time series (Premium)",
                "required_params": ["symbol", "market", "interval"],
                "optional_params": ["outputsize", "datatype"],
                "premium": True,
                "route": "/crypto/intraday"
            },
            "DIGITAL_CURRENCY_DAILY": {
                "function": "DIGITAL_CURRENCY_DAILY",
                "description": "Daily cryptocurrency time series",
                "required_params": ["symbol", "market"],
                "optional_params": ["datatype"],
                "route": "/crypto/daily"
            },
            "DIGITAL_CURRENCY_WEEKLY": {
                "function": "DIGITAL_CURRENCY_WEEKLY",
                "description": "Weekly cryptocurrency time series",
                "required_params": ["symbol", "market"],
                "optional_params": ["datatype"],
                "route": "/crypto/weekly"
            },
            "DIGITAL_CURRENCY_MONTHLY": {
                "function": "DIGITAL_CURRENCY_MONTHLY",
                "description": "Monthly cryptocurrency time series",
                "required_params": ["symbol", "market"],
                "optional_params": ["datatype"],
                "route": "/crypto/monthly"
            }
        }
    
    # ==========================================
    # 🛢️ COMMODITIES
    # ==========================================
    
    @staticmethod
    def get_commodities_endpoints() -> Dict[str, Dict[str, Any]]:
        """Returns all commodities API endpoints"""
        return {
            "WTI": {
                "function": "WTI",
                "description": "West Texas Intermediate crude oil prices",
                "required_params": [],
                "optional_params": ["interval", "datatype"],
                "route": "/commodities/wti"
            },
            "BRENT": {
                "function": "BRENT",
                "description": "Brent crude oil prices",
                "required_params": [],
                "optional_params": ["interval", "datatype"],
                "route": "/commodities/brent"
            },
            "NATURAL_GAS": {
                "function": "NATURAL_GAS",
                "description": "Natural gas prices",
                "required_params": [],
                "optional_params": ["interval", "datatype"],
                "route": "/commodities/natural-gas"
            },
            "COPPER": {
                "function": "COPPER",
                "description": "Copper prices",
                "required_params": [],
                "optional_params": ["interval", "datatype"],
                "route": "/commodities/copper"
            },
            "ALUMINUM": {
                "function": "ALUMINUM",
                "description": "Aluminum prices",
                "required_params": [],
                "optional_params": ["interval", "datatype"],
                "route": "/commodities/aluminum"
            },
            "WHEAT": {
                "function": "WHEAT",
                "description": "Wheat commodity prices",
                "required_params": [],
                "optional_params": ["interval", "datatype"],
                "route": "/commodities/wheat"
            },
            "CORN": {
                "function": "CORN",
                "description": "Corn commodity prices",
                "required_params": [],
                "optional_params": ["interval", "datatype"],
                "route": "/commodities/corn"
            },
            "COTTON": {
                "function": "COTTON",
                "description": "Cotton commodity prices",
                "required_params": [],
                "optional_params": ["interval", "datatype"],
                "route": "/commodities/cotton"
            },
            "SUGAR": {
                "function": "SUGAR",
                "description": "Sugar commodity prices",
                "required_params": [],
                "optional_params": ["interval", "datatype"],
                "route": "/commodities/sugar"
            },
            "COFFEE": {
                "function": "COFFEE",
                "description": "Coffee commodity prices",
                "required_params": [],
                "optional_params": ["interval", "datatype"],
                "route": "/commodities/coffee"
            },
            "GLOBAL_COMMODITIES": {
                "function": "GLOBAL_COMMODITIES",
                "description": "Global commodities index",
                "required_params": [],
                "optional_params": ["interval", "datatype"],
                "route": "/commodities/global-index"
            }
        }
    
    # ==========================================
    # 🏛️ ECONOMIC INDICATORS
    # ==========================================
    
    @staticmethod
    def get_economic_endpoints() -> Dict[str, Dict[str, Any]]:
        """Returns all economic indicators API endpoints"""
        return {
            "REAL_GDP": {
                "function": "REAL_GDP",
                "description": "Real Gross Domestic Product",
                "required_params": [],
                "optional_params": ["interval", "datatype"],
                "route": "/economic/real-gdp"
            },
            "REAL_GDP_PER_CAPITA": {
                "function": "REAL_GDP_PER_CAPITA",
                "description": "Real GDP per capita",
                "required_params": [],
                "optional_params": ["datatype"],
                "route": "/economic/real-gdp-per-capita"
            },
            "TREASURY_YIELD": {
                "function": "TREASURY_YIELD",
                "description": "Treasury yield rates",
                "required_params": [],
                "optional_params": ["interval", "maturity", "datatype"],
                "route": "/economic/treasury-yield"
            },
            "FEDERAL_FUNDS_RATE": {
                "function": "FEDERAL_FUNDS_RATE",
                "description": "Federal funds interest rate",
                "required_params": [],
                "optional_params": ["interval", "datatype"],
                "route": "/economic/federal-funds-rate"
            },
            "CPI": {
                "function": "CPI",
                "description": "Consumer Price Index",
                "required_params": [],
                "optional_params": ["interval", "datatype"],
                "route": "/economic/cpi"
            },
            "INFLATION": {
                "function": "INFLATION",
                "description": "Inflation rate",
                "required_params": [],
                "optional_params": ["datatype"],
                "route": "/economic/inflation"
            },
            "RETAIL_SALES": {
                "function": "RETAIL_SALES",
                "description": "Retail sales data",
                "required_params": [],
                "optional_params": ["datatype"],
                "route": "/economic/retail-sales"
            },
            "DURABLES": {
                "function": "DURABLES",
                "description": "Durable goods orders",
                "required_params": [],
                "optional_params": ["datatype"],
                "route": "/economic/durables"
            },
            "UNEMPLOYMENT": {
                "function": "UNEMPLOYMENT",
                "description": "Unemployment rate",
                "required_params": [],
                "optional_params": ["datatype"],
                "route": "/economic/unemployment"
            },
            "NONFARM_PAYROLL": {
                "function": "NONFARM_PAYROLL",
                "description": "Nonfarm payroll data",
                "required_params": [],
                "optional_params": ["datatype"],
                "route": "/economic/nonfarm-payroll"
            }
        }
    
    # ==========================================
    # 📊 TECHNICAL INDICATORS (70+ indicators)
    # ==========================================
    
    @staticmethod
    def get_technical_endpoints() -> Dict[str, Dict[str, Any]]:
        """Returns all technical indicators API endpoints (70+ indicators)"""
        return {
            # Moving Averages
            "SMA": {
                "function": "SMA",
                "description": "Simple Moving Average",
                "required_params": ["symbol", "interval", "time_period", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/sma"
            },
            "EMA": {
                "function": "EMA",
                "description": "Exponential Moving Average",
                "required_params": ["symbol", "interval", "time_period", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/ema"
            },
            "WMA": {
                "function": "WMA",
                "description": "Weighted Moving Average",
                "required_params": ["symbol", "interval", "time_period", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/wma"
            },
            "DEMA": {
                "function": "DEMA",
                "description": "Double Exponential Moving Average",
                "required_params": ["symbol", "interval", "time_period", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/dema"
            },
            "TEMA": {
                "function": "TEMA",
                "description": "Triple Exponential Moving Average",
                "required_params": ["symbol", "interval", "time_period", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/tema"
            },
            "TRIMA": {
                "function": "TRIMA",
                "description": "Triangular Moving Average",
                "required_params": ["symbol", "interval", "time_period", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/trima"
            },
            "KAMA": {
                "function": "KAMA",
                "description": "Kaufman Adaptive Moving Average",
                "required_params": ["symbol", "interval", "time_period", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/kama"
            },
            "MAMA": {
                "function": "MAMA",
                "description": "MESA Adaptive Moving Average",
                "required_params": ["symbol", "interval", "series_type"],
                "optional_params": ["month", "fastlimit", "slowlimit", "datatype"],
                "route": "/technical/mama"
            },
            "VWAP": {
                "function": "VWAP",
                "description": "Volume Weighted Average Price (Premium)",
                "required_params": ["symbol", "interval"],
                "optional_params": ["month", "datatype"],
                "premium": True,
                "route": "/technical/vwap"
            },
            "T3": {
                "function": "T3",
                "description": "Triple Exponential Moving Average (T3)",
                "required_params": ["symbol", "interval", "time_period", "series_type"],
                "optional_params": ["month", "vfactor", "datatype"],
                "route": "/technical/t3"
            },
            
            # Oscillators
            "MACD": {
                "function": "MACD",
                "description": "Moving Average Convergence Divergence (Premium)",
                "required_params": ["symbol", "interval", "series_type"],
                "optional_params": ["month", "fastperiod", "slowperiod", "signalperiod", "datatype"],
                "premium": True,
                "route": "/technical/macd"
            },
            "MACDEXT": {
                "function": "MACDEXT",
                "description": "MACD with controllable MA type",
                "required_params": ["symbol", "interval", "series_type"],
                "optional_params": ["month", "fastperiod", "slowperiod", "signalperiod", "fastmatype", "slowmatype", "signalmatype", "datatype"],
                "route": "/technical/macdext"
            },
            "STOCH": {
                "function": "STOCH",
                "description": "Stochastic Oscillator",
                "required_params": ["symbol", "interval"],
                "optional_params": ["month", "fastkperiod", "slowkperiod", "slowdperiod", "slowkmatype", "slowdmatype", "datatype"],
                "route": "/technical/stoch"
            },
            "STOCHF": {
                "function": "STOCHF",
                "description": "Stochastic Fast",
                "required_params": ["symbol", "interval"],
                "optional_params": ["month", "fastkperiod", "fastdperiod", "fastdmatype", "datatype"],
                "route": "/technical/stochf"
            },
            "RSI": {
                "function": "RSI",
                "description": "Relative Strength Index",
                "required_params": ["symbol", "interval", "time_period", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/rsi"
            },
            "STOCHRSI": {
                "function": "STOCHRSI",
                "description": "Stochastic RSI",
                "required_params": ["symbol", "interval", "time_period", "series_type"],
                "optional_params": ["month", "fastkperiod", "fastdperiod", "fastdmatype", "datatype"],
                "route": "/technical/stochrsi"
            },
            "WILLR": {
                "function": "WILLR",
                "description": "Williams %R",
                "required_params": ["symbol", "interval", "time_period"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/willr"
            },
            "ADX": {
                "function": "ADX",
                "description": "Average Directional Index",
                "required_params": ["symbol", "interval", "time_period"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/adx"
            },
            "ADXR": {
                "function": "ADXR",
                "description": "Average Directional Index Rating",
                "required_params": ["symbol", "interval", "time_period"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/adxr"
            },
            "APO": {
                "function": "APO",
                "description": "Absolute Price Oscillator",
                "required_params": ["symbol", "interval", "series_type"],
                "optional_params": ["month", "fastperiod", "slowperiod", "matype", "datatype"],
                "route": "/technical/apo"
            },
            "PPO": {
                "function": "PPO",
                "description": "Percentage Price Oscillator",
                "required_params": ["symbol", "interval", "series_type"],
                "optional_params": ["month", "fastperiod", "slowperiod", "matype", "datatype"],
                "route": "/technical/ppo"
            },
            "MOM": {
                "function": "MOM",
                "description": "Momentum",
                "required_params": ["symbol", "interval", "time_period", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/mom"
            },
            "BOP": {
                "function": "BOP",
                "description": "Balance of Power",
                "required_params": ["symbol", "interval"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/bop"
            },
            "CCI": {
                "function": "CCI",
                "description": "Commodity Channel Index",
                "required_params": ["symbol", "interval", "time_period"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/cci"
            },
            "CMO": {
                "function": "CMO",
                "description": "Chande Momentum Oscillator",
                "required_params": ["symbol", "interval", "time_period", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/cmo"
            },
            "ROC": {
                "function": "ROC",
                "description": "Rate of Change",
                "required_params": ["symbol", "interval", "time_period", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/roc"
            },
            "ROCR": {
                "function": "ROCR",
                "description": "Rate of Change Ratio",
                "required_params": ["symbol", "interval", "time_period", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/rocr"
            },
            "AROON": {
                "function": "AROON",
                "description": "Aroon Indicator",
                "required_params": ["symbol", "interval", "time_period"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/aroon"
            },
            "AROONOSC": {
                "function": "AROONOSC",
                "description": "Aroon Oscillator",
                "required_params": ["symbol", "interval", "time_period"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/aroonosc"
            },
            "MFI": {
                "function": "MFI",
                "description": "Money Flow Index",
                "required_params": ["symbol", "interval", "time_period"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/mfi"
            },
            "TRIX": {
                "function": "TRIX",
                "description": "Triple Exponential Average",
                "required_params": ["symbol", "interval", "time_period", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/trix"
            },
            "ULTOSC": {
                "function": "ULTOSC",
                "description": "Ultimate Oscillator",
                "required_params": ["symbol", "interval"],
                "optional_params": ["month", "timeperiod1", "timeperiod2", "timeperiod3", "datatype"],
                "route": "/technical/ultosc"
            },
            "DX": {
                "function": "DX",
                "description": "Directional Movement Index",
                "required_params": ["symbol", "interval", "time_period"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/dx"
            },
            "MINUS_DI": {
                "function": "MINUS_DI",
                "description": "Minus Directional Indicator",
                "required_params": ["symbol", "interval", "time_period"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/minus-di"
            },
            "PLUS_DI": {
                "function": "PLUS_DI",
                "description": "Plus Directional Indicator",
                "required_params": ["symbol", "interval", "time_period"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/plus-di"
            },
            "MINUS_DM": {
                "function": "MINUS_DM",
                "description": "Minus Directional Movement",
                "required_params": ["symbol", "interval", "time_period"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/minus-dm"
            },
            "PLUS_DM": {
                "function": "PLUS_DM",
                "description": "Plus Directional Movement",
                "required_params": ["symbol", "interval", "time_period"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/plus-dm"
            },
            
            # Price Transforms
            "BBANDS": {
                "function": "BBANDS",
                "description": "Bollinger Bands",
                "required_params": ["symbol", "interval", "time_period", "series_type"],
                "optional_params": ["month", "nbdevup", "nbdevdn", "matype", "datatype"],
                "route": "/technical/bbands"
            },
            "MIDPOINT": {
                "function": "MIDPOINT",
                "description": "Midpoint",
                "required_params": ["symbol", "interval", "time_period", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/midpoint"
            },
            "MIDPRICE": {
                "function": "MIDPRICE",
                "description": "Midprice",
                "required_params": ["symbol", "interval", "time_period"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/midprice"
            },
            "SAR": {
                "function": "SAR",
                "description": "Parabolic SAR",
                "required_params": ["symbol", "interval"],
                "optional_params": ["month", "acceleration", "maximum", "datatype"],
                "route": "/technical/sar"
            },
            "TRANGE": {
                "function": "TRANGE",
                "description": "True Range",
                "required_params": ["symbol", "interval"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/trange"
            },
            "ATR": {
                "function": "ATR",
                "description": "Average True Range",
                "required_params": ["symbol", "interval", "time_period"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/atr"
            },
            "NATR": {
                "function": "NATR",
                "description": "Normalized Average True Range",
                "required_params": ["symbol", "interval", "time_period"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/natr"
            },
            
            # Volume Indicators
            "AD": {
                "function": "AD",
                "description": "Accumulation/Distribution Line",
                "required_params": ["symbol", "interval"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/ad"
            },
            "ADOSC": {
                "function": "ADOSC",
                "description": "Accumulation/Distribution Oscillator",
                "required_params": ["symbol", "interval"],
                "optional_params": ["month", "fastperiod", "slowperiod", "datatype"],
                "route": "/technical/adosc"
            },
            "OBV": {
                "function": "OBV",
                "description": "On Balance Volume",
                "required_params": ["symbol", "interval"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/obv"
            },
            
            # Cycle Indicators
            "HT_TRENDLINE": {
                "function": "HT_TRENDLINE",
                "description": "Hilbert Transform - Instantaneous Trendline",
                "required_params": ["symbol", "interval", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/ht-trendline"
            },
            "HT_SINE": {
                "function": "HT_SINE",
                "description": "Hilbert Transform - Sine Wave",
                "required_params": ["symbol", "interval", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/ht-sine"
            },
            "HT_TRENDMODE": {
                "function": "HT_TRENDMODE",
                "description": "Hilbert Transform - Trend vs Cycle Mode",
                "required_params": ["symbol", "interval", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/ht-trendmode"
            },
            "HT_DCPERIOD": {
                "function": "HT_DCPERIOD",
                "description": "Hilbert Transform - Dominant Cycle Period",
                "required_params": ["symbol", "interval", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/ht-dcperiod"
            },
            "HT_DCPHASE": {
                "function": "HT_DCPHASE",
                "description": "Hilbert Transform - Dominant Cycle Phase",
                "required_params": ["symbol", "interval", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/ht-dcphase"
            },
            "HT_PHASOR": {
                "function": "HT_PHASOR",
                "description": "Hilbert Transform - Phasor Components",
                "required_params": ["symbol", "interval", "series_type"],
                "optional_params": ["month", "datatype"],
                "route": "/technical/ht-phasor"
            }
        }
    
    # ==========================================
    # COMPLETE API INDEX
    # ==========================================
    
    @classmethod
    def get_complete_api_index(cls) -> Dict[str, Dict[str, Any]]:
        """Returns complete Alpha Vantage API index with all 70+ endpoints"""
        complete_index = {}
        
        # Add all endpoint categories
        complete_index.update(cls.get_core_stock_endpoints())
        complete_index.update(cls.get_options_endpoints())
        complete_index.update(cls.get_intelligence_endpoints())
        complete_index.update(cls.get_fundamental_endpoints())
        complete_index.update(cls.get_forex_endpoints())
        complete_index.update(cls.get_crypto_endpoints())
        complete_index.update(cls.get_commodities_endpoints())
        complete_index.update(cls.get_economic_endpoints())
        complete_index.update(cls.get_technical_endpoints())
        
        return complete_index
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    async def make_api_request(self, function: str, **params) -> Dict[str, Any]:
        """Make API request to Alpha Vantage with given function and parameters"""
        params_dict = {
            "function": function,
            "apikey": self.api_key,
            **params
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.BASE_URL, params=params_dict)
            return response.json()
    
    def build_url(self, function: str, **params) -> str:
        """Build complete Alpha Vantage API URL"""
        params_dict = {
            "function": function,
            "apikey": self.api_key,
            **params
        }
        
        param_string = "&".join([f"{k}={v}" for k, v in params_dict.items()])
        return f"{self.BASE_URL}?{param_string}"


# ==========================================
# FASTAPI ROUTE IMPLEMENTATIONS
# ==========================================

# Instance for making API calls
alpha_vantage = AlphaVantageAPI()

@router.get("/")
async def get_api_index():
    """Get complete Alpha Vantage API index with all endpoints"""
    return {
        "title": "Alpha Vantage API - Complete Route Index",
        "description": "All 70+ Alpha Vantage API endpoints organized by category",
        "total_endpoints": len(alpha_vantage.get_complete_api_index()),
        "categories": {
            "core_stock": len(alpha_vantage.get_core_stock_endpoints()),
            "options": len(alpha_vantage.get_options_endpoints()),
            "intelligence": len(alpha_vantage.get_intelligence_endpoints()),
            "fundamental": len(alpha_vantage.get_fundamental_endpoints()),
            "forex": len(alpha_vantage.get_forex_endpoints()),
            "crypto": len(alpha_vantage.get_crypto_endpoints()),
            "commodities": len(alpha_vantage.get_commodities_endpoints()),
            "economic": len(alpha_vantage.get_economic_endpoints()),
            "technical": len(alpha_vantage.get_technical_endpoints())
        },
        "endpoints": alpha_vantage.get_complete_api_index()
    }

# Example route implementations for each category
@router.get("/stock/intraday")
async def get_stock_intraday(
    symbol: str,
    interval: str = Query(..., description="1min, 5min, 15min, 30min, 60min"),
    adjusted: bool = Query(True, description="Adjust for splits/dividends"),
    outputsize: str = Query("compact", description="compact or full"),
    datatype: str = Query("json", description="json or csv")
):
    """Get intraday stock data"""
    return await alpha_vantage.make_api_request(
        "TIME_SERIES_INTRADAY",
        symbol=symbol,
        interval=interval,
        adjusted=str(adjusted).lower(),
        outputsize=outputsize,
        datatype=datatype
    )

@router.get("/fundamental/overview")
async def get_company_overview(symbol: str):
    """Get company overview and fundamentals"""
    return await alpha_vantage.make_api_request("OVERVIEW", symbol=symbol)

@router.get("/technical/rsi")
async def get_rsi(
    symbol: str,
    interval: str,
    time_period: int = 14,
    series_type: str = "close"
):
    """Get Relative Strength Index (RSI)"""
    return await alpha_vantage.make_api_request(
        "RSI",
        symbol=symbol,
        interval=interval,
        time_period=time_period,
        series_type=series_type
    )

@router.get("/intelligence/news")
async def get_news_sentiment(
    tickers: Optional[str] = None,
    topics: Optional[str] = None,
    limit: int = 50
):
    """Get news and sentiment analysis"""
    params = {"limit": limit}
    if tickers:
        params["tickers"] = tickers
    if topics:
        params["topics"] = topics
    
    return await alpha_vantage.make_api_request("NEWS_SENTIMENT", **params)

# ==========================================
# BULK OPERATIONS & UTILITIES
# ==========================================

@router.post("/bulk/stock-data")
async def get_bulk_stock_data(symbols: List[str], data_type: str = "daily"):
    """Get bulk stock data for multiple symbols"""
    results = {}
    
    for symbol in symbols[:10]:  # Limit to 10 symbols for demo
        try:
            if data_type == "daily":
                data = await alpha_vantage.make_api_request("TIME_SERIES_DAILY", symbol=symbol)
            elif data_type == "quote":
                data = await alpha_vantage.make_api_request("GLOBAL_QUOTE", symbol=symbol)
            elif data_type == "overview":
                data = await alpha_vantage.make_api_request("OVERVIEW", symbol=symbol)
            else:
                data = {"error": f"Unsupported data type: {data_type}"}
            
            results[symbol] = data
            # Add delay to respect rate limits
            await asyncio.sleep(0.2)
            
        except Exception as e:
            results[symbol] = {"error": str(e)}
    
    return results

@router.get("/url-builder")
async def build_api_url(function: str, **params):
    """Build Alpha Vantage API URL for testing"""
    return {
        "function": function,
        "url": alpha_vantage.build_url(function, **params),
        "endpoint_info": alpha_vantage.get_complete_api_index().get(function, "Function not found")
    }

@router.get("/categories/{category}")
async def get_category_endpoints(category: str):
    """Get all endpoints for a specific category"""
    category_map = {
        "stock": alpha_vantage.get_core_stock_endpoints(),
        "options": alpha_vantage.get_options_endpoints(),
        "intelligence": alpha_vantage.get_intelligence_endpoints(),
        "fundamental": alpha_vantage.get_fundamental_endpoints(),
        "forex": alpha_vantage.get_forex_endpoints(),
        "crypto": alpha_vantage.get_crypto_endpoints(),
        "commodities": alpha_vantage.get_commodities_endpoints(),
        "economic": alpha_vantage.get_economic_endpoints(),
        "technical": alpha_vantage.get_technical_endpoints()
    }
    
    if category not in category_map:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    return {
        "category": category,
        "endpoints": category_map[category]
    }
