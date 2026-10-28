from psycopg.rows import dict_row
from db import get_connection

LAST_30_DAYS = "p.published_at > NOW() - INTERVAL '30 days'"


def query(cur, sql):
    cur.execute(sql)
    return cur.fetchall()


def table(headers, rows):
    """Turn rows into a Markdown table."""
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "---|" * len(headers)]
    for row in rows:
        lines.append("| " + " | ".join(str(v) for v in row) + " |")
    return "\n".join(lines)


def main():
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        overview = query(cur, """
            SELECT COUNT(*) AS papers,
                   MIN(published_at)::date AS first_day,
                   MAX(published_at)::date AS last_day,
                   ROUND(AVG(difficulty), 1) AS avg_difficulty
            FROM papers
        """)[0]

        top_topics = query(cur, f"""
            SELECT t.name, COUNT(*) AS papers,
                   ROUND(100.0 * COUNT(*) / (
                       SELECT COUNT(DISTINCT pt2.paper_id)
                       FROM paper_topics pt2
                       JOIN papers p ON p.id = pt2.paper_id
                       WHERE {LAST_30_DAYS}
                   )) AS share
            FROM topics t
            JOIN paper_topics pt ON pt.topic_id = t.id
            JOIN papers p ON p.id = pt.paper_id
            WHERE {LAST_30_DAYS}
            GROUP BY t.name
            ORDER BY papers DESC
            LIMIT 5
        """)

        hardest = query(cur, """
            SELECT t.name, ROUND(AVG(p.difficulty), 1) AS avg_difficulty, COUNT(*) AS papers
            FROM topics t
            JOIN paper_topics pt ON pt.topic_id = t.id
            JOIN papers p ON p.id = pt.paper_id
            GROUP BY t.name
            HAVING COUNT(*) >= 3
            ORDER BY avg_difficulty DESC
            LIMIT 5
        """)

        pairs = query(cur, """
            SELECT t1.name AS topic_a, t2.name AS topic_b, COUNT(*) AS papers
            FROM paper_topics a
            JOIN paper_topics b ON a.paper_id = b.paper_id AND a.topic_id < b.topic_id
            JOIN topics t1 ON t1.id = a.topic_id
            JOIN topics t2 ON t2.id = b.topic_id
            GROUP BY t1.name, t2.name
            ORDER BY papers DESC
            LIMIT 5
        """)

        weekdays = query(cur, """
            SELECT TO_CHAR(published_at, 'Dy') AS weekday,
                   EXTRACT(ISODOW FROM published_at) AS day_number,
                   COUNT(*) AS papers
            FROM papers
            GROUP BY 1, 2
            ORDER BY 2
        """)

    print("## 📊 Insights from my data\n")
    print(f"_Based on {overview['papers']} robotics papers published between "
          f"{overview['first_day']} and {overview['last_day']}. "
          f"Average AI-rated difficulty: {overview['avg_difficulty']}/5. "
          f"Generated with `src/insights.py`._\n")

    print("**Top research topics (last 30 days)**\n")
    print(table(["Topic", "Papers", "Share of papers"],
                [(r["name"], r["papers"], f"{r['share']}%") for r in top_topics]))
    print("\n_A paper can have up to 3 topics, so shares add up to more than 100%._\n")

    print("**Hardest topics (average difficulty, at least 3 papers)**\n")
    print(table(["Topic", "Avg difficulty", "Papers"],
                [(r["name"], r["avg_difficulty"], r["papers"]) for r in hardest]))

    print("\n**Topics that appear together most often**\n")
    print(table(["Topic A", "Topic B", "Papers"],
                [(r["topic_a"], r["topic_b"], r["papers"]) for r in pairs]))

    print("\n**Papers by publication weekday**\n")
    print(table(["Weekday", "Papers"],
                [(r["weekday"], r["papers"]) for r in weekdays]))


if __name__ == "__main__":
    main()