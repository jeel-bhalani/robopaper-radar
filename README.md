# 🤖 RoboPaper Radar

![Tests](https://github.com/jeel-bhalani/robopaper-radar/actions/workflows/tests.yml/badge.svg)

**An automated pipeline that collects the newest robotics research papers and industry news, uses AI to summarize and categorize them, and shows everything on a searchable web dashboard.**

Every day, hundreds of new robotics papers are published on arXiv. RoboPaper Radar fetches them automatically, writes a short plain-English summary for each one, tags it with research topics, rates its difficulty, scrapes the latest robotics industry headlines, and presents it all in a dashboard with search, filters, and charts.

![Dashboard](docs/dashboard.png)

> 🚧 **Status:** In active development. Pipeline, database, AI enrichment, REST API, dashboard, scraping, daily automation, and tests with CI are working. Docker and extra features are next (see Roadmap).

---

## ✨ Features

- **Paper ingestion from the arXiv API**: newest papers in the Robotics category (`cs.RO`)
- **Responsible web scraping** of robotics industry news (checks `robots.txt`, identifies itself, stores only headlines and links)
- **PostgreSQL database** with a normalized schema (papers, authors, topics, news, pipeline runs)
- **AI enrichment with an LLM** (Claude API or local model via Ollama):
  - 2–3 sentence summary in simple English
  - 1–3 topic tags from a fixed list
  - Difficulty score from 1 to 5
- **Validation of AI output with Pydantic**: bad answers are rejected and retried, never saved
- **REST API with FastAPI**: search, filters, pagination, statistics, automatic interactive docs
- **Web dashboard** (HTML, CSS, JavaScript, Chart.js): stats, topic and timeline charts, news, search, filters, pages
- **Daily automated pipeline** with logging, fault isolation, and run tracking in the database
- **Automated tests** for the AI validation logic, run on every push with GitHub Actions
- **Safe by design**: parameterized SQL (no SQL injection), HTML escaping (no XSS), secrets in `.env`

---

## 🏗️ Architecture

```
                      ┌──────────────── pipeline.py (daily, Task Scheduler) ────────────────┐
                      │                                                                      │
arXiv API ──► load_papers.py ──► PostgreSQL ◄── ai_enrich.py ◄──► LLM (Claude / Ollama)      │
                      │              ▲   ▲            (validated with Pydantic)              │
News website ──► scrape_news.py ─────┘   │                                                   │
                      │                  │                                                   │
                      └──► logs/ + pipeline_runs table ──────────────────────────────────────┘
                                         │
                                  FastAPI (api.py)
                                         │  JSON
                                         ▼
                             Dashboard (HTML / CSS / JS)
```

---

## 🛠️ Tech Stack

| Area | Technology |
|---|---|
| Language | Python 3 |
| Data sources | arXiv API (`requests`, `feedparser`), web scraping (`BeautifulSoup`) |
| Database | PostgreSQL 18, `psycopg` |
| AI | Anthropic Claude API / Ollama (local) |
| Validation | Pydantic |
| API | FastAPI, Uvicorn |
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Automation | Python `logging`, Windows Task Scheduler |
| Testing & CI | pytest, GitHub Actions |
| Config & secrets | `python-dotenv` (`.env`) |
| Version control | Git & GitHub |
| Development | VS Code, AI coding assistant (Claude) |

---

## 📁 Project Structure

```
robopaper-radar/
├── .github/workflows/
│   └── tests.yml           # runs tests on every push
├── docs/
│   └── dashboard.png       # screenshot
├── frontend/
│   ├── index.html          # dashboard structure
│   ├── style.css           # dashboard design
│   └── app.js              # calls the API, renders papers, charts, news
├── logs/                   # pipeline logs (ignored by Git)
├── notes/
│   └── LEARNING_LOG.md     # progress, concepts, and bugs fixed
├── sql/
│   └── schema.sql          # database tables
├── src/
│   ├── fetch_arxiv.py      # get papers from the arXiv API
│   ├── db.py               # database connection
│   ├── init_db.py          # create / update tables
│   ├── load_papers.py      # save papers and authors
│   ├── llm.py              # talk to the AI model (Claude or Ollama)
│   ├── analysis.py         # prompt + validation of AI output
│   ├── ai_enrich.py        # AI summaries, topics, difficulty
│   ├── scrape_news.py      # responsible news scraper
│   ├── schemas.py          # API response models
│   ├── api.py              # REST API + serves the dashboard
│   └── pipeline.py         # runs all steps with logging
├── tests/
│   └── test_analysis.py    # unit tests for AI output validation
├── run_pipeline.bat        # entry point for Task Scheduler
├── pytest.ini              # test settings
├── .env                    # secrets (NOT in Git)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🗄️ Database Schema

```
papers ──< paper_authors >── authors
   │
   └────< paper_topics  >── topics

news_articles        pipeline_runs
```

| Table | Purpose |
|---|---|
| `papers` | One row per paper: arXiv ID (unique), title, abstract, date, URL, AI summary, difficulty |
| `authors` / `paper_authors` | Authors and the many-to-many link to papers (with author order) |
| `topics` / `paper_topics` | Research topics and the many-to-many link to papers |
| `news_articles` | Scraped headlines (URL unique) |
| `pipeline_runs` | One row per automated run: status, counts, errors |

---

## 🔌 API Endpoints

Interactive docs are available at `http://127.0.0.1:8000/docs`.

| Endpoint | Description |
|---|---|
| `GET /health` | API and database status |
| `GET /papers` | Papers with `search`, `topic`, `difficulty`, `limit`, `offset` |
| `GET /papers/{arxiv_id}` | One paper with full abstract |
| `GET /topics` | Topics with paper counts |
| `GET /stats/papers-per-day` | Paper count per day |
| `GET /authors/top` | Authors with the most papers |
| `GET /news` | Latest scraped industry news |

Example: `GET /papers?topic=manipulation&difficulty=3&limit=5`

---

## 🚀 Getting Started

### Requirements
- Python 3.11+
- PostgreSQL with a database named `robopaper`
- An Anthropic API key **or** Ollama installed locally

### Setup (Windows / PowerShell)

```powershell
git clone https://github.com/jeel-bhalani/robopaper-radar.git
cd robopaper-radar
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project folder:

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/robopaper

# AI – Option A: Claude API
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=your-key-here
CLAUDE_MODEL=claude-haiku-5-5
AI_LIMIT=100

# AI – Option B: local model
# LLM_PROVIDER=ollama
# OLLAMA_MODEL=llama3.2
```

### Run

```powershell
python src/init_db.py                      # create tables
python src/pipeline.py                     # fetch papers, AI enrich, scrape news
uvicorn api:app --reload --app-dir src     # start API + dashboard
```

Open the dashboard at **http://127.0.0.1:8000/**

### Run single steps

```powershell
python src/load_papers.py      # fetch and save papers
python src/ai_enrich.py 5      # AI-process 5 papers (test small first)
python src/scrape_news.py      # scrape news headlines
```

### Run tests

```powershell
pytest -v
```

The tests check the AI validation rules: valid answers pass, extra text around the JSON is ignored, topics are cleaned and deduplicated, and invalid answers (unknown topics, difficulty outside 1–5, too many topics, too-long summaries, missing or broken JSON) are rejected. They use fake AI answers, so they need no database, API key, or internet. GitHub Actions runs them on every push.

### Daily automation (Windows)
`run_pipeline.bat` is scheduled with Windows Task Scheduler (daily). Logs are written to `logs/pipeline.log`, and every run is recorded in the `pipeline_runs` table.

---

## 🧠 Design Decisions

- **Fixed topic list:** keeps tags consistent ("RL" vs "reinforcement learning"), so charts and analysis are reliable.
- **Never trust AI output blindly:** every answer is parsed and validated (length, topics, score range) before saving, and these rules are covered by unit tests.
- **Idempotent steps:** `ON CONFLICT DO NOTHING`, unique URLs, and `ai_processed_at IS NULL` mean every step can run daily with no duplicates and no paying twice for AI.
- **Commit per item:** one failed paper never loses the others, and failed items are retried next run.
- **Fault isolation in the pipeline:** each step runs separately; one failure gives status `partial`, not a full crash.
- **Logging + run table:** text logs for debugging, database records for monitoring.
- **Cost control:** `AI_LIMIT` caps AI calls per run.
- **Responsible scraping:** `robots.txt` check, honest User-Agent, same-site links only, headlines only, and a loud error if the page layout changes.
- **Security:** parameterized SQL, HTML escaping in the dashboard, input limits in the API (422 for invalid values), secrets only in `.env`.
- **Reproducible installs:** `requirements.txt` lists only direct dependencies with pinned versions.

---

## 🗺️ Roadmap

- [x] Fetch papers from the arXiv API
- [x] Store papers and authors in PostgreSQL
- [x] AI summaries, topic tags, difficulty scores
- [x] Validation of AI output
- [x] REST API with FastAPI
- [x] Web dashboard (HTML, CSS, JavaScript, charts)
- [x] Web scraping of robotics industry news
- [x] Daily automated pipeline with logging
- [x] Unit tests for AI output validation + CI with GitHub Actions
- [ ] Docker & docker-compose
- [ ] "Chat with papers" (semantic search / RAG)
- [ ] Data quality report page + insights from real data
- [ ] More tests (API endpoints, scraper)
- [ ] Email digest of new papers

---

## 🤝 AI-Assisted Development

This project was built with the help of an AI coding assistant (Claude) for planning, explanations, and debugging. All code was run, tested, and debugged by me. The bugs found and fixed along the way, including feedback from a code review, are documented in `notes/LEARNING_LOG.md`.