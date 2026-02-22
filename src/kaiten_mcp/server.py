"""Kaiten MCP Server - exposes Kaiten API as MCP tools."""

import asyncio
import json
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, TextContent, Tool

from kaiten_mcp.client import KaitenApiError, KaitenClient
from kaiten_mcp.tools import (
    audit_and_analytics,
    automations,
    blockers,
    boards,
    card_relations,
    card_types,
    cards,
    charts,
    checklists,
    columns,
    comments,
    custom_properties,
    documents,
    external_links,
    files,
    lanes,
    members,
    projects,
    roles_and_groups,
    service_desk,
    spaces,
    subscribers,
    tags,
    time_logs,
    tree,
    utilities,
    webhooks,
)
from kaiten_mcp.tools.compact import strip_base64

load_dotenv()

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Response size thresholds
COMPACT_JSON_THRESHOLD = 10_000  # 10KB: switch to compact JSON (no indent)
FILE_OUTPUT_THRESHOLD = 200_000  # 200KB: save to file if output dir configured

app = Server("kaiten-mcp")

_client: KaitenClient | None = None


def get_client() -> KaitenClient:
    global _client
    if _client is None:
        _client = KaitenClient()
    return _client


TOOL_MODULES = [
    audit_and_analytics,
    automations,
    blockers,
    boards,
    card_relations,
    card_types,
    cards,
    charts,
    checklists,
    columns,
    comments,
    custom_properties,
    documents,
    external_links,
    files,
    lanes,
    members,
    projects,
    roles_and_groups,
    service_desk,
    spaces,
    subscribers,
    tags,
    time_logs,
    tree,
    utilities,
    webhooks,
]


def _collect_tools() -> dict[str, dict]:
    """Collect tool definitions from all modules."""
    tools = {}
    for module in TOOL_MODULES:
        if hasattr(module, "TOOLS"):
            for name, definition in module.TOOLS.items():
                tools[name] = definition  # noqa: PERF403 — nested conditional loop
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
    try:
        if name not in ALL_TOOLS:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])
        handler = ALL_TOOLS[name]["handler"]
        client = get_client()
        result = await handler(client, arguments)

        # Auto-strip base64 data URIs (avatars, etc.) from all responses
        if isinstance(result, (dict, list)):
            result, stripped = strip_base64(result)
            text = json.dumps(result, ensure_ascii=False, indent=2, default=str)
            if len(text) > COMPACT_JSON_THRESHOLD:
                text = json.dumps(result, ensure_ascii=False, separators=(",", ":"), default=str)
            # File-based output for oversized responses
            output_dir = os.environ.get("KAITEN_MCP_OUTPUT_DIR")
            if len(text) > FILE_OUTPUT_THRESHOLD and output_dir:
                os.makedirs(output_dir, exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(output_dir, f"{name}_{ts}.json")
                with open(file_path, "w", encoding="utf-8") as f:  # noqa: ASYNC230 — small temp file write, sub-millisecond
                    f.write(text)
                count = len(result) if isinstance(result, list) else 1
                sample = result[:3] if isinstance(result, list) else result
                summary = json.dumps(
                    {
                        "saved_to": file_path,
                        "total_items": count,
                        "size_bytes": len(text),
                        "sample": sample,
                        "tip": "Read the saved file to process data. Use 'fields' parameter to reduce response size.",
                    },
                    ensure_ascii=False,
                    separators=(",", ":"),
                    default=str,
                )
                text = summary
            if stripped:
                text += f"\n\n[Omitted {stripped} base64-encoded field(s). Data available via Kaiten web UI.]"
        else:
            text = str(result) if result is not None else "OK"
        return CallToolResult(content=[TextContent(type="text", text=text)])
    except KaitenApiError as e:
        return CallToolResult(
            content=[
                TextContent(type="text", text=f"Kaiten API Error {e.status_code}: {e.message}")
            ],
            isError=True,
        )
    except Exception as e:
        logger.exception("Unhandled error in call_tool")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")],
            isError=True,
        )


def main() -> None:
    async def run() -> None:
        try:
            async with stdio_server() as (read_stream, write_stream):
                await app.run(read_stream, write_stream, app.create_initialization_options())
        finally:
            if _client is not None:
                await _client.close()

    asyncio.run(run())


if __name__ == "__main__":
    main()
