from __future__ import annotations

import os
from typing import List

import httpx

from src.config import AppConfig
from src.discovery.web_sources import Source
from src.models import Listing


def _contains_any(text: str, terms: list[str]) -> bool:
    t = text.lower()
    return any(term.lower() in t for term in terms)


def _build_queries(cfg: AppConfig) -> list[str]:
    locations = cfg.search.locations or ["Stockholm"]
    loc = " ".join(locations)

    # Focused LIA+Java combos (best recall)
    base = [
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
        f"LIA test automation Java {loc}",
        f"LIA testautomatisering Java {loc}",
    ]

    if cfg.search.remote_ok and cfg.search.query.add_remote_queries:
        base += [
            "LIA Java distans",
            "praktik Java distans",
            "internship Java remote",
            "LIA backend Java remote",
            "LIA Spring Boot remote",
            "LIA Java hybrid",
        ]

    # Deduplicate while preserving order
    seen = set()
    uniq = []
    for q in base:
        if q not in seen:
            seen.add(q)
            uniq.append(q)
    return uniq


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

    queries = _build_queries(cfg)
    limit = cfg.search.query.max_per_query

    # Debug counters (helps tuning)
    kept = 0
    dropped_not_lia = 0
    dropped_not_java = 0
    dropped_not_lia_title = 0
    dropped_not_lia_terms = 0

    listings: List[Listing] = []

    with httpx.Client(headers=headers, timeout=25.0) as client:
        for s in sources:
            if getattr(s, "kind", "") != "jobtech_jobsearch":
                continue

            search_url = f"{s.base_url}/search"

            for q in queries:
                resp = client.get(search_url, params={"q": q, "limit": limit})
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

                    title_l = title.lower()
                    combined_l = f"{title}\n{desc or ''}".lower()

                    # Exclude obvious non-LIA/permanent jobs
                    if _contains_any(combined_l, cfg.search.not_lia_terms):
                        dropped_not_lia += 1
                        continue

                    # LIA gate
                    if cfg.search.strict.title_must_contain_lia:
                        if not _contains_any(title_l, cfg.search.lia_terms):
                            dropped_not_lia_title += 1
                            continue
                    else:
                        if not _contains_any(combined_l, cfg.search.lia_terms):
                            dropped_not_lia_terms += 1
                            continue

                    # Java gate
                    if cfg.search.strict.must_contain_java:
                        if not _contains_any(combined_l, cfg.search.java_terms):
                            dropped_not_java += 1
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
                        kept += 1

    # Print debug summary (super useful while tuning)
    print(
        f"Filter summary: kept={kept}, dropped_not_lia={dropped_not_lia}, "
        f"dropped_not_java={dropped_not_java}, dropped_not_lia_title={dropped_not_lia_title}, "
        f"dropped_not_lia_terms={dropped_not_lia_terms}"
    )

    # Deduplicate by URL
    seen = set()
    uniq: List[Listing] = []
    for l in listings:
        if l.url not in seen:
            seen.add(l.url)
            uniq.append(l)

    return uniq
