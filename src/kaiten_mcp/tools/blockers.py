"""Kaiten card blockers MCP tools."""
from __future__ import annotations

from typing import Any


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
    return await client.patch(
        f"/cards/{card_id}/blockers/{blocker_id}", json=body
    )


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
