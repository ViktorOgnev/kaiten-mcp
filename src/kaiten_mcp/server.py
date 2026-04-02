"""Kaiten MCP stdio entrypoint."""

import asyncio

from mcp.server.stdio import stdio_server

from kaiten_mcp.runtime import (
    ALL_TOOLS,
    COMPACT_JSON_THRESHOLD,
    FILE_OUTPUT_THRESHOLD,
    TOOL_MODULES,
    app,
    call_tool,
    close_client,
    get_client,
    list_tools,
)


def main() -> None:
    async def run() -> None:
        try:
            async with stdio_server() as (read_stream, write_stream):
                await app.run(read_stream, write_stream, app.create_initialization_options())
        finally:
            await close_client()

    asyncio.run(run())


__all__ = [
    "ALL_TOOLS",
    "COMPACT_JSON_THRESHOLD",
    "FILE_OUTPUT_THRESHOLD",
    "TOOL_MODULES",
    "app",
    "call_tool",
    "get_client",
    "list_tools",
    "main",
]
