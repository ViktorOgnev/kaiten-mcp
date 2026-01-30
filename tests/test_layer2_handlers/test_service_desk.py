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
            client, {"query": "IT", "limit": 5, "offset": 0}
        )
        url = str(route.calls[0].request.url)
        assert "query=IT" in url
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
            client, {"query": "Acme", "limit": 10, "offset": 0}
        )
        url = str(route.calls[0].request.url)
        assert "query=Acme" in url
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
