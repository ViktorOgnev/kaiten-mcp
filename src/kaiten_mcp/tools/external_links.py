"""Kaiten External Links MCP tools."""
from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# --- Card External Links ---

async def _list_external_links(client, args: dict) -> Any:
    return await client.get(f"/cards/{args['card_id']}/external-links")


_tool(
    "kaiten_list_external_links",
    "List all external links on a Kaiten card.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
        },
        "required": ["card_id"],
    },
    _list_external_links,
)


async def _create_external_link(client, args: dict) -> Any:
    body = {"url": args["url"]}
    if args.get("description") is not None:
        body["description"] = args["description"]
    return await client.post(f"/cards/{args['card_id']}/external-links", json=body)


_tool(
    "kaiten_create_external_link",
    "Create an external link on a Kaiten card.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
            "url": {"type": "string", "description": "URL of the external link"},
            "description": {"type": "string", "description": "Description of the external link"},
        },
        "required": ["card_id", "url"],
    },
    _create_external_link,
)


async def _update_external_link(client, args: dict) -> Any:
    body = {}
    if args.get("url") is not None:
        body["url"] = args["url"]
    if args.get("description") is not None:
        body["description"] = args["description"]
    return await client.patch(
        f"/cards/{args['card_id']}/external-links/{args['link_id']}", json=body
    )


_tool(
    "kaiten_update_external_link",
    "Update an external link on a Kaiten card.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
            "link_id": {"type": "integer", "description": "External link ID"},
            "url": {"type": "string", "description": "URL of the external link"},
            "description": {"type": "string", "description": "Description of the external link"},
        },
        "required": ["card_id", "link_id"],
    },
    _update_external_link,
)


async def _delete_external_link(client, args: dict) -> Any:
    return await client.delete(
        f"/cards/{args['card_id']}/external-links/{args['link_id']}"
    )


_tool(
    "kaiten_delete_external_link",
    "Delete an external link from a Kaiten card.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
            "link_id": {"type": "integer", "description": "External link ID"},
        },
        "required": ["card_id", "link_id"],
    },
    _delete_external_link,
)
