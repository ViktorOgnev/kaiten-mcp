from typing import Any

from kaiten_mcp.tools.compact import DEFAULT_LIMIT, compact_response

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {
        "description": description,
        "inputSchema": schema,
        "handler": handler,
    }


# ---------------------------------------------------------------------------
# kaiten_list_card_members
# ---------------------------------------------------------------------------


async def _list_card_members(client, args: dict) -> Any:
    card_id = args["card_id"]
    compact = args.get("compact", False)
    result = await client.get(f"/cards/{card_id}/members")
    return compact_response(result, compact)


_tool(
    name="kaiten_list_card_members",
    description="List all members assigned to a card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the card.",
            },
            "compact": {
                "type": "boolean",
                "description": "Return compact response without heavy fields (avatars, etc.).",
                "default": False,
            },
        },
        "required": ["card_id"],
    },
    handler=_list_card_members,
)


# ---------------------------------------------------------------------------
# kaiten_add_card_member
# ---------------------------------------------------------------------------


async def _add_card_member(client, args: dict) -> Any:
    card_id = args["card_id"]
    body: dict[str, Any] = {"user_id": args["user_id"]}
    return await client.post(f"/cards/{card_id}/members", json=body)


_tool(
    name="kaiten_add_card_member",
    description="Add a member to a card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the card.",
            },
            "user_id": {
                "type": "integer",
                "description": "ID of the user to add as a member.",
            },
        },
        "required": ["card_id", "user_id"],
    },
    handler=_add_card_member,
)


# ---------------------------------------------------------------------------
# kaiten_remove_card_member
# ---------------------------------------------------------------------------


async def _remove_card_member(client, args: dict) -> Any:
    card_id = args["card_id"]
    user_id = args["user_id"]
    return await client.delete(f"/cards/{card_id}/members/{user_id}")


_tool(
    name="kaiten_remove_card_member",
    description="Remove a member from a card.",
    schema={
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "ID of the card.",
            },
            "user_id": {
                "type": "integer",
                "description": "ID of the user to remove.",
            },
        },
        "required": ["card_id", "user_id"],
    },
    handler=_remove_card_member,
)


# ---------------------------------------------------------------------------
# kaiten_list_users
# ---------------------------------------------------------------------------


async def _list_users(client, args: dict) -> Any:
    params: dict[str, Any] = {}
    query = args.get("query")
    if query is not None:
        params["query"] = query
    # Apply default limit
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    offset = args.get("offset")
    if offset is not None:
        params["offset"] = offset
    include_inactive = args.get("include_inactive")
    if include_inactive is not None:
        params["include_inactive"] = include_inactive
    compact = args.get("compact", False)
    result = await client.get("/users", params=params if params else None)
    return compact_response(result, compact)


_tool(
    name="kaiten_list_users",
    description=("List company users. Supports search, pagination, and filtering inactive users."),
    schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search filter for user names or emails.",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of users to return (default 50).",
            },
            "offset": {
                "type": "integer",
                "description": "Number of users to skip (for pagination).",
            },
            "include_inactive": {
                "type": "boolean",
                "description": "Include inactive (deactivated) users in results.",
            },
            "compact": {
                "type": "boolean",
                "description": "Return compact response without heavy fields (avatars, etc.).",
                "default": False,
            },
        },
    },
    handler=_list_users,
)


# ---------------------------------------------------------------------------
# kaiten_get_current_user
# ---------------------------------------------------------------------------


async def _get_current_user(client, args: dict) -> Any:
    return await client.get("/users/current")


_tool(
    name="kaiten_get_current_user",
    description="Get the current authenticated Kaiten user profile.",
    schema={
        "type": "object",
        "properties": {},
    },
    handler=_get_current_user,
)
