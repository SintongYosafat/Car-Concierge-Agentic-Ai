"""
Vehicle Search Service — msearch-based
 
Replaces the sequential geo-fallback approach (up to 8 HTTP round-trips)
with a single msearch call that batches all BM25 + hybrid queries
for every geo level into one HTTP request.
 
Uses `min_score` in each sub-request body so OpenSearch filters
low-scoring results server-side.
"""
 
import time
import logging
from typing import Any, Dict, List, Optional, Tuple
 
from app_strands_agent.core.config import settings
from app_strands_agent.engine.os_query_builder import (
    build_base_filters,
    build_bm25_queries,
    build_bm25_filter_query,
    build_vector_bm25_hybrid_query,
)
 
logger = logging.getLogger(__name__)
 
class VehicleSearchService:
 
    def __init__(self, os_client):
        self.os_client = os_client
 
    def search(
        self,
        keyword: str,
        intent: Dict[str, Any],
        embedding_vector: Optional[List[float]] = None,
    ) -> Tuple[List[Dict], float]:
        """
        Execute vehicle search using a single msearch round-trip.
 
        Returns:
            (hits, elapsed_ms) tuple.
        """
        t0 = time.perf_counter()
 
        geo = intent.get("geo_info")
        base_filters = build_base_filters(intent)
        bm25_queries = build_bm25_queries(keyword)
 
        filter_steps = self._build_geo_filter_steps(geo, base_filters)
 
        # Build msearch body: BM25 + hybrid for each geo level
        body_lines: List[Dict] = []
        index = settings.OS_INDEX
        result_size = settings.DEFAULT_RESULT_SIZE
 
        for filters in filter_steps:
            # BM25 query
            body_lines.append({"index": index})
            body_lines.append({
                "size": result_size,
                "min_score": settings.BM25_SCORE_THRESHOLD,
                "query": build_bm25_filter_query(bm25_queries, filters),
            })
 
            # Hybrid query (only if we have an embedding)
            if embedding_vector and bm25_queries:
                body_lines.append({"index": index})
                body_lines.append({
                    "size": result_size,
                    "min_score": settings.HYBRID_SCORE_THRESHOLD,
                    "query": build_vector_bm25_hybrid_query(
                        embedding=embedding_vector,
                        bm25_queries=bm25_queries,
                        filters=filters,
                        knn_k=settings.DEFAULT_KNN_K,
                    ),
                })
 
        if not body_lines:
            return [], round((time.perf_counter() - t0) * 1000, 1)
 
        # Single msearch round-trip
        try:
            response = self.os_client.msearch(
                body=body_lines,
                request_timeout=settings.OS_TIMEOUT,
            )
        except Exception:
            logger.exception("msearch failed")
            elapsed = round((time.perf_counter() - t0) * 1000, 1)
            return [], elapsed
 
        # Pick first non-empty result set (narrowest geo, BM25 > hybrid)
        for resp in response.get("responses", []):
            if resp.get("error"):
                logger.warning("msearch sub-query error: %s", resp["error"])
                continue
            hits = resp.get("hits", {}).get("hits", [])
            if hits:
                elapsed = round((time.perf_counter() - t0) * 1000, 1)
                logger.info(
                    "[Search] Found %d hits in %.1fms",
                    len(hits), elapsed,
                )
                return hits[:result_size], elapsed
 
        elapsed = round((time.perf_counter() - t0) * 1000, 1)
        logger.info("[Search] No results after msearch (%.1fms)", elapsed)
        return [], elapsed
 
    @staticmethod
    def _build_geo_filter_steps(
        geo: Optional[Dict[str, Any]],
        base_filters: List[Dict],
    ) -> List[List[Dict]]:
        """
        Build filter step variants for progressive geo fallback.
 
        Priority order (narrowest → broadest):
        city → state → region → global
        """
        steps: List[List[Dict]] = []
 
        if geo and settings.ENABLE_LOCATION_FALLBACK:
 
            mode = geo.get("mode")
 
            if mode == "city":
                steps.append(
                    base_filters + [{"term": {"ad_city": geo["city"]}}]
                )
                if geo.get("state"):
                    steps.append(
                        base_filters + [{"term": {"ad_state": geo["state"]}}]
                    )
                if geo.get("region_allied_states"):
                    steps.append(
                        base_filters + [{"terms": {"ad_state": geo["region_allied_states"]}}]
                    )
 
            elif mode == "multi_city":
                cities = [
                    c["city"] for c in geo.get("cities", []) if c.get("city")
                ]
                if cities:
                    steps.append(
                        base_filters + [{"terms": {"ad_city": cities}}]
                    )
                states = {
                    c["state"] for c in geo.get("cities", []) if c.get("state")
                }
                if len(states) == 1:
                    steps.append(
                        base_filters + [{"term": {"ad_state": list(states)[0]}}]
                    )
                if geo.get("region_allied_states"):
                    steps.append(
                        base_filters + [{"terms": {"ad_state": geo["region_allied_states"]}}]
                    )
 
            elif mode == "state":
                steps.append(
                    base_filters + [{"term": {"ad_state": geo["state"]}}]
                )
                if geo.get("region_allied_states"):
                    steps.append(
                        base_filters + [{"terms": {"ad_state": geo["region_allied_states"]}}]
                    )
 
            elif mode == "multi_state":
                steps.append(
                    base_filters + [{"terms": {"ad_state": geo["states"]}}]
                )
                if geo.get("region_allied_states"):
                    steps.append(
                        base_filters + [{"terms": {"ad_state": geo["region_allied_states"]}}]
                    )
 
            elif mode in ("region", "multi_region"):
                if geo.get("region_allied_states"):
                    steps.append(
                        base_filters + [{"terms": {"ad_state": geo["region_allied_states"]}}]
                    )
 
        # Global fallback (no location filter)
        steps.append(base_filters)
 
        return steps