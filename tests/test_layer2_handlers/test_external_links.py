"""Layer 2 handler integration tests for tools/external_links.py."""

import json

from httpx import Response

from kaiten_mcp.tools.external_links import TOOLS


class TestListExternalLinks:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/cards/1/external-links").mock(
            return_value=Response(200, json=[{"id": 7, "url": "https://example.com"}])
        )
        result = await TOOLS["kaiten_list_external_links"]["handler"](client, {"card_id": 1})
        assert route.called
        assert result == [{"id": 7, "url": "https://example.com"}]


class TestCreateExternalLink:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/cards/1/external-links").mock(
            return_value=Response(200, json={"id": 7, "url": "https://example.com"})
        )
        result = await TOOLS["kaiten_create_external_link"]["handler"](
            client, {"card_id": 1, "url": "https://example.com"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"url": "https://example.com"}
        assert result == {"id": 7, "url": "https://example.com"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/cards/1/external-links").mock(
            return_value=Response(200, json={"id": 7})
        )
        result = await TOOLS["kaiten_create_external_link"]["handler"](
            client,
            {"card_id": 1, "url": "https://example.com", "description": "Docs link"},
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"url": "https://example.com", "description": "Docs link"}


class TestUpdateExternalLink:
    async def test_required_only(self, client, mock_api):
        route = mock_api.patch("/cards/1/external-links/7").mock(
            return_value=Response(200, json={"id": 7})
        )
        result = await TOOLS["kaiten_update_external_link"]["handler"](
            client, {"card_id": 1, "link_id": 7}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_all_args(self, client, mock_api):
        route = mock_api.patch("/cards/1/external-links/7").mock(
            return_value=Response(200, json={"id": 7})
        )
        result = await TOOLS["kaiten_update_external_link"]["handler"](
            client,
            {
                "card_id": 1,
                "link_id": 7,
                "url": "https://new.example.com",
                "description": "Updated desc",
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"url": "https://new.example.com", "description": "Updated desc"}


class TestDeleteExternalLink:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/cards/1/external-links/7").mock(
            return_value=Response(200, json={})
        )
        result = await TOOLS["kaiten_delete_external_link"]["handler"](
            client, {"card_id": 1, "link_id": 7}
        )
        assert route.called
        assert result == {}
