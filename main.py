from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.table import Table

from src.config import load_config
from src.discovery.web_sources import build_default_sources
from src.discovery.fetch import fetch_listings
from src.ranking.score import score_listings
from src.storage.save import ensure_dirs, save_listings_json


def main() -> None:
    console = Console()
    cfg = load_config("config.yaml")
    ensure_dirs(cfg)

    sources = build_default_sources(cfg)
    console.print(f"[bold]Sources:[/bold] {len(sources)}")

    listings = fetch_listings(cfg, sources)
    scored = score_listings(cfg, listings)

    save_listings_json(cfg, scored)

    table = Table(title="Top matches (preview)")
    table.add_column("Score", justify="right")
    table.add_column("Title")
    table.add_column("Company")
    table.add_column("Location")
    table.add_column("Link")

    for item in scored[:10]:
        table.add_row(
            f"{item.score:.1f}",
            item.title[:40],
            item.company[:25],
            item.location[:18],
            item.url[:60],
        )

    console.print(table)
    console.print(f"\nSaved: [bold]{cfg.output.data_dir}/listings.json[/bold]")


if __name__ == "__main__":
    main()
