"""Kaiten Service Desk MCP tools."""
from typing import Any

from kaiten_mcp.tools.compact import DEFAULT_LIMIT

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# --- SD Requests ---

async def _list_sd_requests(client, args: dict) -> Any:
    params = {}
    for key in ("query", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    return await client.get("/service-desk/requests", params=params)


_tool(
    "kaiten_list_sd_requests",
    "List Service Desk requests.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search filter"},
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_sd_requests,
)


async def _create_sd_request(client, args: dict) -> Any:
    body = {"title": args["title"], "service_id": args["service_id"]}
    for key in ("description", "priority"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.post("/service-desk/requests", json=body)


_tool(
    "kaiten_create_sd_request",
    "Create a new Service Desk request. Note: may return 405; request creation may only be available via the Service Desk portal.",
    {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Request title"},
            "service_id": {"type": "integer", "description": "Service ID"},
            "description": {"type": "string", "description": "Request description"},
            "priority": {"type": "string", "description": "Request priority"},
        },
        "required": ["title", "service_id"],
    },
    _create_sd_request,
)


async def _get_sd_request(client, args: dict) -> Any:
    return await client.get(f"/service-desk/requests/{args['request_id']}")


_tool(
    "kaiten_get_sd_request",
    "Get a Service Desk request by ID. Note: may return 405; use kaiten_list_sd_requests and filter client-side.",
    {
        "type": "object",
        "properties": {
            "request_id": {"type": "integer", "description": "Request ID"},
        },
        "required": ["request_id"],
    },
    _get_sd_request,
)


