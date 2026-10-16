import os
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

# Route all LLM calls through the Scrapely LLM gateway (OpenRouter-compatible),
# billed against the run's Scrapely account, so no provider API key is needed.
# The gateway authenticates via `Authorization: Bearer $SCRAPELY_TOKEN`, which
# is what the OpenAI client sends when api_key=SCRAPELY_TOKEN. The platform
# injects SCRAPELY_LLM_BASE_URL into every run.
OPENROUTER_BASE_URL = os.environ.get('SCRAPELY_LLM_BASE_URL', 'https://api.scrape.ly/v2/llm/api/v1')


def _build_provider() -> OpenAIProvider:
    return OpenAIProvider(base_url=OPENROUTER_BASE_URL, api_key=os.environ['SCRAPELY_TOKEN'])


@dataclass
class Deps:
    """Dependencies."""

    joke_topic: str
    model_name: str


async def create_joke(ctx: RunContext[Deps]) -> str:
    """Create a joke using AI agent."""
    joker = Agent(
        OpenAIChatModel(ctx.deps.model_name, provider=_build_provider()),
        output_type=str,
        system_prompt='You are a joke creation agent.',
    )
    return (await joker.run(user_prompt=ctx.deps.joke_topic)).output


def get_joker_agent(model_name: str) -> Agent[Deps, str]:
    """Get a joke creation agent."""
    return Agent(
        OpenAIChatModel(model_name, provider=_build_provider()),
        output_type=str,
        system_prompt=(
            'Use `create_joke` tool to create four jokes, select the best one and return it without any other comments.'
        ),
        deps_type=Deps,
        tools=[Tool(create_joke, takes_ctx=True)],
    )
