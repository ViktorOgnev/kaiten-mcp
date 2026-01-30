"""Integration tests for audit_and_analytics handler layer."""
import json

import pytest
from httpx import Response

from kaiten_mcp.tools.audit_and_analytics import TOOLS


# ---------------------------------------------------------------------------
# Audit Logs
# ---------------------------------------------------------------------------


class TestListAuditLogs:
    async def test_list_audit_logs_required_only(self, client, mock_api):
        route = mock_api.get("/audit-logs").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_audit_logs"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_audit_logs_all_args(self, client, mock_api):
        route = mock_api.get("/audit-logs").mock(
            return_value=Response(200, json=[{"id": 1}])
        )
        await TOOLS["kaiten_list_audit_logs"]["handler"](
            client, {"query": "login", "limit": 50, "offset": 10}
        )
        url = str(route.calls[0].request.url)
        assert "query=login" in url
        assert "limit=50" in url
        assert "offset=10" in url


# ---------------------------------------------------------------------------
# Activity
# ---------------------------------------------------------------------------


class TestGetCardActivity:
    async def test_get_card_activity_required_only(self, client, mock_api):
        route = mock_api.get("/cards/42/activity").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_get_card_activity"]["handler"](
            client, {"card_id": 42}
        )
        assert route.called
        assert result == []

    async def test_get_card_activity_all_args(self, client, mock_api):
        route = mock_api.get("/cards/42/activity").mock(
            return_value=Response(200, json=[{"id": 1}])
        )
        await TOOLS["kaiten_get_card_activity"]["handler"](
            client, {"card_id": 42, "limit": 10, "offset": 5}
        )
        url = str(route.calls[0].request.url)
        assert "limit=10" in url
        assert "offset=5" in url


class TestGetSpaceActivity:
    async def test_get_space_activity_required_only(self, client, mock_api):
        route = mock_api.get("/spaces/1/activity").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_get_space_activity"]["handler"](
            client, {"space_id": 1}
        )
        assert route.called
        assert result == []

    async def test_get_space_activity_all_args(self, client, mock_api):
        route = mock_api.get("/spaces/1/activity").mock(
            return_value=Response(200, json=[{"id": 1}])
        )
        await TOOLS["kaiten_get_space_activity"]["handler"](
            client, {"space_id": 1, "limit": 20, "offset": 0}
        )
        url = str(route.calls[0].request.url)
        assert "limit=20" in url
        assert "offset=0" in url


class TestGetCompanyActivity:
    async def test_get_company_activity_required_only(self, client, mock_api):
        route = mock_api.get("/company/activity").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_get_company_activity"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_get_company_activity_all_args(self, client, mock_api):
        route = mock_api.get("/company/activity").mock(
            return_value=Response(200, json=[{"id": 1}])
        )
        await TOOLS["kaiten_get_company_activity"]["handler"](
            client, {"limit": 100, "offset": 50}
        )
        url = str(route.calls[0].request.url)
        assert "limit=100" in url
        assert "offset=50" in url


# ---------------------------------------------------------------------------
# Card History
# ---------------------------------------------------------------------------


class TestGetCardLocationHistory:
    async def test_get_card_location_history_required_only(self, client, mock_api):
        route = mock_api.get("/cards/42/location-history").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_get_card_location_history"]["handler"](
            client, {"card_id": 42}
        )
        assert route.called
        assert result == []


# ---------------------------------------------------------------------------
# Saved Filters
# ---------------------------------------------------------------------------


class TestListSavedFilters:
    async def test_list_saved_filters_required_only(self, client, mock_api):
        route = mock_api.get("/saved-filters").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_saved_filters"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_saved_filters_all_args(self, client, mock_api):
        route = mock_api.get("/saved-filters").mock(
            return_value=Response(200, json=[{"id": 1}])
        )
        await TOOLS["kaiten_list_saved_filters"]["handler"](
            client, {"limit": 10, "offset": 5}
        )
        url = str(route.calls[0].request.url)
        assert "limit=10" in url
        assert "offset=5" in url


class TestCreateSavedFilter:
    async def test_create_saved_filter_required_only(self, client, mock_api):
        route = mock_api.post("/saved-filters").mock(
            return_value=Response(200, json={"id": 1, "name": "My Filter"})
        )
        filter_obj = {"status": "open"}
        result = await TOOLS["kaiten_create_saved_filter"]["handler"](
            client, {"name": "My Filter", "filter": filter_obj}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "My Filter", "filter": {"status": "open"}}

    async def test_create_saved_filter_all_args(self, client, mock_api):
        route = mock_api.post("/saved-filters").mock(
            return_value=Response(200, json={"id": 1})
        )
        filter_obj = {"status": "open", "assignee": 42}
        await TOOLS["kaiten_create_saved_filter"]["handler"](
            client, {"name": "Shared Filter", "filter": filter_obj, "shared": True}
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "title": "Shared Filter",
            "filter": {"status": "open", "assignee": 42},
            "shared": True,
        }


class TestGetSavedFilter:
    async def test_get_saved_filter_required_only(self, client, mock_api):
        route = mock_api.get("/saved-filters/1").mock(
            return_value=Response(200, json={"id": 1})
        )
        result = await TOOLS["kaiten_get_saved_filter"]["handler"](
            client, {"filter_id": 1}
        )
        assert route.called
        assert result == {"id": 1}


class TestUpdateSavedFilter:
    async def test_update_saved_filter_required_only(self, client, mock_api):
        route = mock_api.patch("/saved-filters/1").mock(
            return_value=Response(200, json={"id": 1})
        )
        result = await TOOLS["kaiten_update_saved_filter"]["handler"](
            client, {"filter_id": 1}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_saved_filter_all_args(self, client, mock_api):
        route = mock_api.patch("/saved-filters/1").mock(
            return_value=Response(200, json={"id": 1})
        )
        filter_obj = {"priority": "high"}
        await TOOLS["kaiten_update_saved_filter"]["handler"](
            client,
            {
                "filter_id": 1,
                "name": "Renamed",
                "filter": filter_obj,
                "shared": False,
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "title": "Renamed",
            "filter": {"priority": "high"},
            "shared": False,
        }


class TestDeleteSavedFilter:
    async def test_delete_saved_filter_required_only(self, client, mock_api):
        route = mock_api.delete("/saved-filters/1").mock(
            return_value=Response(204)
        )
        await TOOLS["kaiten_delete_saved_filter"]["handler"](
            client, {"filter_id": 1}
        )
        assert route.called
