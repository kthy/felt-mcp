"""Client for the Felt REST API."""

from os import environ

import httpx
import structlog

logger = structlog.get_logger()

FELT_API_BASE = "https://felt.com/api/v2"


def _get_api_token() -> str:
    """Read the Felt API token from the environment."""
    token = environ.get("FELT_API_TOKEN")
    if not token:
        msg = "FELT_API_TOKEN environment variable is not set"
        raise ValueError(msg)
    return token


def _auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {_get_api_token()}"}


async def get_map(map_id: str) -> dict[str, object]:
    """Fetch details for a single map."""
    async with httpx.AsyncClient(base_url=FELT_API_BASE, headers=_auth_headers()) as client:
        resp = await client.get(f"/maps/{map_id}")
        resp.raise_for_status()
        return resp.json()


async def create_map(
    title: str | None = None,
    *,
    lat: float | None = None,
    lon: float | None = None,
    zoom: int | None = None,
) -> dict[str, object]:
    """Create a new map."""
    body: dict[str, object] = {}
    if title is not None:
        body["title"] = title
    if lat is not None:
        body["lat"] = lat
    if lon is not None:
        body["lon"] = lon
    if zoom is not None:
        body["zoom"] = zoom

    async with httpx.AsyncClient(base_url=FELT_API_BASE, headers=_auth_headers()) as client:
        resp = await client.post("/maps", json=body)
        resp.raise_for_status()
        return resp.json()


async def get_maps() -> list[dict[str, object]]:
    """Fetch all maps accessible to the authenticated user.

    The Felt API has no single "list maps" endpoint, so this fetches all
    projects and collects the maps referenced in each one.
    """
    async with httpx.AsyncClient(base_url=FELT_API_BASE, headers=_auth_headers()) as client:
        resp = await client.get("/projects")
        resp.raise_for_status()
        projects: list[dict[str, object]] = resp.json()

        logger.info("fetched_projects", count=len(projects))

        maps: list[dict[str, object]] = []
        for project in projects:
            project_id = project["id"]
            detail_resp = await client.get(f"/projects/{project_id}")
            detail_resp.raise_for_status()
            project_detail: dict[str, object] = detail_resp.json()
            project_maps: list[dict[str, object]] = project_detail.get("maps", [])
            for m in project_maps:
                m["project_id"] = project_id
                m["project_name"] = project.get("name")
            maps.extend(project_maps)

        logger.info("fetched_maps", count=len(maps))
        return maps
