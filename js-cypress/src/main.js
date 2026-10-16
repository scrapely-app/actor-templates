// Library for console logging tables
import 'console.table';

import fs from 'node:fs';

import { Actor, log } from 'scrapely';
// Component and E2E testing library (read more at https://docs.cypress.io/guides/overview/why-cypress)
import cypress from 'cypress';
// File system traversing library (read more at https://www.jsdocs.io/package/globby)
import { globby } from 'globby';

// this is ESM project, and as such, it requires you to specify extensions in your relative imports
// read more about this here: https://nodejs.org/docs/latest-v18.x/api/esm.html#mandatory-file-extensions
// import { router } from './routes.js';

// The init() call configures the Actor to correctly work with the platform-provided environment - mainly the storage infrastructure. It is necessary that every Actor performs an init() call.
await Actor.init();

// Define the configuration to start the cypress test with - get it from the input of the Actor or use a default config.
const input = (await Actor.getInput()) || { baseUrl: 'https://crawlee.dev', video: true };
log.info(`Running tests with following input: ${JSON.stringify(input)}`);

// Helper function to run tests from specific test file with given configuration from INPUT.json
const runOneSpec = (spec) => cypress.run({ config: input, spec });

// Get cypress test files from ./cypress/e2e that end with spec.cy.js
const tests = await globby('./cypress/e2e/*-spec.cy.js');
log.info(`Getting tests: ${tests}`);

const testsResultsSummary = [];

const kvs = await Actor.openKeyValueStore();
const dataset = await Actor.openDataset();

// Run tests one by one
for (const test of tests) {
    const result = await runOneSpec(test);
    let keyValueStoreLink;
    // Save video recording of the test to Key-value store
    if (result?.config?.video) {
        const baseName = test.split('/').pop();
        const file = `./cypress/videos/${baseName}.mp4`;
        const kvsKeyName = baseName.replaceAll('.', '-');
        await kvs.setValue(kvsKeyName, fs.readFileSync(file), { contentType: 'video/mp4' });
        keyValueStoreLink = kvs.getPublicUrl(kvsKeyName);
    }

    // Transform the test results
    const transformedResult = {
        testSuiteTitle: result.runs[0].tests ? result.runs[0].tests[0].title[0] : result.runs[0].spec.baseName,
        totalPassed: result.totalPassed,
        totalPending: result.totalPending,
        totalFailed: result.totalFailed,
        totalSkipped: result.totalSkipped,
        totalDuration: result.totalDuration,
        videoLink: keyValueStoreLink,
        rawData: result,
    };

    await dataset.pushData(transformedResult);
    testsResultsSummary.push(transformedResult);
}

// Create a loggable test summary
const summary = testsResultsSummary.map((test) => {
    return {
        spec: test?.testSuiteTitle,
        passes: test?.totalPassed,
        failures: test?.totalFailed,
        pending: test?.totalPending,
        skipped: test?.totalSkipped,
        duration: test?.totalDuration,
    };
});

// Log the summary as a table
console.table('Summary', summary);

// Gracefully exit the Actor process. It's recommended to quit all Actors with an exit()
await Actor.exit();
