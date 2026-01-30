"""Kaiten Cards MCP tools."""
from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# --- List / Search cards ---

async def _list_cards(client, args: dict) -> Any:
    params = {}
    str_keys = [
        "query", "tag_ids", "member_ids", "owner_ids", "responsible_ids",
        "states", "column_ids", "type_ids", "external_id",
        "created_after", "created_before", "updated_after", "updated_before",
        "due_date_after", "due_date_before",
    ]
    int_keys = [
        "space_id", "board_id", "column_id", "lane_id", "condition",
        "type_id", "owner_id", "responsible_id", "limit", "offset",
    ]
    bool_keys = ["overdue", "asap", "archived"]
    for key in str_keys + int_keys + bool_keys:
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get("/cards", params=params or None)


_tool(
    "kaiten_list_cards",
    "Search and list Kaiten cards with filtering. Conditions: 1=active, 2=archived. States: 1=queued, 2=inProgress, 3=done.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Full-text search query"},
            "space_id": {"type": "integer", "description": "Filter by space ID"},
            "board_id": {"type": "integer", "description": "Filter by board ID"},
            "column_id": {"type": "integer", "description": "Filter by column ID"},
            "lane_id": {"type": "integer", "description": "Filter by lane ID"},
            "condition": {"type": "integer", "enum": [1, 2], "description": "1=active, 2=archived"},
            "type_id": {"type": "integer", "description": "Filter by card type ID"},
            "owner_id": {"type": "integer", "description": "Filter by owner user ID"},
            "responsible_id": {"type": "integer", "description": "Filter by responsible user ID"},
            "tag_ids": {"type": "string", "description": "Comma-separated tag IDs"},
            "member_ids": {"type": "string", "description": "Comma-separated member IDs"},
            "states": {"type": "string", "description": "Comma-separated states (1=queued,2=inProgress,3=done)"},
            "created_after": {"type": "string", "description": "ISO datetime filter"},
            "created_before": {"type": "string", "description": "ISO datetime filter"},
            "updated_after": {"type": "string", "description": "ISO datetime filter"},
            "updated_before": {"type": "string", "description": "ISO datetime filter"},
            "due_date_after": {"type": "string", "description": "ISO datetime filter"},
            "due_date_before": {"type": "string", "description": "ISO datetime filter"},
            "external_id": {"type": "string", "description": "External ID filter"},
            "overdue": {"type": "boolean", "description": "Filter overdue cards"},
            "asap": {"type": "boolean", "description": "Filter ASAP cards"},
            "archived": {"type": "boolean", "description": "Include archived"},
            "limit": {"type": "integer", "description": "Max results (default 20, max 100)"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_cards,
)


# --- Get card ---

async def _get_card(client, args: dict) -> Any:
    return await client.get(f"/cards/{args['card_id']}")


_tool(
    "kaiten_get_card",
    "Get a Kaiten card by ID. Supports numeric ID or card key (e.g. PROJ-123).",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": ["integer", "string"], "description": "Card ID or key (e.g. PROJ-123)"},
        },
        "required": ["card_id"],
    },
    _get_card,
)


# --- Create card ---

async def _create_card(client, args: dict) -> Any:
    body = {"title": args["title"], "board_id": args["board_id"]}
    opt_keys = [
        "column_id", "lane_id", "description", "due_date", "asap",
        "size_text", "owner_id", "type_id", "external_id",
        "sort_order", "position", "properties", "tags",
        "sprint_id", "planned_start", "planned_end",
    ]
    for key in opt_keys:
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.post("/cards", json=body)


_tool(
    "kaiten_create_card",
    "Create a new Kaiten card. Title max 1024 chars, description max 32768 chars.",
    {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Card title (1-1024 chars)"},
            "board_id": {"type": "integer", "description": "Target board ID"},
            "column_id": {"type": "integer", "description": "Target column ID"},
            "lane_id": {"type": "integer", "description": "Target lane ID"},
            "description": {"type": "string", "description": "Card description (max 32768)"},
            "due_date": {"type": ["string", "null"], "description": "Deadline (ISO 8601)"},
            "asap": {"type": "boolean", "description": "ASAP marker"},
            "size_text": {"type": "string", "description": "Size (e.g. S, M, L, 1, 23.45)"},
            "owner_id": {"type": "integer", "description": "Owner user ID"},
            "type_id": {"type": "integer", "description": "Card type ID"},
            "external_id": {"type": "string", "description": "External ID (max 1024)"},
            "sort_order": {"type": "number", "description": "Position in cell"},
            "position": {"type": "integer", "enum": [1, 2], "description": "1=first, 2=last in cell"},
            "properties": {"type": "object", "description": "Custom properties as {id_N: value}"},
            "tags": {"type": "array", "description": "Tags to attach"},
            "sprint_id": {"type": "integer", "description": "Sprint ID to assign card to"},
            "planned_start": {"type": ["string", "null"], "description": "Planned start date (ISO 8601)"},
            "planned_end": {"type": ["string", "null"], "description": "Planned end date (ISO 8601)"},
        },
        "required": ["title", "board_id"],
    },
    _create_card,
)


