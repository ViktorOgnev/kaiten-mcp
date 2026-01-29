"""Kaiten Boards MCP tools."""
from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


async def _list_boards(client, args: dict) -> Any:
    return await client.get(f"/spaces/{args['space_id']}/boards")


_tool(
    "kaiten_list_boards",
    "List boards in a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
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
    if args.get("description") is not None:
        body["description"] = args["description"]
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
        },
        "required": ["space_id", "title"],
    },
    _create_board,
)


async def _update_board(client, args: dict) -> Any:
    body = {}
    for key in ("title", "description"):
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
