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
| `cli-start` | JavaScript | CLI Actor wrapper |
| `js-bootstrap-cheerio-crawler` | JavaScript | JavaScript minimal site crawler (Crawlee + Cheerio) |
| `js-crawlee-playwright-camoufox` | JavaScript | JavaScript stealth crawler (Crawlee + Playwright + Camoufox) |
| `js-cypress` | JavaScript | JavaScript test runner (Cypress) |
| `js-empty` | JavaScript | Empty JavaScript Actor |
| `js-langchain` | JavaScript | JavaScript website chat (LangChain) |
| `js-langgraph-agent` | JavaScript | JavaScript web search agent (LangGraph) |
| `js-standby` | JavaScript | JavaScript API Actor |
| `js-start` | JavaScript | JavaScript one-page scraper (Cheerio) |
| `python-beautifulsoup` | Python | Python site crawler (BeautifulSoup) |
| `python-browseruse` | Python | Browser Use scraping agent |
| `python-crawlee-parsel` | Python | Python site crawler (Crawlee + Parsel) |
| `python-crawlee-playwright-camoufox` | Python | Python stealth crawler (Crawlee + Playwright + Camoufox) |
| `python-crewai` | Python | Python social media agent (CrewAI) |
| `python-empty` | Python | Empty Python Actor |
| `python-langgraph` | Python | Python social media agent (LangGraph) |
| `python-llamaindex-agent` | Python | Python contact finder agent (LlamaIndex) |
| `python-mcp-empty` | Python | Python MCP server |
| `python-mcp-proxy` | Python | Python MCP proxy |
| `python-playwright` | Python | Python browser crawler (Playwright) |
| `python-pydanticai` | Python | Python joke agent (PydanticAI) |
| `python-scrapy` | Python | Python site crawler (Scrapy) |
| `python-selenium` | Python | Python browser crawler (Selenium) |
| `python-smolagents` | Python | Python news agent (Smolagents) |
| `python-standby` | Python | Python API Actor |
| `python-start` | Python | Python one-page scraper (BeautifulSoup) |
| `python-uv` | Python | Empty Python Actor (uv) |
| `ts-beeai-agent` | TypeScript | TypeScript social media agent (BeeAI) |
| `ts-crawlee-cheerio` | TypeScript | TypeScript site crawler (Crawlee + Cheerio) |
| `ts-crawlee-playwright-camoufox` | TypeScript | TypeScript stealth crawler (Crawlee + Playwright + Camoufox) |
| `ts-crawlee-puppeteer-chrome` | TypeScript | TypeScript browser crawler (Crawlee + Puppeteer + Chrome) |
| `ts-empty` | TypeScript | Empty TypeScript Actor |
| `ts-mastraai` | TypeScript | TypeScript social media agent (Mastra) |
| `ts-mcp-empty` | TypeScript | TypeScript MCP server |
| `ts-mcp-proxy` | TypeScript | TypeScript MCP proxy |
| `ts-playwright-test-runner` | TypeScript | TypeScript test runner (Playwright) |
| `ts-standby` | TypeScript | TypeScript API Actor |
| `ts-start` | TypeScript | TypeScript one-page scraper (Cheerio) |
| `ts-start-bun` | TypeScript | TypeScript one-page scraper (Bun + Cheerio) |

Each folder is a complete, buildable Actor: `scrapely.json` config, input/dataset schemas,
Dockerfile based on the Scrapely prebuilt images, and CI-ready source code.

## Template manifest

[`templates.json`](templates.json) at the repo root is the machine-readable catalog the
Scrapely platform consumes (`GET /v2/actor-templates`, the console template wizard, and
`scrapely create` in the CLI). Each entry maps a stable template `id` (plus optional legacy
`aliases`) to its `folder` in this repo and the `mainFile` used for previews. Keep it in
sync when adding, renaming, or removing template folders.
