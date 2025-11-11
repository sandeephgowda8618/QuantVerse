"""
Infrastructure monitoring collector for exchange status and blockchain health.
Monitors Coinbase, Binance, Solana, and other critical infrastructure.
"""

import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..config.settings import settings
from ..db.postgres_handler import db
from ..utils.logging_utils import setup_logger

logger = setup_logger(__name__)

class InfrastructureCollector:
    """Collects infrastructure status data from exchanges and blockchain networks."""
    
    def __init__(self):
        self.session = requests.Session()
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=2,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def check_coinbase_status(self) -> Dict[str, Any]:
        """Check Coinbase exchange status."""
        try:
            logger.info("Checking Coinbase status")
            
            response = self.session.get(settings.COINBASE_STATUS_URL, timeout=15)
            response.raise_for_status()
            
            status_data = response.json()
            
            # Parse Coinbase status
            page = status_data.get('page', {})
            status = page.get('status', 'unknown')
            
            # Check for active incidents
            incidents = status_data.get('incidents', [])
            active_incidents = [inc for inc in incidents if inc.get('status') not in ['resolved', 'postmortem']]
            
            # Determine severity
            severity = 'low'
            if status in ['major_outage', 'critical']:
                severity = 'critical'
            elif status in ['partial_outage', 'degraded_performance']:
                severity = 'high'
            elif active_incidents:
                severity = 'medium'
            
            # Create incident record
            incident_data = {
                'platform': 'coinbase',
                'incident_type': 'status_check',
                'description': f"Status: {status}. Active incidents: {len(active_incidents)}",
                'severity': severity,
                'started_at': datetime.now(),
                'resolved_at': None if severity != 'low' else datetime.now(),
                'source': 'coinbase_status_api',
                'raw_data': status_data
            }
            
            logger.info(f"Coinbase status: {status}, severity: {severity}")
            return incident_data
            
        except Exception as e:
            logger.error(f"Failed to check Coinbase status: {e}")
            return {
                'platform': 'coinbase',
                'incident_type': 'api_error',
                'description': f"Failed to fetch status: {str(e)}",
                'severity': 'medium',
                'started_at': datetime.now(),
                'resolved_at': None,
                'source': 'coinbase_status_api'
            }
    
    def check_binance_status(self) -> Dict[str, Any]:
        """Check Binance exchange status using ping endpoint."""
        try:
            logger.info("Checking Binance status")
            
            response = self.session.get(settings.BINANCE_STATUS_URL, timeout=15)
            response.raise_for_status()
            
            # Ping endpoint returns empty dict {} if successful
            status_data = response.json()
            
            # If we got a response and it's a dict, Binance is operational
            if isinstance(status_data, dict):
                severity = 'low'
                incident_type = 'normal_operation'
                description = "Binance API responding normally"
                resolved_at = datetime.now()
            else:
                severity = 'medium'
                incident_type = 'api_issue'
                description = "Unexpected response from Binance API"
                resolved_at = None
            
            incident_data = {
                'platform': 'binance',
                'incident_type': incident_type,
                'description': description,
                'severity': severity,
                'started_at': datetime.now(),
                'resolved_at': resolved_at,
                'source': 'binance_status_api',
                'raw_data': status_data
            }
            
            logger.info(f"Binance status: {description}, severity: {severity}")
            return incident_data
            
        except Exception as e:
            logger.error(f"Failed to check Binance status: {e}")
            return {
                'platform': 'binance',
                'incident_type': 'api_error',
                'description': f"Failed to fetch status: {str(e)}",
                'severity': 'medium',
                'started_at': datetime.now(),
                'resolved_at': None,
                'source': 'binance_status_api'
            }
    
    def check_solana_network_health(self) -> Dict[str, Any]:
        """Check Solana network health and congestion."""
        try:
            logger.info("Checking Solana network health")
            
            # Get recent performance samples
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getRecentPerformanceSamples",
                "params": [10]  # Last 10 samples
            }
            
            response = self.session.post(
                settings.SOLANA_RPC_URL,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'result' not in data:
                raise Exception(f"Invalid Solana RPC response: {data}")
            
            samples = data['result']
            if not samples:
                raise Exception("No performance samples returned")
            
            # Analyze latest sample
            latest_sample = samples[0]
            tps = latest_sample.get('numTransactions', 0) / latest_sample.get('samplePeriodSecs', 1)
            slot_time = latest_sample.get('samplePeriodSecs', 0)
            
            # Determine network health
            severity = 'low'
            incident_type = 'normal_operation'
            description = f"Solana TPS: {tps:.1f}, Slot time: {slot_time}s"
            
            # Check for congestion indicators
            if tps < 1000:  # Low TPS might indicate issues
                severity = 'medium'
                incident_type = 'low_throughput'
                description += " - Low throughput detected"
            elif slot_time > 1.0:  # Slow slot times
                severity = 'medium'
                incident_type = 'slow_slots'
                description += " - Slow slot processing"
            
            incident_data = {
                'platform': 'solana',
                'incident_type': incident_type,
                'description': description,
                'severity': severity,
                'started_at': datetime.now(),
                'resolved_at': datetime.now() if severity == 'low' else None,
                'source': 'solana_rpc',
                'raw_data': {'latest_sample': latest_sample, 'tps': tps}
            }
            
            logger.info(f"Solana network: TPS {tps:.1f}, severity: {severity}")
            return incident_data
            
        except Exception as e:
            logger.error(f"Failed to check Solana network health: {e}")
            return {
                'platform': 'solana',
                'incident_type': 'api_error',
                'description': f"Failed to fetch network health: {str(e)}",
                'severity': 'medium',
                'started_at': datetime.now(),
                'resolved_at': None,
                'source': 'solana_rpc'
            }
    
    def check_general_outages(self) -> List[Dict[str, Any]]:
        """Check for general infrastructure outages affecting multiple platforms."""
        incidents = []
        
        try:
            # This is a simplified implementation
            # In production, you might integrate with services like:
            # - Cloudflare status API
            # - AWS status API
            # - Internet health monitoring services
            
            # For now, we'll create a placeholder that could be extended
            logger.info("Checking for general infrastructure issues")
            
            # Example: Check if multiple platforms are down simultaneously
            # This could indicate broader internet/infrastructure issues
            
            # This would be implemented with real monitoring APIs
            general_status = {
                'platform': 'general_infrastructure',
                'incident_type': 'health_check',
                'description': 'General infrastructure monitoring - no issues detected',
                'severity': 'low',
                'started_at': datetime.now(),
                'resolved_at': datetime.now(),
                'source': 'infrastructure_monitor'
            }
            
            incidents.append(general_status)
            
        except Exception as e:
            logger.error(f"Failed to check general infrastructure: {e}")
            incidents.append({
                'platform': 'general_infrastructure',
                'incident_type': 'monitor_error',
                'description': f"Infrastructure monitoring failed: {str(e)}",
                'severity': 'low',
                'started_at': datetime.now(),
                'resolved_at': None,
                'source': 'infrastructure_monitor'
            })
        
        return incidents
    
    def store_infrastructure_incidents(self, incidents: List[Dict[str, Any]]) -> int:
        """Store infrastructure incidents in database."""
        if not incidents:
            return 0
        
        stored_count = 0
        
        for incident in incidents:
            try:
                query = """
                    INSERT INTO infra_incidents 
                    (platform, incident_type, description, severity, started_at, resolved_at, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """
                
                params = (
                    incident['platform'],
                    incident['incident_type'],
                    incident['description'],
                    incident['severity'],
                    incident['started_at'].isoformat(),
                    incident['resolved_at'].isoformat() if incident.get('resolved_at') else None,
                    incident['source']
                )
                
                incident_id = db.execute_insert(query, params)
                if incident_id:
                    stored_count += 1
                    
                    # Log high severity incidents
                    if incident['severity'] in ['high', 'critical']:
                        logger.warning(f"High severity infrastructure incident: {incident['description']}")
                    
            except Exception as e:
                logger.warning(f"Failed to store infrastructure incident: {e}")
                continue
        
        logger.info(f"Stored {stored_count} infrastructure incidents in database")
        return stored_count
    
    def generate_infrastructure_alert(self, incidents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Generate alert if critical infrastructure issues are detected."""
        critical_incidents = [inc for inc in incidents if inc['severity'] in ['high', 'critical']]
        
        if not critical_incidents:
            return None
        
        # Create consolidated alert
        platforms_affected = [inc['platform'] for inc in critical_incidents]
        
        alert = {
            'ticker': None,  # Infrastructure alerts are not ticker-specific
            'risk_type': 'infra',
            'severity': 'high' if any(inc['severity'] == 'critical' for inc in critical_incidents) else 'medium',
            'message': f"Infrastructure issues detected on: {', '.join(platforms_affected)}",
            'details': critical_incidents
        }
        
        return alert
    
    async def run_collection_cycle(self) -> Dict[str, Any]:
        """Run a complete infrastructure monitoring cycle."""
        start_time = datetime.now()
        logger.info("Starting infrastructure monitoring cycle")
        
        results = {
            'start_time': start_time.isoformat(),
            'platforms_checked': 0,
            'incidents_detected': 0,
            'incidents_stored': 0,
            'alerts_generated': 0,
            'errors': [],
            'success': True
        }
        
        try:
            all_incidents = []
            
            # Check Coinbase status
            try:
                coinbase_incident = self.check_coinbase_status()
                all_incidents.append(coinbase_incident)
                results['platforms_checked'] += 1
            except Exception as e:
                results['errors'].append(f"Coinbase check failed: {str(e)}")
                logger.error(f"Coinbase status check failed: {e}")
            
            # Check Binance status
            try:
                binance_incident = self.check_binance_status()
                all_incidents.append(binance_incident)
                results['platforms_checked'] += 1
            except Exception as e:
                results['errors'].append(f"Binance check failed: {str(e)}")
                logger.error(f"Binance status check failed: {e}")
            
            # Check Solana network
            try:
                solana_incident = self.check_solana_network_health()
                all_incidents.append(solana_incident)
                results['platforms_checked'] += 1
            except Exception as e:
                results['errors'].append(f"Solana check failed: {str(e)}")
                logger.error(f"Solana network check failed: {e}")
            
            # Check general infrastructure
            try:
                general_incidents = self.check_general_outages()
                all_incidents.extend(general_incidents)
                results['platforms_checked'] += len(general_incidents)
            except Exception as e:
                results['errors'].append(f"General infrastructure check failed: {str(e)}")
                logger.error(f"General infrastructure check failed: {e}")
            
            # Store incidents
            if all_incidents:
                stored_count = self.store_infrastructure_incidents(all_incidents)
                results['incidents_detected'] = len(all_incidents)
                results['incidents_stored'] = stored_count
                
                # Generate alerts for critical issues
                alert = self.generate_infrastructure_alert(all_incidents)
                if alert:
                    # Store alert in database
                    try:
                        from ..db.postgres_handler import insert_alert
                        alert_id = insert_alert(
                            ticker=alert['ticker'] or '',
                            risk_type=alert['risk_type'],
                            severity=alert['severity'],
                            message=alert['message']
                        )
                        if alert_id:
                            results['alerts_generated'] = 1
                    except Exception as e:
                        logger.error(f"Failed to store infrastructure alert: {e}")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Infrastructure monitoring completed in {duration:.2f}s: "
                       f"{results['platforms_checked']} platforms, "
                       f"{results['incidents_detected']} incidents, "
                       f"{results['alerts_generated']} alerts")
            
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = duration
            
        except Exception as e:
            logger.error(f"Infrastructure monitoring cycle failed: {e}")
            results['success'] = False
            results['errors'].append(str(e))
        
        return results

# Global collector instance
infra_collector = InfrastructureCollector()

# Convenience functions for external use
def collect_infrastructure_status() -> Dict[str, Any]:
    """Synchronous wrapper for infrastructure monitoring."""
    return asyncio.run(infra_collector.run_collection_cycle())

def check_coinbase_only() -> Dict[str, Any]:
    """Check only Coinbase status."""
    return infra_collector.check_coinbase_status()

def check_binance_only() -> Dict[str, Any]:
    """Check only Binance status."""
    return infra_collector.check_binance_status()

def check_solana_only() -> Dict[str, Any]:
    """Check only Solana network health."""
    return infra_collector.check_solana_network_health()