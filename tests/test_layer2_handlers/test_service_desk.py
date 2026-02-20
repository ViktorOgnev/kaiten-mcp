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
