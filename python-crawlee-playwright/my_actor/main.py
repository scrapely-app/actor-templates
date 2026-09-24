"""Module defines the main entry point for the Scrapely Actor.

Feel free to modify this file to suit your specific needs.

To build Scrapely Actors, utilize the Scrapely SDK toolkit.
"""

from __future__ import annotations

from scrapely import Actor
from crawlee.crawlers import PlaywrightCrawler

from .routes import router


async def main() -> None:
    """Define a main entry point for the Scrapely Actor.

    This coroutine is executed using `asyncio.run()`, so it must remain an asynchronous function for proper execution.
    Asynchronous execution is required for communication with the Scrapely platform, and it also enhances performance in
    the field of web scraping significantly.
    """
    # Enter the context of the Actor.
    async with Actor:
        # Retrieve the Actor input, and use default values if not provided.
        actor_input = await Actor.get_input() or {}
        start_urls = [
            url.get('url')
            for url in actor_input.get(
                'start_urls',
                [{'url': 'https://crawlee.dev'}],
            )
        ]

        # Exit if no start URLs are provided.
        if not start_urls:
            Actor.log.info('No start URLs specified in Actor input, exiting...')
            await Actor.exit()

        # Create a crawler.
        crawler = PlaywrightCrawler(
            # Limit the crawl to max requests. Remove or increase it for crawling all links.
            max_requests_per_crawl=10,
            headless=True,
            browser_launch_options={'args': ['--disable-gpu', '--no-sandbox']},
            # Set the request handler to the request router defined in routes.py.
            request_handler=router,
        )

        # Run the crawler with the starting requests.
        await crawler.run(start_urls)
