"""Kaiten Webhooks MCP tools."""
from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# --- External Webhooks (outbound event notifications) ---

async def _list_webhooks(client, args: dict) -> Any:
    return await client.get(f"/spaces/{args['space_id']}/external-webhooks")


_tool(
    "kaiten_list_webhooks",
    "List all external webhooks (outbound event notifications) for a Kaiten space. Only 1 external webhook per space is allowed.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
        },
        "required": ["space_id"],
    },
    _list_webhooks,
)


async def _create_webhook(client, args: dict) -> Any:
    body: dict[str, Any] = {"url": args["url"]}
    return await client.post(f"/spaces/{args['space_id']}/external-webhooks", json=body)


_tool(
    "kaiten_create_webhook",
    "Create an external webhook (outbound event notification) for a Kaiten space. Only 1 per space allowed; URL max 4096 chars. Requires webhooks paid feature.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "url": {"type": "string", "description": "Webhook URL to receive events (max 4096 chars)"},
        },
        "required": ["space_id", "url"],
    },
    _create_webhook,
)


async def _get_webhook(client, args: dict) -> Any:
    return await client.get(
        f"/spaces/{args['space_id']}/external-webhooks/{args['webhook_id']}"
    )


_tool(
    "kaiten_get_webhook",
    "Get a specific external webhook for a Kaiten space. Note: GET by ID may return 405; use kaiten_list_webhooks instead.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "webhook_id": {"type": "integer", "description": "Webhook ID"},
        },
        "required": ["space_id", "webhook_id"],
    },
    _get_webhook,
)


async def _update_webhook(client, args: dict) -> Any:
    body: dict[str, Any] = {}
    if args.get("url") is not None:
        body["url"] = args["url"]
    if args.get("enabled") is not None:
        body["enabled"] = args["enabled"]
    return await client.patch(
        f"/spaces/{args['space_id']}/external-webhooks/{args['webhook_id']}", json=body
    )


_tool(
    "kaiten_update_webhook",
    "Update an external webhook for a Kaiten space. Can change URL and enable/disable.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "webhook_id": {"type": "integer", "description": "Webhook ID"},
            "url": {"type": "string", "description": "Webhook URL to receive events (max 4096 chars)"},
            "enabled": {"type": "boolean", "description": "Whether the webhook is enabled"},
        },
        "required": ["space_id", "webhook_id"],
    },
    _update_webhook,
)


async def _delete_webhook(client, args: dict) -> Any:
    return await client.delete(
        f"/spaces/{args['space_id']}/external-webhooks/{args['webhook_id']}"
    )


_tool(
    "kaiten_delete_webhook",
    "Delete an external webhook from a Kaiten space. Note: DELETE may return 405; webhook removal may not be supported via API.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "webhook_id": {"type": "integer", "description": "Webhook ID"},
        },
        "required": ["space_id", "webhook_id"],
    },
    _delete_webhook,
)


# --- Incoming Webhooks (card-creation webhooks) ---

async def _list_incoming_webhooks(client, args: dict) -> Any:
    return await client.get(f"/spaces/{args['space_id']}/webhooks")


_tool(
    "kaiten_list_incoming_webhooks",
    "List all incoming (card-creation) webhooks for a Kaiten space. These webhooks accept external payloads and create cards.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
        },
        "required": ["space_id"],
    },
    _list_incoming_webhooks,
)


async def _create_incoming_webhook(client, args: dict) -> Any:
    body: dict[str, Any] = {
        "board_id": args["board_id"],
        "column_id": args["column_id"],
        "lane_id": args["lane_id"],
        "owner_id": args["owner_id"],
    }
    for key in ("type_id", "position", "format"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.post(f"/spaces/{args['space_id']}/webhooks", json=body)


_tool(
    "kaiten_create_incoming_webhook",
    "Create an incoming (card-creation) webhook for a Kaiten space. Requires webhooks paid feature. Cards created via this webhook will be placed at the specified board/column/lane.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "board_id": {"type": "integer", "description": "Board ID where cards will be created"},
            "column_id": {"type": "integer", "description": "Column ID for new cards"},
            "lane_id": {"type": "integer", "description": "Lane ID for new cards"},
            "owner_id": {"type": "integer", "description": "User ID who will be the card owner"},
            "type_id": {"type": "integer", "description": "Card type ID. Default: 1"},
            "position": {
                "type": "integer",
                "description": "Position of new cards in the column (0=first, 1=last). Default: last",
            },
            "format": {
                "type": "integer",
                "enum": [1, 2, 3, 4, 5, 6, 7],
                "description": (
                    "Payload format: 1=kaiten (default), 2=jira, 3=airbrake, "
                    "4=sentry, 5=crashlytics, 6=tilda, 7=google_forms"
                ),
            },
        },
        "required": ["space_id", "board_id", "column_id", "lane_id", "owner_id"],
    },
    _create_incoming_webhook,
)


async def _update_incoming_webhook(client, args: dict) -> Any:
    body: dict[str, Any] = {}
    for key in ("board_id", "column_id", "lane_id", "owner_id", "type_id", "position", "format"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(
        f"/spaces/{args['space_id']}/webhooks/{args['webhook_id']}", json=body
    )


_tool(
    "kaiten_update_incoming_webhook",
    "Update an incoming (card-creation) webhook in a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "webhook_id": {"type": "string", "description": "Webhook ID (128-char hash string)"},
            "board_id": {"type": "integer", "description": "Board ID where cards will be created"},
            "column_id": {"type": "integer", "description": "Column ID for new cards"},
            "lane_id": {"type": "integer", "description": "Lane ID for new cards"},
            "owner_id": {"type": "integer", "description": "User ID who will be the card owner"},
            "type_id": {"type": "integer", "description": "Card type ID"},
            "position": {
                "type": "integer",
                "description": "Position of new cards in the column (0=first, 1=last)",
            },
            "format": {
                "type": "integer",
                "enum": [1, 2, 3, 4, 5, 6, 7],
                "description": (
                    "Payload format: 1=kaiten, 2=jira, 3=airbrake, "
                    "4=sentry, 5=crashlytics, 6=tilda, 7=google_forms"
                ),
            },
        },
        "required": ["space_id", "webhook_id"],
    },
    _update_incoming_webhook,
)


async def _delete_incoming_webhook(client, args: dict) -> Any:
    return await client.delete(
        f"/spaces/{args['space_id']}/webhooks/{args['webhook_id']}"
    )


_tool(
    "kaiten_delete_incoming_webhook",
    "Delete an incoming (card-creation) webhook from a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "webhook_id": {"type": "string", "description": "Webhook ID (128-char hash string)"},
        },
        "required": ["space_id", "webhook_id"],
    },
    _delete_incoming_webhook,
)
