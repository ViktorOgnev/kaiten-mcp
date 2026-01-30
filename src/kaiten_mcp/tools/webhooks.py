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
    "List all external webhooks for a Kaiten space.",
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
    "Create an external webhook for a Kaiten space. Only 'url' is accepted on create.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "url": {"type": "string", "description": "Webhook URL to receive events"},
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
    "Update an external webhook for a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "webhook_id": {"type": "integer", "description": "Webhook ID"},
            "url": {"type": "string", "description": "Webhook URL to receive events"},
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