async def _update_sd_request(client, args: dict) -> Any:
    body = {}
    for key in ("title", "description", "priority"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(f"/service-desk/requests/{args['request_id']}", json=body)


_tool(
    "kaiten_update_sd_request",
    "Update a Service Desk request. Note: may return 405; request updates may only be available via the Service Desk portal.",
    {
        "type": "object",
        "properties": {
            "request_id": {"type": "integer", "description": "Request ID"},
            "title": {"type": "string", "description": "Request title"},
            "description": {"type": "string", "description": "Request description"},
            "priority": {"type": "string", "description": "Request priority"},
        },
        "required": ["request_id"],
    },
    _update_sd_request,
)


async def _delete_sd_request(client, args: dict) -> Any:
    return await client.delete(f"/service-desk/requests/{args['request_id']}")


_tool(
    "kaiten_delete_sd_request",
    "Delete a Service Desk request. Note: may return 405; request deletion may only be available via the Service Desk portal.",
    {
        "type": "object",
        "properties": {
            "request_id": {"type": "integer", "description": "Request ID"},
        },
        "required": ["request_id"],
    },
    _delete_sd_request,
)


# --- SD Services ---

async def _list_sd_services(client, args: dict) -> Any:
    params = {}
    for key in ("query", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    if args.get("include_archived"):
        params["include_archived"] = True
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    return await client.get("/service-desk/services", params=params)


_tool(
    "kaiten_list_sd_services",
    "List Service Desk services.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search filter"},
            "include_archived": {"type": "boolean", "description": "Include archived services"},
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_sd_services,
)


async def _get_sd_service(client, args: dict) -> Any:
    return await client.get(f"/service-desk/services/{args['service_id']}")


_tool(
    "kaiten_get_sd_service",
    "Get a Service Desk service by ID.",
    {
        "type": "object",
        "properties": {
            "service_id": {"type": "integer", "description": "Service ID"},
        },
        "required": ["service_id"],
    },
    _get_sd_service,
)


async def _create_sd_service(client, args: dict) -> Any:
    body = {
        "name": args["name"],
        "board_id": args["board_id"],
        "position": args["position"],
    }
    for key in ("description", "template_description", "lng", "display_status"):
        if args.get(key) is not None:
            body[key] = args[key]
    for key in ("column_id", "lane_id", "type_id", "email_settings"):
        if args.get(key) is not None:
            body[key] = args[key]
    for key in ("fields_settings", "settings"):
        if key in args:
            body[key] = args[key]
    for key in ("allow_to_add_external_recipients", "hide_in_list", "is_default"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.post("/service-desk/services", json=body)


_tool(
    "kaiten_create_sd_service",
    "Create a new Service Desk service.",
    {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Service name (max 256 chars)"},
            "board_id": {"type": "integer", "description": "Board ID where request cards are created"},
            "position": {"type": "integer", "description": "Sort position"},
            "description": {"type": "string", "description": "Service description"},
            "template_description": {"type": "string", "description": "Default description template for new requests"},
            "lng": {"type": "string", "description": "Language code (2-char, e.g. 'en', 'ru')", "enum": ["en", "ru"]},
            "display_status": {"type": "string", "description": "How status is displayed", "enum": ["by_column", "by_state"]},
            "column_id": {"type": "integer", "description": "Default column ID on the board"},
            "lane_id": {"type": "integer", "description": "Default lane ID on the board"},
            "type_id": {"type": "integer", "description": "Card type ID for created request cards"},
            "email_settings": {"type": "integer", "description": "Email notification settings bitmask (default 7)"},
            "fields_settings": {"type": "object", "description": "Custom property fields configuration for the request form (JSON)"},
            "settings": {"type": "object", "description": "Additional settings (e.g. {allowed_email_masks: [...]})"},
            "allow_to_add_external_recipients": {"type": "boolean", "description": "Allow adding external email recipients"},
            "hide_in_list": {"type": "boolean", "description": "Hide service in the public service list"},
            "is_default": {"type": "boolean", "description": "Set as the default service (only one allowed per company)"},
        },
        "required": ["name", "board_id", "position"],
    },
    _create_sd_service,
)


async def _update_sd_service(client, args: dict) -> Any:
    body = {}
    for key in ("name", "description", "template_description", "lng", "display_status"):
        if args.get(key) is not None:
            body[key] = args[key]
    for key in ("board_id", "column_id", "lane_id", "type_id", "position", "email_settings"):
        if args.get(key) is not None:
            body[key] = args[key]
    for key in ("fields_settings", "settings"):
        if key in args:
            body[key] = args[key]
    for key in ("archived", "allow_to_add_external_recipients", "hide_in_list"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(
        f"/service-desk/services/{args['service_id']}", json=body
    )


_tool(
    "kaiten_update_sd_service",
    "Update a Service Desk service.",
    {
        "type": "object",
        "properties": {
            "service_id": {"type": "integer", "description": "Service ID"},
            "name": {"type": "string", "description": "Service name (max 256 chars)"},
            "description": {"type": "string", "description": "Service description"},
            "template_description": {"type": "string", "description": "Default description template for new requests"},
            "lng": {"type": "string", "description": "Language code (2-char, e.g. 'en', 'ru')"},
            "display_status": {"type": "string", "description": "How status is displayed", "enum": ["by_column", "by_state"]},
            "board_id": {"type": "integer", "description": "Board ID where request cards are created"},
            "column_id": {"type": "integer", "description": "Default column ID on the board"},
            "lane_id": {"type": "integer", "description": "Default lane ID on the board"},
            "type_id": {"type": "integer", "description": "Card type ID for created request cards"},
            "position": {"type": "integer", "description": "Sort position"},
            "email_settings": {"type": "integer", "description": "Email notification settings bitmask"},
            "fields_settings": {"type": "object", "description": "Custom property fields configuration for the request form (JSON)"},
            "settings": {"type": "object", "description": "Additional settings (e.g. {allowed_email_masks: [...]})"},
            "archived": {"type": "boolean", "description": "Archive or unarchive the service"},
            "allow_to_add_external_recipients": {"type": "boolean", "description": "Allow adding external email recipients"},
            "hide_in_list": {"type": "boolean", "description": "Hide service in the public service list"},
        },
        "required": ["service_id"],
    },
    _update_sd_service,
)


async def _delete_sd_service(client, args: dict) -> Any:
    return await client.patch(
        f"/service-desk/services/{args['service_id']}", json={"archived": True}
    )


_tool(
    "kaiten_delete_sd_service",
    "Delete (archive) a Service Desk service.",
    {
        "type": "object",
        "properties": {
            "service_id": {"type": "integer", "description": "Service ID"},
        },
        "required": ["service_id"],
    },
    _delete_sd_service,
)


# --- SD Organizations ---

async def _list_sd_organizations(client, args: dict) -> Any:
    params = {}
    for key in ("query", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    if args.get("includeUsers") is not None:
        params["includeUsers"] = args["includeUsers"]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    return await client.get("/service-desk/organizations", params=params)


_tool(
    "kaiten_list_sd_organizations",
    "List Service Desk organizations.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search filter"},
            "includeUsers": {"type": "boolean", "description": "Include organization users in response"},
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_sd_organizations,
)


async def _create_sd_organization(client, args: dict) -> Any:
    body = {"name": args["name"]}
    if args.get("description") is not None:
        body["description"] = args["description"]
    return await client.post("/service-desk/organizations", json=body)


_tool(
    "kaiten_create_sd_organization",
    "Create a new Service Desk organization.",
    {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Organization name (max 256 chars)"},
            "description": {"type": "string", "description": "Organization description (max 1024 chars)"},
        },
        "required": ["name"],
    },
    _create_sd_organization,
)


async def _get_sd_organization(client, args: dict) -> Any:
    return await client.get(f"/service-desk/organizations/{args['organization_id']}")


_tool(
    "kaiten_get_sd_organization",
    "Get a Service Desk organization by ID.",
    {
        "type": "object",
        "properties": {
            "organization_id": {"type": "integer", "description": "Organization ID"},
        },
        "required": ["organization_id"],
    },
    _get_sd_organization,
)


async def _update_sd_organization(client, args: dict) -> Any:
    body = {}
    for key in ("name", "description"):
        if key in args:
            body[key] = args[key]
    return await client.patch(
        f"/service-desk/organizations/{args['organization_id']}", json=body
    )


_tool(
    "kaiten_update_sd_organization",
    "Update a Service Desk organization.",
    {
        "type": "object",
        "properties": {
            "organization_id": {"type": "integer", "description": "Organization ID"},
            "name": {"type": "string", "description": "Organization name (max 256 chars)"},
            "description": {"type": "string", "description": "Organization description (max 1024 chars)"},
        },
        "required": ["organization_id"],
    },
    _update_sd_organization,
)


async def _delete_sd_organization(client, args: dict) -> Any:
    return await client.delete(
        f"/service-desk/organizations/{args['organization_id']}"
    )


_tool(
    "kaiten_delete_sd_organization",
    "Delete a Service Desk organization.",
    {
        "type": "object",
        "properties": {
            "organization_id": {"type": "integer", "description": "Organization ID"},
        },
        "required": ["organization_id"],
    },
    _delete_sd_organization,
)


# --- SD SLA ---

async def _list_sd_sla(client, args: dict) -> Any:
    params = {}
    if args.get("offset") is not None:
        params["offset"] = args["offset"]
    params["limit"] = args.get("limit", DEFAULT_LIMIT)
    return await client.get("/service-desk/sla", params=params)


_tool(
    "kaiten_list_sd_sla",
    "List Service Desk SLA policies.",
    {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "Max results"},
            "offset": {"type": "integer", "description": "Pagination offset"},
        },
    },
    _list_sd_sla,
)


