from fastapi import APIRouter
from app_strands_agent.api.v1.endpoints import chat

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(chat.chat_router, prefix="/chat", tags=["chat"])