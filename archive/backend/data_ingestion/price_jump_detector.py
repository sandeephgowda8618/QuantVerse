"""
Price jump detection for sudden market move analysis.
Monitors minute-level price changes and detects significant movements.
Used primarily by Member-2 Sudden Move Explainer.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np

from ..config.settings import settings, TRACKED_ASSETS
from ..db.postgres_handler import db, insert_anomaly
from ..utils.logging_utils import setup_logger

logger = setup_logger(__name__)

class PriceJumpDetector:
    """Detects sudden price movements and classifies their significance."""
    
    def __init__(self):
        # Configurable thresholds for different asset types
        self.price_jump_thresholds = {
            'crypto': {
                'minor': 0.03,    # 3%
                'medium': 0.05,   # 5%
                'major': 0.10,    # 10%
                'extreme': 0.20   # 20%
            },
            'stock': {
                'minor': 0.02,    # 2%
                'medium': 0.04,   # 4%
                'major': 0.08,    # 8%
                'extreme': 0.15   # 15%
            },
            'index': {
                'minor': 0.01,    # 1%
                'medium': 0.02,   # 2%
                'major': 0.04,    # 4%
                'extreme': 0.08   # 8%
            },
            'fx': {
                'minor': 0.005,   # 0.5%
                'medium': 0.01,   # 1%
                'major': 0.02,    # 2%
                'extreme': 0.05   # 5%
            }
        }
        
        # Time windows for analysis
        self.analysis_windows = [
            ('1min', 1),
            ('5min', 5),
            ('15min', 15),
            ('1hour', 60)
        ]
    
    def get_asset_type(self, ticker: str) -> str:
        """Determine asset type for a ticker."""
        for asset_type, tickers in TRACKED_ASSETS.items():
            if ticker in tickers:
                if asset_type == 'crypto':
                    return 'crypto'
                elif asset_type == 'stocks':
                    return 'stock'
                elif asset_type == 'indices':
                    return 'index'
                elif asset_type == 'fx':
                    return 'fx'
        
        # Default to stock if not found
        return 'stock'
    
    def get_recent_price_data(self, ticker: str, hours_back: int = 24) -> pd.DataFrame:
        """
        Retrieve recent price data for a ticker.
        
        Args:
            ticker: Ticker symbol
            hours_back: Number of hours of historical data to retrieve
        
        Returns:
            DataFrame with price data sorted by timestamp
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            query = """
                SELECT timestamp, open, high, low, close, volume, source
                FROM market_prices 
                WHERE ticker = %s 
                AND timestamp >= %s 
                ORDER BY timestamp ASC
            """
            
            params = (ticker, cutoff_time.isoformat())
            results = db.execute_query(query, params)
            
            if not results:
                logger.warning(f"No recent price data found for {ticker}")
                return pd.DataFrame()
            
            df = pd.DataFrame(results)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            logger.debug(f"Retrieved {len(df)} price records for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to retrieve price data for {ticker}: {e}")
            return pd.DataFrame()
    
    def calculate_price_changes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate price changes over different time windows.
        
        Args:
            df: DataFrame with price data
        
        Returns:
            DataFrame with additional price change columns
        """
        if df.empty or 'close' not in df.columns:
            return df
        
        try:
            df = df.copy()
            
            # Calculate percentage changes for different windows
            for window_name, minutes in self.analysis_windows:
                # Calculate rolling price change
                periods = max(1, minutes)  # At least 1 period
                
                if len(df) > periods:
                    df[f'pct_change_{window_name}'] = df['close'].pct_change(periods=periods)
                    df[f'abs_change_{window_name}'] = df['close'].diff(periods=periods)
                else:
                    df[f'pct_change_{window_name}'] = 0.0
                    df[f'abs_change_{window_name}'] = 0.0
            
            # Calculate volume-weighted changes
            if 'volume' in df.columns:
                df['volume_ma'] = df['volume'].rolling(window=10, min_periods=1).mean()
                df['volume_spike'] = df['volume'] / df['volume_ma']
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to calculate price changes: {e}")
            return df
    
    def detect_price_jumps(self, df: pd.DataFrame, ticker: str) -> List[Dict[str, Any]]:
        """
        Detect significant price jumps in the data.
        
        Args:
            df: DataFrame with price data and calculated changes
            ticker: Ticker symbol
        
        Returns:
            List of detected price jump anomalies
        """
        if df.empty:
            return []
        
        asset_type = self.get_asset_type(ticker)
        thresholds = self.price_jump_thresholds.get(asset_type, self.price_jump_thresholds['stock'])
        
        jumps = []
        
        try:
            # Check each time window for significant jumps
            for window_name, minutes in self.analysis_windows:
                pct_change_col = f'pct_change_{window_name}'
                
                if pct_change_col not in df.columns:
                    continue
                
                # Find significant movements
                for _, row in df.iterrows():
                    try:
                        pct_change = row[pct_change_col]
                        
                        if pd.isna(pct_change) or abs(pct_change) == 0:
                            continue
                        
                        abs_pct_change = abs(pct_change)
                        
                        # Classify jump severity
                        severity = None
                        severity_level = None
                        
                        if abs_pct_change >= thresholds['extreme']:
                            severity = 'critical'
                            severity_level = 'extreme'
                        elif abs_pct_change >= thresholds['major']:
                            severity = 'high'
                            severity_level = 'major'
                        elif abs_pct_change >= thresholds['medium']:
                            severity = 'medium'
                            severity_level = 'medium'
                        elif abs_pct_change >= thresholds['minor']:
                            severity = 'low'
                            severity_level = 'minor'
                        
                        if severity:
                            # Calculate direction
                            direction = 'up' if pct_change > 0 else 'down'
                            
                            # Check for volume confirmation
                            volume_confirmation = False
                            if 'volume_spike' in df.columns:
                                volume_spike = row.get('volume_spike', 1.0)
                                volume_confirmation = volume_spike > 1.5  # 50% above average
                            
                            # Create jump record
                            jump = {
                                'ticker': ticker,
                                'metric': 'price_jump',
                                'anomaly_score': min(abs_pct_change / thresholds['extreme'], 1.0),
                                'severity': severity,
                                'explanation': (
                                    f'{severity_level.title() if severity_level else "Unknown"} {direction} move: '
                                    f'{pct_change*100:+.2f}% in {window_name}'
                                    f'{" with volume spike" if volume_confirmation else ""}'
                                ),
                                'timestamp': row['timestamp'],
                                'details': {
                                    'window': window_name,
                                    'pct_change': pct_change,
                                    'abs_pct_change': abs_pct_change,
                                    'direction': direction,
                                    'severity_level': severity_level,
                                    'price_before': row['close'] / (1 + pct_change) if pct_change != -1 else None,
                                    'price_after': row['close'],
                                    'volume': row.get('volume'),
                                    'volume_spike': row.get('volume_spike', 1.0),
                                    'volume_confirmation': volume_confirmation,
                                    'asset_type': asset_type
                                }
                            }
                            
                            jumps.append(jump)
                            
                    except Exception as e:
                        logger.warning(f"Failed to process row for jump detection: {e}")
                        continue
            
            # Remove duplicates (same timestamp, different windows)
            unique_jumps = self.deduplicate_jumps(jumps)
            
            logger.info(f"Detected {len(unique_jumps)} price jumps for {ticker}")
            return unique_jumps
            
        except Exception as e:
            logger.error(f"Failed to detect price jumps for {ticker}: {e}")
            return []
    
    def deduplicate_jumps(self, jumps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate jumps (same timestamp, keep highest severity).
        
        Args:
            jumps: List of jump anomalies
        
        Returns:
            Deduplicated list of jumps
        """
        if not jumps:
            return []
        
        # Group by timestamp
        timestamp_groups = {}
        
        for jump in jumps:
            timestamp = jump['timestamp']
            
            if timestamp not in timestamp_groups:
                timestamp_groups[timestamp] = []
            
            timestamp_groups[timestamp].append(jump)
        
        # Keep highest severity jump for each timestamp
        severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        
        unique_jumps = []
        
        for timestamp, group in timestamp_groups.items():
            if len(group) == 1:
                unique_jumps.append(group[0])
            else:
                # Sort by severity and anomaly score
                best_jump = max(
                    group,
                    key=lambda x: (
                        severity_order.get(x['severity'], 0),
                        x['anomaly_score']
                    )
                )
                unique_jumps.append(best_jump)
        
        return unique_jumps
    
    def analyze_jump_context(self, jump: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze the context around a price jump for additional insights.
        
        Args:
            jump: Jump anomaly record
            df: Price data DataFrame
        
        Returns:
            Jump record with additional context
        """
        try:
            jump_timestamp = jump['timestamp']
            
            # Find the row corresponding to this jump
            jump_row_idx = df[df['timestamp'] == jump_timestamp].index
            
            if len(jump_row_idx) == 0:
                return jump
            
            jump_idx = jump_row_idx[0]
            
            # Analyze pre-jump trend
            pre_jump_window = 10  # Look at 10 periods before
            start_idx = max(0, jump_idx - pre_jump_window)
            
            if start_idx < jump_idx:
                pre_jump_data = df.iloc[start_idx:jump_idx]
                
                if len(pre_jump_data) > 1:
                    pre_jump_trend = pre_jump_data['close'].pct_change().mean()
                    pre_jump_volatility = pre_jump_data['close'].pct_change().std()
                    
                    # Classify pre-jump behavior
                    trend_description = 'neutral'
                    if pre_jump_trend > 0.01:
                        trend_description = 'uptrending'
                    elif pre_jump_trend < -0.01:
                        trend_description = 'downtrending'
                    
                    volatility_description = 'normal'
                    if pre_jump_volatility > 0.02:
                        volatility_description = 'high'
                    elif pre_jump_volatility < 0.005:
                        volatility_description = 'low'
                    
                    # Add context to jump details
                    jump['details']['pre_jump_context'] = {
                        'trend': trend_description,
                        'volatility': volatility_description,
                        'trend_value': pre_jump_trend,
                        'volatility_value': pre_jump_volatility
                    }
            
            return jump
            
        except Exception as e:
            logger.warning(f"Failed to analyze jump context: {e}")
            return jump
    
    def store_price_jumps(self, jumps: List[Dict[str, Any]]) -> int:
        """Store price jump anomalies in the database."""
        if not jumps:
            return 0
        
        stored_count = 0
        
        for jump in jumps:
            try:
                anomaly_id = insert_anomaly(
                    ticker=jump['ticker'],
                    metric=jump['metric'],
                    anomaly_score=jump['anomaly_score'],
                    severity=jump['severity'],
                    explanation=jump['explanation'],
                    timestamp=jump['timestamp'].isoformat()
                )
                
                if anomaly_id:
                    stored_count += 1
                    
                    if jump['severity'] in ['high', 'critical']:
                        logger.warning(f"Significant price jump detected: {jump['explanation']}")
                    
            except Exception as e:
                logger.warning(f"Failed to store price jump: {e}")
                continue
        
        logger.info(f"Stored {stored_count} price jump anomalies in database")
        return stored_count
    
    async def run_detection_cycle(self, tickers: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run price jump detection for specified tickers.
        
        Args:
            tickers: List of tickers to analyze (defaults to all tracked assets)
        """
        start_time = datetime.now()
        logger.info("Starting price jump detection cycle")
        
        results = {
            'start_time': start_time.isoformat(),
            'tickers_processed': 0,
            'jumps_detected': 0,
            'jumps_stored': 0,
            'errors': [],
            'success': True
        }
        
        try:
            if tickers is None:
                # Get all tracked tickers
                all_tickers = []
                for asset_type, ticker_list in TRACKED_ASSETS.items():
                    all_tickers.extend(ticker_list)
                tickers = all_tickers
            
            all_jumps = []
            
            for ticker in tickers:
                try:
                    logger.debug(f"Analyzing price jumps for {ticker}")
                    
                    # Get recent price data
                    df = self.get_recent_price_data(ticker, hours_back=6)
                    
                    if df.empty:
                        logger.warning(f"No price data available for {ticker}")
                        continue
                    
                    # Calculate price changes
                    df = self.calculate_price_changes(df)
                    
                    # Detect jumps
                    ticker_jumps = self.detect_price_jumps(df, ticker)
                    
                    # Add context analysis
                    for jump in ticker_jumps:
                        jump = self.analyze_jump_context(jump, df)
                    
                    all_jumps.extend(ticker_jumps)
                    results['tickers_processed'] += 1
                    
                except Exception as e:
                    results['errors'].append(f"Failed to analyze {ticker}: {str(e)}")
                    logger.error(f"Failed to analyze price jumps for {ticker}: {e}")
            
            # Store detected jumps
            if all_jumps:
                stored_count = self.store_price_jumps(all_jumps)
                results['jumps_detected'] = len(all_jumps)
                results['jumps_stored'] = stored_count
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Price jump detection completed in {duration:.2f}s: "
                       f"{results['tickers_processed']} tickers, "
                       f"{results['jumps_detected']} jumps detected")
            
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = duration
            
        except Exception as e:
            logger.error(f"Price jump detection cycle failed: {e}")
            results['success'] = False
            results['errors'].append(str(e))
        
        return results

