CREATE TABLE IF NOT EXISTS papers (
    id           SERIAL PRIMARY KEY,
    arxiv_id     VARCHAR(50) UNIQUE NOT NULL,
    title        TEXT NOT NULL,
    summary      TEXT,
    published_at TIMESTAMPTZ,
    url          TEXT,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS authors (
    id   SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS paper_authors (
    paper_id     INT REFERENCES papers(id) ON DELETE CASCADE,
    author_id    INT REFERENCES authors(id) ON DELETE CASCADE,
    author_order INT,
    PRIMARY KEY (paper_id, author_id)
);