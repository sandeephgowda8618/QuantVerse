"""
Sentence Embedder for the uRISK RAG Engine
Handles text embedding using sentence-transformers.
"""

import logging
import asyncio
from typing import List, Optional, Tuple, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np
import torch

logger = logging.getLogger(__name__)

class SentenceEmbedder:
    """Handles text embedding using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedder.
        
        Args:
            model_name: Name of the sentence transformer model to use
                      Options: 
                      - all-MiniLM-L6-v2 (384 dim, fast, good quality)
                      - all-mpnet-base-v2 (768 dim, slower, better quality)
                      - multi-qa-MiniLM-L6-cos-v1 (384 dim, optimized for Q&A)
        """
        self.model_name = model_name
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.max_seq_length = 512
        
    async def initialize(self):
        """Initialize the embedding model."""
        try:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            
            # Load model in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None, 
                self._load_model
            )
            
            logger.info(f"Model loaded successfully on device: {self.device}")
            logger.info(f"Model embedding dimension: {self.get_embedding_dimension()}")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise
    
    def _load_model(self):
        """Load the sentence transformer model (runs in thread)."""
        model = SentenceTransformer(self.model_name, device=self.device)
        
        # Configure model settings
        if hasattr(model, 'max_seq_length'):
            model.max_seq_length = self.max_seq_length
            
        return model
    
    async def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        if not self.model:
            raise ValueError("Model not initialized. Call initialize() first.")
        
        try:
            # Run embedding in thread to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                self._embed_single,
                text
            )
            
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            return []
    
    async def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Embed multiple texts in batches."""
        if not self.model:
            raise ValueError("Model not initialized. Call initialize() first.")
        
        if not texts:
            return []
        
        try:
            # Process in batches to manage memory
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Run batch embedding in thread
                loop = asyncio.get_event_loop()
                batch_embeddings = await loop.run_in_executor(
                    None,
                    self._embed_batch,
                    batch
                )
                
                all_embeddings.extend([emb.tolist() for emb in batch_embeddings])
                
                # Log progress for large batches
                if len(texts) > 100 and (i + batch_size) % 100 == 0:
                    logger.debug(f"Embedded {i + batch_size}/{len(texts)} texts")
            
            logger.info(f"Successfully embedded {len(texts)} texts")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Failed to embed texts: {e}")
            return [[] for _ in texts]  # Return empty embeddings
    
    def _embed_single(self, text: str) -> np.ndarray:
        """Embed a single text (runs in thread)."""
        if not self.model:
            raise ValueError("Model not initialized")
            
        # Truncate text if too long
        if len(text) > self.max_seq_length * 4:  # Rough character estimate
            text = text[:self.max_seq_length * 4] + "..."
        
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True  # L2 normalize for better cosine similarity
        )
        
        return np.array(embedding)
    
    def _embed_batch(self, texts: List[str]) -> np.ndarray:
        """Embed a batch of texts (runs in thread)."""
        if not self.model:
            raise ValueError("Model not initialized")
            
        # Truncate long texts
        processed_texts = []
        for text in texts:
            if len(text) > self.max_seq_length * 4:
                text = text[:self.max_seq_length * 4] + "..."
            processed_texts.append(text)
        
        embeddings = self.model.encode(
            processed_texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            batch_size=len(texts),  # Process entire batch at once
            show_progress_bar=False
        )
        
        return np.array(embeddings)
    
    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension of the model."""
        if not self.model:
            return 384 if "MiniLM" in self.model_name else 768
        
        try:
            # Use duck typing to get the dimension
            sample_emb = self.model.encode("test", convert_to_numpy=True)
            return len(sample_emb)
        except:
            return 384 if "MiniLM" in self.model_name else 768
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings."""
        try:
            # Convert to numpy arrays
            emb1 = np.array(embedding1)
            emb2 = np.array(embedding2)
            
            # Compute cosine similarity
            dot_product = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to compute similarity: {e}")
            return 0.0
    
    async def find_most_similar(
        self, 
        query_text: str, 
        candidate_texts: List[str], 
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """Find most similar texts to a query."""
        try:
            # Embed query and candidates
            query_embedding = await self.embed_text(query_text)
            candidate_embeddings = await self.embed_texts(candidate_texts)
            
            # Compute similarities
            similarities = []
            for i, candidate_emb in enumerate(candidate_embeddings):
                if candidate_emb:  # Skip empty embeddings
                    sim = self.compute_similarity(query_embedding, candidate_emb)
                    similarities.append((candidate_texts[i], sim))
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to find similar texts: {e}")
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "embedding_dimension": self.get_embedding_dimension(),
            "max_seq_length": self.max_seq_length,
            "is_initialized": self.model is not None
        }

# Global embedder instance
default_embedder = SentenceEmbedder()
