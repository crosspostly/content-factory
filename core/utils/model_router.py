"""
Model Router with Fallback & Retry Logic

Based on proven patterns from youtube_podcast.
Features:
  - Primary model (fast) → Fallback model (powerful)
  - Exponential backoff retries (2s, 4s, 8s)
  - Detailed logging for audit trail
  - Automatic JSON error recovery
"""

import logging
import json
import time
from typing import Callable, Any, Optional, Dict
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Model configuration
# Updated Dec 2025: Gemini 2.5 is now available and should be used
MODELS = {
    "error_analysis": {
        "primary": "qwen2.5-coder:1.5b",
        "fallback": "gemini-2.5-flash"
    },
    "script": {
        "primary": "gemini-2.5-flash",
        "fallback": "gemini-1.5-flash"
    },
    "tts": {
        "primary": "gemini-2.5-flash",
        "fallback": "gemini-1.5-flash"
    },
    "image_gen": {
        "primary": "gemini-2.5-flash",
        "fallback": "gemini-1.5-pro"
    }
}

# Retry configuration
MAX_RETRIES = 3
BASE_RETRY_DELAY = 2  # seconds
MAX_RETRY_DELAY = 16  # cap at 16 seconds


class ModelRouter:
    """
    Intelligent model selection with fallback and retry logic.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.stats = {
            "total_attempts": 0,
            "successful_attempts": 0,
            "failed_attempts": 0,
            "model_usage": {}  # {model: count}
        }
    
    def generate(
        self,
        task: str,  # "script", "tts", "image_gen", "error_analysis"
        prompt: str,
        **kwargs
    ) -> str:
        """
        Generate content with automatic fallback and retries.
        
        Args:
            task: Type of generation (defines model priority)
            prompt: The prompt to send to the model
            **kwargs: Additional params (temperature, tools, etc)
        
        Returns:
            Model response text
        
        Raises:
            RuntimeError: If all models and retries exhausted
        """
        
        models = MODELS.get(task)
        if not models:
            raise ValueError(f"Unknown task: {task}. Available: {list(MODELS.keys())}")
        
        primary_model = models["primary"]
        fallback_model = models["fallback"]
        
        logger.info(f"\n🌖 Starting generation for task: {task}")
        logger.info(f"   Primary: {primary_model}")
        logger.info(f"   Fallback: {fallback_model}")
        logger.info(f"   Retries: up to {MAX_RETRIES} per model")
        
        # Try each model
        for model_name in [primary_model, fallback_model]:
            if not model_name:
                continue
            
            # Qwen is local, not a Gemini model
            is_gemini_model = "gemini" in model_name.lower()

            response = self._try_model(model_name, prompt, is_gemini_model, **kwargs)
            if response:
                return response
        
        # All failed
        error_msg = (
            f"All models exhausted for task '{task}':\n"
            f"  Primary: {primary_model} - {MAX_RETRIES} attempts\n"
            f"  Fallback: {fallback_model} - {MAX_RETRIES} attempts\n"
            f"Total attempts: {self.stats['total_attempts']}\n"
            f"Successful: {self.stats['successful_attempts']}\n"
            f"Failed: {self.stats['failed_attempts']}\n\n"
            f"Model usage: {self.stats['model_usage']}"
        )
        logger.error(f"💩 {error_msg}")
        raise RuntimeError(error_msg)
    
    def _try_model(
        self,
        model_name: str,
        prompt: str,
        is_gemini: bool,
        **kwargs
    ) -> Optional[str]:
        """
        Try a specific model with retries.
        """
        
        logger.info(f"\n🔄 Trying model: {model_name}")
        
        for attempt in range(1, MAX_RETRIES + 1):
            self.stats["total_attempts"] += 1
            self.stats["model_usage"][model_name] = self.stats["model_usage"].get(model_name, 0) + 1
            
            try:
                logger.info(f"   Attempt {attempt}/{MAX_RETRIES}...")
                
                # Call the appropriate API
                if is_gemini:
                    response = self._call_gemini_api(model_name, prompt, **kwargs)
                else:
                    # Assuming Qwen or other local model via Ollama
                    response = self._call_ollama_api(model_name, prompt, **kwargs)

                if not response:
                    logger.warning(f"   ❌ Empty response from {model_name}")
                    continue
                
                logger.info(f"   ✅ Success! Got {len(response)} characters from {model_name}")
                self.stats["successful_attempts"] += 1
                return response
            
            except Exception as e:
                self.stats["failed_attempts"] += 1
                error_str = str(e)[:100]  # First 100 chars
                logger.warning(f"   ❌ Attempt {attempt} failed: {error_str}")
                
                if attempt < MAX_RETRIES:
                    wait_time = min(BASE_RETRY_DELAY * (2 ** (attempt - 1)), MAX_RETRY_DELAY)
                    logger.info(f"   ⏳ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"   💩 Model {model_name} exhausted all {MAX_RETRIES} retries")
        
        return None

    def _call_gemini_api(self, model: str, prompt: str, **kwargs) -> Optional[str]:
        client = genai.GenerativeModel(model)
        log_prompt = prompt[:150] + "..." if len(prompt) > 150 else prompt
        logger.debug(f"   Gemini API Request: {log_prompt}")
        response = client.generate_content(prompt, **kwargs)
        return response.text if response else None

    def _call_ollama_api(self, model: str, prompt: str, **kwargs) -> Optional[str]:
        # Placeholder for calling a local Ollama model
        # You would implement the actual API call here, e.g., using requests
        logger.info(f"   (Simulated) Calling Ollama for model {model}")
        # This is a mock. In a real scenario, you'd use requests.post
        # import requests
        # try:
        #     res = requests.post("http://localhost:11434/api/generate", 
        #         json={"model": model, "prompt": prompt, "stream": False})
        #     res.raise_for_status()
        #     return res.json()['response']
        # except Exception as e:
        #     logger.error(f"Ollama call failed: {e}")
        #     raise e
        # For now, we'll simulate a failure to test fallback
        if "qwen" in model:
             logger.warning("Simulating Ollama failure to test Gemini fallback.")
             raise ConnectionError("Ollama not running")
        return None

    def generate_json(self, task: str, prompt: str, **kwargs) -> Dict[str, Any]:
        response_text = self.generate(task, prompt, **kwargs)
        try:
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()
            return json.loads(json_str)
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"JSON parsing failed: {e}. Attempting repair...")
            repair_prompt = f'''Fix this malformed JSON and return ONLY valid JSON: {response_text[:500]}'''
            repaired = self.generate(task, repair_prompt)
            try:
                return json.loads(repaired.strip())
            except Exception as repair_error:
                logger.error(f"💩 JSON repair failed: {repair_error}")
                raise RuntimeError(f"Failed to parse/repair JSON: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        return self.stats

# Singleton and factory functions
_router_instance: Optional[ModelRouter] = None

def get_router(api_key: str) -> ModelRouter:
    global _router_instance
    if _router_instance is None:
        _router_instance = ModelRouter(api_key)
    return _router_instance

def reset_router():
    global _router_instance
    _router_instance = None
