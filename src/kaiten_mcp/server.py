"""Kaiten MCP Server - exposes Kaiten API as MCP tools."""
import asyncio
import json
import logging
import os

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolResult

from kaiten_mcp.client import KaitenClient, KaitenApiError
from kaiten_mcp.tools import (
    spaces, boards, columns, lanes, cards, tags,
    card_types, custom_properties, comments, members, time_logs,
)

load_dotenv()

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = Server("kaiten-mcp")

_client: KaitenClient | None = None


def get_client() -> KaitenClient:
    global _client
    if _client is None:
        _client = KaitenClient()
    return _client


TOOL_MODULES = [
    spaces, boards, columns, lanes, cards, tags,
    card_types, custom_properties, comments, members, time_logs,
]


def _collect_tools() -> dict[str, dict]:
    """Collect tool definitions from all modules."""
    tools = {}
    for module in TOOL_MODULES:
        if hasattr(module, "TOOLS"):
            for name, definition in module.TOOLS.items():
                tools[name] = definition
    return tools


ALL_TOOLS = _collect_tools()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name=name,
            description=defn["description"],
            inputSchema=defn["inputSchema"],
        )
        for name, defn in ALL_TOOLS.items()
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    if name not in ALL_TOOLS:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Unknown tool: {name}")]
        )
    handler = ALL_TOOLS[name]["handler"]
    client = get_client()
    try:
        result = await handler(client, arguments)
        if isinstance(result, (dict, list)):
            text = json.dumps(result, ensure_ascii=False, indent=2, default=str)
        else:
            text = str(result) if result is not None else "OK"
        return CallToolResult(content=[TextContent(type="text", text=text)])
    except KaitenApiError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Kaiten API Error {e.status_code}: {e.message}")]
        )
    except Exception as e:
        logger.exception("Tool execution error")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]
        )


def main():
    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
