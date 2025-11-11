"""
Centralized LLM Manager for QuantVerse uRISK System

This singleton manages Ollama server lifecycle, model loading, and provides
persistent session management for fast inference across all backend services.

Implements the 6-step lifecycle:
1. FastAPI startup triggers LLM warm-up
2. Ollama server health check and auto-start
3. Model loading (llama3.1) with warm inference
4. Persistent aiohttp session with keep_alive=20m
5. Request reuse → 1-2s latency instead of 10-15s
6. Graceful shutdown with session cleanup

Updated with 4 specialized prompt templates:
- Core Risk Assessment (general analysis)
- Options Flow Interpreter (institutional positioning)  
- Market Move Explainer (sudden price movements)
- Macro Gap Forecaster (overnight gaps from macro events)
"""

import asyncio
import aiohttp
import logging
import subprocess
import json
import time
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import os
import signal

from ..config.settings import settings
from .prompt_templates import PromptBuilder, IntentRouter

logger = logging.getLogger(__name__)

class LLMManager:
    """
    Singleton LLM Manager for Ollama
    
    Provides:
    - Automatic Ollama server management
    - Model downloading and warm-up
    - Persistent session for fast inference
    - Circuit breaker for fault tolerance
    - Graceful shutdown handling
    """
    
    _instance: Optional['LLMManager'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            # Use configuration from settings
            self.session: Optional[aiohttp.ClientSession] = None
            self.ollama_url = settings.OLLAMA_URL
            self.model_name = settings.OLLAMA_MODEL
            self.keep_alive_duration = settings.OLLAMA_KEEP_ALIVE
            self.timeout_seconds = settings.OLLAMA_TIMEOUT
            self.max_retries = settings.OLLAMA_MAX_RETRIES
            self.auto_start = settings.OLLAMA_AUTO_START
            
            # Process and state management
            self.ollama_process = None
            self.is_ready = False
            self.circuit_breaker_open = False
            self.circuit_breaker_failures = 0
            self.circuit_breaker_reset_time = 0
            self.max_failures = 3
            self.circuit_breaker_timeout = 60  # seconds
            self.prompt_builder = PromptBuilder()
            self.intent_router = IntentRouter()
            self._initialized = True
    
    @classmethod
    async def initialize(cls) -> 'LLMManager':
        """
        Initialize the LLM manager with full startup sequence.
        Call this during FastAPI startup.
        """
        instance = cls()
        if instance.is_ready:
            logger.info("[LLM] LLM Manager already initialized")
            return instance
            
        logger.info("[LLM] Starting LLM Manager initialization...")
        start_time = time.time()
        
        try:
            # Step 1: Check and start Ollama server
            await instance._ensure_ollama_running()
            
            # Step 2: Check and download model if needed
            await instance._ensure_model_available()
            
            # Step 3: Create persistent session
            await instance._create_session()
            
            # Step 4: Warm up model with test query
            await instance._warm_up_model()
            
            instance.is_ready = True
            init_time = (time.time() - start_time) * 1000
            
            logger.info(f"[LLM] LLM Manager initialized successfully in {init_time:.2f}ms")
            logger.info(f"[LLM] Model: {instance.model_name}")
            logger.info(f"[LLM] Ollama URL: {instance.ollama_url}")
            
            return instance
            
        except Exception as e:
            logger.error(f"[LLM] Failed to initialize LLM Manager: {e}")
            instance.is_ready = False
            raise
    
    @classmethod
    def get_instance(cls) -> 'LLMManager':
        """Get the singleton instance (must be initialized first)"""
        if cls._instance is None or not cls._instance.is_ready:
            raise RuntimeError("LLM Manager not initialized. Call LLMManager.initialize() first.")
        return cls._instance
    
    async def _ensure_ollama_running(self):
        """Check if Ollama server is running, start it if not"""
        try:
            # Test if Ollama is responding
            async with aiohttp.ClientSession() as temp_session:
                async with temp_session.get(f"{self.ollama_url}/api/tags", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        logger.info("[LLM] Ollama server is already running")
                        return
        except Exception:
            pass
        
        if not self.auto_start:
            raise Exception(f"Ollama server not running at {self.ollama_url} and auto-start is disabled. Please start Ollama manually.")
        
        logger.info("[LLM] Ollama server not detected, attempting to start...")
        
        try:
            # Try to start Ollama server
            self.ollama_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            # Wait for server to be ready
            for attempt in range(30):  # 30 seconds timeout
                try:
                    async with aiohttp.ClientSession() as temp_session:
                        async with temp_session.get(f"{self.ollama_url}/api/tags", timeout=aiohttp.ClientTimeout(total=2)) as response:
                            if response.status == 200:
                                logger.info(f"[LLM] Ollama server started successfully (attempt {attempt + 1})")
                                return
                except Exception:
                    pass
                
                await asyncio.sleep(1)
            
            raise Exception("Ollama server failed to start within 30 seconds")
            
        except FileNotFoundError:
            raise Exception("Ollama not installed. Please install Ollama first: https://ollama.ai")
        except Exception as e:
            raise Exception(f"Failed to start Ollama server: {e}")
    
    async def _ensure_model_available(self):
        """Check if model is available, download if not"""
        try:
            async with aiohttp.ClientSession() as temp_session:
                async with temp_session.get(f"{self.ollama_url}/api/tags") as response:
                    if response.status != 200:
                        raise Exception("Could not get model list from Ollama")
                    
                    data = await response.json()
                    models = [model.get("name", "") for model in data.get("models", [])]
                    
                    if self.model_name in models:
                        logger.info(f"[LLM] Model {self.model_name} is available")
                        return
            
            logger.info(f"[LLM] Model {self.model_name} not found, downloading...")
            
            # Download model using ollama pull
            process = subprocess.Popen(
                ["ollama", "pull", self.model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Failed to download model: {stderr}")
            
            logger.info(f"[LLM] Model {self.model_name} downloaded successfully")
            
        except Exception as e:
            raise Exception(f"Failed to ensure model availability: {e}")
    
    async def _create_session(self):
        """Create persistent aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
        
        # Create session with optimized settings
        connector = aiohttp.TCPConnector(
            limit=10,  # Connection pool limit
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
        )
        
        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)  # Use settings timeout
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        
        logger.info(f"[LLM] Persistent aiohttp session created with {self.timeout_seconds}s timeout")
    
    async def _warm_up_model(self):
        """Warm up model with a test query to load weights into memory"""
        logger.info("[LLM] Starting model warm-up...")
        start_time = time.time()
        
        try:
            warm_up_prompt = "Hello, respond with just 'Ready' to confirm you are working."
            
            response = await self._generate_internal(warm_up_prompt)
            
            warm_up_time = (time.time() - start_time) * 1000
            logger.info(f"[LLM] Warm-up prompt completed in {warm_up_time:.2f}ms")
            logger.info(f"[LLM] Model response: {response[:50]}...")
            
        except Exception as e:
            logger.warning(f"[LLM] Warm-up failed, but continuing: {e}")
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text using the persistent LLM session.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated text response
        """
        if not self.is_ready:
            raise RuntimeError("LLM Manager not initialized")
        
        # Check circuit breaker
        if self._is_circuit_breaker_open():
            raise Exception("LLM circuit breaker is open, service temporarily unavailable")
        
        try:
            response = await self._generate_internal(prompt, system_prompt)
            self._reset_circuit_breaker()
            return response
            
        except Exception as e:
            self._record_failure()
            logger.error(f"[LLM] Generation failed: {e}")
            raise
    
    async def _generate_internal(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Internal generation method"""
        if not self.session or self.session.closed:
            await self._create_session()
        
        if not self.session:
            raise RuntimeError("Failed to create session")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 1500,
                "keep_alive": self.keep_alive_duration  # Use settings keep_alive duration
            }
        }
        
        start_time = time.time()
        
        async with self.session.post(f"{self.ollama_url}/api/chat", json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Ollama API error {response.status}: {error_text}")
            
            data = await response.json()
            
            if "message" not in data:
                raise Exception(f"Unexpected response format: {data}")
            
            content = data["message"].get("content", "")
            
            inference_time = (time.time() - start_time) * 1000
            logger.debug(f"[LLM] Using persistent session, inference time: {inference_time:.2f}ms")
            
            return content
    
    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open"""
        if not self.circuit_breaker_open:
            return False
        
        if time.time() > self.circuit_breaker_reset_time:
            self.circuit_breaker_open = False
            self.circuit_breaker_failures = 0
            logger.info("[LLM] Circuit breaker reset")
            return False
        
        return True
    
    def _record_failure(self):
        """Record a failure for circuit breaker"""
        self.circuit_breaker_failures += 1
        logger.warning(f"[LLM] Failure #{self.circuit_breaker_failures}")
        
        if self.circuit_breaker_failures >= self.max_failures:
            self.circuit_breaker_open = True
            self.circuit_breaker_reset_time = time.time() + self.circuit_breaker_timeout
            logger.error(f"[LLM] Circuit breaker opened for {self.circuit_breaker_timeout} seconds")
    
    def _reset_circuit_breaker(self):
        """Reset circuit breaker on successful request"""
        if self.circuit_breaker_failures > 0:
            self.circuit_breaker_failures = 0
    
    async def shutdown(self):
        """Graceful shutdown - close sessions and stop processes"""
        logger.info("[LLM] Starting LLM Manager shutdown...")
        
        try:
            # Close aiohttp session
            if self.session and not self.session.closed:
                await self.session.close()
                logger.info("[LLM] HTTP session closed")
            
            # Stop Ollama process if we started it
            if self.ollama_process:
                try:
                    # Kill the process group to stop all child processes
                    os.killpg(os.getpgid(self.ollama_process.pid), signal.SIGTERM)
                    self.ollama_process.wait(timeout=10)
                    logger.info("[LLM] Ollama process terminated")
                except (subprocess.TimeoutExpired, ProcessLookupError):
                    # Force kill if graceful shutdown fails
                    try:
                        os.killpg(os.getpgid(self.ollama_process.pid), signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    logger.warning("[LLM] Ollama process force killed")
                except Exception as e:
                    logger.warning(f"[LLM] Error stopping Ollama process: {e}")
            
            self.is_ready = False
            logger.info("[LLM] LLM Manager shutdown completed")
            
        except Exception as e:
            logger.error(f"[LLM] Error during shutdown: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on LLM system"""
        health_status = {
            "status": "healthy",
            "model": self.model_name,
            "ready": self.is_ready,
            "circuit_breaker": {
                "open": self.circuit_breaker_open,
                "failures": self.circuit_breaker_failures
            },
            "session": "active" if self.session and not self.session.closed else "closed"
        }
        
        try:
            if self.is_ready:
                # Quick test generation
                start_time = time.time()
                response = await self._generate_internal("Test")
                response_time = (time.time() - start_time) * 1000
                
                health_status["response_time_ms"] = round(response_time, 2)
                health_status["test_response"] = response[:50] + "..." if len(response) > 50 else response
            else:
                health_status["status"] = "not_ready"
                
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status
    
    # ===== SPECIALIZED PROMPT METHODS =====
    
    async def generate_with_auto_routing(
        self, 
        user_query: str, 
        retrieved_chunks: List[Any], 
        **kwargs
    ) -> Tuple[str, str]:
        """
        Generate response using automatic intent detection and routing
        
        Args:
            user_query: User's question
            retrieved_chunks: Relevant chunks from vector search
            **kwargs: Additional generation parameters
            
        Returns:
            Tuple[str, str]: (generated_response, detected_intent)
        """
        if not self.is_ready:
            raise Exception("LLM Manager not ready. Please initialize first.")
        
        # Build prompt with automatic routing
        prompt, detected_intent = PromptBuilder.build_prompt(user_query, retrieved_chunks)
        
        logger.info(f"[LLM] Auto-routing query to '{detected_intent}' module")
        
        # Generate response
        response = await self.generate(prompt, **kwargs)
        
        return response, detected_intent
    
    async def generate_core_risk_analysis(
        self,
        user_query: str,
        retrieved_chunks: List[Any],
        **kwargs
    ) -> str:
        """Generate response using Core Risk Assessment template"""
        prompt = PromptBuilder.build_specialized_prompt(user_query, retrieved_chunks, "core_risk")
        logger.info("[LLM] Using Core Risk Assessment template")
        return await self.generate(prompt, **kwargs)
    
    async def generate_options_flow_analysis(
        self,
        user_query: str,
        retrieved_chunks: List[Any],
        **kwargs
    ) -> str:
        """Generate response using Options Flow Interpreter template"""
        prompt = PromptBuilder.build_specialized_prompt(user_query, retrieved_chunks, "options_flow")
        logger.info("[LLM] Using Options Flow Interpreter template")
        return await self.generate(prompt, **kwargs)
    
    async def generate_market_move_explanation(
        self,
        user_query: str,
        retrieved_chunks: List[Any],
        **kwargs
    ) -> str:
        """Generate response using Market Move Explainer template"""
        prompt = PromptBuilder.build_specialized_prompt(user_query, retrieved_chunks, "market_move")
        logger.info("[LLM] Using Market Move Explainer template")
        return await self.generate(prompt, **kwargs)
    
    async def generate_macro_gap_forecast(
        self,
        user_query: str,
        retrieved_chunks: List[Any],
        **kwargs
    ) -> str:
        """Generate response using Macro Gap Forecaster template"""
        prompt = PromptBuilder.build_specialized_prompt(user_query, retrieved_chunks, "macro_gap")
        logger.info("[LLM] Using Macro Gap Forecaster template")
        return await self.generate(prompt, **kwargs)
    
    def detect_query_intent(self, user_query: str) -> str:
        """
        Detect the intent of a user query for routing purposes
        
        Args:
            user_query: User's question
            
        Returns:
            str: Detected intent ('core_risk', 'options_flow', 'market_move', 'macro_gap')
        """
        return IntentRouter.detect_intent(user_query)
```
