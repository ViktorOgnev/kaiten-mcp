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

    async def test_format_html(self, client, mock_api):
        route = mock_api.post("/cards/3/comments").mock(
            return_value=Response(200, json={"id": 12, "text": "<h2>Title</h2>", "type": 2})
        )
        result = await TOOLS["kaiten_create_comment"]["handler"](
            client, {"card_id": 3, "text": "<h2>Title</h2>", "format": "html"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"text": "<h2>Title</h2>", "type": 2}

    async def test_format_markdown_no_type(self, client, mock_api):
        route = mock_api.post("/cards/4/comments").mock(
            return_value=Response(200, json={"id": 13, "text": "## Title"})
        )
        await TOOLS["kaiten_create_comment"]["handler"](
            client, {"card_id": 4, "text": "## Title", "format": "markdown"}
        )
        body = json.loads(route.calls[0].request.content)
        assert "type" not in body


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


    async def test_format_html(self, client, mock_api):
        route = mock_api.patch("/cards/1/comments/10").mock(
            return_value=Response(200, json={"id": 10, "text": "<p>Updated</p>", "type": 2})
        )
        await TOOLS["kaiten_update_comment"]["handler"](
            client, {"card_id": 1, "comment_id": 10, "text": "<p>Updated</p>", "format": "html"}
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"text": "<p>Updated</p>", "type": 2}

    async def test_format_markdown(self, client, mock_api):
        route = mock_api.patch("/cards/1/comments/10").mock(
            return_value=Response(200, json={"id": 10, "text": "## Title", "type": 1})
        )
        await TOOLS["kaiten_update_comment"]["handler"](
            client, {"card_id": 1, "comment_id": 10, "text": "## Title", "format": "markdown"}
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"text": "## Title", "type": 1}


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
