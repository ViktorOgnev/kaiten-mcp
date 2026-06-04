"""Kaiten Roles, Groups & Space Users MCP tools."""

from typing import Any

from kaiten_mcp.tools.compact import DEFAULT_LIMIT, compact_response
from kaiten_mcp.tools.entity_helpers import register_direct_tool

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

register_direct_tool(
    TOOLS,
    name="kaiten_get_space_user",
    description="Get a user in a Kaiten space.",
    properties={
        "space_id": {"type": "integer", "description": "Space ID"},
        "user_id": {"type": "integer", "description": "User ID"},
        "compact": {
            "type": "boolean",
            "description": "Return compact response without heavy fields.",
        },
    },
    required=("space_id", "user_id"),
    method="GET",
    path_template="/spaces/{space_id}/users/{user_id}",
    path_fields=("space_id", "user_id"),
    compact_supported=True,
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

register_direct_tool(
    TOOLS,
    name="kaiten_list_company_users",
    description=(
        "List company users from the administrative Members section. "
        "Defaults to for_members_section=true with paginated limit/offset."
    ),
    properties={
        "for_members_section": {
            "type": "boolean",
            "description": "Use the administrative Members section response shape.",
        },
        "query": {"type": "string", "description": "Search by email or full name"},
        "limit": {"type": "integer", "description": "Maximum number of users to return"},
        "offset": {"type": "integer", "description": "Number of users to skip"},
        "only_records_count": {"type": "boolean", "description": "Return only filtered count"},
        "access_type_permissions": {
            "type": "string",
            "enum": ["member", "guest", "denied"],
            "description": "Filter by Kaiten access type.",
        },
        "sd_access_type": {
            "type": "string",
            "enum": ["any", "has_access", "has_no_access"],
            "description": "Filter by Service Desk access.",
        },
        "take_licence": {
            "type": "string",
            "enum": ["any", "yes", "no"],
            "description": "Filter by users who take a paid license.",
        },
        "temporarily_inactive_status": {
            "type": "string",
            "enum": [
                "all_users",
                "only_temporarily_inactive_users",
                "only_active_users",
            ],
            "description": "Filter by temporary deactivation status.",
        },
        "group_ids": {"type": "array", "description": "Company group IDs."},
        "permissions": {"type": "array", "description": "Company permission criteria."},
        "compact": {"type": "boolean", "description": "Return compact response."},
        "fields": {"type": "string", "description": "Comma-separated field names per user."},
    },
    method="GET",
    path_template="/company/users",
    query_fields=(
        "for_members_section",
        "query",
        "limit",
        "offset",
        "only_records_count",
        "access_type_permissions",
        "sd_access_type",
        "take_licence",
        "temporarily_inactive_status",
        "group_ids",
        "permissions",
    ),
    query_defaults={"for_members_section": True, "offset": 0, "limit": 100},
    compact_supported=True,
    fields_supported=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_update_company_user",
    description="Update a company user.",
    properties={
        "user_id": {"type": "integer", "description": "User ID"},
        "full_name": {"type": "string", "description": "Full name"},
        "email": {"type": "string", "description": "Email"},
        "payload": {
            "type": "object",
            "description": "Extra JSON body fields from the Kaiten API docs.",
        },
    },
    required=("user_id",),
    method="PATCH",
    path_template="/company/users/{user_id}",
    path_fields=("user_id",),
    body_fields=("full_name", "email"),
    include_payload=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_remove_virtual_company_user",
    description="Remove a virtual company user.",
    properties={"user_id": {"type": "integer", "description": "Virtual user ID"}},
    required=("user_id",),
    method="DELETE",
    path_template="/company/users/{user_id}",
    path_fields=("user_id",),
)

register_direct_tool(
    TOOLS,
    name="kaiten_list_user_roles",
    description="List user roles.",
    properties={
        "query": {"type": "string", "description": "Search query"},
        "limit": {"type": "integer", "description": "Max results"},
        "offset": {"type": "integer", "description": "Pagination offset"},
    },
    method="GET",
    path_template="/user-roles",
    query_fields=("query", "limit", "offset"),
    query_defaults={"limit": DEFAULT_LIMIT},
)

register_direct_tool(
    TOOLS,
    name="kaiten_get_user_role",
    description="Get a user role.",
    properties={"role_id": {"type": "integer", "description": "User role ID"}},
    required=("role_id",),
    method="GET",
    path_template="/user-roles/{role_id}",
    path_fields=("role_id",),
)

register_direct_tool(
    TOOLS,
    name="kaiten_create_user_role",
    description="Create a user role.",
    properties={
        "name": {"type": "string", "description": "Role name"},
        "permissions": {"type": "object", "description": "Role permissions JSON."},
        "payload": {
            "type": "object",
            "description": "Extra JSON body fields from the Kaiten API docs.",
        },
    },
    required=("name",),
    method="POST",
    path_template="/user-roles",
    body_fields=("name", "permissions"),
    include_payload=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_update_user_role",
    description="Update a user role.",
    properties={
        "role_id": {"type": "integer", "description": "User role ID"},
        "name": {"type": "string", "description": "Role name"},
        "permissions": {"type": "object", "description": "Role permissions JSON."},
        "payload": {
            "type": "object",
            "description": "Extra JSON body fields from the Kaiten API docs.",
        },
    },
    required=("role_id",),
    method="PATCH",
    path_template="/user-roles/{role_id}",
    path_fields=("role_id",),
    body_fields=("name", "permissions"),
    include_payload=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_delete_user_role",
    description="Delete a user role.",
    properties={"role_id": {"type": "integer", "description": "User role ID"}},
    required=("role_id",),
    method="DELETE",
    path_template="/user-roles/{role_id}",
    path_fields=("role_id",),
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

register_direct_tool(
    TOOLS,
    name="kaiten_list_group_admins",
    description="List admins of a company group.",
    properties={
        "group_uid": {"type": "string", "description": "Group UID"},
        "compact": {"type": "boolean", "description": "Return compact response."},
    },
    required=("group_uid",),
    method="GET",
    path_template="/groups/{group_uid}/admins",
    path_fields=("group_uid",),
    compact_supported=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_add_group_admin",
    description="Add an admin to a company group.",
    properties={
        "group_uid": {"type": "string", "description": "Group UID"},
        "user_id": {"type": "integer", "description": "User ID to add as admin"},
    },
    required=("group_uid", "user_id"),
    method="POST",
    path_template="/groups/{group_uid}/admins",
    path_fields=("group_uid",),
    body_fields=("user_id",),
)

register_direct_tool(
    TOOLS,
    name="kaiten_remove_group_admin",
    description="Remove an admin from a company group.",
    properties={
        "group_uid": {"type": "string", "description": "Group UID"},
        "user_id": {"type": "integer", "description": "User ID to remove"},
    },
    required=("group_uid", "user_id"),
    method="DELETE",
    path_template="/groups/{group_uid}/admins/{user_id}",
    path_fields=("group_uid", "user_id"),
)

register_direct_tool(
    TOOLS,
    name="kaiten_list_group_entities",
    description="List tree entities attached to a company group.",
    properties={"group_uid": {"type": "string", "description": "Group UID"}},
    required=("group_uid",),
    method="GET",
    path_template="/company/groups/{group_uid}/entities",
    path_fields=("group_uid",),
)

register_direct_tool(
    TOOLS,
    name="kaiten_add_group_entity",
    description="Attach a tree entity to a company group.",
    properties={
        "group_uid": {"type": "string", "description": "Group UID"},
        "entity_uid": {"type": "string", "description": "Tree entity UID"},
        "role_ids": {"type": "array", "description": "Tree entity role IDs."},
        "payload": {
            "type": "object",
            "description": "Extra JSON body fields from the Kaiten API docs.",
        },
    },
    required=("group_uid", "entity_uid", "role_ids"),
    method="POST",
    path_template="/company/groups/{group_uid}/entities",
    path_fields=("group_uid",),
    body_fields=("entity_uid", "role_ids"),
    include_payload=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_update_group_entity",
    description="Update a tree entity attached to a company group.",
    properties={
        "group_uid": {"type": "string", "description": "Group UID"},
        "entity_uid": {"type": "string", "description": "Tree entity UID"},
        "role_ids": {"type": "array", "description": "Tree entity role IDs."},
        "payload": {
            "type": "object",
            "description": "Extra JSON body fields from the Kaiten API docs.",
        },
    },
    required=("group_uid", "entity_uid"),
    method="PATCH",
    path_template="/company/groups/{group_uid}/entities/{entity_uid}",
    path_fields=("group_uid", "entity_uid"),
    body_fields=("role_ids",),
    include_payload=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_remove_group_entity",
    description="Remove a tree entity from a company group.",
    properties={
        "group_uid": {"type": "string", "description": "Group UID"},
        "entity_uid": {"type": "string", "description": "Tree entity UID"},
    },
    required=("group_uid", "entity_uid"),
    method="DELETE",
    path_template="/company/groups/{group_uid}/entities/{entity_uid}",
    path_fields=("group_uid", "entity_uid"),
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
