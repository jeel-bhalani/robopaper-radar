from datetime import date, datetime
from pydantic import BaseModel


class Paper(BaseModel):
    arxiv_id: str
    title: str
    authors: list[str]
    published_at: datetime | None
    url: str | None
    ai_summary: str | None
    difficulty: int | None
    topics: list[str]


class PaperDetail(Paper):
    abstract: str | None   # full abstract only in the detail view


class TopicCount(BaseModel):
    name: str
    paper_count: int


class DayCount(BaseModel):
    day: date
    paper_count: int


class AuthorCount(BaseModel):
    name: str
    paper_count: int

class NewsItem(BaseModel):
    source: str
    title: str
    url: str
    scraped_at: datetime

class QualityStats(BaseModel):
    total_papers: int
    ai_processed: int
    ai_pending: int
    short_or_missing_abstract: int
    processed_without_topics: int
    papers_without_authors: int
    newest_paper: datetime | None


class NewsStats(BaseModel):
    news_count: int
    last_news: datetime | None


class DifficultyCount(BaseModel):
    difficulty: int
    paper_count: int


class PipelineRun(BaseModel):
    id: int
    started_at: datetime
    finished_at: datetime
    status: str
    new_papers: int | None
    ai_processed: int | None
    ai_failed: int | None
    new_news: int | None
    errors: str | None


class Check(BaseModel):
    name: str
    status: str
    detail: str


class QualityReport(BaseModel):
    stats: QualityStats
    news: NewsStats
    difficulty: list[DifficultyCount]
    recent_runs: list[PipelineRun]
    checks: list[Check]