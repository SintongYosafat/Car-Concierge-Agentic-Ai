from fastapi import APIRouter

from app.api.v1.endpoints import chat, message, conversation

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(chat.chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(message.router, prefix="/messages", tags=["messages"])
api_router.include_router(conversation.router, prefix="/conversations", tags=["conversations"])