# TypeScript one-page scraper (Bun + Cheerio)

Get data from one web page with Cheerio, on the fast Bun runtime.

## Included features

- **Scrapely SDK** — Actor lifecycle, input, storage and proxies
- **[Bun](https://bun.sh)** — fast JavaScript runtime
- **[Cheerio](https://cheerio.js.org)** — fast HTML parsing
- **Input schema** — define and validate the Actor's input (`.actor/input_schema.json`)
- **Dataset schema** — structured results with a preview view (`.actor/dataset_schema.json`)

## Getting started locally

```bash
bun install
scrapely run      # run the Actor locally
```

## Deploying to Scrapely

Create an Actor from this template in the Scrapely Console (**Develop new → template → Git**).
Scrapely creates a repository in your account, pushes this code, and builds the Actor.
Every push to your repository triggers a new build.
