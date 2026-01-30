"""Layer 2 handler integration tests for tools/members.py."""
import json

import pytest
from httpx import Response

from kaiten_mcp.tools.members import TOOLS


class TestListCardMembers:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/cards/1/members").mock(
            return_value=Response(200, json=[{"id": 42, "username": "alice"}])
        )
        result = await TOOLS["kaiten_list_card_members"]["handler"](
            client, {"card_id": 1}
        )
        assert route.called
        assert result == [{"id": 42, "username": "alice"}]


class TestAddCardMember:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/cards/1/members").mock(
            return_value=Response(200, json={"id": 42})
        )
        result = await TOOLS["kaiten_add_card_member"]["handler"](
            client, {"card_id": 1, "user_id": 42}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"user_id": 42}
        assert result == {"id": 42}


class TestRemoveCardMember:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/cards/1/members/42").mock(
            return_value=Response(200, json={})
        )
        result = await TOOLS["kaiten_remove_card_member"]["handler"](
            client, {"card_id": 1, "user_id": 42}
        )
        assert route.called
        assert result == {}


class TestListUsers:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/users").mock(
            return_value=Response(200, json=[{"id": 1, "username": "admin"}])
        )
        result = await TOOLS["kaiten_list_users"]["handler"](client, {})
        assert route.called
        assert result == [{"id": 1, "username": "admin"}]

    async def test_all_args(self, client, mock_api):
        route = mock_api.get("/users").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_users"]["handler"](
            client,
            {"query": "alice", "limit": 10, "offset": 5, "include_inactive": True},
        )
        assert route.called
        req = route.calls[0].request
        assert "query=alice" in str(req.url)
        assert "limit=10" in str(req.url)
        assert "offset=5" in str(req.url)
        assert "include_inactive" in str(req.url)


class TestGetCurrentUser:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/users/current").mock(
            return_value=Response(200, json={"id": 1, "username": "me"})
        )
        result = await TOOLS["kaiten_get_current_user"]["handler"](client, {})
        assert route.called
        assert result == {"id": 1, "username": "me"}
