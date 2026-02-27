from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings, VERSION
from app.core.logger import logger  # noqa: F401 to initialize logger
from contextlib import asynccontextmanager
from app.core.error_handler import setup_exception_handlers
from app.repository.database import get_session
from app.repository.conversation_repository import ConversationRepository
from app.repository.message_repository import MessageRepository
from langgraph.checkpoint.memory import InMemorySaver
from app.stream.dispatcher import StreamDispatcher

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Starting up the AI Concierge Backend application...")
    app.state.session = get_session()
    app.state.conversation_repository = ConversationRepository(app.state.session)
    app.state.message_repository = MessageRepository(app.state.session)
    app.state.checkpointer = InMemorySaver()
    app.state.dispatcher = StreamDispatcher()

    yield
    logger.info("Shutting down database session...")
    app.state.session.shutdown()
    logger.info("Cleaning up stream dispatcher...")
    app.state.dispatcher.reset()
    logger.info("Shutting down the AI Concierge Backend application...")

app = FastAPI(
    title="AI Concierge Backend",
    description="AI-powered car recommendation service",
    version=VERSION,
    lifespan=lifespan
)

# Register custom exception handlers
setup_exception_handlers(app)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get("cors_origins", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "service": "ai-concierge-backend",
        "version": VERSION
    }
