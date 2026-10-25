import sys
import time
from db import get_connection
from llm import ask_llm, PROVIDER
from analysis import build_prompt, parse_response


def get_unprocessed_papers(cur, limit):
    cur.execute(
        """
        SELECT id, title, summary FROM papers
        WHERE ai_processed_at IS NULL
        ORDER BY published_at DESC
        LIMIT %s
        """,
        (limit,),
    )
    return cur.fetchall()


def save_analysis(cur, paper_id, analysis):
    cur.execute(
        """
        UPDATE papers
        SET ai_summary = %s, difficulty = %s, ai_processed_at = NOW()
        WHERE id = %s
        """,
        (analysis.summary, analysis.difficulty, paper_id),
    )
    for topic in analysis.topics:
        cur.execute(
            """
            INSERT INTO topics (name) VALUES (%s)
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
            """,
            (topic,),
        )
        topic_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO paper_topics (paper_id, topic_id) VALUES (%s, %s) "
            "ON CONFLICT DO NOTHING",
            (paper_id, topic_id),
        )


def main(limit):
    ok, failed = 0, 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            papers = get_unprocessed_papers(cur, limit)
            print(f"Using {PROVIDER}. Papers to process: {len(papers)}\n")

            for paper_id, title, abstract in papers:
                answer = None  # reset for each paper
                try:
                    answer = ask_llm(build_prompt(title, abstract))
                    analysis = parse_response(answer)
                    save_analysis(cur, paper_id, analysis)
                    conn.commit()  # save each paper right away
                    ok += 1
                    print(f"✅ {title[:60]}")
                    print(f"   {analysis.topics} | difficulty {analysis.difficulty}")
                except Exception as error:
                    conn.rollback()  # undo only this paper
                    failed += 1
                    print(f"❌ {title[:60]}\n   Reason: {error}")
                    if answer is not None:
                        print(f"   AI answered: {answer[:300]!r}")
                time.sleep(1)  # be polite to the API (rate limits)

    print(f"\nDone: {ok} processed, {failed} failed (will retry next run)")
    return ok, failed


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    main(limit)