"""Kaiten Checklists MCP tools."""

from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# --- Checklists ---


async def _list_checklists(client, args: dict) -> Any:
    return await client.get(f"/cards/{args['card_id']}/checklists")


_tool(
    "kaiten_list_checklists",
    "List all checklists on a Kaiten card.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
        },
        "required": ["card_id"],
    },
    _list_checklists,
)


async def _create_checklist(client, args: dict) -> Any:
    body = {"name": args["name"]}
    if args.get("sort_order") is not None:
        body["sort_order"] = args["sort_order"]
    return await client.post(f"/cards/{args['card_id']}/checklists", json=body)


_tool(
    "kaiten_create_checklist",
    "Create a checklist on a Kaiten card.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
            "name": {"type": "string", "description": "Checklist name"},
            "sort_order": {"type": "number", "description": "Sort order"},
        },
        "required": ["card_id", "name"],
    },
    _create_checklist,
)


async def _update_checklist(client, args: dict) -> Any:
    body = {}
    if args.get("name") is not None:
        body["name"] = args["name"]
    if args.get("sort_order") is not None:
        body["sort_order"] = args["sort_order"]
    return await client.patch(
        f"/cards/{args['card_id']}/checklists/{args['checklist_id']}", json=body
    )


_tool(
    "kaiten_update_checklist",
    "Update a checklist on a Kaiten card.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
            "checklist_id": {"type": "integer", "description": "Checklist ID"},
            "name": {"type": "string", "description": "Checklist name"},
            "sort_order": {"type": "number", "description": "Sort order"},
        },
        "required": ["card_id", "checklist_id"],
    },
    _update_checklist,
)


async def _delete_checklist(client, args: dict) -> Any:
    return await client.delete(f"/cards/{args['card_id']}/checklists/{args['checklist_id']}")


_tool(
    "kaiten_delete_checklist",
    "Delete a checklist from a Kaiten card.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
            "checklist_id": {"type": "integer", "description": "Checklist ID"},
        },
        "required": ["card_id", "checklist_id"],
    },
    _delete_checklist,
)


# --- Checklist Items ---


async def _list_checklist_items(client, args: dict) -> Any:
    return await client.get(f"/cards/{args['card_id']}/checklists/{args['checklist_id']}/items")


_tool(
    "kaiten_list_checklist_items",
    "List all items in a checklist on a Kaiten card.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
            "checklist_id": {"type": "integer", "description": "Checklist ID"},
        },
        "required": ["card_id", "checklist_id"],
    },
    _list_checklist_items,
)


async def _create_checklist_item(client, args: dict) -> Any:
    body = {"text": args["text"]}
    for key in ("checked", "sort_order", "user_id", "due_date"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.post(
        f"/cards/{args['card_id']}/checklists/{args['checklist_id']}/items", json=body
    )


_tool(
    "kaiten_create_checklist_item",
    "Create an item in a checklist on a Kaiten card.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
            "checklist_id": {"type": "integer", "description": "Checklist ID"},
            "text": {"type": "string", "description": "Item text"},
            "checked": {"type": "boolean", "description": "Whether the item is checked"},
            "sort_order": {"type": "number", "description": "Sort order"},
            "user_id": {"type": "integer", "description": "Assigned user ID"},
            "due_date": {"type": "string", "description": "Due date (ISO 8601 format)"},
        },
        "required": ["card_id", "checklist_id", "text"],
    },
    _create_checklist_item,
)


async def _update_checklist_item(client, args: dict) -> Any:
    body = {}
    for key in ("text", "checked", "sort_order", "user_id", "due_date"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(
        f"/cards/{args['card_id']}/checklists/{args['checklist_id']}/items/{args['item_id']}",
        json=body,
    )


_tool(
    "kaiten_update_checklist_item",
    "Update an item in a checklist on a Kaiten card.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
            "checklist_id": {"type": "integer", "description": "Checklist ID"},
            "item_id": {"type": "integer", "description": "Checklist item ID"},
            "text": {"type": "string", "description": "Item text"},
            "checked": {"type": "boolean", "description": "Whether the item is checked"},
            "sort_order": {"type": "number", "description": "Sort order"},
            "user_id": {"type": "integer", "description": "Assigned user ID"},
            "due_date": {"type": "string", "description": "Due date (ISO 8601 format)"},
        },
        "required": ["card_id", "checklist_id", "item_id"],
    },
    _update_checklist_item,
)


async def _delete_checklist_item(client, args: dict) -> Any:
    return await client.delete(
        f"/cards/{args['card_id']}/checklists/{args['checklist_id']}/items/{args['item_id']}"
    )


_tool(
    "kaiten_delete_checklist_item",
    "Delete an item from a checklist on a Kaiten card.",
    {
        "type": "object",
        "properties": {
            "card_id": {"type": "integer", "description": "Card ID"},
            "checklist_id": {"type": "integer", "description": "Checklist ID"},
            "item_id": {"type": "integer", "description": "Checklist item ID"},
        },
        "required": ["card_id", "checklist_id", "item_id"],
    },
    _delete_checklist_item,
)
