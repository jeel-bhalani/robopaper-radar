from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from db import get_connection

SOURCE_NAME = "The Robot Report"
START_URL = "https://www.therobotreport.com/"

# The "address" of headlines on the page (found with Inspect in Step 2)
SELECTOR = "article h2 a, article h3 a, h2.entry-title a"

# Identify ourselves honestly
HEADERS = {
    "User-Agent": "RoboPaperRadar/0.1 (student learning project)"
}


def allowed_by_robots(url):
    """Check the site's robots.txt before scraping."""
    parts = urlparse(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    response = requests.get(robots_url, headers=HEADERS, timeout=30)
    if response.status_code == 404:
        return True  # no robots.txt = no rules
    parser = RobotFileParser()
    parser.parse(response.text.splitlines())
    return parser.can_fetch(HEADERS["User-Agent"], url)


def parse_headlines(html, base_url):
    """Pick headline links out of HTML. Pure function: no internet needed."""
    soup = BeautifulSoup(html, "html.parser")

    articles, seen = [], set()
    for link in soup.select(SELECTOR):
        title = " ".join(link.get_text().split())
        href = urljoin(base_url, link.get("href", ""))

        if len(title) < 15:
            continue
        if href in seen:
            continue
        if urlparse(href).netloc != urlparse(base_url).netloc:
            continue

        seen.add(href)
        articles.append({"title": title, "url": href})
    return articles


def scrape_headlines(url):
    """Download the page, then parse it."""
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return parse_headlines(response.text, url)


def save_articles(articles):
    new_count = 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            for a in articles:
                cur.execute(
                    """
                    INSERT INTO news_articles (source, title, url)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (url) DO NOTHING
                    RETURNING id
                    """,
                    (SOURCE_NAME, a["title"], a["url"]),
                )
                if cur.fetchone():
                    new_count += 1
    return new_count


def main():
    if not allowed_by_robots(START_URL):
        raise RuntimeError("robots.txt does not allow scraping this page")

    articles = scrape_headlines(START_URL)
    if not articles:
        raise RuntimeError("Found 0 headlines - page layout may have changed, update SELECTOR")

    for a in articles[:5]:
        print("-", a["title"])
    new_count = save_articles(articles)
    print(f"Found {len(articles)} headlines, {new_count} new")
    return new_count


if __name__ == "__main__":
    main()