"""Module defines the tools used by the agent.

Feel free to modify or add new tools to suit your specific needs.

To learn how to create a new tool, see:
- https://docs.crewai.com/concepts/tools
"""

from __future__ import annotations

import httpx
from bs4 import BeautifulSoup
from crewai.tools import tool

# Upper bound on the page text handed to the model, which keeps its prompt small.
MAX_PAGE_CHARS = 8000
REQUEST_TIMEOUT_SECS = 30
USER_AGENT = 'Mozilla/5.0 (compatible; ScrapelyAgent/1.0)'


@tool('Scrape web page')
def scrape_page(url: str) -> str:
    """Fetch a web page by its absolute HTTP(S) URL and return its title and readable text (truncated)."""
    with httpx.Client(follow_redirects=True, timeout=REQUEST_TIMEOUT_SECS, headers={'User-Agent': USER_AGENT}) as client:
        response = client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    for element in soup(['script', 'style', 'noscript', 'svg', 'template']):
        element.decompose()
    title = soup.title.get_text(strip=True) if soup.title else ''
    text = ' '.join(soup.get_text(separator=' ').split())
    return f'Title: {title}\nURL: {response.url}\n\n{text[:MAX_PAGE_CHARS]}'
