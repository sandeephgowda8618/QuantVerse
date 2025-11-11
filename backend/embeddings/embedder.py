"""
Text embedding pipeline for financial content.
Converts chunked text data into vector embeddings for semantic search and RAG.
"""

import logging
import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import numpy as np
import hashlib
import re
from collections import Counter
import torch

# Set up logging first
logger = logging.getLogger(__name__)

# LangChain imports for professional embedding pipeline
try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.embeddings import HuggingFaceInstructEmbeddings
    from langchain_core.documents import Document
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    logger.warning(f"LangChain not available: {e}")
    LANGCHAIN_AVAILABLE = False
    OpenAIEmbeddings = None
    HuggingFaceEmbeddings = None

# Fallback to direct imports if needed
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

from ..config.settings import settings

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialEmbedder:
    """
    Advanced LangChain-powered embedding pipeline for financial content.
    
    Follows README requirements:
    - Normalized text before embedding
    - Only meaningful information embedded
    - Proper chunk sizes (150-350 characters)
    - Metadata with every vector chunk
    - Financial domain-specific processing
    - Multi-model support with fallbacks
    """
    
    def __init__(self):
        self.embedder = None
        self.model_type = None
        self.embedding_dim = None
        self.device = self._detect_device()
        self.normalize_embeddings = getattr(settings, 'EMBEDDING_NORMALIZE', True)
        self.batch_size = getattr(settings, 'EMBEDDING_BATCH_SIZE', 32)
        self.financial_keywords = self._load_financial_keywords()
        
        # Performance tracking
        self.total_embeddings = 0
        self.total_time = 0.0
        
        # Initialize based on available resources
        self._initialize_embedder()
    
    def _initialize_embedder(self):
        """Initialize the best available embedding model with LangChain."""
        try:
            # Try LangChain HuggingFace embeddings first (more reliable)
            if LANGCHAIN_AVAILABLE:
                try:
                    # Set HuggingFace token if available
                    import os
                    if hasattr(settings, 'HF_TOKEN') and settings.HF_TOKEN:
                        os.environ['HF_TOKEN'] = settings.HF_TOKEN
                        os.environ['HUGGINGFACE_HUB_TOKEN'] = settings.HF_TOKEN
                    
                    # Use configured model or high-quality defaults
                    primary_model = getattr(settings, 'EMBEDDER_MODEL_NAME', 'sentence-transformers/all-mpnet-base-v2')
                    
                    model_options = [
                        primary_model,  # User configured or default high-quality
                        "sentence-transformers/all-mpnet-base-v2",  # High quality general
                        "sentence-transformers/all-MiniLM-L6-v2",  # Fast and efficient
                        "sentence-transformers/multi-qa-MiniLM-L6-cos-v1",  # Good for Q&A
                        "BAAI/bge-base-en-v1.5"  # Strong general purpose
                    ]
                    
                    # Remove duplicates while preserving order
                    model_options = list(dict.fromkeys(model_options))
                    
                    for model_name in model_options:
                        try:
                            # Initialize with optimal device and settings
                            model_kwargs = {'device': self.device}
                            if hasattr(settings, 'HF_TOKEN') and settings.HF_TOKEN:
                                model_kwargs['token'] = settings.HF_TOKEN
                            
                            encode_kwargs = {
                                'normalize_embeddings': True,  # Built-in normalization
                                'batch_size': self.batch_size
                            }
                            
                            self.embedder = HuggingFaceEmbeddings(
                                model_name=model_name,
                                model_kwargs=model_kwargs,
                                encode_kwargs=encode_kwargs
                            )
                            self.model_type = 'langchain_huggingface'
                            # Test embedding to get dimension
                            test_emb = self.embedder.embed_query("test")
                            self.embedding_dim = len(test_emb)
                            logger.info(f"✅ Initialized LangChain HuggingFace embeddings: {model_name} (dim: {self.embedding_dim})")
                            return
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to load {model_name}: {e}")
                            continue
                    
                except Exception as e:
                    logger.error(f"❌ Failed to initialize LangChain HuggingFace: {e}")
            
            # Try LangChain OpenAI embeddings as fallback
            if LANGCHAIN_AVAILABLE and hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
                try:
                    self.embedder = OpenAIEmbeddings(
                        openai_api_key=settings.OPENAI_API_KEY,
                        model="text-embedding-3-small",  # Latest model
                        dimensions=1536
                    )
                    self.model_type = 'langchain_openai'
                    self.embedding_dim = 1536
                    logger.info("✅ Initialized LangChain OpenAI embeddings (text-embedding-3-small)")
                    return
                except Exception as e:
                    logger.warning(f"⚠️ Failed to initialize LangChain OpenAI embeddings: {e}")
            
            # Fallback to direct sentence transformers
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                try:
                    model_options = [
                        'all-MiniLM-L6-v2',
                        'multi-qa-MiniLM-L6-cos-v1',
                        'all-mpnet-base-v2'
                    ]
                    
                    for model_name in model_options:
                        try:
                            self.embedder = SentenceTransformer(model_name)
                            self.model_type = 'sentence_transformer'
                            self.embedding_dim = self.embedder.get_sentence_embedding_dimension()
                            logger.info(f"✅ Fallback to SentenceTransformer: {model_name}")
                            return
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to load {model_name}: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"❌ SentenceTransformer fallback failed: {e}")
            
            # Ultimate fallback - simple hash-based embedder
            logger.warning("🔄 Using simple hash-based fallback embedder")
            self.model_type = 'simple_fallback'
            self.embedding_dim = 384
            
        except Exception as e:
            logger.error(f"❌ All embedding initialization failed: {e}")
            self.model_type = 'simple_fallback'
            self.embedding_dim = 384
    
    def embed_text(self, text: str) -> Optional[np.ndarray]:
        """
        Generate embedding for a single text with financial preprocessing.
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector as numpy array, or None if failed
        """
        if not text or not text.strip():
            return None
        
        try:
            start_time = time.time()
            
            # Preprocess text for financial domain
            processed_text = self._preprocess_financial_text(text)
            
            if self.model_type == 'langchain_openai':
                embedding = self.embedder.embed_query(processed_text)
                embedding = np.array(embedding)
            elif self.model_type == 'langchain_huggingface':
                embedding = self.embedder.embed_query(processed_text)
                embedding = np.array(embedding)
            elif self.model_type == 'sentence_transformer':
                embedding = self.embedder.encode(processed_text, convert_to_numpy=True)
            elif self.model_type == 'simple_fallback':
                embedding = self._embed_with_simple_fallback(processed_text)
            else:
                logger.error("No embedding model initialized")
                return None
            
            # Apply additional normalization if needed
            if embedding is not None:
                embedding = self._normalize_embedding(embedding)
                
                # Track performance
                elapsed = time.time() - start_time
                self.total_embeddings += 1
                self.total_time += elapsed
                
                return embedding
            
            return None
                
        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            return None
    
    def _detect_device(self) -> str:
        """Detect best available device for embedding computation."""
        device_override = getattr(settings, 'EMBEDDING_DEVICE', 'auto')
        
        if device_override != 'auto':
            logger.info(f"🔧 Using device override: {device_override}")
            return device_override
        
        if torch.cuda.is_available():
            device = 'cuda'
            logger.info(f"🚀 Using CUDA device: {torch.cuda.get_device_name()}")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = 'mps'
            logger.info("🍎 Using Apple MPS device")
        else:
            device = 'cpu'
            logger.info("💻 Using CPU device")
        
        return device
    
    def _normalize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """L2 normalize embedding vector for better similarity search."""
        if not self.normalize_embeddings:
            return embedding
        
        norm = np.linalg.norm(embedding) + 1e-12
        return embedding / norm
    
    def _load_financial_keywords(self) -> set:
        """Load financial domain keywords for preprocessing."""
        return {
            # Market terms
            'earnings', 'revenue', 'profit', 'loss', 'margin', 'ebitda', 'dividend',
            'volatility', 'volume', 'liquidity', 'spread', 'premium', 'strike',
            'options', 'futures', 'derivatives', 'swap', 'hedge', 'arbitrage',
            
            # Market events
            'ipo', 'merger', 'acquisition', 'spinoff', 'bankruptcy', 'restructuring',
            'guidance', 'outlook', 'forecast', 'estimate', 'consensus', 'beat', 'miss',
            
            # Regulatory
            'sec', 'finra', 'cftc', 'fed', 'fomc', 'regulation', 'compliance',
            'filing', 'disclosure', 'investigation', 'penalty', 'settlement',
            
            # Risk terms
            'risk', 'exposure', 'default', 'credit', 'counterparty', 'systemic',
            'stress', 'scenario', 'var', 'drawdown', 'correlation', 'beta'
        }
    
    def _preprocess_financial_text(self, text: str) -> str:
        """
        Preprocess text for financial domain embedding.
        Follows README requirements for normalized text.
        """
        # Remove excessive whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Convert to lowercase for consistency
        text = text.lower()
        
        # Normalize financial symbols (keep structure)
        text = re.sub(r'\$([a-z]+)', r'ticker_\1', text)  # $AAPL -> ticker_aapl
        text = re.sub(r'(\d+)%', r'\1 percent', text)     # 5% -> 5 percent
        text = re.sub(r'\$(\d+)', r'\1 dollars', text)    # $100 -> 100 dollars
        
        # Enhance financial terms
        for keyword in self.financial_keywords:
            if keyword in text:
                text = text.replace(keyword, f"financial_{keyword}")
        
        # Ensure meaningful content only (minimum 10 characters)
        if len(text.strip()) < 10:
            return text.strip()
        
        # Truncate if too long (optimal chunk size per README)
        if len(text) > 350:
            text = text[:347] + '...'
        
        return text.strip()
    
    def _embed_with_simple_fallback(self, text: str) -> Optional[np.ndarray]:
        """Generate simple hash-based embedding as ultimate fallback."""
        try:
            # Create multiple hash representations for better diversity
            text_hash = hashlib.md5(text.encode()).hexdigest()
            sha_hash = hashlib.sha1(text.encode()).hexdigest()
            
            # Combine different hash representations
            combined = text_hash + sha_hash
            
            # Convert to numeric vector
            embedding = np.array([ord(c) / 255.0 for c in combined[:self.embedding_dim]])
            
            # Pad if needed
            if len(embedding) < self.embedding_dim:
                # Use text statistics for padding
                text_stats = [
                    len(text) / 1000.0,  # Length feature
                    text.count(' ') / len(text),  # Word density
                    sum(1 for c in text if c.isupper()) / len(text),  # Uppercase ratio
                    sum(1 for c in text if c.isdigit()) / len(text),  # Digit ratio
                ]
                
                # Repeat stats to fill dimension
                while len(embedding) < self.embedding_dim:
                    remaining = min(len(text_stats), self.embedding_dim - len(embedding))
                    embedding = np.concatenate([embedding, text_stats[:remaining]])
                    
            return embedding[:self.embedding_dim].astype(np.float32)
            
        except Exception as e:
            logger.error(f"Simple fallback embedding failed: {e}")
            # Return zero vector as last resort
            return np.zeros(self.embedding_dim, dtype=np.float32)
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[Optional[np.ndarray]]:
        """
        Generate embeddings for a batch of texts with financial preprocessing.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process at once
        
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        try:
            start_time = time.time()
            
            # Preprocess all texts
            processed_texts = [self._preprocess_financial_text(text) for text in texts]
            embeddings = []
            
            # Process in batches
            for i in range(0, len(processed_texts), batch_size):
                batch = processed_texts[i:i + batch_size]
                
                if self.model_type == 'langchain_openai':
                    batch_embeddings = [np.array(emb) for emb in self.embedder.embed_documents(batch)]
                elif self.model_type == 'langchain_huggingface':
                    batch_embeddings = [np.array(emb) for emb in self.embedder.embed_documents(batch)]
                elif self.model_type == 'sentence_transformer':
                    batch_embeddings = [emb for emb in self.embedder.encode(batch, convert_to_numpy=True)]
                else:
                    batch_embeddings = [self._embed_with_simple_fallback(text) for text in batch]
                
                # Apply normalization to each embedding
                normalized_embeddings = []
                for emb in batch_embeddings:
                    if emb is not None:
                        emb = self._normalize_embedding(emb)
                    normalized_embeddings.append(emb)
                
                embeddings.extend(normalized_embeddings)
            
            # Track performance
            elapsed = time.time() - start_time
            self.total_embeddings += len(embeddings)
            self.total_time += elapsed
            
            tokens_per_sec = len(embeddings) / elapsed if elapsed > 0 else 0
            avg_latency = elapsed / len(embeddings) if embeddings else 0
            
            logger.info(f"✅ Generated {len(embeddings)} embeddings from {len(texts)} texts")
            logger.info(f"📊 Performance: {tokens_per_sec:.1f} emb/sec, {avg_latency*1000:.1f}ms avg latency")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Batch embedding failed: {e}")
            return [None] * len(texts)
    
    def embed_documents_with_metadata(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Embed documents with rich metadata following README requirements.
        
        Args:
            documents: List of document dicts with 'content' and metadata
            
        Returns:
            Documents enhanced with embeddings and financial metadata
        """
        if not documents:
            return []
            
        try:
            enhanced_docs = []
            
            for doc in documents:
                content = doc.get('content', '')
                if not content:
                    continue
                    
                # Generate embedding
                embedding = self.embed_text(content)
                
                if embedding is not None:
                    # Extract financial metadata
                    metadata = self._extract_financial_metadata(content)
                    
                    enhanced_doc = {
                        **doc,  # Original document data
                        'embedding': embedding.tolist(),  # Convert to list for JSON serialization
                        'embedding_model': self.model_type,
                        'embedding_dim': self.embedding_dim,
                        'processed_content': self._preprocess_financial_text(content),
                        'financial_metadata': metadata,
                        'chunk_quality_score': self._calculate_chunk_quality(content),
                        'embedding_timestamp': datetime.utcnow().isoformat()
                    }
                    enhanced_docs.append(enhanced_doc)
                else:
                    # Document with embedding failure
                    enhanced_docs.append({
                        **doc,
                        'embedding': None,
                        'embedding_error': True,
                        'embedding_timestamp': datetime.utcnow().isoformat()
                    })
            
            logger.info(f"✅ Enhanced {len(enhanced_docs)} documents with financial embeddings")
            return enhanced_docs
            
        except Exception as e:
            logger.error(f"❌ Document embedding failed: {e}")
            return documents  # Return original documents on failure
    
    def _extract_financial_metadata(self, text: str) -> Dict[str, Any]:
        """Extract financial domain metadata from text."""
        metadata = {
            'financial_keywords': [],
            'sentiment_indicators': [],
            'numerical_data': [],
            'tickers_mentioned': [],
            'financial_concepts': []
        }
        
        try:
            text_lower = text.lower()
            
            # Extract financial keywords
            for keyword in self.financial_keywords:
                if keyword in text_lower:
                    metadata['financial_keywords'].append(keyword)
            
            # Extract tickers (common patterns)
            ticker_patterns = re.findall(r'\b[A-Z]{2,5}\b', text)
            metadata['tickers_mentioned'] = list(set(ticker_patterns))
            
            # Extract numerical data
            numbers = re.findall(r'\d+\.?\d*%?', text)
            metadata['numerical_data'] = numbers[:10]  # Limit to first 10
            
            # Sentiment indicators
            positive_words = ['gain', 'profit', 'up', 'rise', 'bullish', 'strong', 'beat']
            negative_words = ['loss', 'drop', 'fall', 'bearish', 'weak', 'miss', 'decline']
            
            for word in positive_words:
                if word in text_lower:
                    metadata['sentiment_indicators'].append(f'positive_{word}')
                    
            for word in negative_words:
                if word in text_lower:
                    metadata['sentiment_indicators'].append(f'negative_{word}')
            
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Failed to extract financial metadata: {e}")
            return metadata
    
    def _calculate_chunk_quality(self, text: str) -> float:
        """Calculate quality score for text chunk (0-1)."""
        try:
            score = 0.0
            
            # Length score (optimal 150-350 chars per README)
            length = len(text)
            if 150 <= length <= 350:
                score += 0.3
            elif 100 <= length < 150 or 350 < length <= 500:
                score += 0.2
            elif length > 50:
                score += 0.1
            
            # Financial content score
            financial_count = sum(1 for keyword in self.financial_keywords if keyword in text.lower())
            score += min(financial_count * 0.1, 0.3)
            
            # Information density (non-whitespace ratio)
            non_whitespace = len(text.replace(' ', ''))
            if length > 0:
                density = non_whitespace / length
                score += density * 0.2
            
            # Numerical data presence
            if re.search(r'\d+', text):
                score += 0.1
            
            # Sentence structure
            sentences = text.count('.') + text.count('!') + text.count('?')
            if sentences > 0:
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate chunk quality: {e}")
            return 0.5  # Default neutral score
    
    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for text chunks with metadata.
        
        Args:
            chunks: List of chunk dictionaries with 'text_chunk' and metadata
        
        Returns:
            Chunks with added 'embedding' field
        """
        if not chunks:
            return []
        
        try:
            # Extract texts for embedding
            texts = []
            for chunk in chunks:
                text = chunk.get('text_chunk', '')
                if text:
                    texts.append(text)
                else:
                    texts.append('')  # Empty text for missing chunks
            
            # Generate embeddings
            embeddings = self.embed_batch(texts)
            
            # Add embeddings back to chunks
            enhanced_chunks = []
            for i, chunk in enumerate(chunks):
                enhanced_chunk = chunk.copy()
                
                if i < len(embeddings) and embeddings[i] is not None:
                    enhanced_chunk['embedding'] = embeddings[i].tolist()  # Convert to list for JSON serialization
                    enhanced_chunk['embedding_model'] = self.model_type
                    enhanced_chunk['embedding_dim'] = self.embedding_dim
                else:
                    enhanced_chunk['embedding'] = None
                    enhanced_chunk['embedding_error'] = True
                
                enhanced_chunks.append(enhanced_chunk)
            
            success_count = sum(1 for chunk in enhanced_chunks if chunk.get('embedding') is not None)
            logger.info(f"Successfully embedded {success_count}/{len(chunks)} chunks")
            
            return enhanced_chunks
            
        except Exception as e:
            logger.error(f"Failed to embed chunks: {e}")
            # Return chunks without embeddings
            return [{**chunk, 'embedding': None, 'embedding_error': True} for chunk in chunks]
    
    def get_embedding_info(self) -> Dict[str, Any]:
        """Get information about the current embedding model."""
        model_name = 'unknown'
        
        if self.model_type == 'langchain_openai':
            model_name = 'text-embedding-3-small'
        elif self.model_type == 'langchain_huggingface' and hasattr(self.embedder, 'model_name'):
            model_name = self.embedder.model_name
        elif self.model_type == 'sentence_transformer' and hasattr(self.embedder, '_model_name'):
            model_name = self.embedder._model_name
        elif self.model_type == 'simple_fallback':
            model_name = 'hash-based-fallback'
        
        avg_latency = self.total_time / self.total_embeddings if self.total_embeddings > 0 else 0
        
        return {
            'model_type': self.model_type,
            'embedding_dimension': self.embedding_dim,
            'model_name': model_name,
            'device': self.device,
            'initialized': self.model_type is not None,
            'langchain_enabled': LANGCHAIN_AVAILABLE,
            'normalization_enabled': self.normalize_embeddings,
            'batch_size': self.batch_size,
            'financial_keywords_count': len(self.financial_keywords),
            'supports_batch_processing': True,
            'preprocessing_enabled': True,
            'total_embeddings_generated': self.total_embeddings,
            'average_latency_ms': avg_latency * 1000,
            'is_production_ready': self.model_type not in ['simple_fallback'],
            'chunk_quality_threshold': 0.45
        }

# Backward compatibility class name
class Embedder(FinancialEmbedder):
    """Alias for backward compatibility."""
    pass

# Global embedder instance
financial_embedder = FinancialEmbedder()

# Convenience functions for external use
def embed_text(text: str) -> Optional[np.ndarray]:
    """Generate embedding for a single text with financial preprocessing."""
    return financial_embedder.embed_text(text)

def embed_batch(texts: List[str]) -> List[Optional[np.ndarray]]:
    """Generate embeddings for a batch of texts."""
    return financial_embedder.embed_batch(texts)

def embed_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate embeddings for documents with rich metadata."""
    return financial_embedder.embed_documents_with_metadata(documents)

def get_embedder_info() -> Dict[str, Any]:
    """Get embedding model information."""
    return financial_embedder.get_embedding_info()

def preprocess_financial_text(text: str) -> str:
    """Preprocess text for financial domain."""
    return financial_embedder._preprocess_financial_text(text)
