"""Kaiten Documents MCP tools."""
import time
from typing import Any

TOOLS: dict[str, dict] = {}

DEFAULT_LIMIT = 50


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


def _extract_text_from_node(node: dict) -> str:
    """Extract all text from a ProseMirror node recursively."""
    if not isinstance(node, dict):
        return ""
    if node.get("type") == "text":
        return node.get("text", "")
    texts = []
    for child in node.get("content", []):
        texts.append(_extract_text_from_node(child))
    return "".join(texts)


def _sanitize_prosemirror(node: dict) -> dict | list:
    """
    Transform unsafe ProseMirror nodes that crash Kaiten API.

    Transforms:
    - bullet_list -> paragraphs with bullet prefix
    - ordered_list -> paragraphs with number prefix
    """
    if not isinstance(node, dict):
        return node

    node_type = node.get("type")

    # Transform lists into paragraphs (Kaiten API crashes on bullet_list/ordered_list)
    if node_type in ("bullet_list", "ordered_list"):
        paragraphs = []
        for i, item in enumerate(node.get("content", []), 1):
            prefix = "• " if node_type == "bullet_list" else f"{i}. "
            text = _extract_text_from_node(item)
            if text:  # Only add non-empty paragraphs
                paragraphs.append({
                    "type": "paragraph",
                    "content": [{"type": "text", "text": f"{prefix}{text}"}]
                })
        return paragraphs if paragraphs else [{"type": "paragraph", "content": []}]

    # Recursively process content
    if "content" in node:
        new_content = []
        for child in node["content"]:
            result = _sanitize_prosemirror(child)
            if isinstance(result, list):
                new_content.extend(result)
            else:
                new_content.append(result)
        node = {**node, "content": new_content}

    return node


# --- Documents ---

async def _list_documents(client, args: dict) -> Any:
    params = {}
    for key in ("query", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    return await client.get("/documents", params=params)


_tool(
    "kaiten_list_documents",
    "List Kaiten documents.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search filter"},
            "limit": {"type": "integer", "description": "Max results (default: 50)"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_documents,
)


async def _create_document(client, args: dict) -> Any:
    # sort_order is required by API even though schema says optional
    body: dict[str, Any] = {
        "title": args["title"],
        "sort_order": args.get("sort_order") or int(time.time()),
    }
    for key in ("parent_entity_uid", "key"):
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
            "sort_order": {"type": "integer", "description": "Sort order (auto-generated if not provided)"},
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
    for key in ("title", "parent_entity_uid", "sort_order", "key"):
        if args.get(key) is not None:
            body[key] = args[key]
    # Sanitize ProseMirror data to avoid API crashes on bullet_list/ordered_list
    if args.get("data") is not None:
        sanitized = _sanitize_prosemirror(args["data"])
        body["data"] = sanitized if isinstance(sanitized, dict) else args["data"]
    return await client.patch(f"/documents/{args['document_uid']}", json=body)


_tool(
    "kaiten_update_document",
    "Update a Kaiten document.",
    {
        "type": "object",
        "properties": {
            "document_uid": {"type": "string", "description": "Document UID"},
            "title": {"type": "string", "description": "New document title"},
            "data": {"type": "object", "description": "Document content (ProseMirror JSON). Lists are auto-converted to paragraphs."},
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
    for key in ("query", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    return await client.get("/document-groups", params=params)


_tool(
    "kaiten_list_document_groups",
    "List Kaiten document groups.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search filter"},
            "limit": {"type": "integer", "description": "Max results (default: 50)"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_document_groups,
)


async def _create_document_group(client, args: dict) -> Any:
    # sort_order is required by API even though schema says optional
    body: dict[str, Any] = {
        "title": args["title"],
        "sort_order": args.get("sort_order") or int(time.time()),
    }
    if args.get("parent_entity_uid") is not None:
        body["parent_entity_uid"] = args["parent_entity_uid"]
    return await client.post("/document-groups", json=body)


_tool(
    "kaiten_create_document_group",
    "Create a new Kaiten document group.",
    {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Group title"},
            "parent_entity_uid": {"type": "string", "description": "Parent group UID for nesting"},
            "sort_order": {"type": "integer", "description": "Sort order (auto-generated if not provided)"},
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
