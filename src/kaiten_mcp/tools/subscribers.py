"""Kaiten Card Subscribers MCP tools."""
from typing import Any

from kaiten_mcp.tools.compact import compact_response

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# ---------------------------------------------------------------------------
# Card Subscribers
# ---------------------------------------------------------------------------

async def _list_card_subscribers(client, args: dict) -> Any:
    compact = args.get("compact", False)
    result = await client.get(f"/cards/{args['card_id']}/subscribers")
    return compact_response(result, compact)


_tool(
    "kaiten_list_card_subscribers",
    "List all subscribers (watchers) of a Kaiten card. Note: may return 405; subscriber listing may not be available.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
            "compact": {"type": "boolean", "description": "Return compact response without heavy fields (avatars, nested user objects).", "default": False},
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
    compact = args.get("compact", False)
    result = await client.get(f"/columns/{args['column_id']}/subscribers")
    return compact_response(result, compact)


_tool(
    "kaiten_list_column_subscribers",
    "List all subscribers of a Kaiten column. Note: may return 405; subscriber listing may not be available.",
    {
        "type": "object",
        "properties": {
            "column_id": {"type": "integer", "description": "Column ID"},
            "compact": {"type": "boolean", "description": "Return compact response without heavy fields (avatars, nested user objects).", "default": False},
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
