# Python MCP proxy

A proxy that turns any existing MCP server (stdio, HTTP or SSE) into a Scrapely Actor with pay-per-event billing.

## Included features

- **Scrapely SDK** — Actor lifecycle, input, storage and proxies
- **[Model Context Protocol](https://modelcontextprotocol.io)** — tools for AI assistants
- **Dataset schema** — structured results with a preview view (`.actor/dataset_schema.json`)
- **Standby mode** — the Actor stays running and answers HTTP requests at its standby URL

## Getting started locally

```bash
python -m pip install -r requirements.txt
scrapely run      # run the Actor locally
```

## Deploying to Scrapely

Create an Actor from this template in the Scrapely Console (**Develop new → template → Git**).
Scrapely creates a repository in your account, pushes this code, and builds the Actor.
Every push to your repository triggers a new build.
