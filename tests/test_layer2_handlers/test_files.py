"""Layer 2 handler integration tests for files tools."""

import json

from httpx import Response

from kaiten_mcp.tools.files import TOOLS


class TestListCardFiles:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/cards/42/files").mock(
            return_value=Response(200, json=[{"id": 1, "name": "doc.pdf"}])
        )
        result = await TOOLS["kaiten_list_card_files"]["handler"](client, {"card_id": 42})
        assert route.called
        assert result == [{"id": 1, "name": "doc.pdf"}]


class TestCreateCardFile:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/cards/42/files").mock(
            return_value=Response(200, json={"id": 10, "name": "doc.pdf"})
        )
        result = await TOOLS["kaiten_create_card_file"]["handler"](
            client, {"card_id": 42, "url": "https://example.com/doc.pdf", "name": "doc.pdf"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"url": "https://example.com/doc.pdf", "name": "doc.pdf"}
        assert result == {"id": 10, "name": "doc.pdf"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/cards/42/files").mock(return_value=Response(200, json={"id": 10}))
        await TOOLS["kaiten_create_card_file"]["handler"](
            client,
            {
                "card_id": 42,
                "url": "https://example.com/doc.pdf",
                "name": "doc.pdf",
                "sort_order": 2.5,
                "type": 1,
                "size": 1024,
                "custom_property_id": 99,
                "card_cover": True,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "url": "https://example.com/doc.pdf",
            "name": "doc.pdf",
            "sort_order": 2.5,
            "type": 1,
            "size": 1024,
            "custom_property_id": 99,
            "card_cover": True,
        }


class TestUpdateCardFile:
    async def test_required_only(self, client, mock_api):
        route = mock_api.patch("/cards/42/files/10").mock(
            return_value=Response(200, json={"id": 10})
        )
        result = await TOOLS["kaiten_update_card_file"]["handler"](
            client, {"card_id": 42, "file_id": 10}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_all_args(self, client, mock_api):
        route = mock_api.patch("/cards/42/files/10").mock(
            return_value=Response(200, json={"id": 10})
        )
        await TOOLS["kaiten_update_card_file"]["handler"](
            client,
            {
                "card_id": 42,
                "file_id": 10,
                "url": "https://example.com/new.pdf",
                "name": "new.pdf",
                "sort_order": 3.0,
                "type": 2,
                "size": 2048,
                "custom_property_id": 50,
                "card_cover": False,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "url": "https://example.com/new.pdf",
            "name": "new.pdf",
            "sort_order": 3.0,
            "type": 2,
            "size": 2048,
            "custom_property_id": 50,
            "card_cover": False,
        }


class TestDeleteCardFile:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/cards/42/files/10").mock(return_value=Response(204))
        await TOOLS["kaiten_delete_card_file"]["handler"](client, {"card_id": 42, "file_id": 10})
        assert route.called
