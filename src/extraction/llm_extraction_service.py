"""
LLM Extraction Service
======================

Adapter to use the centralized MultiAIOrchestrator/ModelRegistry
for claim extraction tasks. Allows benchmarking different models.
"""

import json
import logging
from typing import List, Dict, Any

from src.services.llm_query_bridge import (
    MODEL_REGISTRY,
    AnthropicProvider,
    OpenAIProvider,
    GoogleProvider,
    ModelConfig
)

logger = logging.getLogger(__name__)

class LLMExtractionService:
    def __init__(self, model_id: str = "gpt-4o"):
        self.model_config = self._resolve_model(model_id)
        self.providers = {
            "anthropic": AnthropicProvider(),
            "openai": OpenAIProvider(),
            "google": GoogleProvider(),
        }
        self.provider = self.providers.get(self.model_config.provider)
        if not self.provider:
            raise ValueError(f"Unsupported provider: {self.model_config.provider}")

    def _resolve_model(self, model_id: str) -> ModelConfig:
        """Resolve model ID to config, supporting aliases."""
        if model_id in MODEL_REGISTRY:
            return MODEL_REGISTRY[model_id]
        
        # Try to find by direct model_id match if not in registry keys
        for config in MODEL_REGISTRY.values():
            if config.model_id == model_id:
                return config
                
        # Default fallback if unknown but looks like openai/anthropic
        if "gpt" in model_id:
            return MODEL_REGISTRY["gpt-4o"]
        if "claude" in model_id:
            return MODEL_REGISTRY["claude-sonnet"]
            
        raise ValueError(f"Unknown model ID: {model_id}")

    def extract_claims_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Run extraction using the configured LLM.
        Returns a list of raw claim dictionaries.
        """
        system_prompt = """You are an expert scientific claim extractor.
Your task is to extract causal claims (IV -> DV) from the provided text.
Return a JSON object with a key "claims" containing a list of extracted claims.
Each claim must have:
- iv: Independent variable
- dv: Dependent variable
- direction: "positive", "negative", or "no effect"
- confidence: 0.0 to 1.0
- quote: The exact sentence supporting this
"""
        
        user_prompt = f"""Extract claims from this text:
        
{text[:10000]}  # Truncate to avoid context limits for now

Return JSON."""

        try:
            response_text, in_tokens, out_tokens = self.provider.complete(
                prompt=user_prompt,
                model_config=self.model_config,
                system=system_prompt
            )
            
            # Simple parsing
            data = json.loads(response_text.replace("```json", "").replace("```", ""))
            return data.get("claims", [])
            
        except Exception as e:
            logger.error(f"LLM Extraction failed: {e}")
            return []
