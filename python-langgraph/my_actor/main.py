"""Module defines the main entry point for the Scrapely Actor.

Feel free to modify this file to suit your specific needs.

To build Scrapely Actors, use the Scrapely SDK toolkit, read more at the official documentation:
"""

from __future__ import annotations

import logging
import os

from scrapely import Actor
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from .models import AgentStructuredOutput
from .tools import tool_scrape_page
from .utils import log_state


async def main() -> None:
    """Define a main entry point for the Scrapely Actor.

    This coroutine is executed using `asyncio.run()`, so it must remain an asynchronous function for proper execution.
    Asynchronous execution is required for communication with Scrapely platform, and it also enhances performance in
    the field of web scraping significantly.

    Raises:
        ValueError: If the input is missing required attributes.
    """
    async with Actor:
        # Charge for Actor start
        await Actor.charge('actor-start')

        # Handle input
        actor_input = await Actor.get_input()

        query = actor_input.get('query')
        if not query:
            msg = 'Missing "query" attribute in input!'
            raise ValueError(msg)

        model_name = actor_input.get('modelName', 'openai/gpt-4o-mini')
        if actor_input.get('debug', False):
            Actor.log.setLevel(logging.DEBUG)

        # All LLM calls go through the Scrapely LLM gateway (OpenAI-compatible, OpenRouter model IDs).
        # The run's Scrapely token is the API key, so token usage is billed to your Scrapely account.
        llm = ChatOpenAI(
            model=model_name,
            base_url=os.environ.get('SCRAPELY_LLM_BASE_URL', 'https://api.scrape.ly/v2/llm/api/v1'),
            api_key=os.environ['SCRAPELY_TOKEN'],
        )

        # Create the agent graph
        # see https://docs.langchain.com/oss/python/langchain/agents
        tools = [tool_scrape_page]
        graph = create_agent(llm, tools, response_format=AgentStructuredOutput)

        inputs: dict = {'messages': [('user', query)]}
        response: AgentStructuredOutput | None = None
        last_message: str | None = None
        async for state in graph.astream(inputs, stream_mode='values'):
            log_state(state)
            if state.get('structured_response'):
                response = state['structured_response']
                last_message = state['messages'][-1].content
                break

        if not response or not last_message:
            Actor.log.error('Failed to get a response from the agent!')
            await Actor.fail(status_message='Failed to get a response from the agent!')
            return

        # Charge for task completion
        await Actor.charge('task-completed')

        # Push results to the key-value store and dataset
        store = await Actor.open_key_value_store()
        await store.set_value('response.txt', last_message)
        Actor.log.info('Saved the "response.txt" file into the key-value store!')

        await Actor.push_data(
            {
                'response': last_message,
                'structured_response': response.model_dump(),
            }
        )
        Actor.log.info('Pushed data into the dataset!')
