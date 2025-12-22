from __future__ import annotations

import sys
import time
from datetime import datetime
from typing import Optional

import shutil
from pathlib import Path

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

# Outreach imports
from src.outreach.generate import (
    load_companies,
    load_profile,
    slugify,
    draft_email_sv,
    draft_linkedin_dm_sv,
    write_outreach_email_txt,
    write_linkedin_dm_txt,
    write_personligt_brev_docx,
    write_cv_highlights_docx,
)


def run_monitor(console: Console) -> None:
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


def run_monitor_daemon(console: Console, interval_minutes: int = 30) -> None:
    console.print(
        f"[bold green]Monitor daemon started[/bold green] — checking every {interval_minutes} minutes. "
        "Press [bold]Stop[/bold] in PyCharm to end.\n"
    )
    while True:
        try:
            console.print(f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim] Running monitor…")
            run_monitor(console)
        except Exception as e:
            console.print(f"[red]Monitor error:[/red] {e}")

        console.print(f"[dim]Sleeping {interval_minutes} minutes…[/dim]\n")
        time.sleep(interval_minutes * 60)


def run_outreach(console: Console, mode: str = "cold") -> None:
    cfg = load_config("config.yaml")
    ensure_dirs(cfg)

    companies = load_companies("companies.yaml")
    profile = load_profile("profile.yaml")

    base = Path(cfg.output.applications_dir)
    base.mkdir(parents=True, exist_ok=True)

    cv_src = Path("assets") / "cv.pdf"
    if not cv_src.exists():
        console.print("[yellow]Warning:[/yellow] assets/cv.pdf not found. Letters/DM will still be generated.")

    for c in companies:
        if not c.name:
            continue

        folder = base / slugify(c.name)
        folder.mkdir(parents=True, exist_ok=True)

        if cv_src.exists():
            shutil.copy2(cv_src, folder / "cv.pdf")

        subject, body = draft_email_sv(cfg, c, profile, mode=mode)
        write_outreach_email_txt(folder, subject, body)

        dm = draft_linkedin_dm_sv(cfg, c, profile)
        write_linkedin_dm_txt(folder, dm)

        write_personligt_brev_docx(folder, cfg, c, profile, variant="kort")
        write_personligt_brev_docx(folder, cfg, c, profile, variant="standard")

        write_cv_highlights_docx(folder, cfg, c, profile)

        console.print(f"[green]Generated outreach pack:[/green] {c.name} -> {folder}")

    console.print(f"\nSaved outreach packs under: [bold]{cfg.output.applications_dir}[/bold]")


def choose_mode(console: Console) -> str:
    console.print("\n[bold]Choose what to run:[/bold]")
    console.print("  1) Monitor LIA (run once)")
    console.print("  2) Outreach Builder (generate emails/letters)")
    console.print("  3) Monitor daemon (run continuously)")

    choice = input("Enter 1, 2 or 3: ").strip()
    if choice == "2":
        return "outreach"
    if choice == "3":
        return "daemon"
    return "monitor"


def parse_arg(argv: list[str]) -> Optional[str]:
    # Accept: python main.py monitor|outreach|daemon
    if len(argv) >= 2:
        v = argv[1].strip().lower()
        if v in ("monitor", "outreach", "daemon"):
            return v
    return None


def main() -> None:
    console = Console()

    mode = parse_arg(sys.argv) or choose_mode(console)

    if mode == "daemon":
        run_monitor_daemon(console, interval_minutes=30)
    elif mode == "outreach":
        OUTREACH_MODE = "cold"  # change to "application" when replying to an ad
        run_outreach(console, mode=OUTREACH_MODE)
    else:
        run_monitor(console)


if __name__ == "__main__":
    main()
