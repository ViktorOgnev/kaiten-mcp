"""Kaiten Projects & Sprints MCP tools."""
from typing import Any

from kaiten_mcp.tools.compact import DEFAULT_LIMIT, compact_response

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# --- Projects ---

async def _list_projects(client, args: dict) -> Any:
    return await client.get("/projects")


_tool(
    "kaiten_list_projects",
    "List all Kaiten projects in the company.",
    {
        "type": "object",
        "properties": {},
    },
    _list_projects,
)


async def _create_project(client, args: dict) -> Any:
    body = {"name": args["title"]}
    if args.get("description") is not None:
        body["description"] = args["description"]
    for key in ("work_calendar_id",):
        if args.get(key) is not None:
            body[key] = args[key]
    for key in ("settings", "properties"):
        if key in args:
            body[key] = args[key]
    return await client.post("/projects", json=body)


_tool(
    "kaiten_create_project",
    "Create a new Kaiten project.",
    {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Project title (stored as 'name')"},
            "description": {"type": "string", "description": "Project description"},
            "work_calendar_id": {
                "type": "string",
                "description": "Work calendar UUID to attach to the project",
            },
            "settings": {
                "type": "object",
                "description": "Project settings (e.g. timeline configuration: {timeline: {startHour, endHour, workDays}})",
            },
            "properties": {
                "type": "object",
                "description": "Custom property values as {id_<N>: value} pairs",
            },
        },
        "required": ["title"],
    },
    _create_project,
)


async def _get_project(client, args: dict) -> Any:
    params = {}
    if args.get("with_cards_data") is not None:
        params["with_cards_data"] = args["with_cards_data"]
    return await client.get(f"/projects/{args['project_id']}", params=params or None)


_tool(
    "kaiten_get_project",
    "Get a Kaiten project by ID.",
    {
        "type": "object",
        "properties": {
            "project_id": {"type": "string", "description": "Project ID (UUID)"},
            "with_cards_data": {
                "type": "boolean",
                "description": "Include full card data with path info and custom properties",
            },
        },
        "required": ["project_id"],
    },
    _get_project,
)


async def _update_project(client, args: dict) -> Any:
    body = {}
    if args.get("title") is not None:
        body["name"] = args["title"]
    if args.get("description") is not None:
        body["description"] = args["description"]
    for key in ("condition", "work_calendar_id"):
        if args.get(key) is not None:
            body[key] = args[key]
    for key in ("settings", "properties"):
        if key in args:
            body[key] = args[key]
    return await client.patch(f"/projects/{args['project_id']}", json=body)


_tool(
    "kaiten_update_project",
    "Update a Kaiten project.",
    {
        "type": "object",
        "properties": {
            "project_id": {"type": "string", "description": "Project ID (UUID)"},
            "title": {"type": "string", "description": "Project title (stored as 'name')"},
            "description": {"type": "string", "description": "Project description"},
            "condition": {
                "type": "string",
                "enum": ["active", "inactive"],
                "description": "Project condition (active or inactive)",
            },
            "work_calendar_id": {
                "type": "string",
                "description": "Work calendar UUID to attach to the project",
            },
            "settings": {
                "type": "object",
                "description": "Project settings (e.g. timeline configuration: {timeline: {startHour, endHour, workDays}})",
            },
            "properties": {
                "type": "object",
                "description": "Custom property values as {id_<N>: value} pairs; set a key to null to clear it",
            },
        },
        "required": ["project_id"],
    },
    _update_project,
)


async def _delete_project(client, args: dict) -> Any:
    return await client.delete(f"/projects/{args['project_id']}")


_tool(
    "kaiten_delete_project",
    "Delete a Kaiten project.",
    {
        "type": "object",
        "properties": {
            "project_id": {"type": "string", "description": "Project ID (UUID)"},
        },
        "required": ["project_id"],
    },
    _delete_project,
)


async def _list_project_cards(client, args: dict) -> Any:
    compact = args.get("compact", False)
    result = await client.get(f"/projects/{args['project_id']}/cards")
    return compact_response(result, compact)


_tool(
    "kaiten_list_project_cards",
    "List cards in a Kaiten project.",
    {
        "type": "object",
        "properties": {
            "project_id": {"type": "string", "description": "Project ID (UUID)"},
            "compact": {"type": "boolean", "description": "Return compact response without heavy fields (avatars, nested user objects).", "default": False},
        },
        "required": ["project_id"],
    },
    _list_project_cards,
)


async def _add_project_card(client, args: dict) -> Any:
    return await client.post(
        f"/projects/{args['project_id']}/cards", json={"card_id": args["card_id"]}
    )


