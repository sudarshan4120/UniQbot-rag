import os
if not os.getenv('ENV_STATUS') == '1':
    import utils  # This loads vars, do not remove

import requests, os, time, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
from utils.helpers import measure_time


class NortheasternScraper:
    def __init__(self, base_url, data_dir):
        self.base_url = base_url
        self.visited_urls = set()
        self.session = requests.Session()
        self.dir = data_dir

        # Add headers to mimic a browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

    def is_valid_url(self, url):
        """Check if the URL belongs to the same domain and is a valid page"""
        parsed_base = urlparse(self.base_url)
        parsed_url = urlparse(url)

        return (parsed_url.netloc == parsed_base.netloc and
                not url.endswith(('.pdf', '.jpg', '.png', '.gif', '.doc', '.docx')) and
                '#' not in url and
                'mailto:' not in url)

    def get_page_content(self, url):
        """Fetch the content of a page"""
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

    def save_page(self, url, content):
        """Save the page content to a file"""
        # Create a valid filename from the URL
        parsed_url = urlparse(url)
        path = parsed_url.path
        if not path or path == '/':
            filename = 'index.html'
        else:
            filename = re.sub(r'[^\w\-_\. ]', '_', path.strip('/'))
            if not filename.endswith('.html'):
                filename += '.html'

        # Create directory structure
        os.makedirs(self.dir, exist_ok=True)
        filepath = os.path.join(self.dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Saved: {filepath}")
        except Exception as e:
            print(f"Error saving {filepath}: {str(e)}")

    def extract_links(self, url, content):
        """Extract all valid links from a page"""
        soup = BeautifulSoup(content, 'html.parser')
        links = set()

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(url, href)
            if self.is_valid_url(full_url):
                links.add(full_url)

        return links

    def scrape_page(self, url):
        """Scrape a single page and its links"""
        if url in self.visited_urls:
            return

        self.visited_urls.add(url)
        print(f"Scraping: {url}")

        content = self.get_page_content(url)
        if content:
            self.save_page(url, content)
            return self.extract_links(url, content)
        return set()

    def scrape_site(self, max_workers=5):
        """Scrape the entire site using multiple threads"""
        urls_to_scrape = {self.base_url}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while urls_to_scrape:
                futures = []
                for url in list(urls_to_scrape)[:max_workers]:
                    urls_to_scrape.remove(url)
                    futures.append(executor.submit(self.scrape_page, url))

                for future in futures:
                    new_urls = future.result()
                    if new_urls:
                        urls_to_scrape.update(new_urls - self.visited_urls)

                # Add a small delay to be respectful to the server
                time.sleep(1)


@measure_time
def run_scrapper():
    base_url = os.getenv('SITEMAP')
    abs_data_dir = os.path.join(os.getenv('HOME_DIR'), os.getenv('RAWDATA_DIR'))

    scraper = NortheasternScraper(base_url, abs_data_dir)
    scraper.scrape_site(max_workers=int(os.getenv('WORKERS')))
    print(f"Scraping completed. Total pages scraped: {len(scraper.visited_urls)}")


if __name__ == "__main__":
    run_scrapper()