LIA Finder AI Assistant 🤖🇸🇪

LIA Finder AI Assistant is a Python-based tool designed to help Java developer students proactively find and prepare for LIA (Lärande i Arbete) opportunities in Sweden.

The tool continuously monitors public job sources for LIA / praktik roles related to Java and Fullstack development, ranks relevant matches, and generates company-specific outreach material (emails, personal letters, LinkedIn messages) — all in a LinkedIn ToS–safe, manual-first workflow.

✨ Key Features
🔍 LIA Monitoring (Java-focused)

Scans public, automation-friendly job sources (e.g. JobTech / Platsbanken)

Strong filtering for:

LIA / praktik / YH-related roles

Java, backend, and fullstack positions

Scores and ranks listings by relevance

Tracks previously seen ads to surface only new matches

🔁 Continuous Monitor Mode

Run once or

Run as a daemon that checks automatically at a fixed interval (e.g. every 30 minutes)

Ideal for long-term LIA tracking (e.g. 6–12 months ahead of start date)

✉️ Outreach Builder (Automated, Personalised)

For each target company, the tool generates:

📧 Tailored outreach email (Swedish)

💬 LinkedIn DM text (manual send — no automation)

📝 Personal letter (kort + standard, Swedish)

📄 CV highlights addendum (DOCX)

📎 Copies your CV (PDF) into each company folder

All content is aligned to:

Java / Fullstack focus

Your education and projects

Your personal writing tone

🔗 LinkedIn Awareness (Safe & Manual)

This project does not scrape LinkedIn (by design).

Instead, it provides:

A global LinkedIn manual checklist with ready-to-use search queries

Company-specific LinkedIn checklists, including:

Suggested search phrases

Company name + LIA / praktik / Java combinations

This keeps your workflow:

✅ Ethical

✅ ToS-compliant

✅ Low risk to your LinkedIn account

🧠 Typical Workflow

Run the monitor (once or continuously)

Review newly found LIA opportunities

Maintain a list of target companies

Run the outreach builder

Use generated material to:

Send emails

Send LinkedIn DMs manually

Apply proactively (even before ads are published)

🚀 How to Run
1️⃣ Install dependencies
pip install -r requirements.txt

2️⃣ Configure

Edit:

config.yaml — search rules, LIA timing, LinkedIn queries

companies.yaml — target companies

profile.yaml — your personal data (❗ ignored by git)

Place your CV here:

assets/cv.pdf

3️⃣ Run via PyCharm (recommended)

Right-click main.py → Run

Choose:

1 Monitor once

2 Outreach builder

3 Monitor daemon (continuous)

Or via terminal:

python main.py

📂 Project Structure (simplified)
LIA_FINDER_AI_ASSISTANT/
├── main.py                     # Unified launcher
├── outreach_build.py           # Outreach-only entry
├── config.yaml                 # Search + LinkedIn config
├── companies.yaml              # Target companies
├── profile.yaml                # Personal data (gitignored)
├── assets/
│   └── cv.pdf
├── data/
│   ├── listings.json
│   ├── seen_ads.json
│   ├── linkedin_checklist.txt
│   └── applications/
│       └── Company_Name/
│           ├── outreach_email.txt
│           ├── linkedin_dm.txt
│           ├── personligt_brev_*.docx
│           ├── cv_highlights.docx
│           └── cv.pdf
└── src/
    ├── discovery/
    ├── ranking/
    ├── outreach/
    └── storage/

🛡️ Ethics & Safety

❌ No LinkedIn scraping

❌ No automated applications

❌ No credential usage

✅ Manual-first, assistive tooling

✅ Designed for students and proactive outreach

🎯 Target Audience

Java / Fullstack YH students

LIA seekers in Sweden

Anyone preparing long-term internships via proactive outreach

📌 Future Ideas

Company contact history & follow-up tracking

Calendar reminders

GUI or tray-based monitor

Export to Notion / CSV

Support for other YH programs

📜 License

Personal / educational use.
Adapt freely for your own LIA search.
