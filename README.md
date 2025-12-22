# LIA Finder AI Assistant

A Python-based assistant that helps discover **LIA (Lärande i Arbete)** opportunities in Sweden — with a focus on **Java / Java developer–related roles** — and prepares the groundwork for **AI-tailored applications**.

The project is designed to run locally, be compliant with platform rules, and significantly reduce the manual effort involved in finding relevant LIA placements.

---

## 🎯 Purpose

Finding relevant LIA placements (especially in software development) is time-consuming and noisy.  
This tool aims to:

- Automatically **discover LIA / praktik opportunities**
- Filter out regular full-time jobs
- Focus on **Java, backend, and JVM-related roles**
- Rank listings by relevance
- Prepare for **AI-generated, role-specific personal letters**

---

## 🔍 Current Capabilities (Phase 1)

### ✔ LIA Discovery
- Fetches real job listings from **Platsbanken (Arbetsförmedlingen)** using the official JobTech JobSearch API
- Searches specifically for:
  - `LIA`
  - `praktik`
  - `lärande i arbete`
  - `yrkeshögskola`
  - `internship`
- Supports:
  - Stockholm-based roles
  - Remote / hybrid roles

### ✔ Java-Focused Filtering
Listings are ranked higher if they mention:
- Java
- Backend development
- Software development keywords
- LIA / YH terminology

Regular full-time developer roles are penalized or filtered out.

### ✔ Ranking & Output
- Listings are scored based on relevance
- Results are shown in a clean terminal table
- All results are saved to:


---

## 🧠 Planned Features (Next Phases)

### 🔜 AI-Tailored Personal Letters
- Base personal letter + CV
- Automatically adjusted per LIA listing
- Emphasis on Java / backend skills
- Export as DOCX or PDF

### 🔜 Application Assistant
- Per-listing application folders
- Notes on how/where to apply
- Follow-up reminders

### 🔜 Improved Matching
- Skill-to-requirement matching
- LIA period date validation
- Company-specific ranking boosts

---

## 🛠 Tech Stack

- **Python 3.11**
- `httpx` – HTTP client
- `pydantic` – data modeling
- `PyYAML` – configuration
- `rich` – terminal UI
- `python-docx` – document generation (planned)
- JobTech **JobSearch API** (Platsbanken)

---

## 📁 Project Structure


LIA_FINDER_AI_ASSISTANT/
├─ main.py
├─ config.yaml
├─ requirements.txt
├─ README.md
├─ src/
│ ├─ config.py
│ ├─ models.py
│ ├─ discovery/
│ ├─ ranking/
│ ├─ letters/
│ └─ storage/
└─ data/


---

## ⚙️ Setup & Run

### 1️⃣ Create virtual environment
```bash
python3.11 -m venv .venv
source .venv/bin/activate

3️⃣ Configure API access

Create a .env file:

JOBTECH_API_KEY=your_jobtech_api_key_here

4️⃣ Run the assistant
python main.py

📌 Notes on Compliance

No LinkedIn scraping or automated applications

Uses official APIs where available

Designed as an assistant, not a spam bot

👤 Target Profile

This project is tailored for:

YH students

Java / backend developer tracks

LIA placements in Sweden (Stockholm & remote)

📄 License

Personal / educational use.
Not intended for mass automation or commercial job scraping.

