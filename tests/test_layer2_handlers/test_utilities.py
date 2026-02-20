"""Integration tests for utilities handler layer."""

import json

from httpx import Response

from kaiten_mcp.tools.utilities import TOOLS

# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------


class TestListApiKeys:
    async def test_list_api_keys_required_only(self, client, mock_api):
        route = mock_api.get("/api-keys").mock(return_value=Response(200, json=[]))
        result = await TOOLS["kaiten_list_api_keys"]["handler"](client, {})
        assert route.called
        assert result == []


class TestCreateApiKey:
    async def test_create_api_key_required_only(self, client, mock_api):
        route = mock_api.post("/api-keys").mock(
            return_value=Response(200, json={"id": 1, "name": "ci-key"})
        )
        result = await TOOLS["kaiten_create_api_key"]["handler"](client, {"name": "ci-key"})
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "ci-key"}
        assert result["name"] == "ci-key"


class TestDeleteApiKey:
    async def test_delete_api_key_required_only(self, client, mock_api):
        route = mock_api.delete("/api-keys/1").mock(return_value=Response(204))
        await TOOLS["kaiten_delete_api_key"]["handler"](client, {"key_id": 1})
        assert route.called


# ---------------------------------------------------------------------------
# User Timers
# ---------------------------------------------------------------------------


class TestListUserTimers:
    async def test_list_user_timers_required_only(self, client, mock_api):
        route = mock_api.get("/user-timers").mock(return_value=Response(200, json=[]))
        result = await TOOLS["kaiten_list_user_timers"]["handler"](client, {})
        assert route.called
        assert result == []


class TestCreateUserTimer:
    async def test_create_user_timer_required_only(self, client, mock_api):
        route = mock_api.post("/user-timers").mock(
            return_value=Response(200, json={"id": 1, "card_id": 42})
        )
        result = await TOOLS["kaiten_create_user_timer"]["handler"](client, {"card_id": 42})
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"card_id": 42}
        assert result["card_id"] == 42


class TestGetUserTimer:
    async def test_get_user_timer_required_only(self, client, mock_api):
        route = mock_api.get("/user-timers/1").mock(return_value=Response(200, json={"id": 1}))
        result = await TOOLS["kaiten_get_user_timer"]["handler"](client, {"timer_id": 1})
        assert route.called
        assert result == {"id": 1}


class TestUpdateUserTimer:
    async def test_update_user_timer_required_only(self, client, mock_api):
        route = mock_api.patch("/user-timers/1").mock(return_value=Response(200, json={"id": 1}))
        result = await TOOLS["kaiten_update_user_timer"]["handler"](client, {"timer_id": 1})
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_user_timer_all_args(self, client, mock_api):
        route = mock_api.patch("/user-timers/1").mock(return_value=Response(200, json={"id": 1}))
        await TOOLS["kaiten_update_user_timer"]["handler"](client, {"timer_id": 1, "paused": True})
        body = json.loads(route.calls[0].request.content)
        assert body == {"paused": True}


class TestDeleteUserTimer:
    async def test_delete_user_timer_required_only(self, client, mock_api):
        route = mock_api.delete("/user-timers/1").mock(return_value=Response(204))
        await TOOLS["kaiten_delete_user_timer"]["handler"](client, {"timer_id": 1})
        assert route.called


# ---------------------------------------------------------------------------
# Removed Items (Recycle Bin)
# ---------------------------------------------------------------------------


class TestListRemovedCards:
    async def test_list_removed_cards_required_only(self, client, mock_api):
        route = mock_api.get("/removed/cards").mock(return_value=Response(200, json=[]))
        result = await TOOLS["kaiten_list_removed_cards"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_removed_cards_all_args(self, client, mock_api):
        route = mock_api.get("/removed/cards").mock(return_value=Response(200, json=[{"id": 1}]))
        await TOOLS["kaiten_list_removed_cards"]["handler"](client, {"limit": 10, "offset": 5})
        url = str(route.calls[0].request.url)
        assert "limit=10" in url
        assert "offset=5" in url


class TestListRemovedBoards:
    async def test_list_removed_boards_required_only(self, client, mock_api):
        route = mock_api.get("/removed/boards").mock(return_value=Response(200, json=[]))
        result = await TOOLS["kaiten_list_removed_boards"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_removed_boards_all_args(self, client, mock_api):
        route = mock_api.get("/removed/boards").mock(return_value=Response(200, json=[{"id": 1}]))
        await TOOLS["kaiten_list_removed_boards"]["handler"](client, {"limit": 10, "offset": 5})
        url = str(route.calls[0].request.url)
        assert "limit=10" in url
        assert "offset=5" in url


# ---------------------------------------------------------------------------
# Calendars
# ---------------------------------------------------------------------------


class TestListCalendars:
    async def test_list_calendars_required_only(self, client, mock_api):
        route = mock_api.get("/calendars").mock(return_value=Response(200, json=[]))
        result = await TOOLS["kaiten_list_calendars"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_calendars_all_args(self, client, mock_api):
        route = mock_api.get("/calendars").mock(return_value=Response(200, json=[{"id": 1}]))
        await TOOLS["kaiten_list_calendars"]["handler"](client, {"limit": 10, "offset": 0})
        url = str(route.calls[0].request.url)
        assert "limit=10" in url
        assert "offset=0" in url


class TestGetCalendar:
    async def test_get_calendar_required_only(self, client, mock_api):
        route = mock_api.get("/calendars/1").mock(return_value=Response(200, json={"id": 1}))
        result = await TOOLS["kaiten_get_calendar"]["handler"](client, {"calendar_id": 1})
        assert route.called
        assert result == {"id": 1}


# ---------------------------------------------------------------------------
# Company Info
# ---------------------------------------------------------------------------


class TestGetCompany:
    async def test_get_company_required_only(self, client, mock_api):
        route = mock_api.get("/companies/current").mock(
            return_value=Response(200, json={"id": 1, "name": "Acme"})
        )
        result = await TOOLS["kaiten_get_company"]["handler"](client, {})
        assert route.called
        assert result["name"] == "Acme"


class TestUpdateCompany:
    async def test_update_company_required_only(self, client, mock_api):
        route = mock_api.patch("/companies/current").mock(
            return_value=Response(200, json={"id": 1})
        )
        result = await TOOLS["kaiten_update_company"]["handler"](client, {})
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_company_all_args(self, client, mock_api):
        route = mock_api.patch("/companies/current").mock(
            return_value=Response(200, json={"id": 1, "name": "NewCo"})
        )
        result = await TOOLS["kaiten_update_company"]["handler"](client, {"name": "NewCo"})
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "NewCo"}
        assert result["name"] == "NewCo"
