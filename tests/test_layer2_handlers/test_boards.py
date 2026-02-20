"""Layer 2 handler integration tests for boards tools."""

import json

from httpx import Response

from kaiten_mcp.tools.boards import TOOLS


class TestListBoards:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/spaces/1/boards").mock(
            return_value=Response(200, json=[{"id": 10, "title": "Board A"}])
        )
        result = await TOOLS["kaiten_list_boards"]["handler"](client, {"space_id": 1})
        assert route.called
        assert result == [{"id": 10, "title": "Board A"}]


class TestGetBoard:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/boards/10").mock(
            return_value=Response(200, json={"id": 10, "title": "Board A"})
        )
        result = await TOOLS["kaiten_get_board"]["handler"](client, {"board_id": 10})
        assert route.called
        assert result == {"id": 10, "title": "Board A"}


class TestCreateBoard:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/spaces/1/boards").mock(
            return_value=Response(200, json={"id": 20, "title": "New Board"})
        )
        result = await TOOLS["kaiten_create_board"]["handler"](
            client, {"space_id": 1, "title": "New Board"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "New Board"}
        assert result == {"id": 20, "title": "New Board"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/spaces/1/boards").mock(return_value=Response(200, json={"id": 20}))
        result = await TOOLS["kaiten_create_board"]["handler"](
            client,
            {
                "space_id": 1,
                "title": "Full Board",
                "description": "Board desc",
                "external_id": "ext-1",
                "top": 100.0,
                "left": 200.0,
                "sort_order": 3.5,
                "default_card_type_id": 7,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "title": "Full Board",
            "description": "Board desc",
            "external_id": "ext-1",
            "top": 100.0,
            "left": 200.0,
            "sort_order": 3.5,
            "default_card_type_id": 7,
        }


class TestUpdateBoard:
    async def test_required_only(self, client, mock_api):
        route = mock_api.patch("/spaces/1/boards/10").mock(
            return_value=Response(200, json={"id": 10})
        )
        result = await TOOLS["kaiten_update_board"]["handler"](
            client, {"space_id": 1, "board_id": 10}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_all_args(self, client, mock_api):
        route = mock_api.patch("/spaces/1/boards/10").mock(
            return_value=Response(200, json={"id": 10})
        )
        result = await TOOLS["kaiten_update_board"]["handler"](
            client,
            {
                "space_id": 1,
                "board_id": 10,
                "title": "Renamed Board",
                "description": "New desc",
                "external_id": "ext-2",
                "top": 50.0,
                "left": 75.0,
                "sort_order": 2.0,
                "default_card_type_id": 4,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "title": "Renamed Board",
            "description": "New desc",
            "external_id": "ext-2",
            "top": 50.0,
            "left": 75.0,
            "sort_order": 2.0,
            "default_card_type_id": 4,
        }


class TestDeleteBoard:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/spaces/1/boards/10").mock(return_value=Response(204))
        result = await TOOLS["kaiten_delete_board"]["handler"](
            client, {"space_id": 1, "board_id": 10}
        )
        assert route.called
