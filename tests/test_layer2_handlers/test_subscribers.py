"""Layer 2 handler integration tests for tools/subscribers.py."""
import json

import pytest
from httpx import Response

from kaiten_mcp.tools.subscribers import TOOLS


# ---------------------------------------------------------------------------
# Card Subscribers
# ---------------------------------------------------------------------------


class TestListCardSubscribers:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/cards/1/subscribers").mock(
            return_value=Response(200, json=[{"id": 42}])
        )
        result = await TOOLS["kaiten_list_card_subscribers"]["handler"](
            client, {"card_id": 1}
        )
        assert route.called
        assert result == [{"id": 42}]


class TestAddCardSubscriber:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/cards/1/subscribers").mock(
            return_value=Response(200, json={"id": 42})
        )
        result = await TOOLS["kaiten_add_card_subscriber"]["handler"](
            client, {"card_id": 1, "user_id": 42}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"user_id": 42}
        assert result == {"id": 42}


class TestRemoveCardSubscriber:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/cards/1/subscribers/42").mock(
            return_value=Response(200, json={})
        )
        result = await TOOLS["kaiten_remove_card_subscriber"]["handler"](
            client, {"card_id": 1, "user_id": 42}
        )
        assert route.called
        assert result == {}


# ---------------------------------------------------------------------------
# Column Subscribers
# ---------------------------------------------------------------------------


class TestListColumnSubscribers:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/columns/10/subscribers").mock(
            return_value=Response(200, json=[{"id": 7}])
        )
        result = await TOOLS["kaiten_list_column_subscribers"]["handler"](
            client, {"column_id": 10}
        )
        assert route.called
        assert result == [{"id": 7}]


class TestAddColumnSubscriber:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/columns/10/subscribers").mock(
            return_value=Response(200, json={"id": 7})
        )
        result = await TOOLS["kaiten_add_column_subscriber"]["handler"](
            client, {"column_id": 10, "user_id": 7}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"user_id": 7, "type": 1}
        assert result == {"id": 7}

    async def test_explicit_type(self, client, mock_api):
        route = mock_api.post("/columns/10/subscribers").mock(
            return_value=Response(200, json={"id": 7})
        )
        result = await TOOLS["kaiten_add_column_subscriber"]["handler"](
            client, {"column_id": 10, "user_id": 7, "type": 2}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"user_id": 7, "type": 2}


class TestRemoveColumnSubscriber:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/columns/10/subscribers/7").mock(
            return_value=Response(200, json={})
        )
        result = await TOOLS["kaiten_remove_column_subscriber"]["handler"](
            client, {"column_id": 10, "user_id": 7}
        )
        assert route.called
        assert result == {}


# ---------------------------------------------------------------------------
# Subcolumns
# ---------------------------------------------------------------------------


class TestListSubcolumns:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/columns/10/subcolumns").mock(
            return_value=Response(200, json=[{"id": 20, "title": "In Progress"}])
        )
        result = await TOOLS["kaiten_list_subcolumns"]["handler"](
            client, {"column_id": 10}
        )
        assert route.called
        assert result == [{"id": 20, "title": "In Progress"}]


class TestCreateSubcolumn:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/columns/10/subcolumns").mock(
            return_value=Response(200, json={"id": 20, "title": "Done"})
        )
        result = await TOOLS["kaiten_create_subcolumn"]["handler"](
            client, {"column_id": 10, "title": "Done"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "Done"}
        assert result == {"id": 20, "title": "Done"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/columns/10/subcolumns").mock(
            return_value=Response(200, json={"id": 20})
        )
        result = await TOOLS["kaiten_create_subcolumn"]["handler"](
            client, {"column_id": 10, "title": "Done", "sort_order": 3, "wip_limit": 5}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "Done", "sort_order": 3, "wip_limit": 5}


class TestUpdateSubcolumn:
    async def test_required_only(self, client, mock_api):
        route = mock_api.patch("/columns/10/subcolumns/20").mock(
            return_value=Response(200, json={"id": 20})
        )
        result = await TOOLS["kaiten_update_subcolumn"]["handler"](
            client, {"column_id": 10, "subcolumn_id": 20}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_all_args(self, client, mock_api):
        route = mock_api.patch("/columns/10/subcolumns/20").mock(
            return_value=Response(200, json={"id": 20})
        )
        result = await TOOLS["kaiten_update_subcolumn"]["handler"](
            client,
            {
                "column_id": 10,
                "subcolumn_id": 20,
                "title": "Review",
                "sort_order": 1,
                "wip_limit": 3,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "Review", "sort_order": 1, "wip_limit": 3}


class TestDeleteSubcolumn:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/columns/10/subcolumns/20").mock(
            return_value=Response(200, json={})
        )
        result = await TOOLS["kaiten_delete_subcolumn"]["handler"](
            client, {"column_id": 10, "subcolumn_id": 20}
        )
        assert route.called
        assert result == {}
