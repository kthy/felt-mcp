# Architecture Decision Records

<!-- omit in toc -->
## Table of Contents

- [ADR-001: Use Structlog for logging](#adr-001-use-structlog-for-logging)
- [ADR-002: Use FastMCP for the MCP server](#adr-002-use-fastmcp-for-the-mcp-server)
- [ADR-003: Aggregate maps from projects](#adr-003-aggregate-maps-from-projects)
- [ADR-004: Containerize with Docker and uv](#adr-004-containerize-with-docker-and-uv)

## ADR-001: Use Structlog for logging

**Date:** 2026-03-09

**Context:**

We want the module to output structured logs.

**Decision:**

Use [structlog](https://www.structlog.org/) for log messages.

**Consequences:**

- Benefits
  - Emits structured, machine-readable logs (JSON, key/value) that are easy to index and query in log stores (ELK, Loki, Datadog).
  - Encourages consistent log schema and contextual logging (event-wise context, bound processors).
  - Easier to attach contextual data (request id, user id) without string formatting.
  - Simpler testing and assertions against emitted events.
  - Flexible output pipelines — processors can format, filter, redact, or enrich events centrally.

- Costs / Trade-offs
  - Adds a runtime dependency (structlog) and requires team familiarity with its API and concepts (processors, bind, event_dict).
  - Slight configuration complexity to wire structlog with Python's stdlib logging and third‑party libraries.
  - Possible performance overhead if many expensive processors are used; careful processor design is required.

- Operational considerations
  - Decide a canonical output format (JSON for ingestion systems or human console format for local dev).
  - Standardize event and field names to avoid fragmentation across services.
  - Implement redaction/PII handling as processors.
  - Ensure log rotation/retention and existing monitoring tooling accept the chosen format.

- Developer impact
  - Improves debuggability and observability long term.
  - Requires documentation and examples for developers to adopt consistent usage.
  - Tests should assert on structured events instead of formatted strings.

## ADR-002: Use FastMCP for the MCP server

**Date:** 2026-03-10

**Context:**

We need an MCP server framework. The [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk) offers two APIs: the low-level `MCPServer` class and the high-level `FastMCP` decorator-based API.

**Decision:**

Use `FastMCP` from `mcp.server.fastmcp` to define the server and its tools.

**Consequences:**

- Benefits
  - Minimal boilerplate — tools are plain async functions decorated with `@mcp.tool()`.
  - Automatic input validation and JSON schema generation from type hints.
  - Built-in support for stdio, SSE, and Streamable HTTP transports.

- Costs / Trade-offs
  - Less control over low-level protocol details than using `MCPServer` directly.
  - Tightly coupled to the `mcp` package's API surface, which is still evolving.

## ADR-003: Aggregate maps from projects

**Date:** 2026-03-10

**Context:**

The Felt REST API does not expose a "list all maps" endpoint. Maps are accessible through project details (`GET /api/v2/projects/{project_id}`), which include a `maps` array.

**Decision:**

The `list_maps` tool fetches all projects via `GET /api/v2/projects`, then retrieves each project's detail to collect its maps. This is an N+1 request pattern.

**Consequences:**

- Benefits
  - Provides a single tool that returns all maps across all projects, which is what users typically want.

- Costs / Trade-offs
  - N+1 HTTP requests. For users with many projects this may be slow.
  - If the Felt API adds a bulk maps endpoint in the future, this should be replaced.

## ADR-004: Containerize with Docker and uv

**Date:** 2026-03-10

**Context:**

The server needs a reproducible deployment option beyond `uv run` on a developer machine.

**Decision:**

Provide a `Dockerfile` based on `python:3.14-slim` that installs `uv` from the official `ghcr.io/astral-sh/uv` image and uses `uv sync --frozen` for deterministic installs.

**Consequences:**

- Benefits
  - Reproducible builds from the lockfile.
  - Small image size via `--no-dev` and the slim base.
  - Compatible with MCP clients that launch servers as `docker run` subprocesses.

- Costs / Trade-offs
  - Requires Docker to be installed for this deployment path.
  - The `python:3.14-slim` base image may not yet be widely available on all registries while 3.14 is in pre-release.
