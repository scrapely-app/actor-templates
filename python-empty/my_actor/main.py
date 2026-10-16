"""Module defines the main entry point for the Scrapely Actor.

Feel free to modify this file to suit your specific needs.

To build Scrapely Actors, utilize the Scrapely SDK toolkit, read more at the official documentation:
"""

from __future__ import annotations

from scrapely import Actor


async def main() -> None:
    """Define a main entry point for the Scrapely Actor.

    This coroutine is executed using `asyncio.run()`, so it must remain an asynchronous function for proper execution.
    Asynchronous execution is required for communication with Scrapely platform, and it also enhances performance in
    the field of web scraping significantly.
    """
    async with Actor:
        Actor.log.info('Hello from the Actor!')
        # Write your code here
