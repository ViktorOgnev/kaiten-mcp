from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {
        "description": description,
        "inputSchema": schema,
        "handler": handler,
    }


# ---------------------------------------------------------------------------
# kaiten_list_card_time_logs
# ---------------------------------------------------------------------------


async def _list_card_time_logs(client, args: dict) -> Any:
    card_id = args["card_id"]
    params: dict[str, Any] = {}
    for_date = args.get("for_date")
    if for_date is not None:
        params["for_date"] = for_date
    personal = args.get("personal")
    if personal is not None:
        params["personal"] = personal
    return await client.get(f"/cards/{card_id}/time-logs", params=params if params else None)


_tool(
    name="kaiten_list_card_time_logs",
    description="List time logs for a card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the card.",
            },
            "for_date": {
                "type": "string",
                "description": "Filter by date (YYYY-MM-DD).",
            },
            "personal": {
                "type": "boolean",
                "description": "Return only the current user's time logs.",
            },
        },
        "required": ["card_id"],
    },
    handler=_list_card_time_logs,
)


# ---------------------------------------------------------------------------
# kaiten_create_time_log
# ---------------------------------------------------------------------------


async def _create_time_log(client, args: dict) -> Any:
    card_id = args["card_id"]
    body: dict[str, Any] = {
        "time_spent": args["time_spent"],
        "role_id": args.get("role_id", -1),
    }
    for_date = args.get("for_date")
    if for_date is not None:
        body["for_date"] = for_date
    comment = args.get("comment")
    if comment is not None:
        body["comment"] = comment
    return await client.post(f"/cards/{card_id}/time-logs", json=body)


_tool(
    name="kaiten_create_time_log",
    description="Log time spent on a card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the card.",
            },
            "time_spent": {
                "type": "integer",
                "minimum": 1,
                "description": "Time spent in minutes (minimum 1).",
            },
            "role_id": {
                "type": "integer",
                "description": "Role ID for the time log. Use -1 for the default role.",
            },
            "for_date": {
                "type": "string",
                "description": "Date for the time log (YYYY-MM-DD). Defaults to today.",
            },
            "comment": {
                "type": "string",
                "maxLength": 32767,
                "description": "Optional comment for the time log (max 32767 characters).",
            },
        },
        "required": ["card_id", "time_spent"],
    },
    handler=_create_time_log,
)


# ---------------------------------------------------------------------------
# kaiten_update_time_log
# ---------------------------------------------------------------------------


async def _update_time_log(client, args: dict) -> Any:
    card_id = args["card_id"]
    time_log_id = args["time_log_id"]
    body: dict[str, Any] = {}
    for key in ("time_spent", "role_id", "comment", "for_date"):
        value = args.get(key)
        if value is not None:
            body[key] = value
    return await client.patch(f"/cards/{card_id}/time-logs/{time_log_id}", json=body)


_tool(
    name="kaiten_update_time_log",
    description="Update a time log entry on a card (author only).",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the card.",
            },
            "time_log_id": {
                "type": "integer",
                "description": "ID of the time log to update.",
            },
            "time_spent": {
                "type": "integer",
                "minimum": 1,
                "description": "Updated time spent in minutes.",
            },
            "role_id": {
                "type": "integer",
                "description": "Updated role ID.",
            },
            "comment": {
                "type": "string",
                "maxLength": 32767,
                "description": "Updated comment.",
            },
            "for_date": {
                "type": "string",
                "description": "Updated date (YYYY-MM-DD).",
            },
        },
        "required": ["card_id", "time_log_id"],
    },
    handler=_update_time_log,
)


# ---------------------------------------------------------------------------
# kaiten_delete_time_log
# ---------------------------------------------------------------------------


async def _delete_time_log(client, args: dict) -> Any:
    card_id = args["card_id"]
    time_log_id = args["time_log_id"]
    return await client.delete(f"/cards/{card_id}/time-logs/{time_log_id}")


_tool(
    name="kaiten_delete_time_log",
    description="Delete a time log entry from a card (author only).",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the card.",
            },
            "time_log_id": {
                "type": "integer",
                "description": "ID of the time log to delete.",
            },
        },
        "required": ["card_id", "time_log_id"],
    },
    handler=_delete_time_log,
)
