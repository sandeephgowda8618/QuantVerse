"""
Configuration settings for the uRISK system.
Loads environment variables and API keys.
DO NOT COMMIT SECRETS TO VERSION CONTROL.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/urisk_core")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "urisk_core")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "username")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    
    # Redis Configuration (disabled - using no-cache implementation)
    # REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    # REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    # REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    # REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # Vector Database Configuration
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8000"))
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "urisk_chunks")
    
    # Market Data APIs
    YFINANCE_ENABLED: bool = os.getenv("YFINANCE_ENABLED", "true").lower() == "true"
    TIINGO_API_KEY: str = os.getenv("TIINGO_API_KEY", "")
    TIINGO_BASE_URL: str = os.getenv("TIINGO_BASE_URL", "https://api.tiingo.com")
    
    # News & Market Data APIs
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY", "")
    FINNHUB_BASE_URL: str = os.getenv("FINNHUB_BASE_URL", "https://finnhub.io/api/v1")
    FINNHUB_WEBSOCKET_URL: str = os.getenv("FINNHUB_WEBSOCKET_URL", "wss://ws.finnhub.io")
    
    # Perplexity AI
    PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY", "")
    PERPLEXITY_BASE_URL: str = os.getenv("PERPLEXITY_BASE_URL", "https://api.perplexity.ai")
    
    # Alpha Vantage API - Multiple Keys for Higher Rate Limits
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY") or os.getenv("ALPHA_VANTAGE_API_KEY_1", "")
    ALPHA_VANTAGE_BASE_URL: str = os.getenv("ALPHA_VANTAGE_BASE_URL", "https://www.alphavantage.co/query")
    
    # Alpha Vantage Multiple Keys for Rate Limiting Management (81 total keys)
    ALPHA_VANTAGE_API_KEYS: list = [
        os.getenv("ALPHA_VANTAGE_API_KEY_1", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_2", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_3", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_4", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_5", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_6", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_7", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_8", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_9", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_10", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_11", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_12", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_13", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_14", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_15", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_16", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_17", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_18", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_19", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_20", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_21", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_22", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_23", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_24", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_25", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_26", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_27", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_28", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_29", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_30", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_31", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_32", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_33", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_34", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_35", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_36", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_37", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_38", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_39", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_40", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_41", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_42", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_43", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_44", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_45", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_46", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_47", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_48", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_49", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_50", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_51", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_52", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_53", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_54", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_55", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_56", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_57", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_58", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_59", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_60", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_61", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_62", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_63", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_64", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_65", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_66", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_67", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_68", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_69", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_70", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_71", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_72", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_73", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_74", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_75", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_76", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_77", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_78", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_79", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_80", ""),
        os.getenv("ALPHA_VANTAGE_API_KEY_81", "")
    ]
    
    # Options Data APIs (for Member-1)
    POLYGON_API_KEY: str = os.getenv("POLYGON_API_KEY", "")
    
    # Trading Data APIs - Multiple Provider Support
    # Alpaca Markets
    ALPACA_API_KEY: str = os.getenv("ALPACA_API_KEY", "")
    ALPACA_SECRET_KEY: str = os.getenv("ALPACA_SECRET_KEY", "")
    ALPACA_BASE_URL: str = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    ALPACA_DATA_URL: str = os.getenv("ALPACA_DATA_URL", "https://data.alpaca.markets")
    
    # TD Ameritrade
    TD_AMERITRADE_API_KEY: str = os.getenv("TD_AMERITRADE_API_KEY", "")
    TD_AMERITRADE_BASE_URL: str = os.getenv("TD_AMERITRADE_BASE_URL", "https://api.tdameritrade.com/v1")
    
    # Interactive Brokers
    IBKR_HOST: str = os.getenv("IBKR_HOST", "127.0.0.1")
    IBKR_PORT: int = int(os.getenv("IBKR_PORT", "7497"))
    IBKR_CLIENT_ID: int = int(os.getenv("IBKR_CLIENT_ID", "1"))
    
    # Tradier (Original - keeping as fallback)
    TRADIER_API_KEY: str = os.getenv("TRADIER_API_KEY", "")
    TRADIER_BASE_URL: str = os.getenv("TRADIER_BASE_URL", "https://api.tradier.com/v1")
    
    # Yahoo Finance
    YAHOO_FINANCE_ENABLED: bool = os.getenv("YAHOO_FINANCE_ENABLED", "true").lower() == "true"
    
    # Regulatory Data Sources
    SEC_EDGAR_USER_AGENT: str = os.getenv("SEC_EDGAR_USER_AGENT", "uRISK system urisk@company.com")
    SEC_BASE_URL: str = os.getenv("SEC_BASE_URL", "https://www.sec.gov/Archives/edgar")
    RBI_RSS_URL: str = os.getenv("RBI_RSS_URL", "https://www.rbi.org.in/Scripts/RSS/PressReleases.xml")
    FED_RSS_URL: str = os.getenv("FED_RSS_URL", "https://www.federalreserve.gov/feeds/press_all.xml")
    
    # Infrastructure Status APIs
    COINBASE_STATUS_URL: str = os.getenv("COINBASE_STATUS_URL", "https://status.coinbase.com/api/v2/status.json")
    BINANCE_STATUS_URL: str = os.getenv("BINANCE_STATUS_URL", "https://www.binance.com/bapi/system/v1/public/system/status")
    SOLANA_RPC_URL: str = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
    
    # ML Model Serving
    ANOMALY_MODEL_URL: str = os.getenv("ANOMALY_MODEL_URL", "http://localhost:8001")
    SENTIMENT_MODEL_URL: str = os.getenv("SENTIMENT_MODEL_URL", "http://localhost:8002")
    FORECASTER_MODEL_URL: str = os.getenv("FORECASTER_MODEL_URL", "http://localhost:8003")
    
    # LLM Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    LLAMA_MODEL_PATH: str = os.getenv("LLAMA_MODEL_PATH", "./models/llama-2-7b-chat")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Ollama LLM Configuration
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
    OLLAMA_KEEP_ALIVE: str = os.getenv("OLLAMA_KEEP_ALIVE", "20m")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "35"))  # seconds
    OLLAMA_MAX_RETRIES: int = int(os.getenv("OLLAMA_MAX_RETRIES", "2"))
    OLLAMA_AUTO_START: bool = os.getenv("OLLAMA_AUTO_START", "true").lower() == "true"
    
    # Scheduler Configuration
    MARKET_DATA_INTERVAL: int = int(os.getenv("MARKET_DATA_INTERVAL", "300"))  # 5 minutes
    NEWS_DATA_INTERVAL: int = int(os.getenv("NEWS_DATA_INTERVAL", "600"))      # 10 minutes
    REGULATORY_INTERVAL: int = int(os.getenv("REGULATORY_INTERVAL", "43200"))   # 12 hours
    ANOMALY_DETECTION_INTERVAL: int = int(os.getenv("ANOMALY_DETECTION_INTERVAL", "600"))  # 10 minutes
    
    # Alert Configuration
    ALERT_EMAIL_ENABLED: bool = os.getenv("ALERT_EMAIL_ENABLED", "false").lower() == "true"
    ALERT_EMAIL_SMTP_HOST: str = os.getenv("ALERT_EMAIL_SMTP_HOST", "smtp.gmail.com")
    ALERT_EMAIL_SMTP_PORT: int = int(os.getenv("ALERT_EMAIL_SMTP_PORT", "587"))
    ALERT_EMAIL_FROM: str = os.getenv("ALERT_EMAIL_FROM", "alerts@yourcompany.com")
    ALERT_EMAIL_PASSWORD: str = os.getenv("ALERT_EMAIL_PASSWORD", "")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    INTERNAL_API_KEY: str = os.getenv("INTERNAL_API_KEY", "internal-api-key-change-in-production")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def validate_required_keys(self) -> list[str]:
        """Validate that required API keys are present."""
        missing_keys = []
        
        required_keys = [
            ("ALPHA_VANTAGE_API_KEY", self.ALPHA_VANTAGE_API_KEY),
            ("TIINGO_API_KEY", self.TIINGO_API_KEY),
            ("FINNHUB_API_KEY", self.FINNHUB_API_KEY),
            ("PERPLEXITY_API_KEY", self.PERPLEXITY_API_KEY),
        ]
        
        for key_name, key_value in required_keys:
            if not key_value or key_value == "":
                missing_keys.append(key_name)
        
        return missing_keys

# Global settings instance
settings = Settings()

# Tracked assets configuration
TRACKED_ASSETS = {
    "crypto": ["BTC", "ETH", "SOL", "ADA", "DOT"],
    "stocks": ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "NVDA"],
    "indices": ["SPY", "QQQ", "NIFTY", "NASDAQ"],
    "fx": ["EURUSD", "GBPUSD", "USDJPY"]
}
