from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml


# -----------------------------
# Search-related configs
# -----------------------------

@dataclass(frozen=True)
class StrictConfig:
    title_must_contain_lia: bool = True
    must_contain_java: bool = True


@dataclass(frozen=True)
class QueryConfig:
    max_per_query: int = 50
    add_remote_queries: bool = True


@dataclass(frozen=True)
class LinkedInConfig:
    enabled: bool = True
    queries: List[str] = None
    strict: bool = False
    not_lia_terms: List[str] = None


@dataclass(frozen=True)
class SearchConfig:
    locations: List[str]
    remote_ok: bool

    lia_terms: List[str]
    java_terms: List[str]
    not_lia_terms: List[str]

    strict: StrictConfig
    query: QueryConfig


# -----------------------------
# LIA timing / target
# -----------------------------

@dataclass(frozen=True)
class TargetConfig:
    desired_start: str  # e.g. "2026-10" or "oktober 2026"


@dataclass(frozen=True)
class LIAConfig:
    start_date: str
    end_date: str
    target: TargetConfig


# -----------------------------
# Output
# -----------------------------

@dataclass(frozen=True)
class OutputConfig:
    data_dir: str
    applications_dir: str


@dataclass(frozen=True)
class AppConfig:
    search: SearchConfig
    lia: LIAConfig
    output: OutputConfig
    linkedin: LinkedInConfig


# -----------------------------
# Loader
# -----------------------------

def load_config(path: str) -> AppConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}

    # ---- search ----
    raw_search = raw.get("search", {}) or {}

    strict = StrictConfig(**(raw_search.get("strict", {}) or {}))
    query = QueryConfig(**(raw_search.get("query", {}) or {}))

    search = SearchConfig(
        locations=list(raw_search.get("locations", []) or []),
        remote_ok=bool(raw_search.get("remote_ok", True)),
        lia_terms=list(raw_search.get("lia_terms", []) or []),
        java_terms=list(raw_search.get("java_terms", []) or []),
        not_lia_terms=list(raw_search.get("not_lia_terms", []) or []),
        strict=strict,
        query=query,
    )

    # ---- linkedin ----
    raw_linkedin = raw.get("linkedin", {}) or {}
    linkedin = LinkedInConfig(
        enabled=bool(raw_linkedin.get("enabled", True)),
        queries=list(raw_linkedin.get("queries", []) or []),
        strict=bool(raw_linkedin.get("strict", False)),
        not_lia_terms=list(raw_linkedin.get("not_lia_terms", []) or []),
    )

    # ---- lia ----
    raw_lia = raw.get("lia", {}) or {}
    raw_target = raw_lia.get("target", {}) or {}
    target = TargetConfig(
        desired_start=str(raw_target.get("desired_start", "oktober 2026"))
    )

    lia = LIAConfig(
        start_date=str(raw_lia.get("start_date", "")),
        end_date=str(raw_lia.get("end_date", "")),
        target=target,
    )

    # ---- output ----
    raw_output = raw.get("output", {}) or {}
    output = OutputConfig(
        data_dir=str(raw_output.get("data_dir", "data")),
        applications_dir=str(raw_output.get("applications_dir", "data/applications")),
    )

    return AppConfig(search=search, lia=lia, output=output, linkedin=linkedin)
