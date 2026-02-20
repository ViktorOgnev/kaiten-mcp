"""Kaiten Custom Properties MCP tools."""
from typing import Any

from kaiten_mcp.tools.compact import DEFAULT_LIMIT

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


async def _list_custom_properties(client, args: dict) -> Any:
    params = {}
    for key in ("include_values", "types", "query", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    return await client.get("/company/custom-properties", params=params)


_tool(
    "kaiten_list_custom_properties",
    "List company custom properties. Types: string, number, date, email, checkbox, select, formula, url, collective_score, vote, collective_vote, catalog, phone, user, attachment.",
    {
        "type": "object",
        "properties": {
            "include_values": {"type": "boolean", "description": "Include select/catalog values"},
            "types": {"type": "string", "description": "Comma-separated type names to filter"},
            "query": {"type": "string", "description": "Search filter"},
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_custom_properties,
)


async def _get_custom_property(client, args: dict) -> Any:
    return await client.get(f"/company/custom-properties/{args['property_id']}")


_tool(
    "kaiten_get_custom_property",
    "Get a custom property by ID.",
    {
        "type": "object",
        "properties": {
            "property_id": {"type": "integer", "description": "Property ID"},
        },
        "required": ["property_id"],
    },
    _get_custom_property,
)


async def _create_custom_property(client, args: dict) -> Any:
    body = {"name": args["name"], "type": args["type"]}
    for key in ("show_on_facade", "multi_select", "colorful", "multiline"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.post("/company/custom-properties", json=body)


_tool(
    "kaiten_create_custom_property",
    "Create a company custom property.",
    {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Property name (1-255 chars)"},
            "type": {
                "type": "string",
                "enum": [
                    "string", "number", "date", "email", "checkbox", "select",
                    "formula", "url", "collective_score", "vote",
                    "collective_vote", "catalog", "phone", "user", "attachment",
                ],
                "description": "Property type",
            },
            "show_on_facade": {"type": "boolean", "description": "Show on card facade"},
            "multi_select": {"type": "boolean", "description": "Enable multi-select (for select type)"},
            "colorful": {"type": "boolean", "description": "Enable colors for select values"},
            "multiline": {"type": "boolean", "description": "Multiline text field"},
        },
        "required": ["name", "type"],
    },
    _create_custom_property,
)


async def _update_custom_property(client, args: dict) -> Any:
    body = {}
    for key in ("name", "condition", "show_on_facade", "multi_select", "colorful", "multiline"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(f"/company/custom-properties/{args['property_id']}", json=body)


_tool(
    "kaiten_update_custom_property",
    "Update a custom property.",
    {
        "type": "object",
        "properties": {
            "property_id": {"type": "integer", "description": "Property ID"},
            "name": {"type": "string", "description": "New name"},
            "condition": {"type": "string", "enum": ["active", "inactive"], "description": "Status"},
            "show_on_facade": {"type": "boolean", "description": "Show on card facade"},
            "multi_select": {"type": "boolean", "description": "Multi-select mode"},
            "colorful": {"type": "boolean", "description": "Enable colors"},
            "multiline": {"type": "boolean", "description": "Multiline mode"},
        },
        "required": ["property_id"],
    },
    _update_custom_property,
)


async def _delete_custom_property(client, args: dict) -> Any:
    return await client.delete(f"/company/custom-properties/{args['property_id']}")


_tool(
    "kaiten_delete_custom_property",
    "Delete (soft) a custom property.",
    {
        "type": "object",
        "properties": {
            "property_id": {"type": "integer", "description": "Property ID"},
        },
        "required": ["property_id"],
    },
    _delete_custom_property,
)


# --- Select values ---

async def _list_select_values(client, args: dict) -> Any:
    params = {}
    for key in ("query", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    return await client.get(
        f"/company/custom-properties/{args['property_id']}/select-values",
        params=params,
    )


_tool(
    "kaiten_list_select_values",
    "List select values for a custom property.",
    {
        "type": "object",
        "properties": {
            "property_id": {"type": "integer", "description": "Property ID"},
            "query": {"type": "string", "description": "Search filter"},
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
        "required": ["property_id"],
    },
    _list_select_values,
)


async def _create_select_value(client, args: dict) -> Any:
    body = {"value": args["value"]}
    for key in ("color", "sort_order"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.post(
        f"/company/custom-properties/{args['property_id']}/select-values",
        json=body,
    )


_tool(
    "kaiten_create_select_value",
    "Create a select value for a custom property.",
    {
        "type": "object",
        "properties": {
            "property_id": {"type": "integer", "description": "Property ID"},
            "value": {"type": "string", "description": "Select value text (1-255 chars)"},
            "color": {"type": "integer", "description": "Color"},
            "sort_order": {"type": "number", "description": "Sort order"},
        },
        "required": ["property_id", "value"],
    },
    _create_select_value,
)
