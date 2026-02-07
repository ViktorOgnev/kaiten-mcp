"""Layer 2 handler integration tests for tools/members.py."""
import json

import pytest
from httpx import Response

from kaiten_mcp.tools.members import TOOLS
from kaiten_mcp.tools.compact import DEFAULT_LIMIT


# ---------------------------------------------------------------------------
# Default Limit Tests
# ---------------------------------------------------------------------------


class TestListUsersDefaultLimit:
    """Tests for default limit behavior in list_users."""

    async def test_default_limit_50_when_not_specified(self, client, mock_api):
        """Without explicit limit, should use DEFAULT_LIMIT (50)."""
        route = mock_api.get("/users").mock(
            return_value=Response(200, json=[])
        )
        await TOOLS["kaiten_list_users"]["handler"](client, {})
        assert route.called
        url = str(route.calls[0].request.url)
        assert "limit=50" in url

    async def test_explicit_limit_overrides_default(self, client, mock_api):
        """Explicit limit should override the default."""
        route = mock_api.get("/users").mock(
            return_value=Response(200, json=[])
        )
        await TOOLS["kaiten_list_users"]["handler"](client, {"limit": 25})
        url = str(route.calls[0].request.url)
        assert "limit=25" in url
        assert "limit=50" not in url


# ---------------------------------------------------------------------------
# Compact Mode Tests
# ---------------------------------------------------------------------------


class TestListUsersCompact:
    """Tests for compact mode in list_users."""

    async def test_compact_false_returns_full_response(self, client, mock_api):
        """compact=False (default) should return full response."""
        full_response = [
            {
                "id": 1,
                "full_name": "John Doe",
                "email": "john@example.com",
                "avatar_url": "data:image/png;base64,iVBORw0KGgo=",
            }
        ]
        route = mock_api.get("/users").mock(
            return_value=Response(200, json=full_response)
        )
        result = await TOOLS["kaiten_list_users"]["handler"](client, {"compact": False})
        assert route.called
        assert result == full_response

    async def test_compact_strips_base64_avatar(self, client, mock_api):
        """compact=True should strip base64 avatar_url."""
        full_response = [
            {
                "id": 1,
                "full_name": "John Doe",
                "avatar_url": "data:image/png;base64,iVBORw0KGgo=",
            }
        ]
        route = mock_api.get("/users").mock(
            return_value=Response(200, json=full_response)
        )
        result = await TOOLS["kaiten_list_users"]["handler"](client, {"compact": True})
        assert route.called
        assert "avatar_url" not in result[0]
        assert result[0]["id"] == 1
        assert result[0]["full_name"] == "John Doe"

    async def test_compact_keeps_http_avatar(self, client, mock_api):
        """compact=True should keep HTTP avatar URLs."""
        full_response = [
            {
                "id": 1,
                "avatar_url": "https://example.com/avatar.png",
            }
        ]
        route = mock_api.get("/users").mock(
            return_value=Response(200, json=full_response)
        )
        result = await TOOLS["kaiten_list_users"]["handler"](client, {"compact": True})
        assert result[0]["avatar_url"] == "https://example.com/avatar.png"

    async def test_compact_default_is_false(self, client, mock_api):
        """Without compact param, should behave as compact=False."""
        full_response = [
            {
                "id": 1,
                "avatar_url": "data:image/png;base64,xxx",
            }
        ]
        route = mock_api.get("/users").mock(
            return_value=Response(200, json=full_response)
        )
        result = await TOOLS["kaiten_list_users"]["handler"](client, {})
        assert route.called
        # Should keep the avatar since compact defaults to False
        assert result[0]["avatar_url"] == "data:image/png;base64,xxx"


# ---------------------------------------------------------------------------
# Card Members Tests
# ---------------------------------------------------------------------------


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
