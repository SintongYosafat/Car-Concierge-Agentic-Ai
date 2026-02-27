"""
Location Resolution & Normalization

This module provides deterministic (non-fuzzy) geographic resolution
from free-form user queries.

Capabilities:
- Text normalization & alias resolution
- City / state / region extraction (exact match only)
- Multi-region & multi-admin support
- Admin-type disambiguation (kota vs kabupaten)

Design principles:
- No fuzzy matching (predictable & debuggable)
- Pre-built indexes for fast lookup
- Alias-first normalization to reduce ambiguity
"""

import re
from typing import Dict, Any, List, Optional

from app_strands_agent.engine.geo_data import REGION_TO_STATE_TO_CITIES, ALL_ALIASES


# TEXT NORMALIZATION
def normalize_text(text: str) -> str:
    """
    Normalize text for comparison purposes.

    Steps:
    - Lowercase
    - Remove punctuation
    - Collapse multiple whitespaces

    Parameters
    ----------
    text : str
        Raw input text.

    Returns
    -------
    str
        Normalized text suitable for regex matching.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ALIAS NORMALIZATION
def normalize_aliases(text: str) -> str:
    """
    Replace known aliases with their canonical names.

    Alias replacement happens BEFORE geographic extraction
    to ensure consistent matching.

    Example
    -------
    'jakarta' -> 'jakarta d k i'

    Parameters
    ----------
    text : str
        Raw query text.

    Returns
    -------
    str
        Normalized text with aliases resolved.
    """
    text_norm = normalize_text(text)

    for alias, canonical in ALL_ALIASES.items():
        alias_norm = normalize_text(alias)
        canonical_norm = normalize_text(canonical)

        if re.search(rf"\b{re.escape(alias_norm)}\b", text_norm):
            text_norm = re.sub(
                rf"\b{re.escape(alias_norm)}\b",
                canonical_norm,
                text_norm,
            )

    return text_norm

# CITY NAME PARSER
def parse_city_name(raw: str):
    """
    Parse city / regency names from raw data definitions.

    Supported patterns:
    - 'Bandung Kota'      -> ('Bandung', 'kota')
    - 'Bandung Kab.'      -> ('Bandung', 'kabupaten')
    - 'Kab. Pangandaran'  -> ('Pangandaran', 'kabupaten')
    - 'Jakarta Selatan'   -> ('Jakarta Selatan', 'kota')
    - 'Kab. Badung'       -> ('Badung', 'kabupaten')

    Parameters
    ----------
    raw : str
        Raw city name from data source.

    Returns
    -------
    Tuple[str, str]
        (clean_city_name, admin_type)
    """
    text = raw.strip()
    low = text.lower()

    if low.startswith("kab"):
        name = re.sub(r"^kab\.?\s*", "", text, flags=re.I)
        return name.strip(), "kabupaten"

    if re.search(r"\b(kab|kab\.)$", low):
        name = re.sub(r"\s*(kab|kab\.)$", "", text, flags=re.I)
        return name.strip(), "kabupaten"

    if re.search(r"\bkota$", low):
        name = re.sub(r"\s*kota$", "", text, flags=re.I)
        return name.strip(), "kota"

    # Default assumption: kota
    return text.strip(), "kota"


# STATIC INDEX BUILD (ONE-TIME)
CITY_INDEX: Dict[str, List[Dict[str, Any]]] = {}
STATE_INDEX: Dict[str, str] = {}
REGION_INDEX: List[str] = []

for region, states in REGION_TO_STATE_TO_CITIES.items():
    REGION_INDEX.append(normalize_text(region))

    for state, cities in states.items():
        STATE_INDEX[normalize_text(state)] = state

        for raw_city in cities:
            name, admin_type = parse_city_name(raw_city)
            key = normalize_text(name)

            CITY_INDEX.setdefault(key, []).append({
                "raw": raw_city,
                "admin_type": admin_type,
                "state": state,
                "region": region,
            })

# ADMIN TYPE HINT DETECTION
def detect_admin_hint(query: str) -> Optional[str]:
    """
    Detect administrative hints from query text.

    Parameters
    ----------
    query : str

    Returns
    -------
    Optional[str]
        'kota', 'kabupaten', or None
    """
    q = normalize_text(query)

    if re.search(r"\bkota\b", q):
        return "kota"
    if re.search(r"\b(kab|kabupaten)\b", q):
        return "kabupaten"

    return None

# EXACT MATCH EXTRACTORS
def extract_cities_exact(query: str) -> List[Dict[str, Any]]:
    """
    Extract city matches using exact (word-boundary) matching.

    Admin hints (kota/kabupaten) are applied when present.

    Parameters
    ----------
    query : str

    Returns
    -------
    List[Dict[str, Any]]
        List of matched city records.
    """
    norm = normalize_aliases(query)
    admin_hint = detect_admin_hint(query)
    results: List[Dict[str, Any]] = []

    for key, entries in CITY_INDEX.items():
        if re.search(rf"\b{re.escape(key)}\b", norm):
            if admin_hint:
                results.extend(
                    e for e in entries if e["admin_type"] == admin_hint
                )
            else:
                results.extend(entries)

    return results


def extract_states_exact(query: str) -> List[str]:
    """
    Extract exact state/province matches from query.
    """
    norm = normalize_aliases(query)
    return sorted({
        state
        for key, state in STATE_INDEX.items()
        if re.search(rf"\b{re.escape(key)}\b", norm)
    })


def extract_regions_exact(query: str) -> List[str]:
    """
    Extract exact region matches from query.
    """
    norm = normalize_aliases(query)
    return [
        region
        for region in REGION_INDEX
        if re.search(rf"\b{re.escape(region)}\b", norm)
    ]

# REGION HELPERS
def get_region_by_state(state: str) -> Optional[str]:
    """
    Resolve region name from a given state.
    """
    for region, states in REGION_TO_STATE_TO_CITIES.items():
        if state in states:
            return region
    return None


def get_region_allied_states(region: Optional[str]) -> List[str]:
    """
    Get all states belonging to the same region.
    """
    if not region:
        return []
    return sorted(REGION_TO_STATE_TO_CITIES.get(region, {}).keys())

# FINAL GEO RESOLVER (DETERMINISTIC)
def resolve_geo(query: str) -> Optional[Dict[str, Any]]:
    """
    Resolve geographic intent from a user query.

    Resolution priority:
    1. City
    2. State
    3. Region

    Supports multi-entity resolution (e.g. multiple cities or regions).

    Parameters
    ----------
    query : str

    Returns
    -------
    Optional[Dict[str, Any]]
        Structured geo resolution result or None if no match.
    """
    cities = extract_cities_exact(query)

    # CITY MODE

    if len(cities) == 1:
        city = cities[0]
        region = city["region"]
        return {
            "mode": "city",
            "city": city["raw"],
            "state": city["state"],
            "region": region,
            "region_allied_states": get_region_allied_states(region),
            "matched_by": "exact",
        }

    if len(cities) > 1:
        regions = sorted({c["region"] for c in cities})
        return {
            "mode": "multi_city",
            "cities": [
                {
                    "city": c["raw"],
                    "state": c["state"],
                    "region": c["region"],
                    "admin_type": c["admin_type"],
                }
                for c in cities
            ],
            "regions": regions,
            "region_allied_states": sorted({
                st
                for r in regions
                for st in REGION_TO_STATE_TO_CITIES.get(r, {})
            }),
            "matched_by": "exact",
        }

    
    # STATE MODE
    
    states = extract_states_exact(query)

    if len(states) == 1:
        state = states[0]
        region = get_region_by_state(state)
        return {
            "mode": "state",
            "city": None,
            "state": state,
            "region": region,
            "region_allied_states": get_region_allied_states(region),
            "matched_by": "exact",
        }

    if len(states) > 1:
        regions = sorted({
            get_region_by_state(s)
            for s in states
            if get_region_by_state(s)
        })
        return {
            "mode": "multi_state",
            "states": states,
            "regions": regions,
            "region_allied_states": sorted({
                st
                for r in regions
                for st in REGION_TO_STATE_TO_CITIES.get(r, {})
            }),
            "matched_by": "exact",
        }

    
    # REGION MODE
    
    regions = extract_regions_exact(query)

    if len(regions) == 1:
        region = regions[0]
        return {
            "mode": "region",
            "city": None,
            "state": None,
            "region": region,
            "region_allied_states": get_region_allied_states(region),
            "matched_by": "exact",
        }

    if len(regions) > 1:
        return {
            "mode": "multi_region",
            "regions": regions,
            "region_allied_states": sorted({
                st
                for r in regions
                for st in REGION_TO_STATE_TO_CITIES.get(r, {})
            }),
            "matched_by": "exact",
        }

    return None
