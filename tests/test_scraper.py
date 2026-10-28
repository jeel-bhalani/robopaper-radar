from scrape_news import parse_headlines

BASE = "https://www.therobotreport.com/"

HTML = """
<article><h2 class="entry-title">
  <a href="/robot-startup-raises-funding/">Robot startup raises funding for warehouse robots</a>
</h2></article>

<article><h3>
  <a href="https://www.therobotreport.com/new-humanoid/">  New humanoid robot
     walks faster than before  </a>
</h3></article>

<article><h2><a href="/robot-startup-raises-funding/">Robot startup raises funding for warehouse robots</a></h2></article>

<article><h2><a href="/short/">Read more</a></h2></article>

<article><h2><a href="https://ads.example.com/buy">Buy this amazing product today, limited offer</a></h2></article>

<nav><a href="/about/">About The Robot Report editorial team</a></nav>
"""


def titles(articles):
    return [a["title"] for a in articles]


def test_finds_only_valid_headlines():
    assert titles(parse_headlines(HTML, BASE)) == [
        "Robot startup raises funding for warehouse robots",
        "New humanoid robot walks faster than before",
    ]


def test_relative_links_become_absolute():
    first = parse_headlines(HTML, BASE)[0]
    assert first["url"] == "https://www.therobotreport.com/robot-startup-raises-funding/"


def test_whitespace_in_titles_is_cleaned():
    assert "New humanoid robot walks faster than before" in titles(parse_headlines(HTML, BASE))


def test_duplicate_links_are_removed():
    urls = [a["url"] for a in parse_headlines(HTML, BASE)]
    assert len(urls) == len(set(urls))


def test_short_titles_are_skipped():
    assert "Read more" not in titles(parse_headlines(HTML, BASE))


def test_links_to_other_sites_are_skipped():
    assert all("ads.example.com" not in a["url"] for a in parse_headlines(HTML, BASE))


def test_links_outside_articles_are_ignored():
    assert "About The Robot Report editorial team" not in titles(parse_headlines(HTML, BASE))


def test_empty_page_returns_empty_list():
    assert parse_headlines("<html><body></body></html>", BASE) == []