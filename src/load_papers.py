from db import get_connection
from fetch_arxiv import fetch_papers


def save_paper(cur, paper):
    """Insert one paper and its authors. Returns True if the paper was new."""
    cur.execute(
        """
        INSERT INTO papers (arxiv_id, title, summary, published_at, url)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (arxiv_id) DO NOTHING
        RETURNING id
        """,
        (paper["arxiv_id"], paper["title"], paper["summary"],
         paper["published"], paper["url"]),
    )
    row = cur.fetchone()
    if row is None:          # paper already in database, so skip it
        return False
    paper_id = row[0]

    for order, name in enumerate(paper["authors"], start=1):
        cur.execute(
            """
            INSERT INTO authors (name) VALUES (%s)
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
            """,
            (name,),
        )
        author_id = cur.fetchone()[0]
        cur.execute(
            """
            INSERT INTO paper_authors (paper_id, author_id, author_order)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (paper_id, author_id, order),
        )
    return True


def main(max_results=100):
    papers = fetch_papers(max_results=max_results)
    new_count = 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            for paper in papers:
                if save_paper(cur, paper):
                    new_count += 1
    print(f"Fetched {len(papers)} papers, {new_count} new, "
          f"{len(papers) - new_count} already in database")
    return new_count


if __name__ == "__main__":
    main()