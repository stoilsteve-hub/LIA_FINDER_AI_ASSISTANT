from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from src.config import AppConfig
from src.models import ScoredListing


def ensure_dirs(cfg: AppConfig) -> None:
    Path(cfg.output.data_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.output.applications_dir).mkdir(parents=True, exist_ok=True)


def save_listings_json(cfg: AppConfig, listings: List[ScoredListing]) -> Path:
    path = Path(cfg.output.data_dir) / "listings.json"
    payload = [asdict(x) for x in listings]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
