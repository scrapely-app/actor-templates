"""Module defines the tools used by the agent.

Feel free to modify or add new tools to suit your specific needs.

To learn how to create a new tool, see:
- https://python.langchain.com/docs/concepts/tools/
- https://python.langchain.com/docs/how_to/#tools
"""

from __future__ import annotations

import httpx
from bs4 import BeautifulSoup
from langchain_core.tools import tool

# Upper bound on the page text handed to the model, which keeps its prompt small.
MAX_PAGE_CHARS = 8000
REQUEST_TIMEOUT_SECS = 30
USER_AGENT = 'Mozilla/5.0 (compatible; ScrapelyAgent/1.0)'


@tool
async def tool_scrape_page(url: str) -> str:
    """Tool to fetch a web page and return its title and readable text.

    Args:
        url (str): Absolute HTTP(S) URL of the page to fetch.

    Returns:
        str: Page title, final URL, and the visible text of the page (truncated).
    """
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=REQUEST_TIMEOUT_SECS,
        headers={'User-Agent': USER_AGENT},
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    for element in soup(['script', 'style', 'noscript', 'svg', 'template']):
        element.decompose()
    title = soup.title.get_text(strip=True) if soup.title else ''
    text = ' '.join(soup.get_text(separator=' ').split())
    return f'Title: {title}\nURL: {response.url}\n\n{text[:MAX_PAGE_CHARS]}'
