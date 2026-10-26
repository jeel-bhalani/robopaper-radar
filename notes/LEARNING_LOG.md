# 📒 RoboPaper Radar – Learning Log

My personal notes: what I built, what I learned, which errors I faced, and how I solved them.
I add a new section after every day of work.

---

## 📍 Progress Overview

| Day | Topic | Status |
|---|---|---|
| 1 | Project setup, Git, first API call (arXiv) | ✅ Done |
| 2 | PostgreSQL database and SQL | ✅ Done |
| 3 | AI summaries, topic tags, validation | ✅ Done |
| 4 | REST API with FastAPI | ✅ Done |
| 5 | Web dashboard (HTML, CSS, JavaScript) | ✅ Done |
| 6 | Web scraping | ✅ Done |
| 7 | Automation (daily pipeline) | ✅ Done |
| 8 | Docker | ⏳ Next |
| 9 | Extra features (RAG chat, quality report, tests, CI) | ⬜ |

---

## Day 1 – Project Setup & First API Call

### What I built
- Project folder with a clean structure (`src/`, `data/`)
- Virtual environment, `.gitignore`, `README.md`, `requirements.txt`
- `fetch_arxiv.py`: gets the newest robotics papers from the arXiv API and saves them to CSV
- First commit and push to GitHub

### Concepts I learned

| Concept | Meaning |
|---|---|
| **Virtual environment (venv)** | A separate box of Python libraries just for this project |
| **requirements.txt** | List of libraries the project needs (`pip install -r requirements.txt`) |
| **Git / commit** | Saves the history of my code; a commit is one saved snapshot |
| **.gitignore** | Files Git should NOT save (venv, secrets, data, logs) |
| **API** | A way for programs to ask another service for data using a URL and parameters |
| **Parameters** | The "question" sent to the API (category, number of results, sort order) |
| **XML / feed** | The format arXiv returns; `feedparser` turns it into Python objects |
| **Data cleaning** | Fixing raw data, e.g. removing line breaks from titles |
| **`if __name__ == "__main__"`** | Code that runs only when the file is started directly |

---

## Day 2 – PostgreSQL Database

### What I built
- PostgreSQL 18 + pgAdmin, database `robopaper`
- `sql/schema.sql`: tables `papers`, `authors`, `paper_authors`
- `db.py`, `init_db.py`, `load_papers.py`, and `.env` for the password

### Concepts I learned

| Concept | Meaning |
|---|---|
| **Database vs CSV** | Adds instead of overwriting, blocks duplicates, answers questions fast |
| **Schema** | The design of the tables (columns and rules) |
| **PRIMARY KEY / UNIQUE** | Unique ID of a row / database refuses duplicate values |
| **FOREIGN KEY (REFERENCES)** | Link between tables; no links to rows that don't exist |
| **Many-to-many** | One paper has many authors, one author many papers → link table |
| **Normalization** | Splitting data into tables so nothing is stored twice |
| **SQL basics** | `SELECT`, `INSERT`, `WHERE`, `ORDER BY`, `LIMIT`, `COUNT`, `JOIN`, `GROUP BY` |
| **`.env` file** | Secrets outside the code, never on GitHub |
| **Parameterized query (`%s`)** | Values sent separately from SQL → protects against **SQL injection** |
| **`ON CONFLICT DO NOTHING`** | Skip a row that already exists |
| **Idempotent** | Running many times gives the same result, no duplicates |
| **Transaction / commit** | Changes saved all together, or not at all on error |

---

## Day 3 – AI Enrichment

### What I built
- `llm.py` (Claude API or Ollama, switchable in `.env`)
- `analysis.py` (prompt, fixed topic list, Pydantic validation)
- `ai_enrich.py` (summary, topics, difficulty for unprocessed papers)
- Tables `topics`, `paper_topics`, new columns in `papers`

### Concepts I learned

