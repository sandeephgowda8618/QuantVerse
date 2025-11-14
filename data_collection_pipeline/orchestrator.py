#!/usr/bin/env python3
"""
Main Data Collection Pipeline Orchestrator
Coordinates all data collectors with scheduling and session management
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import signal
import sys

from .config import config, PRIORITY_TICKERS
from .utils import db_manager, http_client, ingestion_logger, generate_session_id
from .market_collectors import MarketDataOrchestrator
from .news_collectors import NewsOrchestrator
from .regulatory_collectors import RegulatoryOrchestrator
from .technical_collectors import TechnicalIndicatorsOrchestrator

logger = logging.getLogger(__name__)

class DataCollectionPipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self):
        self.running = False
        self.session_id = None
        
        # Initialize orchestrators
        self.market_orchestrator = MarketDataOrchestrator()
        self.news_orchestrator = NewsOrchestrator()
        self.regulatory_orchestrator = RegulatoryOrchestrator()
        self.technical_orchestrator = TechnicalIndicatorsOrchestrator()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False
    
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing data collection pipeline...")
        
        try:
            # Initialize database and HTTP client
            await db_manager.initialize()
            await http_client.initialize()
            
            logger.info("Pipeline initialization complete")
        except Exception as e:
            logger.error(f"Pipeline initialization failed: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown all components gracefully"""
        logger.info("Shutting down data collection pipeline...")
        
        try:
            # Update session status if running
            if self.session_id:
                await ingestion_logger.update_session(
                    self.session_id, 
                    status='stopped',
                    error_info={'shutdown_timestamp': datetime.now(timezone.utc).isoformat()}
                )
            
            # Close connections
            await http_client.close()
            await db_manager.close()
            
            logger.info("Pipeline shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    async def run_single_collection_cycle(self, tickers: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run a single complete data collection cycle"""
        tickers = tickers or PRIORITY_TICKERS
        
        # Generate session ID
        self.session_id = generate_session_id("pipeline")
        
        # Initialize session
        await ingestion_logger.create_session(
            self.session_id,
            metadata={
                'pipeline_type': 'complete_cycle',
                'target_tickers': tickers,
                'total_tickers': len(tickers),
                'started_at': datetime.now(timezone.utc).isoformat(),
                'config': {
                    'market_interval': config.scheduler.market_data_interval,
                    'news_interval': config.scheduler.news_data_interval,
                    'regulatory_interval': config.scheduler.regulatory_interval
                }
            }
        )
        
        logger.info(f"Starting collection cycle {self.session_id} for {len(tickers)} tickers")
        
        # Collect results
        cycle_results = {
            'session_id': self.session_id,
            'started_at': datetime.now(timezone.utc),
            'completed_at': None,
            'total_records': 0,
            'total_api_calls': 0,
            'collectors': {},
            'errors': [],
            'duration_seconds': 0
        }
        
        start_time = datetime.now()
        
        try:
            # Run all collectors in parallel for maximum efficiency
            collector_tasks = [
                ('market_data', self.market_orchestrator.collect_all(self.session_id, tickers)),
                ('news', self.news_orchestrator.collect_all(self.session_id, tickers)),
                ('technical', self.technical_orchestrator.collect_all(self.session_id, tickers)),
                ('regulatory', self.regulatory_orchestrator.collect_all(self.session_id))
            ]
            
            # Execute all collectors concurrently
            for collector_name, task in collector_tasks:
                try:
                    logger.info(f"Starting {collector_name} collection...")
                    collector_results = await task
                    
                    cycle_results['collectors'][collector_name] = collector_results
                    cycle_results['total_records'] += collector_results['total_records']
                    cycle_results['total_api_calls'] += collector_results['total_calls']
                    
                    if collector_results['errors']:
                        cycle_results['errors'].extend([
                            f"{collector_name}: {err}" for err in collector_results['errors']
                        ])
                    
                    logger.info(f"{collector_name} complete: {collector_results['total_records']} records, {collector_results['total_calls']} API calls")
                
                except Exception as e:
                    error_msg = f"{collector_name} collection failed: {str(e)}"
                    cycle_results['errors'].append(error_msg)
                    logger.error(error_msg)
            
            # Calculate duration
            end_time = datetime.now()
            cycle_results['completed_at'] = end_time
            cycle_results['duration_seconds'] = (end_time - start_time).total_seconds()
            
            # Update session with final results
            await ingestion_logger.update_session(
                self.session_id,
                status='COMPLETED',
                total_records=cycle_results['total_records'],
                total_api_calls=cycle_results['total_api_calls']
            )
            
            logger.info(f"Collection cycle {self.session_id} completed:")
            logger.info(f"  Total records: {cycle_results['total_records']:,}")
            logger.info(f"  Total API calls: {cycle_results['total_api_calls']}")
            logger.info(f"  Duration: {cycle_results['duration_seconds']:.1f} seconds")
            logger.info(f"  Errors: {len(cycle_results['errors'])}")
            
            return cycle_results
        
        except Exception as e:
            # Update session with error
            await ingestion_logger.update_session(
                self.session_id,
                status='FAILED',
                total_records=0,
                total_api_calls=0
            )
            
            logger.error(f"Collection cycle {self.session_id} failed: {e}")
            raise
    
    async def run_scheduled_pipeline(self):
        """Run the pipeline with scheduled intervals"""
        logger.info("Starting scheduled data collection pipeline")
        self.running = True
        
        # Initialize pipeline
        await self.initialize()
        
        try:
            # Track last run times for different collectors
            last_runs = {
                'market': datetime.min.replace(tzinfo=timezone.utc),
                'news': datetime.min.replace(tzinfo=timezone.utc),
                'regulatory': datetime.min.replace(tzinfo=timezone.utc),
                'technical': datetime.min.replace(tzinfo=timezone.utc)
            }
            
            while self.running:
                current_time = datetime.now(timezone.utc)
                
                # Determine which collectors to run based on intervals
                collectors_to_run = []
                
                # Market data (every 5 minutes)
                if (current_time - last_runs['market']).total_seconds() >= config.scheduler.market_data_interval:
                    collectors_to_run.append('market')
                    last_runs['market'] = current_time
                
                # News data (every 10 minutes)
                if (current_time - last_runs['news']).total_seconds() >= config.scheduler.news_data_interval:
                    collectors_to_run.append('news')
                    last_runs['news'] = current_time
                
                # Technical indicators (every 10 minutes, offset by 5 minutes from news)
                if (current_time - last_runs['technical']).total_seconds() >= config.scheduler.news_data_interval:
                    collectors_to_run.append('technical')
                    last_runs['technical'] = current_time
                
                # Regulatory data (every 12 hours)
                if (current_time - last_runs['regulatory']).total_seconds() >= config.scheduler.regulatory_interval:
                    collectors_to_run.append('regulatory')
                    last_runs['regulatory'] = current_time
                
                # Run selected collectors
                if collectors_to_run:
                    await self._run_selected_collectors(collectors_to_run)
                
                # Sleep for a short interval before checking again
                await asyncio.sleep(60)  # Check every minute
        
        except Exception as e:
            logger.error(f"Scheduled pipeline error: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def _run_selected_collectors(self, collector_names: List[str]):
        """Run specific collectors"""
        session_id = generate_session_id("scheduled")
        
        logger.info(f"Running scheduled collectors: {', '.join(collector_names)}")
        
        # Initialize session
        await ingestion_logger.create_session(
            session_id,
            metadata={
                'pipeline_type': 'scheduled',
                'collectors': collector_names,
                'started_at': datetime.now(timezone.utc).isoformat()
            }
        )
        
        total_records = 0
        total_calls = 0
        errors = []
        
        try:
            # Run collectors in parallel
            tasks = []
            
            if 'market' in collector_names:
                tasks.append(('market', self.market_orchestrator.collect_all(session_id, PRIORITY_TICKERS)))
            
            if 'news' in collector_names:
                tasks.append(('news', self.news_orchestrator.collect_all(session_id, PRIORITY_TICKERS)))
            
            if 'technical' in collector_names:
                tasks.append(('technical', self.technical_orchestrator.collect_all(session_id, PRIORITY_TICKERS)))
            
            if 'regulatory' in collector_names:
                tasks.append(('regulatory', self.regulatory_orchestrator.collect_all(session_id)))
            
            # Execute tasks
            for collector_name, task in tasks:
                try:
                    results = await task
                    total_records += results['total_records']
                    total_calls += results['total_calls']
                    
                    if results['errors']:
                        errors.extend([f"{collector_name}: {err}" for err in results['errors']])
                    
                    logger.info(f"Scheduled {collector_name}: {results['total_records']} records, {results['total_calls']} calls")
                
                except Exception as e:
                    error_msg = f"Scheduled {collector_name} failed: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            # Update session
            await ingestion_logger.update_session(
                session_id,
                status='completed',
                total_records=total_records,
                total_api_calls=total_calls,
                total_errors=len(errors)
            )
            
            logger.info(f"Scheduled collection complete: {total_records} records, {total_calls} calls, {len(errors)} errors")
        
        except Exception as e:
            await ingestion_logger.update_session(
                session_id,
                status='failed',
                error_info={'error_message': str(e)}
            )
            logger.error(f"Scheduled collection failed: {e}")
    
    async def run_market_data_only(self, tickers: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run only market data collection"""
        tickers = tickers or PRIORITY_TICKERS
        session_id = generate_session_id("market_only")
        
        await ingestion_logger.create_session(
            session_id,
            metadata={
                'pipeline_type': 'market_only', 
                'tickers': tickers,
                'total_tickers': len(tickers)
            }
        )
        
        logger.info(f"Running market data collection for {len(tickers)} tickers")
        
        try:
            results = await self.market_orchestrator.collect_all(session_id, tickers)
            
            await ingestion_logger.update_session(
                session_id,
                status='completed',
                total_records=results['total_records'],
                total_api_calls=results['total_calls']
            )
            
            return results
        
        except Exception as e:
            await ingestion_logger.update_session(
                session_id,
                status='failed'
            )
            raise
    
    async def run_news_only(self, tickers: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run only news collection"""
        tickers = tickers or PRIORITY_TICKERS
        session_id = generate_session_id("news_only")
        
        await ingestion_logger.create_session(
            session_id,
            metadata={
                'pipeline_type': 'news_only', 
                'tickers': tickers,
                'total_tickers': len(tickers)
            }
        )
        
        logger.info(f"Running news collection for {len(tickers)} tickers")
        
        try:
            results = await self.news_orchestrator.collect_all(session_id, tickers)
            
            await ingestion_logger.update_session(
                session_id,
                status='completed',
                total_records=results['total_records'],
                total_api_calls=results['total_calls']
            )
            
            return results
        
        except Exception as e:
            await ingestion_logger.update_session(
                session_id,
                status='failed'
            )
            raise

# Global pipeline instance
pipeline = DataCollectionPipeline()
