import os
from typing import Optional

from langchain.tools import tool
import time
from typing import Any, Dict, List, Optional

from .data.mock_ads_data import filter_ads_by_criteria

@tool
def search_vehicle_ads(
    ad_id: Optional[str] = None,
    category: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    make: Optional[str] = None,
    model: Optional[str] = None,
    transmission: Optional[str] = None,
    year: Optional[int] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    limit: int = 20,
) -> dict:
    """
    Search for vehicle ads in the OLX Database.

    This tool searches through a database of car and motorcycle ads, returning
    popular vehicle models available in Indonesia.

    Args:
        ad_id (str, optional): Search by specific ad ID
        category (int, optional): Filter by category (198=car, 199=motorcycle)
        title (str, optional): Search in ad titles (case insensitive)
        description (str, optional): Search in ad descriptions (case insensitive)
        make (str, optional): Filter by vehicle make (e.g., 'toyota', 'honda')
        model (str, optional): Filter by vehicle model (e.g., 'avanza', 'vario')
        transmission (str, optional): Filter by transmission ('automatic', 'manual')
        year (int, optional): Filter by vehicle year (e.g., 2017, 2020)
        price_min (int, optional): Minimum price in Rupiah (e.g., 50000000)
        price_max (int, optional): Maximum price in Rupiah (e.g., 250000000)
        limit (int): Maximum number of results to return (default: 20)

    Returns:
        dict: Search results with vehicle ads information

    Examples:
        - Search Toyota cars: search_vehicle_ads(make="toyota", category=198)
        - Find cheap motorcycles: search_vehicle_ads(category=199, price_max=20000000)
        - Find 2020 automatic vehicles: search_vehicle_ads(transmission="automatic", year=2020)
    """
    return relevance_search_api(
        ad_id=ad_id,
        category=category,
        title=title,
        description=description,
        make=make,
        model=model,
        transmission=transmission,
        year=year,
        price_min=price_min,
        price_max=price_max,
        limit=limit,
    )


def relevance_search_api(
    ad_id: Optional[str] = None,
    category: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    make: Optional[str] = None,
    model: Optional[str] = None,
    transmission: Optional[str] = None,
    year: Optional[int] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    Mock Relevance Search API for searching ads in Indonesia database

    This function simulates searching through a database of car and motorcycle ads
    registered in external services. It returns popular car models and motorcycles in Indonesia.

    Args:
        ad_id (str, optional): Search by specific ad ID
        category (int, optional): Filter by category (198=car, 199=motorcycle)
        title (str, optional): Search in ad titles (case insensitive)
        description (str, optional): Search in ad descriptions (case insensitive)
        make (str, optional): Filter by vehicle make (e.g., 'toyota', 'honda')
        model (str, optional): Filter by vehicle model (e.g., 'avanza', 'vario')
        transmission (str, optional): Filter by transmission type ('automatic', 'manual')
        year (int, optional): Filter by vehicle year (e.g., 2017, 2020)
        price_min (int, optional): Minimum price in Rupiah (e.g., 50_000_000)
        price_max (int, optional): Maximum price in Rupiah (e.g., 250_000_000)
        limit (int): Maximum number of results to return (default: 20)

    Returns:
        Dict[str, Any]: API response containing:
            - status: Request status ('success' or 'error')
            - total_results: Total number of matching ads
            - results: List of matching ads
            - query_info: Information about the search query
            - response_time_ms: Simulated response time

    Examples:
        # Search all Toyota cars
        response = relevance_search_api(make="toyota", category=198)

        # Search motorcycles under 20 million rupiah
        response = relevance_search_api(category=199, price_max=20_000_000)

        # Search for automatic transmission vehicles from 2020
        response = relevance_search_api(transmission="automatic", year=2020)
    """
    # Simulate API processing time
    start_time = time.time()

    try:
        # Filter ads based on criteria
        filtered_ads = filter_ads_by_criteria(
            ad_id=ad_id,
            category=category,
            title=title,
            description=description,
            make=make,
            model=model,
            transmission=transmission,
            year=year,
            price_min=price_min,
            price_max=price_max,
        )

        # Apply limit
        limited_results = filtered_ads[:limit] if limit else filtered_ads

        # Calculate response time
        response_time = int((time.time() - start_time) * 1000)

        # Build query info
        query_params = {
            "ad_id": ad_id,
            "category": category,
            "title": title,
            "description": description,
            "make": make,
            "model": model,
            "transmission": transmission,
            "year": year,
            "price_min": price_min,
            "price_max": price_max,
            "limit": limit,
        }

        # Remove None values from query_params
        active_filters = {k: v for k, v in query_params.items() if v is not None}

        return {
            "status": "success",
            "total_results": len(filtered_ads),
            "results_returned": len(limited_results),
            "results": limited_results,
            "query_info": {
                "active_filters": active_filters,
                "applied_limit": limit,
                "total_available": len(filtered_ads),
            },
            "response_time_ms": response_time,
            "api_version": "1.0",
            "timestamp": int(time.time()),
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "total_results": 0,
            "results_returned": 0,
            "results": [],
            "query_info": {},
            "response_time_ms": int((time.time() - start_time) * 1000),
            "api_version": "1.0",
            "timestamp": int(time.time()),
        }