| Concept | Meaning |
|---|---|
| **LLM** | Large Language Model, AI that reads and writes text |
| **API key** | Password for a paid API; stays secret in `.env` |
| **Prompt / prompt engineering** | Instruction to the AI; exact numbers work better than vague words |
| **Structured output (JSON)** | AI answers in JSON so Python can read fields directly |
| **Pydantic / validation** | Automatic checks of shape and values; bad AI answers rejected |
| **Fixed category list** | Keeps tags consistent for reliable analysis |
| **Tokens / `max_tokens`** | Pieces of words / maximum length of the AI answer |
| **Thinking block** | Part of the answer where the model reasons before the final text |
| **`stop_reason`** | Why the API stopped (finished, or hit `max_tokens`) |
| **Rate limit** | Max requests per minute; `time.sleep(1)` avoids it |
| **Commit / rollback per item** | Save each paper separately; undo only the failed one |
| **Migration** | Changing the database step by step (`ALTER TABLE ... IF NOT EXISTS`) |
| **Provider abstraction** | `ask_llm()` hides which AI is used |
| **Human evaluation** | Checking AI output against the real paper |

---

## Day 4 – REST API with FastAPI

### What I built
- `schemas.py`: response models (`Paper`, `PaperDetail`, `TopicCount`, `DayCount`, `AuthorCount`)
- `api.py`: endpoints `/health`, `/papers`, `/papers/{arxiv_id}`, `/topics`, `/stats/papers-per-day`, `/authors/top`
- Automatic interactive docs at `/docs`

### Concepts I learned

| Concept | Meaning |
|---|---|
| **REST API** | A "waiter" between users and the database; fixed endpoints return JSON |
| **Endpoint** | One URL the API offers, e.g. `/papers` |
| **HTTP methods** | `GET` read, `POST` create, `PUT` update, `DELETE` delete |
| **Path parameter** | Part of the URL, for one item: `/papers/{arxiv_id}` |
| **Query parameter** | After `?`, for filters/options: `/papers?topic=slam&limit=5` |
| **Status codes** | `200` OK, `404` not found, `422` invalid input, `500` server error |
| **Response model** | Pydantic class that defines what the API returns |
| **Input validation (`Query(ge=, le=)`)** | FastAPI rejects bad values automatically (422) |
| **Pagination (`limit` / `offset`)** | Return data in pages, never everything at once |
| **`array_agg`** | SQL: collect many rows into one list (authors per paper) |
| **Uvicorn / server / port** | Program that runs the API; `127.0.0.1:8000` = this computer, door 8000 |
| **`--reload`** | Restart automatically when code changes (development only) |
| **Swagger docs (`/docs`)** | Documentation generated automatically from the code |
| **Inheritance** | `PaperDetail(Paper)` = everything in `Paper` plus more |

---

## Day 5 – Web Dashboard

### What I built
- `frontend/index.html`, `style.css`, `app.js`
- Stats cards, topic bar chart, papers-per-day line chart, search, filters, pagination
- FastAPI serves the dashboard at `/` (`StaticFiles`)

### Concepts I learned

| Concept | Meaning |
|---|---|
| **HTML / CSS / JavaScript** | Structure / design / behavior of a web page |
| **`id` vs `class`** | Unique name (for JS) vs group name (for styling) |
| **CSS variables (`--accent`)** | Change one color, it changes everywhere |
| **Grid / Flexbox** | Main CSS layout tools: rows+columns / items in a line |
| **Responsive design (`@media`)** | Layout adapts to phone screens |
| **`fetch` + `async/await`** | Call an API from JavaScript without freezing the page |
| **`Promise.all`** | Send several requests at the same time |
| **DOM / `innerHTML`** | The live page structure / put new HTML into it |
| **Events (`addEventListener`)** | React to typing, clicks, dropdown changes |
| **Debounce** | Wait until the user stops typing → 1 request instead of 8 |
| **XSS + `escapeHtml`** | Outside data could run code in the page → always escape it |
| **CDN** | Public server for libraries (Chart.js) |
| **Same origin / static files** | One server delivers API + website, so no CORS problems |
| **Route order** | FastAPI checks routes in order; `mount("/")` must be last |
| **Browser DevTools (F12)** | Console = JS errors, Network = every API call |

---

## Day 6 – Web Scraping

### What I built
- `scrape_news.py`: scrapes robotics industry headlines with BeautifulSoup
- Table `news_articles`, endpoint `/news`, news section on the dashboard

### Concepts I learned

