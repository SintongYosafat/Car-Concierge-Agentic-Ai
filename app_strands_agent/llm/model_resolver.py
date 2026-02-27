from strands.models.bedrock import BedrockModel
from strands.models.openai import OpenAIModel
from app_strands_agent.core.config import settings
from app_strands_agent.core.exceptions import AcHttpException
from app_strands_agent.llm import get_model_info
from typing import Dict, Any


def resolve(model_name: str):
    model_info = get_model_info(model_name)
    if not model_info:
        raise AcHttpException("INVALID_MODEL_NAME", detail=f"Invalid model name: {model_name}")
    model_id = model_info.get("model_id")

    if model_name.startswith("bedrock"):
        params: Dict[str,Any] = {
            "temperature": 0.1,
            "top_p": 0.5
        }
        guardrail_id = settings.get("GUARDRAIL_ID", "")
        if guardrail_id:
            params.update({
                "guardrail_id": guardrail_id,
                "guardrail_version": "DRAFT",
                "guardrail_trace": "enabled",
                "guardrail_stream_processing_mode": "sync",
                "guardrail_redact_input": True,
                "guardrail_redact_input_message": 'Maaf, input kamu melanggar guardrails.',
                "guardrail_redact_output": False,
                "guardrail_redact_output_message": 'Maaf, output model melanggar guardrails.'
            })
        model = BedrockModel(model_id=model_id, **params)
    elif model_name.startswith("openai"):
        openai_key=settings.get("OPENAI_KEY")
        model = OpenAIModel(
            client_args={
                "api_key": openai_key,
            },
            model_id = model_id
        )
    else:
        raise AcHttpException("INVALID_MODEL_NAME", detail=f"Invalid model name: {model_name}")
    return model