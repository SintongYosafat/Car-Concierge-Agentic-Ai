"""
OpenSearch Query Builders & Execution Layer
 
This module provides composable helpers to:
- Build numeric range filters
- Construct BM25 and hybrid (vector + BM25) queries
- Execute OpenSearch searches with score thresholding
 
Design goals:
- Predictable query structure
- Clear separation between query building and execution
"""
 
from typing import Any, Dict, List, Optional
import logging
 
from app_strands_agent.core.config import settings
 
logger = logging.getLogger(__name__)
 
 
# RANGE FILTER BUILDERS
 
def build_range_filter(
    field: str,
    min_val: Optional[Any],
    max_val: Optional[Any],
) -> Optional[Dict[str, Any]]:
    """
    Build an OpenSearch range filter (gte / lte).
 
    Parameters
    ----------
    field : str
        Field name in the index.
    min_val : Optional[Any]
        Lower bound (inclusive).
    max_val : Optional[Any]
        Upper bound (inclusive).
 
    Returns
    -------
    Optional[Dict[str, Any]]
        Range filter query or None if no bounds provided.
    """
    if min_val is None and max_val is None:
        return None
 
    range_query: Dict[str, Any] = {}
 
    if min_val is not None:
        range_query["gte"] = min_val
    if max_val is not None:
        range_query["lte"] = max_val
 
    return {"range": {field: range_query}}
 
 
