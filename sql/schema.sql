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

-- Day 3: AI results
ALTER TABLE papers ADD COLUMN IF NOT EXISTS ai_summary TEXT;
ALTER TABLE papers ADD COLUMN IF NOT EXISTS difficulty INT;
ALTER TABLE papers ADD COLUMN IF NOT EXISTS ai_processed_at TIMESTAMPTZ;

CREATE TABLE IF NOT EXISTS topics (
    id   SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS paper_topics (
    paper_id INT REFERENCES papers(id) ON DELETE CASCADE,
    topic_id INT REFERENCES topics(id) ON DELETE CASCADE,
    PRIMARY KEY (paper_id, topic_id)
);