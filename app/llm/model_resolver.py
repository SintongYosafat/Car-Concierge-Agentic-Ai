import os
from langchain_openai import ChatOpenAI
from langchain_aws import ChatBedrockConverse
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.core.exceptions import AcHttpException

def resolve(model_id: str):
    if model_id.startswith("amazon"):
        model = ChatBedrockConverse(
            model_id=model_id
        )
    elif model_id.startswith("gpt"):
        model = ChatOpenAI(
            model_name = model_id,
            base_url=settings['AZURE_AI_ENDPOINT'],
            api_key=settings['AZURE_AI_CREDENTIAL'],
        )
    elif model_id.startswith("gemini"):
        model = ChatGoogleGenerativeAI(
            model=model_id,
            api_key=settings['GEMINI_API_KEY']
        )
    else:
        raise AcHttpException("INVALID_MODEL_ID", detail=f"Invalid model ID: {model_id}")
    
    return model