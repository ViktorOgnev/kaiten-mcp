"""Kaiten Card Files MCP tools."""

from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# ---------------------------------------------------------------------------
# kaiten_list_card_files
# ---------------------------------------------------------------------------


async def _list_card_files(client, args: dict) -> Any:
    return await client.get(f"/cards/{args['card_id']}/files")


_tool(
    "kaiten_list_card_files",
    "List all file attachments on a Kaiten card.",
    {
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "Card ID.",
            },
        },
        "required": ["card_id"],
    },
    _list_card_files,
)


# ---------------------------------------------------------------------------
# kaiten_create_card_file
# ---------------------------------------------------------------------------


async def _create_card_file(client, args: dict) -> Any:
    body: dict[str, Any] = {"url": args["url"], "name": args["name"]}
    for key in ("sort_order", "type", "size", "custom_property_id"):
        if args.get(key) is not None:
            body[key] = args[key]
    if args.get("card_cover") is not None:
        body["card_cover"] = args["card_cover"]
    return await client.post(f"/cards/{args['card_id']}/files", json=body)


_tool(
    "kaiten_create_card_file",
    (
        "Create a file attachment on a card by URL. "
        "This registers an external file link as a card attachment "
        "(does not upload binary data). "
        "File types: 1=attachment, 2=googleDrive, 3=dropBox, 4=box, 5=oneDrive, 6=yandexDisk."
    ),
    {
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "Card ID.",
            },
            "url": {
                "type": "string",
                "description": "URL of the file.",
            },
            "name": {
                "type": "string",
                "description": "Display name of the file.",
            },
            "type": {
                "type": "integer",
                "enum": [1, 2, 3, 4, 5, 6],
                "description": "File type: 1=attachment, 2=googleDrive, 3=dropBox, 4=box, 5=oneDrive, 6=yandexDisk.",
            },
            "size": {
                "type": "integer",
                "description": "File size in bytes.",
            },
            "sort_order": {
                "type": "number",
                "description": "Sort order of the file in the list.",
            },
            "custom_property_id": {
                "type": "integer",
                "description": "Custom property ID to associate the file with.",
            },
            "card_cover": {
                "type": "boolean",
                "description": "Set this file as the card cover image.",
            },
        },
        "required": ["card_id", "url", "name"],
    },
    _create_card_file,
)


# ---------------------------------------------------------------------------
# kaiten_update_card_file
# ---------------------------------------------------------------------------


async def _update_card_file(client, args: dict) -> Any:
    body: dict[str, Any] = {}
    for key in ("url", "name", "sort_order", "type", "size", "custom_property_id"):
        if args.get(key) is not None:
            body[key] = args[key]
    if args.get("card_cover") is not None:
        body["card_cover"] = args["card_cover"]
    return await client.patch(f"/cards/{args['card_id']}/files/{args['file_id']}", json=body)


_tool(
    "kaiten_update_card_file",
    "Update a file attachment on a card (name, URL, sort order, cover, etc.).",
    {
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "Card ID.",
            },
            "file_id": {
                "type": "integer",
                "description": "File ID.",
            },
            "url": {
                "type": "string",
                "description": "New URL of the file.",
            },
            "name": {
                "type": "string",
                "description": "New display name.",
            },
            "type": {
                "type": "integer",
                "enum": [1, 2, 3, 4, 5, 6],
                "description": "File type: 1=attachment, 2=googleDrive, 3=dropBox, 4=box, 5=oneDrive, 6=yandexDisk.",
            },
            "size": {
                "type": "integer",
                "description": "File size in bytes.",
            },
            "sort_order": {
                "type": "number",
                "description": "Sort order of the file in the list.",
            },
            "custom_property_id": {
                "type": "integer",
                "description": "Custom property ID to associate the file with.",
            },
            "card_cover": {
                "type": "boolean",
                "description": "Set this file as the card cover image.",
            },
        },
        "required": ["card_id", "file_id"],
    },
    _update_card_file,
)


# ---------------------------------------------------------------------------
# kaiten_delete_card_file
# ---------------------------------------------------------------------------


async def _delete_card_file(client, args: dict) -> Any:
    return await client.delete(f"/cards/{args['card_id']}/files/{args['file_id']}")


_tool(
    "kaiten_delete_card_file",
    "Delete a file attachment from a card. Files on blocked cards cannot be deleted.",
    {
        "type": "object",
        "properties": {
            "card_id": {
                "type": "integer",
                "description": "Card ID.",
            },
            "file_id": {
                "type": "integer",
                "description": "File ID.",
            },
        },
        "required": ["card_id", "file_id"],
    },
    _delete_card_file,
)