_tool(
    "kaiten_add_project_card",
    "Add a card to a Kaiten project.",
    {
        "type": "object",
        "properties": {
            "project_id": {"type": "string", "description": "Project ID (UUID)"},
            "card_id": {"type": "integer", "description": "Card ID to add"},
        },
        "required": ["project_id", "card_id"],
    },
    _add_project_card,
)


async def _remove_project_card(client, args: dict) -> Any:
    return await client.delete(
        f"/projects/{args['project_id']}/cards/{args['card_id']}"
    )


_tool(
    "kaiten_remove_project_card",
    "Remove a card from a Kaiten project.",
    {
        "type": "object",
        "properties": {
            "project_id": {"type": "string", "description": "Project ID (UUID)"},
            "card_id": {"type": "integer", "description": "Card ID to remove"},
        },
        "required": ["project_id", "card_id"],
    },
    _remove_project_card,
)


# --- Sprints ---

async def _list_sprints(client, args: dict) -> Any:
    params = {}
    for key in ("active", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    return await client.get("/sprints", params=params)


_tool(
    "kaiten_list_sprints",
    "List Kaiten sprints.",
    {
        "type": "object",
        "properties": {
            "active": {"type": "boolean", "description": "Filter by active/inactive"},
            "limit": {"type": "integer", "description": "Max results (max 100)"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_sprints,
)


async def _create_sprint(client, args: dict) -> Any:
    body = {"title": args["title"], "board_id": args["board_id"]}
    for key in ("goal", "start_date", "finish_date"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.post("/sprints", json=body)


_tool(
    "kaiten_create_sprint",
    "Create a new Kaiten sprint.",
    {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Sprint title"},
            "board_id": {"type": "integer", "description": "Board ID for the sprint"},
            "goal": {"type": "string", "description": "Sprint goal"},
            "start_date": {"type": "string", "description": "Start date (ISO 8601)"},
            "finish_date": {"type": "string", "description": "Finish date (ISO 8601)"},
        },
        "required": ["title", "board_id"],
    },
    _create_sprint,
)


async def _get_sprint(client, args: dict) -> Any:
    params = {}
    if args.get("exclude_deleted_cards") is not None:
        params["exclude_deleted_cards"] = args["exclude_deleted_cards"]
    return await client.get(f"/sprints/{args['sprint_id']}", params=params or None)


_tool(
    "kaiten_get_sprint",
    "Get a Kaiten sprint by ID. Returns sprint summary with cards, path data, and custom properties.",
    {
        "type": "object",
        "properties": {
            "sprint_id": {"type": "integer", "description": "Sprint ID"},
            "exclude_deleted_cards": {
                "type": "boolean",
                "description": "Exclude deleted cards from the sprint summary",
            },
        },
        "required": ["sprint_id"],
    },
    _get_sprint,
)


async def _update_sprint(client, args: dict) -> Any:
    body = {}
    for key in ("title", "goal", "start_date", "finish_date"):
        if args.get(key) is not None:
            body[key] = args[key]
    if "active" in args:
        body["active"] = args["active"]
    if "archive_done_cards" in args:
        body["archive_done_cards"] = args["archive_done_cards"]
    return await client.patch(f"/sprints/{args['sprint_id']}", json=body)


_tool(
    "kaiten_update_sprint",
    "Update a Kaiten sprint. Set active=false to finish/complete the sprint.",
    {
        "type": "object",
        "properties": {
            "sprint_id": {"type": "integer", "description": "Sprint ID"},
            "title": {"type": "string", "description": "Sprint title"},
            "goal": {"type": "string", "description": "Sprint goal"},
            "start_date": {"type": "string", "description": "Start date (ISO 8601)"},
            "finish_date": {"type": "string", "description": "Finish date (ISO 8601)"},
            "active": {
                "type": "boolean",
                "description": "Set to false to finish/complete the sprint",
            },
            "archive_done_cards": {
                "type": "boolean",
                "description": "Archive completed cards when finishing a sprint (default true, only used when active=false)",
            },
        },
        "required": ["sprint_id"],
    },
    _update_sprint,
)


async def _delete_sprint(client, args: dict) -> Any:
    return await client.delete(f"/sprints/{args['sprint_id']}")


_tool(
    "kaiten_delete_sprint",
    "Delete a Kaiten sprint. Note: may return 405; sprint deletion may not be supported (sprints can only be completed).",
    {
        "type": "object",
        "properties": {
            "sprint_id": {"type": "integer", "description": "Sprint ID"},
        },
        "required": ["sprint_id"],
    },
    _delete_sprint,
)
