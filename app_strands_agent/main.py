import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app_strands_agent.api.v1.router import api_router
from app_strands_agent.core import settings, logger, VERSION
from app_strands_agent.clients.valkey import create_valkey_client
from app_strands_agent.clients.keyspaces import create_keyspace_client
from app_strands_agent.clients.bedrock import get_bedrock_client, generate_embedding
from app_strands_agent.core.error_handler import setup_exception_handlers
from fastapi.responses import JSONResponse
import traceback
 
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management.
 
    This is the single place responsible for:
    - Initializing shared infrastructure clients (e.g. Valkey, Keyspaces)
    - Gracefully closing resources on shutdown
 
    Keep this minimal and framework-centric.
    """
    app.state.valkey = create_valkey_client()
    app.state.keyspaces = create_keyspace_client()
 
    # Pre-warm boto3 + Bedrock: eliminates cold-start on first request
    logger.info("Pre-warming Bedrock connections...")
    t = time.perf_counter()
    get_bedrock_client()
    generate_embedding("warmup")
    logger.info("Bedrock pre-warm done in %.0fms", (time.perf_counter() - t) * 1000)
 
    yield
    app.state.keyspaces.close()
    app.state.valkey.close()
 
 
app = FastAPI(
    title="AI Concierge Backend",
    description="AI-powered car recommendation service",
    version=VERSION,
    lifespan=lifespan,
)
 
# CORS middleware configuration
# NOTE: Allow-all is intentional for non-production environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get("cors_origins", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# API routes
app.include_router(api_router)

# Exception handlers
setup_exception_handlers(app)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s\n%s", exc, traceback.format_exc())
    return JSONResponse(status_code=500, content={"error": {"key": "INTERNAL_SERVER_ERROR", "detail": str(exc)}})
 
 
@app.middleware("http")
async def latency_middleware(request: Request, call_next):
    """Track total request latency for all endpoints."""
    start = time.perf_counter()
    response = await call_next(request)
    total_ms = round((time.perf_counter() - start) * 1000,3)
    response.headers["X-Total-Latency-Ms"] = str(total_ms)
    return response
 
 
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for container orchestration.
 
    Used by load balancers and schedulers to verify
    that the service is up and responding.
    """
    return {
        "status": "healthy",
        "service": "ai-concierge-backend",
        "version": VERSION,
    }