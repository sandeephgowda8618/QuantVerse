"""
Vector database adapter for Chroma DB.
Handles storage and retrieval of embedded financial content for RAG.
"""

import logging
import asyncio
import uuid
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np

# Disable ChromaDB telemetry to prevent spam messages
os.environ["CHROMA_TELEMETRY_STRICT"] = "false"

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import json
import os

# Disable ChromaDB telemetry to prevent spam messages
try:
    os.environ["ANONYMIZED_TELEMETRY"] = "False"
except:
    pass

from ..config.settings import settings
from ..utils.logging_utils import setup_logger
from .embedder import financial_embedder

logger = setup_logger(__name__)

class ChromaVectorStore:
    """
    ChromaDB-based vector store for financial content retrieval.
    Handles collections for different content types and semantic search.
    """
    
    def __init__(self):
        self.client = None
        self.collections: Dict[str, Any] = {}
        self.embedding_function = None
        
        # Collection names for different content types
        self.collection_names = {
            'news': 'financial_news',
            'regulatory': 'regulatory_events', 
            'market': 'market_summaries',
            'anomalies': 'anomaly_alerts',
            'general': 'mixed_financial_content'
        }
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client and collections."""
        try:
            # Set up persistent storage
            persist_directory = getattr(settings, 'CHROMA_PERSIST_DIR', './vector_db')
            
            # Ensure directory exists
            os.makedirs(persist_directory, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create or get collections
            self._setup_collections()
            
            logger.info(f"ChromaDB initialized with persistent storage at {persist_directory}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def _setup_collections(self):
        """Create or retrieve collections for different content types."""
        try:
            # Custom embedding function that uses our embedder
            embedding_function = self._create_embedding_function()
            
            for content_type, collection_name in self.collection_names.items():
                try:
                    # Try to get existing collection
                    collection = self.client.get_collection(
                        name=collection_name,
                        embedding_function=embedding_function
                    )
                    logger.debug(f"Retrieved existing collection: {collection_name}")
                    
                except Exception:
                    # Create new collection if it doesn't exist
                    collection = self.client.create_collection(
                        name=collection_name,
                        embedding_function=embedding_function,
                        metadata={
                            "hnsw:space": "cosine",
                            "content_type": content_type,
                            "created_at": datetime.now().isoformat()
                        }
                    )
                    logger.info(f"Created new collection: {collection_name}")
                
                self.collections[content_type] = collection
                
        except Exception as e:
            logger.error(f"Failed to setup collections: {e}")
            raise
    
    def _create_embedding_function(self):
        """Create custom embedding function for ChromaDB."""
        class FinancialEmbeddingFunction(embedding_functions.EmbeddingFunction):
            def __call__(self, input: List[str]) -> List[List[float]]:
                embeddings = financial_embedder.embed_batch(input)
                
                # Convert numpy arrays to lists and handle None values
                result = []
                for emb in embeddings:
                    if emb is not None:
                        result.append(emb.tolist())
                    else:
                        # Return zero vector if embedding failed
                        dim = financial_embedder.embedding_dim or 384
                        result.append([0.0] * dim)
                
                return result
        
        return FinancialEmbeddingFunction()
    
    def add_chunks(self, chunks: List[Dict[str, Any]], content_type: str = 'general') -> Dict[str, Any]:
        """
        Add embedded chunks to the vector store.
        
        Args:
            chunks: List of chunk dictionaries with embeddings and metadata
            content_type: Type of content ('news', 'regulatory', 'market', etc.)
        
        Returns:
            Status information about the operation
        """
        if not chunks:
            return {'success': True, 'added_count': 0, 'errors': []}
        
        try:
            collection = self.collections.get(content_type, self.collections['general'])
            
            # Prepare data for ChromaDB
            documents = []
            metadatas = []
            ids = []
            embeddings = []
            
            for chunk in chunks:
                try:
                    # Generate unique ID
                    chunk_id = str(uuid.uuid4())
                    
                    # Extract text content
                    text_content = chunk.get('text_chunk', '')
                    if not text_content:
                        continue
                    
                    # Prepare metadata (ChromaDB requires flat dict with string/number values)
                    metadata = self._prepare_metadata(chunk)
                    
                    # Use pre-computed embedding if available
                    embedding = chunk.get('embedding')
                    if embedding:
                        if isinstance(embedding, np.ndarray):
                            embedding = embedding.tolist()
                        embeddings.append(embedding)
                    else:
                        # Generate embedding on the fly
                        emb = financial_embedder.embed_text(text_content)
                        if emb is not None:
                            embeddings.append(emb.tolist())
                        else:
                            continue  # Skip if no embedding available
                    
                    documents.append(text_content)
                    metadatas.append(metadata)
                    ids.append(chunk_id)
                    
                except Exception as e:
                    logger.warning(f"Failed to prepare chunk for storage: {e}")
                    continue
            
            if not documents:
                return {'success': True, 'added_count': 0, 'errors': ['No valid chunks to add']}
            
            # Add to collection
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            
            logger.info(f"Added {len(documents)} chunks to {content_type} collection")
            
            return {
                'success': True,
                'added_count': len(documents),
                'collection': content_type,
                'errors': []
            }
            
        except Exception as e:
            logger.error(f"Failed to add chunks to vector store: {e}")
            return {
                'success': False,
                'added_count': 0,
                'collection': content_type,
                'errors': [str(e)]
            }
    
    def _prepare_metadata(self, chunk: Dict[str, Any]) -> Dict[str, Union[str, int, float]]:
        """
        Prepare metadata for ChromaDB (must be flat dict with primitive types).
        
        Args:
            chunk: Chunk dictionary with metadata
        
        Returns:
            Flattened metadata dictionary
        """
        metadata = {}
        
        # Extract core fields
        for key in ['ticker', 'source', 'risk_type', 'content_type', 'chunk_index', 
                   'total_chunks', 'word_count', 'sentiment_score', 'anomaly_score', 'severity']:
            value = chunk.get(key)
            if value is not None:
                if isinstance(value, (str, int, float, bool)):
                    metadata[key] = value
                else:
                    metadata[key] = str(value)
        
        # Handle timestamp
        timestamp = chunk.get('timestamp')
        if timestamp:
            if isinstance(timestamp, datetime):
                metadata['timestamp'] = timestamp.isoformat()
            elif isinstance(timestamp, str):
                metadata['timestamp'] = timestamp
        
        # Add processed timestamp
        metadata['processed_at'] = datetime.now().isoformat()
        
        # Handle nested metadata
        for nested_key in ['details', 'metadata']:
            nested_data = chunk.get(nested_key, {})
            if isinstance(nested_data, dict):
                for k, v in nested_data.items():
                    if isinstance(v, (str, int, float, bool)):
                        metadata[f"{nested_key}_{k}"] = v
                    else:
                        metadata[f"{nested_key}_{k}"] = str(v)
        
        return metadata
    
    def search_similar(self, query: str, content_types: Optional[List[str]] = None, 
                      limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar content across collections.
        
        Args:
            query: Search query text
            content_types: List of content types to search (defaults to all)
            limit: Maximum number of results per collection
            filters: Metadata filters for search
        
        Returns:
            List of search results with scores and metadata
        """
        if not query.strip():
            return []
        
        try:
            if content_types is None:
                content_types = list(self.collections.keys())
            
            all_results = []
            
            for content_type in content_types:
                if content_type not in self.collections:
                    continue
                
                try:
                    collection = self.collections[content_type]
                    
                    # Prepare where clause for filtering
                    where_clause = {}
                    if filters:
                        # Convert filters to ChromaDB format
                        for key, value in filters.items():
                            if isinstance(value, list):
                                where_clause[key] = {"$in": value}
                            else:
                                where_clause[key] = value
                    
                    # Perform search
                    results = collection.query(
                        query_texts=[query],
                        n_results=limit,
                        where=where_clause if where_clause else None,
                        include=['documents', 'metadatas', 'distances']
                    )
                    
                    # Process results
                    if results['documents'] and results['documents'][0]:
                        for i, doc in enumerate(results['documents'][0]):
                            result = {
                                'content': doc,
                                'content_type': content_type,
                                'score': 1.0 - results['distances'][0][i],  # Convert distance to similarity
                                'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                            }
                            all_results.append(result)
                    
                except Exception as e:
                    logger.warning(f"Search failed for {content_type} collection: {e}")
                    continue
            
            # Sort by score and limit total results
            all_results.sort(key=lambda x: x['score'], reverse=True)
            
            logger.debug(f"Search returned {len(all_results)} results for query: '{query[:50]}...'")
            return all_results[:limit * len(content_types)]
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def search_by_ticker(self, ticker: str, content_types: Optional[List[str]] = None,
                        limit: int = 20, hours_back: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for content related to a specific ticker.
        
        Args:
            ticker: Ticker symbol to search for
            content_types: Content types to search
            limit: Maximum results
            hours_back: Only return content from last N hours
        
        Returns:
            List of matching content
        """
        try:
            filters = {'ticker': ticker}
            
            # Add time filter if specified
            if hours_back:
                cutoff_time = datetime.now() - timedelta(hours=hours_back)
                # Note: This would require proper timestamp filtering in ChromaDB
                # For now, we'll filter post-search
            
            # Use ticker as search query to leverage semantic similarity
            results = self.search_similar(
                query=f"financial news about {ticker}",
                content_types=content_types,
                limit=limit,
                filters=filters
            )
            
            # Apply time filtering if needed
            if hours_back:
                cutoff_time = datetime.now() - timedelta(hours=hours_back)
                filtered_results = []
                
                for result in results:
                    timestamp_str = result['metadata'].get('timestamp')
                    if timestamp_str:
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            if timestamp >= cutoff_time:
                                filtered_results.append(result)
                        except:
                            # Include if timestamp parsing fails
                            filtered_results.append(result)
                    else:
                        filtered_results.append(result)
                
                results = filtered_results
            
            logger.debug(f"Found {len(results)} results for ticker {ticker}")
            return results
            
        except Exception as e:
            logger.error(f"Ticker search failed for {ticker}: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics about all collections."""
        stats = {}
        
        for content_type, collection in self.collections.items():
            try:
                count = collection.count()
                stats[content_type] = {
                    'document_count': count,
                    'collection_name': collection.name
                }
            except Exception as e:
                stats[content_type] = {
                    'document_count': 0,
                    'error': str(e)
                }
        
        return stats
    
    def clear_old_content(self, content_type: str, days_old: int = 30) -> int:
        """
        Clear old content from a collection.
        
        Args:
            content_type: Type of content to clear
            days_old: Clear content older than this many days
        
        Returns:
            Number of documents cleared
        """
        try:
            if content_type not in self.collections:
                return 0
            
            collection = self.collections[content_type]
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Note: ChromaDB doesn't have built-in date-based deletion
            # This would require getting all documents, filtering by date, and deleting by ID
            # For now, we'll just log the intent
            logger.info(f"Old content cleanup requested for {content_type} (>{days_old} days)")
            
            # Implementation would go here for actual cleanup
            return 0
            
        except Exception as e:
            logger.error(f"Failed to clear old content: {e}")
            return 0
    
    def reset_collections(self):
        """Reset all collections (useful for testing)."""
        try:
            if self.client is None:
                logger.warning("ChromaDB client not initialized")
                return
                
            # Delete existing collections
            for content_type, collection_name in self.collection_names.items():
                try:
                    self.client.delete_collection(collection_name)
                    logger.debug(f"Deleted existing collection: {collection_name}")
                except Exception:
                    pass  # Collection might not exist
            
            # Clear collections dict
            self.collections.clear()
            
            # Re-setup collections
            self._setup_collections()
            
            logger.info("Collections reset successfully")
            
        except Exception as e:
            logger.error(f"Failed to reset collections: {e}")
            raise

# Global vector store instance
chroma_store = ChromaVectorStore()

# Convenience functions for external use
def add_chunks_to_store(chunks: List[Dict[str, Any]], content_type: str = 'general') -> Dict[str, Any]:
    """Add chunks to vector store."""
    return chroma_store.add_chunks(chunks, content_type)

def search_content(query: str, content_types: Optional[List[str]] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for similar content."""
    return chroma_store.search_similar(query, content_types, limit)

def search_ticker_content(ticker: str, limit: int = 20, hours_back: Optional[int] = None) -> List[Dict[str, Any]]:
    """Search content for a specific ticker."""
    return chroma_store.search_by_ticker(ticker, limit=limit, hours_back=hours_back)

def get_store_stats() -> Dict[str, Dict[str, Any]]:
    """Get vector store statistics."""
    return chroma_store.get_collection_stats()

# Backward compatibility alias
VectorStore = ChromaVectorStore