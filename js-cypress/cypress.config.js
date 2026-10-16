import { defineConfig } from 'cypress';

export default defineConfig({
    e2e: {
        // Default base URL, used when running the tests directly with the Cypress CLI (e.g. `npm run cypress:open`)
        baseUrl: 'https://crawlee.dev',
    },
});
