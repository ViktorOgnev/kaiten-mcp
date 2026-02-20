"""Layer 2 handler integration tests for tools/time_logs.py."""

import json

from httpx import Response

from kaiten_mcp.tools.time_logs import TOOLS


class TestListCardTimeLogs:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/cards/1/time-logs").mock(
            return_value=Response(200, json=[{"id": 50, "time_spent": 60}])
        )
        result = await TOOLS["kaiten_list_card_time_logs"]["handler"](client, {"card_id": 1})
        assert route.called
        assert result == [{"id": 50, "time_spent": 60}]

    async def test_all_args(self, client, mock_api):
        route = mock_api.get("/cards/1/time-logs").mock(return_value=Response(200, json=[]))
        result = await TOOLS["kaiten_list_card_time_logs"]["handler"](
            client, {"card_id": 1, "for_date": "2025-01-15", "personal": True}
        )
        assert route.called
        req = route.calls[0].request
        assert "for_date=2025-01-15" in str(req.url)
        assert "personal" in str(req.url)


class TestCreateTimeLog:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/cards/1/time-logs").mock(
            return_value=Response(200, json={"id": 50, "time_spent": 30})
        )
        result = await TOOLS["kaiten_create_time_log"]["handler"](
            client, {"card_id": 1, "time_spent": 30}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"time_spent": 30, "role_id": -1}
        assert result == {"id": 50, "time_spent": 30}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/cards/1/time-logs").mock(
            return_value=Response(200, json={"id": 50})
        )
        result = await TOOLS["kaiten_create_time_log"]["handler"](
            client,
            {
                "card_id": 1,
                "time_spent": 120,
                "role_id": 5,
                "for_date": "2025-03-01",
                "comment": "Worked on feature",
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "time_spent": 120,
            "role_id": 5,
            "for_date": "2025-03-01",
            "comment": "Worked on feature",
        }


class TestUpdateTimeLog:
    async def test_required_only(self, client, mock_api):
        route = mock_api.patch("/cards/1/time-logs/50").mock(
            return_value=Response(200, json={"id": 50})
        )
        result = await TOOLS["kaiten_update_time_log"]["handler"](
            client, {"card_id": 1, "time_log_id": 50}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_all_args(self, client, mock_api):
        route = mock_api.patch("/cards/1/time-logs/50").mock(
            return_value=Response(200, json={"id": 50})
        )
        result = await TOOLS["kaiten_update_time_log"]["handler"](
            client,
            {
                "card_id": 1,
                "time_log_id": 50,
                "time_spent": 90,
                "role_id": 3,
                "comment": "Updated log",
                "for_date": "2025-03-02",
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "time_spent": 90,
            "role_id": 3,
            "comment": "Updated log",
            "for_date": "2025-03-02",
        }


class TestDeleteTimeLog:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/cards/1/time-logs/50").mock(return_value=Response(200, json={}))
        result = await TOOLS["kaiten_delete_time_log"]["handler"](
            client, {"card_id": 1, "time_log_id": 50}
        )
        assert route.called
        assert result == {}
