from __future__ import annotations

import logging
import re
from collections import deque
from typing import TYPE_CHECKING
from urllib.parse import urldefrag, urljoin, urlsplit

import httpx
import polars as pl
from bs4 import BeautifulSoup
from llama_index.core.prompts import PromptTemplate

if TYPE_CHECKING:
    from llama_index.core.llms import LLM

REQUEST_TIMEOUT_SECS = 30
USER_AGENT = 'Mozilla/5.0 (compatible; ScrapelyAgent/1.0)'
# Fields that differ between pages even when the contact details are the same; ignored by deduplication.
PAGE_FIELDS = {'url', 'depth', 'originalStartUrl', 'referrerUrl'}

EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
# International phone numbers written with a leading `+`, e.g. "+1 (555) 123-4567".
PHONE_RE = re.compile(r'\+\d[\d\s().-]{7,}\d')
# Image file names like "logo@2x.png" look like emails; skip them.
NOT_EMAIL_SUFFIXES = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')
SOCIAL_PATTERNS = {
    'linkedIns': re.compile(r'^https?://([a-z]+\.)?linkedin\.com/(in|company|school)/[^/?#]+', re.IGNORECASE),
    'twitters': re.compile(r'^https?://(www\.)?(twitter|x)\.com/[A-Za-z0-9_]+/?$', re.IGNORECASE),
    'facebooks': re.compile(r'^https?://([a-z]+\.)?facebook\.com/[^/?#]+', re.IGNORECASE),
    'instagrams': re.compile(r'^https?://(www\.)?instagram\.com/[^/?#]+', re.IGNORECASE),
    'youtubes': re.compile(r'^https?://(www\.)?youtube\.com/(@|c/|channel/|user/)[^/?#]+', re.IGNORECASE),
    'githubs': re.compile(r'^https?://(www\.)?github\.com/[^/?#]+/?$', re.IGNORECASE),
    'tiktoks': re.compile(r'^https?://(www\.)?tiktok\.com/@[^/?#]+', re.IGNORECASE),
    'discords': re.compile(r'^https?://(www\.)?(discord\.gg|discord\.com/invite)/[^/?#]+', re.IGNORECASE),
}

PROMPT_SUMMARIZE = PromptTemplate(
    'Scraped contact data is below.\n'
    '---------------------\n'
    '{scraped_data}\n'
    '---------------------\n'
    'Given the scraped contact information and no prior knowledge, '
    'summarize contact information in a concise and informative manner.\n'
    'Summary of contact details:'
)

logger = logging.getLogger('scrapely')


class LLMRegistry:
    """Registry for the LLM instance to be used by the tools."""

    _llm: LLM | None = None

    @classmethod
    def get(cls) -> LLM:
        """Get the LLM instance to be used by the tools."""
        if cls._llm is None:
            raise ValueError('LLM instance has not been set.')
        return cls._llm

    @classmethod
    def set(cls, new_llm: LLM) -> None:
        """Set the LLM instance to be used by the tools."""
        cls._llm = new_llm


def extract_contacts(html: str, page_url: str) -> tuple[dict[str, list[str]], list[str]]:
    """Extract emails, phone numbers and social profile links from a page, plus the page's absolute links."""
    soup = BeautifulSoup(html, 'html.parser')
    hrefs = [urldefrag(urljoin(page_url, a['href'])).url for a in soup.find_all('a', href=True)]

    emails = {m.lower() for m in EMAIL_RE.findall(soup.get_text(' '))}
    emails |= {h.removeprefix('mailto:').split('?')[0].lower() for h in hrefs if h.startswith('mailto:')}
    phones = {' '.join(m.split()) for m in PHONE_RE.findall(soup.get_text(' '))}
    phones |= {h.removeprefix('tel:').strip() for h in hrefs if h.startswith('tel:')}

    contacts: dict[str, list[str]] = {
        'emails': sorted(e for e in emails if e and not e.endswith(NOT_EMAIL_SUFFIXES)),
        'phones': sorted(p for p in phones if p),
    }
    for field, pattern in SOCIAL_PATTERNS.items():
        contacts[field] = sorted({h.rstrip('/') for h in hrefs if pattern.match(h)})

    return contacts, [h for h in hrefs if h.startswith(('http://', 'https://'))]


