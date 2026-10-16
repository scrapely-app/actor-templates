"""Module defines Pydantic models for this project.

These models are used mainly for the structured tool and LLM outputs.
Resources:
- https://docs.pydantic.dev/latest/concepts/models/
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AgentStructuredOutput(BaseModel):
    """Structured output returned by the ReAct agent."""

    summary: str = Field(description='Concise answer to the user query.')
    key_points: list[str] = Field(default_factory=list, description='Most important facts found on the pages.')
    sources: list[str] = Field(default_factory=list, description='URLs of the pages the answer is based on.')