# Global detector instance
price_jump_detector = PriceJumpDetector()

# Convenience functions for external use
def detect_price_jumps() -> Dict[str, Any]:
    """Synchronous wrapper for price jump detection."""
    return asyncio.run(price_jump_detector.run_detection_cycle())

def detect_jumps_for_ticker(ticker: str) -> List[Dict[str, Any]]:
    """Detect price jumps for a specific ticker."""
    df = price_jump_detector.get_recent_price_data(ticker, hours_back=6)
    if df.empty:
        return []
    
    df = price_jump_detector.calculate_price_changes(df)
    jumps = price_jump_detector.detect_price_jumps(df, ticker)
    
    # Add context analysis
    for jump in jumps:
        jump = price_jump_detector.analyze_jump_context(jump, df)
    
    return jumps

def get_recent_jumps(ticker: str, hours_back: int = 24) -> List[Dict[str, Any]]:
    """Get recent price jumps from database for a ticker."""
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        query = """
            SELECT ticker, metric, anomaly_score, severity, explanation, timestamp
            FROM anomalies 
            WHERE ticker = %s 
            AND metric = 'price_jump'
            AND timestamp >= %s 
            ORDER BY timestamp DESC
        """
        
        params = (ticker, cutoff_time.isoformat())
        results = db.execute_query(query, params)
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to retrieve recent jumps for {ticker}: {e}")
        return []