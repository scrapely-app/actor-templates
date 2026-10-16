# JavaScript test runner (Cypress)

A cloud test runner for Cypress that saves results and videos.

## Included features

- **Scrapely SDK** — Actor lifecycle, input, storage and proxies
- **[Cypress](https://www.cypress.io)** — end-to-end browser tests
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
