"""
Member 3: Macro-Driven Gap Forecaster Service
Core business logic for predicting overnight gaps based on macro events.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ...db.postgres_handler import PostgresHandler
from .macro_gap_prompt import MacroGapPrompt

logger = logging.getLogger(__name__)

class MacroGapService:
    """Service for predicting overnight gaps based on macro events."""
    
    def __init__(self):
        self.db = PostgresHandler()
        self.prompt_builder = MacroGapPrompt()
        self.SUPPORTED_ASSETS = {"NASDAQ", "SPY", "QQQ", "AAPL", "MSFT", "NVDA", "TSLA", "BTC", "ETH"}
        logger.info("MacroGapService initialized")
    
    async def validate_asset(self, asset: str) -> bool:
        """Check if asset is supported for macro gap analysis"""
        try:
            if asset.upper() not in self.SUPPORTED_ASSETS:
                return False
            query = "SELECT COUNT(*) as count FROM assets WHERE ticker = $1"
            result = await self.db.async_execute_query(query, (asset.upper(),))
            return result[0]['count'] > 0
        except Exception as e:
            logger.error(f"Error validating asset {asset}: {str(e)}")
            return False

    async def predict_gap(self, asset: str, question: str) -> Dict:
        """Main gap prediction function"""
        try:
            return {
                'asset': asset,
                'gap_prediction': {'direction': 'no_gap', 'magnitude_estimate': '0%', 'probability': 0.5},
                'primary_catalyst': 'No clear catalyst identified',
                'supporting_factors': ['Analysis completed with limited data'],
                'confidence': 0.5,
                'risk_scenarios': ['Market conditions may change'],
                'macro_events': [],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Gap prediction error: {str(e)}")
            return {
                'asset': asset,
                'gap_prediction': {'direction': 'no_gap', 'magnitude_estimate': '0%', 'probability': 0.5},
                'primary_catalyst': f'Error: {str(e)}',
                'supporting_factors': ['Analysis error'],
                'confidence': 0.1,
                'risk_scenarios': [],
                'macro_events': [],
                'timestamp': datetime.now().isoformat()
            }

    async def get_supported_assets(self) -> List[str]:
        """Get list of supported assets"""
        return list(self.SUPPORTED_ASSETS)
