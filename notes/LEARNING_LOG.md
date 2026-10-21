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
| 4 | REST API with FastAPI | ⏳ Next |
| 5 | Web dashboard (HTML, CSS, JavaScript) | ⬜ |
| 6 | Web scraping | ⬜ |
| 7 | Automation (daily pipeline) | ⬜ |
| 8 | Docker | ⬜ |
| 9 | Extra features (RAG chat, quality report, tests) | ⬜ |

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
| **Virtual environment (venv)** | A separate box of Python libraries just for this project, so projects don't mix |
| **requirements.txt** | List of libraries the project needs. Anyone can install them with `pip install -r requirements.txt` |
| **Git** | Saves the history of my code. I can go back to older versions |
| **Commit** | One saved snapshot of my code with a message |
| **.gitignore** | List of files Git should NOT save (venv, secrets, data) |
| **API** | A way for programs to ask another service for data using a URL and parameters |
| **Parameters** | The "question" sent to the API (category, how many results, sort order) |
| **XML / feed** | The data format arXiv returns; `feedparser` turns it into Python objects |
| **Data cleaning** | Fixing raw data, e.g. removing line breaks from titles |
| **`if __name__ == "__main__"`** | Code that runs only when I start the file directly, not when another file imports it |

---

## Day 2 – PostgreSQL Database

### What I built
- Installed PostgreSQL 18 + pgAdmin, created the `robopaper` database
- `sql/schema.sql`: tables `papers`, `authors`, `paper_authors`
- `db.py` (connection), `init_db.py` (create tables), `load_papers.py` (save papers)
- `.env` file for the database password

### Concepts I learned

| Concept | Meaning |
|---|---|
| **Database vs CSV** | A database adds data instead of overwriting, blocks duplicates, and answers questions fast |
| **Table / row / column** | Like an Excel sheet: columns = fields, rows = records |
| **Schema** | The design of the tables (which columns, which rules) |
| **PRIMARY KEY** | The unique ID of each row |
| **UNIQUE** | The database refuses duplicate values (data quality enforced by the database) |
| **FOREIGN KEY (REFERENCES)** | A link between tables. Prevents links to rows that don't exist |
| **Many-to-many relationship** | One paper has many authors, one author has many papers. Solved with a link table |
| **Normalization** | Splitting data into separate tables so nothing is stored twice |
| **SQL** | Language to talk to the database: `SELECT`, `INSERT`, `WHERE`, `ORDER BY`, `LIMIT`, `COUNT`, `JOIN`, `GROUP BY` |
| **`.env` file** | Stores secrets (passwords, API keys) outside the code. Never goes to GitHub |
| **Parameterized query (`%s`)** | Values are sent separately from SQL text. Protects against **SQL injection** |
| **`ON CONFLICT DO NOTHING`** | If the row already exists, skip it |
| **Idempotent** | Running a script many times gives the same result. No duplicates |
| **Transaction / commit** | Changes are saved all together, or not at all if an error happens |

---

## Day 3 – AI Enrichment

### What I built
- `llm.py`: sends prompts to the AI (Claude API or local Ollama), switchable in `.env`
- `analysis.py`: the prompt, a fixed topic list, and Pydantic validation of AI answers
- `ai_enrich.py`: processes papers that don't have AI results yet and saves summary, topics, difficulty
- New tables `topics` and `paper_topics`, new columns in `papers`

### Concepts I learned

