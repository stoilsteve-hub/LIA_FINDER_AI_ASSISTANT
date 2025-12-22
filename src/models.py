from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Listing:
    title: str
    company: str
    location: str
    url: str
    description: Optional[str] = None
    source: Optional[str] = None


@dataclass
class ScoredListing(Listing):
    score: float = 0.0
    reasons: Optional[list[str]] = None
