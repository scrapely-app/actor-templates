"""Module defines the main entry point for the Scrapely Actor.

Feel free to modify this file to suit your specific needs.

To build Scrapely Actors, use the Scrapely SDK toolkit, read more at the official documentation:
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

# On first run in a fresh container, crewAI prompts "Would you like to view your
# execution traces?" and waits up to 20 s for stdin input that never comes.
# There is no dedicated "non-interactive" env var in crewAI; CREWAI_TESTING=true
# is the only flag that suppresses this prompt (it is checked first in
# should_auto_collect_first_time_traces() and prompt_user_for_trace_viewing()).
# setdefault is used so an explicit override in the environment is still respected.
# See: https://github.com/crewAIInc/crewAI/issues/3789
os.environ.setdefault('CREWAI_TESTING', 'true')

from scrapely import Actor
from crewai import LLM, Agent, Crew, Task

from .tools import scrape_page

if TYPE_CHECKING:
    from crewai.tools import BaseTool


async def main() -> None:
    """Define a main entry point for the Scrapely Actor.

    This coroutine is executed using `asyncio.run()`, so it must remain an asynchronous function for proper execution.
    Asynchronous execution is required for communication with the Scrapely platform, and it also enhances performance in
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
            raise ValueError('Missing "query" attribute in input!')

        model_name = actor_input.get('modelName', 'openai/gpt-4o-mini')

        # All LLM calls go through the Scrapely LLM gateway (OpenAI-compatible, OpenRouter model IDs).
        # The run's Scrapely token is the API key, so token usage is billed to your Scrapely account.
        # CrewAI reads the first `openai/` as the provider and sends the rest as the model name,
        # so the OpenRouter ID `openai/gpt-4o-mini` becomes `openai/openai/gpt-4o-mini` here.
        llm = LLM(
            model=f'openai/{model_name}',
            base_url=os.environ.get('SCRAPELY_LLM_BASE_URL', 'https://api.scrape.ly/v2/llm/api/v1'),
            api_key=os.environ['SCRAPELY_TOKEN'],
        )

        # Create a toolkit for the agent
        # containing the web page scraper tool
        tools: list[BaseTool] = [scrape_page]

        # Create an agent
        # For more information, see https://docs.crewai.com/concepts/agents
        agent = Agent(
            role='Web Research Expert',
            goal='Research topics and websites and provide accurate, well-sourced insights.',
            backstory=(
                'I am an expert web researcher. I read web pages with my scraping tool, '
                'extract the facts that matter, and summarize them clearly, citing the pages I used.'
            ),
            tools=tools,
            verbose=True,
            llm=llm,
        )

        # Create a task assigned to the agent
        # For more information, see https://docs.crewai.com/concepts/tasks
        task = Task(
            description=query,
            expected_output='A helpful response to the user query.',
            agent=agent,
        )

        # Create a one-man crew
        # For more information, see https://docs.crewai.com/concepts/crews
        crew = Crew(agents=[agent], tasks=[task])

        # Kick off the crew and get the response
        # Use kickoff_async() to avoid blocking the event loop in async context
        crew_output = await crew.kickoff_async()
        raw_response = crew_output.raw

        # Log total token usage
        Actor.log.info('Total tokens used by the model: %s', crew_output.token_usage.total_tokens)

        # Charge for task completion
        await Actor.charge('task-completed')

        # Push results to the dataset
        await Actor.push_data(
            {
                'query': query,
                'response': raw_response,
            }
        )
        Actor.log.info('Pushed the data into the dataset!')
