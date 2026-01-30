"""Integration tests for webhooks handler layer."""
import json

import pytest
from httpx import Response

from kaiten_mcp.tools.webhooks import TOOLS


class TestListWebhooks:
    async def test_list_webhooks_required_only(self, client, mock_api):
        route = mock_api.get("/spaces/1/external-webhooks").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_webhooks"]["handler"](
            client, {"space_id": 1}
        )
        assert route.called
        assert result == []


class TestCreateWebhook:
    async def test_create_webhook_required_only(self, client, mock_api):
        route = mock_api.post("/spaces/1/external-webhooks").mock(
            return_value=Response(200, json={"id": 10, "url": "https://example.com/hook"})
        )
        result = await TOOLS["kaiten_create_webhook"]["handler"](
            client, {"space_id": 1, "url": "https://example.com/hook"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"url": "https://example.com/hook"}
        assert result["id"] == 10

    async def test_create_webhook_all_args(self, client, mock_api):
        """Create webhook only sends 'url' — 'enabled' is not accepted on create."""
        route = mock_api.post("/spaces/1/external-webhooks").mock(
            return_value=Response(200, json={"id": 10})
        )
        await TOOLS["kaiten_create_webhook"]["handler"](
            client,
            {
                "space_id": 1,
                "url": "https://example.com/hook",
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "url": "https://example.com/hook",
        }


class TestGetWebhook:
    async def test_get_webhook_required_only(self, client, mock_api):
        route = mock_api.get("/spaces/1/external-webhooks/10").mock(
            return_value=Response(200, json={"id": 10})
        )
        result = await TOOLS["kaiten_get_webhook"]["handler"](
            client, {"space_id": 1, "webhook_id": 10}
        )
        assert route.called
        assert result == {"id": 10}


class TestUpdateWebhook:
    async def test_update_webhook_required_only(self, client, mock_api):
        route = mock_api.patch("/spaces/1/external-webhooks/10").mock(
            return_value=Response(200, json={"id": 10})
        )
        result = await TOOLS["kaiten_update_webhook"]["handler"](
            client, {"space_id": 1, "webhook_id": 10}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_webhook_all_args(self, client, mock_api):
        route = mock_api.patch("/spaces/1/external-webhooks/10").mock(
            return_value=Response(200, json={"id": 10})
        )
        await TOOLS["kaiten_update_webhook"]["handler"](
            client,
            {
                "space_id": 1,
                "webhook_id": 10,
                "url": "https://new.example.com/hook",
                "enabled": True,
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "url": "https://new.example.com/hook",
            "enabled": True,
        }


class TestDeleteWebhook:
    async def test_delete_webhook_required_only(self, client, mock_api):
        route = mock_api.delete("/spaces/1/external-webhooks/10").mock(
            return_value=Response(204)
        )
        await TOOLS["kaiten_delete_webhook"]["handler"](
            client, {"space_id": 1, "webhook_id": 10}
        )
        assert route.called
