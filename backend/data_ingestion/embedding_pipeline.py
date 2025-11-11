"""
Embedding Pipeline for uRISK System

This module handles:
1. Text embedding generation using OpenAI/Hugging Face models
2. Vector database storage and retrieval using ChromaDB
3. Semantic search and similarity matching
4. Batch processing of preprocessed text chunks
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import json
import numpy as np
from dataclasses import dataclass

import openai
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from backend.config.settings import get_settings
from backend.db.postgres_handler import PostgresHandler
from backend.utils.logging_utils import get_logger

logger = get_logger(__name__)
settings = get_settings()

@dataclass
class EmbeddingResult:
    """Result of embedding operation"""
    chunk_id: str
    embedding: List[float]
    metadata: Dict[str, Any]
    success: bool
    error: Optional[str] = None

class EmbeddingGenerator:
    """Handles text embedding generation using various models"""
    
    def __init__(self):
        self.openai_client = None
        self.sentence_transformer = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize embedding models"""
        try:
            # Initialize OpenAI client if API key available
            if settings.OPENAI_API_KEY:
                openai.api_key = settings.OPENAI_API_KEY
                self.openai_client = openai
                logger.info("OpenAI embedding model initialized")
            
            # Initialize local sentence transformer as fallback
            try:
                self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Local sentence transformer model initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize sentence transformer: {e}")
                
        except Exception as e:
            logger.error(f"Error initializing embedding models: {e}")
    
    async def generate_embeddings(
        self, 
        texts: List[str], 
        model: str = "openai"
    ) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        try:
            if model == "openai" and self.openai_client:
                return await self._generate_openai_embeddings(texts)
            elif model == "sentence_transformer" and self.sentence_transformer:
                return self._generate_local_embeddings(texts)
            else:
                # Fallback to available model
                if self.openai_client:
                    return await self._generate_openai_embeddings(texts)
                elif self.sentence_transformer:
                    return self._generate_local_embeddings(texts)
                else:
                    raise ValueError("No embedding models available")
                    
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    async def _generate_openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API"""
        try:
            # Batch process to respect API limits
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = await self.openai_client.embeddings.acreate(
                    model="text-embedding-3-small",
                    input=batch,
                    encoding_format="float"
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
                
                # Rate limiting
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error with OpenAI embeddings: {e}")
            raise
    
    def _generate_local_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local sentence transformer"""
        try:
            embeddings = self.sentence_transformer.encode(
                texts, 
                convert_to_tensor=False,
                show_progress_bar=True
            )
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Error with local embeddings: {e}")
            raise

class VectorDatabase:
    """ChromaDB vector database handler"""
    
    def __init__(self):
        self.client = None
        self.collections = {}
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client"""
        try:
            # Use persistent storage
            chroma_settings = Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=settings.VECTOR_DB_PATH or "./chroma_db"
            )
            
            self.client = chromadb.Client(chroma_settings)
            logger.info("ChromaDB client initialized")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise
    
    def get_or_create_collection(
        self, 
        name: str, 
        embedding_function: Optional[Any] = None
    ) -> Any:
        """Get or create a ChromaDB collection"""
        try:
            if name not in self.collections:
                # Use default embedding function if none provided
                if embedding_function is None:
                    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                        model_name="all-MiniLM-L6-v2"
                    )
                
                collection = self.client.get_or_create_collection(
                    name=name,
                    embedding_function=embedding_function
                )
                self.collections[name] = collection
                logger.info(f"Collection '{name}' ready")
            
            return self.collections[name]
            
        except Exception as e:
            logger.error(f"Error with collection '{name}': {e}")
            raise
    
    def add_embeddings(
        self,
        collection_name: str,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> bool:
        """Add embeddings to collection"""
        try:
            collection = self.get_or_create_collection(collection_name)
            
            # Add to collection
            collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(embeddings)} embeddings to '{collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error adding embeddings to '{collection_name}': {e}")
            return False
    
    def search_similar(
        self,
        collection_name: str,
        query_embedding: List[float],
        n_results: int = 10,
        where: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Search for similar embeddings"""
        try:
            collection = self.get_or_create_collection(collection_name)
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching in '{collection_name}': {e}")
            return {}

