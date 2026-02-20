"""Integration tests for roles_and_groups handler layer."""

import json

from httpx import Response

from kaiten_mcp.tools.roles_and_groups import TOOLS

# ---------------------------------------------------------------------------
# Space Users
# ---------------------------------------------------------------------------


class TestListSpaceUsers:
    async def test_list_space_users_required_only(self, client, mock_api):
        route = mock_api.get("/spaces/1/users").mock(return_value=Response(200, json=[]))
        result = await TOOLS["kaiten_list_space_users"]["handler"](client, {"space_id": 1})
        assert route.called
        assert result == []


class TestAddSpaceUser:
    async def test_add_space_user_required_only(self, client, mock_api):
        route = mock_api.post("/spaces/1/users").mock(
            return_value=Response(200, json={"user_id": 42})
        )
        result = await TOOLS["kaiten_add_space_user"]["handler"](
            client, {"space_id": 1, "user_id": 42}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"user_id": 42}

    async def test_add_space_user_all_args(self, client, mock_api):
        route = mock_api.post("/spaces/1/users").mock(
            return_value=Response(200, json={"user_id": 42})
        )
        await TOOLS["kaiten_add_space_user"]["handler"](
            client, {"space_id": 1, "user_id": 42, "role_id": 3}
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"user_id": 42, "role_id": 3}


class TestUpdateSpaceUser:
    async def test_update_space_user_required_only(self, client, mock_api):
        route = mock_api.patch("/spaces/1/users/42").mock(
            return_value=Response(200, json={"user_id": 42})
        )
        result = await TOOLS["kaiten_update_space_user"]["handler"](
            client, {"space_id": 1, "user_id": 42}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_space_user_all_args(self, client, mock_api):
        route = mock_api.patch("/spaces/1/users/42").mock(
            return_value=Response(200, json={"user_id": 42})
        )
        await TOOLS["kaiten_update_space_user"]["handler"](
            client, {"space_id": 1, "user_id": 42, "role_id": 5}
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"role_id": 5}


class TestRemoveSpaceUser:
    async def test_remove_space_user_required_only(self, client, mock_api):
        route = mock_api.delete("/spaces/1/users/42").mock(return_value=Response(204))
        await TOOLS["kaiten_remove_space_user"]["handler"](client, {"space_id": 1, "user_id": 42})
        assert route.called


# ---------------------------------------------------------------------------
# Company Groups
# ---------------------------------------------------------------------------


class TestListCompanyGroups:
    async def test_list_company_groups_required_only(self, client, mock_api):
        route = mock_api.get("/company/groups").mock(return_value=Response(200, json=[]))
        result = await TOOLS["kaiten_list_company_groups"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_company_groups_all_args(self, client, mock_api):
        route = mock_api.get("/company/groups").mock(
            return_value=Response(200, json=[{"uid": "g1"}])
        )
        await TOOLS["kaiten_list_company_groups"]["handler"](
            client, {"query": "eng", "limit": 10, "offset": 0}
        )
        url = str(route.calls[0].request.url)
        assert "query=eng" in url
        assert "limit=10" in url
        assert "offset=0" in url


class TestCreateCompanyGroup:
    async def test_create_company_group_required_only(self, client, mock_api):
        route = mock_api.post("/company/groups").mock(
            return_value=Response(200, json={"uid": "g1", "name": "Engineering"})
        )
        result = await TOOLS["kaiten_create_company_group"]["handler"](
            client, {"name": "Engineering"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Engineering"}

    async def test_create_company_group_all_args(self, client, mock_api):
        """Company group create only accepts 'name' — no other fields."""
        route = mock_api.post("/company/groups").mock(
            return_value=Response(200, json={"uid": "g1"})
        )
        await TOOLS["kaiten_create_company_group"]["handler"](client, {"name": "Engineering"})
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Engineering"}


class TestGetCompanyGroup:
    async def test_get_company_group_required_only(self, client, mock_api):
        route = mock_api.get("/company/groups/g1").mock(
            return_value=Response(200, json={"uid": "g1"})
        )
        result = await TOOLS["kaiten_get_company_group"]["handler"](client, {"group_uid": "g1"})
        assert route.called
        assert result["uid"] == "g1"


class TestUpdateCompanyGroup:
    async def test_update_company_group_required_only(self, client, mock_api):
        route = mock_api.patch("/company/groups/g1").mock(
            return_value=Response(200, json={"uid": "g1"})
        )
        result = await TOOLS["kaiten_update_company_group"]["handler"](client, {"group_uid": "g1"})
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_company_group_all_args(self, client, mock_api):
        route = mock_api.patch("/company/groups/g1").mock(
            return_value=Response(200, json={"uid": "g1"})
        )
        await TOOLS["kaiten_update_company_group"]["handler"](
            client,
            {"group_uid": "g1", "name": "Platform"},
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Platform"}


class TestDeleteCompanyGroup:
    async def test_delete_company_group_required_only(self, client, mock_api):
        route = mock_api.delete("/company/groups/g1").mock(return_value=Response(204))
        await TOOLS["kaiten_delete_company_group"]["handler"](client, {"group_uid": "g1"})
        assert route.called


class TestListGroupUsers:
    async def test_list_group_users_required_only(self, client, mock_api):
        route = mock_api.get("/groups/g1/users").mock(return_value=Response(200, json=[]))
        result = await TOOLS["kaiten_list_group_users"]["handler"](client, {"group_uid": "g1"})
        assert route.called
        assert result == []


class TestAddGroupUser:
    async def test_add_group_user_required_only(self, client, mock_api):
        route = mock_api.post("/groups/g1/users").mock(
            return_value=Response(200, json={"user_id": 7})
        )
        result = await TOOLS["kaiten_add_group_user"]["handler"](
            client, {"group_uid": "g1", "user_id": 7}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"user_id": 7}


class TestRemoveGroupUser:
    async def test_remove_group_user_required_only(self, client, mock_api):
        route = mock_api.delete("/groups/g1/users/7").mock(return_value=Response(204))
        await TOOLS["kaiten_remove_group_user"]["handler"](
            client, {"group_uid": "g1", "user_id": 7}
        )
        assert route.called


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------


class TestListRoles:
    async def test_list_roles_required_only(self, client, mock_api):
        route = mock_api.get("/tree-entity-roles").mock(return_value=Response(200, json=[]))
        result = await TOOLS["kaiten_list_roles"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_roles_all_args(self, client, mock_api):
        route = mock_api.get("/tree-entity-roles").mock(
            return_value=Response(200, json=[{"id": 1}])
        )
        await TOOLS["kaiten_list_roles"]["handler"](
            client, {"query": "admin", "limit": 5, "offset": 0}
        )
        url = str(route.calls[0].request.url)
        assert "query=admin" in url
        assert "limit=5" in url
        assert "offset=0" in url


class TestGetRole:
    async def test_get_role_required_only(self, client, mock_api):
        route = mock_api.get("/tree-entity-roles/1").mock(
            return_value=Response(200, json={"id": 1, "name": "Admin"})
        )
        result = await TOOLS["kaiten_get_role"]["handler"](client, {"role_id": 1})
        assert route.called
        assert result == {"id": 1, "name": "Admin"}
