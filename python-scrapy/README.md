# Python site crawler (Scrapy)

A crawler for large sites, built on the Scrapy framework. Can't run client-side JavaScript.

## Included features

- **Scrapely SDK** — Actor lifecycle, input, storage and proxies
- **[Scrapy](https://scrapy.org)** — crawling framework, wired to Scrapely storage
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
