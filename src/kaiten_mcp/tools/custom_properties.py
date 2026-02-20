"""Kaiten Custom Properties MCP tools."""
from typing import Any

from kaiten_mcp.tools.compact import DEFAULT_LIMIT

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


async def _list_custom_properties(client, args: dict) -> Any:
    params = {}
    for key in ("include_values", "include_author", "types", "conditions",
                "query", "offset", "order_by", "order_direction", "board_id"):
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
            "include_author": {"type": "boolean", "description": "Include author user object"},
            "types": {"type": "string", "description": "Comma-separated type names to filter"},
            "conditions": {
                "type": "string",
                "description": "Comma-separated conditions to filter: active, inactive (default: active,inactive)",
            },
            "query": {"type": "string", "description": "Search filter by name"},
            "order_by": {
                "type": "string",
                "description": "Column to sort by (e.g. 'name', 'created', 'updated')",
            },
            "order_direction": {
                "type": "string",
                "description": "Sort direction (asc or desc), matches order_by columns",
            },
            "board_id": {
                "type": "integer",
                "description": "Filter properties available on a specific board",
            },
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
    for key in ("show_on_facade", "multi_select", "colorful", "multiline",
                "values_creatable_by_users"):
        if args.get(key) is not None:
            body[key] = args[key]
    for key in ("values_type", "vote_variant"):
        if args.get(key) is not None:
            body[key] = args[key]
    if args.get("color") is not None:
        body["color"] = args["color"]
    if "data" in args:
        body["data"] = args["data"]
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
            "multiline": {"type": "boolean", "description": "Multiline text field (for string type)"},
            "values_creatable_by_users": {
                "type": "boolean",
                "description": "Allow regular users to create new select values (for select type)",
            },
            "values_type": {
                "type": "string",
                "enum": ["number", "text"],
                "description": "Values type (required for collective_score type)",
            },
            "vote_variant": {
                "type": "string",
                "enum": ["rating", "scale", "emoji_set"],
                "description": "Vote variant (required for vote/collective_vote types)",
            },
            "color": {"type": "integer", "description": "Color index"},
            "data": {
                "type": "object",
                "description": "Type-specific data (e.g. restrictions {min, max} for number, {minLength, maxLength} for string; vote scale config for vote types)",
            },
        },
        "required": ["name", "type"],
    },
    _create_custom_property,
)


async def _update_custom_property(client, args: dict) -> Any:
    body = {}
    for key in ("name", "condition"):
        if args.get(key) is not None:
            body[key] = args[key]
    for key in ("show_on_facade", "multi_select", "colorful", "multiline",
                "values_creatable_by_users", "is_used_as_progress"):
        if args.get(key) is not None:
            body[key] = args[key]
    if args.get("color") is not None:
        body["color"] = args["color"]
    if "data" in args:
        body["data"] = args["data"]
    if "fields_settings" in args:
        body["fields_settings"] = args["fields_settings"]
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
            "values_creatable_by_users": {
                "type": "boolean",
                "description": "Allow regular users to create new select values",
            },
            "is_used_as_progress": {
                "type": "boolean",
                "description": "Set this formula property as the card progress indicator (only for formula type, one per company)",
            },
            "color": {"type": "integer", "description": "Color index"},
            "data": {
                "type": "object",
                "description": "Type-specific data (e.g. restrictions for number/string, vote config)",
            },
            "fields_settings": {
                "type": "object",
                "description": "Catalog fields configuration (only for catalog type). Keys are field UIDs, values have {name, required, sortOrder, deleted}",
            },
        },
        "required": ["property_id"],
    },
    _update_custom_property,
)


async def _delete_custom_property(client, args: dict) -> Any:
    return await client.delete(f"/company/custom-properties/{args['property_id']}")


_tool(
    "kaiten_delete_custom_property",
    "Delete (soft) a custom property. Cannot delete properties used as progress or attached to Service Desk services.",
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
    for key in ("query", "offset", "order_by"):
        if args.get(key) is not None:
            params[key] = args[key]
    if args.get("conditions") is not None:
        params["conditions"] = args["conditions"]
    if args.get("v2_select_search") is not None:
        params["v2_select_search"] = args["v2_select_search"]
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
            "query": {"type": "string", "description": "Search filter by value text"},
            "order_by": {
                "type": "string",
                "enum": ["id", "sort_order", "match_query_priority"],
                "description": "Sort order: 'id', 'sort_order', or 'match_query_priority' (ranks by query match relevance, requires query param)",
            },
            "conditions": {
                "type": "string",
                "description": "Comma-separated conditions to filter: active, inactive (default: active,inactive)",
            },
            "v2_select_search": {
                "type": "boolean",
                "description": "Use v2 search with pagination and filtering support (recommended: true)",
            },
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
        "required": ["property_id"],
    },
    _list_select_values,
)


async def _get_select_value(client, args: dict) -> Any:
    return await client.get(
        f"/company/custom-properties/{args['property_id']}/select-values/{args['value_id']}"
    )


_tool(
    "kaiten_get_select_value",
    "Get a single select value by ID.",
    {
        "type": "object",
        "properties": {
            "property_id": {"type": "integer", "description": "Property ID"},
            "value_id": {"type": "integer", "description": "Select value ID"},
        },
        "required": ["property_id", "value_id"],
    },
    _get_select_value,
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
            "value": {"type": "string", "description": "Select value text (1-1024 chars, must be unique within the property)"},
            "color": {"type": "integer", "description": "Color index"},
            "sort_order": {"type": "number", "description": "Sort order (float)"},
        },
        "required": ["property_id", "value"],
    },
    _create_select_value,
)


async def _update_select_value(client, args: dict) -> Any:
    body = {}
    for key in ("value",):
        if args.get(key) is not None:
            body[key] = args[key]
    if "condition" in args:
        body["condition"] = args["condition"]
    for key in ("color", "sort_order"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(
        f"/company/custom-properties/{args['property_id']}/select-values/{args['value_id']}",
        json=body,
    )


_tool(
    "kaiten_update_select_value",
    "Update a select value for a custom property.",
    {
        "type": "object",
        "properties": {
            "property_id": {"type": "integer", "description": "Property ID"},
            "value_id": {"type": "integer", "description": "Select value ID"},
            "value": {"type": "string", "description": "New value text (1-1024 chars)"},
            "condition": {
                "type": "string",
                "enum": ["active", "inactive"],
                "description": "Value status",
            },
            "color": {"type": "integer", "description": "Color index"},
            "sort_order": {"type": "number", "description": "Sort order (float)"},
        },
        "required": ["property_id", "value_id"],
    },
    _update_select_value,
)


async def _delete_select_value(client, args: dict) -> Any:
    return await client.patch(
        f"/company/custom-properties/{args['property_id']}/select-values/{args['value_id']}",
        json={"deleted": True},
    )


_tool(
    "kaiten_delete_select_value",
    "Delete (soft) a select value by marking it as deleted.",
    {
        "type": "object",
        "properties": {
            "property_id": {"type": "integer", "description": "Property ID"},
            "value_id": {"type": "integer", "description": "Select value ID"},
        },
        "required": ["property_id", "value_id"],
    },
    _delete_select_value,
)
