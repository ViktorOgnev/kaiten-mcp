"""Kaiten Audit, Activity & Analytics MCP tools."""
from typing import Any

from kaiten_mcp.tools.compact import compact_response, select_fields, DEFAULT_LIMIT

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# --- Audit Logs ---

async def _list_audit_logs(client, args: dict) -> Any:
    params: dict[str, Any] = {}
    for key in ("offset", "categories", "actions", "from", "to"):
        if args.get(key) is not None:
            params[key] = args[key]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    return await client.get("/audit-logs", params=params)


_tool(
    "kaiten_list_audit_logs",
    "List Kaiten audit logs for the company. Supports filtering by category, action, and date range.",
    {
        "type": "object",
        "properties": {
            "categories": {
                "type": "string",
                "description": (
                    "Comma-separated list of log categories to filter by. "
                    "Values: app, auth, user_management, group_management, "
                    "user_profile, service_desk, publication, import, company_profile"
                ),
            },
            "actions": {
                "type": "string",
                "description": (
                    "Comma-separated list of actions to filter by. "
                    "Values: start, stop, sign_in, sign_in_fail, sign_out, "
                    "request_auth_pin, invite, invite_fail, change_password, "
                    "request_change_email, change_email, activate, deactivate, "
                    "change_permissions, change_apps_permissions, grant_access, "
                    "revoke_access, transfer_ownership, create, delete, add_user, "
                    "add_admin, admin_add_user, delete_user, delete_admin, "
                    "admin_delete_user, set_sd_password, "
                    "change_temporary_sd_password, group_activate, "
                    "group_deactivate, publish_document, publish_document_group, "
                    "publish_card, unpublish_document, unpublish_document_group, "
                    "unpublish_card, share_entity, unshare_entity, public_link, "
                    "extend_trial"
                ),
            },
            "from": {
                "type": "string",
                "description": "Start of date range filter (ISO 8601 datetime, e.g. '2025-01-01T00:00:00Z').",
            },
            "to": {
                "type": "string",
                "description": "End of date range filter (ISO 8601 datetime, e.g. '2025-12-31T23:59:59Z').",
            },
            "limit": {
                "type": "integer",
                "description": "Max results (default 100, max 100).",
            },
            "offset": {
                "type": "integer",
                "description": "Pagination offset.",
            },
        },
    },
    _list_audit_logs,
)


# --- Activity ---

async def _get_card_activity(client, args: dict) -> Any:
    params = {}
    if args.get("offset") is not None:
        params["offset"] = args["offset"]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    return await client.get(f"/cards/{args['card_id']}/activity", params=params)


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
    for key in ("offset", "author_id"):
        if args.get(key) is not None:
            params[key] = args[key]
    for key in ("actions", "created_after", "created_before"):
        if args.get(key) is not None:
            params[key] = args[key]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    result = await client.get(f"/spaces/{args['space_id']}/activity", params=params)
    result = compact_response(result, args.get("compact", False))
    return select_fields(result, args.get("fields"))


_tool(
    "kaiten_get_space_activity",
    (
        "Get activity feed for a Kaiten space. "
        "EFFICIENT BULK ALTERNATIVE: Use actions='card_add,card_move,card_archive,"
        "card_join_board,card_revive' to get all location history for ALL cards in a space. "
        "Paginate with offset to get complete history — much more efficient than calling "
        "kaiten_get_card_location_history for each card individually."
    ),
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "actions": {
                "type": "string",
                "description": (
                    "Comma-separated action types to filter (card_add, card_move, "
                    "card_archive, card_join_board, card_revive, card_delete, "
                    "comment_add, checklist_add, member_add, etc.)"
                ),
            },
            "created_after": {
                "type": "string",
                "description": "Filter activities after this datetime (ISO 8601)",
            },
            "created_before": {
                "type": "string",
                "description": "Filter activities before this datetime (ISO 8601)",
            },
            "author_id": {
                "type": "integer",
                "description": "Filter by author user ID",
            },
            "limit": {"type": "integer", "description": "Max results (default 50, max 100)"},
            "offset": {"type": "integer", "description": "Pagination offset"},
            "compact": {"type": "boolean", "description": "Strip heavy fields (avatars, user details). Default true for bulk."},
            "fields": {"type": "string", "description": "Comma-separated field names to keep. Strips everything else."},
        },
        "required": ["space_id"],
    },
    _get_space_activity,
)


