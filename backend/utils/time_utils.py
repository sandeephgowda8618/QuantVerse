"""
Time Utilities for Movement Analysis
Part of Member 2 implementation
"""

from datetime import datetime, timedelta
from typing import Tuple
import pytz

class TimeUtils:
    """
    Time manipulation utilities for movement analysis windows.
    
    This class handles:
    1. Analysis window creation around target timestamps
    2. Market hours validation
    3. Session detection (pre-market, regular, after-hours, overnight)
    """
    
    def __init__(self):
        self.utc = pytz.UTC
    
    def create_analysis_window(self, timestamp: datetime, window_minutes: int = 30) -> Tuple[datetime, datetime]:
        """
        Create start/end times for analysis window around a target timestamp
        
        Args:
            timestamp: Target timestamp for movement analysis
            window_minutes: Minutes before and after timestamp (default ±30 min)
            
        Returns:
            Tuple[datetime, datetime]: (start_time, end_time)
        """
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=self.utc)
        
        start_time = timestamp - timedelta(minutes=window_minutes)
        end_time = timestamp + timedelta(minutes=window_minutes)
        
        return start_time, end_time
    
    def format_time_window(self, start_time: datetime, end_time: datetime) -> str:
        """
        Format time window for display/logging
        
        Args:
            start_time: Window start time
            end_time: Window end time
            
        Returns:
            str: Formatted time range
        """
        return f"{start_time.isoformat()} to {end_time.isoformat()}"
    
    def is_market_hours(self, timestamp: datetime, exchange: str = "NYSE") -> bool:
        """
        Check if timestamp falls within market hours
        
        Args:
            timestamp: Time to check
            exchange: Exchange to check ("NYSE", "NASDAQ", "CRYPTO")
            
        Returns:
            bool: True if within market hours
        """
        # Convert to EST for US markets
        if exchange in ["NYSE", "NASDAQ"]:
            est = pytz.timezone('US/Eastern')
            local_time = timestamp.astimezone(est)
            
            # Check if weekday and within 9:30 AM - 4:00 PM EST
            if local_time.weekday() >= 5:  # Weekend
                return False
            
            market_open = local_time.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = local_time.replace(hour=16, minute=0, second=0, microsecond=0)
            
            return market_open <= local_time <= market_close
        
        # For crypto/24-7 markets
        return True
    
    def find_market_session(self, timestamp: datetime) -> str:
        """
        Determine which market session the timestamp falls into
        
        Args:
            timestamp: Time to classify
            
        Returns:
            str: Session type ("pre_market", "regular_hours", "after_hours", "overnight")
        """
        est = pytz.timezone('US/Eastern')
        local_time = timestamp.astimezone(est)
        hour = local_time.hour
        
        if 4 <= hour < 9:
            return "pre_market"
        elif 9 <= hour < 16:
            return "regular_hours"
        elif 16 <= hour < 20:
            return "after_hours"
        else:
            return "overnight"
    
    def time_until_market_open(self, timestamp: datetime) -> timedelta:
        """
        Calculate time until next market open
        
        Args:
            timestamp: Current time
            
        Returns:
            timedelta: Time until market opens
        """
        est = pytz.timezone('US/Eastern')
        local_time = timestamp.astimezone(est)
        
        # If it's weekend, find next Monday
        if local_time.weekday() >= 5:
            days_ahead = 7 - local_time.weekday()
            next_monday = local_time + timedelta(days=days_ahead)
            market_open = next_monday.replace(hour=9, minute=30, second=0, microsecond=0)
        else:
            # Same day or next day
            market_open = local_time.replace(hour=9, minute=30, second=0, microsecond=0)
            if local_time.hour >= 16:  # After market close
                market_open += timedelta(days=1)
        
        return market_open - local_time
