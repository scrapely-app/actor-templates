# Python web research agent (LangGraph)

An AI agent that researches a topic or website with a page-scraping tool and returns a structured summary, built on graph-based, multi-step workflows.

## Included features

- **Scrapely SDK** — Actor lifecycle, input, storage and proxies
- **[LangGraph](https://langchain-ai.github.io/langgraph/)** — agent workflows
- **Scrapely LLM gateway** — call OpenRouter models with the run token; usage is billed to your Scrapely account, no provider API key needed
- **Input schema** — define and validate the Actor's input (`.actor/input_schema.json`)
- **Dataset schema** — structured results with a preview view (`.actor/dataset_schema.json`)

## Getting started locally

```bash
python -m pip install -r requirements.txt
scrapely run      # run the Actor locally
```

LLM calls go to `SCRAPELY_LLM_BASE_URL` (set automatically on the platform) with the run's
`SCRAPELY_TOKEN`, so the agent works inside a Scrapely run without any provider API key.

## Deploying to Scrapely

Create an Actor from this template in the Scrapely Console (**Develop new → template → Git**).
Scrapely creates a repository in your account, pushes this code, and builds the Actor.
Every push to your repository triggers a new build.
