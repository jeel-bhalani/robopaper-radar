from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from psycopg.rows import dict_row
from pathlib import Path
from fastapi.staticfiles import StaticFiles

from db import get_connection
from schemas import (
    Paper, PaperDetail, TopicCount, DayCount, AuthorCount, NewsItem, QualityReport,
)
from quality import build_checks

app = FastAPI(
    title="RoboPaper Radar API",
    description="Search robotics research papers with AI summaries and topics.",
    version="0.1.0",
)

# Allow the dashboard (Day 5) to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def run_query(sql, params=None):
    """Run a SELECT and return rows as dictionaries."""
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params)
            return cur.fetchall()


# Shared SQL: one paper row + its authors + its topics as lists
PAPER_SELECT = """
    SELECT
        p.arxiv_id, p.title, p.published_at, p.url,
        p.ai_summary, p.difficulty, p.summary AS abstract,
        COALESCE((
            SELECT array_agg(a.name ORDER BY pa.author_order)
            FROM paper_authors pa
            JOIN authors a ON a.id = pa.author_id
            WHERE pa.paper_id = p.id
        ), '{}') AS authors,
        COALESCE((
            SELECT array_agg(t.name ORDER BY t.name)
            FROM paper_topics pt
            JOIN topics t ON t.id = pt.topic_id
            WHERE pt.paper_id = p.id
        ), '{}') AS topics
    FROM papers p
"""


@app.get("/health")
def health():
    run_query("SELECT 1")
    return {"status": "ok"}


@app.get("/papers", response_model=list[Paper])
def list_papers(
    search: str | None = Query(None, description="Search in title and abstract"),
    topic: str | None = Query(None, description="e.g. manipulation"),
    difficulty: int | None = Query(None, ge=1, le=5),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    sql = PAPER_SELECT + """
        WHERE (%(search)s::text IS NULL
               OR p.title ILIKE '%%' || %(search)s || '%%'
               OR p.summary ILIKE '%%' || %(search)s || '%%')
          AND (%(topic)s::text IS NULL OR EXISTS (
                SELECT 1 FROM paper_topics pt
                JOIN topics t ON t.id = pt.topic_id
                WHERE pt.paper_id = p.id AND t.name = %(topic)s))
          AND (%(difficulty)s::int IS NULL OR p.difficulty = %(difficulty)s)
        ORDER BY p.published_at DESC
        LIMIT %(limit)s OFFSET %(offset)s
    """
    params = {"search": search, "topic": topic, "difficulty": difficulty,
              "limit": limit, "offset": offset}
    return run_query(sql, params)


@app.get("/papers/{arxiv_id}", response_model=PaperDetail)
def get_paper(arxiv_id: str):
    rows = run_query(PAPER_SELECT + "WHERE p.arxiv_id = %s", (arxiv_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Paper not found")
    return rows[0]


@app.get("/topics", response_model=list[TopicCount])
def list_topics():
    return run_query("""
        SELECT t.name, COUNT(*) AS paper_count
        FROM topics t
        JOIN paper_topics pt ON pt.topic_id = t.id
        GROUP BY t.name
        ORDER BY paper_count DESC
    """)


@app.get("/stats/papers-per-day", response_model=list[DayCount])
def papers_per_day():
    return run_query("""
        SELECT DATE(published_at) AS day, COUNT(*) AS paper_count
        FROM papers
        GROUP BY day
        ORDER BY day
    """)


@app.get("/authors/top", response_model=list[AuthorCount])
def top_authors(limit: int = Query(10, ge=1, le=50)):
    return run_query("""
        SELECT a.name, COUNT(*) AS paper_count
        FROM authors a
        JOIN paper_authors pa ON pa.author_id = a.id
        GROUP BY a.name
        ORDER BY paper_count DESC
        LIMIT %s
    """, (limit,))

@app.get("/news", response_model=list[NewsItem])
def list_news(limit: int = Query(10, ge=1, le=50)):
    return run_query("""
        SELECT source, title, url, scraped_at
        FROM news_articles
        ORDER BY scraped_at DESC, id
        LIMIT %s
    """, (limit,))


QUALITY_STATS_SQL = """
    SELECT
        COUNT(*) AS total_papers,
        COUNT(*) FILTER (WHERE ai_processed_at IS NOT NULL) AS ai_processed,
        COUNT(*) FILTER (WHERE ai_processed_at IS NULL) AS ai_pending,
        COUNT(*) FILTER (WHERE summary IS NULL OR LENGTH(summary) < 100)
            AS short_or_missing_abstract,
        COUNT(*) FILTER (
            WHERE ai_processed_at IS NOT NULL
              AND NOT EXISTS (SELECT 1 FROM paper_topics pt WHERE pt.paper_id = papers.id)
        ) AS processed_without_topics,
        COUNT(*) FILTER (
            WHERE NOT EXISTS (SELECT 1 FROM paper_authors pa WHERE pa.paper_id = papers.id)
        ) AS papers_without_authors,
        MAX(published_at) AS newest_paper
    FROM papers
"""


@app.get("/quality", response_model=QualityReport)
def quality_report():
    stats = run_query(QUALITY_STATS_SQL)[0]
    news = run_query("""
        SELECT COUNT(*) AS news_count, MAX(scraped_at) AS last_news
        FROM news_articles
    """)[0]
    difficulty = run_query("""
        SELECT difficulty, COUNT(*) AS paper_count
        FROM papers
        WHERE difficulty IS NOT NULL
        GROUP BY difficulty
        ORDER BY difficulty
    """)
    runs = run_query("""
        SELECT id, started_at, finished_at, status, new_papers,
               ai_processed, ai_failed, new_news, errors
        FROM pipeline_runs
        ORDER BY id DESC
        LIMIT 10
    """)
    checks = build_checks(stats, runs[0] if runs else None)
    return {
        "stats": stats,
        "news": news,
        "difficulty": difficulty,
        "recent_runs": runs,
        "checks": checks,
    }
# Serve the dashboard (must be the LAST line, after all API routes)
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

