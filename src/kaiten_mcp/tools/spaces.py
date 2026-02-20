"""Kaiten Spaces MCP tools."""
from typing import Any

from kaiten_mcp.tools.compact import compact_response

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


async def _list_spaces(client, args: dict) -> Any:
    params = {}
    if args.get("archived") is not None:
        params["archived"] = args["archived"]
    compact = args.get("compact", False)
    result = await client.get("/spaces", params=params or None)
    return compact_response(result, compact)


_tool(
    "kaiten_list_spaces",
    "List all Kaiten spaces. Returns array of space objects with id, title, description, access type.",
    {
        "type": "object",
        "properties": {
            "archived": {"type": "boolean", "description": "Include archived spaces"},
            "compact": {"type": "boolean", "description": "Return compact response without heavy fields (avatars, nested user objects)", "default": False},
        },
    },
    _list_spaces,
)


async def _get_space(client, args: dict) -> Any:
    return await client.get(f"/spaces/{args['space_id']}")


_tool(
    "kaiten_get_space",
    "Get a Kaiten space by ID.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
        },
        "required": ["space_id"],
    },
    _get_space,
)


async def _create_space(client, args: dict) -> Any:
    body = {"title": args["title"]}
    for key in ("description", "access", "external_id", "parent_entity_uid"):
        if args.get(key) is not None:
            body[key] = args[key]
    for key in ("sort_order",):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.post("/spaces", json=body)


_tool(
    "kaiten_create_space",
    "Create a new Kaiten space.",
    {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Space title"},
            "description": {"type": "string", "description": "Space description"},
            "access": {
                "type": "string",
                "enum": ["for_everyone", "by_invite"],
                "description": "Access type (default: for_everyone)",
            },
            "external_id": {"type": "string", "description": "External ID"},
            "parent_entity_uid": {"type": "string", "description": "Parent entity UID for nesting spaces"},
            "sort_order": {"type": "number", "description": "Sort order"},
        },
        "required": ["title"],
    },
    _create_space,
)


async def _update_space(client, args: dict) -> Any:
    body = {}
    for key in ("title", "description", "access", "external_id", "parent_entity_uid"):
        if args.get(key) is not None:
            body[key] = args[key]
    for key in ("sort_order",):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(f"/spaces/{args['space_id']}", json=body)


_tool(
    "kaiten_update_space",
    "Update a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "title": {"type": "string", "description": "New title"},
            "description": {"type": "string", "description": "New description"},
            "access": {
                "type": "string",
                "enum": ["for_everyone", "by_invite"],
                "description": "Access type",
            },
            "external_id": {"type": "string", "description": "External ID"},
            "parent_entity_uid": {"type": "string", "description": "Parent entity UID for nesting spaces"},
            "sort_order": {"type": "number", "description": "Sort order"},
        },
        "required": ["space_id"],
    },
    _update_space,
)


async def _delete_space(client, args: dict) -> Any:
    return await client.delete(f"/spaces/{args['space_id']}")


_tool(
    "kaiten_delete_space",
    "Delete a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
        },
        "required": ["space_id"],
    },
    _delete_space,
)
