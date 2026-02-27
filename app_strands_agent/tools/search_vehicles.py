import time
from typing import List, Dict, Any, Optional
 
from strands import tool
from app_strands_agent.session_context import _current_session_id, _workflow_timings
from app_strands_agent.clients.bedrock import generate_embedding
from app_strands_agent.clients.opensearch import create_opensearch_client
from app_strands_agent.engine.geo_resolver import resolve_geo
from app_strands_agent.engine.os_engine import VehicleSearchService
from app_strands_agent.core import logger
 
 
_search_service = VehicleSearchService(create_opensearch_client())
 
 
@tool(
    name="search_vehicles",
    description=(
        "Search vehicles listed on OLX Indonesia. "
        "Use this tool when the user wants to find, browse, or compare cars. "
        "Extract structured parameters from the user query: "
        "query (brand/model keywords), location, price range, year range, mileage range."
    ),
)
def search_vehicles(
    query: str,
    location: Optional[str] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    mileage_min: Optional[int] = None,
    mileage_max: Optional[int] = None,
) -> str:
    """
    Execute vehicle search with structured parameters.
 
    The orchestrator agent extracts fields from the user's message
    and passes them directly — no second LLM call needed for intent parsing.
 
    Args:
        query: Vehicle keywords for BM25 + vector search (e.g. "toyota avanza").
        location: City, state, or region name (e.g. "Bandung", "Jawa Barat").
        price_min: Minimum price in Rupiah.
        price_max: Maximum price in Rupiah.
        year_min: Minimum year.
        year_max: Maximum year.
        mileage_min: Minimum mileage in km.
        mileage_max: Maximum mileage in km.
 
    Returns:
        Formatted vehicle search results as a string.
    """
    try:
        session_id = _current_session_id.get()
    except LookupError:
        session_id = "anonymous"
 
    logger.info(
        "search_vehicles called",
        extra={"session_id": session_id, "query": query, "location": location},
    )
 
    timings: Dict[str, float] = {}
 
    # 1. Generate embedding for vector search (LRU cached)
    t0 = time.perf_counter()
    embedding = generate_embedding(query)
    timings["tool_embed_ms"] = round((time.perf_counter() - t0) * 1000, 1)
 
    # 2. Resolve geographic location
    geo_info = resolve_geo(location) if location else None
 
    # 3. Build intent dict (compatible with existing query builders)
    intent: Dict[str, Any] = {
        "keyword": query,
        "location": location,
        "price": {"min": price_min, "max": price_max},
        "year": {"min": year_min, "max": year_max},
        "mileage": {"min": mileage_min, "max": mileage_max},
        "geo_info": geo_info,
    }
 
    logger.info("intent: %s", intent)
 
    # 4. Execute msearch (single round-trip)
    results, opensearch_ms = _search_service.search(
        keyword=query,
        intent=intent,
        embedding_vector=embedding,
    )
    timings["opensearch_ms"] = opensearch_ms
 
    # 5. Report timings to parent via ContextVar
    _workflow_timings.get().update(timings)
 
    # 6. Format results
    return _format_results(results)
 
 
def _format_results(hits: List[Dict[str, Any]]) -> str:
    if not hits:
        return "Sorry, no vehicles were found matching your search criteria."
 
    lines: List[str] = ["Here are the vehicle search results:"]
 
    for idx, hit in enumerate(hits, start=1):
        src = hit.get("_source", {})
 
        ad_id = src.get("ad_id", "-")
        make = src.get("item_make", "-")
        model = src.get("item_model", "-")
        year = src.get("item_year", "-")
        price = src.get("item_price", "-")
        city = src.get("ad_city", "-")
 
        lines.append("")
        lines.append(f"{idx}. {make} {model}")
        lines.append(f"   - Ad ID    : {ad_id}")
        lines.append(f"   - Year     : {year}")
        lines.append(f"   - Price    : Rp {price}")
        lines.append(f"   - Location : {city}")
 
        desc = src.get("ad_description")
        if desc:
            lines.append(f"   - Description: {desc}")
 
    return "\n".join(lines)