import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import ai_enrich
import load_papers
import scrape_news
from db import get_connection


# ---------- Logging setup ----------
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8"),  # to file
        logging.StreamHandler(),                                         # to screen
    ],
)
log = logging.getLogger("pipeline")

AI_LIMIT = int(os.getenv("AI_LIMIT", "100"))  # max AI calls per run (cost control)


def run_step(name, func, errors):
    """Run one step. If it fails, log it and continue with the next step."""
    log.info(f"START  {name}")
    start = time.time()
    try:
        result = func()
        log.info(f"DONE   {name} in {time.time() - start:.1f}s -> {result}")
        return result
    except Exception as error:
        log.exception(f"FAILED {name}")  # writes the full error traceback to the log
        errors.append(f"{name}: {error}")
        return None


def save_run(started_at, status, new_papers, ai_ok, ai_failed, new_news, errors):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO pipeline_runs
                (started_at, finished_at, status, new_papers,
                 ai_processed, ai_failed, new_news, errors)
            VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s)
            """,
            (started_at, status, new_papers, ai_ok, ai_failed, new_news,
             "\n".join(errors) or None),
        )


def main():
    started_at = datetime.now(timezone.utc)
    errors = []
    log.info("=" * 50)
    log.info("Pipeline started")

    new_papers = run_step("Fetch papers", load_papers.main, errors)
    ai_result = run_step("AI enrichment", lambda: ai_enrich.main(AI_LIMIT), errors)
    new_news = run_step("Scrape news", scrape_news.main, errors)

    ai_ok, ai_failed = ai_result if ai_result else (None, None)

    if not errors:
        status = "success"
    elif len(errors) == 3:
        status = "failed"
    else:
        status = "partial"

    summary = (f"Status: {status} | new papers: {new_papers} | "
               f"AI ok/failed: {ai_ok}/{ai_failed} | new news: {new_news}")

    

    try:
        save_run(started_at, status, new_papers, ai_ok, ai_failed, new_news, errors)
    except Exception:
        log.exception("Could not save run record")

    log.info(summary)
    log.info("Pipeline finished")
    sys.exit(1 if status == "failed" else 0)


if __name__ == "__main__":
    main()