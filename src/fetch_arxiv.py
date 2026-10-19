import csv
import os
import requests
import feedparser

ARXIV_URL = "https://export.arxiv.org/api/query"


def fetch_papers(category="cs.RO", max_results=20):
    """Ask the arXiv API for the newest papers in a category."""
    params = {
        "search_query": f"cat:{category}",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results,
    }
    response = requests.get(ARXIV_URL, params=params, timeout=30)
    response.raise_for_status()  # stop with an error if the request failed

    feed = feedparser.parse(response.text)  # turn XML into Python objects

    papers = []
    for entry in feed.entries:
        papers.append({
            "arxiv_id": entry.id.split("/abs/")[-1],
            "title": " ".join(entry.title.split()),      # remove extra spaces/newlines
            "authors": ", ".join(a.name for a in entry.authors),
            "published": entry.published,
            "summary": " ".join(entry.summary.split()),
            "url": entry.link,
        })
    return papers


def save_to_csv(papers, path="data/papers.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=papers[0].keys())
        writer.writeheader()
        writer.writerows(papers)
    print(f"Saved {len(papers)} papers to {path}")


if __name__ == "__main__":
    papers = fetch_papers()
    for p in papers[:3]:
        print(p["title"], "|", p["published"])
    save_to_csv(papers)