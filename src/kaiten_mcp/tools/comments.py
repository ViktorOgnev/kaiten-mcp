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
# kaiten_list_comments
# ---------------------------------------------------------------------------


async def _list_comments(client, args: dict) -> Any:
    card_id = args["card_id"]
    return await client.get(f"/cards/{card_id}/comments")


_tool(
    name="kaiten_list_comments",
    description="List all comments on a card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the card whose comments to list.",
            },
        },
        "required": ["card_id"],
    },
    handler=_list_comments,
)


# ---------------------------------------------------------------------------
# kaiten_create_comment
# ---------------------------------------------------------------------------


async def _create_comment(client, args: dict) -> Any:
    card_id = args["card_id"]
    body: dict[str, Any] = {"text": args["text"]}
    internal = args.get("internal")
    if internal is not None:
        body["internal"] = internal
    return await client.post(f"/cards/{card_id}/comments", json=body)


_tool(
    name="kaiten_create_comment",
    description="Add a comment to a card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the card to comment on.",
            },
            "text": {
                "type": "string",
                "description": "Comment text.",
            },
            "internal": {
                "type": "boolean",
                "description": "Mark the comment as internal (visible only to team).",
            },
        },
        "required": ["card_id", "text"],
    },
    handler=_create_comment,
)


# ---------------------------------------------------------------------------
# kaiten_update_comment
# ---------------------------------------------------------------------------


async def _update_comment(client, args: dict) -> Any:
    card_id = args["card_id"]
    comment_id = args["comment_id"]
    body: dict[str, Any] = {"text": args["text"]}
    return await client.patch(
        f"/cards/{card_id}/comments/{comment_id}", json=body
    )


_tool(
    name="kaiten_update_comment",
    description="Update a comment on a card (author only).",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the card.",
            },
            "comment_id": {
                "type": "integer",
                "description": "ID of the comment to update.",
            },
            "text": {
                "type": "string",
                "description": "New comment text.",
            },
        },
        "required": ["card_id", "comment_id", "text"],
    },
    handler=_update_comment,
)


# ---------------------------------------------------------------------------
# kaiten_delete_comment
# ---------------------------------------------------------------------------


async def _delete_comment(client, args: dict) -> Any:
    card_id = args["card_id"]
    comment_id = args["comment_id"]
    return await client.delete(f"/cards/{card_id}/comments/{comment_id}")


_tool(
    name="kaiten_delete_comment",
    description="Delete a comment from a card (author only).",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the card.",
            },
            "comment_id": {
                "type": "integer",
                "description": "ID of the comment to delete.",
            },
        },
        "required": ["card_id", "comment_id"],
    },
    handler=_delete_comment,
)