async def _get_company_activity(client, args: dict) -> Any:
    params = {}
    for key in ("offset", "author_id", "cursor_id"):
        if args.get(key) is not None:
            params[key] = args[key]
    for key in ("actions", "created_after", "created_before", "cursor_created"):
        if args.get(key) is not None:
            params[key] = args[key]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    result = await client.get("/company/activity", params=params)
    result = compact_response(result, args.get("compact", False))
    return select_fields(result, args.get("fields"))


_tool(
    "kaiten_get_company_activity",
    "Get company-wide activity feed. Supports cursor-based pagination for large datasets.",
    {
        "type": "object",
        "properties": {
            "actions": {
                "type": "string",
                "description": (
                    "Comma-separated action types to filter (card_add, card_move, "
                    "card_archive, card_join_board, card_revive, card_delete, "
                    "comment_add, checklist_add, member_add, etc.)"
                ),
            },
            "created_after": {
                "type": "string",
                "description": "Filter activities after this datetime (ISO 8601)",
            },
            "created_before": {
                "type": "string",
                "description": "Filter activities before this datetime (ISO 8601)",
            },
            "author_id": {
                "type": "integer",
                "description": "Filter by author user ID",
            },
            "cursor_created": {
                "type": "string",
                "description": (
                    "Cursor-based pagination: datetime of last item "
                    "(more efficient than offset for large datasets)"
                ),
            },
            "cursor_id": {
                "type": "integer",
                "description": "Cursor-based pagination: ID of last item (use with cursor_created)",
            },
            "limit": {"type": "integer", "description": "Max results (default 50, max 100)"},
            "offset": {"type": "integer", "description": "Pagination offset"},
            "compact": {"type": "boolean", "description": "Strip heavy fields (avatars, user details). Default true for bulk."},
            "fields": {"type": "string", "description": "Comma-separated field names to keep. Strips everything else."},
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


# --- Auto-paginating Activity ---

async def _get_all_space_activity(client, args: dict) -> Any:
    """Fetch all space activity with automatic pagination."""
    page_size = min(args.get("page_size", 100), 100)
    max_pages = args.get("max_pages", 50)
    compact = args.get("compact", True)  # Default compact for bulk

    params: dict[str, Any] = {}
    for key in ("actions", "created_after", "created_before", "author_id"):
        if args.get(key) is not None:
            params[key] = args[key]

    all_activity: list = []
    for page in range(max_pages):
        params["limit"] = page_size
        params["offset"] = page * page_size
        result = await client.get(
            f"/spaces/{args['space_id']}/activity", params=params,
        )
        if not result:
            break
        all_activity.extend(result)
        if len(result) < page_size:
            break

    result = compact_response(all_activity, compact)
    return select_fields(result, args.get("fields"))


_tool(
    "kaiten_get_all_space_activity",
    (
        "Fetch ALL activity for a space with automatic pagination. "
        "Use actions filter to get specific event types. "
        "For complete card flow history: actions='card_add,card_move,card_archive,"
        "card_join_board,card_revive'. "
        "Safety limit: 50 pages (5000 events). "
        "This is the EFFICIENT way to get location history for all cards in a space — "
        "one paginated endpoint instead of hundreds of individual card requests."
    ),
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "actions": {
                "type": "string",
                "description": (
                    "Comma-separated action types "
                    "(card_add, card_move, card_archive, card_join_board, card_revive, etc.)"
                ),
            },
            "created_after": {
                "type": "string",
                "description": "Filter activities after this datetime (ISO 8601)",
            },
            "created_before": {
                "type": "string",
                "description": "Filter activities before this datetime (ISO 8601)",
            },
            "author_id": {
                "type": "integer",
                "description": "Filter by author user ID",
            },
            "page_size": {
                "type": "integer",
                "description": "Events per page (default 100, max 100)",
            },
            "max_pages": {
                "type": "integer",
                "description": "Safety limit on pages to fetch (default 50, max 5000 events)",
            },
            "compact": {"type": "boolean", "description": "Strip heavy fields (avatars, user details). Default true for bulk."},
            "fields": {"type": "string", "description": "Comma-separated field names to keep. Strips everything else."},
        },
        "required": ["space_id"],
    },
    _get_all_space_activity,
)


# --- Saved Filters ---

async def _list_saved_filters(client, args: dict) -> Any:
    params = {}
    if args.get("offset") is not None:
        params["offset"] = args["offset"]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    return await client.get("/saved-filters", params=params)


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
    body = {"title": args["name"], "filter": args["filter"]}
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
    if args.get("name") is not None:
        body["title"] = args["name"]
    for key in ("filter", "shared"):
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