| Concept | Meaning |
|---|---|
| **Web scraping** | Downloading a page and extracting data from its HTML |
| **API vs scraping** | API = clean, stable data; scraping = messy, can break |
| **`robots.txt`** | File where a site says what bots may visit; always check it |
| **User-Agent** | How a program identifies itself; honest bots say who they are |
| **Inspect (DevTools)** | Find where data sits in the HTML |
| **CSS selector** | "Address" of elements; used for styling AND for scraping |
| **`soup.select()`** | BeautifulSoup's way to find elements by selector |
| **Relative vs absolute URL (`urljoin`)** | `/news/abc` → `https://site.com/news/abc` |
| **Scraped data cleaning** | Remove short links, duplicates, links to other sites |
| **Silent failure** | Site layout changes → scraper finds 0 items; must be detected |
| **Copyright** | Store only headlines + links, not full articles |

---

## Day 7 – Automation

### What I built
- Scripts now **return** results; `pipeline.py` runs all steps
- `logs/pipeline.log`, table `pipeline_runs`, optional email digest (`digest.py`)
- `run_pipeline.bat` + Windows Task Scheduler (daily)

### Concepts I learned

| Concept | Meaning |
|---|---|
| **Pipeline / orchestration** | Running several steps automatically in the right order |
| **Return vs print** | Print is for humans, return is for other code |
| **`raise` in automated jobs** | Nobody reads warnings at 8 AM; errors must be recorded |
| **Logging** | Timestamped messages to screen and file, with levels (INFO, WARNING, ERROR) |
| **`log.exception`** | Saves the full error traceback in the log |
| **Fault isolation** | One failed step doesn't stop the others |
| **Run status** | `success` / `partial` / `failed` |
| **Monitoring** | Storing run results as data to answer questions later |
| **`lambda`** | Tiny function created on the spot |
| **Cost control (`AI_LIMIT`)** | Cap paid API calls in automatic jobs |
| **Exit code** | `0` = OK, other = error; read by schedulers, Docker, CI |
| **SMTP / `starttls`** | Protocol for sending email / encrypt the connection |
| **App password** | Special password for apps, not the normal account password |
| **Batch file (`.bat`)** | Windows script that starts the pipeline with the venv's Python |
| **`PYTHONUTF8=1`** | Prevents emoji/UTF-8 crashes on Windows when output goes to a file |
| **Task Scheduler** | Windows tool to run programs on a schedule |

---

## 🐞 Errors I Faced & How I Solved Them

| # | Day | Error | Cause | Solution | Lesson |
|---|---|---|---|---|---|
| 1 | 1 | `ensurepip ... returned non-zero exit status 1` | Windows Python install problem; pip couldn't be installed in the venv | Deleted broken folder, created the venv again (project moved to `D:\robopaper-radar`) | Fix the environment first |
| 2 | 1 | `The term '.env' is not recognized as ... cmdlet` | Pasted `.gitignore` content into the **terminal** | Pasted it into the `.gitignore` file | Terminal = commands. Editor = file contents |
| 3 | 1 | Couldn't switch to the D drive in cmd | `cd D:\...` alone doesn't change drive in cmd | `D:` first, or `cd /d D:\folder` | cmd and PowerShell behave differently |
| 4 | 2 | Unsure what to install in Stack Builder | It offers optional extras | Cancelled; only Server, pgAdmin, Command Line Tools needed | Don't install what you don't need |
| 5 | 2 | Couldn't find where to create the `sql` folder | Looked in pgAdmin | Created it in the VS Code Explorer | pgAdmin = database. VS Code = files |
| 6 | 3 | `ModuleNotFoundError: No module named 'pydantic'` | Library not installed in the venv | `pip install anthropic ollama pydantic` | "No module named X" → `pip install X` |
| 7 | 3 | `string_too_long` for `summary` | Prompt only said "short" | Prompt: "MAXIMUM 60 words"; limit 800 | Exact numbers in prompts + always validate |
| 8 | 3 | `'ThinkingBlock' object has no attribute 'text'` | Code took `content[0]`, which was a thinking block | Join only blocks with `type == "text"` | Don't trust positions like `[0]` in API data |
| 9 | 3 | `No JSON found in AI response` | `max_tokens=500` too small; thinking used it up | `max_tokens=2000` + `stop_reason` check + print raw answer | Print the real data; check why the API stopped |
| 10 | 4 | `unicorn ... CommandNotFoundException` | Typo: `unicorn` instead of `uvicorn` | Typed `uvicorn` | CommandNotFound = typo or not installed |
| 11 | 5 | `{"detail":"Not Found"}` on the dashboard (`GET / 404`) | File named `indext.html` instead of `index.html` | Renamed the file (F2) | File names must be exact; read the server log |
| 12 | 6 | Dashboard showed "Could not load news" | `/news` endpoint was placed after `app.mount("/")`, which catches all URLs | Moved the endpoint above the mount | Route order matters; test the endpoint URL directly |
| 13 | 5 | Topic chart showed only every second label | Chart.js auto-skips labels when space is tight | `ticks: { autoSkip: false }` | Read library options |
| 14 | 5 | "Papers per day" was a flat line at 50 | Not a bug: arXiv publishes in daily batches, and I fetched 50 per run | Will become a real trend with daily automation | Check if "weird" data is real before "fixing" it |
| — | 7 | (Prevented) emoji crash when output goes to a file on Windows | Windows default encoding isn't UTF-8 | `set PYTHONUTF8=1` in `run_pipeline.bat` | Think about the environment where code runs unattended |