async def _get_sd_sla(client, args: dict) -> Any:
    return await client.get(f"/service-desk/sla/{args['sla_id']}")


_tool(
    "kaiten_get_sd_sla",
    "Get a Service Desk SLA policy by ID.",
    {
        "type": "object",
        "properties": {
            "sla_id": {"type": "string", "description": "SLA ID (UUID)"},
        },
        "required": ["sla_id"],
    },
    _get_sd_sla,
)


async def _create_sd_sla(client, args: dict) -> Any:
    body = {"name": args["name"], "rules": args["rules"]}
    if args.get("notification_settings") is not None:
        body["notification_settings"] = args["notification_settings"]
    if args.get("v2") is not None:
        body["v2"] = args["v2"]
    return await client.post("/service-desk/sla", json=body)


_tool(
    "kaiten_create_sd_sla",
    "Create a new Service Desk SLA policy.",
    {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "SLA policy name"},
            "rules": {
                "type": "array",
                "description": "SLA rules (conditions and time targets)",
                "items": {"type": "object"},
            },
            "notification_settings": {"type": "object", "description": "Notification configuration"},
            "v2": {"type": "boolean", "description": "Use v2 SLA format"},
        },
        "required": ["name", "rules"],
    },
    _create_sd_sla,
)


async def _update_sd_sla(client, args: dict) -> Any:
    body = {}
    for key in ("name", "status"):
        if args.get(key) is not None:
            body[key] = args[key]
    if "notification_settings" in args:
        body["notification_settings"] = args["notification_settings"]
    if args.get("should_delete_sla_from_cards") is not None:
        body["should_delete_sla_from_cards"] = args["should_delete_sla_from_cards"]
    return await client.patch(f"/service-desk/sla/{args['sla_id']}", json=body)


