# JavaScript stealth crawler (Crawlee + Playwright + Camoufox)

A browser crawler built to get past bot protection. Uses Camoufox, a Firefox build that looks like a real user.

## Included features

- **Scrapely SDK** — Actor lifecycle, input, storage and proxies
- **[Crawlee](https://crawlee.dev)** — crawling, request queues, retries and storage
- **[Playwright](https://playwright.dev)** — headless browser automation
- **[Camoufox](https://camoufox.com)** — stealth Firefox build
- **Input schema** — define and validate the Actor's input (`.actor/input_schema.json`)
- **Dataset schema** — structured results with a preview view (`.actor/dataset_schema.json`)

## Getting started locally

```bash
npm install
npm run start      # run the Actor
```

## Deploying to Scrapely

Create an Actor from this template in the Scrapely Console (**Develop new → template → Git**).
Scrapely creates a repository in your account, pushes this code, and builds the Actor.
Every push to your repository triggers a new build.
