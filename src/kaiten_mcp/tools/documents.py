"""Kaiten Documents MCP tools."""
from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# --- Documents ---

async def _list_documents(client, args: dict) -> Any:
    params = {}
    for key in ("query", "limit", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get("/documents", params=params or None)


_tool(
    "kaiten_list_documents",
    "List Kaiten documents.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search filter"},
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_documents,
)


async def _create_document(client, args: dict) -> Any:
    body: dict[str, Any] = {"title": args["title"]}
    for key in ("parent_entity_uid", "sort_order", "key"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.post("/documents", json=body)


_tool(
    "kaiten_create_document",
    "Create a new Kaiten document.",
    {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Document title"},
            "parent_entity_uid": {"type": "string", "description": "Parent document group UID"},
            "sort_order": {"type": "integer", "description": "Sort order"},
            "key": {"type": "string", "description": "Unique key identifier"},
        },
        "required": ["title"],
    },
    _create_document,
)


async def _get_document(client, args: dict) -> Any:
    return await client.get(f"/documents/{args['document_uid']}")


_tool(
    "kaiten_get_document",
    "Get a Kaiten document by UID.",
    {
        "type": "object",
        "properties": {
            "document_uid": {"type": "string", "description": "Document UID"},
        },
        "required": ["document_uid"],
    },
    _get_document,
)


async def _update_document(client, args: dict) -> Any:
    body: dict[str, Any] = {}
    for key in ("title", "data", "parent_entity_uid", "sort_order", "key"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(f"/documents/{args['document_uid']}", json=body)


_tool(
    "kaiten_update_document",
    "Update a Kaiten document.",
    {
        "type": "object",
        "properties": {
            "document_uid": {"type": "string", "description": "Document UID"},
            "title": {"type": "string", "description": "New document title"},
            "data": {"type": "object", "description": "Document content (ProseMirror JSON)"},
            "parent_entity_uid": {"type": "string", "description": "New parent group UID"},
            "sort_order": {"type": "integer", "description": "Sort order"},
            "key": {"type": "string", "description": "Unique key identifier"},
        },
        "required": ["document_uid"],
    },
    _update_document,
)


async def _delete_document(client, args: dict) -> Any:
    return await client.delete(f"/documents/{args['document_uid']}")


_tool(
    "kaiten_delete_document",
    "Delete a Kaiten document.",
    {
        "type": "object",
        "properties": {
            "document_uid": {"type": "string", "description": "Document UID"},
        },
        "required": ["document_uid"],
    },
    _delete_document,
)


# --- Document Groups ---

async def _list_document_groups(client, args: dict) -> Any:
    params = {}
    for key in ("query", "limit", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get("/document-groups", params=params or None)


_tool(
    "kaiten_list_document_groups",
    "List Kaiten document groups.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search filter"},
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_document_groups,
)


async def _create_document_group(client, args: dict) -> Any:
    body: dict[str, Any] = {"title": args["title"]}
    if args.get("parent_entity_uid") is not None:
        body["parent_entity_uid"] = args["parent_entity_uid"]
    if args.get("sort_order") is not None:
        body["sort_order"] = args["sort_order"]
    return await client.post("/document-groups", json=body)


_tool(
    "kaiten_create_document_group",
    "Create a new Kaiten document group.",
    {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Group title"},
            "parent_entity_uid": {"type": "string", "description": "Parent group UID for nesting"},
            "sort_order": {"type": "integer", "description": "Sort order"},
        },
        "required": ["title"],
    },
    _create_document_group,
)


async def _get_document_group(client, args: dict) -> Any:
    return await client.get(f"/document-groups/{args['group_uid']}")


_tool(
    "kaiten_get_document_group",
    "Get a Kaiten document group by UID.",
    {
        "type": "object",
        "properties": {
            "group_uid": {"type": "string", "description": "Document group UID"},
        },
        "required": ["group_uid"],
    },
    _get_document_group,
)


async def _update_document_group(client, args: dict) -> Any:
    body = {}
    if args.get("title") is not None:
        body["title"] = args["title"]
    return await client.patch(f"/document-groups/{args['group_uid']}", json=body)


_tool(
    "kaiten_update_document_group",
    "Update a Kaiten document group.",
    {
        "type": "object",
        "properties": {
            "group_uid": {"type": "string", "description": "Document group UID"},
            "title": {"type": "string", "description": "New group title"},
        },
        "required": ["group_uid"],
    },
    _update_document_group,
)


async def _delete_document_group(client, args: dict) -> Any:
    return await client.delete(f"/document-groups/{args['group_uid']}")


_tool(
    "kaiten_delete_document_group",
    "Delete a Kaiten document group.",
    {
        "type": "object",
        "properties": {
            "group_uid": {"type": "string", "description": "Document group UID"},
        },
        "required": ["group_uid"],
    },
    _delete_document_group,
)
