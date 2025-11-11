"""
Regulatory data collector for SEC, RBI, and Federal Reserve sources.
Collects regulatory events, policy changes, and macro announcements.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
import feedparser
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..config.settings import settings
from ..db.postgres_handler import db
from ..utils.logging_utils import setup_logger

logger = setup_logger(__name__)

class RegulatoryCollector:
    """Collects regulatory data from SEC, RBI, and Fed sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.SEC_EDGAR_USER_AGENT
        })
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def collect_sec_filings(self, days_back: int = 1) -> List[Dict[str, Any]]:
        """
        Collect recent SEC filings that may impact tracked assets.
        
        Args:
            days_back: Number of days to look back for filings
        """
        try:
            logger.info(f"Collecting SEC filings from last {days_back} days")
            
            # SEC RSS feed for recent filings
            sec_rss_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=&company=&dateb=&owner=include&start=0&count=100&output=atom"
            
            response = self.session.get(sec_rss_url, timeout=30)
            response.raise_for_status()
            
            # Parse RSS feed
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                logger.warning("No SEC filings found in RSS feed")
                return []
            
            filings = []
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            for entry in feed.entries:
                try:
                    # Parse publication date with better error handling
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed and isinstance(entry.published_parsed, tuple):
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'published') and isinstance(entry.published, str):
                        # Try to parse the published string directly
                        from dateutil import parser
                        pub_date = parser.parse(entry.published)
                    else:
                        # Default to current time if no date found
                        pub_date = datetime.now()
                    
                    if pub_date < cutoff_date:
                        continue
                    
                    # Extract relevant information with proper type checking
                    title = str(entry.title) if hasattr(entry, 'title') else 'Unknown SEC Filing'
                    summary = str(getattr(entry, 'summary', ''))
                    link = str(entry.link) if hasattr(entry, 'link') else ''
                    
                    # Determine severity based on filing type
                    severity = self.classify_sec_filing_severity(title)
                    
                    # Extract ticker if possible
                    ticker = self.extract_ticker_from_sec_filing(title, summary)
                    
                    filing = {
                        'ticker': ticker,
                        'title': title,
                        'body': summary,
                        'source': 'sec',
                        'severity': severity,
                        'event_type': self.classify_sec_event_type(title),
                        'published_at': pub_date,
                        'url': link,
                        'raw_data': dict(entry)
                    }
                    
                    filings.append(filing)
                    
                except Exception as e:
                    logger.warning(f"Failed to process SEC filing entry: {e}")
                    continue
            
            logger.info(f"Collected {len(filings)} SEC filings")
            return filings
            
        except Exception as e:
            logger.error(f"Failed to collect SEC filings: {e}")
            return []
    
    def collect_rbi_announcements(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Collect RBI press releases and policy announcements.
        
        Args:
            days_back: Number of days to look back
        """
        try:
            logger.info(f"Collecting RBI announcements from last {days_back} days")
            
            response = self.session.get(settings.RBI_RSS_URL, timeout=30)
            response.raise_for_status()
            
            # Parse RSS feed
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                logger.warning("No RBI announcements found")
                return []
            
            announcements = []
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            for entry in feed.entries:
                try:
                    # Parse publication date
                    pub_date = datetime(*entry.published_parsed[:6])
                    
                    if pub_date < cutoff_date:
                        continue
                    
                    title = entry.title
                    summary = getattr(entry, 'summary', '')
                    link = entry.link
                    
                    # Classify announcement
                    severity = self.classify_rbi_severity(title, summary)
                    event_type = self.classify_rbi_event_type(title)
                    
                    # RBI announcements generally affect Indian markets
                    ticker = 'NIFTY' if self.is_market_impacting_rbi_event(title) else None
                    
                    announcement = {
                        'ticker': ticker,
                        'title': title,
                        'body': summary,
                        'source': 'rbi',
                        'severity': severity,
                        'event_type': event_type,
                        'published_at': pub_date,
                        'url': link,
                        'raw_data': dict(entry)
                    }
                    
                    announcements.append(announcement)
                    
                except Exception as e:
                    logger.warning(f"Failed to process RBI announcement: {e}")
                    continue
            
            logger.info(f"Collected {len(announcements)} RBI announcements")
            return announcements
            
        except Exception as e:
            logger.error(f"Failed to collect RBI announcements: {e}")
            return []
    
    def collect_fed_releases(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Collect Federal Reserve press releases and policy statements.
        
        Args:
            days_back: Number of days to look back
        """
        try:
            logger.info(f"Collecting Fed releases from last {days_back} days")
            
            response = self.session.get(settings.FED_RSS_URL, timeout=30)
            response.raise_for_status()
            
            # Parse RSS feed
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                logger.warning("No Fed releases found")
                return []
            
            releases = []
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            for entry in feed.entries:
                try:
                    # Parse publication date
                    pub_date = datetime(*entry.published_parsed[:6])
                    
                    if pub_date < cutoff_date:
                        continue
                    
                    title = entry.title
                    summary = getattr(entry, 'summary', '')
                    link = entry.link
                    
                    # Classify Fed release
                    severity = self.classify_fed_severity(title, summary)
                    event_type = self.classify_fed_event_type(title)
                    
                    # Fed releases generally affect US markets
                    ticker = self.determine_fed_impacted_ticker(title)
                    
                    release = {
                        'ticker': ticker,
                        'title': title,
                        'body': summary,
                        'source': 'fed',
                        'severity': severity,
                        'event_type': event_type,
                        'published_at': pub_date,
                        'url': link,
                        'raw_data': dict(entry)
                    }
                    
                    releases.append(release)
                    
                except Exception as e:
                    logger.warning(f"Failed to process Fed release: {e}")
                    continue
            
            logger.info(f"Collected {len(releases)} Fed releases")
            return releases
            
        except Exception as e:
            logger.error(f"Failed to collect Fed releases: {e}")
            return []
    
    def classify_sec_filing_severity(self, title: str) -> str:
        """Classify SEC filing severity based on filing type."""
        title_upper = title.upper()
        
        high_impact_types = ['8-K', '10-K', '10-Q', 'DEF 14A', 'FORM 8-K']
        medium_impact_types = ['S-1', 'S-3', '424B', 'FORM 4']
        
        for filing_type in high_impact_types:
            if filing_type in title_upper:
                return 'high'
        
        for filing_type in medium_impact_types:
            if filing_type in title_upper:
                return 'medium'
        
        return 'low'
    
    def classify_sec_event_type(self, title: str) -> str:
        """Classify SEC event type."""
        title_upper = title.upper()
        
        if any(term in title_upper for term in ['8-K', 'CURRENT REPORT']):
            return 'current_report'
        elif any(term in title_upper for term in ['10-K', 'ANNUAL REPORT']):
            return 'annual_report'
        elif any(term in title_upper for term in ['10-Q', 'QUARTERLY']):
            return 'quarterly_report'
        elif 'PROXY' in title_upper:
            return 'proxy_statement'
        elif any(term in title_upper for term in ['S-1', 'REGISTRATION']):
            return 'registration'
        else:
            return 'other'
    
    def extract_ticker_from_sec_filing(self, title: str, summary: str) -> Optional[str]:
        """Extract ticker symbol from SEC filing title or summary."""
        # This is a simplified implementation
        # In production, you might want to use SEC's company database
        
        content = f"{title} {summary}".upper()
        
        # Common patterns for ticker extraction
        import re
        ticker_patterns = [
            r'\(([A-Z]{1,5})\)',  # Ticker in parentheses
            r'TICKER:\s*([A-Z]{1,5})',  # Explicit ticker field
            r'SYMBOL:\s*([A-Z]{1,5})'   # Symbol field
        ]
        
        for pattern in ticker_patterns:
            match = re.search(pattern, content)
            if match:
                ticker = match.group(1)
                # Validate it's a reasonable ticker
                if 1 <= len(ticker) <= 5:
                    return ticker
        
        return None
    
    def classify_rbi_severity(self, title: str, summary: str) -> str:
        """Classify RBI announcement severity."""
        content = f"{title} {summary}".upper()
        
        high_impact_terms = ['REPO RATE', 'MONETARY POLICY', 'INTEREST RATE', 'INFLATION']
        medium_impact_terms = ['CIRCULAR', 'NOTIFICATION', 'GUIDELINES']
        
        if any(term in content for term in high_impact_terms):
            return 'high'
        elif any(term in content for term in medium_impact_terms):
            return 'medium'
        else:
            return 'low'
    
    def classify_rbi_event_type(self, title: str) -> str:
        """Classify RBI event type."""
        title_upper = title.upper()
        
        if 'MONETARY POLICY' in title_upper:
            return 'monetary_policy'
        elif 'REPO RATE' in title_upper or 'INTEREST RATE' in title_upper:
            return 'rate_decision'
        elif 'CIRCULAR' in title_upper:
            return 'circular'
        elif 'NOTIFICATION' in title_upper:
            return 'notification'
        else:
            return 'announcement'
    
    def is_market_impacting_rbi_event(self, title: str) -> bool:
        """Check if RBI event is likely to impact markets."""
        market_impact_terms = [
            'MONETARY POLICY', 'REPO RATE', 'REVERSE REPO', 'INTEREST RATE',
            'INFLATION', 'GROWTH', 'LIQUIDITY', 'FOREX', 'EXCHANGE RATE'
        ]
        
        title_upper = title.upper()
        return any(term in title_upper for term in market_impact_terms)
    
    def classify_fed_severity(self, title: str, summary: str) -> str:
        """Classify Fed release severity."""
        content = f"{title} {summary}".upper()
        
        high_impact_terms = [
            'FEDERAL FUNDS RATE', 'INTEREST RATE', 'MONETARY POLICY',
            'FOMC', 'QUANTITATIVE EASING', 'INFLATION'
        ]
        medium_impact_terms = [
            'ECONOMIC PROJECTIONS', 'BEIGE BOOK', 'FINANCIAL STABILITY'
        ]
        
        if any(term in content for term in high_impact_terms):
            return 'high'
        elif any(term in content for term in medium_impact_terms):
            return 'medium'
        else:
            return 'low'
    
    def classify_fed_event_type(self, title: str) -> str:
        """Classify Fed event type."""
        title_upper = title.upper()
        
        if 'FOMC' in title_upper and 'STATEMENT' in title_upper:
            return 'fomc_statement'
        elif 'FEDERAL FUNDS RATE' in title_upper:
            return 'rate_decision'
        elif 'BEIGE BOOK' in title_upper:
            return 'beige_book'
        elif 'ECONOMIC PROJECTIONS' in title_upper:
            return 'economic_projections'
        elif 'SPEECH' in title_upper:
            return 'speech'
        else:
            return 'press_release'
    
    def determine_fed_impacted_ticker(self, title: str) -> Optional[str]:
        """Determine which ticker is most impacted by Fed release."""
        title_upper = title.upper()
        
        # Fed releases generally impact broad market indices
        if any(term in title_upper for term in ['FOMC', 'FEDERAL FUNDS', 'MONETARY POLICY']):
            return 'SPY'  # S&P 500 as broad market proxy
        
        return None
    
    def store_regulatory_events(self, events: List[Dict[str, Any]]) -> int:
        """Store regulatory events in database."""
        if not events:
            return 0
        
        stored_count = 0
        
        for event in events:
            try:
                query = """
                    INSERT INTO regulatory_events 
                    (ticker, title, body, source, severity, event_type, published_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """
                
                params = (
                    event.get('ticker'),
                    event['title'],
                    event.get('body', ''),
                    event['source'],
                    event['severity'],
                    event['event_type'],
                    event['published_at'].isoformat()
                )
                
                event_id = db.execute_insert(query, params)
                if event_id:
                    stored_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to store regulatory event: {e}")
                continue
        
        logger.info(f"Stored {stored_count} regulatory events in database")
        return stored_count
    
    async def run_collection_cycle(self) -> Dict[str, Any]:
        """Run a complete regulatory data collection cycle."""
        start_time = datetime.now()
        logger.info("Starting regulatory data collection cycle")
        
        results = {
            'start_time': start_time.isoformat(),
            'events_collected': 0,
            'events_stored': 0,
            'sources_processed': [],
            'errors': [],
            'success': True
        }
        
        try:
            all_events = []
            
            # Collect SEC filings
            try:
                sec_events = self.collect_sec_filings(days_back=1)
                all_events.extend(sec_events)
                results['sources_processed'].append('sec')
                logger.info(f"Collected {len(sec_events)} SEC events")
            except Exception as e:
                results['errors'].append(f"SEC collection failed: {str(e)}")
                logger.error(f"SEC collection failed: {e}")
            
            # Collect RBI announcements
            try:
                rbi_events = self.collect_rbi_announcements(days_back=7)
                all_events.extend(rbi_events)
                results['sources_processed'].append('rbi')
                logger.info(f"Collected {len(rbi_events)} RBI events")
            except Exception as e:
                results['errors'].append(f"RBI collection failed: {str(e)}")
                logger.error(f"RBI collection failed: {e}")
            
            # Collect Fed releases
            try:
                fed_events = self.collect_fed_releases(days_back=7)
                all_events.extend(fed_events)
                results['sources_processed'].append('fed')
                logger.info(f"Collected {len(fed_events)} Fed events")
            except Exception as e:
                results['errors'].append(f"Fed collection failed: {str(e)}")
                logger.error(f"Fed collection failed: {e}")
            
            # Store events in database
            if all_events:
                stored_count = self.store_regulatory_events(all_events)
                results['events_collected'] = len(all_events)
                results['events_stored'] = stored_count
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Regulatory data collection completed in {duration:.2f}s: "
                       f"{results['events_collected']} collected, {results['events_stored']} stored")
            
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = duration
            
        except Exception as e:
            logger.error(f"Regulatory data collection cycle failed: {e}")
            results['success'] = False
            results['errors'].append(str(e))
        
        return results

# Global collector instance
regulatory_collector = RegulatoryCollector()

# Convenience functions for external use
def collect_regulatory_data() -> Dict[str, Any]:
    """Synchronous wrapper for regulatory data collection."""
    return asyncio.run(regulatory_collector.run_collection_cycle())

def collect_sec_only() -> List[Dict[str, Any]]:
    """Collect only SEC filings."""
    return regulatory_collector.collect_sec_filings()

def collect_fed_only() -> List[Dict[str, Any]]:
    """Collect only Fed releases."""
    return regulatory_collector.collect_fed_releases()

def collect_rbi_only() -> List[Dict[str, Any]]:
    """Collect only RBI announcements."""
    return regulatory_collector.collect_rbi_announcements()