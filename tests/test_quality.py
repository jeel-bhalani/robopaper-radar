from datetime import datetime, timedelta, timezone

from quality import build_checks

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc)

GOOD_STATS = {
    "total_papers": 100,
    "ai_processed": 100,
    "ai_pending": 0,
    "short_or_missing_abstract": 0,
    "processed_without_topics": 0,
    "papers_without_authors": 0,
    "newest_paper": NOW - timedelta(days=1),
}
GOOD_RUN = {"finished_at": NOW - timedelta(hours=2), "status": "success"}


def statuses(checks):
    return {c["name"]: c["status"] for c in checks}


def test_everything_ok():
    result = statuses(build_checks(GOOD_STATS, GOOD_RUN, now=NOW))
    assert set(result.values()) == {"ok"}


def test_low_ai_coverage_gives_warning():
    stats = {**GOOD_STATS, "ai_processed": 80, "ai_pending": 20}
    assert statuses(build_checks(stats, GOOD_RUN, now=NOW))["AI coverage"] == "warning"


def test_empty_database_does_not_crash():
    stats = {**GOOD_STATS, "total_papers": 0, "ai_processed": 0, "newest_paper": None}
    result = statuses(build_checks(stats, None, now=NOW))
    assert result["AI coverage"] == "warning"
    assert result["Newest paper"] == "warning"


def test_old_pipeline_run_gives_warning():
    old_run = {**GOOD_RUN, "finished_at": NOW - timedelta(hours=30)}
    assert statuses(build_checks(GOOD_STATS, old_run, now=NOW))["Pipeline freshness"] == "warning"


def test_failed_run_gives_warning():
    bad_run = {**GOOD_RUN, "status": "partial"}
    assert statuses(build_checks(GOOD_STATS, bad_run, now=NOW))["Last run status"] == "warning"


def test_no_runs_gives_warning():
    assert statuses(build_checks(GOOD_STATS, None, now=NOW))["Pipeline freshness"] == "warning"


def test_paper_without_authors_gives_warning():
    stats = {**GOOD_STATS, "papers_without_authors": 3}
    assert statuses(build_checks(stats, GOOD_RUN, now=NOW))["Authors for every paper"] == "warning"