# TypeScript one-page scraper (Cheerio)

A scraper that gets data from one web page with Cheerio. The simplest way to start scraping.

## Included features

- **Scrapely SDK** — Actor lifecycle, input, storage and proxies
- **[Cheerio](https://cheerio.js.org)** — fast HTML parsing
- **Input schema** — define and validate the Actor's input (`.actor/input_schema.json`)
- **Dataset schema** — structured results with a preview view (`.actor/dataset_schema.json`)

## Getting started locally

```bash
npm install
npm run start      # run the Actor
npm run build      # compile to dist/
```

## Deploying to Scrapely

Create an Actor from this template in the Scrapely Console (**Develop new → template → Git**).
Scrapely creates a repository in your account, pushes this code, and builds the Actor.
Every push to your repository triggers a new build.
