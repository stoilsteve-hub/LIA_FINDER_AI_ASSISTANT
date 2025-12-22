from __future__ import annotations

from dataclasses import dataclass
from typing import List

from src.config import AppConfig


@dataclass(frozen=True)
class Source:
    name: str
    kind: str  # "jobtech_jobsearch"
    base_url: str


def build_default_sources(cfg: AppConfig) -> List[Source]:
    return [
        Source(
            name="JobTechJobSearch",
            kind="jobtech_jobsearch",
            base_url="https://jobsearch.api.jobtechdev.se",
        )
    ]
