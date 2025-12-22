from __future__ import annotations

import shutil
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from src.config import load_config
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


def main() -> None:
    cfg = load_config("config.yaml")
    companies = load_companies("companies.yaml")
    profile = load_profile("profile.yaml")

    # Toggle:
    # - "cold" for proactive outreach (no ad)
    # - "application" when replying to an actual ad/role
    MODE = "cold"

    base = Path(cfg.output.applications_dir)
    base.mkdir(parents=True, exist_ok=True)

    cv_src = Path("assets") / "cv.pdf"

    for c in companies:
        if not c.name:
            continue

        folder = base / slugify(c.name)
        folder.mkdir(parents=True, exist_ok=True)

        # Copy CV PDF into each company folder
        if cv_src.exists():
            shutil.copy2(cv_src, folder / "cv.pdf")

        # Email (SV): cold outreach or application reply
        subject, body = draft_email_sv(cfg, c, profile, mode=MODE)
        write_outreach_email_txt(folder, subject, body)

        # LinkedIn DM (SV)
        dm = draft_linkedin_dm_sv(cfg, c, profile)
        write_linkedin_dm_txt(folder, dm)

        # Letters: short + standard
        write_personligt_brev_docx(folder, cfg, c, profile, variant="kort")
        write_personligt_brev_docx(folder, cfg, c, profile, variant="standard")

        # CV highlights addendum
        write_cv_highlights_docx(folder, cfg, c, profile)

        print(f"Generated outreach pack for: {c.name} -> {folder}")


if __name__ == "__main__":
    main()
