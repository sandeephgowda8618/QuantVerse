"""
Data preprocessing pipeline for chunking and summarization.
Prepares collected data for embedding and vector storage.
"""

import logging
import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
from bs4 import BeautifulSoup

from ..config.settings import settings
from ..db.postgres_handler import db
from ..utils.logging_utils import setup_logger
# Import embedding and vector store modules
from ..embeddings.embedder import financial_embedder
from ..embeddings.vector_store import chroma_store, add_chunks_to_store

logger = setup_logger(__name__)

class PreprocessingPipeline:
    """Preprocesses data for embedding and vector storage."""
    
    def __init__(self):
        self.max_chunk_size = 500  # Maximum words per chunk
        self.min_chunk_size = 50   # Minimum words per chunk
        self.overlap_size = 50     # Words to overlap between chunks
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        try:
            # Remove HTML tags
            text = BeautifulSoup(text, 'html.parser').get_text()
            
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove special characters but keep basic punctuation
            text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)\[\]\"\']+', '', text)
            
            # Remove URLs
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
            
            # Remove email addresses
            text = re.sub(r'\S+@\S+', '', text)
            
            # Strip and return
            return text.strip()
            
        except Exception as e:
            logger.warning(f"Failed to clean text: {e}")
            return text
    
    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks suitable for embedding.
        
        Args:
            text: Text content to chunk
            metadata: Additional metadata to include with each chunk
        
        Returns:
            List of chunk dictionaries
        """
        if not text or len(text.strip()) == 0:
            return []
        
        try:
            # Clean the text first
            cleaned_text = self.clean_text(text)
            
            if len(cleaned_text.split()) < self.min_chunk_size:
                # Text is too short to chunk, return as single chunk
                chunk = {
                    'text_chunk': cleaned_text,
                    'chunk_index': 0,
                    'total_chunks': 1,
                    'word_count': len(cleaned_text.split()),
                    **(metadata or {})
                }
                return [chunk]
            
            # Split into words
            words = cleaned_text.split()
            chunks = []
            
            start_idx = 0
            chunk_index = 0
            
            while start_idx < len(words):
                # Determine end index for this chunk
                end_idx = min(start_idx + self.max_chunk_size, len(words))
                
                # Extract chunk words
                chunk_words = words[start_idx:end_idx]
                chunk_text = ' '.join(chunk_words)
                
                # Create chunk dictionary
                chunk = {
                    'text_chunk': chunk_text,
                    'chunk_index': chunk_index,
                    'word_count': len(chunk_words),
                    'start_word_idx': start_idx,
                    'end_word_idx': end_idx,
                    **(metadata or {})
                }
                
                chunks.append(chunk)
                
                # Move start index for next chunk (with overlap)
                start_idx = end_idx - self.overlap_size
                chunk_index += 1
                
                # Break if we're at the end
                if end_idx >= len(words):
                    break
            
            # Add total chunks count to all chunks
            for chunk in chunks:
                chunk['total_chunks'] = len(chunks)
            
            logger.debug(f"Created {len(chunks)} chunks from {len(words)} words")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to chunk text: {e}")
            return []
    
    def extract_news_content(self, news_record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and prepare news content for chunking."""
        try:
            # Combine headline and body for comprehensive content
            headline = news_record.get('headline', '')
            body = news_record.get('body', '')
            url = news_record.get('url', '')
            
            # Create full content
            content_parts = []
            if headline:
                content_parts.append(f"Headline: {headline}")
            if body:
                content_parts.append(f"Content: {body}")
            
            full_content = '\n\n'.join(content_parts)
            
            # Prepare metadata
            metadata = {
                'ticker': news_record.get('ticker'),
                'source': news_record.get('source', 'unknown'),
                'risk_type': 'sentiment',
                'timestamp': news_record.get('published_at') or news_record.get('inserted_at'),
                'url': url,
                'original_headline': headline,
                'content_type': 'news'
            }
            
            return {
                'content': full_content,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to extract news content: {e}")
            return {'content': '', 'metadata': {}}
    
    def extract_regulatory_content(self, regulatory_record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and prepare regulatory content for chunking."""
        try:
            title = regulatory_record.get('title', '')
            body = regulatory_record.get('body', '')
            
            # Create full content
            content_parts = []
            if title:
                content_parts.append(f"Title: {title}")
            if body:
                content_parts.append(f"Content: {body}")
            
            full_content = '\n\n'.join(content_parts)
            
            # Prepare metadata
            metadata = {
                'ticker': regulatory_record.get('ticker'),
                'source': regulatory_record.get('source', 'regulatory'),
                'risk_type': 'regulatory',
                'timestamp': regulatory_record.get('published_at'),
                'severity': regulatory_record.get('severity', 'medium'),
                'event_type': regulatory_record.get('event_type', 'announcement'),
                'content_type': 'regulatory'
            }
            
            return {
                'content': full_content,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to extract regulatory content: {e}")
            return {'content': '', 'metadata': {}}
    
    def extract_market_summary(self, ticker: str, hours_back: int = 24) -> Dict[str, Any]:
        """Create a market summary for a ticker."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            # Get recent market data
            query = """
                SELECT timestamp, close, volume, high, low
                FROM market_prices 
                WHERE ticker = %s 
                AND timestamp >= %s 
                ORDER BY timestamp DESC
                LIMIT 100
            """
            
            params = (ticker, cutoff_time.isoformat())
            results = db.execute_query(query, params)
            
            if not results:
                return {'content': '', 'metadata': {}}
            
            df = pd.DataFrame(results)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate summary statistics
            latest_price = df.iloc[0]['close']
            price_change = df.iloc[0]['close'] - df.iloc[-1]['close'] if len(df) > 1 else 0
            pct_change = (price_change / df.iloc[-1]['close'] * 100) if len(df) > 1 and df.iloc[-1]['close'] != 0 else 0
            
            avg_volume = df['volume'].mean()
            high_24h = df['high'].max()
            low_24h = df['low'].min()
            
            # Create summary content
            content = f"""
            Market Summary for {ticker}:
            Current Price: ${latest_price:.2f}
            24h Change: {pct_change:+.2f}% (${price_change:+.2f})
            24h High: ${high_24h:.2f}
            24h Low: ${low_24h:.2f}
            Average Volume: {avg_volume:,.0f}
            Data Points: {len(df)} price updates in last {hours_back} hours
            """.strip()
            
            metadata = {
                'ticker': ticker,
                'source': 'market_data',
                'risk_type': 'market',
                'timestamp': datetime.now(),
                'content_type': 'market_summary',
                'latest_price': latest_price,
                'pct_change_24h': pct_change,
                'volume_24h': df['volume'].sum()
            }
            
            return {
                'content': content,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to create market summary for {ticker}: {e}")
            return {'content': '', 'metadata': {}}
    
    def process_news_batch(self, hours_back: int = 6) -> List[Dict[str, Any]]:
        """Process recent news articles for chunking."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            query = """
                SELECT nh.ticker, nh.headline, nh.url, nh.source, nh.published_at,
                       ns.sentiment_score, ns.sentiment_label
                FROM news_headlines nh
                LEFT JOIN news_sentiment ns ON nh.id = ns.headline_id
                WHERE nh.published_at >= %s
                ORDER BY nh.published_at DESC
                LIMIT 100
            """
            
            params = (cutoff_time.isoformat(),)
            results = db.execute_query(query, params)
            
            if not results:
                logger.info("No recent news found for processing")
                return []
            
            all_chunks = []
            
            for news_record in results:
                try:
                    # Extract content and metadata
                    extracted = self.extract_news_content(news_record)
                    
                    if not extracted['content']:
                        continue
                    
                    # Add sentiment information if available
                    if news_record.get('sentiment_score') is not None:
                        extracted['metadata']['sentiment_score'] = news_record['sentiment_score']
                        extracted['metadata']['sentiment_label'] = news_record.get('sentiment_label')
                    
                    # Create chunks
                    chunks = self.chunk_text(extracted['content'], extracted['metadata'])
                    all_chunks.extend(chunks)
                    
                except Exception as e:
                    logger.warning(f"Failed to process news record: {e}")
                    continue
            
            logger.info(f"Processed {len(results)} news articles into {len(all_chunks)} chunks")
            return all_chunks
            
        except Exception as e:
            logger.error(f"Failed to process news batch: {e}")
            return []
    
    def process_regulatory_batch(self, hours_back: int = 72) -> List[Dict[str, Any]]:
        """Process recent regulatory events for chunking."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            query = """
                SELECT ticker, title, body, source, severity, event_type, published_at
                FROM regulatory_events
                WHERE published_at >= %s
                ORDER BY published_at DESC
                LIMIT 50
            """
            
            params = (cutoff_time.isoformat(),)
            results = db.execute_query(query, params)
            
            if not results:
                logger.info("No recent regulatory events found for processing")
                return []
            
            all_chunks = []
            
            for regulatory_record in results:
                try:
                    # Extract content and metadata
                    extracted = self.extract_regulatory_content(regulatory_record)
                    
                    if not extracted['content']:
                        continue
                    
                    # Create chunks
                    chunks = self.chunk_text(extracted['content'], extracted['metadata'])
                    all_chunks.extend(chunks)
                    
                except Exception as e:
                    logger.warning(f"Failed to process regulatory record: {e}")
                    continue
            
            logger.info(f"Processed {len(results)} regulatory events into {len(all_chunks)} chunks")
            return all_chunks
            
        except Exception as e:
            logger.error(f"Failed to process regulatory batch: {e}")
            return []
    
    def process_market_summaries(self, tickers: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Process market summaries for all or specified tickers."""
        try:
            if tickers is None:
                from ..config.settings import TRACKED_ASSETS
                tickers = []
                for asset_type, ticker_list in TRACKED_ASSETS.items():
                    tickers.extend(ticker_list)
            
            all_chunks = []
            
            for ticker in tickers:
                try:
                    # Create market summary
                    extracted = self.extract_market_summary(ticker)
                    
                    if not extracted['content']:
                        continue
                    
                    # Create chunks (market summaries are usually short)
                    chunks = self.chunk_text(extracted['content'], extracted['metadata'])
                    all_chunks.extend(chunks)
                    
                except Exception as e:
                    logger.warning(f"Failed to process market summary for {ticker}: {e}")
                    continue
            
            logger.info(f"Processed market summaries for {len(tickers)} tickers into {len(all_chunks)} chunks")
            return all_chunks
            
        except Exception as e:
            logger.error(f"Failed to process market summaries: {e}")
            return []
    
    def extract_infra_content(self, infra_record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and prepare infrastructure event content for chunking."""
        try:
            title = infra_record.get('service_name', '')
            description = infra_record.get('description', '')
            status = infra_record.get('status', '')
            
            # Create full content
            content_parts = []
            if title:
                content_parts.append(f"Service: {title}")
            if status:
                content_parts.append(f"Status: {status}")
            if description:
                content_parts.append(f"Details: {description}")
            
            full_content = '\n\n'.join(content_parts)
            
            # Prepare metadata
            metadata = {
                'ticker': infra_record.get('ticker'),
                'source': infra_record.get('source', 'infrastructure'),
                'risk_type': 'infrastructure',
                'timestamp': infra_record.get('timestamp'),
                'service_name': title,
                'status': status,
                'severity': infra_record.get('severity', 'medium'),
                'content_type': 'infrastructure'
            }
            
            return {
                'content': full_content,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to extract infrastructure content: {e}")
            return {'content': '', 'metadata': {}}
    
    def process_infra_batch(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Process recent infrastructure events for chunking."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            query = """
                SELECT ticker, service_name, status, description, source, severity, timestamp
                FROM infrastructure_status
                WHERE timestamp >= %s
                ORDER BY timestamp DESC
                LIMIT 50
            """
            
            params = (cutoff_time.isoformat(),)
            results = db.execute_query(query, params)
            
            if not results:
                logger.info("No recent infrastructure events found for processing")
                return []
            
            all_chunks = []
            
            for infra_record in results:
                try:
                    # Extract content and metadata
                    extracted = self.extract_infra_content(infra_record)
                    
                    if not extracted['content']:
                        continue
                    
                    # Create chunks
                    chunks = self.chunk_text(extracted['content'], extracted['metadata'])
                    all_chunks.extend(chunks)
                    
                except Exception as e:
                    logger.warning(f"Failed to process infrastructure record: {e}")
                    continue
            
            logger.info(f"Processed {len(results)} infrastructure events into {len(all_chunks)} chunks")
            return all_chunks
            
        except Exception as e:
            logger.error(f"Failed to process infrastructure batch: {e}")
            return []
    
    async def run_preprocessing_cycle(self) -> Dict[str, Any]:
        """Run a complete preprocessing cycle."""
        start_time = datetime.now()
        logger.info("Starting data preprocessing cycle")
        
        results = {
            'start_time': start_time.isoformat(),
            'chunks_created': 0,
            'content_types_processed': [],
            'errors': [],
            'success': True
        }
        
        try:
            all_chunks = []
            
            # Process news articles
            try:
                news_chunks = self.process_news_batch(hours_back=6)
                all_chunks.extend(news_chunks)
                results['content_types_processed'].append(f'news ({len(news_chunks)} chunks)')
            except Exception as e:
                results['errors'].append(f"News processing failed: {str(e)}")
                logger.error(f"News processing failed: {e}")
            
            # Process regulatory events
            try:
                regulatory_chunks = self.process_regulatory_batch(hours_back=72)
                all_chunks.extend(regulatory_chunks)
                results['content_types_processed'].append(f'regulatory ({len(regulatory_chunks)} chunks)')
            except Exception as e:
                results['errors'].append(f"Regulatory processing failed: {str(e)}")
                logger.error(f"Regulatory processing failed: {e}")
            
            # Process market summaries
            try:
                market_chunks = self.process_market_summaries()
                all_chunks.extend(market_chunks)
                results['content_types_processed'].append(f'market ({len(market_chunks)} chunks)')
            except Exception as e:
                results['errors'].append(f"Market processing failed: {str(e)}")
                logger.error(f"Market processing failed: {e}")
            
            # Process infrastructure events
            try:
                infra_chunks = self.process_infra_batch(hours_back=24)
                all_chunks.extend(infra_chunks)
                results['content_types_processed'].append(f'infrastructure ({len(infra_chunks)} chunks)')
            except Exception as e:
                results['errors'].append(f"Infrastructure processing failed: {str(e)}")
                logger.error(f"Infrastructure processing failed: {e}")
            
            # Process infrastructure events
            try:
                infra_chunks = self.process_infra_batch(hours_back=24)
                all_chunks.extend(infra_chunks)
                results['content_types_processed'].append(f'infrastructure ({len(infra_chunks)} chunks)')
            except Exception as e:
                results['errors'].append(f"Infrastructure processing failed: {str(e)}")
                logger.error(f"Infrastructure processing failed: {e}")
            
            results['chunks_created'] = len(all_chunks)
            
            # Generate embeddings and store in vector database
            if all_chunks:
                try:
                    # Generate embeddings for all chunks
                    logger.info(f"Generating embeddings for {len(all_chunks)} chunks")
                    embedded_chunks = financial_embedder.embed_chunks(all_chunks)
                    
                    # Group chunks by content type for proper vector store organization
                    chunks_by_type = {}
                    for chunk in embedded_chunks:
                        content_type = chunk.get('content_type', 'general')
                        if content_type not in chunks_by_type:
                            chunks_by_type[content_type] = []
                        chunks_by_type[content_type].append(chunk)
                    
                    # Store in vector database by content type
                    total_stored = 0
                    vector_store_results = {}
                    
                    for content_type, type_chunks in chunks_by_type.items():
                        try:
                            store_result = add_chunks_to_store(type_chunks, content_type)
                            vector_store_results[content_type] = store_result
                            total_stored += store_result.get('added_count', 0)
                            
                            if not store_result.get('success', False):
                                results['errors'].extend(store_result.get('errors', []))
                                
                        except Exception as e:
                            error_msg = f"Vector store failed for {content_type}: {str(e)}"
                            results['errors'].append(error_msg)
                            logger.error(error_msg)
                    
                    results['chunks_embedded'] = len(embedded_chunks)
                    results['chunks_stored_in_vector_db'] = total_stored
                    results['vector_store_results'] = vector_store_results
                    
                    logger.info(f"Successfully stored {total_stored} chunks in vector database")
                    
                except Exception as e:
                    error_msg = f"Embedding/vector store pipeline failed: {str(e)}"
                    results['errors'].append(error_msg)
                    logger.error(error_msg)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Preprocessing completed in {duration:.2f}s: "
                       f"{results['chunks_created']} chunks created")
            
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = duration
            results['chunks'] = all_chunks  # Include chunks in results
            
        except Exception as e:
            logger.error(f"Preprocessing cycle failed: {e}")
            results['success'] = False
            results['errors'].append(str(e))
        
        return results

    async def process_all_data(self) -> Dict[str, Any]:
        """
        Comprehensive data processing pipeline for all data types.
        Processes market data, news, regulatory events, and generates embeddings.
        """
        logger.info("🚀 Starting comprehensive data processing and embedding pipeline")
        start_time = datetime.now()
        
        results = {
            'success': True,
            'start_time': start_time.isoformat(),
            'stages': {},
            'total_documents_processed': 0,
            'total_chunks_created': 0,
            'embeddings_created': 0,
            'vector_store_documents': 0,
            'errors': []
        }
        
        try:
            # Stage 1: Process market data and news
            logger.info("📊 Processing market data and news...")
            market_news_result = await self.run_preprocessing_cycle()
            results['stages']['market_news'] = market_news_result
            
            if market_news_result.get('success'):
                results['total_documents_processed'] += market_news_result.get('documents_processed', 0)
                results['total_chunks_created'] += market_news_result.get('chunks_created', 0)
                results['embeddings_created'] += market_news_result.get('chunks_embedded', 0)
                results['vector_store_documents'] += market_news_result.get('chunks_stored_in_vector_db', 0)
            
            # Stage 2: Process regulatory events
            logger.info("🏛️ Processing regulatory events...")
            try:
                reg_query = """
                SELECT re.title, re.body as description, re.severity as impact_level, re.published_at as event_date,
                       re.source as source_agency, a.name as asset_name, a.ticker
                FROM regulatory_events re
                LEFT JOIN assets a ON re.ticker = a.ticker
                WHERE re.inserted_at >= NOW() - INTERVAL '30 days'
                ORDER BY re.published_at DESC
                LIMIT 100
                """
                
                reg_records = await db.fetch_all(reg_query)
                reg_chunks = []
                
                for record in reg_records:
                    # Create comprehensive regulatory content
                    content = f"""
                    Regulatory Event: {record['title']}
                    
                    Description: {record['description']}
                    Impact Level: {record['impact_level']}
                    Source Agency: {record['source_agency']}
                    Event Date: {record['event_date']}
                    """
                    
                    if record['asset_name']:
                        content += f"\nAffected Asset: {record['asset_name']} ({record['ticker']})"
                    
                    metadata = {
                        'source': 'regulatory_events',
                        'type': 'regulatory',
                        'impact_level': record['impact_level'],
                        'source_agency': record['source_agency'],
                        'event_date': record['event_date'].isoformat() if record['event_date'] else None,
                        'ticker': record['ticker']
                    }
                    
                    chunks = self.chunk_text(content, metadata)
                    reg_chunks.extend(chunks)
                
                # Embed and store regulatory chunks
                if reg_chunks:
                    embedded_reg_chunks = financial_embedder.embed_chunks(reg_chunks)
                    if embedded_reg_chunks:
                        vector_result = add_chunks_to_store(embedded_reg_chunks, "regulatory_events")
                        
                        reg_result = {
                            'success': True,
                            'documents_processed': len(reg_records),
                            'chunks_created': len(reg_chunks),
                            'chunks_embedded': len(embedded_reg_chunks),
                            'chunks_stored': vector_result.get('stored', 0)
                        }
                        
                        results['stages']['regulatory'] = reg_result
                        results['total_documents_processed'] += reg_result['documents_processed']
                        results['total_chunks_created'] += reg_result['chunks_created']
                        results['embeddings_created'] += reg_result['chunks_embedded']
                        results['vector_store_documents'] += reg_result['chunks_stored']
                        
                        logger.info(f"✅ Processed {len(reg_records)} regulatory events into {len(embedded_reg_chunks)} embeddings")
                
            except Exception as e:
                logger.error(f"❌ Regulatory processing failed: {e}")
                results['stages']['regulatory'] = {'success': False, 'error': str(e)}
                results['errors'].append(f"Regulatory processing: {e}")
            
            # Stage 3: Process infrastructure events
            logger.info("🖥️ Processing infrastructure events...")
            try:
                infra_query = """
                SELECT platform as service_name, 'incident' as status, description as message, 
                       0 as response_time_ms, started_at as timestamp
                FROM infra_incidents
                WHERE started_at >= NOW() - INTERVAL '7 days'
                ORDER BY started_at DESC
                LIMIT 200
                """
                
                infra_records = await db.fetch_all(infra_query)
                infra_chunks = []
                
                for record in infra_records:
                    content = f"""
                    Infrastructure Status: {record['service_name']}
                    
                    Status: {record['status']}
                    Message: {record['message']}
                    Response Time: {record['response_time_ms']}ms
                    Timestamp: {record['timestamp']}
                    """
                    
                    metadata = {
                        'source': 'infrastructure_status',
                        'type': 'infrastructure',
                        'service_name': record['service_name'],
                        'status': record['status'],
                        'response_time_ms': record['response_time_ms'],
                        'timestamp': record['timestamp'].isoformat() if record['timestamp'] else None
                    }
                    
                    chunks = self.chunk_text(content, metadata)
                    infra_chunks.extend(chunks)
                
                # Embed and store infrastructure chunks
                if infra_chunks:
                    embedded_infra_chunks = financial_embedder.embed_chunks(infra_chunks)
                    if embedded_infra_chunks:
                        vector_result = add_chunks_to_store(embedded_infra_chunks, "infrastructure_status")
                        
                        infra_result = {
                            'success': True,
                            'documents_processed': len(infra_records),
                            'chunks_created': len(infra_chunks),
                            'chunks_embedded': len(embedded_infra_chunks),
                            'chunks_stored': vector_result.get('stored', 0)
                        }
                        
                        results['stages']['infrastructure'] = infra_result
                        results['total_documents_processed'] += infra_result['documents_processed']
                        results['total_chunks_created'] += infra_result['chunks_created']
                        results['embeddings_created'] += infra_result['chunks_embedded']
                        results['vector_store_documents'] += infra_result['chunks_stored']
                        
                        logger.info(f"✅ Processed {len(infra_records)} infrastructure events into {len(embedded_infra_chunks)} embeddings")
                
            except Exception as e:
                logger.error(f"❌ Infrastructure processing failed: {e}")
                results['stages']['infrastructure'] = {'success': False, 'error': str(e)}
                results['errors'].append(f"Infrastructure processing: {e}")
            
            # Calculate final results
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results.update({
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'success': len(results['errors']) == 0
            })
            
            logger.info(f"🎉 Comprehensive data processing completed in {duration:.2f}s:")
            logger.info(f"   📄 Documents processed: {results['total_documents_processed']}")
            logger.info(f"   📝 Chunks created: {results['total_chunks_created']}")
            logger.info(f"   🧠 Embeddings generated: {results['embeddings_created']}")
            logger.info(f"   🗃️ Vector DB documents: {results['vector_store_documents']}")
            
            if results['errors']:
                logger.warning(f"   ⚠️ Errors encountered: {len(results['errors'])}")
            
        except Exception as e:
            logger.error(f"❌ Comprehensive data processing failed: {e}")
            results['success'] = False
            results['errors'].append(str(e))
        
        return results

# Global preprocessing instance
preprocessing_pipeline = PreprocessingPipeline()

# Convenience functions for external use
def preprocess_data() -> Dict[str, Any]:
    """Synchronous wrapper for data preprocessing."""
    return asyncio.run(preprocessing_pipeline.run_preprocessing_cycle())

def chunk_text_content(text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Chunk a text string with optional metadata."""
    return preprocessing_pipeline.chunk_text(text, metadata)

def process_single_news_article(headline: str, body: str = "", metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Process a single news article into chunks."""
    news_record = {
        'headline': headline,
        'body': body,
        **(metadata or {})
    }
    
    extracted = preprocessing_pipeline.extract_news_content(news_record)
    return preprocessing_pipeline.chunk_text(extracted['content'], extracted['metadata'])
