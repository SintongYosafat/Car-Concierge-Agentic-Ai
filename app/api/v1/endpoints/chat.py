from fastapi import APIRouter

chat_router = APIRouter()


@chat_router.get("/hello-chat")
async def chat_endpoint():
    return {"message": "Hello from chat endpoint"}
