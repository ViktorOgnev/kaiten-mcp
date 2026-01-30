"""Layer 2 handler integration tests for tools/comments.py."""
import json

import pytest
from httpx import Response

from kaiten_mcp.tools.comments import TOOLS


class TestListComments:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/cards/1/comments").mock(
            return_value=Response(200, json=[{"id": 10, "text": "hi"}])
        )
        result = await TOOLS["kaiten_list_comments"]["handler"](client, {"card_id": 1})
        assert route.called
        assert result == [{"id": 10, "text": "hi"}]


class TestCreateComment:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/cards/1/comments").mock(
            return_value=Response(200, json={"id": 10, "text": "Hello"})
        )
        result = await TOOLS["kaiten_create_comment"]["handler"](
            client, {"card_id": 1, "text": "Hello"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"text": "Hello"}
        assert result == {"id": 10, "text": "Hello"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/cards/2/comments").mock(
            return_value=Response(200, json={"id": 11, "text": "Secret", "internal": True})
        )
        result = await TOOLS["kaiten_create_comment"]["handler"](
            client, {"card_id": 2, "text": "Secret", "internal": True}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"text": "Secret", "internal": True}
        assert result["internal"] is True


class TestUpdateComment:
    async def test_required_only(self, client, mock_api):
        route = mock_api.patch("/cards/1/comments/10").mock(
            return_value=Response(200, json={"id": 10, "text": "Updated"})
        )
        result = await TOOLS["kaiten_update_comment"]["handler"](
            client, {"card_id": 1, "comment_id": 10, "text": "Updated"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"text": "Updated"}
        assert result == {"id": 10, "text": "Updated"}


class TestDeleteComment:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/cards/1/comments/10").mock(
            return_value=Response(200, json={})
        )
        result = await TOOLS["kaiten_delete_comment"]["handler"](
            client, {"card_id": 1, "comment_id": 10}
        )
        assert route.called
        assert result == {}
