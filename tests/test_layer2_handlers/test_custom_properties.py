"""Integration tests for custom_properties handler layer."""
import json

import pytest
from httpx import Response

from kaiten_mcp.tools.custom_properties import TOOLS


class TestListCustomProperties:
    async def test_list_custom_properties_required_only(self, client, mock_api):
        route = mock_api.get("/company/custom-properties").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_custom_properties"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_custom_properties_all_args(self, client, mock_api):
        route = mock_api.get("/company/custom-properties").mock(
            return_value=Response(200, json=[{"id": 1}])
        )
        result = await TOOLS["kaiten_list_custom_properties"]["handler"](
            client,
            {
                "include_values": True,
                "include_author": True,
                "types": "string,number",
                "conditions": "active",
                "query": "priority",
                "order_by": "name",
                "order_direction": "asc",
                "board_id": 42,
                "limit": 20,
                "offset": 0,
            },
        )
        assert route.called
        url = str(route.calls[0].request.url)
        assert "include_values=true" in url.lower() or "include_values=True" in url
        assert "include_author=true" in url.lower() or "include_author=True" in url
        assert "types=string" in url
        assert "conditions=active" in url
        assert "query=priority" in url
        assert "order_by=name" in url
        assert "order_direction=asc" in url
        assert "board_id=42" in url
        assert "limit=20" in url
        assert "offset=0" in url


class TestGetCustomProperty:
    async def test_get_custom_property_required_only(self, client, mock_api):
        route = mock_api.get("/company/custom-properties/5").mock(
            return_value=Response(200, json={"id": 5, "name": "Priority"})
        )
        result = await TOOLS["kaiten_get_custom_property"]["handler"](
            client, {"property_id": 5}
        )
        assert route.called
        assert result == {"id": 5, "name": "Priority"}


