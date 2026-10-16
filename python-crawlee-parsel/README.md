# Python site crawler (Crawlee + Parsel)

A crawler that follows links and gets data from static pages, with Crawlee handling retries and request queues. Uses Parsel, with native XPath and CSS selectors. Can't run client-side JavaScript.

## Included features

- **Scrapely SDK** — Actor lifecycle, input, storage and proxies
- **[Crawlee](https://crawlee.dev)** — crawling, request queues, retries and storage
- **[Parsel](https://parsel.readthedocs.io)** — XPath and CSS selectors
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
