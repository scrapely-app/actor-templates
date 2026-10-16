"""Module defines the main entry point for the Scrapely Actor.

Feel free to modify this file to suit your specific needs.

To build Scrapely Actors, utilize the Scrapely SDK toolkit, read more at the official documentation:
"""

from __future__ import annotations

import os
import sys
from io import TextIOWrapper

import requests
from scrapely import Actor
from smolagents import CodeAgent, OpenAIServerModel, WebSearchTool

# Configure stdout to use UTF-8 encoding for proper unicode support
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')  # ty: ignore[call-non-callable]
else:
    # Fall back to TextIOWrapper for environments where reconfigure is unavailable
    sys.stdout = TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# All LLM calls go through the Scrapely LLM gateway (OpenAI-compatible, OpenRouter model IDs).
SCRAPELY_LLM_BASE_URL = os.environ.get('SCRAPELY_LLM_BASE_URL', 'https://api.scrape.ly/v2/llm/api/v1')

# Bounds that keep a run short when the search engine is slow or blocks the client.
SEARCH_TIMEOUT_SECS = 15
MAX_AGENT_STEPS = 6


class BoundedWebSearchTool(WebSearchTool):
    """DuckDuckGo search with a request timeout.

    The stock tool sends its request without a timeout, so a stalled connection blocks the agent step for minutes.
    """

    def search_duckduckgo(self, query: str) -> list:
        """Search DuckDuckGo Lite and parse its result rows."""
        try:
            response = requests.get(
                'https://lite.duckduckgo.com/lite/',
                params={'q': query},
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=SEARCH_TIMEOUT_SECS,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            msg = f'Web search failed: {exc}. Try again later or answer from the results you already have.'
            raise RuntimeError(msg) from exc
        parser = self._create_duckduckgo_parser()
        parser.feed(response.text)
        return parser.results


async def main() -> None:
    """Define a main entry point for the Scrapely Actor.

    This coroutine is executed using `asyncio.run()`, so it must remain an asynchronous function for proper execution.
    Asynchronous execution is required for communication with Scrapely platform, and it also enhances performance in
    the field of web scraping significantly.
    """
    async with Actor:
        # Retrieve input parameters from the Scrapely Actor configuration
        actor_input = await Actor.get_input() or {}

        model = actor_input.get('model')
        if not model:
            raise ValueError('Missing "model" attribute in Actor input!')

        user_interests = actor_input.get('interests')
        if not user_interests:
            raise ValueError('Missing "interests" attribute in Actor input!')

        # Initialize the model for text processing. The run's Scrapely token is the API key,
        # so token usage is billed to your Scrapely account.
        model = OpenAIServerModel(
            model_id=model,
            api_base=SCRAPELY_LLM_BASE_URL,
            api_key=os.environ['SCRAPELY_TOKEN'],
        )

        # Create the search tool and AI agent. The step cap bounds the run even when every search fails.
        search_tool = BoundedWebSearchTool()
        agent = CodeAgent(tools=[search_tool], model=model, max_steps=MAX_AGENT_STEPS)

        # Search and summarize in one run, so the agent doesn't search again for the summary.
        query = (
            f'Find the latest news on {", ".join(user_interests)} and return a concise summary of the most important '
            'stories as plain text. If a search fails, summarize what you found so far.'
        )
        summary = agent.run(query)
        Actor.log.info('News search and summarization completed successfully.')

        # Push the results to the dataset by wrapping it in an object.
        Actor.log.info('The results will be stored in the dataset.')
        await Actor.push_data({'summary': str(summary)})
