"""Module defines the main entry point for the Scrapely Actor.

Module defines the main coroutine for the Scrapely Scrapy Actor, executed from the __main__.py file. The coroutine
processes the Actor's input and executes the Scrapy spider. Additionally, it updates Scrapy project settings by
applying Scrapely-related settings, which add an item pipeline for pushing data to the Actor's default dataset
and, when configured in the input, a downloader middleware that routes requests through a proxy.

Customization:
--------------

Feel free to customize this file to add specific functionality to the Actor, such as incorporating your own Scrapy
components like spiders and handling Actor input. However, make sure you have a clear understanding of your
modifications. For instance, removing `get_scrapy_settings` breaks the integration between Scrapy and Scrapely.
The integration itself lives in `scrapely_integration.py`.
"""

from __future__ import annotations

from scrapely import Actor
from scrapy.crawler import AsyncCrawlerRunner

from .scrapely_integration import get_scrapy_settings

# Import your Scrapy spider here.
from .spiders import TitleSpider as Spider


async def main() -> None:
    """Scrapely Actor main coroutine for executing the Scrapy spider."""
    async with Actor:
        # Retrieve and process Actor input.
        actor_input = await Actor.get_input() or {}
        start_urls = [url['url'] for url in actor_input.get('startUrls', []) if url.get('url')]
        allowed_domains = actor_input.get('allowedDomains')
        proxy_config = actor_input.get('proxyConfiguration')

        # Load the Scrapy project settings extended with the Scrapely components.
        settings = get_scrapy_settings(proxy_input=proxy_config)

        # Create AsyncCrawlerRunner and execute the Scrapy spider.
        crawler_runner = AsyncCrawlerRunner(settings)
        await crawler_runner.crawl(
            Spider,
            start_urls=start_urls,
            allowed_domains=allowed_domains,
        )
