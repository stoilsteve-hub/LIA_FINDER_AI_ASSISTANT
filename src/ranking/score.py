from __future__ import annotations

from typing import List

from src.config import AppConfig
from src.models import Listing, ScoredListing


def score_listings(cfg: AppConfig, listings: List[Listing]) -> List[ScoredListing]:
    scored: List[ScoredListing] = []

    for l in listings:
        score = 0.0
        reasons: list[str] = []

        text = f"{l.title} {l.location} {l.description or ''}".lower()

        for kw in cfg.search.keywords:
            if kw.lower() in text:
                score += 10
                reasons.append(f"Matched keyword: {kw}")

        if cfg.search.remote_ok and "remote" in text:
            score += 5
            reasons.append("Remote mention")

        if any(loc.lower() in text for loc in cfg.search.locations):
            score += 3
            reasons.append("Location match")

        scored.append(
            ScoredListing(
                title=l.title,
                company=l.company,
                location=l.location,
                url=l.url,
                description=l.description,
                source=l.source,
                score=score,
                reasons=reasons,
            )
        )

    scored.sort(key=lambda x: x.score, reverse=True)
    return scored
