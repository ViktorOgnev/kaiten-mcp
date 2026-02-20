"""Kaiten Entity Tree navigation tools."""

import asyncio
from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


async def _fetch_all_entities(client) -> list[dict]:
    """Fetch spaces, documents, and document groups in parallel and normalize."""
    spaces_resp, docs_resp, groups_resp = await asyncio.gather(
        client.get("/spaces"),
        client.get("/documents", params={"limit": 500}),
        client.get("/document-groups", params={"limit": 500}),
    )

    entities: list[dict] = []

    for space in spaces_resp if isinstance(spaces_resp, list) else []:
        uid = space.get("uid")
        if uid is None:
            continue
        entities.append(
            {
                "type": "space",
                "uid": uid,
                "id": space.get("id"),
                "title": space.get("title", ""),
                "parent_entity_uid": space.get("parent_entity_uid"),
            }
        )

    for doc in docs_resp if isinstance(docs_resp, list) else []:
        entities.append(  # noqa: PERF401 — multi-loop building shared list
            {
                "type": "document",
                "uid": doc.get("uid", ""),
                "id": None,
                "title": doc.get("title", ""),
                "parent_entity_uid": doc.get("parent_entity_uid"),
            }
        )

    for group in groups_resp if isinstance(groups_resp, list) else []:
        entities.append(  # noqa: PERF401 — multi-loop building shared list
            {
                "type": "document_group",
                "uid": group.get("uid", ""),
                "id": None,
                "title": group.get("title", ""),
                "parent_entity_uid": group.get("parent_entity_uid"),
            }
        )

    return entities


def _sort_entities(entities: list[dict]) -> list[dict]:
    """Sort entities by (type, title) for stable output."""
    type_order = {"document_group": 0, "space": 1, "document": 2}
    return sorted(entities, key=lambda e: (type_order.get(e["type"], 99), e.get("title", "")))


def _strip_id_none(entity: dict) -> dict:
    """Return entity dict, omitting 'id' key when it is None."""
    result = {k: v for k, v in entity.items() if not (k == "id" and v is None)}
    return result


# --- list_children ---


async def _list_children(client, args: dict) -> Any:
    parent_uid = args.get("parent_entity_uid")
    entities = await _fetch_all_entities(client)

    children = [e for e in entities if e.get("parent_entity_uid") == parent_uid]
    children = _sort_entities(children)
    return [_strip_id_none(e) for e in children]


_tool(
    "kaiten_list_children",
    "List direct children of an entity in the Kaiten sidebar tree. "
    "Without parent_entity_uid: returns root-level entities. "
    "With parent_entity_uid: returns direct children of that entity. "
    "Fetches spaces, documents, and document groups in parallel.",
    {
        "type": "object",
        "properties": {
            "parent_entity_uid": {
                "type": "string",
                "description": "Parent entity UID. Omit to list root-level entities.",
            },
        },
    },
    _list_children,
)


# --- get_tree ---


def _build_tree(entities: list[dict], root_uid: str | None, max_depth: int) -> list[dict]:
    """Build nested tree from flat entity list."""
    by_parent: dict[str | None, list[dict]] = {}
    for e in entities:
        parent = e.get("parent_entity_uid")
        by_parent.setdefault(parent, []).append(e)

    def _recurse(parent_uid: str | None, depth: int) -> list[dict]:
        children = by_parent.get(parent_uid, [])
        children = _sort_entities(children)
        result = []
        for child in children:
            node = _strip_id_none(child)
            node.pop("parent_entity_uid", None)
            if max_depth == 0 or depth < max_depth:
                node["children"] = _recurse(child["uid"], depth + 1)
            else:
                node["children"] = []
            result.append(node)
        return result

    return _recurse(root_uid, 0)


async def _get_tree(client, args: dict) -> Any:
    root_uid = args.get("root_uid")
    depth = args.get("depth", 0)
    entities = await _fetch_all_entities(client)

    if root_uid is not None:
        # Verify root exists
        root = next((e for e in entities if e["uid"] == root_uid), None)
        if root is None:
            raise ValueError(f"Entity with uid '{root_uid}' not found")

    return _build_tree(entities, root_uid, depth)


_tool(
    "kaiten_get_tree",
    "Build a nested entity tree from the Kaiten sidebar. "
    "Returns spaces, documents, and document groups as a recursive tree with 'children' arrays. "
    "Use root_uid to start from a specific entity. Use depth to limit recursion.",
    {
        "type": "object",
        "properties": {
            "root_uid": {
                "type": "string",
                "description": "Start tree from this entity UID. Omit for full tree from roots.",
            },
            "depth": {
                "type": "integer",
                "description": "Max recursion depth (0 = unlimited). Default: 0.",
                "default": 0,
            },
        },
    },
    _get_tree,
)
