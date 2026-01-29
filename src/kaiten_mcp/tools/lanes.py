"""Kaiten Lanes MCP tools."""
from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


async def _list_lanes(client, args: dict) -> Any:
    return await client.get(f"/boards/{args['board_id']}/lanes")


_tool(
    "kaiten_list_lanes",
    "List lanes (swimlanes) on a Kaiten board.",
    {
        "type": "object",
        "properties": {
            "board_id": {"type": "integer", "description": "Board ID"},
        },
        "required": ["board_id"],
    },
    _list_lanes,
)


async def _create_lane(client, args: dict) -> Any:
    body = {"title": args["title"]}
    if args.get("sort_order") is not None:
        body["sort_order"] = args["sort_order"]
    return await client.post(f"/boards/{args['board_id']}/lanes", json=body)


_tool(
    "kaiten_create_lane",
    "Create a lane (swimlane) on a Kaiten board.",
    {
        "type": "object",
        "properties": {
            "board_id": {"type": "integer", "description": "Board ID"},
            "title": {"type": "string", "description": "Lane title"},
            "sort_order": {"type": "number", "description": "Sort order"},
        },
        "required": ["board_id", "title"],
    },
    _create_lane,
)


async def _update_lane(client, args: dict) -> Any:
    body = {}
    for key in ("title", "sort_order"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(
        f"/boards/{args['board_id']}/lanes/{args['lane_id']}", json=body
    )


_tool(
    "kaiten_update_lane",
    "Update a lane on a Kaiten board.",
    {
        "type": "object",
        "properties": {
            "board_id": {"type": "integer", "description": "Board ID"},
            "lane_id": {"type": "integer", "description": "Lane ID"},
            "title": {"type": "string", "description": "New title"},
            "sort_order": {"type": "number", "description": "Sort order"},
        },
        "required": ["board_id", "lane_id"],
    },
    _update_lane,
)


async def _delete_lane(client, args: dict) -> Any:
    return await client.delete(
        f"/boards/{args['board_id']}/lanes/{args['lane_id']}"
    )


_tool(
    "kaiten_delete_lane",
    "Delete a lane from a Kaiten board.",
    {
        "type": "object",
        "properties": {
            "board_id": {"type": "integer", "description": "Board ID"},
            "lane_id": {"type": "integer", "description": "Lane ID"},
        },
        "required": ["board_id", "lane_id"],
    },
    _delete_lane,
)
