"""Felt MCP server."""

import structlog
from mcp.server.fastmcp import FastMCP

from felt_mcp.felt_api import create_map, get_map, get_maps

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


@mcp.tool()
async def get_map_details(map_id: str) -> dict[str, object]:
    """Get details for a specific Felt map, including its layers and elements.

    Args:
        map_id: The ID of the map to retrieve.
    """
    return await get_map(map_id)


@mcp.tool()
async def get_map_layers(map_id: str) -> list[dict[str, object]]:
    """List all layers on a specific Felt map.

    Args:
        map_id: The ID of the map whose layers to list.
    """
    map_data = await get_map(map_id)
    layers = map_data.get("layers", [])
    if not isinstance(layers, list):
        return []
    return layers  # type: ignore[return-value]


@mcp.tool()
async def create_new_map(
    title: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    zoom: int | None = None,
) -> dict[str, object]:
    """Create a new Felt map.

    Args:
        title: Optional title for the new map.
        lat: Optional initial latitude.
        lon: Optional initial longitude.
        zoom: Optional initial zoom level.
    """
    return await create_map(title=title, lat=lat, lon=lon, zoom=zoom)
