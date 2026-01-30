"""Layer 2 handler integration tests for columns tools."""
import json

from httpx import Response

from kaiten_mcp.tools.columns import TOOLS


class TestListColumns:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/boards/10/columns").mock(
            return_value=Response(200, json=[{"id": 1, "title": "To Do"}])
        )
        result = await TOOLS["kaiten_list_columns"]["handler"](
            client, {"board_id": 10}
        )
        assert route.called
        assert result == [{"id": 1, "title": "To Do"}]


class TestCreateColumn:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/boards/10/columns").mock(
            return_value=Response(200, json={"id": 5, "title": "Backlog"})
        )
        result = await TOOLS["kaiten_create_column"]["handler"](
            client, {"board_id": 10, "title": "Backlog", "type": 1}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "Backlog", "type": 1}
        assert result == {"id": 5, "title": "Backlog"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/boards/10/columns").mock(
            return_value=Response(200, json={"id": 5})
        )
        result = await TOOLS["kaiten_create_column"]["handler"](
            client,
            {
                "board_id": 10,
                "title": "In Progress",
                "type": 2,
                "wip_limit": 5,
                "sort_order": 2.0,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "title": "In Progress",
            "type": 2,
            "wip_limit": 5,
            "sort_order": 2.0,
        }


class TestUpdateColumn:
    async def test_required_only(self, client, mock_api):
        route = mock_api.patch("/boards/10/columns/5").mock(
            return_value=Response(200, json={"id": 5})
        )
        result = await TOOLS["kaiten_update_column"]["handler"](
            client, {"board_id": 10, "column_id": 5}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_all_args(self, client, mock_api):
        route = mock_api.patch("/boards/10/columns/5").mock(
            return_value=Response(200, json={"id": 5})
        )
        result = await TOOLS["kaiten_update_column"]["handler"](
            client,
            {
                "board_id": 10,
                "column_id": 5,
                "title": "Done",
                "type": 3,
                "wip_limit": 10,
                "sort_order": 3.5,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "title": "Done",
            "type": 3,
            "wip_limit": 10,
            "sort_order": 3.5,
        }


class TestDeleteColumn:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/boards/10/columns/5").mock(
            return_value=Response(204)
        )
        result = await TOOLS["kaiten_delete_column"]["handler"](
            client, {"board_id": 10, "column_id": 5}
        )
        assert route.called
