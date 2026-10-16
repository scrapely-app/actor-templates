"""Module defines the main entry point for the Scrapely Actor.

Feel free to modify this file to suit your specific needs.

To build Scrapely Actors, utilize the Scrapely SDK toolkit, read more at the official documentation:
"""

from __future__ import annotations

from http.server import HTTPServer, SimpleHTTPRequestHandler

from scrapely import Actor


class GetHandler(SimpleHTTPRequestHandler):
    """A simple GET HTTP handler that will respond with a message."""

    def do_GET(self) -> None:
        """Handle GET request and respond with a message."""
        # Handle Scrapely standby readiness probe
        if 'x-scrapely-standby-readiness-probe' in self.headers:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'ok')
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello from Actor Standby!')


async def main() -> None:
    """Define a main entry point for the Scrapely Actor.

    This coroutine is executed using `asyncio.run()`, so it must remain an asynchronous function for proper execution.
    Asynchronous execution is required for communication with Scrapely platform, and it also enhances performance in
    the field of web scraping significantly.
    """
    async with Actor:
        # A simple HTTP server listening on the Actor web server port.
        with HTTPServer(('', Actor.configuration.web_server_port), GetHandler) as http_server:
            http_server.serve_forever()
