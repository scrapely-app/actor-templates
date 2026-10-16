"""Minimal integration of Scrapy with the Scrapely platform.

This module provides everything needed to run a Scrapy spider as a Scrapely Actor:

- `run_scrapy_actor` configures Scrapy logging and runs the Actor coroutine on Twisted's asyncio reactor, so Scrapy
  and the Scrapely SDK share the same asyncio event loop.
- `get_scrapy_settings` loads the Scrapy project settings and enables the Scrapely components below.
- `ScrapelyPushDataPipeline` stores every scraped item in the Actor's default dataset using `Actor.push_data`.
- `ScrapelyProxyMiddleware` routes requests through the proxy configured in the Actor input
  (`Actor.create_proxy_configuration`), by setting `request.meta['proxy']` for Scrapy's `HttpProxyMiddleware`.

We recommend you do not modify this file unless you really know what you are doing.
"""
# ruff: noqa: ARG002

from __future__ import annotations

import asyncio
import logging
import sys
from typing import TYPE_CHECKING, Any

from itemadapter import ItemAdapter
from scrapely import Actor
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from scrapy.utils.reactor import install_reactor

if TYPE_CHECKING:
    from collections.abc import Coroutine

    from scrapely.proxy_configuration import ProxyConfiguration
    from scrapy import Request, Spider
    from scrapy.crawler import Crawler
    from scrapy.settings import Settings

ASYNCIO_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

logger = logging.getLogger(__name__)


def run_scrapy_actor(coro: Coroutine[Any, Any, Any]) -> None:
    """Run the Actor coroutine on the Twisted asyncio reactor and exit with a non-zero code on failure."""
    # Show Scrapy and spider logs, using LOG_LEVEL and the other LOG_* options from the project settings.
    configure_logging(get_project_settings())
    install_reactor(ASYNCIO_REACTOR)

    from twisted.internet import reactor  # noqa: PLC0415 - must be imported after the reactor is installed
    from twisted.internet.defer import Deferred  # noqa: PLC0415

    # `install_reactor` creates the asyncio event loop used by the reactor and sets it as the current one.
    task = asyncio.get_event_loop().create_task(coro)
    Deferred.fromFuture(task).addBoth(lambda _: reactor.stop())  # type: ignore[attr-defined]
    reactor.run()  # type: ignore[attr-defined]

    if not task.done():
        # The reactor was stopped from outside (e.g. Ctrl+C) before the Actor finished.
        sys.exit(1)
    if task.cancelled() or task.exception() is not None:
        if not task.cancelled():
            logger.error('Actor failed', exc_info=task.exception())
        sys.exit(1)


def get_scrapy_settings(proxy_input: dict[str, Any] | None = None) -> Settings:
    """Load the Scrapy project settings and enable the Scrapely components.

    Args:
        proxy_input: The proxy configuration from the Actor input (the `proxy` editor value), if any.
    """
    settings = get_project_settings()

    # Scrapely components rely on asyncio, so the asyncio reactor is required.
    settings['TWISTED_REACTOR'] = ASYNCIO_REACTOR

    # Push scraped items to the default dataset. Runs last, after all project pipelines.
    item_pipelines = settings.getdict('ITEM_PIPELINES')
    item_pipelines[f'{__name__}.ScrapelyPushDataPipeline'] = 1000
    settings['ITEM_PIPELINES'] = item_pipelines

    if proxy_input:
        # Must run before Scrapy's HttpProxyMiddleware (priority 750), which turns the proxy URL
        # credentials into the Proxy-Authorization header.
        downloader_middlewares = settings.getdict('DOWNLOADER_MIDDLEWARES')
        downloader_middlewares[f'{__name__}.ScrapelyProxyMiddleware'] = 740
        settings['DOWNLOADER_MIDDLEWARES'] = downloader_middlewares
        settings['SCRAPELY_PROXY_INPUT'] = proxy_input

    return settings


class ScrapelyPushDataPipeline:
    """Item pipeline that pushes every scraped item to the Actor's default dataset."""

    async def process_item(self, item: Any, spider: Spider | None = None) -> Any:
        await Actor.push_data(ItemAdapter(item).asdict())
        return item


class ScrapelyProxyMiddleware:
    """Downloader middleware that sets a proxy from the Actor input proxy configuration on each request."""

    def __init__(self, proxy_input: dict[str, Any]) -> None:
        self._proxy_input = proxy_input
        self._proxy_configuration: ProxyConfiguration | None = None
        self._initialized = False
        self._lock = asyncio.Lock()

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> ScrapelyProxyMiddleware:
        return cls(crawler.settings.getdict('SCRAPELY_PROXY_INPUT'))

    async def process_request(self, request: Request, spider: Spider | None = None) -> None:
        # Respect proxies set explicitly by the spider.
        if 'proxy' in request.meta:
            return

        async with self._lock:
            if not self._initialized:
                self._proxy_configuration = await Actor.create_proxy_configuration(
                    actor_proxy_input=self._proxy_input,
                )
                self._initialized = True

        if self._proxy_configuration is not None:
            request.meta['proxy'] = await self._proxy_configuration.new_url()
