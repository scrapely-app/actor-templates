# TypeScript browser crawler (Crawlee + Puppeteer + Chrome)

A browser crawler that renders JavaScript in headless Chrome, with Crawlee handling retries, queues, and proxies. Good for social feeds, dashboards, or single-page apps.

## Included features

- **Scrapely SDK** — Actor lifecycle, input, storage and proxies
- **[Crawlee](https://crawlee.dev)** — crawling, request queues, retries and storage
- **[Puppeteer](https://pptr.dev)** — headless Chrome automation
- **Headless Chrome** — renders client-side JavaScript
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
