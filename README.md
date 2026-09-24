# Scrapely Actor templates

Ready-to-run Actor templates that Scrapely uses when you create an Actor with a new Git
repository (Console: **Develop new → template → Git**, or `scrapely create` in the CLI).

Scrapely copies the chosen template into a new private repository under your account and
configures builds so every push rebuilds your Actor.

| Folder | Language | Stack |
|---|---|---|
| `js-crawlee-cheerio` | JavaScript | Crawlee + Cheerio (HTTP, no browser) |
| `js-crawlee-playwright-chrome` | JavaScript | Crawlee + Playwright (headless Chromium) |
| `js-crawlee-puppeteer-chrome` | JavaScript | Crawlee + Puppeteer (headless Chrome) |
| `ts-crawlee-playwright-chrome` | TypeScript | Crawlee + Playwright (headless Chromium) |
| `python-crawlee-playwright` | Python | Crawlee + Playwright (headless Chromium) |
| `python-crawlee-beautifulsoup` | Python | Crawlee + BeautifulSoup (HTTP, no browser) |

Each folder is a complete, buildable Actor: `scrapely.json` config, input/dataset schemas,
Dockerfile based on the Scrapely prebuilt images, and CI-ready source code.

## Template manifest

[`templates.json`](templates.json) at the repo root is the machine-readable catalog the
Scrapely platform consumes (`GET /v2/actor-templates`, the console template wizard, and
`scrapely create` in the CLI). Each entry maps a stable template `id` (plus optional legacy
`aliases`) to its `folder` in this repo and the `mainFile` used for previews. Keep it in
sync when adding, renaming, or removing template folders.
