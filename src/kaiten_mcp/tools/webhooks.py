"""Kaiten Webhooks MCP tools."""
from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# --- Space Webhooks ---

async def _list_webhooks(client, args: dict) -> Any:
    return await client.get(f"/spaces/{args['space_id']}/webhooks")


_tool(
    "kaiten_list_webhooks",
    "List all webhooks for a Kaiten space.",
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
    body = {"url": args["url"]}
    if args.get("events") is not None:
        body["events"] = args["events"]
    if args.get("active") is not None:
        body["active"] = args["active"]
    return await client.post(f"/spaces/{args['space_id']}/webhooks", json=body)


_tool(
    "kaiten_create_webhook",
    "Create a webhook for a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "url": {"type": "string", "description": "Webhook URL to receive events"},
            "events": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of event types to subscribe to",
            },
            "active": {"type": "boolean", "description": "Whether the webhook is active"},
        },
        "required": ["space_id", "url"],
    },
    _create_webhook,
)


async def _get_webhook(client, args: dict) -> Any:
    return await client.get(
        f"/spaces/{args['space_id']}/webhooks/{args['webhook_id']}"
    )


_tool(
    "kaiten_get_webhook",
    "Get a specific webhook for a Kaiten space.",
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
    body = {}
    if args.get("url") is not None:
        body["url"] = args["url"]
    if args.get("events") is not None:
        body["events"] = args["events"]
    if args.get("active") is not None:
        body["active"] = args["active"]
    return await client.patch(
        f"/spaces/{args['space_id']}/webhooks/{args['webhook_id']}", json=body
    )


_tool(
    "kaiten_update_webhook",
    "Update a webhook for a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "webhook_id": {"type": "integer", "description": "Webhook ID"},
            "url": {"type": "string", "description": "Webhook URL to receive events"},
            "events": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of event types to subscribe to",
            },
            "active": {"type": "boolean", "description": "Whether the webhook is active"},
        },
        "required": ["space_id", "webhook_id"],
    },
    _update_webhook,
)


async def _delete_webhook(client, args: dict) -> Any:
    return await client.delete(
        f"/spaces/{args['space_id']}/webhooks/{args['webhook_id']}"
    )


_tool(
    "kaiten_delete_webhook",
    "Delete a webhook from a Kaiten space.",
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
