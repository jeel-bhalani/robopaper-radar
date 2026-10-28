from datetime import datetime, timezone


def build_checks(stats, last_run, now=None):
    """Turn database numbers into a list of ok/warning checks.

    Pure function: no database, no internet, so it's easy to test.
    """
    now = now or datetime.now(timezone.utc)
    checks = []

    def add(name, passed, detail):
        checks.append({
            "name": name,
            "status": "ok" if passed else "warning",
            "detail": detail,
        })

    total = stats["total_papers"]
    coverage = stats["ai_processed"] / total * 100 if total else 0
    add("AI coverage", total > 0 and coverage >= 95,
        f"{coverage:.0f}% of papers have AI results ({stats['ai_pending']} pending)")

    add("Topics for processed papers", stats["processed_without_topics"] == 0,
        f"{stats['processed_without_topics']} processed papers have no topics")

    add("Authors for every paper", stats["papers_without_authors"] == 0,
        f"{stats['papers_without_authors']} papers have no authors")

    add("Abstracts", stats["short_or_missing_abstract"] == 0,
        f"{stats['short_or_missing_abstract']} papers have a missing or very short abstract")

    if last_run is None:
        add("Pipeline freshness", False, "No pipeline run recorded yet")
    else:
        hours = (now - last_run["finished_at"]).total_seconds() / 3600
        add("Pipeline freshness", hours <= 26, f"Last run finished {hours:.0f} hours ago")
        add("Last run status", last_run["status"] == "success",
            f"Last run status: {last_run['status']}")

    newest = stats["newest_paper"]
    if newest is None:
        add("Newest paper", False, "No papers in the database")
    else:
        days = (now - newest).days
        add("Newest paper", days <= 4, f"Newest paper is {days} days old")

    return checks