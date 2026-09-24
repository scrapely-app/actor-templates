# Crawlee + Playwright (Python)

A production-ready Scrapely Actor template built on `PlaywrightCrawler` for Python. Give it a
list of starting URLs and it loads each page in a headless Chromium browser, enqueues the
links it finds, and stores the page title and URL in the default dataset.

## Included features

- **[Crawlee for Python](https://crawlee.dev/python)** and the **Scrapely SDK** — crawling, queues and storage
- **Input schema** — define and validate the Actor's input (`.actor/input_schema.json`)
- **Dataset schema** — structured results with a preview view (`.actor/dataset_schema.json`)
- **Proxy configuration** — rotate IP addresses to avoid blocking (`Actor.create_proxy_configuration()`)

## Getting started locally

```bash
python -m pip install -r requirements.txt
scrapely run --purge      # run the Actor locally
```

Input is read from `.actor/input_schema.json`. By default the Actor starts from
`https://crawlee.dev`; change `start_urls` to point it anywhere.

## Deploying to Scrapely

Create an Actor from this template in the Scrapely Console (**Develop new → template → Git**).
Scrapely creates a repository in your account, pushes this code, and builds the Actor.
Every push to your repository triggers a new build.
