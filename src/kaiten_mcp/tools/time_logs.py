import asyncio
from typing import Any

from kaiten_mcp.tools.compact import compact_response, select_fields
from kaiten_mcp.tools.entity_helpers import register_direct_tool

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


register_direct_tool(
    TOOLS,
    name="kaiten_list_timesheet",
    description="List time logs across the current user's accessible scope.",
    properties={
        "from_date": {"type": "string", "description": "Start date filter."},
        "to_date": {"type": "string", "description": "End date filter."},
        "user_id": {"type": "integer", "description": "User ID filter."},
        "card_id": {"type": "integer", "description": "Card ID filter."},
        "limit": {"type": "integer", "description": "Max results."},
        "offset": {"type": "integer", "description": "Pagination offset."},
    },
    method="GET",
    path_template="/time-logs",
    query_fields=("from_date", "to_date", "user_id", "card_id", "limit", "offset"),
)


async def _batch_list_time_logs(client, args: dict) -> Any:
    card_ids = args["card_ids"]
    workers = max(1, min(int(args.get("workers") or 2), 6))
    compact = bool(args.get("compact", False))
    fields = args.get("fields")
    params = {}
    for key in ("for_date", "personal"):
        if args.get(key) is not None:
            params[key] = args[key]
    semaphore = asyncio.Semaphore(workers)

    async def fetch_one(card_id: int) -> dict[str, Any]:
        async with semaphore:
            try:
                logs = await client.get(
                    f"/cards/{card_id}/time-logs",
                    params=params if params else None,
                )
                logs = compact_response(logs, compact)
                logs = select_fields(logs, fields)
                return {"card_id": card_id, "ok": True, "time_logs": logs}
            except Exception as exc:
                return {"card_id": card_id, "ok": False, "error": str(exc)}

    items = await asyncio.gather(*(fetch_one(card_id) for card_id in card_ids))
    return {
        "items": [item for item in items if item["ok"]],
        "errors": [item for item in items if not item["ok"]],
        "meta": {"requested": len(card_ids), "workers": workers},
    }


_tool(
    name="kaiten_batch_list_time_logs",
    description="Fetch time logs for multiple cards with bounded request concurrency.",
    schema={
        "type": "object",
        "properties": {
            "card_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Card IDs to inspect.",
            },
            "workers": {"type": "integer", "description": "Parallel workers (default 2, max 6)."},
            "for_date": {"type": "string", "description": "Date filter."},
            "personal": {"type": "boolean", "description": "Personal logs flag."},
            "compact": {"type": "boolean", "description": "Strip heavy nested fields."},
            "fields": {
                "type": "string",
                "description": "Comma-separated time log fields to keep.",
            },
        },
        "required": ["card_ids"],
    },
    handler=_batch_list_time_logs,
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
