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
    for key in ("wip_limit", "wip_limit_type", "col_count", "sort_order"):
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
            "wip_limit": {"type": "integer", "description": "WIP limit"},
            "wip_limit_type": {"type": "integer", "description": "WIP limit type (1=cards count, 2=size sum)"},
            "col_count": {"type": "integer", "description": "Number of sub-columns to split into"},
            "sort_order": {"type": "number", "description": "Sort order"},
        },
        "required": ["board_id", "title", "type"],
    },
    _create_column,
)


async def _update_column(client, args: dict) -> Any:
    body = {}
    for key in ("title", "type", "wip_limit", "wip_limit_type", "col_count", "sort_order"):
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
            "wip_limit_type": {"type": "integer", "description": "WIP limit type (1=cards count, 2=size sum)"},
            "col_count": {"type": "integer", "description": "Number of sub-columns to split into"},
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


# ---------------------------------------------------------------------------
# Subcolumns
# ---------------------------------------------------------------------------

async def _list_subcolumns(client, args: dict) -> Any:
    return await client.get(f"/columns/{args['column_id']}/subcolumns")


_tool(
    "kaiten_list_subcolumns",
    "List all subcolumns of a Kaiten column.",
    {
        "type": "object",
        "properties": {
            "column_id": {"type": "integer", "description": "Column ID"},
        },
        "required": ["column_id"],
    },
    _list_subcolumns,
)


async def _create_subcolumn(client, args: dict) -> Any:
    body = {"title": args["title"]}
    for key in ("sort_order", "wip_limit", "col_count"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.post(f"/columns/{args['column_id']}/subcolumns", json=body)


_tool(
    "kaiten_create_subcolumn",
    "Create a subcolumn inside a Kaiten column.",
    {
        "type": "object",
        "properties": {
            "column_id": {"type": "integer", "description": "Column ID"},
            "title": {"type": "string", "description": "Subcolumn title"},
            "sort_order": {"type": "number", "description": "Sort order"},
            "wip_limit": {"type": "integer", "description": "WIP limit"},
            "col_count": {"type": "integer", "description": "Number of sub-columns to split into"},
        },
        "required": ["column_id", "title"],
    },
    _create_subcolumn,
)


async def _update_subcolumn(client, args: dict) -> Any:
    body = {}
    for key in ("title", "sort_order", "wip_limit", "col_count"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(
        f"/columns/{args['column_id']}/subcolumns/{args['subcolumn_id']}", json=body
    )


_tool(
    "kaiten_update_subcolumn",
    "Update a subcolumn of a Kaiten column.",
    {
        "type": "object",
        "properties": {
            "column_id": {"type": "integer", "description": "Column ID"},
            "subcolumn_id": {"type": "integer", "description": "Subcolumn ID"},
            "title": {"type": "string", "description": "New title"},
            "sort_order": {"type": "number", "description": "Sort order"},
            "wip_limit": {"type": "integer", "description": "WIP limit"},
            "col_count": {"type": "integer", "description": "Number of sub-columns to split into"},
        },
        "required": ["column_id", "subcolumn_id"],
    },
    _update_subcolumn,
)


async def _delete_subcolumn(client, args: dict) -> Any:
    return await client.delete(
        f"/columns/{args['column_id']}/subcolumns/{args['subcolumn_id']}"
    )


_tool(
    "kaiten_delete_subcolumn",
    "Delete a subcolumn from a Kaiten column.",
    {
        "type": "object",
        "properties": {
            "column_id": {"type": "integer", "description": "Column ID"},
            "subcolumn_id": {"type": "integer", "description": "Subcolumn ID"},
        },
        "required": ["column_id", "subcolumn_id"],
    },
    _delete_subcolumn,
)
