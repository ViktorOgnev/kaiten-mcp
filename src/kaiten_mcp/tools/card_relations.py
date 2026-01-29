"""Kaiten Card Relations MCP tools."""
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
# kaiten_list_card_children
# ---------------------------------------------------------------------------


async def _list_card_children(client, args: dict) -> Any:
    card_id = args["card_id"]
    return await client.get(f"/cards/{card_id}/children")


_tool(
    name="kaiten_list_card_children",
    description="List all child cards of a given card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the parent card.",
            },
        },
        "required": ["card_id"],
    },
    handler=_list_card_children,
)


# ---------------------------------------------------------------------------
# kaiten_add_card_child
# ---------------------------------------------------------------------------


async def _add_card_child(client, args: dict) -> Any:
    card_id = args["card_id"]
    body: dict[str, Any] = {"child_card_id": args["child_card_id"]}
    return await client.post(f"/cards/{card_id}/children", json=body)


_tool(
    name="kaiten_add_card_child",
    description="Add a child card to a given card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the parent card.",
            },
            "child_card_id": {
                "type": "integer",
                "description": "ID of the card to add as a child.",
            },
        },
        "required": ["card_id", "child_card_id"],
    },
    handler=_add_card_child,
)


# ---------------------------------------------------------------------------
# kaiten_remove_card_child
# ---------------------------------------------------------------------------


async def _remove_card_child(client, args: dict) -> Any:
    card_id = args["card_id"]
    child_id = args["child_id"]
    return await client.delete(f"/cards/{card_id}/children/{child_id}")


_tool(
    name="kaiten_remove_card_child",
    description="Remove a child card from a given card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the parent card.",
            },
            "child_id": {
                "type": "integer",
                "description": "ID of the child card to remove.",
            },
        },
        "required": ["card_id", "child_id"],
    },
    handler=_remove_card_child,
)


# ---------------------------------------------------------------------------
# kaiten_list_card_parents
# ---------------------------------------------------------------------------


async def _list_card_parents(client, args: dict) -> Any:
    card_id = args["card_id"]
    return await client.get(f"/cards/{card_id}/parents")


_tool(
    name="kaiten_list_card_parents",
    description="List all parent cards of a given card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the child card.",
            },
        },
        "required": ["card_id"],
    },
    handler=_list_card_parents,
)


# ---------------------------------------------------------------------------
# kaiten_add_card_parent
# ---------------------------------------------------------------------------


async def _add_card_parent(client, args: dict) -> Any:
    card_id = args["card_id"]
    body: dict[str, Any] = {"parent_card_id": args["parent_card_id"]}
    return await client.post(f"/cards/{card_id}/parents", json=body)


_tool(
    name="kaiten_add_card_parent",
    description="Add a parent card to a given card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the child card.",
            },
            "parent_card_id": {
                "type": "integer",
                "description": "ID of the card to add as a parent.",
            },
        },
        "required": ["card_id", "parent_card_id"],
    },
    handler=_add_card_parent,
)


# ---------------------------------------------------------------------------
# kaiten_remove_card_parent
# ---------------------------------------------------------------------------


async def _remove_card_parent(client, args: dict) -> Any:
    card_id = args["card_id"]
    parent_id = args["parent_id"]
    return await client.delete(f"/cards/{card_id}/parents/{parent_id}")


_tool(
    name="kaiten_remove_card_parent",
    description="Remove a parent card from a given card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the child card.",
            },
            "parent_id": {
                "type": "integer",
                "description": "ID of the parent card to remove.",
            },
        },
        "required": ["card_id", "parent_id"],
    },
    handler=_remove_card_parent,
)
