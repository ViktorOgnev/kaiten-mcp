"""Kaiten Charts / Analytics MCP tools."""
from typing import Any

TOOLS: dict[str, dict] = {}


def _tool(name: str, description: str, schema: dict, handler):
    TOOLS[name] = {"description": description, "inputSchema": schema, "handler": handler}


# ---------------------------------------------------------------------------
# 1. kaiten_get_chart_boards  (GET, sync)
# ---------------------------------------------------------------------------

async def _get_chart_boards(client, args: dict) -> Any:
    space_id = args["space_id"]
    return await client.get(f"/charts/{space_id}/boards")


_tool(
    "kaiten_get_chart_boards",
    "Get board structure for chart configuration in a space. "
    "Returns boards with columns and lanes available for building charts.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
        },
        "required": ["space_id"],
    },
    _get_chart_boards,
)


# ---------------------------------------------------------------------------
# 2. kaiten_chart_summary  (POST, sync)
# ---------------------------------------------------------------------------

async def _chart_summary(client, args: dict) -> Any:
    body: dict[str, Any] = {
        "space_id": args["space_id"],
        "date_from": args["date_from"],
        "date_to": args["date_to"],
        "done_columns": args["done_columns"],
    }
    return await client.post("/charts/summary", json=body)


_tool(
    "kaiten_chart_summary",
    "Get done-card summary for a space within a date range. "
    "Returns aggregated statistics for cards that reached the specified done columns.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "date_from": {"type": "string", "description": "Start date (ISO 8601)"},
            "date_to": {"type": "string", "description": "End date (ISO 8601)"},
            "done_columns": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Array of done column IDs",
            },
        },
        "required": ["space_id", "date_from", "date_to", "done_columns"],
    },
    _chart_summary,
)


# ---------------------------------------------------------------------------
# 3. kaiten_chart_block_resolution  (POST, sync)
# ---------------------------------------------------------------------------

async def _chart_block_resolution(client, args: dict) -> Any:
    body: dict[str, Any] = {"space_id": args["space_id"]}
    if args.get("category_ids") is not None:
        body["category_ids"] = args["category_ids"]
    return await client.post("/charts/block-resolution-time-chart", json=body)


_tool(
    "kaiten_chart_block_resolution",
    "Get blocker resolution time data for a space. "
    "Returns resolved blockers with their resolution durations.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "category_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Filter by blocker category IDs",
            },
        },
        "required": ["space_id"],
    },
    _chart_block_resolution,
)


# ---------------------------------------------------------------------------
# 4. kaiten_chart_due_dates  (POST, sync)
# ---------------------------------------------------------------------------

async def _chart_due_dates(client, args: dict) -> Any:
    body: dict[str, Any] = {
        "space_id": args["space_id"],
        "card_date_from": args["card_date_from"],
        "card_date_to": args["card_date_to"],
        "checklist_item_date_from": args["checklist_item_date_from"],
        "checklist_item_date_to": args["checklist_item_date_to"],
    }
    for key in (
        "due_date", "responsible_id",
    ):
        if args.get(key) is not None:
            body[key] = args[key]
    if args.get("tz_offset") is not None:
        body["tz_offset"] = args["tz_offset"]
    for key in ("lane_ids", "column_ids", "card_type_ids", "tag_ids"):
        if args.get(key) is not None:
            body[key] = args[key]
    return await client.post("/charts/due-dates", json=body)


_tool(
    "kaiten_chart_due_dates",
    "Get due dates analysis for a space. "
    "Returns completed tasks summary with card and checklist item due date filtering.",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "card_date_from": {"type": "string", "description": "Card date range start (ISO 8601)"},
            "card_date_to": {"type": "string", "description": "Card date range end (ISO 8601)"},
            "checklist_item_date_from": {"type": "string", "description": "Checklist item date range start (ISO 8601)"},
            "checklist_item_date_to": {"type": "string", "description": "Checklist item date range end (ISO 8601)"},
            "due_date": {"type": "string", "description": "Due date filter (ISO 8601)"},
            "responsible_id": {"type": "string", "description": "Filter by responsible user ID"},
            "tz_offset": {"type": "integer", "description": "Timezone offset in minutes"},
            "lane_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Filter by lane IDs",
            },
            "column_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Filter by column IDs",
            },
            "card_type_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Filter by card type IDs",
            },
            "tag_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Filter by tag IDs",
            },
        },
        "required": ["space_id", "card_date_from", "card_date_to", "checklist_item_date_from", "checklist_item_date_to"],
    },
    _chart_due_dates,
)


