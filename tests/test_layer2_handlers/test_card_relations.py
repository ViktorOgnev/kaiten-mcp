"""Layer 2 handler integration tests for tools/card_relations.py."""
import json

import pytest
from httpx import Response

from kaiten_mcp.tools.card_relations import TOOLS


# ---------------------------------------------------------------------------
# Children
# ---------------------------------------------------------------------------


class TestListCardChildren:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/cards/1/children").mock(
            return_value=Response(200, json=[{"id": 10}])
        )
        result = await TOOLS["kaiten_list_card_children"]["handler"](
            client, {"card_id": 1}
        )
        assert route.called
        assert result == [{"id": 10}]


class TestAddCardChild:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/cards/1/children").mock(
            return_value=Response(200, json={"id": 10})
        )
        result = await TOOLS["kaiten_add_card_child"]["handler"](
            client, {"card_id": 1, "child_card_id": 10}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"child_card_id": 10}
        assert result == {"id": 10}


class TestRemoveCardChild:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/cards/1/children/10").mock(
            return_value=Response(200, json={})
        )
        result = await TOOLS["kaiten_remove_card_child"]["handler"](
            client, {"card_id": 1, "child_id": 10}
        )
        assert route.called
        assert result == {}


# ---------------------------------------------------------------------------
# Parents
# ---------------------------------------------------------------------------


class TestListCardParents:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/cards/5/parents").mock(
            return_value=Response(200, json=[{"id": 2}])
        )
        result = await TOOLS["kaiten_list_card_parents"]["handler"](
            client, {"card_id": 5}
        )
        assert route.called
        assert result == [{"id": 2}]


class TestAddCardParent:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/cards/5/parents").mock(
            return_value=Response(200, json={"id": 2})
        )
        result = await TOOLS["kaiten_add_card_parent"]["handler"](
            client, {"card_id": 5, "parent_card_id": 2}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"parent_card_id": 2}
        assert result == {"id": 2}


class TestRemoveCardParent:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/cards/5/parents/2").mock(
            return_value=Response(200, json={})
        )
        result = await TOOLS["kaiten_remove_card_parent"]["handler"](
            client, {"card_id": 5, "parent_id": 2}
        )
        assert route.called
        assert result == {}
