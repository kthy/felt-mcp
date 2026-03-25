"""Tests for the Felt API client."""

import httpx
import pytest
import respx

from felt_mcp.felt_api import FELT_API_BASE, create_map, get_map, get_maps


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


# --- get_map tests ---


@respx.mock
@pytest.mark.asyncio
async def test_get_map_returns_map_details() -> None:
    map_data = {
        "id": "map-1",
        "title": "Test Map",
        "url": "https://felt.com/map/test-map",
        "public_access": "private",
        "layers": [{"id": "layer-1", "name": "Points"}],
        "project_id": "proj-1",
    }
    respx.get(f"{FELT_API_BASE}/maps/map-1").mock(
        return_value=httpx.Response(200, json=map_data)
    )

    result = await get_map("map-1")

    assert result["id"] == "map-1"
    assert result["title"] == "Test Map"
    assert result["layers"] == [{"id": "layer-1", "name": "Points"}]


@respx.mock
@pytest.mark.asyncio
async def test_get_map_raises_on_not_found() -> None:
    respx.get(f"{FELT_API_BASE}/maps/bad-id").mock(
        return_value=httpx.Response(404, json={"error": "not found"})
    )

    with pytest.raises(httpx.HTTPStatusError):
        await get_map("bad-id")


# --- create_map tests ---


@respx.mock
@pytest.mark.asyncio
async def test_create_map_with_title() -> None:
    created = {
        "id": "map-new",
        "title": "My New Map",
        "url": "https://felt.com/map/my-new-map",
        "public_access": "private",
    }
    route = respx.post(f"{FELT_API_BASE}/maps").mock(
        return_value=httpx.Response(200, json=created)
    )

    result = await create_map(title="My New Map")

    assert result["id"] == "map-new"
    assert result["title"] == "My New Map"
    request_json = route.calls[0].request.content
    assert b"My New Map" in request_json


@respx.mock
@pytest.mark.asyncio
async def test_create_map_minimal() -> None:
    created = {"id": "map-min", "title": "Untitled Map", "url": "https://felt.com/map/map-min"}
    respx.post(f"{FELT_API_BASE}/maps").mock(
        return_value=httpx.Response(200, json=created)
    )

    result = await create_map()

    assert result["id"] == "map-min"
