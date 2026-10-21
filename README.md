# 🤖 RoboPaper Radar

**An automated pipeline that collects the newest robotics research papers, uses AI to summarize and categorize them, and stores everything in a database for search and trend analysis.**

Every day, hundreds of new robotics papers are published on arXiv. RoboPaper Radar fetches them automatically, writes a short plain-English summary for each one, tags it with research topics, rates its difficulty, and makes the results searchable.

> 🚧 **Status:** In active development. Data pipeline, database, and AI enrichment are working. API, dashboard, scraping, automation, and Docker are next (see Roadmap).

---

## ✨ Features (so far)

- **Paper ingestion from the arXiv API**: fetches the newest papers in the Robotics category (`cs.RO`)
- **PostgreSQL database** with a normalized schema (papers, authors, topics, and many-to-many link tables)
- **Duplicate protection**: database constraints and idempotent inserts, so the pipeline can run any number of times safely
- **AI enrichment with an LLM** (Claude API or a local model via Ollama):
  - 2–3 sentence summary in simple English
  - 1–3 topic tags from a fixed list
  - Difficulty score from 1 to 5
- **Validation of AI output with Pydantic**: wrong or badly formatted AI answers are rejected and retried, never saved
- **Swappable AI provider**: switch between a cloud API and a local model by changing one setting

---

## 🏗️ Architecture

```
arXiv API ──► fetch_arxiv.py ──► load_papers.py ──► PostgreSQL
                                                       │
                                                       ▼
                       LLM (Claude / Ollama) ◄── ai_enrich.py
                                │                      │
                                └──► analysis.py ──────┘
                                     (validate JSON with Pydantic,
                                      save only valid results)
```

---

## 🛠️ Tech Stack

| Area | Technology |
|---|---|
| Language | Python 3 |
| Data source | arXiv API (`requests`, `feedparser`) |
| Database | PostgreSQL 18, `psycopg` |
| AI | Anthropic Claude API / Ollama (local) |
| Validation | Pydantic |
| Config & secrets | `python-dotenv` (`.env` file) |
| Version control | Git & GitHub |
| Development | VS Code, AI coding assistant (Claude) |

---

## 📁 Project Structure

```
robopaper-radar/
├── data/                 # CSV exports (ignored by Git)
├── notes/
│   └── LEARNING_LOG.md   # progress, concepts, and bugs fixed
├── sql/
│   └── schema.sql        # database tables
├── src/
│   ├── fetch_arxiv.py    # get papers from the arXiv API
│   ├── db.py             # database connection
│   ├── init_db.py        # create / update tables
│   ├── load_papers.py    # save papers and authors to the database
│   ├── llm.py            # talk to the AI model (Claude or Ollama)
│   ├── analysis.py       # prompt + validation of AI output
│   └── ai_enrich.py      # add AI summaries, topics, difficulty
├── .env                  # secrets (NOT in Git)
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
```

| Table | Purpose |
|---|---|
| `papers` | One row per paper: arXiv ID (unique), title, abstract, date, URL, AI summary, difficulty |
| `authors` | One row per author |
| `paper_authors` | Links papers and authors (many-to-many), with author order |
| `topics` | Research topics (e.g. manipulation, navigation) |
| `paper_topics` | Links papers and topics (many-to-many) |

---

## 🚀 Getting Started

### Requirements
- Python 3.11+
- PostgreSQL (with a database named `robopaper`)
- An Anthropic API key **or** Ollama installed locally

### Setup (Windows / PowerShell)

```powershell
git clone https://github.com/YOUR-USERNAME/robopaper-radar.git
cd robopaper-radar
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project folder:

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/robopaper

# Option A: Claude API
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=your-key-here
CLAUDE_MODEL=claude-haiku-5-5

# Option B: local model
# LLM_PROVIDER=ollama
# OLLAMA_MODEL=llama3.2
```

### Run the pipeline

```powershell
python src/init_db.py          # create tables
python src/load_papers.py      # fetch papers and save them
python src/ai_enrich.py 5      # AI-process 5 papers (test first!)
python src/ai_enrich.py 50     # process more
```

### Example output

```
Using claude. Papers to process: 3

✅ Learning Adaptable Dexterous Skills via Hybrid Dexterous Mim...
   ['manipulation', 'reinforcement learning'] | difficulty 4
✅ Planning under Noise with Neural Operators
   ['navigation', 'control'] | difficulty 5
```

### Example analysis query

```sql
-- Most common research topics right now
SELECT t.name, COUNT(*) AS papers
FROM topics t
JOIN paper_topics pt ON pt.topic_id = t.id
GROUP BY t.name
ORDER BY papers DESC;
```

---

## 🧠 Design Decisions

- **Fixed topic list:** prevents messy tags like "RL", "reinforcement learning", and "Reinforcement-Learning" for the same thing, which keeps analysis and charts reliable.
- **Never trust AI output blindly:** every AI answer is parsed and validated (length, topic list, score range) before it reaches the database.
- **Idempotent pipeline:** `ON CONFLICT DO NOTHING` and the `ai_processed_at IS NULL` filter mean scripts can be re-run safely, with no duplicates and no paying twice for the same AI call.
- **Commit per paper:** if one paper fails, all others are still saved, and the failed one is retried on the next run.
- **Secrets in `.env`:** database password and API key are never in the code or on GitHub.

---

## 🗺️ Roadmap

- [x] Fetch papers from the arXiv API
- [x] Store papers and authors in PostgreSQL
- [x] AI summaries, topic tags, and difficulty scores
- [x] Validation of AI output
- [ ] REST API with FastAPI
- [ ] Web dashboard (HTML, CSS, JavaScript, charts)
- [ ] Web scraping of robotics lab / conference pages
- [ ] Daily automated pipeline + email digest
- [ ] Docker & docker-compose
- [ ] "Chat with papers" (semantic search / RAG)
- [ ] Data quality report page
- [ ] Tests (pytest) and CI with GitHub Actions

---

## 🤝 AI-Assisted Development

This project was built with the help of an AI coding assistant (Claude) for planning, explanations, and debugging. All code was run, tested, and debugged by me. The bugs found and fixed along the way are documented in `notes/LEARNING_LOG.md`.