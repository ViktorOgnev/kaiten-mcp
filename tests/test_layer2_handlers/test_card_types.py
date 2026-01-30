"""Integration tests for card_types handler layer."""
import json

import pytest
from httpx import Response

from kaiten_mcp.tools.card_types import TOOLS


class TestListCardTypes:
    async def test_list_card_types_required_only(self, client, mock_api):
        route = mock_api.get("/card-types").mock(return_value=Response(200, json=[]))
        result = await TOOLS["kaiten_list_card_types"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_card_types_all_args(self, client, mock_api):
        route = mock_api.get("/card-types").mock(return_value=Response(200, json=[{"id": 1}]))
        result = await TOOLS["kaiten_list_card_types"]["handler"](
            client, {"query": "bug", "limit": 10, "offset": 5}
        )
        assert route.called
        request = route.calls[0].request
        assert "query=bug" in str(request.url)
        assert "limit=10" in str(request.url)
        assert "offset=5" in str(request.url)
        assert result == [{"id": 1}]


class TestGetCardType:
    async def test_get_card_type_required_only(self, client, mock_api):
        route = mock_api.get("/card-types/42").mock(
            return_value=Response(200, json={"id": 42, "name": "Bug"})
        )
        result = await TOOLS["kaiten_get_card_type"]["handler"](client, {"type_id": 42})
        assert route.called
        assert result == {"id": 42, "name": "Bug"}


class TestCreateCardType:
    async def test_create_card_type_required_only(self, client, mock_api):
        route = mock_api.post("/card-types").mock(
            return_value=Response(200, json={"id": 1, "name": "Feature"})
        )
        result = await TOOLS["kaiten_create_card_type"]["handler"](
            client, {"name": "Feature", "letter": "F", "color": 3}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Feature", "letter": "F", "color": 3}
        assert result["name"] == "Feature"

    async def test_create_card_type_all_args(self, client, mock_api):
        route = mock_api.post("/card-types").mock(
            return_value=Response(200, json={"id": 1})
        )
        await TOOLS["kaiten_create_card_type"]["handler"](
            client,
            {
                "name": "Feature",
                "letter": "F",
                "color": 5,
                "description_template": "## Summary\n",
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "name": "Feature",
            "letter": "F",
            "color": 5,
            "description_template": "## Summary\n",
        }


class TestUpdateCardType:
    async def test_update_card_type_required_only(self, client, mock_api):
        route = mock_api.patch("/card-types/10").mock(
            return_value=Response(200, json={"id": 10})
        )
        result = await TOOLS["kaiten_update_card_type"]["handler"](client, {"type_id": 10})
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}
        assert result == {"id": 10}

    async def test_update_card_type_all_args(self, client, mock_api):
        route = mock_api.patch("/card-types/10").mock(
            return_value=Response(200, json={"id": 10})
        )
        await TOOLS["kaiten_update_card_type"]["handler"](
            client,
            {
                "type_id": 10,
                "name": "Renamed",
                "letter": "R",
                "color": 7,
                "description_template": "tmpl",
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "name": "Renamed",
            "letter": "R",
            "color": 7,
            "description_template": "tmpl",
        }


class TestDeleteCardType:
    async def test_delete_card_type_required_only(self, client, mock_api):
        route = mock_api.delete("/card-types/10").mock(
            return_value=Response(204)
        )
        await TOOLS["kaiten_delete_card_type"]["handler"](client, {"type_id": 10})
        assert route.called
