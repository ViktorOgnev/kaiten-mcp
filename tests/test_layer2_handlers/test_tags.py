"""Layer 2 handler integration tests for tools/tags.py."""
import json

import pytest
from httpx import Response

from kaiten_mcp.tools.tags import TOOLS


# ---------------------------------------------------------------------------
# Company-level tags
# ---------------------------------------------------------------------------


class TestListTags:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/tags").mock(
            return_value=Response(200, json=[{"id": 1, "name": "bug"}])
        )
        result = await TOOLS["kaiten_list_tags"]["handler"](client, {})
        assert route.called
        assert result == [{"id": 1, "name": "bug"}]

    async def test_all_args(self, client, mock_api):
        route = mock_api.get("/tags").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_tags"]["handler"](
            client, {"query": "feat", "limit": 5, "offset": 10, "space_id": 1, "ids": "1,2"}
        )
        assert route.called
        req = route.calls[0].request
        assert "query=feat" in str(req.url)
        assert "limit=5" in str(req.url)
        assert "offset=10" in str(req.url)


class TestCreateTag:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/tags").mock(
            return_value=Response(200, json={"id": 1, "name": "bug"})
        )
        result = await TOOLS["kaiten_create_tag"]["handler"](
            client, {"name": "bug"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "bug"}
        assert result == {"id": 1, "name": "bug"}


class TestUpdateTag:
    async def test_required_only(self, client, mock_api):
        route = mock_api.patch("/company/tags/1").mock(
            return_value=Response(200, json={"id": 1, "name": "bug"})
        )
        result = await TOOLS["kaiten_update_tag"]["handler"](
            client, {"tag_id": 1}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_all_args(self, client, mock_api):
        route = mock_api.patch("/company/tags/1").mock(
            return_value=Response(200, json={"id": 1, "name": "urgent", "color": 5})
        )
        result = await TOOLS["kaiten_update_tag"]["handler"](
            client, {"tag_id": 1, "name": "urgent", "color": 5}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "urgent", "color": 5}


class TestDeleteTag:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/company/tags/1").mock(
            return_value=Response(200, json={})
        )
        result = await TOOLS["kaiten_delete_tag"]["handler"](
            client, {"tag_id": 1}
        )
        assert route.called
        assert result == {}


# ---------------------------------------------------------------------------
# Card-level tags
# ---------------------------------------------------------------------------


class TestAddCardTag:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/cards/1/tags").mock(
            return_value=Response(200, json={"id": 5, "name": "feature"})
        )
        result = await TOOLS["kaiten_add_card_tag"]["handler"](
            client, {"card_id": 1, "name": "feature"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "feature"}
        assert result == {"id": 5, "name": "feature"}


class TestRemoveCardTag:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/cards/1/tags/5").mock(
            return_value=Response(200, json={})
        )
        result = await TOOLS["kaiten_remove_card_tag"]["handler"](
            client, {"card_id": 1, "tag_id": 5}
        )
        assert route.called
        assert result == {}
