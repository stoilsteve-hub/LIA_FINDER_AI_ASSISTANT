from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml


@dataclass(frozen=True)
class SearchConfig:
    keywords: List[str]
    locations: List[str]
    remote_ok: bool


@dataclass(frozen=True)
class LIAConfig:
    start_date: str
    end_date: str


@dataclass(frozen=True)
class OutputConfig:
    data_dir: str
    applications_dir: str


@dataclass(frozen=True)
class AppConfig:
    search: SearchConfig
    lia: LIAConfig
    output: OutputConfig


def load_config(path: str) -> AppConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))

    search = SearchConfig(**raw["search"])
    lia = LIAConfig(**raw["lia"])
    output = OutputConfig(**raw["output"])

    return AppConfig(search=search, lia=lia, output=output)
