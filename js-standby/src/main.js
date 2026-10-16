import http from 'node:http';

import { Actor } from 'scrapely';

// this is ESM project, and as such, it requires you to specify extensions in your relative imports
// read more about this here: https://nodejs.org/docs/latest-v18.x/api/esm.html#mandatory-file-extensions
// import { router } from './routes.js';

// The init() call configures the Actor to correctly work with the platform-provided environment - mainly the storage infrastructure. It is necessary that every Actor performs an init() call.
await Actor.init();

// Create a simple HTTP server that will respond with a message
const server = http.createServer((req, res) => {
    // Handle Scrapely standby readiness probe
    if (req.headers['x-scrapely-standby-readiness-probe']) {
        res.writeHead(200);
        res.end('ok');
        return;
    }
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Hello from Actor Standby!\n');
});

// Listen on the standby port
server.listen(Actor.config.get('standbyPort'));
