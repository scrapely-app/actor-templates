# Python web research agent (CrewAI)

A CrewAI agent that researches websites with a page-scraping tool and writes up what it finds.

## Included features

- **Scrapely SDK** — Actor lifecycle, input, storage and proxies
- **[CrewAI](https://www.crewai.com)** — multi-agent framework
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
