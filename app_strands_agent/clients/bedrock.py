import json, boto3
from functools import lru_cache
from app_strands_agent.core.config import settings
from app_strands_agent.core import logger
from app_strands_agent.llm import get_model_info
from app_strands_agent.core.exceptions import AcHttpException
 
@lru_cache(maxsize=1)
def get_bedrock_client():
    """
    Create a Bedrock Runtime client.
    """
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=settings.get("AWS_REGION")
    )
 
@lru_cache(maxsize=256)
def generate_embedding(text: str) -> list:
    """Generate embedding using AWS Bedrock Titan Embed v2."""
    client = get_bedrock_client()
    body = json.dumps({"inputText": text, "normalize": True})
    model_id = settings.get("EMBEDDING_MODEL")
    response = client.invoke_model(
        modelId=model_id,
        body=body,
        contentType="application/json",
        accept="application/json"
    )
    response_body = json.loads(response['body'].read())
    return response_body['embedding']