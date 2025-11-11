"""
ChromaDB Vector Store Adapter
Handles all ChromaDB operations for the uRISK RAG engine.
"""

import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import json
import uuid

from ..config.settings import settings

logger = logging.getLogger(__name__)

class ChromaVectorStore:
    """ChromaDB adapter for vector storage and retrieval."""
    
    def __init__(self, collection_name: str = "urisk_chunks", 
                 persist_directory: str = "/Users/sandeeph/Documents/QuantVerse/urisk/vector_db"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        
        # Auto-initialize to prevent "Collection not initialized" errors
        self.initialize(persist_directory)
        
    def initialize(self, persist_directory: Optional[str] = None):
        """Initialize ChromaDB client and collection."""
        try:
            if persist_directory is None:
                persist_directory = self.persist_directory
                
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=persist_directory
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "uRISK financial data chunks for RAG"}
            )
            
            logger.info(f"ChromaDB collection '{self.collection_name}' initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            # Don't raise exception - allow graceful degradation
            self.collection = None
    
    def add_documents(
        self, 
        documents: List[str], 
        metadatas: List[Dict[str, Any]], 
        ids: List[str],
        embeddings: Optional[List[Any]] = None
    ) -> bool:
        """Add documents to ChromaDB collection."""
        try:
            if not self.collection:
                raise ValueError("Collection not initialized")
                
            # Validate inputs
            if len(documents) != len(metadatas) or len(documents) != len(ids):
                raise ValueError("Documents, metadatas, and ids must have same length")
            
            # Convert metadata to strings where needed
            processed_metadatas = []
            for metadata in metadatas:
                processed_metadata = {}
                for key, value in metadata.items():
                    if isinstance(value, datetime):
                        processed_metadata[key] = value.isoformat()
                    elif isinstance(value, (dict, list)):
                        processed_metadata[key] = json.dumps(value)
                    else:
                        processed_metadata[key] = str(value)
                processed_metadatas.append(processed_metadata)
            
            # Add to collection
            if embeddings:
                self.collection.add(
                    documents=documents,
                    metadatas=processed_metadatas,
                    ids=ids,
                    embeddings=embeddings
                )
            else:
                self.collection.add(
                    documents=documents,
                    metadatas=processed_metadatas,
                    ids=ids
                )
            
            logger.info(f"Added {len(documents)} documents to ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to ChromaDB: {e}")
            return False
    
    def upsert_documents(
        self, 
        documents: List[str], 
        metadatas: List[Dict[str, Any]], 
        ids: List[str],
        embeddings: Optional[List[Any]] = None
    ) -> bool:
        """Upsert documents (add or update) to ChromaDB collection."""
        try:
            if not self.collection:
                raise ValueError("Collection not initialized")
            
            # Convert metadata to strings where needed
            processed_metadatas = []
            for metadata in metadatas:
                processed_metadata = {}
                for key, value in metadata.items():
                    if isinstance(value, datetime):
                        processed_metadata[key] = value.isoformat()
                    elif isinstance(value, (dict, list)):
                        processed_metadata[key] = json.dumps(value)
                    else:
                        processed_metadata[key] = str(value)
                processed_metadatas.append(processed_metadata)
            
            # Upsert to collection
            if embeddings:
                self.collection.upsert(
                    documents=documents,
                    metadatas=processed_metadatas,
                    ids=ids,
                    embeddings=embeddings
                )
            else:
                self.collection.upsert(
                    documents=documents,
                    metadatas=processed_metadatas,
                    ids=ids
                )
            
            logger.info(f"Upserted {len(documents)} documents to ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert documents to ChromaDB: {e}")
            return False
    
    def query_documents(
        self,
        query_texts: List[str],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Query documents from ChromaDB collection."""
        try:
            if not self.collection:
                raise ValueError("Collection not initialized")
            
            # Build query parameters
            query_params = {
                "query_texts": query_texts,
                "n_results": n_results
            }
            
            if where:
                query_params["where"] = where
                
            # Note: where_document has complex typing in chromadb, omitting for simplicity
            
            results = self.collection.query(**query_params)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to query ChromaDB: {e}")
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            if not self.collection:
                return {"count": 0, "error": "Collection not initialized"}
            
            count = self.collection.count()
            return {
                "count": count,
                "name": self.collection_name
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"count": 0, "error": str(e)}
    
    def delete_by_ids(self, ids: List[str]) -> bool:
        """Delete documents by IDs."""
        try:
            if not self.collection:
                raise ValueError("Collection not initialized")
            
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return False
    
    def delete_by_filter(self, where: Dict[str, Any]) -> bool:
        """Delete documents by metadata filter."""
        try:
            if not self.collection:
                raise ValueError("Collection not initialized")
            
            self.collection.delete(where=where)
            logger.info(f"Deleted documents matching filter: {where}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete documents by filter: {e}")
            return False

    # MEMBER EXTENSION METHODS
    # The following methods support the 3 member implementations
    
    async def retrieve_options_evidence(self, ticker: str, query_text: str, limit: int = 5) -> List[Dict]:
        """
        Retrieve options-related evidence from vector DB for Member 1
        
        Args:
            ticker: Stock ticker symbol
            query_text: User's question about options activity
            limit: Maximum number of results to return
            
        Returns:
            List[Dict]: Formatted evidence results
        """
        try:
            # Enhanced search for options content
            options_query = f"options flow volume IV calls puts {ticker} {query_text}"
            
            filter_conditions = {
                "ticker": ticker,
                "risk_type": "options"
            }
            
            results = self.query_documents(
                query_texts=[options_query],
                where=filter_conditions,
                n_results=limit
            )
            
            return self._format_query_results(results)
            
        except Exception as e:
            logger.error(f"Failed to retrieve options evidence: {e}")
            return []
    
    async def retrieve_timestamped_evidence(self, ticker: str, timestamp: datetime, window_minutes: int = 30) -> List[Dict]:
        """
        Retrieve evidence around a specific timestamp for Member 2
        
        Args:
            ticker: Stock ticker symbol
            timestamp: Target timestamp for movement analysis
            window_minutes: Window around timestamp (±minutes)
            
        Returns:
            List[Dict]: Formatted evidence results around the timestamp
        """
        try:
            # Query for movement-related content
            movement_query = f"price movement {ticker} sudden change spike"
            
            filter_conditions = {
                "ticker": ticker
                # Note: ChromaDB timestamp filtering would need metadata structure
                # For now, we'll get results and filter post-query if needed
            }
            
            results = self.query_documents(
                query_texts=[movement_query],
                where=filter_conditions,
                n_results=5
            )
            
            return self._format_query_results(results)
            
        except Exception as e:
            logger.error(f"Failed to retrieve timestamped evidence: {e}")
            return []
    
    async def retrieve_macro_evidence(self, asset: str, question: str, limit: int = 5) -> List[Dict]:
        """
        Retrieve macro/regulatory evidence from vector DB for Member 3
        
        Args:
            asset: Asset symbol (e.g., "NASDAQ", "BTC")
            question: User's question about macro impact
            limit: Maximum number of results to return
            
        Returns:
            List[Dict]: Formatted macro evidence results
        """
        try:
            # Enhanced search for macro content
            macro_query = f"macro economic federal reserve FOMC RBI regulatory {asset} {question}"
            
            filter_conditions = {
                "risk_type": "regulatory"  # Simplified filter for now
            }
            
            results = self.query_documents(
                query_texts=[macro_query],
                where=filter_conditions,
                n_results=limit
            )
            
            return self._format_query_results(results)
            
        except Exception as e:
            logger.error(f"Failed to retrieve macro evidence: {e}")
            return []
    
    def _format_query_results(self, results) -> List[Dict]:
        """
        Format ChromaDB query results for member services
        
        Args:
            results: Raw ChromaDB query results
            
        Returns:
            List[Dict]: Formatted results with source, text, timestamp
        """
        try:
            if not results or 'documents' not in results:
                return []
            
            formatted_results = []
            documents = results['documents'][0] if results['documents'] else []
            metadatas = results['metadatas'][0] if results.get('metadatas') else []
            
            for i, doc in enumerate(documents):
                metadata = metadatas[i] if i < len(metadatas) else {}
                
                formatted_results.append({
                    "source": metadata.get("source", "unknown"),
                    "text": doc,
                    "timestamp": metadata.get("timestamp", datetime.utcnow().isoformat()),
                    "ticker": metadata.get("ticker", ""),
                    "risk_type": metadata.get("risk_type", "")
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to format query results: {e}")
            return []

# Global vector store instance
vector_store = ChromaVectorStore()
