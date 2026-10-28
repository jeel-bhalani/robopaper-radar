import pytest
from fastapi.testclient import TestClient

import api

FAKE_PAPER = {
    "arxiv_id": "2610.00001v1",
    "title": "A test paper about grasping",
    "authors": ["Ada Author", "Bob Builder"],
    "published_at": "2026-10-20T10:00:00Z",
    "url": "https://arxiv.org/abs/2610.00001v1",
    "ai_summary": "A short summary.",
    "difficulty": 3,
    "topics": ["manipulation"],
    "abstract": "The full abstract text.",
}


@pytest.fixture
def db_calls():
    """Records every query the API tries to run."""
    return []


@pytest.fixture
def client(monkeypatch, db_calls):
    """API client with a FAKE database, so tests need no PostgreSQL."""
    def fake_run_query(sql, params=None):
        db_calls.append(params)
        if "WHERE p.arxiv_id" in sql:
            return [FAKE_PAPER] if params == (FAKE_PAPER["arxiv_id"],) else []
        return [FAKE_PAPER]

    monkeypatch.setattr(api, "run_query", fake_run_query)
    return TestClient(api.app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_papers(client):
    response = client.get("/papers")
    assert response.status_code == 200
    paper = response.json()[0]
    assert paper["arxiv_id"] == FAKE_PAPER["arxiv_id"]
    assert paper["topics"] == ["manipulation"]


def test_list_does_not_include_full_abstract(client):
    # The response model for the list (Paper) has no 'abstract' field
    assert "abstract" not in client.get("/papers").json()[0]


def test_paper_detail_includes_abstract(client):
    response = client.get(f"/papers/{FAKE_PAPER['arxiv_id']}")
    assert response.status_code == 200
    assert response.json()["abstract"] == "The full abstract text."


def test_unknown_paper_returns_404(client):
    response = client.get("/papers/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "Paper not found"


@pytest.mark.parametrize("query", ["limit=500", "limit=0", "difficulty=9", "offset=-1"])
def test_invalid_parameters_return_422_without_touching_db(client, db_calls, query):
    response = client.get(f"/papers?{query}")
    assert response.status_code == 422
    assert db_calls == []  # invalid requests never reach the database


def test_filters_are_sent_as_query_parameters(client, db_calls):
    client.get("/papers?search=grasp&topic=manipulation&difficulty=3")
    params = db_calls[-1]
    assert params["search"] == "grasp"
    assert params["topic"] == "manipulation"
    assert params["difficulty"] == 3