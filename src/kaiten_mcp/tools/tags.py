"""Kaiten Tags MCP tools."""
from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


async def _list_tags(client, args: dict) -> Any:
    params = {}
    for key in ("query", "limit", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get("/tags", params=params or None)


_tool(
    "kaiten_list_tags",
    "List Kaiten tags. Note: API may return empty for company-level tags; tags are primarily card-scoped.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search filter"},
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_tags,
)


async def _create_tag(client, args: dict) -> Any:
    body = {"name": args["name"]}
    if args.get("color") is not None:
        body["color"] = args["color"]
    return await client.post("/tags", json=body)


_tool(
    "kaiten_create_tag",
    "Create a new Kaiten tag.",
    {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Tag name"},
            "color": {"type": "string", "description": "Color in HEX format (e.g. #FF0000)"},
        },
        "required": ["name"],
    },
    _create_tag,
)


async def _delete_tag(client, args: dict) -> Any:
    return await client.delete(f"/tags/{args['tag_id']}")


_tool(
    "kaiten_delete_tag",
    "Delete a Kaiten tag.",
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
