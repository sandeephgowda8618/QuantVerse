"""
Configuration for PostgreSQL to ChromaDB Pipeline
"""

# ChromaDB Configuration
CHROMA_CONFIG = {
    "persist_directory": "./vector_db",
    "collection_name": "urisk_chunks",
    "auth_provider": "chromadb.auth.basic.BasicAuthClientProvider",
    "auth_credentials": "admin:admin"  # Change in production
}

# Embedding Configuration
EMBEDDING_CONFIG = {
    "model_name": "all-MiniLM-L6-v2",  # Fast, good quality, 384 dimensions
    # Alternative models:
    # "all-mpnet-base-v2"  # Better quality, slower, 768 dimensions  
    # "multi-qa-MiniLM-L6-cos-v1"  # Optimized for Q&A
    "batch_size": 256,  # Increased for faster bulk processing
    "max_seq_length": 512,
    "device": "auto"  # "cuda", "cpu", or "auto"
}

# Ingestion Pipeline Configuration (PostgreSQL → ChromaDB)
PIPELINE_CONFIG = {
    "batch_size": 256,  # Increased for faster bulk processing
    "sync_limit_per_run": 5000,  # Higher batch size for full ingestion
    "process_all_historical_data": True,  # Don't filter by time for ingestion
    "chunk_overlap": 50,  # Character overlap for text chunking
    "max_chunk_size": 1000,  # Maximum characters per chunk
    "parallel_processing": False,  # Set to True for faster ingestion
    "memory_efficient_mode": True  # Process in batches to save memory
}

# Data Source Configurations
DATA_SOURCES = {
    "alpha_vantage_data": {
        "enabled": True,
        "batch_size": 1000,
        "priority": 1,
        "endpoints_to_sync": [
            "RSI", "EMA", "BBANDS", "MFI", "ADX", "TRIX",  # Technical indicators
            "OVERVIEW", "EARNINGS", "BALANCE_SHEET", "CASH_FLOW",  # Fundamentals
            "TIME_SERIES_DAILY", "TIME_SERIES_WEEKLY", "TIME_SERIES_MONTHLY",  # Time series
            "NEWS_SENTIMENT", "TOP_GAINERS_LOSERS", "MARKET_STATUS"  # Market intelligence
        ],
        "exclude_endpoints": [
            "RAW_DATA", "HISTORICAL_BACKFILL"  # Skip noisy data
        ]
    },
    "news_headlines": {
        "enabled": True,
        "batch_size": 500,
        "priority": 2,
        "include_sentiment": True
    },
    "anomalies": {
        "enabled": True,
        "batch_size": 200,
        "priority": 3,
        "severity_filter": ["medium", "high"]  # Only sync important anomalies
    },
    "market_prices": {
        "enabled": False,  # Too granular, only sync summaries
        "batch_size": 1000,
        "priority": 4
    }
}

# Metadata Enhancement
METADATA_CONFIG = {
    "known_tickers": {
        # Stock mappings
        "AAPL": {"asset_type": "stock", "sector": "technology"},
        "MSFT": {"asset_type": "stock", "sector": "technology"},
        "NVDA": {"asset_type": "stock", "sector": "technology"},
        "GOOGL": {"asset_type": "stock", "sector": "technology"},
        "AMZN": {"asset_type": "stock", "sector": "technology"},
        "TSLA": {"asset_type": "stock", "sector": "automotive"},
        "META": {"asset_type": "stock", "sector": "technology"},
        
        # Crypto mappings
        "BTC": {"asset_type": "crypto", "sector": "cryptocurrency"},
        "ETH": {"asset_type": "crypto", "sector": "cryptocurrency"},
        "DOGE": {"asset_type": "crypto", "sector": "cryptocurrency"},
        
        # Index mappings
        "SPY": {"asset_type": "index", "sector": "broad_market"},
        "QQQ": {"asset_type": "index", "sector": "technology"},
        "DIA": {"asset_type": "index", "sector": "broad_market"}
    },
    
    "risk_type_mapping": {
        # Technical indicators
        "RSI": "technical",
        "EMA": "technical", 
        "BBANDS": "technical",
        "MFI": "technical",
        "ADX": "technical",
        "TRIX": "technical",
        
        # Fundamental data
        "OVERVIEW": "fundamental",
        "EARNINGS": "fundamental",
        "BALANCE_SHEET": "fundamental",
        "CASH_FLOW": "fundamental",
        
        # Market data
        "TIME_SERIES_DAILY": "market",
        "TIME_SERIES_WEEKLY": "market",
        "TIME_SERIES_MONTHLY": "market",
        
        # Sentiment and news
        "NEWS_SENTIMENT": "sentiment",
        "NEWS": "sentiment",
        
        # Market intelligence
        "TOP_GAINERS_LOSERS": "macro",
        "MARKET_STATUS": "macro"
    },
    
    "severity_calculation": {
        "high_impact_endpoints": ["EARNINGS", "NEWS_SENTIMENT", "ANOMALIES"],
        "rsi_thresholds": {"overbought": 70, "oversold": 30},
        "sentiment_thresholds": {"positive": 0.1, "negative": -0.1}
    }
}

# Scheduling Configuration  
SCHEDULE_CONFIG = {
    "modes": {
        "continuous": {
            "enabled": False,
            "interval_minutes": 30,
            "description": "Run every 30 minutes"
        },
        "hourly": {
            "enabled": True,
            "interval_minutes": 60,
            "description": "Run every hour"
        },
        "daily": {
            "enabled": False,
            "cron": "0 2 * * *",  # 2 AM daily
            "description": "Run once daily at 2 AM"
        },
        "on_demand": {
            "enabled": True,
            "description": "Manual trigger via API or script"
        }
    },
    "max_runtime_minutes": 120,  # Kill after 2 hours
    "retry_failed_batches": True,
    "retry_max_attempts": 3
}

# Monitoring and Logging
MONITORING_CONFIG = {
    "log_level": "INFO",
    "log_to_file": True,
    "log_file": "postgres_to_vectordb.log",
    "metrics": {
        "track_processing_speed": True,
        "track_error_rates": True,
        "track_vector_store_growth": True
    },
    "alerts": {
        "slow_processing_threshold_seconds": 300,
        "high_error_rate_threshold": 0.1,  # 10% error rate
        "email_notifications": False,  # Set to True and configure SMTP
        "slack_notifications": False   # Set to True and configure webhook
    }
}

# Performance Optimization
PERFORMANCE_CONFIG = {
    "postgres": {
        "connection_pool_size": 10,
        "max_connections": 20,
        "query_timeout_seconds": 60
    },
    "chromadb": {
        "batch_upsert_size": 200,  # Increased for faster bulk inserts
        "enable_persistence": True,
        "memory_optimization": True
    },
    "embedding": {
        "batch_processing": True,
        "parallel_processing": False,  # Set to True if you have multiple GPUs
        "memory_efficient_mode": True
    }
}