def build_base_filters(intent: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build base numeric filters from parsed intent.
 
    This includes:
    - Price range
    - Year range
    - Mileage range
 
    Parameters
    ----------
    intent : Dict[str, Any]
        Normalized intent structure.
 
    Returns
    -------
    List[Dict[str, Any]]
        List of OpenSearch filter clauses.
    """
    return list(
        filter(
            None,
            [
                build_range_filter(
                    "item_price",
                    intent["price"]["min"],
                    intent["price"]["max"],
                ),
                build_range_filter(
                    "item_year",
                    intent["year"]["min"],
                    intent["year"]["max"],
                ),
                build_range_filter(
                    "item_mileage",
                    intent["mileage"]["min"],
                    intent["mileage"]["max"],
                ),
            ],
        )
    )
 
 
# BM25 TEXT QUERIES
 
def build_bm25_queries(keyword: Optional[str]) -> List[Dict[str, Any]]:
    """
    Build BM25 match queries for keyword search.
 
    Each field is assigned a configurable boost to
    influence ranking relevance.
 
    Parameters
    ----------
    keyword : Optional[str]
        Search keyword.
 
    Returns
    -------
    List[Dict[str, Any]]
        List of BM25 match queries.
    """
    if not keyword:
        return []
 
    return [
        {
            "match": {
                "item_model": {
                    "query": keyword,
                    "boost": settings.MODEL_BOOST,
                }
            }
        },
        {
            "match": {
                "item_make": {
                    "query": keyword,
                    "boost": settings.MAKE_BOOST,
                }
            }
        },
        {
            "match": {
                "ad_title": {
                    "query": keyword,
                    "boost": settings.TITLE_BOOST,
                }
            }
        },
        {
            "match": {
                "ad_description": {
                    "query": keyword,
                    "boost": settings.DESCRIPTION_BOOST,
                }
            }
        },
    ]
 
 
# QUERY COMPOSITION
 
def build_bm25_filter_query(
    bm25_queries: List[Dict[str, Any]],
    filters: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build a low-cost BM25 query with filters.
 
    Used as the first (cheapest) search phase.
 
    Parameters
    ----------
    bm25_queries : List[Dict[str, Any]]
        BM25 match queries.
    filters : List[Dict[str, Any]]
        Filter clauses.
 
    Returns
    -------
    Dict[str, Any]
        OpenSearch bool query.
    """
    return {
        "bool": {
            "must": bm25_queries or [{"match_all": {}}],
            "filter": filters,
        }
    }
 
 
def build_vector_bm25_hybrid_query(
    embedding: List[float],
    bm25_queries: List[Dict[str, Any]],
    filters: List[Dict[str, Any]],
    knn_k: int,
) -> Dict[str, Any]:
    """
    Build a hybrid vector + BM25 query with filters.
 
    This query is computationally expensive and should
    only be used as a fallback after BM25.
 
    Parameters
    ----------
    embedding : List[float]
        Query embedding vector.
    bm25_queries : List[Dict[str, Any]]
        BM25 match queries.
    filters : List[Dict[str, Any]]
        Filter clauses.
    knn_k : int
        Number of nearest neighbors for vector search.
 
    Returns
    -------
    Dict[str, Any]
        OpenSearch script_score query.
    """
    return {
        "script_score": {
            "query": {
                "bool": {
                    "must": [
                        {
                            "knn": {
                                "embedding": {
                                    "vector": embedding,
                                    "k": knn_k,
                                }
                            }
                        }
                    ],
                    "should": bm25_queries,
                    "filter": filters,
                    "minimum_should_match": 0,
                }
            },
            "script": {"source": "_score"},
        }
    }
 
 
# SEARCH EXECUTION
 
def execute_search(
    *,
    os_client,
    index: str,
    query: Dict[str, Any],
    size: int,
    query_type: str = "bm25",
) -> List[Dict[str, Any]]:
    """
    Execute an OpenSearch query with score thresholding.
 
    Parameters
    ----------
    os_client
        OpenSearch client instance.
    index : str
        Index name.
    query : Dict[str, Any]
        OpenSearch query body.
    size : int
        Maximum number of results.
    query_type : str
        Logical query type ('bm25' or 'hybrid').
 
    Returns
    -------
    List[Dict[str, Any]]
        Filtered search hits.
    """
    threshold = (
        settings.HYBRID_SCORE_THRESHOLD
        if query_type == "hybrid"
        else settings.BM25_SCORE_THRESHOLD
    )
 
    try:
        response = os_client.search(
            index=index,
            body={
                "size": size,
                "query": query,
            },
            request_timeout=settings.OS_TIMEOUT,
        )
 
        hits = response["hits"]["hits"]
 
        # Apply minimum score threshold
        filtered = [
            hit
            for hit in hits
            if hit.get("_score", 0) >= threshold
        ]
 
        return filtered[:size]
 
    except Exception:
        logger.exception("OpenSearch query failed")
        return []
 
 
def execute_msearch(
    *,
    os_client,
    index: str,
    queries: List[Dict[str, Any]],
    size: int,
    query_type: str = "bm25",
) -> List[List[Dict[str, Any]]]:
    """
    Execute multiple OpenSearch queries in a single HTTP round-trip.
 
    Returns one result list per query, in the same order as *queries*.
    Each sub-list is already score-filtered and size-capped.
    """
    if not queries:
        return []
 
    threshold = (
        settings.HYBRID_SCORE_THRESHOLD
        if query_type == "hybrid"
        else settings.BM25_SCORE_THRESHOLD
    )
 
    # Build msearch body: alternating header / body lines
    body_lines = []
    for q in queries:
        body_lines.append({"index": index})
        body_lines.append({
            "size": size,
            "query": q,
        })
 
    try:
        response = os_client.msearch(
            body=body_lines,
            request_timeout=settings.OS_TIMEOUT,
        )
    except Exception:
        logger.exception("OpenSearch msearch failed")
        return [[] for _ in queries]
 
    results: List[List[Dict[str, Any]]] = []
    for resp in response.get("responses", []):
        if resp.get("error"):
            logger.warning("msearch sub-query error: %s", resp["error"])
            results.append([])
            continue
        hits = resp.get("hits", {}).get("hits", [])
        filtered = [h for h in hits if h.get("_score", 0) >= threshold]
        results.append(filtered[:size])
 
    return results