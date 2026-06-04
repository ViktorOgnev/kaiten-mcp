"""Kaiten Catalog (custom directories) MCP tools."""

from typing import Any

from kaiten_mcp.tools.entity_helpers import register_direct_tool

TOOLS: dict[str, dict] = {}

DIRECTORY_ID: dict[str, Any] = {
    "type": "string",
    "description": "Custom directory ID (UUID).",
}
FIELD_ID: dict[str, Any] = {
    "type": "string",
    "description": "Custom directory field ID (UUID).",
}
RECORD_ID: dict[str, Any] = {
    "type": "string",
    "description": "Custom directory record ID (UUID).",
}
CONDITIONS: dict[str, Any] = {
    "type": "array",
    "description": 'Condition filters, for example ["active", "inactive", "removed"].',
}
PAYLOAD: dict[str, Any] = {
    "type": "object",
    "description": "Extra JSON body fields from the Kaiten API docs.",
}


register_direct_tool(
    TOOLS,
    name="kaiten_list_custom_directories",
    description="List Kaiten Catalogs (custom directories).",
    properties={
        "include_fields": {"type": "boolean", "description": "Include directory fields."},
        "include_author": {"type": "boolean", "description": "Include author user object."},
        "include_records_count": {"type": "boolean", "description": "Include records_count."},
        "query": {"type": "string", "description": "Search by directory name."},
        "conditions": CONDITIONS,
        "limit": {"type": "integer", "description": "Max results, capped by Kaiten at 200."},
        "offset": {"type": "integer", "description": "Pagination offset."},
    },
    method="GET",
    path_template="/company/custom-directories",
    query_fields=(
        "include_fields",
        "include_author",
        "include_records_count",
        "query",
        "conditions",
        "limit",
        "offset",
    ),
    query_defaults={"limit": 200},
)

register_direct_tool(
    TOOLS,
    name="kaiten_get_custom_directory",
    description="Get a Kaiten Catalog (custom directory).",
    properties={
        "directory_id": DIRECTORY_ID,
        "include_fields": {"type": "boolean", "description": "Include directory fields."},
        "include_author": {"type": "boolean", "description": "Include author user object."},
        "include_records_count": {"type": "boolean", "description": "Include records_count."},
    },
    required=("directory_id",),
    method="GET",
    path_template="/company/custom-directories/{directory_id}",
    path_fields=("directory_id",),
    query_fields=("include_fields", "include_author", "include_records_count"),
)

register_direct_tool(
    TOOLS,
    name="kaiten_create_custom_directory",
    description="Create a Kaiten Catalog (custom directory).",
    properties={
        "name": {"type": "string", "description": "Directory name."},
        "description": {"type": ["string", "null"], "description": "Directory description."},
        "settings": {"type": "object", "description": "Directory settings."},
        "fields": {"type": "array", "description": "Initial directory fields."},
        "payload": PAYLOAD,
    },
    required=("name",),
    method="POST",
    path_template="/company/custom-directories",
    body_fields=("name", "description", "settings", "fields"),
    include_payload=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_update_custom_directory",
    description="Update a Kaiten Catalog (custom directory).",
    properties={
        "directory_id": DIRECTORY_ID,
        "name": {"type": "string", "description": "Directory name."},
        "description": {"type": ["string", "null"], "description": "Directory description."},
        "settings": {"type": "object", "description": "Directory settings."},
        "condition": {
            "type": "string",
            "enum": ["active", "inactive", "removed"],
            "description": "Directory condition.",
        },
        "payload": PAYLOAD,
    },
    required=("directory_id",),
    method="PATCH",
    path_template="/company/custom-directories/{directory_id}",
    path_fields=("directory_id",),
    body_fields=("name", "description", "settings", "condition"),
    include_payload=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_delete_custom_directory",
    description="Delete a Kaiten Catalog (custom directory).",
    properties={"directory_id": DIRECTORY_ID},
    required=("directory_id",),
    method="DELETE",
    path_template="/company/custom-directories/{directory_id}",
    path_fields=("directory_id",),
)

