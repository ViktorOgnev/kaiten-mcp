"""Kaiten Service Desk MCP tools."""
from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# --- SD Requests ---

async def _list_sd_requests(client, args: dict) -> Any:
    params = {}
    for key in ("query", "limit", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get("/service-desk/requests", params=params or None)


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
    for key in ("query", "limit", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get("/service-desk/services", params=params or None)


_tool(
    "kaiten_list_sd_services",
    "List Service Desk services.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search filter"},
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


# --- SD Organizations ---

async def _list_sd_organizations(client, args: dict) -> Any:
    params = {}
    for key in ("query", "limit", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get("/service-desk/organizations", params=params or None)


_tool(
    "kaiten_list_sd_organizations",
    "List Service Desk organizations.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search filter"},
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
            "name": {"type": "string", "description": "Organization name"},
            "description": {"type": "string", "description": "Organization description"},
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
        if args.get(key) is not None:
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
            "name": {"type": "string", "description": "Organization name"},
            "description": {"type": "string", "description": "Organization description"},
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
    for key in ("limit", "offset"):
        if args.get(key) is not None:
            params[key] = args[key]
    return await client.get("/service-desk/sla", params=params or None)


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
            "sla_id": {"type": "integer", "description": "SLA ID"},
        },
        "required": ["sla_id"],
    },
    _get_sd_sla,
)
