"""Integration tests for automations handler layer."""
import json

import pytest
from httpx import Response

from kaiten_mcp.tools.automations import TOOLS


# ---------------------------------------------------------------------------
# Space Automations
# ---------------------------------------------------------------------------


class TestListAutomations:
    async def test_list_automations_required_only(self, client, mock_api):
        route = mock_api.get("/spaces/1/automations").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_automations"]["handler"](
            client, {"space_id": 1}
        )
        assert route.called
        assert result == []


class TestCreateAutomation:
    async def test_create_automation_required_only(self, client, mock_api):
        route = mock_api.post("/spaces/1/automations").mock(
            return_value=Response(200, json={"id": 5, "name": "Auto-assign"})
        )
        trigger = {"type": "card_created"}
        action = {"type": "assign_user", "user_id": 99}
        result = await TOOLS["kaiten_create_automation"]["handler"](
            client,
            {"space_id": 1, "name": "Auto-assign", "trigger": trigger, "action": action},
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Auto-assign", "trigger": trigger, "action": action}
        assert result["name"] == "Auto-assign"

    async def test_create_automation_all_args(self, client, mock_api):
        route = mock_api.post("/spaces/1/automations").mock(
            return_value=Response(200, json={"id": 5})
        )
        trigger = {"type": "card_moved"}
        action = {"type": "notify"}
        await TOOLS["kaiten_create_automation"]["handler"](
            client,
            {
                "space_id": 1,
                "name": "Notify on move",
                "trigger": trigger,
                "action": action,
                "active": False,
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "name": "Notify on move",
            "trigger": trigger,
            "action": action,
            "active": False,
        }


class TestGetAutomation:
    async def test_get_automation_required_only(self, client, mock_api):
        route = mock_api.get("/spaces/1/automations/5").mock(
            return_value=Response(200, json={"id": 5})
        )
        result = await TOOLS["kaiten_get_automation"]["handler"](
            client, {"space_id": 1, "automation_id": 5}
        )
        assert route.called
        assert result == {"id": 5}


class TestUpdateAutomation:
    async def test_update_automation_required_only(self, client, mock_api):
        route = mock_api.patch("/spaces/1/automations/5").mock(
            return_value=Response(200, json={"id": 5})
        )
        result = await TOOLS["kaiten_update_automation"]["handler"](
            client, {"space_id": 1, "automation_id": 5}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_automation_all_args(self, client, mock_api):
        route = mock_api.patch("/spaces/1/automations/5").mock(
            return_value=Response(200, json={"id": 5})
        )
        new_trigger = {"type": "card_updated"}
        new_action = {"type": "send_email"}
        await TOOLS["kaiten_update_automation"]["handler"](
            client,
            {
                "space_id": 1,
                "automation_id": 5,
                "name": "Renamed",
                "trigger": new_trigger,
                "action": new_action,
                "active": True,
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "name": "Renamed",
            "trigger": new_trigger,
            "action": new_action,
            "active": True,
        }


class TestDeleteAutomation:
    async def test_delete_automation_required_only(self, client, mock_api):
        route = mock_api.delete("/spaces/1/automations/5").mock(
            return_value=Response(200, json=None)
        )
        await TOOLS["kaiten_delete_automation"]["handler"](
            client, {"space_id": 1, "automation_id": 5}
        )
        assert route.called


# ---------------------------------------------------------------------------
# Company Workflows
# ---------------------------------------------------------------------------


class TestListWorkflows:
    async def test_list_workflows_required_only(self, client, mock_api):
        route = mock_api.get("/company/workflows").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_workflows"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_workflows_all_args(self, client, mock_api):
        route = mock_api.get("/company/workflows").mock(
            return_value=Response(200, json=[{"id": 1}])
        )
        await TOOLS["kaiten_list_workflows"]["handler"](
            client, {"query": "dev", "limit": 5, "offset": 10}
        )
        url = str(route.calls[0].request.url)
        assert "query=dev" in url
        assert "limit=5" in url
        assert "offset=10" in url


class TestCreateWorkflow:
    async def test_create_workflow_required_only(self, client, mock_api):
        route = mock_api.post("/company/workflows").mock(
            return_value=Response(200, json={"id": 1, "name": "Dev Pipeline"})
        )
        result = await TOOLS["kaiten_create_workflow"]["handler"](
            client, {"name": "Dev Pipeline"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Dev Pipeline"}

    async def test_create_workflow_all_args(self, client, mock_api):
        route = mock_api.post("/company/workflows").mock(
            return_value=Response(200, json={"id": 1})
        )
        await TOOLS["kaiten_create_workflow"]["handler"](
            client, {"name": "Dev Pipeline", "description": "Main dev workflow"}
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Dev Pipeline", "description": "Main dev workflow"}


class TestGetWorkflow:
    async def test_get_workflow_required_only(self, client, mock_api):
        route = mock_api.get("/company/workflows/1").mock(
            return_value=Response(200, json={"id": 1})
        )
        result = await TOOLS["kaiten_get_workflow"]["handler"](
            client, {"workflow_id": 1}
        )
        assert route.called
        assert result == {"id": 1}


class TestUpdateWorkflow:
    async def test_update_workflow_required_only(self, client, mock_api):
        route = mock_api.patch("/company/workflows/1").mock(
            return_value=Response(200, json={"id": 1})
        )
        result = await TOOLS["kaiten_update_workflow"]["handler"](
            client, {"workflow_id": 1}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_workflow_all_args(self, client, mock_api):
        route = mock_api.patch("/company/workflows/1").mock(
            return_value=Response(200, json={"id": 1})
        )
        await TOOLS["kaiten_update_workflow"]["handler"](
            client,
            {"workflow_id": 1, "name": "Renamed", "description": "Updated desc"},
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Renamed", "description": "Updated desc"}


class TestDeleteWorkflow:
    async def test_delete_workflow_required_only(self, client, mock_api):
        route = mock_api.delete("/company/workflows/1").mock(
            return_value=Response(200, json=None)
        )
        await TOOLS["kaiten_delete_workflow"]["handler"](client, {"workflow_id": 1})
        assert route.called
