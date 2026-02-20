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
    for key in ("conditions", "type", "sort_order", "source_automation_id"):
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
            "name": {"type": "string", "description": "Automation name (max 256 chars)"},
            "trigger": {
                "type": "object",
                "description": (
                    "Trigger configuration {type, data}. "
                    "Trigger types: card_created, card_moved_in_path, comment_posted, "
                    "card_user_added, responsible_added, card_type_changed, "
                    "checklists_completed, tag_added, tag_removed, card_state_changed, "
                    "custom_property_changed, due_date_changed, child_cards_state_changed, "
                    "checklist_item_checked, due_date_on_date, "
                    "checklist_item_due_date_on_date, custom_property_date_on_date, "
                    "blocked, unblocked, blocker_added, all_conditions_met"
                ),
            },
            "actions": {
                "type": "array",
                "items": {"type": "object"},
                "description": (
                    "List of action configurations [{type, data}]. "
                    "Action types: add_assignee, remove_assignee, move_to_path, "
                    "move_on_board, add_tag, remove_tags, add_card_users, add_property, "
                    "add_child_card, add_parent_card, connect_parent_card, "
                    "remove_card_users, change_asap, add_user_groups, add_size, "
                    "add_timeline, add_due_date, remove_due_date, "
                    "add_template_checklists, complete_checklists, sort_cards, "
                    "add_comment, card_add_sla, card_remove_sla, blocked, unblocked, "
                    "blocker_added, archive, change_custom_property_value, "
                    "property_add_to_child_card, change_type, change_service"
                ),
            },
            "conditions": {
                "type": "object",
                "description": (
                    "Conditions configuration. Top-level: {clause: 'and'|'or', "
                    "conditions: [...]}. Condition types: tag, target_tag, card_type, "
                    "new_card_type, updater, path, new_path, card_state, new_card_state, "
                    "comment, target_custom_property, custom_property, due_date, "
                    "new_due_date, new_child_cards_state, child_cards_state, "
                    "checklist_item_text, checklist_item_due_date, "
                    "checklist_item_checked_state, card_is_request, card_author, "
                    "block_status, relations, service, size"
                ),
            },
            "type": {
                "type": "string",
                "enum": ["on_action", "on_date", "on_demand", "on_workflow"],
                "description": "Automation type. Default: on_action",
            },
            "sort_order": {
                "type": "number",
                "description": "Sort position of the automation within the space.",
            },
            "source_automation_id": {
                "type": "string",
                "description": "UUID of an existing automation to copy. When set, the automation is cloned from the source instead of being created from trigger/actions.",
            },
        },
        "required": ["space_id", "name", "trigger", "actions"],
    },
    _create_automation,
)


async def _get_automation(client, args: dict) -> Any:
    return await client.get(f"/spaces/{args['space_id']}/automations/{args['automation_id']}")


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
    for key in ("name", "trigger", "actions", "conditions", "status", "sort_order"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(
        f"/spaces/{args['space_id']}/automations/{args['automation_id']}", json=body
    )


_tool(
    "kaiten_update_automation",
    "Update an automation in a Kaiten space. Cannot update automations of type 'on_workflow' (use Workflow API instead).",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "automation_id": {"type": "string", "description": "Automation ID (UUID)"},
            "name": {"type": "string", "description": "New automation name (max 256 chars)"},
            "trigger": {
                "type": "object",
                "description": (
                    "New trigger configuration {type, data}. See kaiten_create_automation "
                    "for supported trigger types."
                ),
            },
            "actions": {
                "type": "array",
                "items": {"type": "object"},
                "description": (
                    "New action configurations [{type, data}]. See kaiten_create_automation "
                    "for supported action types."
                ),
            },
            "conditions": {
                "type": "object",
                "description": (
                    "New conditions configuration {clause, conditions}. "
                    "See kaiten_create_automation for supported condition types."
                ),
            },
            "status": {
                "type": "string",
                "enum": ["active", "disabled"],
                "description": "Automation status (active or disabled).",
            },
            "sort_order": {
                "type": "number",
                "description": "Sort position of the automation within the space.",
            },
        },
        "required": ["space_id", "automation_id"],
    },
    _update_automation,
)


async def _delete_automation(client, args: dict) -> Any:
    return await client.delete(f"/spaces/{args['space_id']}/automations/{args['automation_id']}")


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


async def _copy_automation(client, args: dict) -> Any:
    body: dict[str, Any] = {"targetSpaceId": args["target_space_id"]}
    return await client.post(
        f"/spaces/{args['space_id']}/automations/{args['automation_id']}/copy",
        json=body,
    )


_tool(
    "kaiten_copy_automation",
    "Copy an automation to another space.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Source space ID"},
            "automation_id": {"type": "string", "description": "Automation ID (UUID) to copy"},
            "target_space_id": {
                "type": "integer",
                "description": "Target space ID to copy the automation into",
            },
        },
        "required": ["space_id", "automation_id", "target_space_id"],
    },
    _copy_automation,
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