register_direct_tool(
    TOOLS,
    name="kaiten_list_custom_directory_fields",
    description="List fields (columns) of a Kaiten Catalog.",
    properties={
        "directory_id": DIRECTORY_ID,
        "include_author": {"type": "boolean", "description": "Include author user object."},
        "conditions": CONDITIONS,
    },
    required=("directory_id",),
    method="GET",
    path_template="/company/custom-directories/{directory_id}/fields",
    path_fields=("directory_id",),
    query_fields=("include_author", "conditions"),
)

register_direct_tool(
    TOOLS,
    name="kaiten_get_custom_directory_field",
    description="Get a field (column) of a Kaiten Catalog.",
    properties={"directory_id": DIRECTORY_ID, "field_id": FIELD_ID},
    required=("directory_id", "field_id"),
    method="GET",
    path_template="/company/custom-directories/{directory_id}/fields/{field_id}",
    path_fields=("directory_id", "field_id"),
)

register_direct_tool(
    TOOLS,
    name="kaiten_create_custom_directory_field",
    description="Create a field (column) in a Kaiten Catalog.",
    properties={
        "directory_id": DIRECTORY_ID,
        "name": {"type": "string", "description": "Field name."},
        "type": {"type": "string", "description": "Field type."},
        "required": {"type": "boolean", "description": "Whether the field is required."},
        "is_display": {"type": "boolean", "description": "Whether it is the display field."},
        "sort_order": {"type": "number", "description": "Field sort order."},
        "settings": {"type": "object", "description": "Type-specific field settings."},
        "payload": PAYLOAD,
    },
    required=("directory_id", "name", "type"),
    method="POST",
    path_template="/company/custom-directories/{directory_id}/fields",
    path_fields=("directory_id",),
    body_fields=("name", "type", "required", "is_display", "sort_order", "settings"),
    include_payload=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_update_custom_directory_field",
    description="Update a field (column) in a Kaiten Catalog.",
    properties={
        "directory_id": DIRECTORY_ID,
        "field_id": FIELD_ID,
        "name": {"type": "string", "description": "Field name."},
        "required": {"type": "boolean", "description": "Whether the field is required."},
        "is_display": {"type": "boolean", "description": "Whether it is the display field."},
        "sort_order": {"type": "number", "description": "Field sort order."},
        "condition": {
            "type": "string",
            "enum": ["active", "inactive", "removed"],
            "description": "Field condition.",
        },
        "settings": {"type": "object", "description": "Type-specific field settings."},
        "payload": PAYLOAD,
    },
    required=("directory_id", "field_id"),
    method="PATCH",
    path_template="/company/custom-directories/{directory_id}/fields/{field_id}",
    path_fields=("directory_id", "field_id"),
    body_fields=("name", "required", "is_display", "sort_order", "condition", "settings"),
    include_payload=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_delete_custom_directory_field",
    description="Delete a field (column) from a Kaiten Catalog.",
    properties={"directory_id": DIRECTORY_ID, "field_id": FIELD_ID},
    required=("directory_id", "field_id"),
    method="DELETE",
    path_template="/company/custom-directories/{directory_id}/fields/{field_id}",
    path_fields=("directory_id", "field_id"),
)

