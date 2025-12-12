from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

from .config_loader import ProjectConfig
from . import secrets_manager

logger = logging.getLogger(__name__)


@dataclass
class ProviderCallError(RuntimeError):
    message: str
    status_code: int | None = None

    def __str__(self) -> str:  # pragma: no cover
        if self.status_code is None:
            return self.message
        return f"{self.message} (status_code={self.status_code})"


def generate_text(
    config: ProjectConfig,
    prompt: str,
    system_prompt: str | None = None,
    model_hint: str | None = None,
    temperature: float | None = None,
) -> str:
    """Generate text using configured LLM with fallbacks.

    The config supports both the newer schema:
      generation.primary_model + generation.fallback_models
    and the legacy schema:
      generation.model
    """

    gen_cfg = config.generation
    temp = temperature if temperature is not None else gen_cfg.temperature
    max_retries = max(1, int(gen_cfg.max_retries))
    retry_delay = float(getattr(gen_cfg, "retry_delay_sec", 2.0) or 2.0)

    primary_model = model_hint or gen_cfg.primary_model or gen_cfg.model
    if not primary_model:
        raise ValueError("No model configured (generation.primary_model or generation.model)")

    models_to_try = [primary_model] + list(gen_cfg.fallback_models or [])

    last_error: BaseException | None = None
    for model in models_to_try:
        provider = _get_provider_for_model(model, config)

        for attempt in range(max_retries):
            try:
                response = _call_model(provider, model, prompt, system_prompt, temp)
                logger.info("LLM response from %s/%s", provider, model)
                return response

            except ProviderCallError as e:
                last_error = e

                if e.status_code in {401, 403}:
                    logger.warning("%s/%s: auth error, skipping model: %s", provider, model, e)
                    break

                if e.status_code == 429:
                    if attempt < max_retries - 1:
                        wait = retry_delay * (2**attempt)
                        logger.warning("%s/%s: rate limited, retrying in %ss", provider, model, wait)
                        time.sleep(wait)
                        continue
                    break

                if attempt < max_retries - 1:
                    wait = retry_delay * (2**attempt)
                    logger.warning("%s/%s: error, retrying in %ss: %s", provider, model, wait, e)
                    time.sleep(wait)
                    continue

            except (TimeoutError, ConnectionError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait = retry_delay * (2**attempt)
                    logger.warning("%s/%s: connection error, retrying in %ss: %s", provider, model, wait, e)
                    time.sleep(wait)
                    continue

        logger.info("Fallback: %s/%s failed, trying next", provider, model)

    raise RuntimeError(f"All LLM models failed. Last error: {last_error}")


def _get_provider_for_model(model: str, config: ProjectConfig) -> str:
    model_l = model.lower()

    if "gemini" in model_l:
        return "gemini"

    if "qwen" in model_l:
        return "openrouter"

    provider_priority = list(getattr(config.generation, "provider_priority", []) or [])
    if provider_priority:
        if ":" in model_l:
            return "ollama"
        return provider_priority[0]

    return "ollama"


def _call_model(provider: str, model: str, prompt: str, system: str | None, temp: float) -> str:
    if provider == "gemini":
        return _call_gemini(model, prompt, system, temp)
    if provider == "ollama":
        return _call_ollama(model, prompt, system, temp)
    if provider == "openrouter":
        return _call_openrouter(model, prompt, system, temp)

    raise ValueError(f"Unknown provider: {provider}")


def _call_gemini(model: str, prompt: str, system: str | None, temp: float) -> str:
    try:
        api_key = secrets_manager.get("GOOGLE_AI_API_KEY")
    except KeyError as e:
        raise ProviderCallError(str(e), status_code=401) from e

    # Keep the import inside the function to avoid making Gemini dependency mandatory.
    try:
        import google.generativeai as genai  # type: ignore
    except Exception as e:
        raise ProviderCallError(
            "google-generativeai is not installed (required for Gemini provider)",
        ) from e

    genai.configure(api_key=api_key)

    try:
        # Library supports both `gemini-...` and `models/gemini-...` naming.
        model_name = model
        if not model_name.startswith("models/") and not model_name.startswith("gemini"):
            model_name = f"models/{model_name}"

        if hasattr(genai, "GenerativeModel"):
            m = genai.GenerativeModel(model_name)
            kwargs: dict[str, Any] = {
                "generation_config": {"temperature": temp},
            }
            if system:
                kwargs["system_instruction"] = system
            resp = m.generate_content(prompt, **kwargs)
            text = getattr(resp, "text", None)
            if not text:
                raise ProviderCallError("Empty response from Gemini")
            return text

        raise ProviderCallError("Unsupported google.generativeai version")

    except ProviderCallError:
        raise
    except Exception as e:
        status_code = getattr(e, "status_code", None)
        raise ProviderCallError(f"Gemini call failed: {e}", status_code=status_code) from e


def _call_ollama(model: str, prompt: str, system: str | None, temp: float) -> str:
    try:
        import ollama  # type: ignore
    except Exception as e:
        raise ProviderCallError("ollama-python is not installed (required for Ollama provider)") from e

    try:
        response = ollama.generate(
            model=model,
            prompt=prompt,
            system=system,
            stream=False,
            options={"temperature": temp},
        )
        text = response.get("response") if isinstance(response, dict) else None
        if not text:
            raise ProviderCallError("Empty response from Ollama")
        return text
    except ProviderCallError:
        raise
    except Exception as e:
        raise ProviderCallError(f"Ollama call failed: {e}") from e


def _call_openrouter(model: str, prompt: str, system: str | None, temp: float) -> str:
    try:
        api_key = secrets_manager.get("OPENROUTER_API_KEY")
    except KeyError as e:
        raise ProviderCallError(str(e), status_code=401) from e

    try:
        import openai  # type: ignore
    except Exception as e:
        raise ProviderCallError("openai is not installed (required for OpenRouter provider)") from e

    try:
        client = openai.OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system or ""},
                {"role": "user", "content": prompt},
            ],
            temperature=temp,
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        status = getattr(e, "status_code", None)
        if status is None:
            status = getattr(getattr(e, "response", None), "status_code", None)
        raise ProviderCallError(f"OpenRouter call failed: {e}", status_code=status) from e
