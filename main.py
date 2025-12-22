from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.table import Table

from src.config import load_config
from src.discovery.web_sources import build_default_sources
from src.discovery.fetch import fetch_listings
from src.ranking.score import score_listings
from src.storage.save import (
    ensure_dirs,
    save_listings_json,
    load_seen_urls,
    save_seen_urls,
)


def main() -> None:
    console = Console()
    cfg = load_config("config.yaml")
    ensure_dirs(cfg)

    sources = build_default_sources(cfg)
    console.print(f"[bold]Sources:[/bold] {len(sources)}")

    listings = fetch_listings(cfg, sources)
    scored = score_listings(cfg, listings)
    save_listings_json(cfg, scored)

    seen = load_seen_urls(cfg)
    new_items = [x for x in scored if x.url not in seen]

    # Update seen with all current URLs
    seen_updated = set(seen)
    for x in scored:
        seen_updated.add(x.url)
    save_seen_urls(cfg, seen_updated)

    table = Table(title="NEW matches (Java + LIA) — since last run")
    table.add_column("Score", justify="right")
    table.add_column("Title")
    table.add_column("Company")
    table.add_column("Location")
    table.add_column("Link")

    if not new_items:
        console.print("[yellow]No new matches since last run.[/yellow]")
    else:
        for item in new_items[:25]:
            table.add_row(
                f"{item.score:.1f}",
                (item.title or "")[:50],
                (item.company or "")[:28],
                (item.location or "")[:18],
                (item.url or "")[:80],
            )
        console.print(table)

    console.print(f"\nSaved full list: [bold]{cfg.output.data_dir}/listings.json[/bold]")
    console.print(f"Saved seen URLs: [bold]{cfg.output.data_dir}/seen_ads.json[/bold]")


if __name__ == "__main__":
    main()
