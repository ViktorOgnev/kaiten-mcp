"""Layer 2 handler integration tests for charts & compute-jobs tools."""

import json

from httpx import Response

from kaiten_mcp.tools.charts import TOOLS

# ---------------------------------------------------------------------------
# 1. kaiten_get_chart_boards  (GET /charts/:space_id/boards)
# ---------------------------------------------------------------------------


class TestGetChartBoards:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/charts/1/boards").mock(
            return_value=Response(200, json=[{"id": 10, "title": "Board A"}])
        )
        result = await TOOLS["kaiten_get_chart_boards"]["handler"](client, {"space_id": 1})
        assert route.called
        assert result == [{"id": 10, "title": "Board A"}]


# ---------------------------------------------------------------------------
# 2. kaiten_chart_summary  (POST /charts/summary, sync)
# ---------------------------------------------------------------------------


class TestChartSummary:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/charts/summary").mock(
            return_value=Response(200, json={"total": 5})
        )
        result = await TOOLS["kaiten_chart_summary"]["handler"](
            client,
            {
                "space_id": 1,
                "date_from": "2025-01-01",
                "date_to": "2025-01-31",
                "done_columns": [10, 20],
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "space_id": 1,
            "date_from": "2025-01-01",
            "date_to": "2025-01-31",
            "done_columns": [10, 20],
        }
        assert result == {"total": 5}


# ---------------------------------------------------------------------------
# 3. kaiten_chart_block_resolution  (POST /charts/block-resolution-time-chart, sync)
# ---------------------------------------------------------------------------


class TestChartBlockResolution:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/charts/block-resolution-time-chart").mock(
            return_value=Response(200, json=[{"blocker_id": 1, "hours": 8}])
        )
        result = await TOOLS["kaiten_chart_block_resolution"]["handler"](client, {"space_id": 1})
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"space_id": 1}
        assert result == [{"blocker_id": 1, "hours": 8}]

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/charts/block-resolution-time-chart").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_chart_block_resolution"]["handler"](
            client, {"space_id": 1, "category_ids": [3, 5]}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"space_id": 1, "category_ids": [3, 5]}
        assert result == []


# ---------------------------------------------------------------------------
# 4. kaiten_chart_due_dates  (POST /charts/due-dates, sync)
# ---------------------------------------------------------------------------