class EmbeddingPipeline:
    """Main embedding pipeline orchestrator"""
    
    def __init__(self):
        self.db_handler = PostgresHandler()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_db = VectorDatabase()
        
        # Collection names for different data types
        self.collections = {
            'news': 'urisk_news_embeddings',
            'regulatory': 'urisk_regulatory_embeddings',
            'market': 'urisk_market_embeddings',
            'infra': 'urisk_infra_embeddings',
            'options': 'urisk_options_embeddings'
        }
    
    async def process_chunks(
        self, 
        data_type: str,
        limit: int = 100,
        reprocess: bool = False
    ) -> Dict[str, int]:
        """Process preprocessed chunks and generate embeddings"""
        try:
            # Get unprocessed chunks from preprocessing results
            query = """
                SELECT id, content, metadata, data_type, source_id, created_at
                FROM preprocessing_results 
                WHERE data_type = %s 
                AND (embedding_processed = FALSE OR embedding_processed IS NULL OR %s = TRUE)
                ORDER BY created_at DESC
                LIMIT %s
            """
            
            chunks = await self.db_handler.fetch_all(
                query, (data_type, reprocess, limit)
            )
            
            if not chunks:
                logger.info(f"No chunks to process for {data_type}")
                return {"processed": 0, "failed": 0}
            
            logger.info(f"Processing {len(chunks)} {data_type} chunks for embedding")
            
            # Prepare data for embedding
            texts = [chunk['content'] for chunk in chunks]
            chunk_ids = [str(chunk['id']) for chunk in chunks]
            
            # Generate embeddings
            embeddings = await self.embedding_generator.generate_embeddings(texts)
            
            # Prepare metadata
            metadatas = []
            for chunk in chunks:
                metadata = json.loads(chunk['metadata']) if chunk['metadata'] else {}
                metadata.update({
                    'data_type': chunk['data_type'],
                    'source_id': chunk['source_id'],
                    'created_at': chunk['created_at'].isoformat(),
                    'chunk_id': str(chunk['id'])
                })
                metadatas.append(metadata)
            
            # Store in vector database
            collection_name = self.collections.get(data_type, f'urisk_{data_type}_embeddings')
            success = self.vector_db.add_embeddings(
                collection_name=collection_name,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=chunk_ids
            )
            
            processed_count = 0
            failed_count = 0
            
            if success:
                # Update preprocessing results to mark as embedded
                update_query = """
                    UPDATE preprocessing_results 
                    SET embedding_processed = TRUE, 
                        embedding_processed_at = %s
                    WHERE id = ANY(%s)
                """
                
                await self.db_handler.execute(
                    update_query, 
                    (datetime.now(), chunk_ids)
                )
                processed_count = len(chunks)
                logger.info(f"Successfully processed {processed_count} {data_type} embeddings")
            else:
                failed_count = len(chunks)
                logger.error(f"Failed to process {failed_count} {data_type} embeddings")
            
            return {"processed": processed_count, "failed": failed_count}
            
        except Exception as e:
            logger.error(f"Error in embedding pipeline for {data_type}: {e}")
            return {"processed": 0, "failed": len(chunks) if 'chunks' in locals() else 0}
    
    async def search_relevant_content(
        self,
        query: str,
        data_types: Optional[List[str]] = None,
        n_results: int = 10,
        time_filter: Optional[Dict] = None
    ) -> Dict[str, List[Dict]]:
        """Search for relevant content across collections"""
        try:
            # Generate query embedding
            query_embeddings = await self.embedding_generator.generate_embeddings([query])
            query_embedding = query_embeddings[0]
            
            # Search in specified collections or all
            search_types = data_types or list(self.collections.keys())
            results = {}
            
            for data_type in search_types:
                collection_name = self.collections.get(data_type, f'urisk_{data_type}_embeddings')
                
                # Build where clause for time filtering
                where_clause = None
                if time_filter:
                    where_clause = time_filter
                
                search_results = self.vector_db.search_similar(
                    collection_name=collection_name,
                    query_embedding=query_embedding,
                    n_results=n_results,
                    where=where_clause
                )
                
                # Format results
                formatted_results = []
                if search_results.get('documents'):
                    for i, doc in enumerate(search_results['documents'][0]):
                        result = {
                            'content': doc,
                            'metadata': search_results['metadatas'][0][i],
                            'distance': search_results['distances'][0][i],
                            'id': search_results['ids'][0][i]
                        }
                        formatted_results.append(result)
                
                results[data_type] = formatted_results
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching relevant content: {e}")
            return {}
    
    async def run_batch_processing(self, data_types: Optional[List[str]] = None) -> Dict:
        """Run batch embedding processing for specified data types"""
        try:
            process_types = data_types or list(self.collections.keys())
            results = {}
            
            for data_type in process_types:
                logger.info(f"Starting embedding processing for {data_type}")
                result = await self.process_chunks(data_type, limit=500)
                results[data_type] = result
            
            # Summary
            total_processed = sum(r.get('processed', 0) for r in results.values())
            total_failed = sum(r.get('failed', 0) for r in results.values())
            
            logger.info(f"Batch processing complete: {total_processed} processed, {total_failed} failed")
            
            return {
                'summary': {
                    'total_processed': total_processed,
                    'total_failed': total_failed
                },
                'by_type': results
            }
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            return {'error': str(e)}

# Convenience functions for external use
async def process_embeddings_for_type(data_type: str, limit: int = 100) -> Dict:
    """Process embeddings for a specific data type"""
    pipeline = EmbeddingPipeline()
    return await pipeline.process_chunks(data_type, limit)

async def search_content(query: str, data_types: List[str] = None, n_results: int = 10) -> Dict:
    """Search for relevant content"""
    pipeline = EmbeddingPipeline()
    return await pipeline.search_relevant_content(query, data_types, n_results)

async def run_embedding_pipeline(data_types: List[str] = None) -> Dict:
    """Run the full embedding pipeline"""
    pipeline = EmbeddingPipeline()
    return await pipeline.run_batch_processing(data_types)

if __name__ == "__main__":
    # Test the embedding pipeline
    async def test_pipeline():
        try:
            pipeline = EmbeddingPipeline()
            
            # Test embedding generation
            test_texts = ["Market volatility increased today", "Fed announces rate hike"]
            embeddings = await pipeline.embedding_generator.generate_embeddings(test_texts)
            print(f"Generated {len(embeddings)} embeddings")
            
            # Test search
            results = await pipeline.search_relevant_content("market crash")
            print(f"Search results: {results}")
            
        except Exception as e:
            print(f"Test error: {e}")
    
    asyncio.run(test_pipeline())
