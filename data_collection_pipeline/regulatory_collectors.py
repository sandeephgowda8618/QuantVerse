#!/usr/bin/env python3
"""
Regulatory and Infrastructure Data Collectors
Handles regulatory events and infrastructure status monitoring
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET

from .config import config
from .utils import http_client, db_manager, ingestion_logger, hash_content

logger = logging.getLogger(__name__)

class SECCollector:
    """SEC EDGAR filings collector"""
    
    def __init__(self):
        self.provider = 'sec'
        self.call_count = 0
        self.max_calls = 6
        self.base_url = 'https://www.sec.gov/files/company_tickers.json'
        self.edgar_base = 'https://data.sec.gov/submissions'
    
    async def collect_regulatory_events(self, session_id: str) -> Dict[str, Any]:
        """Collect recent SEC filings"""
        results = {'records': 0, 'calls': 0, 'errors': []}
        
        headers = {
            'User-Agent': 'QuantVerse Analytics (contact@quantverse.com)',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'data.sec.gov'
        }
        
        try:
            # Get company ticker mapping first
            start_time = datetime.now()
            
            try:
                company_response = await http_client.request_with_retries(
                    self.base_url.replace('data.sec.gov', 'www.sec.gov'),
                    headers={'User-Agent': headers['User-Agent']},
                    provider=self.provider
                )
                
                self.call_count += 1
                results['calls'] += 1
                
                # Process company mappings (limit to major companies)
                target_ciks = []
                if 'data' in company_response or isinstance(company_response, dict):
                    companies = company_response.get('data', company_response)
                    
                    # Focus on major companies (Fortune 500 tickers)
                    major_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'BAC']
                    
                    for company in companies:
                        if isinstance(company, dict) and company.get('ticker') in major_tickers:
                            target_ciks.append(str(company.get('cik_str', '')).zfill(10))
                        elif isinstance(company, list) and len(company) > 1 and company[1] in major_tickers:
                            target_ciks.append(str(company[0]).zfill(10))
                
                # Get recent filings for target companies
                regulatory_records = []
                
                for cik in target_ciks[:5]:  # Limit to 5 companies due to API limits
                    if self.call_count >= self.max_calls:
                        break
                    
                    try:
                        filing_url = f"{self.edgar_base}/CIK{cik}.json"
                        filing_response = await http_client.request_with_retries(
                            filing_url, headers=headers, provider=self.provider
                        )
                        
                        self.call_count += 1
                        results['calls'] += 1
                        
                        if 'filings' in filing_response and 'recent' in filing_response['filings']:
                            recent_filings = filing_response['filings']['recent']
                            
                            # Process recent filings (last 30 days)
                            cutoff_date = datetime.now() - timedelta(days=30)
                            
                            for i, form_type in enumerate(recent_filings.get('form', [])):
                                try:
                                    filing_date = datetime.strptime(
                                        recent_filings['filingDate'][i], '%Y-%m-%d'
                                    ).replace(tzinfo=timezone.utc)
                                    
                                    if filing_date >= cutoff_date:
                                        # Important form types
                                        if form_type in ['10-K', '10-Q', '8-K', '13F-HR', 'DEF 14A']:
                                            regulatory_record = {
                                                'event_type': f'SEC_{form_type}',
                                                'description': f"{form_type}: {recent_filings.get('primaryDocument', [''])[i]}",
                                                'filing_date': filing_date,
                                                'document_url': f"https://www.sec.gov/Archives/edgar/data/{cik}/{recent_filings.get('accessionNumber', [''])[i].replace('-', '')}/{recent_filings.get('primaryDocument', [''])[i]}",
                                                'impact_level': self._assess_filing_impact(form_type),
                                                'source': 'sec_edgar',
                                                'raw_data': json.dumps({
                                                    'cik': cik,
                                                    'accessionNumber': recent_filings.get('accessionNumber', [''])[i],
                                                    'primaryDocument': recent_filings.get('primaryDocument', [''])[i],
                                                    'reportDate': recent_filings.get('reportDate', [''])[i]
                                                }),
                                                'created_at': datetime.now(timezone.utc)
                                            }
                                            regulatory_records.append(regulatory_record)
                                
                                except (IndexError, ValueError, KeyError) as e:
                                    logger.warning(f"Error processing filing {i} for CIK {cik}: {e}")
                    
                    except Exception as e:
                        logger.warning(f"Failed to get filings for CIK {cik}: {e}")
                        results['errors'].append(f"CIK {cik}: {str(e)}")
                
                # Bulk upsert regulatory events
                if regulatory_records:
                    await db_manager.upsert_batch(
                        'regulatory_events', 
                        regulatory_records, 
                        ['document_url']
                    )
                    results['records'] += len(regulatory_records)
                
                duration = (datetime.now() - start_time).total_seconds()
                await ingestion_logger.log_ingestion(
                    session_id, self.provider, 'sec_filings',
                    duration, 'success', len(regulatory_records)
                )
                
                logger.info(f"SEC: Collected {len(regulatory_records)} regulatory events")
            
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                error_msg = str(e)
                results['errors'].append(error_msg)
                
                await ingestion_logger.log_ingestion(
                    session_id, self.provider, 'sec_filings',
                    duration, 'error', 0, error_msg
                )
                
                logger.error(f"SEC collection failed: {e}")
        
        except Exception as e:
            logger.error(f"SEC collector initialization failed: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def _assess_filing_impact(self, form_type: str) -> str:
        """Assess the potential market impact of different filing types"""
        high_impact = ['8-K', '10-K', '10-Q']  # Current reports, annual/quarterly
        medium_impact = ['13F-HR', 'DEF 14A']  # Institutional holdings, proxy statements
        
        if form_type in high_impact:
            return 'high'
        elif form_type in medium_impact:
            return 'medium'
        else:
            return 'low'

class FedCollector:
    """Federal Reserve data collector"""
    
    def __init__(self):
        self.provider = 'fed'
        self.call_count = 0
        self.max_calls = 3
        self.base_url = 'https://www.federalreserve.gov'
    
    async def collect_regulatory_events(self, session_id: str) -> Dict[str, Any]:
        """Collect Federal Reserve announcements and data"""
        results = {'records': 0, 'calls': 0, 'errors': []}
        
        try:
            # Fed news releases RSS
            rss_endpoints = [
                '/feeds/press_all.xml',  # All press releases
                '/feeds/testimony.xml',  # Fed testimonies
                '/feeds/speeches.xml'    # Fed speeches
            ]
            
            regulatory_records = []
            
            for endpoint in rss_endpoints[:self.max_calls]:
                if self.call_count >= self.max_calls:
                    break
                
                start_time = datetime.now()
                
                try:
                    url = f"{self.base_url}{endpoint}"
                    response = await http_client.request_with_retries(
                        url, provider=self.provider
                    )
                    
                    self.call_count += 1
                    results['calls'] += 1
                    
                    if 'data' in response:
                        # Parse XML
                        try:
                            root = ET.fromstring(response['data'])
                            
                            # Look for items in the RSS feed
                            for item in root.findall('.//item')[:10]:  # Limit to recent items
                                title_elem = item.find('title')
                                link_elem = item.find('link')
                                pub_date_elem = item.find('pubDate')
                                description_elem = item.find('description')
                                
                                if title_elem is not None and link_elem is not None:
                                    title = title_elem.text or ""
                                    link = link_elem.text or ""
                                    description = description_elem.text or "" if description_elem is not None else ""
                                    
                                    # Parse publication date
                                    published_at = datetime.now(timezone.utc)
                                    if pub_date_elem is not None and pub_date_elem.text:
                                        try:
                                            from email.utils import parsedate_to_datetime
                                            published_at = parsedate_to_datetime(pub_date_elem.text)
                                        except:
                                            pass
                                    
                                    # Only include recent events (last 30 days)
                                    cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
                                    if published_at >= cutoff_date:
                                        event_type = self._categorize_fed_event(title, endpoint)
                                        impact_level = self._assess_fed_impact(title, event_type)
                                        
                                        regulatory_record = {
                                            'event_type': event_type,
                                            'description': f"{title}: {description[:200]}...",
                                            'filing_date': published_at,
                                            'document_url': link,
                                            'impact_level': impact_level,
                                            'source': 'federal_reserve',
                                            'raw_data': json.dumps({
                                                'title': title,
                                                'description': description,
                                                'feed_type': endpoint
                                            }),
                                            'created_at': datetime.now(timezone.utc)
                                        }
                                        regulatory_records.append(regulatory_record)
                        
                        except ET.ParseError as e:
                            logger.warning(f"Failed to parse Fed XML for {endpoint}: {e}")
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'fed_{endpoint.split("/")[-1]}',
                        duration, 'success', len(regulatory_records)
                    )
                
                except Exception as e:
                    duration = (datetime.now() - start_time).total_seconds()
                    error_msg = str(e)
                    results['errors'].append(f"{endpoint}: {error_msg}")
                    
                    await ingestion_logger.log_ingestion(
                        session_id, self.provider, f'fed_{endpoint.split("/")[-1]}',
                        duration, 'error', 0, error_msg
                    )
                    
                    logger.error(f"Fed {endpoint} failed: {e}")
            
            # Bulk upsert
            if regulatory_records:
                await db_manager.upsert_batch(
                    'regulatory_events',
                    regulatory_records,
                    ['document_url']
                )
                results['records'] += len(regulatory_records)
            
            logger.info(f"Fed: Collected {len(regulatory_records)} regulatory events")
        
        except Exception as e:
            logger.error(f"Fed collection failed: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def _categorize_fed_event(self, title: str, endpoint: str) -> str:
        """Categorize Fed events based on title and source"""
        title_lower = title.lower()
        
        if 'interest rate' in title_lower or 'federal funds' in title_lower:
            return 'FED_INTEREST_RATE'
        elif 'monetary policy' in title_lower or 'fomc' in title_lower:
            return 'FED_MONETARY_POLICY'
        elif 'inflation' in title_lower:
            return 'FED_INFLATION'
        elif 'employment' in title_lower or 'unemployment' in title_lower:
            return 'FED_EMPLOYMENT'
        elif 'speech' in endpoint:
            return 'FED_SPEECH'
        elif 'testimony' in endpoint:
            return 'FED_TESTIMONY'
        else:
            return 'FED_ANNOUNCEMENT'
    
    def _assess_fed_impact(self, title: str, event_type: str) -> str:
        """Assess market impact of Fed events"""
        title_lower = title.lower()
        
        high_impact_keywords = ['interest rate', 'monetary policy', 'fomc', 'quantitative easing']
        medium_impact_keywords = ['inflation', 'employment', 'economic outlook']
        
        if event_type in ['FED_INTEREST_RATE', 'FED_MONETARY_POLICY']:
            return 'high'
        elif any(keyword in title_lower for keyword in high_impact_keywords):
            return 'high'
        elif any(keyword in title_lower for keyword in medium_impact_keywords):
            return 'medium'
        else:
            return 'low'

class InfrastructureCollector:
    """Infrastructure status collector for various services"""
    
    def __init__(self):
        self.provider = 'infrastructure'
        self.call_count = 0
        self.max_calls = 6
    
    async def collect_infrastructure_status(self, session_id: str) -> Dict[str, Any]:
        """Collect infrastructure status from various providers"""
        results = {'records': 0, 'calls': 0, 'errors': []}
        
        # Define status endpoints
        status_endpoints = [
            {
                'name': 'coinbase',
                'url': 'https://status.coinbase.com/api/v2/status.json',
                'service_type': 'cryptocurrency_exchange'
            },
            {
                'name': 'binance',
                'url': 'https://status.binance.com/api/v2/status.json',
                'service_type': 'cryptocurrency_exchange'
            },
            {
                'name': 'aws',
                'url': 'https://status.aws.amazon.com/rss/all.rss',
                'service_type': 'cloud_infrastructure',
                'format': 'rss'
            },
            {
                'name': 'github',
                'url': 'https://www.githubstatus.com/api/v2/status.json',
                'service_type': 'development_platform'
            },
            {
                'name': 'nasdaq',
                'url': 'https://nasdaqtrader.com/trader.aspx?id=tradinghalts',
                'service_type': 'stock_exchange',
                'format': 'html'
            }
        ]
        
        infra_records = []
        incident_records = []
        
        for endpoint in status_endpoints:
            if self.call_count >= self.max_calls:
                break
            
            start_time = datetime.now()
            
            try:
                response = await http_client.request_with_retries(
                    endpoint['url'], provider=self.provider
                )
                
                self.call_count += 1
                results['calls'] += 1
                
                # Process different response formats
                if endpoint.get('format') == 'rss':
                    await self._process_rss_status(
                        response, endpoint, infra_records, incident_records
                    )
                elif endpoint.get('format') == 'html':
                    await self._process_html_status(
                        response, endpoint, infra_records, incident_records
                    )
                else:
                    await self._process_json_status(
                        response, endpoint, infra_records, incident_records
                    )
                
                duration = (datetime.now() - start_time).total_seconds()
                await ingestion_logger.log_ingestion(
                    session_id, self.provider, f'status_{endpoint["name"]}',
                    duration, 'success', 1
                )
                
                logger.info(f"Infrastructure: {endpoint['name']} status collected")
            
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                error_msg = str(e)
                results['errors'].append(f"{endpoint['name']}: {error_msg}")
                
                await ingestion_logger.log_ingestion(
                    session_id, self.provider, f'status_{endpoint["name"]}',
                    duration, 'error', 0, error_msg
                )
                
                logger.error(f"Infrastructure {endpoint['name']} failed: {e}")
        
        # Bulk upsert infrastructure status
        if infra_records:
            await db_manager.upsert_batch(
                'infrastructure_status',
                infra_records,
                ['service_name', 'timestamp']
            )
            results['records'] += len(infra_records)
        
        # Bulk upsert incidents
        if incident_records:
            await db_manager.upsert_batch(
                'infra_incidents',
                incident_records,
                ['service_name', 'incident_id']
            )
            results['records'] += len(incident_records)
        
        logger.info(f"Infrastructure: Collected {len(infra_records)} status records, {len(incident_records)} incidents")
        return results
    
    async def _process_json_status(self, response: Dict, endpoint: Dict, infra_records: List, incident_records: List):
        """Process JSON status response"""
        if 'status' in response:
            status_data = response['status']
            
            # Infrastructure status record
            infra_record = {
                'service_name': endpoint['name'],
                'service_type': endpoint['service_type'],
                'status': status_data.get('indicator', 'unknown'),
                'description': status_data.get('description', ''),
                'timestamp': datetime.now(timezone.utc),
                'raw_data': json.dumps(response),
                'updated_at': datetime.now(timezone.utc)
            }
            infra_records.append(infra_record)
            
            # Check for incidents
            if 'incidents' in response:
                for incident in response['incidents'][:5]:  # Limit recent incidents
                    incident_record = {
                        'service_name': endpoint['name'],
                        'incident_id': incident.get('id', hash_content(str(incident))),
                        'title': incident.get('name', 'Unknown Incident'),
                        'description': incident.get('status', ''),
                        'severity': self._map_severity(incident.get('impact', 'minor')),
                        'status': incident.get('status', 'investigating'),
                        'started_at': self._parse_timestamp(incident.get('created_at')),
                        'resolved_at': self._parse_timestamp(incident.get('resolved_at')),
                        'raw_data': json.dumps(incident),
                        'created_at': datetime.now(timezone.utc)
                    }
                    incident_records.append(incident_record)
    
    async def _process_rss_status(self, response: Dict, endpoint: Dict, infra_records: List, incident_records: List):
        """Process RSS status response"""
        if 'data' in response:
            try:
                root = ET.fromstring(response['data'])
                
                # General status (assume operational if RSS is working)
                infra_record = {
                    'service_name': endpoint['name'],
                    'service_type': endpoint['service_type'],
                    'status': 'operational',
                    'description': 'RSS feed accessible',
                    'timestamp': datetime.now(timezone.utc),
                    'raw_data': json.dumps({'rss_accessible': True}),
                    'updated_at': datetime.now(timezone.utc)
                }
                infra_records.append(infra_record)
                
                # Check for recent incidents in RSS items
                for item in root.findall('.//item')[:5]:
                    title_elem = item.find('title')
                    description_elem = item.find('description')
                    
                    if title_elem is not None:
                        title = title_elem.text or ""
                        description = description_elem.text or "" if description_elem is not None else ""
                        
                        # Look for incident keywords
                        if any(keyword in title.lower() for keyword in ['outage', 'incident', 'degraded', 'issue']):
                            incident_record = {
                                'service_name': endpoint['name'],
                                'incident_id': hash_content(title + str(datetime.now().date())),
                                'title': title,
                                'description': description,
                                'severity': 'medium',
                                'status': 'investigating',
                                'started_at': datetime.now(timezone.utc),
                                'resolved_at': None,
                                'raw_data': json.dumps({'title': title, 'description': description}),
                                'created_at': datetime.now(timezone.utc)
                            }
                            incident_records.append(incident_record)
            
            except ET.ParseError as e:
                logger.warning(f"Failed to parse RSS for {endpoint['name']}: {e}")
    
    async def _process_html_status(self, response: Dict, endpoint: Dict, infra_records: List, incident_records: List):
        """Process HTML status response (simplified)"""
        # Basic status record for HTML endpoints
        infra_record = {
            'service_name': endpoint['name'],
            'service_type': endpoint['service_type'],
            'status': 'operational',  # Assume operational if we can reach it
            'description': 'Service accessible via HTTP',
            'timestamp': datetime.now(timezone.utc),
            'raw_data': json.dumps({'http_accessible': True}),
            'updated_at': datetime.now(timezone.utc)
        }
        infra_records.append(infra_record)
    
    def _parse_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        """Parse various timestamp formats"""
        if not timestamp_str:
            return None
        
        try:
            # Try ISO format first
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            try:
                # Try other common formats
                return datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
            except:
                return None
    
    def _map_severity(self, impact: str) -> str:
        """Map various impact levels to our severity scale"""
        impact_lower = impact.lower()
        
        if impact_lower in ['critical', 'major']:
            return 'high'
        elif impact_lower in ['minor', 'maintenance']:
            return 'low'
        else:
            return 'medium'

class RegulatoryOrchestrator:
    """Orchestrates regulatory and infrastructure data collection"""
    
    def __init__(self):
        self.collectors = {
            'sec': SECCollector(),
            'fed': FedCollector(),
            'infrastructure': InfrastructureCollector()
        }
    
    async def collect_all(self, session_id: str) -> Dict[str, Any]:
        """Collect regulatory and infrastructure data from all sources"""
        results = {
            'total_records': 0,
            'total_calls': 0,
            'providers': {},
            'errors': []
        }
        
        logger.info("Starting regulatory and infrastructure data collection")
        
        # Run collectors in parallel
        tasks = []
        for name, collector in self.collectors.items():
            if name == 'infrastructure':
                task = asyncio.create_task(
                    collector.collect_infrastructure_status(session_id),
                    name=f"regulatory_{name}"
                )
            else:
                task = asyncio.create_task(
                    collector.collect_regulatory_events(session_id),
                    name=f"regulatory_{name}"
                )
            tasks.append((name, task))
        
        # Wait for all collectors to complete
        for provider_name, task in tasks:
            try:
                provider_results = await task
                results['providers'][provider_name] = provider_results
                results['total_records'] += provider_results['records']
                results['total_calls'] += provider_results['calls']
                
                if provider_results['errors']:
                    results['errors'].extend([f"{provider_name}: {err}" for err in provider_results['errors']])
                
                logger.info(f"Regulatory - {provider_name}: {provider_results['records']} records, {provider_results['calls']} calls")
                
            except Exception as e:
                error_msg = f"{provider_name} failed: {str(e)}"
                results['errors'].append(error_msg)
                logger.error(error_msg)
        
        logger.info(f"Regulatory collection complete: {results['total_records']} records, {results['total_calls']} calls")
        return results