class TestCreateCustomProperty:
    async def test_create_custom_property_required_only(self, client, mock_api):
        route = mock_api.post("/company/custom-properties").mock(
            return_value=Response(200, json={"id": 1, "name": "Score", "type": "number"})
        )
        result = await TOOLS["kaiten_create_custom_property"]["handler"](
            client, {"name": "Score", "type": "number"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Score", "type": "number"}
        assert result["name"] == "Score"

    async def test_create_custom_property_all_args(self, client, mock_api):
        route = mock_api.post("/company/custom-properties").mock(
            return_value=Response(200, json={"id": 1})
        )
        await TOOLS["kaiten_create_custom_property"]["handler"](
            client,
            {
                "name": "Status",
                "type": "select",
                "show_on_facade": True,
                "multi_select": True,
                "colorful": False,
                "multiline": False,
                "values_creatable_by_users": True,
                "values_type": "text",
                "vote_variant": "rating",
                "color": 3,
                "data": {"min": 0, "max": 100},
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "name": "Status",
            "type": "select",
            "show_on_facade": True,
            "multi_select": True,
            "colorful": False,
            "multiline": False,
            "values_creatable_by_users": True,
            "values_type": "text",
            "vote_variant": "rating",
            "color": 3,
            "data": {"min": 0, "max": 100},
        }


class TestUpdateCustomProperty:
    async def test_update_custom_property_required_only(self, client, mock_api):
        route = mock_api.patch("/company/custom-properties/5").mock(
            return_value=Response(200, json={"id": 5})
        )
        result = await TOOLS["kaiten_update_custom_property"]["handler"](
            client, {"property_id": 5}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_custom_property_all_args(self, client, mock_api):
        route = mock_api.patch("/company/custom-properties/5").mock(
            return_value=Response(200, json={"id": 5})
        )
        await TOOLS["kaiten_update_custom_property"]["handler"](
            client,
            {
                "property_id": 5,
                "name": "Renamed",
                "condition": "inactive",
                "show_on_facade": False,
                "multi_select": True,
                "colorful": True,
                "multiline": True,
                "values_creatable_by_users": True,
                "is_used_as_progress": True,
                "color": 7,
                "data": {"minLength": 1, "maxLength": 50},
                "fields_settings": {"uid-1": {"name": "Field A", "required": True}},
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "name": "Renamed",
            "condition": "inactive",
            "show_on_facade": False,
            "multi_select": True,
            "colorful": True,
            "multiline": True,
            "values_creatable_by_users": True,
            "is_used_as_progress": True,
            "color": 7,
            "data": {"minLength": 1, "maxLength": 50},
            "fields_settings": {"uid-1": {"name": "Field A", "required": True}},
        }


class TestDeleteCustomProperty:
    async def test_delete_custom_property_required_only(self, client, mock_api):
        route = mock_api.delete("/company/custom-properties/5").mock(
            return_value=Response(204)
        )
        await TOOLS["kaiten_delete_custom_property"]["handler"](
            client, {"property_id": 5}
        )
        assert route.called


class TestListSelectValues:
    async def test_list_select_values_required_only(self, client, mock_api):
        route = mock_api.get("/company/custom-properties/3/select-values").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_select_values"]["handler"](
            client, {"property_id": 3}
        )
        assert route.called
        assert result == []

    async def test_list_select_values_all_args(self, client, mock_api):
        route = mock_api.get("/company/custom-properties/3/select-values").mock(
            return_value=Response(200, json=[{"id": 1}])
        )
        result = await TOOLS["kaiten_list_select_values"]["handler"](
            client,
            {
                "property_id": 3,
                "query": "high",
                "order_by": "sort_order",
                "conditions": "active",
                "v2_select_search": True,
                "limit": 5,
                "offset": 0,
            },
        )
        assert route.called
        url = str(route.calls[0].request.url)
        assert "query=high" in url
        assert "order_by=sort_order" in url
        assert "conditions=active" in url
        assert "v2_select_search=true" in url.lower() or "v2_select_search=True" in url
        assert "limit=5" in url
        assert "offset=0" in url


class TestCreateSelectValue:
    async def test_create_select_value_required_only(self, client, mock_api):
        route = mock_api.post("/company/custom-properties/3/select-values").mock(
            return_value=Response(200, json={"id": 1, "value": "High"})
        )
        result = await TOOLS["kaiten_create_select_value"]["handler"](
            client, {"property_id": 3, "value": "High"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"value": "High"}

    async def test_create_select_value_all_args(self, client, mock_api):
        route = mock_api.post("/company/custom-properties/3/select-values").mock(
            return_value=Response(200, json={"id": 1})
        )
        await TOOLS["kaiten_create_select_value"]["handler"](
            client, {"property_id": 3, "value": "High", "color": 5, "sort_order": 1.0}
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"value": "High", "color": 5, "sort_order": 1.0}


class TestGetSelectValue:
    async def test_get_select_value_required_only(self, client, mock_api):
        route = mock_api.get("/company/custom-properties/3/select-values/10").mock(
            return_value=Response(200, json={"id": 10, "value": "High"})
        )
        result = await TOOLS["kaiten_get_select_value"]["handler"](
            client, {"property_id": 3, "value_id": 10}
        )
        assert route.called
        assert result == {"id": 10, "value": "High"}


class TestUpdateSelectValue:
    async def test_update_select_value_required_only(self, client, mock_api):
        route = mock_api.patch("/company/custom-properties/3/select-values/10").mock(
            return_value=Response(200, json={"id": 10})
        )
        result = await TOOLS["kaiten_update_select_value"]["handler"](
            client, {"property_id": 3, "value_id": 10}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_select_value_all_args(self, client, mock_api):
        route = mock_api.patch("/company/custom-properties/3/select-values/10").mock(
            return_value=Response(200, json={"id": 10})
        )
        await TOOLS["kaiten_update_select_value"]["handler"](
            client,
            {
                "property_id": 3,
                "value_id": 10,
                "value": "Critical",
                "condition": "active",
                "color": 2,
                "sort_order": 3.5,
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "value": "Critical",
            "condition": "active",
            "color": 2,
            "sort_order": 3.5,
        }


class TestDeleteSelectValue:
    async def test_delete_select_value_required_only(self, client, mock_api):
        route = mock_api.patch("/company/custom-properties/3/select-values/10").mock(
            return_value=Response(200, json={"id": 10})
        )
        await TOOLS["kaiten_delete_select_value"]["handler"](
            client, {"property_id": 3, "value_id": 10}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"deleted": True}
