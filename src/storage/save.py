from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Set

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


def load_seen_urls(cfg: AppConfig) -> Set[str]:
    path = Path(cfg.output.data_dir) / "seen_ads.json"
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return set(str(x) for x in data)
    except Exception:
        pass
    return set()


def save_seen_urls(cfg: AppConfig, urls: Set[str]) -> Path:
    path = Path(cfg.output.data_dir) / "seen_ads.json"
    path.write_text(json.dumps(sorted(urls), ensure_ascii=False, indent=2), encoding="utf-8")
    return path
