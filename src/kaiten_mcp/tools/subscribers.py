"""Kaiten Card Subscribers MCP tools."""
from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# ---------------------------------------------------------------------------
# Card Subscribers
# ---------------------------------------------------------------------------

async def _list_card_subscribers(client, args: dict) -> Any:
    return await client.get(f"/cards/{args['card_id']}/subscribers")


_tool(
    "kaiten_list_card_subscribers",
    "List all subscribers (watchers) of a Kaiten card. Note: may return 405; subscriber listing may not be available.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
        },
        "required": ["card_id"],
    },
    _list_card_subscribers,
)


async def _add_card_subscriber(client, args: dict) -> Any:
    return await client.post(
        f"/cards/{args['card_id']}/subscribers", json={"user_id": args["user_id"]}
    )


_tool(
    "kaiten_add_card_subscriber",
    "Add a subscriber (watcher) to a Kaiten card.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
            "user_id": {"type": "integer", "description": "User ID to subscribe"},
        },
        "required": ["card_id", "user_id"],
    },
    _add_card_subscriber,
)


async def _remove_card_subscriber(client, args: dict) -> Any:
    return await client.delete(
        f"/cards/{args['card_id']}/subscribers/{args['user_id']}"
    )


_tool(
    "kaiten_remove_card_subscriber",
    "Remove a subscriber (watcher) from a Kaiten card.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
            "user_id": {"type": "integer", "description": "User ID to unsubscribe"},
        },
        "required": ["card_id", "user_id"],
    },
    _remove_card_subscriber,
)


# ---------------------------------------------------------------------------
# Column Subscribers
# ---------------------------------------------------------------------------

async def _list_column_subscribers(client, args: dict) -> Any:
    return await client.get(f"/columns/{args['column_id']}/subscribers")


_tool(
    "kaiten_list_column_subscribers",
    "List all subscribers of a Kaiten column. Note: may return 405; subscriber listing may not be available.",
    {
        "type": "object",
        "properties": {
            "column_id": {"type": "integer", "description": "Column ID"},
        },
        "required": ["column_id"],
    },
    _list_column_subscribers,
)


async def _add_column_subscriber(client, args: dict) -> Any:
    body = {"user_id": args["user_id"]}
    if args.get("type") is not None:
        body["type"] = args["type"]
    else:
        body["type"] = 1  # default: all notifications
    return await client.post(
        f"/columns/{args['column_id']}/subscribers", json=body
    )


_tool(
    "kaiten_add_column_subscriber",
    "Add a subscriber to a Kaiten column.",
    {
        "type": "object",
        "properties": {
            "column_id": {"type": "integer", "description": "Column ID"},
            "user_id": {"type": "integer", "description": "User ID to subscribe"},
            "type": {"type": "integer", "description": "Subscription type (1=all, 2=mentions only). Default: 1"},
        },
        "required": ["column_id", "user_id"],
    },
    _add_column_subscriber,
)


async def _remove_column_subscriber(client, args: dict) -> Any:
    return await client.delete(
        f"/columns/{args['column_id']}/subscribers/{args['user_id']}"
    )


_tool(
    "kaiten_remove_column_subscriber",
    "Remove a subscriber from a Kaiten column.",
    {
        "type": "object",
        "properties": {
            "column_id": {"type": "integer", "description": "Column ID"},
            "user_id": {"type": "integer", "description": "User ID to unsubscribe"},
        },
        "required": ["column_id", "user_id"],
    },
    _remove_column_subscriber,
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
    for key in ("sort_order", "wip_limit"):
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
        },
        "required": ["column_id", "title"],
    },
    _create_subcolumn,
)


async def _update_subcolumn(client, args: dict) -> Any:
    body = {}
    for key in ("title", "sort_order", "wip_limit"):
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