class TestChartDueDates:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/charts/due-dates").mock(
            return_value=Response(200, json={"cards": []})
        )
        result = await TOOLS["kaiten_chart_due_dates"]["handler"](
            client,
            {
                "space_id": 1,
                "card_date_from": "2025-01-01",
                "card_date_to": "2025-01-31",
                "checklist_item_date_from": "2025-01-01",
                "checklist_item_date_to": "2025-01-31",
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "space_id": 1,
            "card_date_from": "2025-01-01",
            "card_date_to": "2025-01-31",
            "checklist_item_date_from": "2025-01-01",
            "checklist_item_date_to": "2025-01-31",
        }
        assert result == {"cards": []}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/charts/due-dates").mock(
            return_value=Response(200, json={"cards": [{"id": 99}]})
        )
        result = await TOOLS["kaiten_chart_due_dates"]["handler"](
            client,
            {
                "space_id": 1,
                "card_date_from": "2025-01-01",
                "card_date_to": "2025-01-31",
                "checklist_item_date_from": "2025-01-01",
                "checklist_item_date_to": "2025-01-31",
                "tz_offset": 180,
                "due_date": "2025-01-15",
                "responsible_id": "user-42",
                "lane_ids": [1, 2],
                "column_ids": [10, 20],
                "card_type_ids": [3],
                "tag_ids": [7, 8],
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "space_id": 1,
            "card_date_from": "2025-01-01",
            "card_date_to": "2025-01-31",
            "checklist_item_date_from": "2025-01-01",
            "checklist_item_date_to": "2025-01-31",
            "tz_offset": 180,
            "due_date": "2025-01-15",
            "responsible_id": "user-42",
            "lane_ids": [1, 2],
            "column_ids": [10, 20],
            "card_type_ids": [3],
            "tag_ids": [7, 8],
        }
        assert result == {"cards": [{"id": 99}]}


# ---------------------------------------------------------------------------
# 5. kaiten_chart_cfd  (POST /charts/cfd, async)
# ---------------------------------------------------------------------------


class TestChartCfd:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/charts/cfd").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-cfd"})
        )
        result = await TOOLS["kaiten_chart_cfd"]["handler"](
            client,
            {
                "space_id": 1,
                "date_from": "2025-01-01",
                "date_to": "2025-01-31",
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "space_id": 1,
            "date_from": "2025-01-01",
            "date_to": "2025-01-31",
        }
        assert result == {"compute_job_id": "uuid-cfd"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/charts/cfd").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-cfd-2"})
        )
        result = await TOOLS["kaiten_chart_cfd"]["handler"](
            client,
            {
                "space_id": 1,
                "date_from": "2025-01-01",
                "date_to": "2025-01-31",
                "tags": [5, 6],
                "selectedLanes": [10, 20],
                "cardTypes": [1, 2],
                "only_asap_cards": True,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "space_id": 1,
            "date_from": "2025-01-01",
            "date_to": "2025-01-31",
            "tags": [5, 6],
            "selectedLanes": [10, 20],
            "cardTypes": [1, 2],
            "only_asap_cards": True,
        }
        assert result == {"compute_job_id": "uuid-cfd-2"}


# ---------------------------------------------------------------------------
# 6. kaiten_chart_control  (POST /charts/control-chart, async)
# ---------------------------------------------------------------------------

_CONTROL_REQUIRED = {
    "space_id": 1,
    "date_from": "2025-01-01",
    "date_to": "2025-01-31",
    "start_columns": [10],
    "end_columns": [20],
    "start_column_lanes": {"10": [1]},
    "end_column_lanes": {"20": [2]},
}


class TestChartControl:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/charts/control-chart").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-ctrl"})
        )
        result = await TOOLS["kaiten_chart_control"]["handler"](client, {**_CONTROL_REQUIRED})
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == _CONTROL_REQUIRED
        assert result == {"compute_job_id": "uuid-ctrl"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/charts/control-chart").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-ctrl-2"})
        )
        result = await TOOLS["kaiten_chart_control"]["handler"](
            client,
            {
                **_CONTROL_REQUIRED,
                "card_types": [3],
                "only_asap_cards": False,
                "tags": [7],
                "group_by": "card_type",
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            **_CONTROL_REQUIRED,
            "card_types": [3],
            "only_asap_cards": False,
            "tags": [7],
            "group_by": "card_type",
        }
        assert result == {"compute_job_id": "uuid-ctrl-2"}


# ---------------------------------------------------------------------------
# 7. kaiten_chart_spectral  (POST /charts/spectral-chart, async)
# ---------------------------------------------------------------------------


class TestChartSpectral:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/charts/spectral-chart").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-spec"})
        )
        result = await TOOLS["kaiten_chart_spectral"]["handler"](client, {**_CONTROL_REQUIRED})
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == _CONTROL_REQUIRED
        assert result == {"compute_job_id": "uuid-spec"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/charts/spectral-chart").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-spec-2"})
        )
        result = await TOOLS["kaiten_chart_spectral"]["handler"](
            client,
            {
                **_CONTROL_REQUIRED,
                "card_types": [2],
                "only_asap_cards": True,
                "tags": [9],
                "group_by": "tag",
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            **_CONTROL_REQUIRED,
            "card_types": [2],
            "only_asap_cards": True,
            "tags": [9],
            "group_by": "tag",
        }
        assert result == {"compute_job_id": "uuid-spec-2"}


# ---------------------------------------------------------------------------
# 8. kaiten_chart_lead_time  (POST /charts/lead-time, async)
# ---------------------------------------------------------------------------


class TestChartLeadTime:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/charts/lead-time").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-lt"})
        )
        result = await TOOLS["kaiten_chart_lead_time"]["handler"](client, {**_CONTROL_REQUIRED})
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == _CONTROL_REQUIRED
        assert result == {"compute_job_id": "uuid-lt"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/charts/lead-time").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-lt-2"})
        )
        result = await TOOLS["kaiten_chart_lead_time"]["handler"](
            client,
            {
                **_CONTROL_REQUIRED,
                "card_types": [1, 4],
                "only_asap_cards": False,
                "tags": [11],
                "group_by": "responsible",
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            **_CONTROL_REQUIRED,
            "card_types": [1, 4],
            "only_asap_cards": False,
            "tags": [11],
            "group_by": "responsible",
        }
        assert result == {"compute_job_id": "uuid-lt-2"}


# ---------------------------------------------------------------------------
# 9. kaiten_chart_throughput_capacity  (POST /charts/throughput-capacity-chart, async)
# ---------------------------------------------------------------------------


class TestChartThroughputCapacity:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/charts/throughput-capacity-chart").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-tc"})
        )
        result = await TOOLS["kaiten_chart_throughput_capacity"]["handler"](
            client,
            {"space_id": 1, "date_from": "2025-01-01", "end_column": 30},
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "space_id": 1,
            "date_from": "2025-01-01",
            "end_column": 30,
        }
        assert result == {"compute_job_id": "uuid-tc"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/charts/throughput-capacity-chart").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-tc-2"})
        )
        result = await TOOLS["kaiten_chart_throughput_capacity"]["handler"](
            client,
            {
                "space_id": 1,
                "date_from": "2025-01-01",
                "date_to": "2025-03-31",
                "end_column": 30,
                "tags": [4],
                "only_asap_cards": False,
                "group_by": "week",
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "space_id": 1,
            "date_from": "2025-01-01",
            "date_to": "2025-03-31",
            "end_column": 30,
            "tags": [4],
            "only_asap_cards": False,
            "group_by": "week",
        }
        assert result == {"compute_job_id": "uuid-tc-2"}


# ---------------------------------------------------------------------------
# 10. kaiten_chart_throughput_demand  (POST /charts/throughput-demand-chart, async)
# ---------------------------------------------------------------------------


class TestChartThroughputDemand:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/charts/throughput-demand-chart").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-td"})
        )
        result = await TOOLS["kaiten_chart_throughput_demand"]["handler"](
            client,
            {"space_id": 1, "date_from": "2025-01-01", "start_column": 10},
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "space_id": 1,
            "date_from": "2025-01-01",
            "start_column": 10,
        }
        assert result == {"compute_job_id": "uuid-td"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/charts/throughput-demand-chart").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-td-2"})
        )
        result = await TOOLS["kaiten_chart_throughput_demand"]["handler"](
            client,
            {
                "space_id": 1,
                "date_from": "2025-01-01",
                "date_to": "2025-03-31",
                "start_column": 10,
                "tags": [2, 3],
                "only_asap_cards": True,
                "group_by": "month",
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "space_id": 1,
            "date_from": "2025-01-01",
            "date_to": "2025-03-31",
            "start_column": 10,
            "tags": [2, 3],
            "only_asap_cards": True,
            "group_by": "month",
        }
        assert result == {"compute_job_id": "uuid-td-2"}


# ---------------------------------------------------------------------------
# 11. kaiten_chart_task_distribution  (POST /charts/task-distribution-chart, async)
# ---------------------------------------------------------------------------


class TestChartTaskDistribution:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/charts/task-distribution-chart").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-dist"})
        )
        result = await TOOLS["kaiten_chart_task_distribution"]["handler"](client, {"space_id": 1})
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"space_id": 1}
        assert result == {"compute_job_id": "uuid-dist"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/charts/task-distribution-chart").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-dist-2"})
        )
        result = await TOOLS["kaiten_chart_task_distribution"]["handler"](
            client,
            {
                "space_id": 1,
                "timezone": "Europe/Moscow",
                "includeArchivedCards": True,
                "only_asap_cards": False,
                "card_types": [1, 2],
                "itemsFilter": {"status": "active"},
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "space_id": 1,
            "timezone": "Europe/Moscow",
            "includeArchivedCards": True,
            "only_asap_cards": False,
            "card_types": [1, 2],
            "itemsFilter": {"status": "active"},
        }
        assert result == {"compute_job_id": "uuid-dist-2"}


# ---------------------------------------------------------------------------
# 12. kaiten_chart_cycle_time  (POST /charts/cycle-time-chart, async)
# ---------------------------------------------------------------------------


class TestChartCycleTime:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/charts/cycle-time-chart").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-ct"})
        )
        result = await TOOLS["kaiten_chart_cycle_time"]["handler"](
            client,
            {
                "space_id": 1,
                "date_from": "2025-01-01",
                "date_to": "2025-01-31",
                "start_column": 10,
                "end_column": 20,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "space_id": 1,
            "date_from": "2025-01-01",
            "date_to": "2025-01-31",
            "start_column": 10,
            "end_column": 20,
        }
        assert result == {"compute_job_id": "uuid-ct"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/charts/cycle-time-chart").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-ct-2"})
        )
        result = await TOOLS["kaiten_chart_cycle_time"]["handler"](
            client,
            {
                "space_id": 1,
                "date_from": "2025-01-01",
                "date_to": "2025-01-31",
                "start_column": 10,
                "end_column": 20,
                "tags": [5],
                "only_asap_cards": True,
                "card_types": [3, 4],
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "space_id": 1,
            "date_from": "2025-01-01",
            "date_to": "2025-01-31",
            "start_column": 10,
            "end_column": 20,
            "tags": [5],
            "only_asap_cards": True,
            "card_types": [3, 4],
        }
        assert result == {"compute_job_id": "uuid-ct-2"}


# ---------------------------------------------------------------------------
# 13. kaiten_chart_sales_funnel  (POST /charts/sales-funnel, async)
# ---------------------------------------------------------------------------

_BOARD_CONFIGS = [
    {
        "board_id": 10,
        "enabled": True,
        "columns": [
            {"column_id": 100, "enabled": True, "funnel_type": "won"},
            {"column_id": 101, "enabled": True, "funnel_type": "lost"},
        ],
    }
]


class TestChartSalesFunnel:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/charts/sales-funnel").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-sf"})
        )
        result = await TOOLS["kaiten_chart_sales_funnel"]["handler"](
            client,
            {
                "space_id": 1,
                "date_from": "2025-01-01",
                "date_to": "2025-01-31",
                "board_configs": _BOARD_CONFIGS,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "space_id": 1,
            "date_from": "2025-01-01",
            "date_to": "2025-01-31",
            "board_configs": _BOARD_CONFIGS,
        }
        assert result == {"compute_job_id": "uuid-sf"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/charts/sales-funnel").mock(
            return_value=Response(200, json={"compute_job_id": "uuid-sf-2"})
        )
        result = await TOOLS["kaiten_chart_sales_funnel"]["handler"](
            client,
            {
                "space_id": 1,
                "date_from": "2025-01-01",
                "date_to": "2025-01-31",
                "board_configs": _BOARD_CONFIGS,
                "tags": [1, 2],
                "only_asap_cards": False,
                "card_types": [5],
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "space_id": 1,
            "date_from": "2025-01-01",
            "date_to": "2025-01-31",
            "board_configs": _BOARD_CONFIGS,
            "tags": [1, 2],
            "only_asap_cards": False,
            "card_types": [5],
        }
        assert result == {"compute_job_id": "uuid-sf-2"}


# ---------------------------------------------------------------------------
# 14. kaiten_get_compute_job  (GET /users/current/compute-jobs/:id)
# ---------------------------------------------------------------------------


class TestGetComputeJob:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/users/current/compute-jobs/42").mock(
            return_value=Response(
                200,
                json={
                    "id": 42,
                    "status": "done",
                    "result": {"data": [1, 2, 3]},
                },
            )
        )
        result = await TOOLS["kaiten_get_compute_job"]["handler"](client, {"job_id": 42})
        assert route.called
        assert result["id"] == 42
        assert result["status"] == "done"


# ---------------------------------------------------------------------------
# 15. kaiten_cancel_compute_job  (DELETE /users/current/compute-jobs/:id)
# ---------------------------------------------------------------------------


class TestCancelComputeJob:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/users/current/compute-jobs/42").mock(
            return_value=Response(200, json={"id": "42"})
        )
        result = await TOOLS["kaiten_cancel_compute_job"]["handler"](client, {"job_id": 42})
        assert route.called
        assert result == {"id": "42"}