# --- Update card ---

async def _update_card(client, args: dict) -> Any:
    body = {}
    opt_keys = [
        "title", "description", "board_id", "column_id", "lane_id",
        "sort_order", "owner_id", "type_id", "condition", "due_date",
        "asap", "size_text", "blocked", "external_id", "properties",
        "sprint_id", "planned_start", "planned_end",
    ]
    for key in opt_keys:
        if key in args and key != "card_id":
            body[key] = args[key]
    return await client.patch(f"/cards/{args['card_id']}", json=body)


_tool(
    "kaiten_update_card",
    "Update a Kaiten card. Use condition=2 to archive, set column_id/board_id to move.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": ["integer", "string"], "description": "Card ID or key"},
            "title": {"type": "string", "description": "New title"},
            "description": {"type": ["string", "null"], "description": "New description"},
            "board_id": {"type": "integer", "description": "Move to board"},
            "column_id": {"type": "integer", "description": "Move to column"},
            "lane_id": {"type": "integer", "description": "Move to lane"},
            "sort_order": {"type": "number", "description": "Position in cell"},
            "owner_id": {"type": "integer", "description": "New owner user ID"},
            "type_id": {"type": "integer", "description": "Card type ID"},
            "condition": {"type": "integer", "enum": [1, 2], "description": "1=active, 2=archived"},
            "due_date": {"type": ["string", "null"], "description": "Deadline (ISO 8601 or null)"},
            "asap": {"type": "boolean", "description": "ASAP marker"},
            "size_text": {"type": ["string", "null"], "description": "Size"},
            "blocked": {"type": "boolean", "description": "Set to false to unblock"},
            "external_id": {"type": ["string", "null"], "description": "External ID"},
            "properties": {"type": "object", "description": "Custom properties as {id_N: value}"},
            "sprint_id": {"type": ["integer", "null"], "description": "Sprint ID (null to remove)"},
            "planned_start": {"type": ["string", "null"], "description": "Planned start date (ISO 8601)"},
            "planned_end": {"type": ["string", "null"], "description": "Planned end date (ISO 8601)"},
        },
        "required": ["card_id"],
    },
    _update_card,
)


# --- Delete card ---

async def _delete_card(client, args: dict) -> Any:
    return await client.delete(f"/cards/{args['card_id']}")


_tool(
    "kaiten_delete_card",
    "Soft-delete a Kaiten card (sets condition to deleted). Cards with time logs cannot be deleted.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": ["integer", "string"], "description": "Card ID or key"},
        },
        "required": ["card_id"],
    },
    _delete_card,
)


# --- Archive card (convenience) ---

async def _archive_card(client, args: dict) -> Any:
    return await client.patch(f"/cards/{args['card_id']}", json={"condition": 2})


_tool(
    "kaiten_archive_card",
    "Archive a Kaiten card (set condition to archived).",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": ["integer", "string"], "description": "Card ID or key"},
        },
        "required": ["card_id"],
    },
    _archive_card,
)


# --- Move card (convenience) ---

async def _move_card(client, args: dict) -> Any:
    body = {}
    for key in ("board_id", "column_id", "lane_id", "sort_order"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(f"/cards/{args['card_id']}", json=body)


_tool(
    "kaiten_move_card",
    "Move a Kaiten card to a different board, column, or lane.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": ["integer", "string"], "description": "Card ID or key"},
            "board_id": {"type": "integer", "description": "Target board ID"},
            "column_id": {"type": "integer", "description": "Target column ID"},
            "lane_id": {"type": "integer", "description": "Target lane ID"},
            "sort_order": {"type": "number", "description": "Position in cell"},
        },
        "required": ["card_id"],
    },
    _move_card,
)
