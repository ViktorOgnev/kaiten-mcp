"""Kaiten card blockers MCP tools."""

from typing import Any

from kaiten_mcp.tools.entity_helpers import register_direct_tool

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {
        "description": description,
        "inputSchema": schema,
        "handler": handler,
    }


# ---------------------------------------------------------------------------
# kaiten_list_card_blockers
# ---------------------------------------------------------------------------


async def _list_card_blockers(client, args: dict) -> Any:
    card_id = args["card_id"]
    return await client.get(f"/cards/{card_id}/blockers")


_tool(
    name="kaiten_list_card_blockers",
    description="List all blockers on a card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the card whose blockers to list.",
            },
        },
        "required": ["card_id"],
    },
    handler=_list_card_blockers,
)


# ---------------------------------------------------------------------------
# kaiten_create_card_blocker
# ---------------------------------------------------------------------------


async def _create_card_blocker(client, args: dict) -> Any:
    card_id = args["card_id"]
    body: dict[str, Any] = {}
    reason = args.get("reason")
    if reason is not None:
        body["reason"] = reason
    blocker_card_id = args.get("blocker_card_id")
    if blocker_card_id is not None:
        body["blocker_card_id"] = blocker_card_id
    return await client.post(f"/cards/{card_id}/blockers", json=body)


_tool(
    name="kaiten_create_card_blocker",
    description="Create a blocker on a card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the card to add a blocker to.",
            },
            "reason": {
                "type": "string",
                "description": "Reason for the blocker.",
            },
            "blocker_card_id": {
                "type": "integer",
                "description": "ID of the card that blocks this one.",
            },
        },
        "required": ["card_id"],
    },
    handler=_create_card_blocker,
)


# ---------------------------------------------------------------------------
# kaiten_get_card_blocker
# ---------------------------------------------------------------------------


async def _get_card_blocker(client, args: dict) -> Any:
    card_id = args["card_id"]
    blocker_id = args["blocker_id"]
    # The Kaiten API does not support GET /cards/{id}/blockers/{blocker_id}.
    # Fetch the full list and filter client-side.
    blockers = await client.get(f"/cards/{card_id}/blockers")
    if not isinstance(blockers, list):
        return blockers
    for b in blockers:
        if b.get("id") == blocker_id:
            return b
    return None


_tool(
    name="kaiten_get_card_blocker",
    description="Get a specific blocker on a card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the card.",
            },
            "blocker_id": {
                "type": "integer",
                "description": "ID of the blocker to retrieve.",
            },
        },
        "required": ["card_id", "blocker_id"],
    },
    handler=_get_card_blocker,
)


# ---------------------------------------------------------------------------
# kaiten_update_card_blocker
# ---------------------------------------------------------------------------


async def _update_card_blocker(client, args: dict) -> Any:
    card_id = args["card_id"]
    blocker_id = args["blocker_id"]
    body: dict[str, Any] = {}
    reason = args.get("reason")
    if reason is not None:
        body["reason"] = reason
    return await client.patch(f"/cards/{card_id}/blockers/{blocker_id}", json=body)


_tool(
    name="kaiten_update_card_blocker",
    description="Update a blocker on a card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the card.",
            },
            "blocker_id": {
                "type": "integer",
                "description": "ID of the blocker to update.",
            },
            "reason": {
                "type": "string",
                "description": "New reason for the blocker.",
            },
        },
        "required": ["card_id", "blocker_id"],
    },
    handler=_update_card_blocker,
)


# ---------------------------------------------------------------------------
# kaiten_delete_card_blocker
# ---------------------------------------------------------------------------


async def _delete_card_blocker(client, args: dict) -> Any:
    card_id = args["card_id"]
    blocker_id = args["blocker_id"]
    return await client.delete(f"/cards/{card_id}/blockers/{blocker_id}")


_tool(
    name="kaiten_delete_card_blocker",
    description="Delete a blocker from a card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the card.",
            },
            "blocker_id": {
                "type": "integer",
                "description": "ID of the blocker to delete.",
            },
        },
        "required": ["card_id", "blocker_id"],
    },
    handler=_delete_card_blocker,
)


register_direct_tool(
    TOOLS,
    name="kaiten_list_blocker_categories",
    description="List blocker categories.",
    properties={
        "query": {"type": "string", "description": "Search filter."},
        "limit": {"type": "integer", "description": "Max results."},
        "offset": {"type": "integer", "description": "Pagination offset."},
    },
    method="GET",
    path_template="/categories",
    query_fields=("query", "limit", "offset"),
)


register_direct_tool(
    TOOLS,
    name="kaiten_add_blocker_category",
    description="Attach a category to a blocker.",
    properties={
        "blocker_id": {"type": "integer", "description": "Blocker ID."},
        "category_uuid": {"type": "string", "description": "Category UUID."},
        "payload": {"type": "object", "description": "Extra JSON body fields."},
    },
    required=("blocker_id", "category_uuid"),
    method="POST",
    path_template="/blockers/{blocker_id}/categories",
    path_fields=("blocker_id",),
    body_fields=("category_uuid",),
    include_payload=True,
)


register_direct_tool(
    TOOLS,
    name="kaiten_remove_blocker_category",
    description="Remove a category from a blocker.",
    properties={
        "blocker_id": {"type": "integer", "description": "Blocker ID."},
        "category_uuid": {"type": "string", "description": "Category UUID."},
    },
    required=("blocker_id", "category_uuid"),
    method="DELETE",
    path_template="/blockers/{blocker_id}/categories/{category_uuid}",
    path_fields=("blocker_id", "category_uuid"),
)


register_direct_tool(
    TOOLS,
    name="kaiten_list_blocker_users",
    description="List users attached to a blocker.",
    properties={
        "blocker_id": {"type": "integer", "description": "Blocker ID."},
    },
    required=("blocker_id",),
    method="GET",
    path_template="/blockers/{blocker_id}/users",
    path_fields=("blocker_id",),
)


register_direct_tool(
    TOOLS,
    name="kaiten_add_blocker_user",
    description="Attach a user to a blocker.",
    properties={
        "blocker_id": {"type": "integer", "description": "Blocker ID."},
        "user_id": {"type": "integer", "description": "User ID."},
        "payload": {"type": "object", "description": "Extra JSON body fields."},
    },
    required=("blocker_id", "user_id"),
    method="POST",
    path_template="/blockers/{blocker_id}/users",
    path_fields=("blocker_id",),
    body_fields=("user_id",),
    include_payload=True,
)


register_direct_tool(
    TOOLS,
    name="kaiten_remove_blocker_user",
    description="Remove a user from a blocker.",
    properties={
        "blocker_id": {"type": "integer", "description": "Blocker ID."},
        "user_id": {"type": "integer", "description": "User ID."},
    },
    required=("blocker_id", "user_id"),
    method="DELETE",
    path_template="/blockers/{blocker_id}/users/{user_id}",
    path_fields=("blocker_id", "user_id"),
)


register_direct_tool(
    TOOLS,
    name="kaiten_list_current_user_blockers",
    description="List blockers assigned to the current user.",
    properties={
        "limit": {"type": "integer", "description": "Max results."},
        "offset": {"type": "integer", "description": "Pagination offset."},
    },
    method="GET",
    path_template="/users/current/blockers",
    query_fields=("limit", "offset"),
)