# ---------------------------------------------------------------------------
# Helper: build body for async chart POST endpoints
# ---------------------------------------------------------------------------

def _build_async_chart_body(args: dict, extra_keys: tuple[str, ...] = ()) -> dict[str, Any]:
    """Collect common chart parameters from args into a request body."""
    body: dict[str, Any] = {"space_id": args["space_id"]}
    for key in ("date_from", "date_to"):
        if args.get(key) is not None:
            body[key] = args[key]
    if args.get("tags") is not None:
        body["tags"] = args["tags"]
    if args.get("only_asap_cards") is not None:
        body["only_asap_cards"] = args["only_asap_cards"]
    if args.get("card_types") is not None:
        body["card_types"] = args["card_types"]
    if args.get("cardTypes") is not None:
        body["cardTypes"] = args["cardTypes"]
    if args.get("group_by") is not None:
        body["group_by"] = args["group_by"]
    for key in extra_keys:
        if args.get(key) is not None:
            body[key] = args[key]
    return body


# ---------------------------------------------------------------------------
# Common schema fragments for async chart tools
# ---------------------------------------------------------------------------

_COMMON_CHART_PROPS = {
    "space_id": {"type": "integer", "description": "Space ID"},
    "date_from": {"type": "string", "description": "Start date (ISO 8601)"},
    "date_to": {"type": "string", "description": "End date (ISO 8601)"},
    "tags": {
        "type": "array",
        "items": {"type": "integer"},
        "description": "Filter by tag IDs",
    },
    "only_asap_cards": {"type": "boolean", "description": "Include only ASAP (expedite) cards"},
    "card_types": {
        "type": "array",
        "items": {"type": "integer"},
        "description": "Filter by card type IDs",
    },
    "group_by": {"type": "string", "description": "Grouping mode"},
}

_ASYNC_NOTE = (
    "This is an asynchronous operation that returns a compute_job_id. "
    "Use kaiten_get_compute_job to poll for results."
)


# ---------------------------------------------------------------------------
# 5. kaiten_chart_cfd  (POST, async)
# ---------------------------------------------------------------------------

async def _chart_cfd(client, args: dict) -> Any:
    body = _build_async_chart_body(
        args,
        extra_keys=("selectedLanes",),
    )
    return await client.post("/charts/cfd", json=body)


_tool(
    "kaiten_chart_cfd",
    f"Build a Cumulative Flow Diagram (CFD) for a space. {_ASYNC_NOTE}",
    {
        "type": "object",
        "properties": {
            **_COMMON_CHART_PROPS,
            "cardTypes": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Filter by card type IDs (alternative field name used by CFD)",
            },
            "selectedLanes": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Filter by lane IDs",
            },
        },
        "required": ["space_id", "date_from", "date_to"],
    },
    _chart_cfd,
)


# ---------------------------------------------------------------------------
# Helper for control/spectral/lead-time charts (shared params)
# ---------------------------------------------------------------------------

_CONTROL_EXTRA_PROPS = {
    "start_columns": {
        "type": "array",
        "items": {"type": "integer"},
        "description": "Start column IDs (required)",
    },
    "end_columns": {
        "type": "array",
        "items": {"type": "integer"},
        "description": "End column IDs (required)",
    },
    "start_column_lanes": {
        "type": "object",
        "description": "Mapping of start column ID to array of lane IDs, e.g. {\"10\": [1, 2]}",
    },
    "end_column_lanes": {
        "type": "object",
        "description": "Mapping of end column ID to array of lane IDs, e.g. {\"20\": [3, 4]}",
    },
}

_CONTROL_EXTRA_KEYS = (
    "start_columns", "end_columns",
    "start_column_lanes", "end_column_lanes",
)


# ---------------------------------------------------------------------------
# 6. kaiten_chart_control  (POST, async)
# ---------------------------------------------------------------------------

async def _chart_control(client, args: dict) -> Any:
    body = _build_async_chart_body(args, extra_keys=_CONTROL_EXTRA_KEYS)
    return await client.post("/charts/control-chart", json=body)