| Concept | Meaning |
|---|---|
| **LLM** | Large Language Model, an AI that reads and writes text (e.g. Claude) |
| **API key** | Password for a paid API. Like a credit card, so it stays secret in `.env` |
| **Prompt** | The instruction text sent to the AI |
| **Prompt engineering** | Writing clear prompts. Exact numbers ("max 60 words") work better than vague words ("short") |
| **Structured output (JSON)** | Asking the AI for JSON so Python can read the fields directly |
| **Pydantic / validation** | Automatic checks that data has the right shape and values. Bad AI answers are rejected |
| **Fixed category list** | Keeps tags consistent so analysis and charts are reliable |
| **Tokens / `max_tokens`** | Pieces of words. `max_tokens` = maximum length of the AI's answer |
| **Thinking block** | Part of the AI answer where the model reasons before giving the final text |
| **`stop_reason`** | The API tells you why it stopped (e.g. finished, or hit `max_tokens`) |
| **Rate limit** | Maximum number of requests allowed per minute. `time.sleep(1)` avoids hitting it |
| **Commit / rollback per item** | Save each paper separately; undo only the failed one |
| **Migration** | Changing the database step by step (`ALTER TABLE ... ADD COLUMN IF NOT EXISTS`) |
| **Provider abstraction** | One function `ask_llm()` hides which AI is used. Switch provider without changing code |
| **Human evaluation** | Checking AI output by reading the real paper and comparing |

---

## 🐞 Errors I Faced & How I Solved Them

| # | Day | Error | Cause | Solution | Lesson |
|---|---|---|---|---|---|
| 1 | 1 | `ensurepip ... returned non-zero exit status 1` when creating the venv | Windows Python install problem; pip couldn't be installed inside the venv | Deleted the broken folder, created the venv again (project moved to `D:\robopaper-radar`) | Setup errors are normal; read the error and fix the environment first |
| 2 | 1 | `The term '.env' is not recognized as ... cmdlet` | Pasted `.gitignore` content into the **terminal** instead of the file | Pasted the lines into the `.gitignore` file in the editor | Terminal = commands. Editor = file contents |
| 3 | 1 | Couldn't switch to the D drive in cmd | `cd D:\...` alone doesn't change drive in cmd | Type `D:` first, or `cd /d D:\folder` (PowerShell: `cd D:\folder` works) | cmd and PowerShell behave differently |
| 4 | 2 | Unsure what to choose in Stack Builder | Stack Builder offers optional extras | Cancelled it; only Server, pgAdmin, Command Line Tools are needed | Don't install what you don't need |
| 5 | 2 | Couldn't find where to create the `sql` folder | Looked in pgAdmin instead of VS Code | Created folders/files in the VS Code Explorer | pgAdmin = view the database. VS Code = project files |
| 6 | 3 | `ModuleNotFoundError: No module named 'pydantic'` | Library not installed in the venv | `pip install anthropic ollama pydantic` | "No module named X" → `pip install X` in the active venv |
| 7 | 3 | `string_too_long` validation error for `summary` | AI wrote summaries longer than 600 characters; the prompt said only "short" | Prompt: "MAXIMUM 60 words"; limit raised to 800 | Give AI exact numbers, and always validate AI output |
| 8 | 3 | `'ThinkingBlock' object has no attribute 'text'` | Code took `content[0]`, but the first block was a thinking block | Join only blocks where `block.type == "text"` | Don't trust positions like `[0]` in API data; search for what you need |
| 9 | 3 | `No JSON found in AI response` | `max_tokens=500` was too small; thinking used it up before the JSON was written | `max_tokens=2000` + check `stop_reason == "max_tokens"` + print the raw AI answer on errors | When an error is unclear, print the real data. Check why the API stopped |

---

## 🎤 Interview Stories

1. **Validation saved my data:** "My AI pipeline returned summaries that broke my length rule. Pydantic validation caught them, nothing bad was saved, and I fixed it by making the prompt more specific."
2. **Unexpected API response:** "My code assumed the first block of the AI response was text, but sometimes it was a thinking block. I changed the code to search for text blocks instead of trusting a position."
3. **Debugging a hidden cause:** "I got 'No JSON found' for some papers. The real cause was the token limit: the model's thinking used up the budget before it wrote the answer. I raised the limit, added a `stop_reason` check, and logged the raw response for future debugging."
4. **Safe re-runs:** "The pipeline is idempotent. It can run daily without duplicates, and failed papers are retried automatically without paying twice."

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