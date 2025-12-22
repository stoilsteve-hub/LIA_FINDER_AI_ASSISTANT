from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml
from docx import Document

from src.config import AppConfig


@dataclass
class Company:
    name: str
    location: str = ""
    website: str = ""
    careers: str = ""
    contact_email: str = ""
    stack_hints: List[str] = None
    notes: str = ""


def load_companies(path: str = "companies.yaml") -> List[Company]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    items = raw.get("companies", []) or []
    out: List[Company] = []
    for c in items:
        out.append(
            Company(
                name=c.get("name", ""),
                location=c.get("location", ""),
                website=c.get("website", ""),
                careers=c.get("careers", ""),
                contact_email=c.get("contact_email", ""),
                stack_hints=c.get("stack_hints", []) or [],
                notes=c.get("notes", "") or "",
            )
        )
    return out


def slugify(name: str) -> str:
    keep = []
    for ch in name.strip():
        if ch.isalnum() or ch in (" ", "_", "-"):
            keep.append(ch)
    return "".join(keep).strip().replace(" ", "_")[:60]


def draft_outreach_email_sv(cfg: AppConfig, company: Company) -> tuple[str, str]:
    lia_start = cfg.lia.target.desired_start  # e.g. "2026-10"
    stack = ", ".join(company.stack_hints) if company.stack_hints else "Java/Spring och modern webbutveckling"

    subject = f"LIA (start {lia_start}) – Fullstack (Java + frontend) – Förfrågan om praktikplats"

    body = f"""Hej!

Jag heter [Ditt Namn] och studerar på yrkeshögskola. Jag söker en LIA-plats med start {lia_start}, med inriktning mot fullstackutveckling (Java backend + frontend).

Jag är särskilt intresserad av {company.name} eftersom ni arbetar med {stack}. Jag trivs i rollen där jag kan bidra både i backend (t.ex. Java/Spring och API:er) och frontend (t.ex. React/Vue/Angular), och jag vill gärna utvecklas i en miljö med bra kodkultur och samarbete.

Skulle ni kunna tänka er att ta emot en LIA-student under hösten 2026? Jag skickar gärna CV (PDF) och ett personligt brev, eller bokar ett kort samtal för att berätta mer.

Tack på förhand!
Vänliga hälsningar,
[Ditt Namn]
[Telefon]
[LinkedIn/GitHub]
"""
    return subject, body


def write_outreach_email_txt(folder: Path, subject: str, body: str) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "outreach_email.txt"
    path.write_text(f"SUBJECT: {subject}\n\n{body}", encoding="utf-8")
    return path


def write_personligt_brev_docx(folder: Path, cfg: AppConfig, company: Company) -> Path:
    """
    Template-based Swedish personal letter tailored to company + fullstack Java profile.
    (No hallucinations: we keep placeholders for your real facts.)
    """
    lia_start = cfg.lia.target.desired_start
    stack = ", ".join(company.stack_hints) if company.stack_hints else "Java/Spring, API:er och modern frontend"

    doc = Document()
    doc.add_heading("Personligt brev", level=1)

    doc.add_paragraph(f"Hej {company.name}!")
    doc.add_paragraph(
        f"Jag söker en LIA-plats med start {lia_start} och vill arbeta som fullstackutvecklare "
        f"med fokus på Java i backend och modern frontend. Jag är intresserad av {company.name} "
        f"eftersom er verksamhet matchar det jag vill utvecklas inom: {stack}."
    )

    doc.add_paragraph("Kort om mig:")
    doc.add_paragraph("• Jag studerar [YH-program] och söker LIA under hösten 2026.", style=None)
    doc.add_paragraph("• Jag vill bidra i backend (Java/Spring, REST/API) och frontend (React/Vue/Angular).", style=None)
    doc.add_paragraph("• Jag gillar att arbeta strukturerat, kommunicera tydligt och ta ansvar för leveranser.", style=None)

    doc.add_paragraph("Varför jag passar hos er:")
    doc.add_paragraph(
        "• Jag har ett praktiskt fokus och vill snabbt bli produktiv i teamet genom att ta mindre uppgifter "
        "som växer i ansvar över tid."
    )
    doc.add_paragraph(
        "• Jag är van vid att jobba med Git, kodgranskning och att bryta ner krav till konkreta uppgifter."
    )

    doc.add_paragraph(
        "Jag bifogar mitt CV (PDF) och berättar gärna mer i ett kort samtal. "
        "Tack för att ni tar er tid att läsa – jag ser fram emot att höra från er."
    )

    doc.add_paragraph("Vänliga hälsningar,")
    doc.add_paragraph("[Ditt Namn]")
    doc.add_paragraph("[Telefon]  |  [E-post]  |  [LinkedIn/GitHub]")

    path = folder / "personligt_brev.docx"
    doc.save(str(path))
    return path


def write_cv_highlights_docx(folder: Path, cfg: AppConfig, company: Company) -> Path:
    """
    A 1-page addendum that complements your PDF CV: tailored highlights for this company.
    """
    lia_start = cfg.lia.target.desired_start
    stack = ", ".join(company.stack_hints) if company.stack_hints else "Java/Spring + modern frontend"

    doc = Document()
    doc.add_heading("CV Highlights – LIA Fullstack (Java + Frontend)", level=1)
    doc.add_paragraph(f"Mål: LIA start {lia_start} | Företag: {company.name}")
    if company.website:
        doc.add_paragraph(f"Webb: {company.website}")
    if company.careers:
        doc.add_paragraph(f"Karriärsida: {company.careers}")

    doc.add_heading("Relevanta styrkor (anpassas per roll)", level=2)
    doc.add_paragraph("• Java backend: Spring Boot, REST API, databas/persistence (JPA/Hibernate).")
    doc.add_paragraph("• Frontend: React/Vue/Angular (beroende på projekt), komponenttänk och API-integration.")
    doc.add_paragraph("• Arbetsmetodik: Git, code reviews, agilt arbetssätt, tydlig kommunikation.")
    doc.add_paragraph("• Fokus: bygga fungerande features end-to-end med kvalitet och lärande i team.")

    doc.add_heading("Matchning mot ert stack/spår", level=2)
    doc.add_paragraph(f"• Jag vill särskilt fördjupa mig inom: {stack}.")
    doc.add_paragraph("• Jag kan bidra tidigt genom att ta avgränsade uppgifter och växa i ansvar över tiden.")

    doc.add_heading("Projekt/erfarenhet (fyll i)", level=2)
    doc.add_paragraph("• Projekt 1: [kort beskrivning] – tech: Java/Spring + [frontend].")
    doc.add_paragraph("• Projekt 2: [kort beskrivning] – tech: [backend] + [frontend] + [DB].")

    path = folder / "cv_highlights.docx"
    doc.save(str(path))
    return path