_tool(
    "kaiten_chart_control",
    f"Build a Control Chart for a space. Shows cycle time per card. {_ASYNC_NOTE}",
    {
        "type": "object",
        "properties": {
            **_COMMON_CHART_PROPS,
            **_CONTROL_EXTRA_PROPS,
        },
        "required": ["space_id", "date_from", "date_to", "start_columns", "end_columns",
                      "start_column_lanes", "end_column_lanes"],
    },
    _chart_control,
)


# ---------------------------------------------------------------------------
# 7. kaiten_chart_spectral  (POST, async)
# ---------------------------------------------------------------------------

async def _chart_spectral(client, args: dict) -> Any:
    body = _build_async_chart_body(args, extra_keys=_CONTROL_EXTRA_KEYS)
    return await client.post("/charts/spectral-chart", json=body)


_tool(
    "kaiten_chart_spectral",
    f"Build a Spectral Chart for a space. Shows cycle time distribution. {_ASYNC_NOTE}",
    {
        "type": "object",
        "properties": {
            **_COMMON_CHART_PROPS,
            **_CONTROL_EXTRA_PROPS,
        },
        "required": ["space_id", "date_from", "date_to", "start_columns", "end_columns",
                      "start_column_lanes", "end_column_lanes"],
    },
    _chart_spectral,
)


# ---------------------------------------------------------------------------
# 8. kaiten_chart_lead_time  (POST, async)
# ---------------------------------------------------------------------------

async def _chart_lead_time(client, args: dict) -> Any:
    body = _build_async_chart_body(args, extra_keys=_CONTROL_EXTRA_KEYS)
    return await client.post("/charts/lead-time", json=body)


_tool(
    "kaiten_chart_lead_time",
    f"Build a Lead Time Chart for a space. Uses the same engine as the Control Chart. {_ASYNC_NOTE}",
    {
        "type": "object",
        "properties": {
            **_COMMON_CHART_PROPS,
            **_CONTROL_EXTRA_PROPS,
        },
        "required": ["space_id", "date_from", "date_to", "start_columns", "end_columns",
                      "start_column_lanes", "end_column_lanes"],
    },
    _chart_lead_time,
)


# ---------------------------------------------------------------------------
# 9. kaiten_chart_throughput_capacity  (POST, async)
# ---------------------------------------------------------------------------

async def _chart_throughput_capacity(client, args: dict) -> Any:
    body = _build_async_chart_body(args, extra_keys=("end_column",))
    return await client.post("/charts/throughput-capacity-chart", json=body)


_tool(
    "kaiten_chart_throughput_capacity",
    f"Build a Throughput Capacity Chart for a space. Measures delivery throughput. {_ASYNC_NOTE}",
    {
        "type": "object",
        "properties": {
            **_COMMON_CHART_PROPS,
            "end_column": {"type": "integer", "description": "End (done) column ID (required)"},
        },
        "required": ["space_id", "date_from", "end_column"],
    },
    _chart_throughput_capacity,
)


# ---------------------------------------------------------------------------
# 10. kaiten_chart_throughput_demand  (POST, async)
# ---------------------------------------------------------------------------

async def _chart_throughput_demand(client, args: dict) -> Any:
    body = _build_async_chart_body(args, extra_keys=("start_column",))
    return await client.post("/charts/throughput-demand-chart", json=body)


_tool(
    "kaiten_chart_throughput_demand",
    f"Build a Throughput Demand Chart for a space. Measures incoming demand. {_ASYNC_NOTE}",
    {
        "type": "object",
        "properties": {
            **_COMMON_CHART_PROPS,
            "start_column": {"type": "integer", "description": "Start (input) column ID (required)"},
        },
        "required": ["space_id", "date_from", "start_column"],
    },
    _chart_throughput_demand,
)


# ---------------------------------------------------------------------------
# 11. kaiten_chart_task_distribution  (POST, async)
# ---------------------------------------------------------------------------

async def _chart_task_distribution(client, args: dict) -> Any:
    body: dict[str, Any] = {"space_id": args["space_id"]}
    for key in ("timezone",):
        if args.get(key) is not None:
            body[key] = args[key]
    for key in ("includeArchivedCards", "only_asap_cards"):
        if args.get(key) is not None:
            body[key] = args[key]
    if args.get("card_types") is not None:
        body["card_types"] = args["card_types"]
    if args.get("itemsFilter") is not None:
        body["itemsFilter"] = args["itemsFilter"]
    return await client.post("/charts/task-distribution-chart", json=body)


