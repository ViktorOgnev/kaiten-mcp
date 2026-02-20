"""Layer 2 handler integration tests for spaces tools."""
import json

from httpx import Response

from kaiten_mcp.tools.spaces import TOOLS


class TestListSpaces:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/spaces").mock(
            return_value=Response(200, json=[{"id": 1, "title": "Space One"}])
        )
        result = await TOOLS["kaiten_list_spaces"]["handler"](client, {})
        assert route.called
        assert result == [{"id": 1, "title": "Space One"}]

    async def test_all_args(self, client, mock_api):
        route = mock_api.get("/spaces").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_spaces"]["handler"](
            client, {"archived": True}
        )
        assert route.called
        request = route.calls[0].request
        assert "archived" in str(request.url)
        assert result == []


class TestGetSpace:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/spaces/42").mock(
            return_value=Response(200, json={"id": 42, "title": "My Space"})
        )
        result = await TOOLS["kaiten_get_space"]["handler"](
            client, {"space_id": 42}
        )
        assert route.called
        assert result == {"id": 42, "title": "My Space"}


class TestCreateSpace:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/spaces").mock(
            return_value=Response(200, json={"id": 10, "title": "New"})
        )
        result = await TOOLS["kaiten_create_space"]["handler"](
            client, {"title": "New"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "New"}
        assert result == {"id": 10, "title": "New"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/spaces").mock(
            return_value=Response(200, json={"id": 10})
        )
        result = await TOOLS["kaiten_create_space"]["handler"](
            client,
            {
                "title": "Full Space",
                "description": "A description",
                "access": "by_invite",
                "external_id": "ext-space-1",
                "parent_entity_uid": "uid-parent-1",
                "sort_order": 2.5,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "title": "Full Space",
            "description": "A description",
            "access": "by_invite",
            "external_id": "ext-space-1",
            "parent_entity_uid": "uid-parent-1",
            "sort_order": 2.5,
        }


class TestUpdateSpace:
    async def test_required_only(self, client, mock_api):
        route = mock_api.patch("/spaces/5").mock(
            return_value=Response(200, json={"id": 5})
        )
        result = await TOOLS["kaiten_update_space"]["handler"](
            client, {"space_id": 5}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}
        assert result == {"id": 5}

    async def test_all_args(self, client, mock_api):
        route = mock_api.patch("/spaces/5").mock(
            return_value=Response(200, json={"id": 5})
        )
        result = await TOOLS["kaiten_update_space"]["handler"](
            client,
            {
                "space_id": 5,
                "title": "Renamed",
                "description": "Updated desc",
                "access": "for_everyone",
                "external_id": "ext-space-5",
                "parent_entity_uid": "uid-parent-5",
                "sort_order": 1.0,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "title": "Renamed",
            "description": "Updated desc",
            "access": "for_everyone",
            "external_id": "ext-space-5",
            "parent_entity_uid": "uid-parent-5",
            "sort_order": 1.0,
        }


class TestDeleteSpace:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/spaces/7").mock(
            return_value=Response(204)
        )
        result = await TOOLS["kaiten_delete_space"]["handler"](
            client, {"space_id": 7}
        )
        assert route.called