---

## 🎤 Interview Stories

1. **Validation saved my data:** AI summaries broke my length rule; Pydantic caught them, nothing bad was saved, and a more specific prompt fixed it.
2. **Unexpected API response:** my code assumed the first block was text, but sometimes it was a thinking block. I changed it to search for text blocks.
3. **Hidden cause:** "No JSON found" was really a token limit problem. I raised the limit, added a `stop_reason` check, and logged raw responses.
4. **Safe re-runs:** every step is idempotent, so the daily pipeline never creates duplicates or pays twice for AI.
5. **Security in two layers:** parameterized SQL against SQL injection in the backend, and HTML escaping against XSS in the frontend, because titles come from outside sources.
6. **Route order bug:** my new endpoint returned 404 because a catch-all static mount was registered first. I found it by calling the endpoint directly and reading the server log.
7. **Responsible scraping:** robots.txt check, honest User-Agent, only headlines, and a loud failure when the layout changes instead of silently saving nothing.
8. **Reliable automation:** fault isolation per step, `success/partial/failed` status, logs for debugging, a database table for monitoring, and a cost limit on AI calls.
9. **Data vs bug:** a flat chart looked like a bug, but it was how arXiv publishes papers in daily batches.

---

## 🧾 SQL Cheat Sheet (queries that worked)

```sql
-- Count papers
SELECT COUNT(*) FROM papers;

-- 5 newest papers
SELECT title, published_at FROM papers ORDER BY published_at DESC LIMIT 5;

-- Authors with most papers
SELECT a.name, COUNT(*) AS paper_count
FROM authors a
JOIN paper_authors pa ON pa.author_id = a.id
GROUP BY a.name ORDER BY paper_count DESC LIMIT 10;

-- Most common topics
SELECT t.name, COUNT(*) AS papers
FROM topics t
JOIN paper_topics pt ON pt.topic_id = t.id
GROUP BY t.name ORDER BY papers DESC;

-- Average difficulty per topic
SELECT t.name, ROUND(AVG(p.difficulty), 1) AS avg_difficulty
FROM papers p
JOIN paper_topics pt ON pt.paper_id = p.id
JOIN topics t ON t.id = pt.topic_id
GROUP BY t.name ORDER BY avg_difficulty DESC;

-- Papers per day
SELECT DATE(published_at) AS day, COUNT(*) AS paper_count
FROM papers GROUP BY day ORDER BY day;

-- Latest scraped news
SELECT title, url, scraped_at FROM news_articles ORDER BY scraped_at DESC LIMIT 10;

-- Pipeline run history
SELECT id, started_at, status, new_papers, ai_processed, ai_failed, new_news, errors
FROM pipeline_runs ORDER BY id DESC;
```

---

## 📝 Template for Next Days (copy this)

```markdown
## Day X – Title

### What I built
-

### Concepts I learned
| Concept | Meaning |
|---|---|
|  |  |

### Errors (also add them to the error table above)
-
```