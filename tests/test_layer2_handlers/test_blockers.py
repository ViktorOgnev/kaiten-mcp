"""Layer 2 handler integration tests for tools/blockers.py."""
import json

import pytest
from httpx import Response

from kaiten_mcp.tools.blockers import TOOLS


class TestListCardBlockers:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/cards/1/blockers").mock(
            return_value=Response(200, json=[{"id": 3, "reason": "Waiting"}])
        )
        result = await TOOLS["kaiten_list_card_blockers"]["handler"](
            client, {"card_id": 1}
        )
        assert route.called
        assert result == [{"id": 3, "reason": "Waiting"}]


class TestCreateCardBlocker:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/cards/1/blockers").mock(
            return_value=Response(200, json={"id": 3})
        )
        result = await TOOLS["kaiten_create_card_blocker"]["handler"](
            client, {"card_id": 1}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}
        assert result == {"id": 3}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/cards/1/blockers").mock(
            return_value=Response(200, json={"id": 3, "reason": "Blocked by API"})
        )
        result = await TOOLS["kaiten_create_card_blocker"]["handler"](
            client, {"card_id": 1, "reason": "Blocked by API", "blocker_card_id": 99}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"reason": "Blocked by API", "blocker_card_id": 99}


class TestGetCardBlocker:
    async def test_required_only(self, client, mock_api):
        """Handler fetches list endpoint and filters by blocker_id client-side."""
        route = mock_api.get("/cards/1/blockers").mock(
            return_value=Response(200, json=[
                {"id": 2, "reason": "Other"},
                {"id": 3, "reason": "Waiting"},
            ])
        )
        result = await TOOLS["kaiten_get_card_blocker"]["handler"](
            client, {"card_id": 1, "blocker_id": 3}
        )
        assert route.called
        assert result == {"id": 3, "reason": "Waiting"}

    async def test_not_found_returns_none(self, client, mock_api):
        """Returns None when blocker_id is not in the list."""
        route = mock_api.get("/cards/1/blockers").mock(
            return_value=Response(200, json=[
                {"id": 2, "reason": "Other"},
            ])
        )
        result = await TOOLS["kaiten_get_card_blocker"]["handler"](
            client, {"card_id": 1, "blocker_id": 999}
        )
        assert route.called
        assert result is None


class TestUpdateCardBlocker:
    async def test_required_only(self, client, mock_api):
        route = mock_api.patch("/cards/1/blockers/3").mock(
            return_value=Response(200, json={"id": 3})
        )
        result = await TOOLS["kaiten_update_card_blocker"]["handler"](
            client, {"card_id": 1, "blocker_id": 3}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_all_args(self, client, mock_api):
        route = mock_api.patch("/cards/1/blockers/3").mock(
            return_value=Response(200, json={"id": 3, "reason": "New reason"})
        )
        result = await TOOLS["kaiten_update_card_blocker"]["handler"](
            client, {"card_id": 1, "blocker_id": 3, "reason": "New reason"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"reason": "New reason"}


class TestDeleteCardBlocker:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/cards/1/blockers/3").mock(
            return_value=Response(200, json={})
        )
        result = await TOOLS["kaiten_delete_card_blocker"]["handler"](
            client, {"card_id": 1, "blocker_id": 3}
        )
        assert route.called
        assert result == {}
