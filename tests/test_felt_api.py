"""Tests for the Felt API client."""

import httpx
import pytest
import respx

from felt_mcp.felt_api import FELT_API_BASE, get_maps


@pytest.fixture(autouse=True)
def _set_api_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FELT_API_TOKEN", "test-token")


@respx.mock
@pytest.mark.asyncio
async def test_get_maps_returns_maps_from_all_projects() -> None:
    projects = [
        {"id": "proj-1", "name": "Project One", "type": "project_reference"},
        {"id": "proj-2", "name": "Project Two", "type": "project_reference"},
    ]
    project_1_detail = {
        "id": "proj-1",
        "name": "Project One",
        "maps": [
            {"id": "map-a", "title": "Map A", "url": "https://felt.com/map/map-a"},
        ],
    }
    project_2_detail = {
        "id": "proj-2",
        "name": "Project Two",
        "maps": [
            {"id": "map-b", "title": "Map B", "url": "https://felt.com/map/map-b"},
            {"id": "map-c", "title": "Map C", "url": "https://felt.com/map/map-c"},
        ],
    }

    respx.get(f"{FELT_API_BASE}/projects").mock(
        return_value=httpx.Response(200, json=projects)
    )
    respx.get(f"{FELT_API_BASE}/projects/proj-1").mock(
        return_value=httpx.Response(200, json=project_1_detail)
    )
    respx.get(f"{FELT_API_BASE}/projects/proj-2").mock(
        return_value=httpx.Response(200, json=project_2_detail)
    )

    maps = await get_maps()

    assert len(maps) == 3
    assert maps[0]["id"] == "map-a"
    assert maps[0]["project_id"] == "proj-1"
    assert maps[0]["project_name"] == "Project One"
    assert maps[1]["id"] == "map-b"
    assert maps[2]["id"] == "map-c"
    assert maps[2]["project_name"] == "Project Two"


@respx.mock
@pytest.mark.asyncio
async def test_get_maps_empty_when_no_projects() -> None:
    respx.get(f"{FELT_API_BASE}/projects").mock(
        return_value=httpx.Response(200, json=[])
    )

    maps = await get_maps()

    assert maps == []


@respx.mock
@pytest.mark.asyncio
async def test_get_maps_handles_project_with_no_maps() -> None:
    projects = [{"id": "proj-empty", "name": "Empty", "type": "project_reference"}]
    project_detail = {"id": "proj-empty", "name": "Empty", "maps": []}

    respx.get(f"{FELT_API_BASE}/projects").mock(
        return_value=httpx.Response(200, json=projects)
    )
    respx.get(f"{FELT_API_BASE}/projects/proj-empty").mock(
        return_value=httpx.Response(200, json=project_detail)
    )

    maps = await get_maps()

    assert maps == []


@pytest.mark.asyncio
async def test_get_maps_raises_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FELT_API_TOKEN")
    with pytest.raises(ValueError, match="FELT_API_TOKEN"):
        await get_maps()
