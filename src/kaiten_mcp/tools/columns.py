"""Kaiten Columns MCP tools."""
from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


async def _list_columns(client, args: dict) -> Any:
    return await client.get(f"/boards/{args['board_id']}/columns")


_tool(
    "kaiten_list_columns",
    "List columns on a Kaiten board. Column types: 1=queue, 2=in_progress, 3=done.",
    {
        "type": "object",
        "properties": {
            "board_id": {"type": "integer", "description": "Board ID"},
        },
        "required": ["board_id"],
    },
    _list_columns,
)


async def _create_column(client, args: dict) -> Any:
    body = {"title": args["title"], "type": args["type"]}
    for key in ("wip_limit", "sort_order"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.post(f"/boards/{args['board_id']}/columns", json=body)


_tool(
    "kaiten_create_column",
    "Create a column on a Kaiten board. Type: 1=queue, 2=in_progress, 3=done.",
    {
        "type": "object",
        "properties": {
            "board_id": {"type": "integer", "description": "Board ID"},
            "title": {"type": "string", "description": "Column title"},
            "type": {
                "type": "integer",
                "enum": [1, 2, 3],
                "description": "Column type: 1=queue, 2=in_progress, 3=done",
            },
            "wip_limit": {"type": "integer", "description": "WIP limit (optional)"},
            "sort_order": {"type": "number", "description": "Sort order"},
        },
        "required": ["board_id", "title", "type"],
    },
    _create_column,
)


async def _update_column(client, args: dict) -> Any:
    body = {}
    for key in ("title", "type", "wip_limit", "sort_order"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(
        f"/boards/{args['board_id']}/columns/{args['column_id']}", json=body
    )


_tool(
    "kaiten_update_column",
    "Update a column on a Kaiten board.",
    {
        "type": "object",
        "properties": {
            "board_id": {"type": "integer", "description": "Board ID"},
            "column_id": {"type": "integer", "description": "Column ID"},
            "title": {"type": "string", "description": "New title"},
            "type": {"type": "integer", "enum": [1, 2, 3], "description": "Column type"},
            "wip_limit": {"type": "integer", "description": "WIP limit"},
            "sort_order": {"type": "number", "description": "Sort order"},
        },
        "required": ["board_id", "column_id"],
    },
    _update_column,
)


async def _delete_column(client, args: dict) -> Any:
    return await client.delete(
        f"/boards/{args['board_id']}/columns/{args['column_id']}"
    )


_tool(
    "kaiten_delete_column",
    "Delete a column from a Kaiten board.",
    {
        "type": "object",
        "properties": {
            "board_id": {"type": "integer", "description": "Board ID"},
            "column_id": {"type": "integer", "description": "Column ID"},
        },
        "required": ["board_id", "column_id"],
    },
    _delete_column,
)
