"""
Scheduler configuration for data collection tasks.
Defines cron schedules and polling frequencies for different data sources.
"""

from typing import Dict, Any
from .settings import settings

# Task configurations with frequencies and settings
SCHEDULER_CONFIG = {
    "market_data": {
        "interval": settings.MARKET_DATA_INTERVAL,  # 5 minutes
        "enabled": True,
        "sources": ["yfinance", "tiingo"],
        "max_retries": 3,
        "timeout": 30
    },
    
    "news_data": {
        "interval": settings.NEWS_DATA_INTERVAL,  # 10 minutes  
        "enabled": True,
        "sources": ["finnhub", "perplexity"],
        "max_retries": 2,
        "timeout": 45
    },
    
    "regulatory_data": {
        "interval": settings.REGULATORY_INTERVAL,  # 12 hours
        "enabled": True,
        "sources": ["sec", "rbi", "fed"],
        "max_retries": 2,
        "timeout": 60
    },
    
    "infrastructure_monitoring": {
        "interval": 300,  # 5 minutes
        "enabled": True,
        "sources": ["coinbase", "binance", "solana"],
        "max_retries": 2,
        "timeout": 15
    },
    
    "options_flow": {
        "interval": 600,  # 10 minutes
        "enabled": True,
        "sources": ["polygon", "tradier"],
        "max_retries": 2,
        "timeout": 30
    },
    
    "anomaly_detection": {
        "interval": settings.ANOMALY_DETECTION_INTERVAL,  # 10 minutes
        "enabled": True,
        "depends_on": ["market_data"],
        "max_retries": 1,
        "timeout": 120
    },
    
    "sentiment_analysis": {
        "interval": 60,  # 1 minute (real-time processing)
        "enabled": True,
        "depends_on": ["news_data"],
        "max_retries": 1,
        "timeout": 30
    },
    
    "price_gap_detection": {
        "interval": 86400,  # Daily at market open
        "enabled": True,
        "cron": "0 9 * * 1-5",  # 9 AM weekdays
        "depends_on": ["market_data"],
        "max_retries": 1,
        "timeout": 60
    },
    
    "alert_engine": {
        "interval": 60,  # 1 minute
        "enabled": True,
        "depends_on": ["anomaly_detection", "sentiment_analysis"],
        "max_retries": 1,
        "timeout": 10
    }
}

# Priority levels for task execution
TASK_PRIORITIES = {
    "infrastructure_monitoring": 1,  # Highest priority
    "market_data": 2,
    "news_data": 3, 
    "sentiment_analysis": 4,
    "anomaly_detection": 5,
    "alert_engine": 6,
    "options_flow": 7,
    "regulatory_data": 8,
    "price_gap_detection": 9  # Lowest priority
}

# Market hours configuration
MARKET_HOURS = {
    "NYSE": {
        "open": "09:30",
        "close": "16:00",
        "timezone": "America/New_York",
        "weekdays_only": True
    },
    "NASDAQ": {
        "open": "09:30", 
        "close": "16:00",
        "timezone": "America/New_York",
        "weekdays_only": True
    },
    "NSE": {  # National Stock Exchange of India
        "open": "09:15",
        "close": "15:30", 
        "timezone": "Asia/Kolkata",
        "weekdays_only": True
    },
    "CRYPTO": {
        "open": "00:00",
        "close": "23:59",
        "timezone": "UTC",
        "weekdays_only": False  # 24/7 trading
    }
}

def get_task_config(task_name: str) -> Dict[str, Any]:
    """Get configuration for a specific task."""
    return SCHEDULER_CONFIG.get(task_name, {})

def is_market_open(market: str = "NYSE") -> bool:
    """Check if a specific market is currently open."""
    from datetime import datetime
    import pytz
    
    market_config = MARKET_HOURS.get(market, {})
    if not market_config:
        return True  # Default to always open if config not found
    
    # Get current time in market timezone
    tz = pytz.timezone(market_config["timezone"])
    now = datetime.now(tz)
    
    # Check if weekday trading only
    if market_config.get("weekdays_only", True) and now.weekday() >= 5:
        return False
    
    # Check time bounds
    open_time = datetime.strptime(market_config["open"], "%H:%M").time()
    close_time = datetime.strptime(market_config["close"], "%H:%M").time()
    current_time = now.time()
    
    return open_time <= current_time <= close_time
