from __future__ import annotations

import os
from typing import List

import httpx

from src.config import AppConfig
from src.discovery.web_sources import Source
from src.models import Listing

# -------------------------------------------------
# HARD FILTER TERMS (English + Swedish combined)
# -------------------------------------------------

# Must clearly be LIA / internship
LIA_TERMS = [
    # Swedish
    "lia",
    "praktik",
    "praktikplats",
    "lärande i arbete",
    "yh",
    "yrkeshögskola",

    # English
    "internship",
    "intern",
    "trainee",
    "work placement",
]

# Must clearly be Java / JVM related
JAVA_TERMS = [
    "java",
    "jvm",
    "spring",
    "spring boot",
    "spring security",
    "spring data",
    "hibernate",
    "jpa",
    "jdbc",
    "maven",
    "gradle",
    "kotlin",

    # backend / architecture
    "backend",
    "backendutvecklare",
    "systemutvecklare",
    "javautvecklare",
    "microservice",
    "microservices",
    "mikroservice",
    "mikroservicar",
    "rest",
    "api",

    # integration / messaging
    "kafka",
    "rabbitmq",

    # testing / QA
    "junit",
    "selenium",
    "test automation",
    "testautomatisering",
    "sdet",
]

# Clear signals it is NOT an LIA
NOT_LIA_TERMS = [
    # Swedish
    "tillsvidare",
    "heltid",
    "fast anställning",
    "senior",
    "lead",
    "principal",

    # English
    "full-time",
    "permanent",
    "senior developer",
]


# -------------------------------------------------
# QUERY BUILDER
# -------------------------------------------------

def _build_queries(cfg: AppConfig) -> list[str]:
    """
    Multiple focused queries give much better recall
    than one large query.
    """
    locations = cfg.search.locations or ["Stockholm"]
    loc = " ".join(locations)

    queries = [
        f"LIA Java {loc}",
        f"praktik Java {loc}",
        f"\"lärande i arbete\" Java {loc}",
        f"yrkeshögskola Java {loc}",
        f"internship Java {loc}",
        f"LIA Spring Boot {loc}",
        f"praktik Spring Boot {loc}",
        f"LIA backend Java {loc}",
        f"praktik backend Java {loc}",
        f"LIA Kotlin {loc}",
        f"LIA microservices Java {loc}",
        f"LIA API Java {loc}",
        f"LIA testautomation Java {loc}",
    ]

    if cfg.search.remote_ok:
        queries.extend([
            "LIA Java distans",
            "praktik Java distans",
            "internship Java remote",
            "LIA backend Java remote",
            "LIA Spring Boot remote",
        ])

    return queries


def _contains_any(text: str, terms: list[str]) -> bool:
    t = text.lower()
    return any(term in t for term in terms)


# -------------------------------------------------
# MAIN FETCH FUNCTION
# -------------------------------------------------

def fetch_listings(cfg: AppConfig, sources: List[Source]) -> List[Listing]:
    api_key = os.getenv("JOBTECH_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Missing JOBTECH_API_KEY. Create a .env file and set JOBTECH_API_KEY=..."
        )

    headers = {
        "Accept": "application/json",
        "api-key": api_key,
        "User-Agent": "LIA_FINDER_AI_ASSISTANT/1.0",
    }

    listings: List[Listing] = []
    queries = _build_queries(cfg)

    with httpx.Client(headers=headers, timeout=25.0) as client:
        for s in sources:
            if getattr(s, "kind", "") != "jobtech_jobsearch":
                continue

            search_url = f"{s.base_url}/search"

            for q in queries:
                resp = client.get(search_url, params={"q": q, "limit": 50})
                resp.raise_for_status()
                data = resp.json()

                for h in data.get("hits", []) or []:
                    title = h.get("headline") or h.get("title") or ""
                    employer = (h.get("employer") or {}).get("name") or ""

                    workplace = h.get("workplace_address") or {}
                    location = workplace.get("municipality") or workplace.get("city") or ""

                    ad_id = h.get("id") or ""
                    webpage_url = h.get("webpage_url") or ""
                    url_ = webpage_url or (f"{s.base_url}/ad/{ad_id}" if ad_id else "")

                    desc = None
                    d = h.get("description")
                    if isinstance(d, dict):
                        desc = d.get("text")
                    elif isinstance(d, str):
                        desc = d

                    combined = f"{title}\n{desc or ''}".lower()

                    # Exclude obvious non-LIA roles
                    if _contains_any(combined, NOT_LIA_TERMS):
                        continue

                    # HARD GATES: MUST be LIA AND MUST be Java
                    if not _contains_any(combined, LIA_TERMS):
                        continue
                    if not _contains_any(combined, JAVA_TERMS):
                        continue

                    if title and url_:
                        listings.append(
                            Listing(
                                title=title,
                                company=employer,
                                location=location,
                                url=url_,
                                description=desc,
                                source=s.name,
                            )
                        )

    # Deduplicate by URL
    seen = set()
    uniq: List[Listing] = []
    for l in listings:
        if l.url not in seen:
            seen.add(l.url)
            uniq.append(l)

    return uniq
