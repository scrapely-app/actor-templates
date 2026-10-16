# Python site crawler (BeautifulSoup)

A lightweight crawler that follows links and gets data from static pages with BeautifulSoup. Good for blogs, news, or product listings, but it can't run client-side JavaScript.

## Included features

- **Scrapely SDK** — Actor lifecycle, input, storage and proxies
- **[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)** — HTML parsing
- **[HTTPX](https://www.python-httpx.org)** — HTTP client
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
