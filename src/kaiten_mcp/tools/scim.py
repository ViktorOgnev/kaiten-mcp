"""Kaiten SCIM v2 MCP tools."""

from typing import Any

from kaiten_mcp.tools.entity_helpers import register_direct_tool

TOOLS: dict[str, dict] = {}

SCIM_PAYLOAD: dict[str, Any] = {
    "type": "object",
    "description": "SCIM JSON payload. Sent as the request body.",
}


register_direct_tool(
    TOOLS,
    name="kaiten_list_scim_users",
    description="List SCIM users.",
    properties={
        "start_index": {"type": "integer", "description": "SCIM start index."},
        "count": {"type": "integer", "description": "SCIM page size."},
        "filter": {"type": "string", "description": "SCIM filter expression."},
    },
    method="GET",
    path_template="/scim/v2/Users",
    query_fields=("start_index", "count", "filter"),
    query_aliases={"start_index": "startIndex"},
    root_api=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_get_scim_user",
    description="Get a SCIM user.",
    properties={"user_id": {"type": "string", "description": "SCIM user ID."}},
    required=("user_id",),
    method="GET",
    path_template="/scim/v2/Users/{user_id}",
    path_fields=("user_id",),
    root_api=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_create_scim_user",
    description="Create a SCIM user.",
    properties={"payload": SCIM_PAYLOAD},
    required=("payload",),
    method="POST",
    path_template="/scim/v2/Users",
    include_payload=True,
    root_api=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_update_scim_user",
    description="Update a SCIM user.",
    properties={
        "user_id": {"type": "string", "description": "SCIM user ID."},
        "payload": SCIM_PAYLOAD,
    },
    required=("user_id", "payload"),
    method="PATCH",
    path_template="/scim/v2/Users/{user_id}",
    path_fields=("user_id",),
    include_payload=True,
    root_api=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_list_scim_groups",
    description="List SCIM groups.",
    properties={
        "start_index": {"type": "integer", "description": "SCIM start index."},
        "count": {"type": "integer", "description": "SCIM page size."},
        "filter": {"type": "string", "description": "SCIM filter expression."},
    },
    method="GET",
    path_template="/scim/v2/Groups",
    query_fields=("start_index", "count", "filter"),
    query_aliases={"start_index": "startIndex"},
    root_api=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_get_scim_group",
    description="Get a SCIM group.",
    properties={"group_id": {"type": "string", "description": "SCIM group ID."}},
    required=("group_id",),
    method="GET",
    path_template="/scim/v2/Groups/{group_id}",
    path_fields=("group_id",),
    root_api=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_create_scim_group",
    description="Create a SCIM group.",
    properties={"payload": SCIM_PAYLOAD},
    required=("payload",),
    method="POST",
    path_template="/scim/v2/Groups",
    include_payload=True,
    root_api=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_update_scim_group",
    description="Update a SCIM group.",
    properties={
        "group_id": {"type": "string", "description": "SCIM group ID."},
        "payload": SCIM_PAYLOAD,
    },
    required=("group_id", "payload"),
    method="PATCH",
    path_template="/scim/v2/Groups/{group_id}",
    path_fields=("group_id",),
    include_payload=True,
    root_api=True,
)
