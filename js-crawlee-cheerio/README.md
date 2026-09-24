# Crawlee + Cheerio

A fast, production-ready Scrapely Actor template built on `CheerioCrawler`. Give it a list of
starting URLs and it fetches each page, parses the raw HTML with Cheerio (no browser needed),
and stores the page title and URL in the default dataset.

## Included features

- **[Crawlee](https://crawlee.dev)** and the **Scrapely SDK** — crawling, request queues and storage
- **Input schema** — define and validate the Actor's input (`.actor/input_schema.json`)
- **Dataset schema** — structured results with a preview view (`.actor/dataset_schema.json`)
- **ESLint + Prettier + Vitest** — linting, formatting and a runnable test

## Getting started locally

```bash
npm install
npm run start      # run the Actor
npm run test       # run the test suite
```

Input is read from `.actor/input_schema.json`. By default the Actor starts from
`https://crawlee.dev`; change `startUrls` to point it anywhere.

## Deploying to Scrapely

Create an Actor from this template in the Scrapely Console (**Develop new → template → Git**).
Scrapely creates a repository in your account, pushes this code, and builds the Actor.
Every push to your repository triggers a new build.
