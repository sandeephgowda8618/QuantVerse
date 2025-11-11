"""
Logging utilities for the uRISK system.
Provides structured logging with configurable levels and formats.
"""

import logging
import sys
from typing import Optional, List
from datetime import datetime

from ..config.settings import settings

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Args:
        name: Logger name (usually __name__)
        level: Log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set log level
    log_level = level or settings.LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger

def log_collection_start(collector_name: str, tickers: Optional[List[str]] = None):
    """Log the start of a data collection process."""
    logger = logging.getLogger(collector_name)
    ticker_info = f" for {len(tickers)} tickers" if tickers else ""
    logger.info(f"Starting {collector_name} data collection{ticker_info}")

def log_collection_end(collector_name: str, records_count: int, duration: float, errors: Optional[List[str]] = None):
    """Log the end of a data collection process."""
    logger = logging.getLogger(collector_name)
    error_info = f", {len(errors)} errors" if errors else ", no errors"
    logger.info(f"Completed {collector_name} data collection: "
               f"{records_count} records in {duration:.2f}s{error_info}")

def log_api_error(api_name: str, endpoint: str, error: Exception, ticker: Optional[str] = None):
    """Log API-specific errors with context."""
    logger = logging.getLogger(f"api.{api_name}")
    ticker_info = f" for {ticker}" if ticker else ""
    logger.error(f"API error in {endpoint}{ticker_info}: {error}")

def log_database_operation(operation: str, table: str, records_count: Optional[int] = None, error: Optional[Exception] = None):
    """Log database operations."""
    logger = logging.getLogger("database")
    if error:
        logger.error(f"Database {operation} failed on {table}: {error}")
    else:
        record_info = f" ({records_count} records)" if records_count is not None else ""
        logger.info(f"Database {operation} successful on {table}{record_info}")

# Global logger for general use
default_logger = setup_logger("urisk")