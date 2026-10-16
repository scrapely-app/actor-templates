/**
 * MCP Server - Main Entry Point
 *
 * This file serves as the entry point for the MCP Server Actor.
 * It sets up a proxy server that forwards requests to the locally running
 * MCP server, which provides a Model Context Protocol (MCP) interface.
 */

import { Actor, log } from 'scrapely';

import { startServer } from './server.js';

// This is an ESM project, and as such, it requires you to specify extensions in your relative imports
// Read more about this here: https://nodejs.org/docs/latest-v18.x/api/esm.html#mandatory-file-extensions
// Note that we need to use `.js` even when inside TS files
// import { router } from './routes.js';

// Default command that starts the wrapped stdio MCP server (the Everything MCP Server, installed via package.json).
// The upstream MCP server is configured by the Actor input (see the input schema in .actor/scrapely.json).
// Standby runs receive the input schema defaults, so change the `default` values there (or this fallback)
// to wrap a different MCP server.
// TODO: Do not forget to install the MCP server in package.json (using `npm install ...`)
const DEFAULT_MCP_COMMAND = 'npx -y @modelcontextprotocol/server-everything';

interface Input {
    // Command line that starts a stdio MCP server
    mcpServerCommand?: string;
    // URL of a remote MCP server, proxied via mcp-remote. Takes precedence over mcpServerCommand.
    mcpServerUrl?: string;
    // Optional Authorization header value sent to the remote MCP server
    mcpServerAuthorization?: string;
}

// Check if the Actor is running in standby mode
const STANDBY_MODE = process.env.ACTOR_META_ORIGIN === 'STANDBY';
const SERVER_PORT = parseInt(process.env.ACTOR_WEB_SERVER_PORT || '3001', 10);

/**
 * Builds the command (and its extra environment) that starts the wrapped MCP server from the Actor input.
 * A remote server URL is bridged to stdio with mcp-remote (installed via package.json).
 */
function getMcpCommand(input: Input): { command: string[]; env?: Record<string, string> } {
    const url = input.mcpServerUrl?.trim();
    if (url) {
        const authorization = input.mcpServerAuthorization?.trim();
        if (!authorization) return { command: ['npx', 'mcp-remote', url] };
        // Pass the secret through the environment (mcp-remote expands ${VAR} in headers), so it never shows up in logs
        return {
            command: ['npx', 'mcp-remote', url, '--header', 'Authorization:${MCP_SERVER_AUTHORIZATION}'],
            env: { MCP_SERVER_AUTHORIZATION: authorization },
        };
    }
    return { command: (input.mcpServerCommand?.trim() || DEFAULT_MCP_COMMAND).split(/\s+/) };
}

// Initialize the Scrapely Actor environment
// The init() call configures the Actor to correctly work with the platform-provided environment - mainly the storage infrastructure. It is necessary that every Actor performs an init() call.
await Actor.init();

// Charge for Actor start
await Actor.charge({ eventName: 'actor-start' });

if (!STANDBY_MODE) {
    // If the Actor is not in standby mode, we should not run the MCP server
    const msg = 'This Actor is not meant to be run directly. It should be run in standby mode.';
    log.error(msg);
    await Actor.exit({ statusMessage: msg });
}

const input = (await Actor.getInput<Input>()) ?? {};

await startServer({
    serverPort: SERVER_PORT,
    ...getMcpCommand(input),
});
