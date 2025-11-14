#!/usr/bin/env python3
"""
Configuration module for the data collection pipeline
Loads environment variables and defines constants
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

# Load environment from parent directory .env file
from dotenv import load_dotenv

# Load .env from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = os.getenv('DATABASE_URL', 'postgresql://postgres:sandeep@localhost:5432/quant_verse')
    host: str = os.getenv('POSTGRES_HOST', 'localhost')
    port: int = int(os.getenv('POSTGRES_PORT', '5432'))
    database: str = os.getenv('POSTGRES_DB', 'quant_verse')
    user: str = os.getenv('POSTGRES_USER', 'postgres')
    password: str = os.getenv('POSTGRES_PASSWORD', 'sandeep')

@dataclass
class VectorDBConfig:
    """Vector database configuration"""
    host: str = os.getenv('CHROMA_HOST', 'localhost')
    port: int = int(os.getenv('CHROMA_PORT', '8000'))
    collection_name: str = os.getenv('CHROMA_COLLECTION_NAME', 'urisk_chunks')

@dataclass
class APIConfig:
    """API configurations for various providers"""
    # Tiingo
    tiingo_api_key: str = os.getenv('TIINGO_API_KEY', '')
    tiingo_base_url: str = os.getenv('TIINGO_BASE_URL', 'https://api.tiingo.com')
    
    # Finnhub
    finnhub_api_key: str = os.getenv('FINNHUB_API_KEY', '')
    finnhub_base_url: str = os.getenv('FINNHUB_BASE_URL', 'https://finnhub.io/api/v1')
    finnhub_websocket_url: str = os.getenv('FINNHUB_WEBSOCKET_URL', 'wss://ws.finnhub.io')
    
    # Perplexity
    perplexity_api_key: str = os.getenv('PERPLEXITY_API_KEY', '')
    perplexity_base_url: str = os.getenv('PERPLEXITY_BASE_URL', 'https://api.perplexity.ai')
    
    # TwelveData
    twelvedata_api_key: str = os.getenv('TWELVEDATA_API_KEY', '')
    
    # Polygon
    polygon_api_key: str = os.getenv('POLYGON_API_KEY', '')
    polygon_base_url: str = 'https://api.polygon.io'
    
    # Alpaca
    alpaca_api_key: str = os.getenv('ALPACA_API_KEY', '')
    alpaca_secret_key: str = os.getenv('ALPACA_SECRET_KEY', '')
    alpaca_base_url: str = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    alpaca_data_url: str = os.getenv('ALPACA_DATA_URL', 'https://data.alpaca.markets')
    
    # Alpha Vantage (with key rotation)
    alpha_vantage_keys: Optional[List[str]] = None
    alpha_vantage_rate_limit: int = int(os.getenv('ALPHA_VANTAGE_RATE_LIMIT', '5'))
    
    def __post_init__(self):
        """Load Alpha Vantage keys after initialization"""
        if self.alpha_vantage_keys is None:
            self.alpha_vantage_keys = []
            for i in range(1, 82):  # Load all available keys
                key = os.getenv(f'ALPHA_VANTAGE_API_KEY_{i}')
                if key:
                    self.alpha_vantage_keys.append(key)

@dataclass
class SchedulerConfig:
    """Scheduler configuration"""
    market_data_interval: int = int(os.getenv('MARKET_DATA_INTERVAL', '300'))  # 5 minutes
    news_data_interval: int = int(os.getenv('NEWS_DATA_INTERVAL', '600'))      # 10 minutes
    regulatory_interval: int = int(os.getenv('REGULATORY_INTERVAL', '43200'))  # 12 hours
    anomaly_detection_interval: int = int(os.getenv('ANOMALY_DETECTION_INTERVAL', '600'))  # 10 minutes

@dataclass
class Config:
    """Main configuration class"""
    database: DatabaseConfig
    vector_db: VectorDBConfig
    api: APIConfig
    scheduler: SchedulerConfig
    
    # General settings
    environment: str = os.getenv('ENVIRONMENT', 'development')
    debug: bool = os.getenv('DEBUG', 'true').lower() == 'true'
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Logging configuration
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @property
    def log_dir(self) -> str:
        """Get the logs directory path"""
        return os.path.join(os.path.dirname(__file__), 'logs')
    
    def get_log_file_path(self, log_type: str = 'pipeline') -> str:
        """Get timestamped log file path in the logs directory"""
        os.makedirs(self.log_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return os.path.join(self.log_dir, f'{log_type}_{timestamp}.log')
    
    # Rate limiting
    max_concurrent_requests: int = int(os.getenv('MAX_CONCURRENT_REQUESTS', '3'))
    request_timeout: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
    retry_attempts: int = int(os.getenv('RETRY_ATTEMPTS', '3'))
    backoff_factor: int = int(os.getenv('BACKOFF_FACTOR', '2'))
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.vector_db = VectorDBConfig()
        self.api = APIConfig()
        self.scheduler = SchedulerConfig()

# Constants
PRIORITY_TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'AVGO',
    'JPM', 'BAC', 'GS', 'WFC', 'MS',
    'XOM', 'CVX', 'COP',
    'BA', 'LMT', 'CAT', 'GE',
    'WMT', 'COST', 'MCD', 'HD', 'SBUX',
    'JNJ', 'PFE', 'MRK',
    'SPY', 'QQQ', 'IWM',
    'BTC-USD', 'ETH-USD'
]

# API call budgets per provider
API_CALL_BUDGETS = {
    'yfinance': 10,
    'tiingo': 10,
    'finnhub': 10,
    'perplexity': 3,  # Expensive
    'alpha_vantage': 10,
    'polygon': 10,
    'alpaca': 10,
    'sec': 6,
    'reddit': 10,
    'coinbase': 3,
    'binance': 3
}

# Table mappings
TABLE_MAPPINGS = {
    'market_data': ['market_prices', 'assets'],
    'news': ['news_headlines', 'news_sentiment'],
    'regulatory': ['regulatory_events'],
    'infrastructure': ['infra_incidents', 'infrastructure_status'],
    'anomalies': ['anomalies', 'price_gaps', 'alerts'],
    'technical': ['alpha_vantage_data', 'technical_indicators']
}

# Create global config instance
config = Config()
