from typing import TypedDict, Optional


class ModelInfo(TypedDict):
    """Model information schema."""
    model_id: str
    input_token_price: float  # USD per million tokens
    cached_input_token_price: Optional[float] = None  # USD per million tokens (cached/prompt caching)
    output_token_price: float  # USD per million tokens

# Master dictionary containing LLM model information
MODEL_CATALOG: dict[str, ModelInfo] = {
    # Bedrock Models: https://aws.amazon.com/bedrock/pricing/

    # Amazon Nova models
    "bedrock_nova_2_lite": {
        "model_id": "amazon.nova-2-lite-v1:0",
        "input_token_price": 0.33,
        "cached_input_token_price": None,
        "output_token_price": 2.75
    },
    "bedrock_nova_pro": {
        "model_id": "amazon.nova-pro-v1:0",
        "input_token_price": 0.8,
        "cached_input_token_price": None,
        "output_token_price": 3.2
    },
    "bedrock_nova_lite": {
        "model_id": "amazon.nova-lite-v1:0",
        "input_token_price": 0.06,
        "cached_input_token_price": None,
        "output_token_price": 0.24
    },
    "bedrock_nova_micro": {
        "model_id": "amazon.nova-micro-v1:0",
        "input_token_price": 0.035,
        "cached_input_token_price": None,
        "output_token_price": 0.14
    },
    # Antropic Claude models
    "bedrock_claude_4.5_sonnet": {
        "model_id": "anthropic.claude-sonnet-4-5-20250929-v1:0",
        "input_token_price": 3.3,
        "cached_input_token_price": 0.33,
        "output_token_price": 16.5
    },
    "bedrock_claude_4_sonnet": {
        "model_id": "anthropic.claude-sonnet-4-20250514-v1:0",
        "input_token_price": 3,
        "cached_input_token_price": 0.3,
        "output_token_price": 15
    },
    "bedrock_claude_4.5_haiku": {
        "model_id": "anthropic.claude-haiku-4-5-20251001-v1:0",
        "input_token_price": 1,
        "cached_input_token_price": 0.1,
        "output_token_price": 5
    },
    "bedrock_claude_3.5_haiku": {
        "model_id": "anthropic.claude-3-5-haiku-20241022-v1:0",
        "input_token_price": 0.80,
        "cached_input_token_price": 0.08,
        "output_token_price": 4
    },
    "bedrock_claude_3_haiku": {
        "model_id": "anthropic.claude-3-haiku-20240307-v1:0",
        "input_token_price": 0.25,
        "cached_input_token_price": None,
        "output_token_price": 1.25
    },
    # OpenAI GPT-oss models
    "bedrock_gpt_oss_120B": {
        "model_id": "openai.gpt-oss-120b-1:0",
        "input_token_price": 0.15,
        "cached_input_token_price": None,
        "output_token_price": 0.6
    },
    "bedrock_gpt_oss_20B": {
        "model_id": "openai.gpt-oss-20b-1:0",
        "input_token_price": 0.07,
        "cached_input_token_price": None,
        "output_token_price": 0.3
    },
    # Meta Llama models
    "bedrock_llama_4_maverick_17B": {
        "model_id": "",
        "input_token_price": 0.24,
        "cached_input_token_price": 0.12,
        "output_token_price": 0.97
    },
    "bedrock_llama_4_scout_17B": {
        "model_id": "",
        "input_token_price": 0.17,
        "cached_input_token_price": 0.085,
        "output_token_price": 0.66
    },
    "bedrock_llama_3.3_scout_70B": {
        "model_id": "",
        "input_token_price": 0.72,
        "cached_input_token_price": 0.36,
        "output_token_price": 0.72
    },


    # OpenAI Models: https://openai.com/api/pricing/
    # GPT-5 models
    "openai_gpt_5.2": {
        "model_id": "gpt-5.2",
        "input_token_price": 1.75,
        "cached_input_token_price": 0.175,
        "output_token_price": 14
    },
    "openai_gpt_5.1": {
        "model_id": "gpt-5.1",
        "input_token_price": 1.25,
        "cached_input_token_price": 0.125,
        "output_token_price": 10
    },
    "openai_gpt_5_mini": {
        "model_id": "gpt-5-mini",
        "input_token_price": 0.25,
        "cached_input_token_price": 0.025,
        "output_token_price": 2
    },
    "openai_gpt_5_nano": {
        "model_id": "gpt-5-nano",
        "input_token_price": 0.05,
        "cached_input_token_price": 0.005,
        "output_token_price": 0.4
    },
    # GPT-4 models
    "openai_gpt_4.1": {
        "model_id": "gpt-4.1",
        "input_token_price": 2,
        "cached_input_token_price": 0.5,
        "output_token_price": 8
    },
    "openai_gpt_4.1_mini": {
        "model_id": "gpt-4.1-mini",
        "input_token_price": 0.4,
        "cached_input_token_price": 0.1,
        "output_token_price": 1.6
    },
    "openai_gpt_4.1_nano": {
        "model_id": "gpt-4.1-nano",
        "input_token_price": 0.1,
        "cached_input_token_price": 0.025,
        "output_token_price": 0.4
    }
}


def get_model_info(model_name: str) -> ModelInfo | None:
    """
    Get model information by model_name.
    
    Args:
        model_name: The model name from provider (Bedrock, OpenAI, etc.)
        
    Returns:
        ModelInfo dictionary or None if model not found
    """
    return MODEL_CATALOG.get(model_name)