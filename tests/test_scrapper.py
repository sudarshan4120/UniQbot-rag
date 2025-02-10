from scrapper.ogs_html import NortheasternScraper

import pytest
from unittest.mock import Mock, patch

base_url = "https://www.google.com/"

@pytest.fixture
def scraper():
    global base_url
    return NortheasternScraper(base_url, "./test_data/")


def test_valid_urls(scraper):
    global base_url
    # Test internal URLs
    assert scraper.is_valid_url(base_url)

    # Test invalid URLs
    assert not scraper.is_valid_url("https://other-site.com")
    assert not scraper.is_valid_url("https://www.google.com/doc.pdf")
    assert not scraper.is_valid_url("mailto:test@example.com")


def test_get_page_content_real(scraper):
    content = scraper.get_page_content("http://quotes.toscrape.com")
    assert content is not None
    assert "<html" in content


def test_extract_links(scraper):
    html_content = """
    <html>
        <body>
            <a href="/page1">Page 1</a>
            <a href="https://www.google.com/page2">Page 2</a>
            <a href="https://other-site.com">External Link</a>
        </body>
    </html>
    """

    links = scraper.extract_links("https://www.google.com", html_content)
    expected_links = {
        "https://www.google.com/page1",
        "https://www.google.com/page2"
    }
    assert links == expected_links
