"""Small helpers for direct Kaiten entity MCP tools."""

import json
from collections.abc import Iterable
from typing import Any

from kaiten_mcp.tools.compact import compact_response, select_fields


def json_schema(
    properties: dict[str, dict[str, Any]],
    required: Iterable[str] = (),
) -> dict[str, Any]:
    schema: dict[str, Any] = {"type": "object", "properties": properties}
    required_list = list(required)
    if required_list:
        schema["required"] = required_list
    return schema


def merge_payload(args: dict[str, Any], fields: Iterable[str]) -> dict[str, Any]:
    body = {field: args[field] for field in fields if args.get(field) is not None}
    payload = args.get("payload")
    if isinstance(payload, dict):
        body.update(payload)
    return body


def query_params(
    args: dict[str, Any],
    fields: Iterable[str],
    defaults: dict[str, Any] | None = None,
    aliases: dict[str, str] | None = None,
    encode_json_fields: Iterable[str] = (),
) -> dict[str, Any] | None:
    params = {field: args[field] for field in fields if args.get(field) is not None}
    if defaults:
        for key, value in defaults.items():
            params.setdefault(key, value)
    for key in encode_json_fields:
        if isinstance(params.get(key), dict):
            params[key] = json.dumps(params[key], ensure_ascii=False)
    if aliases:
        for source, target in aliases.items():
            if source in params:
                params[target] = params.pop(source)
    return params or None


def format_path(template: str, args: dict[str, Any], fields: Iterable[str]) -> str:
    values = {field: args[field] for field in fields}
    return template.format(**values)


def make_direct_handler(
    *,
    method: str,
    path_template: str,
    path_fields: Iterable[str] = (),
    query_fields: Iterable[str] = (),
    body_fields: Iterable[str] = (),
    query_defaults: dict[str, Any] | None = None,
    query_aliases: dict[str, str] | None = None,
    encode_json_query_fields: Iterable[str] = (),
    include_payload: bool = False,
    root_api: bool = False,
    compact_supported: bool = False,
    fields_supported: bool = False,
):
    async def handler(client, args: dict[str, Any]) -> Any:
        path = format_path(path_template, args, path_fields)
        params = query_params(
            args,
            query_fields,
            query_defaults,
            aliases=query_aliases,
            encode_json_fields=encode_json_query_fields,
        )
        body = merge_payload(args, body_fields) if body_fields or include_payload else None
        request_method = method.upper()

        if root_api:
            if request_method == "GET":
                result = await client.get_root(path, params=params)
            elif request_method == "POST":
                result = await client.post_root(path, json=body)
            elif request_method == "PATCH":
                result = await client.patch_root(path, json=body)
            elif request_method == "DELETE":
                result = await client.delete_root(path, json=body)
            else:
                raise ValueError(f"Unsupported root method: {method}")
        else:
            if request_method == "GET":
                result = await client.get(path, params=params)
            elif request_method == "POST":
                result = await client.post(path, json=body)
            elif request_method == "PATCH":
                result = await client.patch(path, json=body)
            elif request_method == "DELETE":
                result = await client.delete(path, json=body)
            else:
                raise ValueError(f"Unsupported method: {method}")

        if compact_supported:
            result = compact_response(result, args.get("compact", False))
        if fields_supported:
            result = select_fields(result, args.get("fields"))
        return result

    return handler


def register_direct_tool(
    tools: dict[str, dict],
    *,
    name: str,
    description: str,
    properties: dict[str, dict[str, Any]],
    required: Iterable[str] = (),
    method: str,
    path_template: str,
    path_fields: Iterable[str] = (),
    query_fields: Iterable[str] = (),
    body_fields: Iterable[str] = (),
    query_defaults: dict[str, Any] | None = None,
    query_aliases: dict[str, str] | None = None,
    encode_json_query_fields: Iterable[str] = (),
    include_payload: bool = False,
    root_api: bool = False,
    compact_supported: bool = False,
    fields_supported: bool = False,
) -> None:
    tools[name] = {
        "description": description,
        "inputSchema": json_schema(properties, required),
        "handler": make_direct_handler(
            method=method,
            path_template=path_template,
            path_fields=path_fields,
            query_fields=query_fields,
            body_fields=body_fields,
            query_defaults=query_defaults,
            query_aliases=query_aliases,
            encode_json_query_fields=encode_json_query_fields,
            include_payload=include_payload,
            root_api=root_api,
            compact_supported=compact_supported,
            fields_supported=fields_supported,
        ),
    }
