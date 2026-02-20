"""Kaiten Card Relations MCP tools."""

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
    body: dict[str, Any] = {"card_id": args["child_card_id"]}
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
    body: dict[str, Any] = {"card_id": args["parent_card_id"]}
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


# ---------------------------------------------------------------------------
# kaiten_add_planned_relation  (Successor cards on Timeline/Gantt)
# ---------------------------------------------------------------------------


async def _add_planned_relation(client, args: dict) -> Any:
    card_id = args["card_id"]
    body: dict[str, Any] = {
        "target_card_id": args["target_card_id"],
        "type": args.get("type", "end-start"),
    }
    return await client.post(f"/cards/{card_id}/planned-relation", json=body)


_tool(
    name="kaiten_add_planned_relation",
    description=(
        "Create a planned relation (successor link) between two cards on "
        "Timeline/Gantt. The source card (card_id) becomes a predecessor "
        "and the target card becomes its successor. Both cards must have "
        "planned_start and planned_end dates set."
    ),
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the source (predecessor) card.",
            },
            "target_card_id": {
                "type": "integer",
                "description": "ID of the target (successor) card.",
            },
            "type": {
                "type": "string",
                "enum": ["end-start"],
                "default": "end-start",
                "description": "Relation type. Currently only 'end-start' (finish-to-start) is supported.",
            },
        },
        "required": ["card_id", "target_card_id"],
    },
    handler=_add_planned_relation,
)


# ---------------------------------------------------------------------------
# kaiten_update_planned_relation
# ---------------------------------------------------------------------------


async def _update_planned_relation(client, args: dict) -> Any:
    card_id = args["card_id"]
    target_card_id = args["target_card_id"]
    body: dict[str, Any] = {
        "gap": args["gap"],
        "gap_type": args["gap_type"],
    }
    return await client.patch(
        f"/cards/{card_id}/planned-relation/{target_card_id}", json=body,
    )


_tool(
    name="kaiten_update_planned_relation",
    description=(
        "Update the gap (lag/lead) of a planned relation between two cards. "
        "Gap defines the time distance between the predecessor's end and "
        "the successor's start on the Timeline/Gantt."
    ),
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the source (predecessor) card.",
            },
            "target_card_id": {
                "type": "integer",
                "description": "ID of the target (successor) card.",
            },
            "gap": {
                "type": ["integer", "null"],
                "description": "Distance between cards (-1000..1000). Positive = lag, negative = lead. null to clear.",
            },
            "gap_type": {
                "type": ["string", "null"],
                "enum": ["hours", "days", None],
                "description": "Unit of the gap: 'hours', 'days', or null to clear.",
            },
        },
        "required": ["card_id", "target_card_id", "gap", "gap_type"],
    },
    handler=_update_planned_relation,
)


# ---------------------------------------------------------------------------
# kaiten_remove_planned_relation
# ---------------------------------------------------------------------------


async def _remove_planned_relation(client, args: dict) -> Any:
    card_id = args["card_id"]
    target_card_id = args["target_card_id"]
    return await client.delete(
        f"/cards/{card_id}/planned-relation/{target_card_id}",
    )


_tool(
    name="kaiten_remove_planned_relation",
    description=(
        "Remove a planned relation (successor link) between two cards. "
        "card_id is the predecessor, target_card_id is the successor."
    ),
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the source (predecessor) card.",
            },
            "target_card_id": {
                "type": "integer",
                "description": "ID of the target (successor) card to unlink.",
            },
        },
        "required": ["card_id", "target_card_id"],
    },
    handler=_remove_planned_relation,
)
