# 🤖 RoboPaper Radar

![Tests](https://github.com/jeel-bhalani/robopaper-radar/actions/workflows/tests.yml/badge.svg)

**An automated pipeline that collects the newest robotics research papers and industry news, uses AI to summarize and categorize them, checks data quality, and shows everything on a searchable web dashboard. Runs fully in Docker.**

Every day, hundreds of new robotics papers are published on arXiv. RoboPaper Radar fetches them automatically, writes a short plain-English summary for each one, tags it with research topics, rates its difficulty, scrapes the latest robotics industry headlines, checks that the data can be trusted, and presents it all in a dashboard with search, filters, and charts.

![Dashboard](docs/dashboard.png)

## 📊 Insights from my data

_Based on 186 robotics papers published between 2026-10-24 and 2026-10-27. Average AI-rated difficulty: 3.9/5. Generated with `src/insights.py`._

**Top research topics (last 30 days)**

| Topic | Papers | Share of papers |
|---|---|---|
| manipulation | 87 | 47% |
| foundation models | 59 | 32% |
| simulation | 50 | 27% |
| perception | 50 | 27% |
| control | 44 | 24% |

_A paper can have up to 3 topics, so shares add up to more than 100%._

**Hardest topics (average difficulty, at least 3 papers)**

| Topic | Avg difficulty | Papers |
|---|---|---|
| locomotion | 4.1 | 15 |
| multi-robot | 4.1 | 17 |
| aerial robots | 4.0 | 18 |
| control | 4.0 | 44 |
| reinforcement learning | 4.0 | 39 |

**Topics that appear together most often**

| Topic A | Topic B | Papers |
|---|---|---|
| manipulation | foundation models | 43 |
| manipulation | simulation | 25 |
| manipulation | reinforcement learning | 17 |
| manipulation | perception | 16 |
| control | simulation | 14 |

**Papers by publication weekday**

| Weekday | Papers |
|---|---|
| Mon | 72 |
| Tue | 72 |
| Sat | 5 |
| Sun | 37 |>

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
- **REST API with FastAPI**: search, filters, pagination, statistics, quality report, automatic interactive docs
- **Web dashboard** (HTML, CSS, JavaScript, Chart.js): stats, topic and timeline charts, news, search, filters, pages
- **Data quality report**: automatic checks for AI coverage, missing topics/authors/abstracts, pipeline freshness, and run status, plus a run history
- **Insights from real data**: analysis script for topic trends, difficulty, topic pairs, and publishing patterns
- **Daily automated pipeline** with logging, fault isolation, and run tracking in the database
- **Docker setup**: database, API, and scheduler start with one command
- **37 automated tests** (AI validation, scraper, quality checks, API) running on every push with GitHub Actions, plus a Docker build check
- **Safe by design**: parameterized SQL (no SQL injection), HTML escaping (no XSS), secrets only in `.env`, browsers always revalidate frontend files

---

## 🏗️ Architecture

```
docker compose up
│
├── scheduler container ─ pipeline.py (now, then every 24h)
│      arXiv API ──► load_papers.py ──┐
│      News site ──► scrape_news.py ──┼──► PostgreSQL ◄──► ai_enrich.py ◄──► LLM (Claude / Ollama)
│                                     │        ▲               (validated with Pydantic)
│      logs/ + pipeline_runs table ◄──┘        │
│                                              │
├── db container ─ PostgreSQL 18 (data in a Docker volume)
│                                              │
└── api container ─ FastAPI (api.py) ──────────┘
                       │ JSON
                       ▼
        Dashboard + Data quality page (HTML / CSS / JS)
```

---

## 🛠️ Tech Stack

| Area | Technology |
|---|---|
| Language | Python 3.12 |
| Data sources | arXiv API (`requests`, `feedparser`), web scraping (`BeautifulSoup`) |
| Database | PostgreSQL 18, `psycopg` |
| AI | Anthropic Claude API / Ollama (local) |
| Validation | Pydantic |
| API | FastAPI, Uvicorn |
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Automation | Python `logging`, Docker scheduler container (Windows Task Scheduler as alternative) |
| Containers | Docker, Docker Compose |
| Testing & CI | pytest, FastAPI TestClient, GitHub Actions |
| Config & secrets | `python-dotenv` (`.env`) |
| Version control | Git & GitHub |
| Development | VS Code, AI coding assistant (Claude) |

---

## 📁 Project Structure

```
robopaper-radar/
├── .github/workflows/
│   └── tests.yml           # tests + Docker build on every push
├── docs/
│   └── dashboard.png       # screenshot
├── frontend/
│   ├── index.html          # dashboard
│   ├── quality.html        # data quality report
│   ├── style.css           # shared design
│   ├── app.js              # dashboard logic
│   └── quality.js          # quality report logic
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
│   ├── quality.py          # data quality check rules
│   ├── insights.py         # analysis queries → Markdown tables
│   ├── schemas.py          # API response models
│   ├── api.py              # REST API + serves the frontend
│   └── pipeline.py         # runs all steps with logging
├── tests/
│   ├── test_analysis.py    # AI output validation
│   ├── test_scraper.py     # headline parsing rules
│   ├── test_quality.py     # quality check rules
│   └── test_api.py         # API endpoints (with a fake database)
├── Dockerfile              # how to build the app image
├── .dockerignore           # files kept out of the image
├── compose.yaml            # db + api + scheduler
├── run_pipeline.bat        # alternative: Windows Task Scheduler
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
| `GET /quality` | Data quality report: checks, numbers, difficulty distribution, recent runs |

Example: `GET /papers?topic=manipulation&difficulty=3&limit=5`

---

## 🚀 Getting Started (Docker, recommended)

### Requirements
- Docker Desktop
- An Anthropic API key **or** Ollama installed locally

### 1. Clone

```powershell
git clone https://github.com/jeel-bhalani/robopaper-radar.git
cd robopaper-radar
```

### 2. Create a `.env` file

```
# Docker database
POSTGRES_PASSWORD=choose-a-password

# AI – Option A: Claude API
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=your-key-here
CLAUDE_MODEL=claude-haiku-5-5
AI_LIMIT=100

# AI – Option B: local model
# LLM_PROVIDER=ollama
# OLLAMA_MODEL=llama3.2
# OLLAMA_HOST=http://host.docker.internal:11434

# Only for running without Docker
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/robopaper
```

### 3. Start everything

```powershell
docker compose up --build -d
```

This starts three containers:
- **db**: PostgreSQL 18 (data kept in a Docker volume)
- **api**: FastAPI + dashboard on port 8000
- **scheduler**: runs the pipeline immediately, then every 24 hours

| Page | URL |
|---|---|
| Dashboard | http://127.0.0.1:8000/ |
| Data quality report | http://127.0.0.1:8000/quality.html |
| API docs | http://127.0.0.1:8000/docs |

### Useful commands

```powershell
docker compose ps                                  # status
docker compose logs -f scheduler                   # watch the pipeline
docker compose exec api python src/insights.py     # print data insights
docker compose down                                # stop (data is kept)
```

⚠️ `docker compose down -v` also deletes the database volume.

### Running without Docker (local development)

Requires Python 3.11+ and a local PostgreSQL with a database named `robopaper`.

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src/init_db.py
python src/pipeline.py
uvicorn api:app --reload --app-dir src
```

### Run tests

```powershell
pytest -v
```

37 tests check:
- **AI validation:** valid answers pass; unknown topics, difficulty outside 1–5, too many topics, too-long summaries, and missing or broken JSON are rejected
- **Scraper:** relative links become absolute; duplicates, short titles, links to other sites, and links outside articles are filtered out
- **Quality checks:** each rule gives `ok` or `warning` correctly, including edge cases like an empty database
- **API:** responses, 404 for unknown papers, 422 for invalid parameters (without touching the database), filters passed as SQL parameters, cache headers

The tests use fake data and a fake database, so they need no PostgreSQL, API key, or internet. GitHub Actions runs them on every push and also checks that the Docker image builds.

---

## 🧠 Design Decisions

- **Fixed topic list:** keeps tags consistent ("RL" vs "reinforcement learning"), so charts and analysis are reliable.
- **Never trust AI output blindly:** every answer is parsed and validated before saving, and these rules are covered by tests.
- **Idempotent steps:** `ON CONFLICT DO NOTHING`, unique URLs, and `ai_processed_at IS NULL` mean every step can run daily with no duplicates and no paying twice for AI.
- **Commit per item:** one failed paper never loses the others; failed items are retried next run.
- **Fault isolation in the pipeline:** each step runs separately; one failure gives status `partial`, not a full crash.
- **Monitoring:** text logs for debugging, a `pipeline_runs` table and a quality report page for monitoring.
- **Thresholds from domain knowledge:** e.g. "newest paper ≤ 4 days old," because arXiv doesn't publish on weekends.
- **Pure functions for testability:** parsing (`parse_headlines`) and check rules (`build_checks`) are separated from network and database code, so they can be tested with fake data.
- **Cost control:** `AI_LIMIT` caps AI calls per run.
- **Responsible scraping:** `robots.txt` check, honest User-Agent, same-site links only, headlines only, and a loud error if the page layout changes.
- **Security:** parameterized SQL, HTML escaping, API input limits (422), secrets only in `.env` and never in the Docker image.
- **Docker:** one command for the whole stack; the database waits for a healthcheck; data lives in a volume; libraries are installed before copying code for fast rebuilds.
- **Fresh frontend for every user:** HTML/CSS/JS are sent with `Cache-Control: no-cache`, so browsers check for updates (cheap 304 if unchanged).
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
- [x] Tests (AI validation, scraper, quality checks, API) + CI with GitHub Actions
- [x] Docker & docker-compose
- [x] Data quality report page
- [x] Insights from real data
- [ ] "Chat with papers" (semantic search / RAG)
- [ ] Email digest of new papers
- [ ] Deployment to a cloud server

---

## 🤝 AI-Assisted Development

This project was built with the help of an AI coding assistant (Claude) for planning, explanations, and debugging. All code was run, tested, and debugged by me. The bugs found and fixed along the way, including feedback from a code review and a difficult Docker/WSL setup on Windows, are documented in `notes/LEARNING_LOG.md`.