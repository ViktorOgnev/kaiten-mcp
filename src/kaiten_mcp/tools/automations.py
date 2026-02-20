"""Kaiten Automations & Workflows MCP tools."""
from typing import Any

from kaiten_mcp.tools.compact import DEFAULT_LIMIT

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# ---------------------------------------------------------------------------
# Space Automations
# ---------------------------------------------------------------------------

async def _list_automations(client, args: dict) -> Any:
    return await client.get(f"/spaces/{args['space_id']}/automations")


_tool(
    "kaiten_list_automations",
    "List all automations for a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
        },
        "required": ["space_id"],
    },
    _list_automations,
)


async def _create_automation(client, args: dict) -> Any:
    body: dict[str, Any] = {
        "name": args["name"],
        "trigger": args["trigger"],
        "actions": args["actions"],
    }
    for key in ("conditions", "type"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.post(f"/spaces/{args['space_id']}/automations", json=body)


_tool(
    "kaiten_create_automation",
    "Create a new automation in a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "name": {"type": "string", "description": "Automation name"},
            "trigger": {"type": "object", "description": "Trigger configuration {type, data}"},
            "actions": {
                "type": "array",
                "items": {"type": "object"},
                "description": "List of action configurations [{type, data}]",
            },
            "conditions": {"type": "object", "description": "Conditions configuration"},
            "type": {
                "type": "string",
                "enum": ["on_action", "on_date", "on_demand", "on_workflow"],
                "description": "Automation type. Default: on_action",
            },
        },
        "required": ["space_id", "name", "trigger", "actions"],
    },
    _create_automation,
)


async def _get_automation(client, args: dict) -> Any:
    return await client.get(
        f"/spaces/{args['space_id']}/automations/{args['automation_id']}"
    )


_tool(
    "kaiten_get_automation",
    "Get a specific automation in a Kaiten space. Note: GET by ID may return 405; use kaiten_list_automations and filter client-side.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "automation_id": {"type": "string", "description": "Automation ID (UUID)"},
        },
        "required": ["space_id", "automation_id"],
    },
    _get_automation,
)


async def _update_automation(client, args: dict) -> Any:
    body: dict[str, Any] = {}
    for key in ("name", "trigger", "actions", "conditions", "status"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(
        f"/spaces/{args['space_id']}/automations/{args['automation_id']}", json=body
    )


_tool(
    "kaiten_update_automation",
    "Update an automation in a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "automation_id": {"type": "string", "description": "Automation ID (UUID)"},
            "name": {"type": "string", "description": "New automation name"},
            "trigger": {"type": "object", "description": "New trigger configuration"},
            "actions": {
                "type": "array",
                "items": {"type": "object"},
                "description": "New action configurations",
            },
            "conditions": {"type": "object", "description": "New conditions configuration"},
            "status": {
                "type": "string",
                "enum": ["active", "disabled"],
                "description": "Automation status (active or disabled)",
            },
        },
        "required": ["space_id", "automation_id"],
    },
    _update_automation,
)


async def _delete_automation(client, args: dict) -> Any:
    return await client.delete(
        f"/spaces/{args['space_id']}/automations/{args['automation_id']}"
    )


_tool(
    "kaiten_delete_automation",
    "Delete an automation from a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "automation_id": {"type": "string", "description": "Automation ID (UUID)"},
        },
        "required": ["space_id", "automation_id"],
    },
    _delete_automation,
)


# ---------------------------------------------------------------------------
# Company Workflows
# ---------------------------------------------------------------------------

async def _list_workflows(client, args: dict) -> Any:
    params: dict[str, Any] = {}
    if args.get("offset") is not None:
        params["offset"] = args["offset"]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    return await client.get("/company/workflows", params=params)


_tool(
    "kaiten_list_workflows",
    "List company workflows. Supports pagination.",
    {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "Maximum number of results"},
            "offset": {"type": "integer", "description": "Offset for pagination"},
        },
    },
    _list_workflows,
)


async def _create_workflow(client, args: dict) -> Any:
    body: dict[str, Any] = {
        "name": args["name"],
        "stages": args["stages"],
        "transitions": args["transitions"],
    }
    return await client.post("/company/workflows", json=body)


_tool(
    "kaiten_create_workflow",
    "Create a new company workflow. Requires at least 2 stages and 1 transition.",
    {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Workflow name (max 128 chars)"},
            "stages": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Workflow stages (min 2). Each: {id (uuid), name, type (queue/in_progress/done), position_data: {x, y}}",
            },
            "transitions": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Stage transitions (min 1). Each: {id (uuid), prev_stage_id, next_stage_id, position_data: {sourceHandle, targetHandle}}",
            },
        },
        "required": ["name", "stages", "transitions"],
    },
    _create_workflow,
)


async def _get_workflow(client, args: dict) -> Any:
    return await client.get(f"/company/workflows/{args['workflow_id']}")


_tool(
    "kaiten_get_workflow",
    "Get a specific company workflow by ID.",
    {
        "type": "object",
        "properties": {
            "workflow_id": {"type": "string", "description": "Workflow ID (UUID)"},
        },
        "required": ["workflow_id"],
    },
    _get_workflow,
)


async def _update_workflow(client, args: dict) -> Any:
    body: dict[str, Any] = {}
    for key in ("name", "stages", "transitions"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(f"/company/workflows/{args['workflow_id']}", json=body)


_tool(
    "kaiten_update_workflow",
    "Update a company workflow.",
    {
        "type": "object",
        "properties": {
            "workflow_id": {"type": "string", "description": "Workflow ID (UUID)"},
            "name": {"type": "string", "description": "New workflow name"},
            "stages": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Updated stages array",
            },
            "transitions": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Updated transitions array",
            },
        },
        "required": ["workflow_id"],
    },
    _update_workflow,
)


async def _delete_workflow(client, args: dict) -> Any:
    return await client.delete(f"/company/workflows/{args['workflow_id']}")


_tool(
    "kaiten_delete_workflow",
    "Delete a company workflow.",
    {
        "type": "object",
        "properties": {
            "workflow_id": {"type": "string", "description": "Workflow ID (UUID)"},
        },
        "required": ["workflow_id"],
    },
    _delete_workflow,
)
