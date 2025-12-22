from __future__ import annotations

import os
from typing import List

import httpx

from src.config import AppConfig
from src.discovery.web_sources import Source
from src.models import Listing

LIA_TERMS = ["lia", "praktik", "lärande i arbete", "yh", "yrkeshögskola", "internship", "trainee"]


def _build_queries(cfg: AppConfig) -> list[str]:
    locations = cfg.search.locations or ["Stockholm"]
    loc_part = " OR ".join(locations)

    base = [
        f"LIA {loc_part}",
        f"praktik {loc_part}",
        f"\"lärande i arbete\" {loc_part}",
        f"yrkeshögskola {loc_part}",
        f"internship {loc_part}",
    ]
    if cfg.search.remote_ok:
        base.extend(
            [
                "LIA distans",
                "praktik distans",
                "internship remote",
                "hybrid praktik",
            ]
        )
    return base


def fetch_listings(cfg: AppConfig, sources: List[Source]) -> List[Listing]:
    api_key = os.getenv("JOBTECH_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Missing JOBTECH_API_KEY. Create a .env file in the project root and set JOBTECH_API_KEY=..."
        )

    listings: List[Listing] = []
    queries = _build_queries(cfg)

    headers = {
        "Accept": "application/json",
        "api-key": api_key,
        "User-Agent": "LIA_FINDER_AI_ASSISTANT/1.0",
    }

    with httpx.Client(headers=headers, timeout=25.0) as client:
        for s in sources:
            if s.kind != "jobtech_jobsearch":
                continue

            search_url = f"{s.base_url}/search"

            for q in queries:
                resp = client.get(search_url, params={"q": q, "limit": 50})
                resp.raise_for_status()
                data = resp.json()

                hits = data.get("hits", []) or []
                for h in hits:
                    title = h.get("headline") or h.get("title") or ""
                    employer = (h.get("employer") or {}).get("name") or ""
                    workplace = h.get("workplace_address") or {}
                    location = workplace.get("municipality") or workplace.get("city") or ""

                    ad_id = h.get("id") or ""
                    webpage_url = h.get("webpage_url") or ""
                    url_ = webpage_url or (f"{s.base_url}/ad/{ad_id}" if ad_id else "")

                    desc = None
                    desc_obj = h.get("description")
                    if isinstance(desc_obj, dict):
                        desc = desc_obj.get("text")
                    elif isinstance(desc_obj, str):
                        desc = desc_obj

                    # HARD FILTER: must look like LIA/praktik
                    text = f"{title} {desc or ''}".lower()
                    if not any(term in text for term in LIA_TERMS):
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