async def call_contact_details_scraper(
    start_urls: list[str],
    max_requests_per_start_url: int = 5,
    max_depth: int = 1,
    *,
    same_domain: bool = True,
    deduplicate: bool = True,
) -> list[dict]:
    """Extract contact details from websites.

    The Contact Details Scraper crawls the given websites and extracts contact information,
    including emails, phone numbers, and social media profiles (LinkedIn, X/Twitter, Facebook,
    Instagram, YouTube, GitHub, TikTok, Discord).

    The scraper retrieves contact details for every URL it visits, with crawling behavior controlled by
    the max_depth and max_requests_per_start_url parameters.

    Since the scraper often produces a list of URLs with duplicate contact details, it is recommended to
    deduplicate the results.

    Args:
        start_urls: List of URLs to be scraped, for example: ["https://crawlee.dev"]
        max_requests_per_start_url: The maximum number of pages that will be visited for each start URL you provide.
        max_depth: Maximum link depth (0 = only the start URL).
        same_domain: If set, the scraper will only follow links within the same domain as the start URL.
        deduplicate: If set, this function will deduplicate the results.

    Returns:
        List of extracted details

        Sample output:
        [
            {
               "url": "https://crawlee.dev/",
               "domain": "crawlee.dev",
               "emails": [],
               "phones": [],
               "githubs": [ "https://github.com/example-org" ],
               "twitters": [ "https://x.com/example" ],
            },
            {
               "url": "https://crawlee.dev/python",
               "domain": "crawlee.dev",
            }
        ]
    """
    data: list[dict] = []
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=REQUEST_TIMEOUT_SECS,
        headers={'User-Agent': USER_AGENT},
    ) as client:
        for start_url in start_urls:
            start_domain = urlsplit(start_url).hostname or ''
            queue: deque[tuple[str, int, str | None]] = deque([(start_url, 0, None)])
            seen = {start_url}
            requests_done = 0
            while queue and requests_done < max_requests_per_start_url:
                url, depth, referrer = queue.popleft()
                requests_done += 1
                try:
                    response = await client.get(url)
                    response.raise_for_status()
                except httpx.HTTPError as e:
                    logger.warning('Failed to fetch %s: %s', url, e)
                    continue
                if 'html' not in response.headers.get('content-type', ''):
                    continue

                contacts, links = extract_contacts(response.text, str(response.url))
                data.append(
                    {
                        'url': str(response.url),
                        'domain': response.url.host,
                        'depth': depth,
                        'originalStartUrl': start_url,
                        'referrerUrl': referrer,
                        **contacts,
                    }
                )

                if depth >= max_depth:
                    continue
                for link in links:
                    if link in seen or (same_domain and urlsplit(link).hostname != start_domain):
                        continue
                    seen.add(link)
                    queue.append((link, depth + 1, url))

    logger.info('Scraped contact details, number of records: %d', len(data))

    if deduplicate and data:
        logger.info('Deduplicating contact information')
        df_data = pl.from_records(data)
        columns = sorted(set(df_data.columns) - PAGE_FIELDS)
        data = df_data.unique(subset=columns, maintain_order=True).to_dicts()

    # Drop empty fields so the LLM sees only what was found.
    return [{k: v for k, v in item.items() if v not in (None, [])} for item in data]


async def summarize_contact_information(contact_information: list[dict]) -> str:
    """Summarize list of scraped contacts from the Contact Details Scraper.

    Args:
        contact_information (list[dict]): List of contact information obtained from the Contact Details Scraper.
        Sample input:
        [
            {
               "url": "https://crawlee.dev/",
               "domain": "crawlee.dev",
               "githubs": [ "https://github.com/example-org" ],
               "twitters": [ "https://x.com/example" ],
            },
            {
               "url": "https://crawlee.dev/python",
               "domain": "crawlee.dev",
            }
        ]

    Returns:
        response (str): Summarized data.
    """
    llm = LLMRegistry.get()
    logger.info('Summarizing contact information')
    return str(await llm.apredict(PROMPT_SUMMARIZE, scraped_data=contact_information))
