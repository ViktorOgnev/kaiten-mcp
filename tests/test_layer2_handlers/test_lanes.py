"""Layer 2 handler integration tests for lanes tools."""

import json

from httpx import Response

from kaiten_mcp.tools.lanes import TOOLS


class TestListLanes:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/boards/10/lanes").mock(
            return_value=Response(200, json=[{"id": 1, "title": "Default"}])
        )
        result = await TOOLS["kaiten_list_lanes"]["handler"](client, {"board_id": 10})
        assert route.called
        assert result == [{"id": 1, "title": "Default"}]


class TestCreateLane:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/boards/10/lanes").mock(
            return_value=Response(200, json={"id": 3, "title": "Bug Lane"})
        )
        result = await TOOLS["kaiten_create_lane"]["handler"](
            client, {"board_id": 10, "title": "Bug Lane"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "Bug Lane"}
        assert result == {"id": 3, "title": "Bug Lane"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/boards/10/lanes").mock(return_value=Response(200, json={"id": 3}))
        result = await TOOLS["kaiten_create_lane"]["handler"](
            client,
            {
                "board_id": 10,
                "title": "Feature Lane",
                "sort_order": 1.5,
                "row_count": 2,
                "wip_limit": 5,
                "wip_limit_type": 1,
                "default_card_type_id": 3,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "title": "Feature Lane",
            "sort_order": 1.5,
            "row_count": 2,
            "wip_limit": 5,
            "wip_limit_type": 1,
            "default_card_type_id": 3,
        }


class TestUpdateLane:
    async def test_required_only(self, client, mock_api):
        route = mock_api.patch("/boards/10/lanes/3").mock(
            return_value=Response(200, json={"id": 3})
        )
        result = await TOOLS["kaiten_update_lane"]["handler"](
            client, {"board_id": 10, "lane_id": 3}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_all_args(self, client, mock_api):
        route = mock_api.patch("/boards/10/lanes/3").mock(
            return_value=Response(200, json={"id": 3})
        )
        result = await TOOLS["kaiten_update_lane"]["handler"](
            client,
            {
                "board_id": 10,
                "lane_id": 3,
                "title": "Renamed Lane",
                "sort_order": 5.0,
                "row_count": 3,
                "wip_limit": 10,
                "wip_limit_type": 2,
                "default_card_type_id": 6,
                "condition": 2,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "title": "Renamed Lane",
            "sort_order": 5.0,
            "row_count": 3,
            "wip_limit": 10,
            "wip_limit_type": 2,
            "default_card_type_id": 6,
            "condition": 2,
        }


class TestDeleteLane:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/boards/10/lanes/3").mock(return_value=Response(204))
        result = await TOOLS["kaiten_delete_lane"]["handler"](
            client, {"board_id": 10, "lane_id": 3}
        )
        assert route.called
