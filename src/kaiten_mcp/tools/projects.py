"""Kaiten Projects & Sprints MCP tools."""
from typing import Any

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
    return await client.post("/projects", json=body)


_tool(
    "kaiten_create_project",
    "Create a new Kaiten project.",
    {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Project title"},
            "description": {"type": "string", "description": "Project description"},
        },
        "required": ["title"],
    },
    _create_project,
)


async def _get_project(client, args: dict) -> Any:
    return await client.get(f"/projects/{args['project_id']}")


_tool(
    "kaiten_get_project",
    "Get a Kaiten project by ID.",
    {
        "type": "object",
        "properties": {
            "project_id": {"type": "integer", "description": "Project ID"},
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
    return await client.patch(f"/projects/{args['project_id']}", json=body)


_tool(
    "kaiten_update_project",
    "Update a Kaiten project.",
    {
        "type": "object",
        "properties": {
            "project_id": {"type": "integer", "description": "Project ID"},
            "title": {"type": "string", "description": "Project title"},
            "description": {"type": "string", "description": "Project description"},
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
            "project_id": {"type": "integer", "description": "Project ID"},
        },
        "required": ["project_id"],
    },
    _delete_project,
)


async def _list_project_cards(client, args: dict) -> Any:
    return await client.get(f"/projects/{args['project_id']}/cards")


_tool(
    "kaiten_list_project_cards",
    "List cards in a Kaiten project.",
    {
        "type": "object",
        "properties": {
            "project_id": {"type": "integer", "description": "Project ID"},
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
            "project_id": {"type": "integer", "description": "Project ID"},
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
            "project_id": {"type": "integer", "description": "Project ID"},
            "card_id": {"type": "integer", "description": "Card ID to remove"},
        },
        "required": ["project_id", "card_id"],
    },
    _remove_project_card,
)


# --- Sprints ---

async def _list_sprints(client, args: dict) -> Any:
    params = {}
    for key in ("active", "limit", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get("/sprints", params=params or None)


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
    return await client.get(f"/sprints/{args['sprint_id']}")


_tool(
    "kaiten_get_sprint",
    "Get a Kaiten sprint by ID.",
    {
        "type": "object",
        "properties": {
            "sprint_id": {"type": "integer", "description": "Sprint ID"},
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
    return await client.patch(f"/sprints/{args['sprint_id']}", json=body)


_tool(
    "kaiten_update_sprint",
    "Update a Kaiten sprint.",
    {
        "type": "object",
        "properties": {
            "sprint_id": {"type": "integer", "description": "Sprint ID"},
            "title": {"type": "string", "description": "Sprint title"},
            "goal": {"type": "string", "description": "Sprint goal"},
            "start_date": {"type": "string", "description": "Start date (ISO 8601)"},
            "finish_date": {"type": "string", "description": "Finish date (ISO 8601)"},
        },
        "required": ["sprint_id"],
    },
    _update_sprint,
)


async def _delete_sprint(client, args: dict) -> Any:
    return await client.delete(f"/sprints/{args['sprint_id']}")


_tool(
    "kaiten_delete_sprint",
    "Delete a Kaiten sprint.",
    {
        "type": "object",
        "properties": {
            "sprint_id": {"type": "integer", "description": "Sprint ID"},
        },
        "required": ["sprint_id"],
    },
    _delete_sprint,
)
