"""Main entry point for the MCP Server Actor."""

import os
import shlex
from typing import Any

from mcp.client.stdio import StdioServerParameters

from scrapely import Actor

from .const import SESSION_TIMEOUT_SECS, TOOL_WHITELIST
from .models import RemoteServerParameters, ServerParameters, ServerType
from .server import ProxyServer

# Actor configuration
STANDBY_MODE = os.environ.get('ACTOR_META_ORIGIN') == 'STANDBY'
# Bind to all interfaces (0.0.0.0) as this is running in a containerized environment (Scrapely Actor)
# The container's network is isolated, so this is safe
HOST = '0.0.0.0'  # noqa: S104 - Required for container networking at Scrapely platform
PORT = (Actor.is_at_home() and int(os.environ.get('ACTOR_STANDBY_PORT') or '5001')) or 5001
SERVER_NAME = 'arxiv-mcp-server'  # Name of the MCP server, without spaces

# EDIT THIS SECTION ------------------------------------------------------------
# The upstream MCP server is configured by the Actor input (see the input schema in .actor/scrapely.json).
# Standby runs receive the input schema defaults, so change the `default` values there (or the fallbacks below)
# to wrap a different MCP server.
#
# 1) Stdio server: `mcpServerCommand` is the command line that starts the server, e.g. `arxiv-mcp-server`.
#    Do not forget to install the server in the Dockerfile (see the `uv tool install` step).
DEFAULT_MCP_SERVER_COMMAND = 'arxiv-mcp-server'
# Optional environment variables passed to the stdio server process.
MCP_SERVER_ENV = {'YOUR-ENV_VAR': os.getenv('YOUR-ENV-VAR') or ''}
#
# 2) Remote server: set `mcpServerUrl` to a Streamable HTTP (or SSE, see `mcpServerTransport`) MCP endpoint.
#    `mcpServerAuthorization` is sent as the Authorization header, e.g. `Bearer YOUR-API-KEY`.
# ------------------------------------------------------------------------------


def get_mcp_server_config(actor_input: dict[str, Any]) -> tuple[ServerType, ServerParameters]:
    """Build the upstream MCP server configuration from the Actor input."""
    url = (actor_input.get('mcpServerUrl') or '').strip()
    if url:
        server_type = ServerType.SSE if actor_input.get('mcpServerTransport') == 'sse' else ServerType.HTTP
        authorization = (actor_input.get('mcpServerAuthorization') or '').strip()
        headers = {'Authorization': authorization} if authorization else None
        return server_type, RemoteServerParameters(url=url, headers=headers)

    command = shlex.split(actor_input.get('mcpServerCommand') or DEFAULT_MCP_SERVER_COMMAND)
    if not command:
        raise ValueError('Input "mcpServerCommand" must not be empty')
    return ServerType.STDIO, StdioServerParameters(command=command[0], args=command[1:], env=MCP_SERVER_ENV)


session_timeout_secs = int(os.getenv('SESSION_TIMEOUT_SECS', SESSION_TIMEOUT_SECS))


async def main() -> None:
    """Run the MCP Server Actor.

    This function:
    1. Initializes the Actor
    2. Charges for Actor startup
    3. Creates and starts the proxy server
    4. Configures charging for MCP operations using Actor.charge

    CHARGING STRATEGIES:
    The template supports multiple charging approaches:

    1. GENERIC MCP CHARGING:
       - Charge for all tool calls with a flat rate (TOOL_CALL event)
       - Charge for resource operations (RESOURCE_LIST, RESOURCE_READ)
       - Charge for prompt operations (PROMPT_LIST, PROMPT_GET)
       - Charge for tool listing (TOOL_LIST)

    2. DOMAIN-SPECIFIC CHARGING (arXiv example):
       - Charge different amounts for different tools
       - search_papers: $0.01 per search
       - list_papers: $0.001 per listing
       - download_paper: $0.005 per download
       - read_paper: $0.02 per paper read

    3. NO CHARGING:
       - Comment out all charging lines for free service

    Charging events are defined in .actor/pay_per_event.json
    """
    async with Actor:
        url = os.environ.get('ACTOR_STANDBY_URL', HOST)
        if not STANDBY_MODE:
            msg = (
                'Actor is not designed to run in the NORMAL mode. Use MCP server URL to connect to the server.\n'
                f'Connect to {url}/mcp to establish a connection.'
            )
            Actor.log.info(msg)
            await Actor.exit(status_message=msg)
            return

        actor_input = await Actor.get_input() or {}
        server_type, mcp_server_params = get_mcp_server_config(actor_input)
        # The tool whitelist and its pricing (const.py) are tailored to the default arXiv server.
        # When wrapping a custom server, all of its tools are exposed and charged as generic tool calls.
        is_default_server = isinstance(mcp_server_params, StdioServerParameters) and [
            mcp_server_params.command,
            *mcp_server_params.args,
        ] == shlex.split(DEFAULT_MCP_SERVER_COMMAND)

        try:
            # Create and start the server with charging enabled
            Actor.log.info('Starting MCP server')
            Actor.log.info('Add the following configuration to your MCP client to use Streamable HTTP transport:')
            Actor.log.info(
                f"""
                {{
                    "mcpServers": {{
                        "{SERVER_NAME}": {{
                            "url": "{url}/mcp",
                        }}
                    }}
                }}
                """
            )
            # Pass Actor.charge to enable charging for MCP operations
            # The proxy server will use this to charge for different operations
            proxy_server = ProxyServer(
                server_name=SERVER_NAME,
                config=mcp_server_params,
                host=HOST,
                port=PORT,
                server_type=server_type,
                actor_charge_function=Actor.charge,
                tool_whitelist=TOOL_WHITELIST if is_default_server else None,
                session_timeout_secs=session_timeout_secs,
            )
            await proxy_server.start()
        except Exception as e:
            Actor.log.exception(f'Server failed to start: {e}')
            await Actor.exit()
            raise
