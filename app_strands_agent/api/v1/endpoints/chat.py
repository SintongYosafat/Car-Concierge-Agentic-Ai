import asyncio, time
from fastapi import APIRouter, Depends, Request
from app_strands_agent.agents.orchestrator_agent import orchestrator_agent
from app_strands_agent.agents._helper import strip_internal_reasoning
from app_strands_agent.session_context import _current_session_id, _workflow_timings
from app_strands_agent.clients.valkey import find_semantic_cache, save_semantic_cache, get_valkey
from app_strands_agent.clients.bedrock import generate_embedding
from app_strands_agent.clients.keyspaces import KeyspaceClient, get_keyspaces
from app_strands_agent.core import logger
from app_strands_agent.api.v1.schema import ChatRequest, ChatResponse
from app_strands_agent.core.exceptions import AcHttpException

chat_router = APIRouter()

def _ms(start: float) -> int:
    return round((time.perf_counter() - start) * 1000)

@chat_router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    payload: ChatRequest,
    request: Request,
    valkey=Depends(get_valkey),
    keyspaces: KeyspaceClient = Depends(get_keyspaces),
):
    """
    chat endpoint — optimized latency via msearch + structured tool params.
    """
    t_total = time.perf_counter()

    message = payload.message.strip()
    session_id = payload.session_id.strip()
    user_id = payload.user_id.strip()

    # 1. Embed query (for semantic cache)
    t0 = time.perf_counter()
    query_embedding = await asyncio.to_thread(generate_embedding, message)
    embedding_ms = _ms(t0)

    # 2. Semantic cache lookup
    t0 = time.perf_counter()
    cached = await asyncio.to_thread(find_semantic_cache, query_embedding, valkey)
    cache_lookup_ms = _ms(t0)

    if cached:
        return ChatResponse(
            source="cache",
            reply=cached,
            latency_breakdown={
                "embedding_ms": embedding_ms,
                "cache_lookup_ms": cache_lookup_ms,
                "total_ms": _ms(t_total),
            },
        )

    # 3. Run agent
    agent = orchestrator_agent(session_id=session_id, user_id=user_id)
    token_sid = _current_session_id.set(session_id)
    token_wt = _workflow_timings.set({})
    t0 = time.perf_counter()
    try:
        agent_response = await asyncio.to_thread(agent, message)
    finally:
        _current_session_id.reset(token_sid)
    workflow_timings = _workflow_timings.get()
    _workflow_timings.reset(token_wt)

    # Extract agent sub-timings
    bedrock_llm_ms = agent_response.metrics.accumulated_metrics.get("latencyMs", 0)
    agent_breakdown = {
        "bedrock_llm_ms": bedrock_llm_ms,
        **{k: round(v) for k, v in workflow_timings.items()},
    }

    # 4. Normalize output
    result = (
        agent_response.output_text
        if hasattr(agent_response, "output_text")
        else str(agent_response)
    )
    token_usage = agent_response.metrics.accumulated_usage

    result = strip_internal_reasoning(result)

    if not result.strip():
        raise AcHttpException("INTERNAL_SERVER_ERROR", detail="Agent returned empty response")

    # 5. Parallel post-agent I/O
    keyspaces_ms = 0
    used_search = "opensearch_ms" in workflow_timings

    async def _do_cache_save():
        if not used_search:
            return
        try:
            await asyncio.to_thread(
                save_semantic_cache, message, query_embedding, result, valkey,
            )
        except Exception as e:
            logger.warning("Semantic cache write failed: %r", e, extra={"session_id": session_id})

    async def _do_keyspaces_save():
        nonlocal keyspaces_ms
        t = time.perf_counter()
        try:
            await asyncio.to_thread(keyspaces.save, user_id, session_id, "user", message)
            await asyncio.to_thread(keyspaces.save, user_id, session_id, "assistant", result)
        except Exception as e:
            logger.warning("Keyspaces chat history save failed: %r", e, extra={"session_id": session_id})
        keyspaces_ms = _ms(t)

    await asyncio.gather(_do_cache_save(), _do_keyspaces_save())

    return ChatResponse(
        source="agent",
        reply=result,
        token_usage=token_usage,
        latency_breakdown={
            "embedding_ms": embedding_ms,
            "cache_lookup_ms": cache_lookup_ms,
            **agent_breakdown,
            "keyspaces_ms": keyspaces_ms,
            "total_ms": _ms(t_total),
        },
    )