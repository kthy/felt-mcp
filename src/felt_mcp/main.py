"""Entry point for the Felt MCP server."""

from felt_mcp.server import mcp


def main() -> None:
    """Run the Felt MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
