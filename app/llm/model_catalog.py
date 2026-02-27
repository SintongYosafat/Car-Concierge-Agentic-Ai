"""
LLM Model Catalog - Centralized model information and pricing.
Prices are in USD per million tokens.
"""

from typing import TypedDict


class ModelInfo(TypedDict):
    """Model information schema."""
    input_token_price: float  # USD per million tokens
    cached_input_token_price: float  # USD per million tokens (cached/prompt caching)
    output_token_price: float  # USD per million tokens


# Master dictionary containing LLM model information
MODEL_CATALOG: dict[str, ModelInfo] = {
    # Amazon Nova models
    "amazon.nova-lite-v1:0": {
        "input_token_price": 0.081,
        "cached_input_token_price": 0.02025,
        "output_token_price": 0.324,
    },
    "amazon.nova-micro-v1:0": {
        "input_token_price": 0.047,
        "cached_input_token_price": 0.011,
        "output_token_price": 0.188,
    },
    "amazon.nova-pro-v1:0": {
        "input_token_price": 1.08,
        "cached_input_token_price": 0.27,
        "output_token_price": 4.32,
    },
    
    # Google Gemini models
    "gemini-2.5-flash": {
        "input_token_price": 0.3,
        "cached_input_token_price": 0.03,
        "output_token_price": 2.5,
    },
    "gemini-2.5-flash-lite": {
        "input_token_price": 0.1,
        "cached_input_token_price": 0.01,
        "output_token_price": 0.4,
    },
    "gemini-2.5-pro": {
        "input_token_price": 1.25,
        "cached_input_token_price": 0.125,
        "output_token_price": 10,
    },
    
    # OpenAI GPT-4.1 models
    "gpt-4.1-mini": {
        "input_token_price": 0.4,
        "cached_input_token_price": 0.1,
        "output_token_price": 1.6,
    },
    "gpt-4.1-nano": {
        "input_token_price": 0.1,
        "cached_input_token_price": 0.03,
        "output_token_price": 0.4,
    },
    "gpt-4.1": {
        "input_token_price": 2,
        "cached_input_token_price": 0.5,
        "output_token_price": 8,
    },
    
    # OpenAI GPT-4o models
    "gpt-4o-mini": {
        "input_token_price": 0.15,
        "cached_input_token_price": 0.08,
        "output_token_price": 0.6,
    },
    
    # OpenAI GPT-5 models
    "gpt-5-mini": {
        "input_token_price": 0.25,
        "cached_input_token_price": 0.03,
        "output_token_price": 2,
    },
    "gpt-5-nano": {
        "input_token_price": 0.05,
        "cached_input_token_price": 0.01,
        "output_token_price": 0.4,
    },
    "gpt-5.1-chat": {
        "input_token_price": 1.25,
        "cached_input_token_price": 0.13,
        "output_token_price": 10,
    },
    "gpt-5-chat": {
        "input_token_price": 1.25,
        "cached_input_token_price": 0.13,
        "output_token_price": 10,
    },
}


def get_model_info(model_id: str) -> ModelInfo | None:
    """
    Get model information by model_id.
    
    Args:
        model_id: The model identifier
        
    Returns:
        ModelInfo dictionary or None if model not found
    """
    return MODEL_CATALOG.get(model_id)
