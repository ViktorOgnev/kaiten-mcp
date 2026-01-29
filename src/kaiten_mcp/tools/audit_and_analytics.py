"""Kaiten Audit, Activity & Analytics MCP tools."""
from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# --- Audit Logs ---

async def _list_audit_logs(client, args: dict) -> Any:
    params = {}
    for key in ("query", "limit", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get("/audit-logs", params=params or None)


_tool(
    "kaiten_list_audit_logs",
    "List Kaiten audit logs.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_audit_logs,
)


# --- Activity ---

async def _get_card_activity(client, args: dict) -> Any:
    params = {}
    for key in ("limit", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get(f"/cards/{args['card_id']}/activity", params=params or None)


_tool(
    "kaiten_get_card_activity",
    "Get activity feed for a Kaiten card.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
        "required": ["card_id"],
    },
    _get_card_activity,
)


async def _get_space_activity(client, args: dict) -> Any:
    params = {}
    for key in ("limit", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get(f"/spaces/{args['space_id']}/activity", params=params or None)


_tool(
    "kaiten_get_space_activity",
    "Get activity feed for a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
        "required": ["space_id"],
    },
    _get_space_activity,
)


async def _get_company_activity(client, args: dict) -> Any:
    params = {}
    for key in ("limit", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get("/company/activity", params=params or None)


_tool(
    "kaiten_get_company_activity",
    "Get company-wide activity feed.",
    {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _get_company_activity,
)


# --- Card History ---

async def _get_card_location_history(client, args: dict) -> Any:
    return await client.get(f"/cards/{args['card_id']}/location-history")


_tool(
    "kaiten_get_card_location_history",
    "Get location history of a Kaiten card (column/lane moves).",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
        },
        "required": ["card_id"],
    },
    _get_card_location_history,
)


# --- Saved Filters ---

async def _list_saved_filters(client, args: dict) -> Any:
    params = {}
    for key in ("limit", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get("/saved-filters", params=params or None)


_tool(
    "kaiten_list_saved_filters",
    "List saved filters.",
    {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_saved_filters,
)


async def _create_saved_filter(client, args: dict) -> Any:
    body = {"name": args["name"], "filter": args["filter"]}
    if args.get("shared") is not None:
        body["shared"] = args["shared"]
    return await client.post("/saved-filters", json=body)


_tool(
    "kaiten_create_saved_filter",
    "Create a saved filter.",
    {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Filter name"},
            "filter": {"type": "object", "description": "Filter criteria object"},
            "shared": {"type": "boolean", "description": "Whether the filter is shared with the team"},
        },
        "required": ["name", "filter"],
    },
    _create_saved_filter,
)


async def _get_saved_filter(client, args: dict) -> Any:
    return await client.get(f"/saved-filters/{args['filter_id']}")


_tool(
    "kaiten_get_saved_filter",
    "Get a saved filter by ID.",
    {
        "type": "object",
        "properties": {
            "filter_id": {"type": "integer", "description": "Filter ID"},
        },
        "required": ["filter_id"],
    },
    _get_saved_filter,
)


async def _update_saved_filter(client, args: dict) -> Any:
    body = {}
    for key in ("name", "filter", "shared"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(f"/saved-filters/{args['filter_id']}", json=body)


_tool(
    "kaiten_update_saved_filter",
    "Update a saved filter.",
    {
        "type": "object",
        "properties": {
            "filter_id": {"type": "integer", "description": "Filter ID"},
            "name": {"type": "string", "description": "Filter name"},
            "filter": {"type": "object", "description": "Filter criteria object"},
            "shared": {"type": "boolean", "description": "Whether the filter is shared with the team"},
        },
        "required": ["filter_id"],
    },
    _update_saved_filter,
)


async def _delete_saved_filter(client, args: dict) -> Any:
    return await client.delete(f"/saved-filters/{args['filter_id']}")


_tool(
    "kaiten_delete_saved_filter",
    "Delete a saved filter.",
    {
        "type": "object",
        "properties": {
            "filter_id": {"type": "integer", "description": "Filter ID"},
        },
        "required": ["filter_id"],
    },
    _delete_saved_filter,
)
