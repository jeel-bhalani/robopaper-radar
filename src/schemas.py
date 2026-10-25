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