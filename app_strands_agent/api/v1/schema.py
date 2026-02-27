from pydantic import BaseModel, Field
from typing import Optional, TypedDict

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)

class TokenUsage(TypedDict):
    inputTokens: int
    outputTokens: int
    totalTokens: int

class ChatResponse(BaseModel):
    source: str
    reply: str
    token_usage: Optional[TokenUsage] = None
    latency_breakdown: Optional[dict] = None