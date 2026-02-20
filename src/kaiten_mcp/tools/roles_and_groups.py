"""Kaiten Roles, Groups & Space Users MCP tools."""

from typing import Any

from kaiten_mcp.tools.compact import DEFAULT_LIMIT, compact_response

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# ---------------------------------------------------------------------------
# Space Users
# ---------------------------------------------------------------------------


async def _list_space_users(client, args: dict) -> Any:
    compact = args.get("compact", False)
    result = await client.get(f"/spaces/{args['space_id']}/users")
    return compact_response(result, compact)


_tool(
    "kaiten_list_space_users",
    "List users of a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "compact": {
                "type": "boolean",
                "description": "Return compact response without heavy fields (avatars, nested user objects).",
                "default": False,
            },
        },
        "required": ["space_id"],
    },
    _list_space_users,
)


async def _add_space_user(client, args: dict) -> Any:
    body: dict[str, Any] = {"user_id": args["user_id"]}
    if args.get("role_id") is not None:
        body["role_id"] = args["role_id"]
    return await client.post(f"/spaces/{args['space_id']}/users", json=body)


_tool(
    "kaiten_add_space_user",
    "Add a user to a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "user_id": {"type": "integer", "description": "User ID to add"},
            "role_id": {"type": "integer", "description": "Role ID to assign"},
        },
        "required": ["space_id", "user_id"],
    },
    _add_space_user,
)


async def _update_space_user(client, args: dict) -> Any:
    body: dict[str, Any] = {}
    if args.get("role_id") is not None:
        body["role_id"] = args["role_id"]
    return await client.patch(f"/spaces/{args['space_id']}/users/{args['user_id']}", json=body)


_tool(
    "kaiten_update_space_user",
    "Update a user's role in a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "user_id": {"type": "integer", "description": "User ID to update"},
            "role_id": {"type": "integer", "description": "New role ID"},
        },
        "required": ["space_id", "user_id"],
    },
    _update_space_user,
)


async def _remove_space_user(client, args: dict) -> Any:
    return await client.delete(f"/spaces/{args['space_id']}/users/{args['user_id']}")


_tool(
    "kaiten_remove_space_user",
    "Remove a user from a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "user_id": {"type": "integer", "description": "User ID to remove"},
        },
        "required": ["space_id", "user_id"],
    },
    _remove_space_user,
)


# ---------------------------------------------------------------------------
# Company Groups
# ---------------------------------------------------------------------------


async def _list_company_groups(client, args: dict) -> Any:
    params: dict[str, Any] = {}
    if args.get("query") is not None:
        params["query"] = args["query"]
    if args.get("offset") is not None:
        params["offset"] = args["offset"]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    return await client.get("/company/groups", params=params)


_tool(
    "kaiten_list_company_groups",
    "List company groups in Kaiten.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "limit": {"type": "integer", "description": "Max results to return"},
            "offset": {"type": "integer", "description": "Offset for pagination"},
        },
    },
    _list_company_groups,
)


async def _create_company_group(client, args: dict) -> Any:
    body: dict[str, Any] = {"name": args["name"]}
    return await client.post("/company/groups", json=body)


_tool(
    "kaiten_create_company_group",
    "Create a new company group in Kaiten.",
    {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Group name"},
        },
        "required": ["name"],
    },
    _create_company_group,
)


async def _get_company_group(client, args: dict) -> Any:
    return await client.get(f"/company/groups/{args['group_uid']}")


_tool(
    "kaiten_get_company_group",
    "Get a company group by UID.",
    {
        "type": "object",
        "properties": {
            "group_uid": {"type": "string", "description": "Group UID"},
        },
        "required": ["group_uid"],
    },
    _get_company_group,
)


async def _update_company_group(client, args: dict) -> Any:
    body: dict[str, Any] = {}
    if args.get("name") is not None:
        body["name"] = args["name"]
    return await client.patch(f"/company/groups/{args['group_uid']}", json=body)


_tool(
    "kaiten_update_company_group",
    "Update a company group in Kaiten.",
    {
        "type": "object",
        "properties": {
            "group_uid": {"type": "string", "description": "Group UID"},
            "name": {"type": "string", "description": "New group name"},
        },
        "required": ["group_uid"],
    },
    _update_company_group,
)


async def _delete_company_group(client, args: dict) -> Any:
    return await client.delete(f"/company/groups/{args['group_uid']}")


_tool(
    "kaiten_delete_company_group",
    "Delete a company group in Kaiten.",
    {
        "type": "object",
        "properties": {
            "group_uid": {"type": "string", "description": "Group UID"},
        },
        "required": ["group_uid"],
    },
    _delete_company_group,
)


async def _list_group_users(client, args: dict) -> Any:
    compact = args.get("compact", False)
    result = await client.get(f"/groups/{args['group_uid']}/users")
    return compact_response(result, compact)


_tool(
    "kaiten_list_group_users",
    "List users in a company group.",
    {
        "type": "object",
        "properties": {
            "group_uid": {"type": "string", "description": "Group UID"},
            "compact": {
                "type": "boolean",
                "description": "Return compact response without heavy fields (avatars, nested user objects).",
                "default": False,
            },
        },
        "required": ["group_uid"],
    },
    _list_group_users,
)


async def _add_group_user(client, args: dict) -> Any:
    body: dict[str, Any] = {"user_id": args["user_id"]}
    return await client.post(f"/groups/{args['group_uid']}/users", json=body)


_tool(
    "kaiten_add_group_user",
    "Add a user to a company group.",
    {
        "type": "object",
        "properties": {
            "group_uid": {"type": "string", "description": "Group UID"},
            "user_id": {"type": "integer", "description": "User ID to add"},
        },
        "required": ["group_uid", "user_id"],
    },
    _add_group_user,
)


async def _remove_group_user(client, args: dict) -> Any:
    return await client.delete(f"/groups/{args['group_uid']}/users/{args['user_id']}")


_tool(
    "kaiten_remove_group_user",
    "Remove a user from a company group.",
    {
        "type": "object",
        "properties": {
            "group_uid": {"type": "string", "description": "Group UID"},
            "user_id": {"type": "integer", "description": "User ID to remove"},
        },
        "required": ["group_uid", "user_id"],
    },
    _remove_group_user,
)


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------


async def _list_roles(client, args: dict) -> Any:
    params: dict[str, Any] = {}
    if args.get("query") is not None:
        params["query"] = args["query"]
    if args.get("offset") is not None:
        params["offset"] = args["offset"]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    return await client.get("/tree-entity-roles", params=params)


_tool(
    "kaiten_list_roles",
    "List available roles in Kaiten.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "limit": {"type": "integer", "description": "Max results to return"},
            "offset": {"type": "integer", "description": "Offset for pagination"},
        },
    },
    _list_roles,
)


async def _get_role(client, args: dict) -> Any:
    return await client.get(f"/tree-entity-roles/{args['role_id']}")


_tool(
    "kaiten_get_role",
    "Get a role by ID.",
    {
        "type": "object",
        "properties": {
            "role_id": {"type": "string", "description": "Role ID (UUID)"},
        },
        "required": ["role_id"],
    },
    _get_role,
)
