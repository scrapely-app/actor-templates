# Python browser crawler (Playwright)

A crawler that uses a real browser through Playwright, so it gets data HTTP crawlers miss. Good for social feeds, dashboards, or single-page apps.

## Included features

- **Scrapely SDK** — Actor lifecycle, input, storage and proxies
- **[Playwright](https://playwright.dev)** — headless browser automation
- **Headless Chrome** — renders client-side JavaScript
- **Input schema** — define and validate the Actor's input (`.actor/input_schema.json`)
- **Dataset schema** — structured results with a preview view (`.actor/dataset_schema.json`)

## Getting started locally

```bash
python -m pip install -r requirements.txt
scrapely run      # run the Actor locally
```

## Deploying to Scrapely

Create an Actor from this template in the Scrapely Console (**Develop new → template → Git**).
Scrapely creates a repository in your account, pushes this code, and builds the Actor.
Every push to your repository triggers a new build.
