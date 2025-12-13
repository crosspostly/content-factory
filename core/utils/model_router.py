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
# Updated Dec 2025: gemini-2.0-flash deprecated, using gemini-2.5-flash as primary
MODELS = {
    "script": {
        "primary": "gemini-2.0-flash-exp",
        "fallback": "gemini-1.5-flash"
    },
    "tts": {
        "primary": "gemini-2.0-flash-exp",
        "fallback": "gemini-1.5-flash"
    },
    "image_gen": {
        "primary": "gemini-2.0-flash-exp",
        "fallback": "gemini-1.5-flash"
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
        task: str,  # "script", "tts", "image_gen"
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
        for model in [primary_model, fallback_model]:
            if not model:
                continue
            
            response = self._try_model(model, prompt, task, **kwargs)
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
        model: str,
        prompt: str,
        task: str,
        **kwargs
    ) -> Optional[str]:
        """
        Try a specific model with retries.
        """
        
        logger.info(f"\n🔄 Trying model: {model}")
        
        for attempt in range(1, MAX_RETRIES + 1):
            self.stats["total_attempts"] += 1
            self.stats["model_usage"][model] = self.stats["model_usage"].get(model, 0) + 1
            
            try:
                logger.info(f"   Attempt {attempt}/{MAX_RETRIES}...")
                
                # Call the model
                response = self._call_api(model, prompt, **kwargs)
                
                if not response or not response.text:
                    logger.warning(f"   ❌ Empty response")
                    continue
                
                logger.info(f"   ✅ Success! Got {len(response.text)} characters")
                self.stats["successful_attempts"] += 1
                return response.text
            
            except Exception as e:
                self.stats["failed_attempts"] += 1
                error_str = str(e)[:100]  # First 100 chars
                logger.warning(f"   ❌ Attempt {attempt} failed: {error_str}")
                
                if attempt < MAX_RETRIES:
                    # Calculate backoff: 2, 4, 8
                    wait_time = min(
                        BASE_RETRY_DELAY * (2 ** (attempt - 1)),
                        MAX_RETRY_DELAY
                    )
                    logger.info(f"   ⏳ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"   💩 Model {model} exhausted all {MAX_RETRIES} retries")
        
        return None
    
    def _call_api(
        self,
        model: str,
        prompt: str,
        **kwargs
    ) -> Any:
        """
        Call Gemini API with specific model.
        """
        client = genai.GenerativeModel(model)
        
        # Log request (sanitized)
        log_prompt = prompt[:150] + "..." if len(prompt) > 150 else prompt
        logger.debug(f"   API Request: {log_prompt}")
        
        response = client.generate_content(prompt, **kwargs)
        
        return response
    
    def generate_json(
        self,
        task: str,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate and parse JSON response.
        Includes automatic JSON repair.
        """
        
        response_text = self.generate(task, prompt, **kwargs)
        
        # Try to parse JSON
        try:
            # Handle markdown code blocks
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()
            
            logger.debug(f"Parsing JSON: {json_str[:100]}...")
            return json.loads(json_str)
        
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}. Attempting repair...")
            
            # Try to repair malformed JSON
            try:
                repair_prompt = f"""
                Fix this malformed JSON and return ONLY the corrected JSON object:
                {response_text[:500]}
                
                Rules:
                - Remove trailing commas
                - Fix unclosed brackets
                - Escape unescaped quotes
                - Return ONLY valid JSON, no markdown, no explanation
                """
                
                repaired = self.generate(task, repair_prompt)
                logger.debug(f"Repairing JSON: {repaired[:100]}...")
                
                if "```json" in repaired:
                    json_str = repaired.split("```json")[1].split("```")[0].strip()
                elif "```" in repaired:
                    json_str = repaired.split("```")[1].split("```")[0].strip()
                else:
                    json_str = repaired.strip()
                
                result = json.loads(json_str)
                logger.info("✅ JSON repaired successfully")
                return result
            
            except Exception as repair_error:
                logger.error(f"💩 JSON repair failed: {repair_error}")
                raise RuntimeError(f"Failed to parse and repair JSON response: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Return generation statistics.
        """
        return {
            "total_attempts": self.stats["total_attempts"],
            "successful": self.stats["successful_attempts"],
            "failed": self.stats["failed_attempts"],
            "success_rate": (
                f"{self.stats['successful_attempts'] / max(1, self.stats['total_attempts']) * 100:.1f}%"
                if self.stats["total_attempts"] > 0 else "N/A"
            ),
            "model_usage": self.stats["model_usage"]
        }


# Singleton instance
_router_instance: Optional[ModelRouter] = None


def get_router(api_key: str) -> ModelRouter:
    """
    Get or create the global ModelRouter instance.
    """
    global _router_instance
    if _router_instance is None:
        _router_instance = ModelRouter(api_key)
    return _router_instance


def reset_router():
    """
    Reset the global router (useful for testing).
    """
    global _router_instance
    _router_instance = None


# Example usage
if __name__ == "__main__":
    import os
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s"
    )
    
    # Example
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key:
        print("💳 Set GOOGLE_AI_API_KEY environment variable")
        exit(1)
    
    router = get_router(api_key)
    
    # Generate a script
    result = router.generate_json(
        task="script",
        prompt="""
        Generate a 2-minute horoscope script for Aries in JSON format:
        {
            "sign": "Aries",
            "date": "2025-12-13",
            "script": "[the actual horoscope text here, min 300 chars]",
            "cta": "engagement call to action"
        }
        """
    )
    
    print("\n✅ Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n📊 Stats:")
    print(json.dumps(router.get_stats(), indent=2))