register_direct_tool(
    TOOLS,
    name="kaiten_list_custom_directory_records",
    description="List records (rows) of a Kaiten Catalog.",
    properties={
        "directory_id": DIRECTORY_ID,
        "query": {"type": "string", "description": "Quick search by display value."},
        "profile": {
            "type": "string",
            "enum": ["none", "summary", "details", "full"],
            "description": "Controls included relations.",
        },
        "include_values": {"type": "boolean", "description": "Include values array."},
        "include_author": {"type": "boolean", "description": "Include author user object."},
        "conditions": CONDITIONS,
        "filters": {"type": "object", "description": "Advanced field-based filters."},
        "filter_operator": {
            "type": "string",
            "enum": ["and", "or"],
            "description": "Boolean operator for filters.",
        },
        "limit": {"type": "integer", "description": "Max results, capped by Kaiten at 100."},
        "offset": {"type": "integer", "description": "Pagination offset."},
    },
    required=("directory_id",),
    method="GET",
    path_template="/company/custom-directories/{directory_id}/records",
    path_fields=("directory_id",),
    query_fields=(
        "query",
        "profile",
        "include_values",
        "include_author",
        "conditions",
        "filters",
        "filter_operator",
        "limit",
        "offset",
    ),
    query_defaults={"limit": 100},
    encode_json_query_fields=("filters",),
)

register_direct_tool(
    TOOLS,
    name="kaiten_get_custom_directory_record",
    description="Get a record (row) from a Kaiten Catalog.",
    properties={
        "directory_id": DIRECTORY_ID,
        "record_id": RECORD_ID,
        "profile": {
            "type": "string",
            "enum": ["none", "summary", "details", "full"],
            "description": "Controls included relations.",
        },
    },
    required=("directory_id", "record_id"),
    method="GET",
    path_template="/company/custom-directories/{directory_id}/records/{record_id}",
    path_fields=("directory_id", "record_id"),
    query_fields=("profile",),
)

register_direct_tool(
    TOOLS,
    name="kaiten_create_custom_directory_record",
    description="Create a record (row) in a Kaiten Catalog.",
    properties={
        "directory_id": DIRECTORY_ID,
        "values": {"type": ["object", "array"], "description": "Field values for the record."},
        "payload": PAYLOAD,
    },
    required=("directory_id", "values"),
    method="POST",
    path_template="/company/custom-directories/{directory_id}/records",
    path_fields=("directory_id",),
    body_fields=("values",),
    include_payload=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_update_custom_directory_record",
    description="Update a record (row) in a Kaiten Catalog.",
    properties={
        "directory_id": DIRECTORY_ID,
        "record_id": RECORD_ID,
        "values": {"type": ["object", "array"], "description": "Field values for the record."},
        "condition": {
            "type": "string",
            "enum": ["active", "inactive", "removed"],
            "description": "Record condition.",
        },
        "payload": PAYLOAD,
    },
    required=("directory_id", "record_id"),
    method="PATCH",
    path_template="/company/custom-directories/{directory_id}/records/{record_id}",
    path_fields=("directory_id", "record_id"),
    body_fields=("values", "condition"),
    include_payload=True,
)

register_direct_tool(
    TOOLS,
    name="kaiten_delete_custom_directory_record",
    description="Delete a record (row) from a Kaiten Catalog.",
    properties={"directory_id": DIRECTORY_ID, "record_id": RECORD_ID},
    required=("directory_id", "record_id"),
    method="DELETE",
    path_template="/company/custom-directories/{directory_id}/records/{record_id}",
    path_fields=("directory_id", "record_id"),
)

register_direct_tool(
    TOOLS,
    name="kaiten_list_custom_directory_record_cards",
    description="List cards linked to a Kaiten Catalog record.",
    properties={
        "directory_id": DIRECTORY_ID,
        "record_id": RECORD_ID,
        "filter": {"type": "string", "description": "Base64-encoded JSON card filter."},
        "limit": {"type": "integer", "description": "Max results, capped by Kaiten at 100."},
        "offset": {"type": "integer", "description": "Pagination offset."},
    },
    required=("directory_id", "record_id"),
    method="GET",
    path_template="/company/custom-directories/{directory_id}/records/{record_id}/cards",
    path_fields=("directory_id", "record_id"),
    query_fields=("filter", "limit", "offset"),
    query_defaults={"limit": 100},
)
