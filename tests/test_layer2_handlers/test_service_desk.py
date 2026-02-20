"""Integration tests for service_desk handler layer."""
import json

import pytest
from httpx import Response

from kaiten_mcp.tools.service_desk import TOOLS


# ---------------------------------------------------------------------------
# SD Requests
# ---------------------------------------------------------------------------


class TestListSdRequests:
    async def test_list_sd_requests_required_only(self, client, mock_api):
        route = mock_api.get("/service-desk/requests").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_sd_requests"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_sd_requests_all_args(self, client, mock_api):
        route = mock_api.get("/service-desk/requests").mock(
            return_value=Response(200, json=[{"id": 1}])
        )
        await TOOLS["kaiten_list_sd_requests"]["handler"](
            client, {"query": "urgent", "limit": 20, "offset": 0}
        )
        url = str(route.calls[0].request.url)
        assert "query=urgent" in url
        assert "limit=20" in url
        assert "offset=0" in url


class TestCreateSdRequest:
    async def test_create_sd_request_required_only(self, client, mock_api):
        route = mock_api.post("/service-desk/requests").mock(
            return_value=Response(200, json={"id": 1, "title": "Fix login"})
        )
        result = await TOOLS["kaiten_create_sd_request"]["handler"](
            client, {"title": "Fix login", "service_id": 3}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "Fix login", "service_id": 3}
        assert result["title"] == "Fix login"

    async def test_create_sd_request_all_args(self, client, mock_api):
        route = mock_api.post("/service-desk/requests").mock(
            return_value=Response(200, json={"id": 1})
        )
        await TOOLS["kaiten_create_sd_request"]["handler"](
            client,
            {
                "title": "Fix login",
                "service_id": 3,
                "description": "Users cannot log in",
                "priority": "high",
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "title": "Fix login",
            "service_id": 3,
            "description": "Users cannot log in",
            "priority": "high",
        }


class TestGetSdRequest:
    async def test_get_sd_request_required_only(self, client, mock_api):
        route = mock_api.get("/service-desk/requests/1").mock(
            return_value=Response(200, json={"id": 1})
        )
        result = await TOOLS["kaiten_get_sd_request"]["handler"](
            client, {"request_id": 1}
        )
        assert route.called
        assert result == {"id": 1}


class TestUpdateSdRequest:
    async def test_update_sd_request_required_only(self, client, mock_api):
        route = mock_api.patch("/service-desk/requests/1").mock(
            return_value=Response(200, json={"id": 1})
        )
        result = await TOOLS["kaiten_update_sd_request"]["handler"](
            client, {"request_id": 1}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_sd_request_all_args(self, client, mock_api):
        route = mock_api.patch("/service-desk/requests/1").mock(
            return_value=Response(200, json={"id": 1})
        )
        await TOOLS["kaiten_update_sd_request"]["handler"](
            client,
            {
                "request_id": 1,
                "title": "Updated title",
                "description": "Updated desc",
                "priority": "low",
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "title": "Updated title",
            "description": "Updated desc",
            "priority": "low",
        }


class TestDeleteSdRequest:
    async def test_delete_sd_request_required_only(self, client, mock_api):
        route = mock_api.delete("/service-desk/requests/1").mock(
            return_value=Response(204)
        )
        await TOOLS["kaiten_delete_sd_request"]["handler"](
            client, {"request_id": 1}
        )
        assert route.called


# ---------------------------------------------------------------------------
# SD Services
# ---------------------------------------------------------------------------


class TestListSdServices:
    async def test_list_sd_services_required_only(self, client, mock_api):
        route = mock_api.get("/service-desk/services").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_sd_services"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_sd_services_all_args(self, client, mock_api):
        route = mock_api.get("/service-desk/services").mock(
            return_value=Response(200, json=[{"id": 1}])
        )
        await TOOLS["kaiten_list_sd_services"]["handler"](
            client,
            {"query": "IT", "include_archived": True, "limit": 5, "offset": 0},
        )
        url = str(route.calls[0].request.url)
        assert "query=IT" in url
        assert "include_archived=true" in url.lower() or "include_archived=True" in url
        assert "limit=5" in url
        assert "offset=0" in url


class TestGetSdService:
    async def test_get_sd_service_required_only(self, client, mock_api):
        route = mock_api.get("/service-desk/services/3").mock(
            return_value=Response(200, json={"id": 3})
        )
        result = await TOOLS["kaiten_get_sd_service"]["handler"](
            client, {"service_id": 3}
        )
        assert route.called
        assert result == {"id": 3}


# ---------------------------------------------------------------------------
# SD Organizations
# ---------------------------------------------------------------------------


class TestListSdOrganizations:
    async def test_list_sd_organizations_required_only(self, client, mock_api):
        route = mock_api.get("/service-desk/organizations").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_sd_organizations"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_sd_organizations_all_args(self, client, mock_api):
        route = mock_api.get("/service-desk/organizations").mock(
            return_value=Response(200, json=[{"id": 1}])
        )
        await TOOLS["kaiten_list_sd_organizations"]["handler"](
            client,
            {"query": "Acme", "includeUsers": True, "limit": 10, "offset": 0},
        )
        url = str(route.calls[0].request.url)
        assert "query=Acme" in url
        assert "includeUsers=True" in url or "includeUsers=true" in url
        assert "limit=10" in url
        assert "offset=0" in url


class TestCreateSdOrganization:
    async def test_create_sd_organization_required_only(self, client, mock_api):
        route = mock_api.post("/service-desk/organizations").mock(
            return_value=Response(200, json={"id": 1, "name": "Acme"})
        )
        result = await TOOLS["kaiten_create_sd_organization"]["handler"](
            client, {"name": "Acme"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Acme"}

    async def test_create_sd_organization_all_args(self, client, mock_api):
        route = mock_api.post("/service-desk/organizations").mock(
            return_value=Response(200, json={"id": 1})
        )
        await TOOLS["kaiten_create_sd_organization"]["handler"](
            client, {"name": "Acme", "description": "Acme Corp"}
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Acme", "description": "Acme Corp"}


class TestGetSdOrganization:
    async def test_get_sd_organization_required_only(self, client, mock_api):
        route = mock_api.get("/service-desk/organizations/1").mock(
            return_value=Response(200, json={"id": 1})
        )
        result = await TOOLS["kaiten_get_sd_organization"]["handler"](
            client, {"organization_id": 1}
        )
        assert route.called
        assert result == {"id": 1}


class TestUpdateSdOrganization:
    async def test_update_sd_organization_required_only(self, client, mock_api):
        route = mock_api.patch("/service-desk/organizations/1").mock(
            return_value=Response(200, json={"id": 1})
        )
        result = await TOOLS["kaiten_update_sd_organization"]["handler"](
            client, {"organization_id": 1}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_sd_organization_all_args(self, client, mock_api):
        route = mock_api.patch("/service-desk/organizations/1").mock(
            return_value=Response(200, json={"id": 1})
        )
        await TOOLS["kaiten_update_sd_organization"]["handler"](
            client,
            {"organization_id": 1, "name": "Acme Inc", "description": "Renamed"},
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Acme Inc", "description": "Renamed"}


class TestDeleteSdOrganization:
    async def test_delete_sd_organization_required_only(self, client, mock_api):
        route = mock_api.delete("/service-desk/organizations/1").mock(
            return_value=Response(204)
        )
        await TOOLS["kaiten_delete_sd_organization"]["handler"](
            client, {"organization_id": 1}
        )
        assert route.called


# ---------------------------------------------------------------------------
# SD SLA
# ---------------------------------------------------------------------------


class TestListSdSla:
    async def test_list_sd_sla_required_only(self, client, mock_api):
        route = mock_api.get("/service-desk/sla").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_sd_sla"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_sd_sla_all_args(self, client, mock_api):
        route = mock_api.get("/service-desk/sla").mock(
            return_value=Response(200, json=[{"id": 1}])
        )
        await TOOLS["kaiten_list_sd_sla"]["handler"](
            client, {"limit": 10, "offset": 5}
        )
        url = str(route.calls[0].request.url)
        assert "limit=10" in url
        assert "offset=5" in url


class TestGetSdSla:
    async def test_get_sd_sla_required_only(self, client, mock_api):
        route = mock_api.get("/service-desk/sla/1").mock(
            return_value=Response(200, json={"id": 1})
        )
        result = await TOOLS["kaiten_get_sd_sla"]["handler"](client, {"sla_id": 1})
        assert route.called
        assert result == {"id": 1}


# ---------------------------------------------------------------------------
# SD Services (create / update / delete)
# ---------------------------------------------------------------------------


class TestCreateSdService:
    async def test_create_sd_service_required_only(self, client, mock_api):
        route = mock_api.post("/service-desk/services").mock(
            return_value=Response(200, json={"id": 5, "name": "IT Support"})
        )
        result = await TOOLS["kaiten_create_sd_service"]["handler"](
            client, {"name": "IT Support", "board_id": 10, "position": 1}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "IT Support", "board_id": 10, "position": 1}
        assert result["name"] == "IT Support"

    async def test_create_sd_service_all_args(self, client, mock_api):
        route = mock_api.post("/service-desk/services").mock(
            return_value=Response(200, json={"id": 5})
        )
        await TOOLS["kaiten_create_sd_service"]["handler"](
            client,
            {
                "name": "IT Support",
                "board_id": 10,
                "position": 1,
                "description": "General IT",
                "template_description": "Describe issue",
                "lng": "en",
                "display_status": "by_column",
                "column_id": 20,
                "lane_id": 30,
                "type_id": 40,
                "email_settings": 7,
                "fields_settings": {"field1": True},
                "settings": {"allowed_email_masks": ["@acme.com"]},
                "allow_to_add_external_recipients": True,
                "hide_in_list": False,
                "is_default": True,
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body["name"] == "IT Support"
        assert body["board_id"] == 10
        assert body["position"] == 1
        assert body["description"] == "General IT"
        assert body["template_description"] == "Describe issue"
        assert body["lng"] == "en"
        assert body["display_status"] == "by_column"
        assert body["column_id"] == 20
        assert body["lane_id"] == 30
        assert body["type_id"] == 40
        assert body["email_settings"] == 7
        assert body["fields_settings"] == {"field1": True}
        assert body["settings"] == {"allowed_email_masks": ["@acme.com"]}
        assert body["allow_to_add_external_recipients"] is True
        assert body["hide_in_list"] is False
        assert body["is_default"] is True


class TestUpdateSdService:
    async def test_update_sd_service_required_only(self, client, mock_api):
        route = mock_api.patch("/service-desk/services/5").mock(
            return_value=Response(200, json={"id": 5})
        )
        result = await TOOLS["kaiten_update_sd_service"]["handler"](
            client, {"service_id": 5}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_sd_service_all_args(self, client, mock_api):
        route = mock_api.patch("/service-desk/services/5").mock(
            return_value=Response(200, json={"id": 5})
        )
        await TOOLS["kaiten_update_sd_service"]["handler"](
            client,
            {
                "service_id": 5,
                "name": "Updated",
                "description": "New desc",
                "template_description": "Template",
                "lng": "ru",
                "display_status": "by_state",
                "board_id": 11,
                "column_id": 21,
                "lane_id": 31,
                "type_id": 41,
                "position": 2,
                "email_settings": 3,
                "fields_settings": {"f": 1},
                "settings": {"s": 2},
                "archived": True,
                "allow_to_add_external_recipients": False,
                "hide_in_list": True,
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body["name"] == "Updated"
        assert body["description"] == "New desc"
        assert body["template_description"] == "Template"
        assert body["lng"] == "ru"
        assert body["display_status"] == "by_state"
        assert body["board_id"] == 11
        assert body["column_id"] == 21
        assert body["lane_id"] == 31
        assert body["type_id"] == 41
        assert body["position"] == 2
        assert body["email_settings"] == 3
        assert body["fields_settings"] == {"f": 1}
        assert body["settings"] == {"s": 2}
        assert body["archived"] is True
        assert body["allow_to_add_external_recipients"] is False
        assert body["hide_in_list"] is True


class TestDeleteSdService:
    async def test_delete_sd_service_required_only(self, client, mock_api):
        route = mock_api.patch("/service-desk/services/5").mock(
            return_value=Response(200, json={"id": 5, "archived": True})
        )
        result = await TOOLS["kaiten_delete_sd_service"]["handler"](
            client, {"service_id": 5}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"archived": True}


# ---------------------------------------------------------------------------
# SD SLA (create / update / delete)
# ---------------------------------------------------------------------------


class TestCreateSdSla:
    async def test_create_sd_sla_required_only(self, client, mock_api):
        route = mock_api.post("/service-desk/sla").mock(
            return_value=Response(200, json={"id": "uuid-1", "name": "Gold"})
        )
        result = await TOOLS["kaiten_create_sd_sla"]["handler"](
            client, {"name": "Gold", "rules": [{"time": 3600}]}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Gold", "rules": [{"time": 3600}]}
        assert result["name"] == "Gold"

    async def test_create_sd_sla_all_args(self, client, mock_api):
        route = mock_api.post("/service-desk/sla").mock(
            return_value=Response(200, json={"id": "uuid-1"})
        )
        await TOOLS["kaiten_create_sd_sla"]["handler"](
            client,
            {
                "name": "Gold",
                "rules": [{"time": 3600}],
                "notification_settings": {"email": True},
                "v2": True,
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "name": "Gold",
            "rules": [{"time": 3600}],
            "notification_settings": {"email": True},
            "v2": True,
        }


class TestUpdateSdSla:
    async def test_update_sd_sla_required_only(self, client, mock_api):
        route = mock_api.patch("/service-desk/sla/uuid-1").mock(
            return_value=Response(200, json={"id": "uuid-1"})
        )
        result = await TOOLS["kaiten_update_sd_sla"]["handler"](
            client, {"sla_id": "uuid-1"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_sd_sla_all_args(self, client, mock_api):
        route = mock_api.patch("/service-desk/sla/uuid-1").mock(
            return_value=Response(200, json={"id": "uuid-1"})
        )
        await TOOLS["kaiten_update_sd_sla"]["handler"](
            client,
            {
                "sla_id": "uuid-1",
                "name": "Platinum",
                "status": "active",
                "notification_settings": {"slack": True},
                "should_delete_sla_from_cards": True,
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "name": "Platinum",
            "status": "active",
            "notification_settings": {"slack": True},
            "should_delete_sla_from_cards": True,
        }


class TestDeleteSdSla:
    async def test_delete_sd_sla_required_only(self, client, mock_api):
        route = mock_api.delete("/service-desk/sla/uuid-1").mock(
            return_value=Response(204)
        )
        await TOOLS["kaiten_delete_sd_sla"]["handler"](
            client, {"sla_id": "uuid-1"}
        )
        assert route.called


# ---------------------------------------------------------------------------
# SD Template Answers
# ---------------------------------------------------------------------------


class TestListSdTemplateAnswers:
    async def test_list_sd_template_answers(self, client, mock_api):
        route = mock_api.get("/service-desk/template-answers").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_sd_template_answers"]["handler"](
            client, {}
        )
        assert route.called
        assert result == []


class TestGetSdTemplateAnswer:
    async def test_get_sd_template_answer_required_only(self, client, mock_api):
        route = mock_api.get("/service-desk/template-answers/ta-uuid-1").mock(
            return_value=Response(200, json={"id": "ta-uuid-1"})
        )
        result = await TOOLS["kaiten_get_sd_template_answer"]["handler"](
            client, {"template_answer_id": "ta-uuid-1"}
        )
        assert route.called
        assert result == {"id": "ta-uuid-1"}


class TestCreateSdTemplateAnswer:
    async def test_create_sd_template_answer_required_only(self, client, mock_api):
        route = mock_api.post("/service-desk/template-answers").mock(
            return_value=Response(
                200, json={"id": "ta-uuid-1", "name": "Greeting"}
            )
        )
        result = await TOOLS["kaiten_create_sd_template_answer"]["handler"](
            client, {"name": "Greeting", "text": "Hello, how can I help?"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Greeting", "text": "Hello, how can I help?"}
        assert result["name"] == "Greeting"


class TestUpdateSdTemplateAnswer:
    async def test_update_sd_template_answer_required_only(self, client, mock_api):
        route = mock_api.patch("/service-desk/template-answers/ta-uuid-1").mock(
            return_value=Response(200, json={"id": "ta-uuid-1"})
        )
        result = await TOOLS["kaiten_update_sd_template_answer"]["handler"](
            client, {"template_answer_id": "ta-uuid-1"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_sd_template_answer_all_args(self, client, mock_api):
        route = mock_api.patch("/service-desk/template-answers/ta-uuid-1").mock(
            return_value=Response(200, json={"id": "ta-uuid-1"})
        )
        await TOOLS["kaiten_update_sd_template_answer"]["handler"](
            client,
            {
                "template_answer_id": "ta-uuid-1",
                "name": "Updated Greeting",
                "text": "Hi there!",
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Updated Greeting", "text": "Hi there!"}


class TestDeleteSdTemplateAnswer:
    async def test_delete_sd_template_answer_required_only(self, client, mock_api):
        route = mock_api.delete(
            "/service-desk/template-answers/ta-uuid-1"
        ).mock(return_value=Response(204))
        await TOOLS["kaiten_delete_sd_template_answer"]["handler"](
            client, {"template_answer_id": "ta-uuid-1"}
        )
        assert route.called


# ---------------------------------------------------------------------------
# SLA Rules
# ---------------------------------------------------------------------------


class TestCreateSlaRule:
    async def test_create_sla_rule_required_only(self, client, mock_api):
        route = mock_api.post("/service-desk/sla/sla-uuid-1/rules").mock(
            return_value=Response(200, json={"id": "rule-uuid-1"})
        )
        result = await TOOLS["kaiten_create_sla_rule"]["handler"](
            client, {"sla_id": "sla-uuid-1"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}
        assert result["id"] == "rule-uuid-1"

    async def test_create_sla_rule_all_args(self, client, mock_api):
        route = mock_api.post("/service-desk/sla/sla-uuid-1/rules").mock(
            return_value=Response(200, json={"id": "rule-uuid-1"})
        )
        await TOOLS["kaiten_create_sla_rule"]["handler"](
            client,
            {
                "sla_id": "sla-uuid-1",
                "type": "reaction",
                "calendar_id": "cal-1",
                "start_column_uid": "col-start",
                "finish_column_uid": "col-finish",
                "estimated_time": 3600,
                "notification_settings": {"email": True},
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "type": "reaction",
            "calendar_id": "cal-1",
            "start_column_uid": "col-start",
            "finish_column_uid": "col-finish",
            "estimated_time": 3600,
            "notification_settings": {"email": True},
        }


class TestUpdateSlaRule:
    async def test_update_sla_rule_required_only(self, client, mock_api):
        route = mock_api.patch(
            "/service-desk/sla/sla-uuid-1/rules/rule-uuid-1"
        ).mock(return_value=Response(200, json={"id": "rule-uuid-1"}))
        result = await TOOLS["kaiten_update_sla_rule"]["handler"](
            client, {"sla_id": "sla-uuid-1", "rule_id": "rule-uuid-1"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_sla_rule_all_args(self, client, mock_api):
        route = mock_api.patch(
            "/service-desk/sla/sla-uuid-1/rules/rule-uuid-1"
        ).mock(return_value=Response(200, json={"id": "rule-uuid-1"}))
        await TOOLS["kaiten_update_sla_rule"]["handler"](
            client,
            {
                "sla_id": "sla-uuid-1",
                "rule_id": "rule-uuid-1",
                "type": "resolution",
                "calendar_id": "cal-2",
                "start_column_uid": "col-a",
                "finish_column_uid": "col-b",
                "estimated_time": 7200,
                "notification_settings": {"slack": True},
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "type": "resolution",
            "calendar_id": "cal-2",
            "start_column_uid": "col-a",
            "finish_column_uid": "col-b",
            "estimated_time": 7200,
            "notification_settings": {"slack": True},
        }


class TestDeleteSlaRule:
    async def test_delete_sla_rule_required_only(self, client, mock_api):
        route = mock_api.delete(
            "/service-desk/sla/sla-uuid-1/rules/rule-uuid-1"
        ).mock(return_value=Response(204))
        await TOOLS["kaiten_delete_sla_rule"]["handler"](
            client, {"sla_id": "sla-uuid-1", "rule_id": "rule-uuid-1"}
        )
        assert route.called


# ---------------------------------------------------------------------------
# SLA Recalculate
# ---------------------------------------------------------------------------


class TestRecalculateSla:
    async def test_recalculate_sla_required_only(self, client, mock_api):
        route = mock_api.post(
            "/service-desk/sla/sla-uuid-1/recalculate-measurements"
        ).mock(return_value=Response(200, json={"job_id": "job-1"}))
        result = await TOOLS["kaiten_recalculate_sla"]["handler"](
            client, {"sla_id": "sla-uuid-1"}
        )
        assert route.called
        assert result == {"job_id": "job-1"}


# ---------------------------------------------------------------------------
# SD Users
# ---------------------------------------------------------------------------


class TestListSdUsers:
    async def test_list_sd_users_required_only(self, client, mock_api):
        route = mock_api.get("/service-desk/users").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_sd_users"]["handler"](client, {})
        assert route.called
        url = str(route.calls[0].request.url)
        assert "limit=50" in url
        assert result == []

    async def test_list_sd_users_all_args(self, client, mock_api):
        route = mock_api.get("/service-desk/users").mock(
            return_value=Response(200, json=[{"id": 42}])
        )
        await TOOLS["kaiten_list_sd_users"]["handler"](
            client,
            {
                "query": "john",
                "limit": 10,
                "offset": 5,
                "include_paid_users": True,
                "include_all_sd_users": False,
            },
        )
        url = str(route.calls[0].request.url)
        assert "query=john" in url
        assert "limit=10" in url
        assert "offset=5" in url
        assert "include_paid_users=true" in url.lower() or "include_paid_users=True" in url
        assert "include_all_sd_users=false" in url.lower() or "include_all_sd_users=False" in url


class TestUpdateSdUser:
    async def test_update_sd_user_required_only(self, client, mock_api):
        route = mock_api.patch("/service-desk/users/42").mock(
            return_value=Response(200, json={"id": 42})
        )
        result = await TOOLS["kaiten_update_sd_user"]["handler"](
            client, {"user_id": 42}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_sd_user_all_args(self, client, mock_api):
        route = mock_api.patch("/service-desk/users/42").mock(
            return_value=Response(200, json={"id": 42})
        )
        await TOOLS["kaiten_update_sd_user"]["handler"](
            client, {"user_id": 42, "full_name": "John Doe", "lng": "en"}
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"full_name": "John Doe", "lng": "en"}


# ---------------------------------------------------------------------------
# SD Temp Password
# ---------------------------------------------------------------------------


class TestSetSdUserTempPassword:
    async def test_set_sd_user_temp_password_required_only(self, client, mock_api):
        route = mock_api.patch(
            "/service-desk/users/set-temporary-password/42"
        ).mock(return_value=Response(200, json={"password": "tmp123"}))
        result = await TOOLS["kaiten_set_sd_user_temp_password"]["handler"](
            client, {"user_id": 42}
        )
        assert route.called
        assert result["password"] == "tmp123"


# ---------------------------------------------------------------------------
# SD Organization Users
# ---------------------------------------------------------------------------


class TestAddSdOrgUser:
    async def test_add_sd_org_user_required_only(self, client, mock_api):
        route = mock_api.post("/service-desk/organizations/1/users").mock(
            return_value=Response(200, json={"id": 42})
        )
        result = await TOOLS["kaiten_add_sd_org_user"]["handler"](
            client, {"organization_id": 1, "user_id": 42}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"user_id": 42}

    async def test_add_sd_org_user_all_args(self, client, mock_api):
        route = mock_api.post("/service-desk/organizations/1/users").mock(
            return_value=Response(200, json={"id": 42})
        )
        await TOOLS["kaiten_add_sd_org_user"]["handler"](
            client,
            {"organization_id": 1, "user_id": 42, "permissions": 7},
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"user_id": 42, "permissions": 7}


class TestUpdateSdOrgUser:
    async def test_update_sd_org_user_required_only(self, client, mock_api):
        route = mock_api.patch(
            "/service-desk/organizations/1/users/42"
        ).mock(return_value=Response(200, json={"id": 42}))
        result = await TOOLS["kaiten_update_sd_org_user"]["handler"](
            client, {"organization_id": 1, "user_id": 42}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_sd_org_user_all_args(self, client, mock_api):
        route = mock_api.patch(
            "/service-desk/organizations/1/users/42"
        ).mock(return_value=Response(200, json={"id": 42}))
        await TOOLS["kaiten_update_sd_org_user"]["handler"](
            client,
            {"organization_id": 1, "user_id": 42, "permissions": 15},
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"permissions": 15}


class TestRemoveSdOrgUser:
    async def test_remove_sd_org_user_required_only(self, client, mock_api):
        route = mock_api.delete(
            "/service-desk/organizations/1/users/42"
        ).mock(return_value=Response(204))
        await TOOLS["kaiten_remove_sd_org_user"]["handler"](
            client, {"organization_id": 1, "user_id": 42}
        )
        assert route.called


class TestBatchAddSdOrgUsers:
    async def test_batch_add_sd_org_users_required_only(self, client, mock_api):
        route = mock_api.patch("/service-desk/organizations/1/users").mock(
            return_value=Response(200, json={"added": 3})
        )
        result = await TOOLS["kaiten_batch_add_sd_org_users"]["handler"](
            client, {"organization_id": 1, "user_ids": [1, 2, 3]}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"user_ids": [1, 2, 3]}


class TestBatchRemoveSdOrgUsers:
    async def test_batch_remove_sd_org_users_required_only(self, client, mock_api):
        route = mock_api.delete("/service-desk/organizations/1/users").mock(
            return_value=Response(200, json={"removed": 2})
        )
        result = await TOOLS["kaiten_batch_remove_sd_org_users"]["handler"](
            client, {"organization_id": 1, "user_ids": [1, 2]}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"user_ids": [1, 2]}


# ---------------------------------------------------------------------------
# SD Settings
# ---------------------------------------------------------------------------


class TestGetSdSettings:
    async def test_get_sd_settings_required_only(self, client, mock_api):
        route = mock_api.get("/sd-settings/current").mock(
            return_value=Response(200, json={"auto_close": True})
        )
        result = await TOOLS["kaiten_get_sd_settings"]["handler"](client, {})
        assert route.called
        assert result == {"auto_close": True}


class TestUpdateSdSettings:
    async def test_update_sd_settings_required_only(self, client, mock_api):
        route = mock_api.patch("/sd-settings/current").mock(
            return_value=Response(200, json={"updated": True})
        )
        result = await TOOLS["kaiten_update_sd_settings"]["handler"](
            client, {"service_desk_settings": {"key": "value"}}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"service_desk_settings": {"key": "value"}}


# ---------------------------------------------------------------------------
# SD Stats
# ---------------------------------------------------------------------------


class TestGetSdStats:
    async def test_get_sd_stats_required_only(self, client, mock_api):
        route = mock_api.get("/service-desk/stats").mock(
            return_value=Response(200, json={"total": 10})
        )
        result = await TOOLS["kaiten_get_sd_stats"]["handler"](client, {})
        assert route.called
        assert result == {"total": 10}

    async def test_get_sd_stats_all_args(self, client, mock_api):
        route = mock_api.get("/service-desk/stats").mock(
            return_value=Response(200, json={"total": 5})
        )
        await TOOLS["kaiten_get_sd_stats"]["handler"](
            client,
            {
                "date_from": "2024-01-01",
                "date_to": "2024-12-31",
                "service_id": 3,
                "report": True,
            },
        )
        url = str(route.calls[0].request.url)
        assert "date-from=2024-01-01" in url
        assert "date-to=2024-12-31" in url
        assert "service_id=3" in url
        assert "report=true" in url.lower() or "report=True" in url


class TestGetSdSlaStats:
    async def test_get_sd_sla_stats_required_only(self, client, mock_api):
        route = mock_api.get("/service-desk/sla-stats").mock(
            return_value=Response(200, json={"compute_job_id": "cj-1"})
        )
        result = await TOOLS["kaiten_get_sd_sla_stats"]["handler"](client, {})
        assert route.called
        assert result == {"compute_job_id": "cj-1"}

    async def test_get_sd_sla_stats_all_args(self, client, mock_api):
        route = mock_api.get("/service-desk/sla-stats").mock(
            return_value=Response(200, json={"compute_job_id": "cj-2"})
        )
        await TOOLS["kaiten_get_sd_sla_stats"]["handler"](
            client,
            {
                "date_from": "2024-01-01",
                "date_to": "2024-06-30",
                "sla_id": "sla-uuid-1",
                "service_id": 5,
                "responsible_id": 10,
                "card_type_ids": [1, 2],
                "tag_ids": [3, 4],
            },
        )
        url = str(route.calls[0].request.url)
        assert "date_from=2024-01-01" in url
        assert "date_to=2024-06-30" in url
        assert "sla_id=sla-uuid-1" in url
        assert "service_id=5" in url
        assert "responsible_id=10" in url


# ---------------------------------------------------------------------------
# Vote Properties
# ---------------------------------------------------------------------------


class TestAddServiceVoteProperty:
    async def test_add_service_vote_property_required_only(self, client, mock_api):
        route = mock_api.post(
            "/service-desk/services/1/vote-properties"
        ).mock(return_value=Response(200, json={"id": 5}))
        result = await TOOLS["kaiten_add_service_vote_property"]["handler"](
            client, {"service_id": 1, "id": 5}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"id": 5}


class TestRemoveServiceVoteProperty:
    async def test_remove_service_vote_property_required_only(self, client, mock_api):
        route = mock_api.delete(
            "/service-desk/services/1/vote-properties/5"
        ).mock(return_value=Response(204))
        await TOOLS["kaiten_remove_service_vote_property"]["handler"](
            client, {"service_id": 1, "property_id": 5}
        )
        assert route.called


# ---------------------------------------------------------------------------
# Card SLAs
# ---------------------------------------------------------------------------


class TestAttachCardSla:
    async def test_attach_card_sla_required_only(self, client, mock_api):
        route = mock_api.post("/cards/100/slas").mock(
            return_value=Response(200, json={"sla_id": "sla-uuid-1"})
        )
        result = await TOOLS["kaiten_attach_card_sla"]["handler"](
            client, {"card_id": 100, "sla_id": "sla-uuid-1"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"sla_id": "sla-uuid-1"}


class TestDetachCardSla:
    async def test_detach_card_sla_required_only(self, client, mock_api):
        route = mock_api.delete("/cards/100/slas/sla-uuid-1").mock(
            return_value=Response(204)
        )
        await TOOLS["kaiten_detach_card_sla"]["handler"](
            client, {"card_id": 100, "sla_id": "sla-uuid-1"}
        )
        assert route.called


# ---------------------------------------------------------------------------
# Card/Space SLA Measurements
# ---------------------------------------------------------------------------


class TestGetCardSlaMeasurements:
    async def test_get_card_sla_measurements_required_only(self, client, mock_api):
        route = mock_api.get("/cards/100/sla-rules-measurements").mock(
            return_value=Response(200, json=[{"rule_id": "r1"}])
        )
        result = await TOOLS["kaiten_get_card_sla_measurements"]["handler"](
            client, {"card_id": 100}
        )
        assert route.called
        assert result == [{"rule_id": "r1"}]


class TestGetSpaceSlaMeasurements:
    async def test_get_space_sla_measurements_required_only(self, client, mock_api):
        route = mock_api.get("/spaces/1/sla-rules-measurements").mock(
            return_value=Response(200, json=[{"card_id": 100}])
        )
        result = await TOOLS["kaiten_get_space_sla_measurements"]["handler"](
            client, {"space_id": 1}
        )
        assert route.called
        assert result == [{"card_id": 100}]