_tool(
    "kaiten_chart_task_distribution",
    f"Build a Task Distribution Chart for a space. Shows how tasks are distributed across the board. {_ASYNC_NOTE}",
    {
        "type": "object",
        "properties": {
            "space_id": {"type": "integer", "description": "Space ID"},
            "timezone": {"type": "string", "description": "Timezone name (e.g. 'Europe/Moscow')"},
            "includeArchivedCards": {"type": "boolean", "description": "Include archived cards"},
            "only_asap_cards": {"type": "boolean", "description": "Include only ASAP (expedite) cards"},
            "card_types": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Filter by card type IDs",
            },
            "itemsFilter": {
                "type": "object",
                "description": "Additional filter object for items",
            },
        },
        "required": ["space_id"],
    },
    _chart_task_distribution,
)


# ---------------------------------------------------------------------------
# 12. kaiten_chart_cycle_time  (POST, async)
# ---------------------------------------------------------------------------

async def _chart_cycle_time(client, args: dict) -> Any:
    body = _build_async_chart_body(
        args,
        extra_keys=("start_column", "end_column"),
    )
    return await client.post("/charts/cycle-time-chart", json=body)


_tool(
    "kaiten_chart_cycle_time",
    f"Build a Cycle Time Chart for a space. Measures time from start to end column. {_ASYNC_NOTE}",
    {
        "type": "object",
        "properties": {
            **_COMMON_CHART_PROPS,
            "start_column": {"type": "integer", "description": "Start column ID (required)"},
            "end_column": {"type": "integer", "description": "End column ID (required)"},
        },
        "required": ["space_id", "date_from", "date_to", "start_column", "end_column"],
    },
    _chart_cycle_time,
)


# ---------------------------------------------------------------------------
# 13. kaiten_chart_sales_funnel  (POST, async)
# ---------------------------------------------------------------------------

async def _chart_sales_funnel(client, args: dict) -> Any:
    body = _build_async_chart_body(
        args,
        extra_keys=("board_configs",),
    )
    return await client.post("/charts/sales-funnel", json=body)


_tool(
    "kaiten_chart_sales_funnel",
    f"Build a Sales Funnel Chart for a space. Requires board_configs with enabled boards "
    f"and columns marked as 'won' or 'lost'. Each enabled board must have a sum property "
    f"configured in its settings. {_ASYNC_NOTE}",
    {
        "type": "object",
        "properties": {
            **_COMMON_CHART_PROPS,
            "board_configs": {
                "type": "array",
                "items": {"type": "object"},
                "description": (
                    "Array of board configuration objects. Each object should have: "
                    "board_id (integer), enabled (boolean), columns (array of "
                    "{column_id, enabled, funnel_type} where funnel_type is 'won', 'lost', or 'stage')."
                ),
            },
        },
        "required": ["space_id", "date_from", "date_to", "board_configs"],
    },
    _chart_sales_funnel,
)


# ---------------------------------------------------------------------------
# 14. kaiten_get_compute_job  (GET)
# ---------------------------------------------------------------------------

async def _get_compute_job(client, args: dict) -> Any:
    job_id = args["job_id"]
    return await client.get(f"/users/current/compute-jobs/{job_id}")


_tool(
    "kaiten_get_compute_job",
    "Get the status and result of an asynchronous compute job. "
    "Use this to poll for results after requesting an async chart. "
    "The response contains a 'status' field ('queued', 'processing', 'done', 'failed') "
    "and a 'result' field with the chart data when status is 'done'.",
    {
        "type": "object",
        "properties": {
            "job_id": {"type": "integer", "description": "Compute job ID returned by an async chart tool"},
        },
        "required": ["job_id"],
    },
    _get_compute_job,
)


# ---------------------------------------------------------------------------
# 15. kaiten_cancel_compute_job  (DELETE)
# ---------------------------------------------------------------------------

async def _cancel_compute_job(client, args: dict) -> Any:
    job_id = args["job_id"]
    return await client.delete(f"/users/current/compute-jobs/{job_id}")


_tool(
    "kaiten_cancel_compute_job",
    "Cancel a running or queued compute job. "
    "Sets canceled_at timestamp on the job, preventing further processing.",
    {
        "type": "object",
        "properties": {
            "job_id": {"type": "integer", "description": "Compute job ID to cancel"},
        },
        "required": ["job_id"],
    },
    _cancel_compute_job,
)
