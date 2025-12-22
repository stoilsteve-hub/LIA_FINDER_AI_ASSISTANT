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
    desired_start: str  # e.g. "2026-10"


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


# -----------------------------
# Loader
# -----------------------------

def load_config(path: str) -> AppConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))

    strict = StrictConfig(**raw["search"].get("strict", {}))
    query = QueryConfig(**raw["search"].get("query", {}))

    search = SearchConfig(
        locations=raw["search"]["locations"],
        remote_ok=raw["search"]["remote_ok"],
        lia_terms=raw["search"]["lia_terms"],
        java_terms=raw["search"]["java_terms"],
        not_lia_terms=raw["search"]["not_lia_terms"],
        strict=strict,
        query=query,
    )

    target = TargetConfig(**raw["lia"].get("target", {}))

    lia = LIAConfig(
        start_date=raw["lia"]["start_date"],
        end_date=raw["lia"]["end_date"],
        target=target,
    )

    output = OutputConfig(**raw["output"])

    return AppConfig(search=search, lia=lia, output=output)