_tool(
    "kaiten_update_sd_sla",
    "Update a Service Desk SLA policy.",
    {
        "type": "object",
        "properties": {
            "sla_id": {"type": "string", "description": "SLA ID (UUID)"},
            "name": {"type": "string", "description": "SLA policy name"},
            "status": {"type": "string", "description": "SLA status"},
            "notification_settings": {"type": "object", "description": "Notification configuration"},
            "should_delete_sla_from_cards": {"type": "boolean", "description": "Remove SLA from cards when deactivating"},
        },
        "required": ["sla_id"],
    },
    _update_sd_sla,
)


async def _delete_sd_sla(client, args: dict) -> Any:
    return await client.delete(f"/service-desk/sla/{args['sla_id']}")


_tool(
    "kaiten_delete_sd_sla",
    "Delete a Service Desk SLA policy.",
    {
        "type": "object",
        "properties": {
            "sla_id": {"type": "string", "description": "SLA ID (UUID)"},
        },
        "required": ["sla_id"],
    },
    _delete_sd_sla,
)


# --- SD Template Answers ---

async def _list_sd_template_answers(client, args: dict) -> Any:
    return await client.get("/service-desk/template-answers")


_tool(
    "kaiten_list_sd_template_answers",
    "List Service Desk template answers.",
    {
        "type": "object",
        "properties": {},
    },
    _list_sd_template_answers,
)


async def _get_sd_template_answer(client, args: dict) -> Any:
    return await client.get(
        f"/service-desk/template-answers/{args['template_answer_id']}"
    )


_tool(
    "kaiten_get_sd_template_answer",
    "Get a Service Desk template answer by ID.",
    {
        "type": "object",
        "properties": {
            "template_answer_id": {"type": "string", "description": "Template answer ID (UUID)"},
        },
        "required": ["template_answer_id"],
    },
    _get_sd_template_answer,
)


async def _create_sd_template_answer(client, args: dict) -> Any:
    body = {"name": args["name"], "text": args["text"]}
    return await client.post("/service-desk/template-answers", json=body)


_tool(
    "kaiten_create_sd_template_answer",
    "Create a new Service Desk template answer.",
    {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Template name (max 256 chars)"},
            "text": {"type": "string", "description": "Template answer text"},
        },
        "required": ["name", "text"],
    },
    _create_sd_template_answer,
)


async def _update_sd_template_answer(client, args: dict) -> Any:
    body = {}
    for key in ("name", "text"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.patch(
        f"/service-desk/template-answers/{args['template_answer_id']}", json=body
    )


_tool(
    "kaiten_update_sd_template_answer",
    "Update a Service Desk template answer.",
    {
        "type": "object",
        "properties": {
            "template_answer_id": {"type": "string", "description": "Template answer ID (UUID)"},
            "name": {"type": "string", "description": "Template name (max 256 chars)"},
            "text": {"type": "string", "description": "Template answer text"},
        },
        "required": ["template_answer_id"],
    },
    _update_sd_template_answer,
)


async def _delete_sd_template_answer(client, args: dict) -> Any:
    return await client.delete(
        f"/service-desk/template-answers/{args['template_answer_id']}"
    )


_tool(
    "kaiten_delete_sd_template_answer",
    "Delete a Service Desk template answer.",
    {
        "type": "object",
        "properties": {
            "template_answer_id": {"type": "string", "description": "Template answer ID (UUID)"},
        },
        "required": ["template_answer_id"],
    },
    _delete_sd_template_answer,
)
