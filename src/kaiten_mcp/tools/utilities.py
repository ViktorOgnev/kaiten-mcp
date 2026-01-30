"""Kaiten Utilities MCP tools."""
from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# --- API Keys ---

async def _list_api_keys(client, args: dict) -> Any:
    return await client.get("/api-keys")


_tool(
    "kaiten_list_api_keys",
    "List all API keys for the current user.",
    {"type": "object", "properties": {}},
    _list_api_keys,
)


async def _create_api_key(client, args: dict) -> Any:
    return await client.post("/api-keys", json={"name": args["name"]})


_tool(
    "kaiten_create_api_key",
    "Create a new API key.",
    {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Name for the API key"},
        },
        "required": ["name"],
    },
    _create_api_key,
)


async def _delete_api_key(client, args: dict) -> Any:
    return await client.delete(f"/api-keys/{args['key_id']}")


_tool(
    "kaiten_delete_api_key",
    "Delete an API key.",
    {
        "type": "object",
        "properties": {
            "key_id": {"type": "integer", "description": "API key ID"},
        },
        "required": ["key_id"],
    },
    _delete_api_key,
)


# --- User Timers ---

async def _list_user_timers(client, args: dict) -> Any:
    return await client.get("/user-timers")


_tool(
    "kaiten_list_user_timers",
    "List all user timers.",
    {"type": "object", "properties": {}},
    _list_user_timers,
)


async def _create_user_timer(client, args: dict) -> Any:
    return await client.post("/user-timers", json={"card_id": args["card_id"]})


_tool(
    "kaiten_create_user_timer",
    "Create a new user timer for a card.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID to start timer for"},
        },
        "required": ["card_id"],
    },
    _create_user_timer,
)


async def _get_user_timer(client, args: dict) -> Any:
    return await client.get(f"/user-timers/{args['timer_id']}")


_tool(
    "kaiten_get_user_timer",
    "Get a specific user timer by ID.",
    {
        "type": "object",
        "properties": {
            "timer_id": {"type": "integer", "description": "Timer ID"},
        },
        "required": ["timer_id"],
    },
    _get_user_timer,
)


async def _update_user_timer(client, args: dict) -> Any:
    body = {}
    if args.get("paused") is not None:
        body["paused"] = args["paused"]
    return await client.patch(f"/user-timers/{args['timer_id']}", json=body)


_tool(
    "kaiten_update_user_timer",
    "Update a user timer (e.g. pause or resume).",
    {
        "type": "object",
        "properties": {
            "timer_id": {"type": "integer", "description": "Timer ID"},
            "paused": {"type": "boolean", "description": "Whether the timer is paused"},
        },
        "required": ["timer_id"],
    },
    _update_user_timer,
)


async def _delete_user_timer(client, args: dict) -> Any:
    return await client.delete(f"/user-timers/{args['timer_id']}")


_tool(
    "kaiten_delete_user_timer",
    "Delete a user timer.",
    {
        "type": "object",
        "properties": {
            "timer_id": {"type": "integer", "description": "Timer ID"},
        },
        "required": ["timer_id"],
    },
    _delete_user_timer,
)


# --- Removed Items (Recycle Bin) ---

async def _list_removed_cards(client, args: dict) -> Any:
    params = {}
    for key in ("limit", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get("/removed/cards", params=params or None)


_tool(
    "kaiten_list_removed_cards",
    "List removed (deleted) cards from the recycle bin. Note: may return 405; the recycle bin listing endpoint may not be available.",
    {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_removed_cards,
)


async def _list_removed_boards(client, args: dict) -> Any:
    params = {}
    for key in ("limit", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get("/removed/boards", params=params or None)


_tool(
    "kaiten_list_removed_boards",
    "List removed (deleted) boards from the recycle bin. Note: may return 405; the recycle bin listing endpoint may not be available.",
    {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_removed_boards,
)


# --- Calendars ---

async def _list_calendars(client, args: dict) -> Any:
    params = {}
    for key in ("limit", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get("/calendars", params=params or None)


_tool(
    "kaiten_list_calendars",
    "List calendars.",
    {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_calendars,
)


async def _get_calendar(client, args: dict) -> Any:
    return await client.get(f"/calendars/{args['calendar_id']}")


_tool(
    "kaiten_get_calendar",
    "Get a specific calendar by ID.",
    {
        "type": "object",
        "properties": {
            "calendar_id": {"type": "string", "description": "Calendar ID (UUID)"},
        },
        "required": ["calendar_id"],
    },
    _get_calendar,
)


# --- Company Info ---

async def _get_company(client, args: dict) -> Any:
    return await client.get("/companies/current")


_tool(
    "kaiten_get_company",
    "Get current company information.",
    {"type": "object", "properties": {}},
    _get_company,
)


async def _update_company(client, args: dict) -> Any:
    body = {}
    if args.get("name") is not None:
        body["name"] = args["name"]
    return await client.patch("/companies/current", json=body)


_tool(
    "kaiten_update_company",
    "Update current company information.",
    {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Company name"},
        },
    },
    _update_company,
)
