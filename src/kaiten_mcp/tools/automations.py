"""Kaiten Automations & Workflows MCP tools."""
from typing import Any

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
        "action": args["action"],
    }
    if args.get("active") is not None:
        body["active"] = args["active"]
    return await client.post(f"/spaces/{args['space_id']}/automations", json=body)


_tool(
    "kaiten_create_automation",
    "Create a new automation in a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "name": {"type": "string", "description": "Automation name"},
            "trigger": {"type": "object", "description": "Trigger configuration"},
            "action": {"type": "object", "description": "Action configuration"},
            "active": {"type": "boolean", "description": "Whether the automation is active"},
        },
        "required": ["space_id", "name", "trigger", "action"],
    },
    _create_automation,
)


async def _get_automation(client, args: dict) -> Any:
    return await client.get(
        f"/spaces/{args['space_id']}/automations/{args['automation_id']}"
    )


_tool(
    "kaiten_get_automation",
    "Get a specific automation in a Kaiten space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "automation_id": {"type": "integer", "description": "Automation ID"},
        },
        "required": ["space_id", "automation_id"],
    },
    _get_automation,
)


async def _update_automation(client, args: dict) -> Any:
    body: dict[str, Any] = {}
    for key in ("name", "trigger", "action", "active"):
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
            "automation_id": {"type": "integer", "description": "Automation ID"},
            "name": {"type": "string", "description": "New automation name"},
            "trigger": {"type": "object", "description": "New trigger configuration"},
            "action": {"type": "object", "description": "New action configuration"},
            "active": {"type": "boolean", "description": "Whether the automation is active"},
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
            "automation_id": {"type": "integer", "description": "Automation ID"},
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
    for key in ("query", "limit", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get("/company/workflows", params=params or None)


_tool(
    "kaiten_list_workflows",
    "List company workflows. Supports search and pagination.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query string"},
            "limit": {"type": "integer", "description": "Maximum number of results"},
            "offset": {"type": "integer", "description": "Offset for pagination"},
        },
    },
    _list_workflows,
)


async def _create_workflow(client, args: dict) -> Any:
    body: dict[str, Any] = {"name": args["name"]}
    if args.get("description") is not None:
        body["description"] = args["description"]
    return await client.post("/company/workflows", json=body)


_tool(
    "kaiten_create_workflow",
    "Create a new company workflow.",
    {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Workflow name"},
            "description": {"type": "string", "description": "Workflow description"},
        },
        "required": ["name"],
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
            "workflow_id": {"type": "integer", "description": "Workflow ID"},
        },
        "required": ["workflow_id"],
    },
    _get_workflow,
)


async def _update_workflow(client, args: dict) -> Any:
    body: dict[str, Any] = {}
    for key in ("name", "description"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(f"/company/workflows/{args['workflow_id']}", json=body)


_tool(
    "kaiten_update_workflow",
    "Update a company workflow.",
    {
        "type": "object",
        "properties": {
            "workflow_id": {"type": "integer", "description": "Workflow ID"},
            "name": {"type": "string", "description": "New workflow name"},
            "description": {"type": "string", "description": "New workflow description"},
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
            "workflow_id": {"type": "integer", "description": "Workflow ID"},
        },
        "required": ["workflow_id"],
    },
    _delete_workflow,
)
