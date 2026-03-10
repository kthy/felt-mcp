"""Felt MCP server."""

import structlog
from mcp.server.fastmcp import FastMCP

from felt_mcp.felt_api import get_maps

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.dev.ConsoleRenderer(),
    ],
)

mcp = FastMCP("Felt")


@mcp.tool()
async def list_maps() -> list[dict[str, object]]:
    """List all maps accessible to the authenticated Felt user.

    Returns a list of maps with their id, title, URL, project, and access level.
    """
    return await get_maps()
