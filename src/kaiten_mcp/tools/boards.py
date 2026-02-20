"""Kaiten Boards MCP tools."""
from typing import Any

from kaiten_mcp.tools.compact import compact_response

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


async def _list_boards(client, args: dict) -> Any:
    compact = args.get("compact", False)
    result = await client.get(f"/spaces/{args['space_id']}/boards")
    return compact_response(result, compact)


_tool(
    "kaiten_list_boards",
    "List boards in a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "compact": {"type": "boolean", "description": "Return compact response without heavy fields (avatars, nested user objects)", "default": False},
        },
        "required": ["space_id"],
    },
    _list_boards,
)


async def _get_board(client, args: dict) -> Any:
    return await client.get(f"/boards/{args['board_id']}")


_tool(
    "kaiten_get_board",
    "Get a Kaiten board by ID. Returns board with columns and lanes.",
    {
        "type": "object",
        "properties": {
            "board_id": {"type": "integer", "description": "Board ID"},
        },
        "required": ["board_id"],
    },
    _get_board,
)


async def _create_board(client, args: dict) -> Any:
    body = {"title": args["title"]}
    for key in ("description", "external_id"):
        if args.get(key) is not None:
            body[key] = args[key]
    for key in ("top", "left", "sort_order", "default_card_type_id"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.post(f"/spaces/{args['space_id']}/boards", json=body)


_tool(
    "kaiten_create_board",
    "Create a new board in a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "title": {"type": "string", "description": "Board title"},
            "description": {"type": "string", "description": "Board description"},
            "external_id": {"type": "string", "description": "External ID"},
            "top": {"type": "number", "description": "Top position (px)"},
            "left": {"type": "number", "description": "Left position (px)"},
            "sort_order": {"type": "number", "description": "Sort order"},
            "default_card_type_id": {"type": "integer", "description": "Default card type ID for new cards"},
        },
        "required": ["space_id", "title"],
    },
    _create_board,
)


async def _update_board(client, args: dict) -> Any:
    body = {}
    for key in ("title", "description", "external_id"):
        if args.get(key) is not None:
            body[key] = args[key]
    for key in ("top", "left", "sort_order", "default_card_type_id"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(
        f"/spaces/{args['space_id']}/boards/{args['board_id']}", json=body
    )


_tool(
    "kaiten_update_board",
    "Update a Kaiten board.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "board_id": {"type": "integer", "description": "Board ID"},
            "title": {"type": "string", "description": "New title"},
            "description": {"type": "string", "description": "New description"},
            "external_id": {"type": "string", "description": "External ID"},
            "top": {"type": "number", "description": "Top position (px)"},
            "left": {"type": "number", "description": "Left position (px)"},
            "sort_order": {"type": "number", "description": "Sort order"},
            "default_card_type_id": {"type": "integer", "description": "Default card type ID for new cards"},
        },
        "required": ["space_id", "board_id"],
    },
    _update_board,
)


async def _delete_board(client, args: dict) -> Any:
    return await client.delete(
        f"/spaces/{args['space_id']}/boards/{args['board_id']}"
    )


_tool(
    "kaiten_delete_board",
    "Delete a Kaiten board.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "board_id": {"type": "integer", "description": "Board ID"},
        },
        "required": ["space_id", "board_id"],
    },
    _delete_board,
)
