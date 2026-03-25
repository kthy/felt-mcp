# Felt MCP

An [MCP](https://modelcontextprotocol.io/) server for interacting with [Felt](https://felt.com) maps programmatically.

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- A [Felt API token](https://felt.com/account/integrations)

## Configuration

Set your Felt API token as an environment variable:

```bash
export FELT_API_TOKEN=felt_pat_...
```

## Running locally

```bash
uv sync
uv run python -m felt_mcp.main
```

The server uses stdio transport by default, which is the standard for MCP servers launched as subprocesses by an MCP client.

## Running with Docker

```bash
docker build -t felt-mcp .
docker run -e FELT_API_TOKEN felt-mcp
```

## MCP client configuration

Add this to your MCP client config (e.g. Claude Desktop `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "felt": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/felt-mcp", "python", "-m", "felt_mcp.main"],
      "env": {
        "FELT_API_TOKEN": "felt_pat_..."
      }
    }
  }
}
```

Or with Docker:

```json
{
  "mcpServers": {
    "felt": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "FELT_API_TOKEN", "felt-mcp"],
      "env": {
        "FELT_API_TOKEN": "felt_pat_..."
      }
    }
  }
}
```

## Available tools

### `list_maps`

Lists all maps accessible to the authenticated Felt user. Returns maps from all projects with their id, title, URL, project, and access level.

### `get_map_details`

Get details for a specific Felt map, including its layers, elements, and settings.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `map_id`  | string | Yes | The ID of the map to retrieve |

### `get_map_layers`

List all layers on a specific Felt map.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `map_id`  | string | Yes | The ID of the map whose layers to list |

### `create_new_map`

Create a new Felt map with an optional title and initial viewport.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title`   | string | No | Title for the new map |
| `lat`     | float  | No | Initial latitude |
| `lon`     | float  | No | Initial longitude |
| `zoom`    | int    | No | Initial zoom level |

## Development

```bash
uv sync                # install all dependencies including dev
just lint              # format, lint, and type check
just test              # run test suite
just test-failed       # re-run previously failed tests
```

## License

See [LICENSE.md](LICENSE.md).
