"""Scrapely Actor integration for Scrapy projects.

This module transforms a Scrapy project into a Scrapely Actor. It establishes the required environment to run
the Scrapy spider within the Scrapely platform: it points Scrapy to the project settings and runs the main Actor
coroutine on Twisted's asyncio reactor.

This file is specifically designed to be executed when the project is run as a Scrapely Actor using `scrapely run`
locally or being run on the Scrapely platform. It is not being executed when running the project as a Scrapy project
using `scrapy crawl title_spider`.

We recommend you do not modify this file unless you really know what you are doing.
"""

from __future__ import annotations

import os

# Import your main Actor coroutine here.
from .main import main
from .scrapely_integration import run_scrapy_actor

# Ensure the location to the Scrapy settings module is defined.
os.environ['SCRAPY_SETTINGS_MODULE'] = 'my_actor.settings'


if __name__ == '__main__':
    run_scrapy_actor(main())
