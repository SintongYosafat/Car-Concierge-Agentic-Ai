import ssl
import json
import hashlib
from typing import Union, Iterable, Dict, List, Optional
import numpy as np
from redis import Redis
from redis.cluster import RedisCluster
from fastapi import Request
from app_strands_agent.core import settings, logger
from app_strands_agent.engine import dot_similarity_batch
from datetime import datetime, timezone

# type alias
ValkeyClient = Union[Redis, RedisCluster]


def create_valkey_client() -> ValkeyClient:
    """
    Create and configure a Valkey/Redis client.

    - dev: plain Redis (no SSL), e.g. local Docker redis
    - prd: AWS ElastiCache with SSL (single-node or cluster)
    """
    host = settings.get("VALKEY_HOST")
    port = int(settings.get("VALKEY_PORT"))
    env = settings.current_env

    if not host:
        raise RuntimeError("VALKEY_HOST not configured in settings")

    logger.info("Creating Valkey client for %s:%s (env=%s)", host, port, env)

    common_params = {
        "host": host,
        "port": port,
        "decode_responses": True,
        "socket_connect_timeout": 10,
        "socket_timeout": 10,
        "socket_keepalive": True,
        "retry_on_timeout": True,
        "health_check_interval": 30,
    }

    # Dev: plain Redis tanpa SSL (docker / local)
    if env == "dev":
        try:
            client = Redis(**common_params)
            client.ping()
            logger.info("Connected to local Redis (dev, no SSL)")
            return client
        except Exception as e:
            raise RuntimeError(f"Cannot connect to Redis at {host}:{port}: {e}") from e

    # Prd: AWS ElastiCache with SSL
    try:
        client = Redis(
            **common_params,
            ssl=True,
            ssl_cert_reqs=ssl.CERT_NONE,
            ssl_check_hostname=False,
        )
        client.ping()
        logger.info("Connected to AWS ElastiCache with SSL")
        return client
    except Exception as ssl_error:
        logger.warning("SSL connection failed: %s, trying cluster mode", ssl_error)

        try:
            client = RedisCluster(
                **common_params,
                ssl=True,
                ssl_cert_reqs=ssl.CERT_NONE,
                skip_full_coverage_check=True,
            )
            client.ping()
            logger.info("Connected to AWS ElastiCache with SSL (cluster mode)")
            return client
        except Exception as cluster_error:
            logger.error("Connection failed: %s", cluster_error)
            raise RuntimeError(f"Cannot connect to Valkey at {host}:{port}") from cluster_error


def get_valkey(request: Request) -> ValkeyClient:
    """
    FastAPI dependency that provides access to the shared Valkey client.
    
    The client is retrieved from `request.app.state` and is expected to be
    initialized during application startup.
    
    Returns:
        The shared Valkey client instance.
    """
    return request.app.state.valkey


def iter_cache_keys(valkey: ValkeyClient, max_keys: int = 500) -> Iterable[str]:
    """
    Iterate over semantic cache keys stored in Valkey.
    
    Args:
        valkey: Valkey client instance.
        max_keys: Maximum number of keys to yield.
    
    Returns:
        Iterable of cache keys.
    """
    prefix = settings.get("VALKEY_CACHE_PREFIX")
    
    if isinstance(valkey, RedisCluster):
        scanner = valkey.scan_iter(match=f"{prefix}*", count=100, target_nodes="all")
    else:
        scanner = valkey.scan_iter(match=f"{prefix}*", count=100)
    
    yielded = 0
    for key in scanner:
        yield key
        yielded += 1
        if yielded >= max_keys:
            break


def _pipeline_mget(
    valkey: ValkeyClient,
    keys: List[str],
) -> List[Optional[str]]:
    """
    Fetch multiple values from Valkey using a pipeline.
    
    Args:
        valkey: Valkey client instance.
        keys: List of cache keys to fetch.
    
    Returns:
        List of raw string values (or None for missing keys).
    """
    if not keys:
        return []
    
    pipe = valkey.pipeline(transaction=False)
    for key in keys:
        pipe.get(key)
    return pipe.execute()


def find_semantic_cache(
    query_embedding: List[float],
    valkey: ValkeyClient,
) -> str | None:
    """
    Perform global semantic cache lookup using a pre-computed embedding.
    
    Args:
        query_embedding: Pre-computed embedding vector for the query.
        valkey: Valkey client instance.
    
    Returns:
        Cached answer if similarity threshold is met, otherwise None.
    """
    logger.debug("SemanticCache lookup started")
    
    if not isinstance(query_embedding, list):
        logger.warning("Invalid query embedding type")
        return None
    
    keys = list(iter_cache_keys(valkey))
    if not keys:
        logger.info("SemanticCache MISS (empty cache)")
        return None
    
    raw_values = _pipeline_mget(valkey, keys)
    
    embeddings: List[list] = []
    answers: List[str] = []
    
    for raw_value in raw_values:
        if not raw_value:
            continue
        try:
            payload = json.loads(raw_value)
        except json.JSONDecodeError:
            continue
        cached_embedding = payload.get("embedding")
        if not isinstance(cached_embedding, list):
            continue
        embeddings.append(cached_embedding)
        answers.append(payload.get("answer"))
    
    if not embeddings:
        logger.info("SemanticCache MISS (no valid embeddings)")
        return None
    
    matrix = np.array(embeddings, dtype=np.float32)
    scores = dot_similarity_batch(query_embedding, matrix)
    
    best_idx = int(np.argmax(scores))
    best_score = float(scores[best_idx])
    
    if best_score >= settings.SIMILARITY_THRESHOLD:
        logger.info("SemanticCache HIT", extra={"score": round(best_score, 4)})
        return answers[best_idx]
    
    logger.info("SemanticCache MISS", extra={"best_score": round(best_score, 4)})
    return None


def save_semantic_cache(
    raw_query: str,
    query_embedding: List[float],
    answer: str,
    valkey: ValkeyClient,
) -> None:
    """
    Save a semantic cache entry to Valkey.
    
    Args:
        raw_query: Original user query.
        query_embedding: Pre-computed embedding vector for the query.
        answer: Final answer to cache.
        valkey: Valkey client instance.
    """
    try:
        cache_key = (
            f"{settings.VALKEY_CACHE_PREFIX}"
            f"{hashlib.sha256(raw_query.encode()).hexdigest()}"
        )
        payload: Dict = {
            "raw_query": raw_query,
            "embedding": query_embedding,
            "answer": answer,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        valkey.set(
            cache_key,
            json.dumps(payload),
            ex=settings.VALKEY_DEFAULT_TTL,
        )
        logger.info("SemanticCache saved key=%s ttl=%ss", cache_key, settings.VALKEY_DEFAULT_TTL)
    except Exception as exc:
        logger.warning("SemanticCache Failed to write cache: %s", exc, exc_info=True)