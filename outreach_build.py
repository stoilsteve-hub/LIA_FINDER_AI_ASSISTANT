from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from src.config import load_config
from src.outreach.generate import (
    load_companies,
    slugify,
    draft_outreach_email_sv,
    write_outreach_email_txt,
    write_personligt_brev_docx,
    write_cv_highlights_docx,
)


def main() -> None:
    cfg = load_config("config.yaml")
    companies = load_companies("companies.yaml")

    base = Path(cfg.output.applications_dir)
    base.mkdir(parents=True, exist_ok=True)

    for c in companies:
        if not c.name:
            continue

        folder = base / slugify(c.name)
        subject, body = draft_outreach_email_sv(cfg, c)

        write_outreach_email_txt(folder, subject, body)
        write_personligt_brev_docx(folder, cfg, c)
        write_cv_highlights_docx(folder, cfg, c)

        print(f"Generated outreach pack for: {c.name} -> {folder}")


if __name__ == "__main__":
    main()

