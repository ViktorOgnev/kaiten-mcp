"""Integration tests for automations handler layer."""

import json

from httpx import Response

from kaiten_mcp.tools.automations import TOOLS

# ---------------------------------------------------------------------------
# Space Automations
# ---------------------------------------------------------------------------


class TestListAutomations:
    async def test_list_automations_required_only(self, client, mock_api):
        route = mock_api.get("/spaces/1/automations").mock(return_value=Response(200, json=[]))
        result = await TOOLS["kaiten_list_automations"]["handler"](client, {"space_id": 1})
        assert route.called
        assert result == []


class TestCreateAutomation:
    async def test_create_automation_required_only(self, client, mock_api):
        route = mock_api.post("/spaces/1/automations").mock(
            return_value=Response(200, json={"id": 5, "name": "Auto-assign"})
        )
        trigger = {"type": "card_created"}
        actions = [{"type": "assign_user", "data": {"user_id": 99}}]
        result = await TOOLS["kaiten_create_automation"]["handler"](
            client,
            {"space_id": 1, "name": "Auto-assign", "trigger": trigger, "actions": actions},
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Auto-assign", "trigger": trigger, "actions": actions}
        assert result["name"] == "Auto-assign"

    async def test_create_automation_all_args(self, client, mock_api):
        route = mock_api.post("/spaces/1/automations").mock(
            return_value=Response(200, json={"id": 5})
        )
        trigger = {"type": "card_moved"}
        actions = [{"type": "notify"}]
        conditions = {"clause": "and", "conditions": []}
        await TOOLS["kaiten_create_automation"]["handler"](
            client,
            {
                "space_id": 1,
                "name": "Notify on move",
                "trigger": trigger,
                "actions": actions,
                "conditions": conditions,
                "type": "on_action",
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "name": "Notify on move",
            "trigger": trigger,
            "actions": actions,
            "conditions": conditions,
            "type": "on_action",
        }


class TestGetAutomation:
    async def test_get_automation_required_only(self, client, mock_api):
        route = mock_api.get("/spaces/1/automations/auto-uuid-5").mock(
            return_value=Response(200, json={"id": 5})
        )
        result = await TOOLS["kaiten_get_automation"]["handler"](
            client, {"space_id": 1, "automation_id": "auto-uuid-5"}
        )
        assert route.called
        assert result == {"id": 5}


class TestUpdateAutomation:
    async def test_update_automation_required_only(self, client, mock_api):
        route = mock_api.patch("/spaces/1/automations/auto-uuid-5").mock(
            return_value=Response(200, json={"id": 5})
        )
        result = await TOOLS["kaiten_update_automation"]["handler"](
            client, {"space_id": 1, "automation_id": "auto-uuid-5"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_automation_all_args(self, client, mock_api):
        route = mock_api.patch("/spaces/1/automations/auto-uuid-5").mock(
            return_value=Response(200, json={"id": 5})
        )
        new_trigger = {"type": "card_updated"}
        new_actions = [{"type": "send_email"}]
        new_conditions = {"clause": "or", "conditions": []}
        await TOOLS["kaiten_update_automation"]["handler"](
            client,
            {
                "space_id": 1,
                "automation_id": "auto-uuid-5",
                "name": "Renamed",
                "trigger": new_trigger,
                "actions": new_actions,
                "conditions": new_conditions,
                "status": "disabled",
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "name": "Renamed",
            "trigger": new_trigger,
            "actions": new_actions,
            "conditions": new_conditions,
            "status": "disabled",
        }


class TestDeleteAutomation:
    async def test_delete_automation_required_only(self, client, mock_api):
        route = mock_api.delete("/spaces/1/automations/auto-uuid-5").mock(
            return_value=Response(204)
        )
        await TOOLS["kaiten_delete_automation"]["handler"](
            client, {"space_id": 1, "automation_id": "auto-uuid-5"}
        )
        assert route.called


class TestCopyAutomation:
    async def test_copy_automation_required_only(self, client, mock_api):
        route = mock_api.post("/spaces/1/automations/auto-uuid-5/copy").mock(
            return_value=Response(200, json={"id": "new-uuid", "name": "Copy"})
        )
        result = await TOOLS["kaiten_copy_automation"]["handler"](
            client,
            {"space_id": 1, "automation_id": "auto-uuid-5", "target_space_id": 2},
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"targetSpaceId": 2}
        assert result["id"] == "new-uuid"


# ---------------------------------------------------------------------------
# Company Workflows
# ---------------------------------------------------------------------------


class TestListWorkflows:
    async def test_list_workflows_required_only(self, client, mock_api):
        route = mock_api.get("/company/workflows").mock(return_value=Response(200, json=[]))
        result = await TOOLS["kaiten_list_workflows"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_workflows_all_args(self, client, mock_api):
        route = mock_api.get("/company/workflows").mock(
            return_value=Response(200, json=[{"id": 1}])
        )
        await TOOLS["kaiten_list_workflows"]["handler"](client, {"limit": 5, "offset": 10})
        url = str(route.calls[0].request.url)
        assert "limit=5" in url
        assert "offset=10" in url


class TestCreateWorkflow:
    async def test_create_workflow_required_only(self, client, mock_api):
        route = mock_api.post("/company/workflows").mock(
            return_value=Response(200, json={"id": 1, "name": "Dev Pipeline"})
        )
        stages = [{"id": "s1", "name": "Queue", "type": "queue"}]
        transitions = [{"id": "t1", "prev_stage_id": "s1", "next_stage_id": "s2"}]
        result = await TOOLS["kaiten_create_workflow"]["handler"](
            client, {"name": "Dev Pipeline", "stages": stages, "transitions": transitions}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Dev Pipeline", "stages": stages, "transitions": transitions}

    async def test_create_workflow_all_args(self, client, mock_api):
        """Company workflows accept: name, stages, transitions. No card_type_uids."""
        route = mock_api.post("/company/workflows").mock(
            return_value=Response(200, json={"id": 1})
        )
        stages = [
            {"id": "s1", "name": "Queue", "type": "queue"},
            {"id": "s2", "name": "Done", "type": "done"},
        ]
        transitions = [{"id": "t1", "prev_stage_id": "s1", "next_stage_id": "s2"}]
        await TOOLS["kaiten_create_workflow"]["handler"](
            client,
            {
                "name": "Dev Pipeline",
                "stages": stages,
                "transitions": transitions,
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "name": "Dev Pipeline",
            "stages": stages,
            "transitions": transitions,
        }


class TestGetWorkflow:
    async def test_get_workflow_required_only(self, client, mock_api):
        route = mock_api.get("/company/workflows/wf-uuid-1").mock(
            return_value=Response(200, json={"id": 1})
        )
        result = await TOOLS["kaiten_get_workflow"]["handler"](
            client, {"workflow_id": "wf-uuid-1"}
        )
        assert route.called
        assert result == {"id": 1}


class TestUpdateWorkflow:
    async def test_update_workflow_required_only(self, client, mock_api):
        route = mock_api.patch("/company/workflows/wf-uuid-1").mock(
            return_value=Response(200, json={"id": 1})
        )
        result = await TOOLS["kaiten_update_workflow"]["handler"](
            client, {"workflow_id": "wf-uuid-1"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_workflow_all_args(self, client, mock_api):
        route = mock_api.patch("/company/workflows/wf-uuid-1").mock(
            return_value=Response(200, json={"id": 1})
        )
        stages = [{"id": "s1", "name": "Queue", "type": "queue"}]
        transitions = [{"id": "t1", "prev_stage_id": "s1", "next_stage_id": "s2"}]
        await TOOLS["kaiten_update_workflow"]["handler"](
            client,
            {
                "workflow_id": "wf-uuid-1",
                "name": "Renamed",
                "stages": stages,
                "transitions": transitions,
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "name": "Renamed",
            "stages": stages,
            "transitions": transitions,
        }


class TestDeleteWorkflow:
    async def test_delete_workflow_required_only(self, client, mock_api):
        route = mock_api.delete("/company/workflows/wf-uuid-1").mock(return_value=Response(204))
        await TOOLS["kaiten_delete_workflow"]["handler"](client, {"workflow_id": "wf-uuid-1"})
        assert route.called
