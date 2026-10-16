# Empty Python Actor (uv)

An Actor with the Scrapely SDK set up and dependencies managed by the uv package manager, so you can build any tool you need.

## Included features

- **Scrapely SDK** — Actor lifecycle, input, storage and proxies
- **[uv](https://docs.astral.sh/uv/)** — dependency management
- **Input schema** — define and validate the Actor's input (`.actor/input_schema.json`)
- **Dataset schema** — structured results with a preview view (`.actor/dataset_schema.json`)

## Getting started locally

```bash
uv sync
scrapely run      # run the Actor locally
```

## Deploying to Scrapely

Create an Actor from this template in the Scrapely Console (**Develop new → template → Git**).
Scrapely creates a repository in your account, pushes this code, and builds the Actor.
Every push to your repository triggers a new build.
