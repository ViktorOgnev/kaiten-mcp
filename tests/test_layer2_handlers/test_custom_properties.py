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
                "types": "string,number",
                "query": "priority",
                "limit": 20,
                "offset": 0,
            },
        )
        assert route.called
        url = str(route.calls[0].request.url)
        assert "include_values=true" in url.lower() or "include_values=True" in url
        assert "types=string" in url
        assert "query=priority" in url
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
        }


class TestDeleteCustomProperty:
    async def test_delete_custom_property_required_only(self, client, mock_api):
        route = mock_api.delete("/company/custom-properties/5").mock(
            return_value=Response(200, json=None)
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
            client, {"property_id": 3, "query": "high", "limit": 5, "offset": 0}
        )
        assert route.called
        url = str(route.calls[0].request.url)
        assert "query=high" in url
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
