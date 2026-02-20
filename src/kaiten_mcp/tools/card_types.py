"""Kaiten Card Types MCP tools."""

from typing import Any

from kaiten_mcp.tools.compact import DEFAULT_LIMIT

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


async def _list_card_types(client, args: dict) -> Any:
    params = {}
    for key in ("query", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    return await client.get("/card-types", params=params)


_tool(
    "kaiten_list_card_types",
    "List Kaiten card types.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search filter"},
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_card_types,
)


async def _get_card_type(client, args: dict) -> Any:
    return await client.get(f"/card-types/{args['type_id']}")


_tool(
    "kaiten_get_card_type",
    "Get a Kaiten card type by ID.",
    {
        "type": "object",
        "properties": {
            "type_id": {"type": "integer", "description": "Card type ID"},
        },
        "required": ["type_id"],
    },
    _get_card_type,
)


async def _create_card_type(client, args: dict) -> Any:
    body = {
        "name": args["name"],
        "letter": args["letter"],
        "color": args["color"],
    }
    if args.get("description_template") is not None:
        body["description_template"] = args["description_template"]
    return await client.post("/card-types", json=body)


_tool(
    "kaiten_create_card_type",
    "Create a Kaiten card type. Color must be integer 2-25 (1 is reserved for default).",
    {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Type name (1-64 chars)"},
            "letter": {"type": "string", "description": "Single letter or emoji"},
            "color": {"type": "integer", "description": "Color (2-25)"},
            "description_template": {
                "type": "string",
                "description": "Template for card description",
            },
        },
        "required": ["name", "letter", "color"],
    },
    _create_card_type,
)


async def _update_card_type(client, args: dict) -> Any:
    body = {}
    for key in ("name", "letter", "color", "description_template"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(f"/card-types/{args['type_id']}", json=body)


_tool(
    "kaiten_update_card_type",
    "Update a Kaiten card type.",
    {
        "type": "object",
        "properties": {
            "type_id": {"type": "integer", "description": "Card type ID"},
            "name": {"type": "string", "description": "New name"},
            "letter": {"type": "string", "description": "New letter"},
            "color": {"type": "integer", "description": "New color (2-25)"},
            "description_template": {"type": "string", "description": "Description template"},
        },
        "required": ["type_id"],
    },
    _update_card_type,
)


async def _delete_card_type(client, args: dict) -> Any:
    body: dict[str, Any] = {}
    if args.get("replace_type_id") is not None:
        body["replace_type_id"] = args["replace_type_id"]
    for key in (
        "has_to_replace_in_automation",
        "has_to_replace_in_restriction",
        "has_to_replace_in_workflow",
    ):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.delete(f"/card-types/{args['type_id']}", json=body or None)


_tool(
    "kaiten_delete_card_type",
    "Delete a Kaiten card type. Requires replace_type_id — the substitute type to "
    "reassign existing cards to. Without it the API returns 500.",
    {
        "type": "object",
        "properties": {
            "type_id": {"type": "integer", "description": "Card type ID to delete"},
            "replace_type_id": {
                "type": "integer",
                "description": "Card type ID to reassign cards to (required by Kaiten API)",
            },
            "has_to_replace_in_automation": {
                "type": "boolean",
                "description": "Replace this type in automations (default: false)",
            },
            "has_to_replace_in_restriction": {
                "type": "boolean",
                "description": "Replace this type in column restrictions (default: false)",
            },
            "has_to_replace_in_workflow": {
                "type": "boolean",
                "description": "Replace this type in workflows (default: false)",
            },
        },
        "required": ["type_id", "replace_type_id"],
    },
    _delete_card_type,
)
