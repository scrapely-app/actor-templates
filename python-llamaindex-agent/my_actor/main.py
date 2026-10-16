"""Module defines the main entry point for the Scrapely LlamaIndex Agent.

This Agent template is intended to give example on how to use LlamaIndex Agent in Scrapely Actors.
It extracts contact details from a plain text query with a URL.

Feel free to modify this file to suit your specific needs.

To build Scrapely Actors, utilize the Scrapely SDK toolkit, read more at the official documentation:
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from scrapely import Actor
from llama_index.llms.openai_like import OpenAILike

from .agent import run_agent

if TYPE_CHECKING:
    from llama_index.core.agent import AgentOutput


async def main() -> None:
    """Define a main entry point for the Scrapely LlamaIndex Agent.

    This coroutine is executed using `asyncio.run()`, so it must remain an asynchronous function for proper execution.
    Asynchronous execution is required for communication with Scrapely platform, and it also enhances performance in
    the field of web scraping significantly.
    """
    async with Actor:
        Actor.log.info('Starting LlamaIndex Agent')
        # Charge for Actor start
        await Actor.charge('actor-start')
        Actor.log.info('Charged for Actor start')
        try:
            if not (actor_input := await Actor.get_input()):
                await Actor.fail(status_message='Actor input was not provided')
                return
            await check_inputs(actor_input)
            answer = await run_query(actor_input['query'], actor_input.get('modelName', 'openai/gpt-4o-mini'))
            await Actor.push_data({'query': actor_input['query'], 'answer': answer})
            Actor.log.info('Charging for task completed')
            await Actor.charge(event_name='task-completed', count=1)
        except Exception as e:
            await Actor.fail(status_message='Failed to process query', exception=e)


async def check_inputs(actor_input: dict) -> None:
    """Check that provided input exists.

    :raises Exception: If query is not provided
    """
    if not actor_input.get('query'):
        msg = 'Input `query` is not provided. Please verify that the `query` is correctly set.'
        await Actor.fail(status_message=msg)


async def run_query(query: str, model_name: str) -> AgentOutput | None:
    """Process query with LlamaIndex Agent."""
    # All LLM calls go through the Scrapely LLM gateway (OpenAI-compatible, OpenRouter model IDs).
    # The run's Scrapely token is the API key, so token usage is billed to your Scrapely account.
    # `OpenAILike` accepts any model name, unlike `OpenAI`, which only knows OpenAI's own model names.
    llm = OpenAILike(
        model=str(model_name),
        api_base=os.environ.get('SCRAPELY_LLM_BASE_URL', 'https://api.scrape.ly/v2/llm/api/v1'),
        api_key=os.environ['SCRAPELY_TOKEN'],
        temperature=0,
        is_chat_model=True,
        is_function_calling_model=True,
        context_window=128_000,
    )
    try:
        return await run_agent(query=query, llm=llm, verbose=True)
    except Exception as e:
        msg = f'Error running LlamaIndex Agent, error: {e}'
        await Actor.fail(status_message=msg, exception=e)
    return None
