"""Integration tests for projects handler layer."""

import json

from httpx import Response

from kaiten_mcp.tools.projects import TOOLS

# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------


class TestListProjects:
    async def test_list_projects_required_only(self, client, mock_api):
        route = mock_api.get("/projects").mock(return_value=Response(200, json=[]))
        result = await TOOLS["kaiten_list_projects"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_projects_returns_list(self, client, mock_api):
        route = mock_api.get("/projects").mock(return_value=Response(200, json=[{"id": 1}]))
        result = await TOOLS["kaiten_list_projects"]["handler"](client, {})
        assert route.called
        assert result == [{"id": 1}]


class TestCreateProject:
    async def test_create_project_required_only(self, client, mock_api):
        route = mock_api.post("/projects").mock(
            return_value=Response(200, json={"id": 1, "name": "Alpha"})
        )
        result = await TOOLS["kaiten_create_project"]["handler"](client, {"title": "Alpha"})
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Alpha"}
        assert result["name"] == "Alpha"

    async def test_create_project_all_args(self, client, mock_api):
        route = mock_api.post("/projects").mock(return_value=Response(200, json={"id": 1}))
        await TOOLS["kaiten_create_project"]["handler"](
            client,
            {
                "title": "Alpha",
                "description": "Main project",
                "work_calendar_id": "cal-uuid-1",
                "settings": {"timeline": {"startHour": 9, "endHour": 18}},
                "properties": {"id_1": "value1"},
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "name": "Alpha",
            "description": "Main project",
            "work_calendar_id": "cal-uuid-1",
            "settings": {"timeline": {"startHour": 9, "endHour": 18}},
            "properties": {"id_1": "value1"},
        }


class TestGetProject:
    async def test_get_project_required_only(self, client, mock_api):
        route = mock_api.get("/projects/proj-uuid-1").mock(
            return_value=Response(200, json={"id": 1})
        )
        result = await TOOLS["kaiten_get_project"]["handler"](
            client, {"project_id": "proj-uuid-1"}
        )
        assert route.called
        assert result == {"id": 1}

    async def test_get_project_with_cards_data(self, client, mock_api):
        route = mock_api.get("/projects/proj-uuid-1").mock(
            return_value=Response(200, json={"id": 1, "cards": []})
        )
        result = await TOOLS["kaiten_get_project"]["handler"](
            client, {"project_id": "proj-uuid-1", "with_cards_data": True}
        )
        assert route.called
        url = str(route.calls[0].request.url)
        assert "with_cards_data" in url
        assert result == {"id": 1, "cards": []}


class TestUpdateProject:
    async def test_update_project_required_only(self, client, mock_api):
        route = mock_api.patch("/projects/proj-uuid-1").mock(
            return_value=Response(200, json={"id": 1})
        )
        result = await TOOLS["kaiten_update_project"]["handler"](
            client, {"project_id": "proj-uuid-1"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_project_all_args(self, client, mock_api):
        route = mock_api.patch("/projects/proj-uuid-1").mock(
            return_value=Response(200, json={"id": 1})
        )
        await TOOLS["kaiten_update_project"]["handler"](
            client,
            {
                "project_id": "proj-uuid-1",
                "title": "Beta",
                "description": "Updated desc",
                "condition": "inactive",
                "work_calendar_id": "cal-uuid-2",
                "settings": {"timeline": {"startHour": 10}},
                "properties": {"id_2": "value2"},
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "name": "Beta",
            "description": "Updated desc",
            "condition": "inactive",
            "work_calendar_id": "cal-uuid-2",
            "settings": {"timeline": {"startHour": 10}},
            "properties": {"id_2": "value2"},
        }


class TestDeleteProject:
    async def test_delete_project_required_only(self, client, mock_api):
        route = mock_api.delete("/projects/proj-uuid-1").mock(return_value=Response(204))
        await TOOLS["kaiten_delete_project"]["handler"](client, {"project_id": "proj-uuid-1"})
        assert route.called


class TestListProjectCards:
    async def test_list_project_cards_required_only(self, client, mock_api):
        route = mock_api.get("/projects/proj-uuid-1/cards").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_project_cards"]["handler"](
            client, {"project_id": "proj-uuid-1"}
        )
        assert route.called
        assert result == []


class TestAddProjectCard:
    async def test_add_project_card_required_only(self, client, mock_api):
        route = mock_api.post("/projects/proj-uuid-1/cards").mock(
            return_value=Response(200, json={"project_id": "proj-uuid-1", "card_id": 99})
        )
        result = await TOOLS["kaiten_add_project_card"]["handler"](
            client, {"project_id": "proj-uuid-1", "card_id": 99}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"card_id": 99}


class TestRemoveProjectCard:
    async def test_remove_project_card_required_only(self, client, mock_api):
        route = mock_api.delete("/projects/proj-uuid-1/cards/99").mock(return_value=Response(204))
        await TOOLS["kaiten_remove_project_card"]["handler"](
            client, {"project_id": "proj-uuid-1", "card_id": 99}
        )
        assert route.called


# ---------------------------------------------------------------------------
# Sprints
# ---------------------------------------------------------------------------


class TestListSprints:
    async def test_list_sprints_required_only(self, client, mock_api):
        route = mock_api.get("/sprints").mock(return_value=Response(200, json=[]))
        result = await TOOLS["kaiten_list_sprints"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_sprints_all_args(self, client, mock_api):
        route = mock_api.get("/sprints").mock(return_value=Response(200, json=[{"id": 1}]))
        await TOOLS["kaiten_list_sprints"]["handler"](
            client, {"active": True, "limit": 5, "offset": 0}
        )
        url = str(route.calls[0].request.url)
        assert "active=true" in url.lower() or "active=True" in url
        assert "limit=5" in url
        assert "offset=0" in url


class TestCreateSprint:
    async def test_create_sprint_required_only(self, client, mock_api):
        route = mock_api.post("/sprints").mock(
            return_value=Response(200, json={"id": 1, "title": "Sprint 1"})
        )
        result = await TOOLS["kaiten_create_sprint"]["handler"](
            client, {"title": "Sprint 1", "board_id": 10}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "Sprint 1", "board_id": 10}

    async def test_create_sprint_all_args(self, client, mock_api):
        route = mock_api.post("/sprints").mock(return_value=Response(200, json={"id": 1}))
        await TOOLS["kaiten_create_sprint"]["handler"](
            client,
            {
                "title": "Sprint 1",
                "board_id": 10,
                "goal": "Deliver MVP",
                "start_date": "2025-01-01",
                "finish_date": "2025-01-14",
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "title": "Sprint 1",
            "board_id": 10,
            "goal": "Deliver MVP",
            "start_date": "2025-01-01",
            "finish_date": "2025-01-14",
        }


class TestGetSprint:
    async def test_get_sprint_required_only(self, client, mock_api):
        route = mock_api.get("/sprints/1").mock(return_value=Response(200, json={"id": 1}))
        result = await TOOLS["kaiten_get_sprint"]["handler"](client, {"sprint_id": 1})
        assert route.called
        assert result == {"id": 1}

    async def test_get_sprint_exclude_deleted_cards(self, client, mock_api):
        route = mock_api.get("/sprints/1").mock(
            return_value=Response(200, json={"id": 1, "cards": []})
        )
        result = await TOOLS["kaiten_get_sprint"]["handler"](
            client, {"sprint_id": 1, "exclude_deleted_cards": True}
        )
        assert route.called
        url = str(route.calls[0].request.url)
        assert "exclude_deleted_cards" in url
        assert result == {"id": 1, "cards": []}


class TestUpdateSprint:
    async def test_update_sprint_required_only(self, client, mock_api):
        route = mock_api.patch("/sprints/1").mock(return_value=Response(200, json={"id": 1}))
        result = await TOOLS["kaiten_update_sprint"]["handler"](client, {"sprint_id": 1})
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_sprint_all_args(self, client, mock_api):
        route = mock_api.patch("/sprints/1").mock(return_value=Response(200, json={"id": 1}))
        await TOOLS["kaiten_update_sprint"]["handler"](
            client,
            {
                "sprint_id": 1,
                "title": "Sprint 1 (revised)",
                "goal": "Updated goal",
                "start_date": "2025-01-02",
                "finish_date": "2025-01-15",
                "active": False,
                "archive_done_cards": True,
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "title": "Sprint 1 (revised)",
            "goal": "Updated goal",
            "start_date": "2025-01-02",
            "finish_date": "2025-01-15",
            "active": False,
            "archive_done_cards": True,
        }


class TestDeleteSprint:
    async def test_delete_sprint_required_only(self, client, mock_api):
        route = mock_api.delete("/sprints/1").mock(return_value=Response(204))
        await TOOLS["kaiten_delete_sprint"]["handler"](client, {"sprint_id": 1})
        assert route.called
