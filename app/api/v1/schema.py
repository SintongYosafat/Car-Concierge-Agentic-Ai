from typing import Literal, TypeVar, Generic
from app.core.config import settings


from pydantic import BaseModel

T = TypeVar('T')

class AcBaseResponse(BaseModel, Generic[T]):
    """Generic response wrapper that wraps all successful API responses in a 'data' field."""
    data: T


ModelId = Literal[
    "amazon.nova-lite-v1:0",
    "amazon.nova-micro-v1:0",
    "amazon.nova-pro-v1:0",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-4o-mini",
    "gpt-5-mini",
    "gpt-5-nano",
    "gpt-5.1-chat",
    "gpt-5-chat",
    "gpt-4.1"
]

class ConversationRequest(BaseModel):
    conversation_id: str
    prompt: str


class ExperimentConversationRequest(BaseModel):
    conversation_id: str
    prompt: str
    model_id: ModelId = settings['DEFAULT_MODEL_ID']
    workflow_id: str = settings['DEFAULT_WORKFLOW_ID']
    random_thread_id: bool = False


class Context(BaseModel):
    """Custom runtime context schema."""
    user_id: str


class OlxAd(BaseModel):
    id: str
    title: str
    price: str


class ChatResponse(BaseModel):
    body: str
    ads: list[OlxAd]
    next_prompt_suggestions: list[str]

class ErrorDetail(BaseModel):
    key: str
    detail: str
    status: int

