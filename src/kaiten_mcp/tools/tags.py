"""Kaiten Tags MCP tools."""
from typing import Any

from kaiten_mcp.tools.compact import DEFAULT_LIMIT

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


async def _list_tags(client, args: dict) -> Any:
    params = {}
    for key in ("query", "offset", "space_id"):
        if args.get(key) is not None:
            params[key] = args[key]
    if args.get("ids") is not None:
        params["ids"] = args["ids"]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    return await client.get("/tags", params=params)


_tool(
    "kaiten_list_tags",
    "List Kaiten tags. Note: API may return empty for company-level tags; tags are primarily card-scoped.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search filter (matches by name)"},
            "space_id": {"type": "integer", "description": "Filter tags by space (only tags used on cards in this space)"},
            "ids": {"type": "string", "description": "Comma-separated tag IDs to fetch specific tags"},
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_tags,
)


async def _create_tag(client, args: dict) -> Any:
    body = {"name": args["name"]}
    return await client.post("/tags", json=body)


_tool(
    "kaiten_create_tag",
    "Create a new Kaiten tag. Color is assigned randomly by the server (1-17).",
    {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Tag name (1-255 chars, must be unique within the company)"},
        },
        "required": ["name"],
    },
    _create_tag,
)


async def _update_tag(client, args: dict) -> Any:
    body = {}
    for key in ("name",):
        if args.get(key) is not None:
            body[key] = args[key]
    if args.get("color") is not None:
        body["color"] = args["color"]
    return await client.patch(f"/company/tags/{args['tag_id']}", json=body)


_tool(
    "kaiten_update_tag",
    "Update a Kaiten tag (name and/or color). Requires company tag management permission.",
    {
        "type": "object",
        "properties": {
            "tag_id": {"type": "integer", "description": "Tag ID"},
            "name": {"type": "string", "description": "New tag name (1-255 chars)"},
            "color": {"type": "integer", "description": "Color index (1-17)", "minimum": 1, "maximum": 17},
        },
        "required": ["tag_id"],
    },
    _update_tag,
)


async def _delete_tag(client, args: dict) -> Any:
    return await client.delete(f"/company/tags/{args['tag_id']}")


_tool(
    "kaiten_delete_tag",
    "Delete a Kaiten tag. Requires company tag management permission. May be blocked if an async operation is in progress.",
    {
        "type": "object",
        "properties": {
            "tag_id": {"type": "integer", "description": "Tag ID"},
        },
        "required": ["tag_id"],
    },
    _delete_tag,
)


# --- Card-level tags ---

async def _add_card_tag(client, args: dict) -> Any:
    return await client.post(
        f"/cards/{args['card_id']}/tags", json={"name": args["name"]}
    )


_tool(
    "kaiten_add_card_tag",
    "Add a tag to a Kaiten card by name. Creates the tag if it doesn't exist.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
            "name": {"type": "string", "description": "Tag name (1-255 chars)"},
        },
        "required": ["card_id", "name"],
    },
    _add_card_tag,
)


async def _remove_card_tag(client, args: dict) -> Any:
    return await client.delete(f"/cards/{args['card_id']}/tags/{args['tag_id']}")


_tool(
    "kaiten_remove_card_tag",
    "Remove a tag from a Kaiten card.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
            "tag_id": {"type": "integer", "description": "Tag ID"},
        },
        "required": ["card_id", "tag_id"],
    },
    _remove_card_tag,
)
