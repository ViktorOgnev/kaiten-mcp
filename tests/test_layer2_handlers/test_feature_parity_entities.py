"""Feature-parity handler tests for entity tools sourced from kaiten-cli gaps."""

import json
from urllib.parse import unquote_plus

import respx
from httpx import Response

from kaiten_mcp.tools.card_relations import TOOLS as RELATION_TOOLS
from kaiten_mcp.tools.cards import TOOLS as CARD_TOOLS
from kaiten_mcp.tools.custom_directories import TOOLS as DIRECTORY_TOOLS
from kaiten_mcp.tools.custom_properties import TOOLS as PROPERTY_TOOLS
from kaiten_mcp.tools.documents import TOOLS as DOCUMENT_TOOLS
from kaiten_mcp.tools.roles_and_groups import TOOLS as ROLE_TOOLS
from kaiten_mcp.tools.scim import TOOLS as SCIM_TOOLS
from kaiten_mcp.tools.time_logs import TOOLS as TIME_LOG_TOOLS


class TestBatchCardTools:
    async def test_batch_get_cards_returns_partial_failures(self, client, mock_api):
        mock_api.get("/cards/1").mock(
            return_value=Response(200, json={"id": 1, "title": "A", "description": "heavy"})
        )
        mock_api.get("/cards/2").mock(return_value=Response(404, json={"message": "missing"}))

        result = await CARD_TOOLS["kaiten_batch_get_cards"]["handler"](
            client,
            {"card_ids": [1, 2], "workers": 20, "compact": True, "fields": "id,title"},
        )

        assert result["meta"] == {"requested": 2, "workers": 6}
        assert result["items"] == [{"card_id": 1, "ok": True, "card": {"id": 1, "title": "A"}}]
        assert result["errors"][0]["card_id"] == 2
        assert result["errors"][0]["ok"] is False
        assert "missing" in result["errors"][0]["error"]

    async def test_batch_list_card_children_returns_partial_failures(self, client, mock_api):
        mock_api.get("/cards/1/children").mock(return_value=Response(200, json=[{"id": 10}]))
        mock_api.get("/cards/2/children").mock(
            return_value=Response(404, json={"message": "missing"})
        )

        result = await RELATION_TOOLS["kaiten_batch_list_card_children"]["handler"](
            client,
            {"card_ids": [1, 2], "workers": 0, "fields": "id"},
        )

        assert result["meta"] == {"requested": 2, "workers": 2}
        assert result["items"] == [{"card_id": 1, "ok": True, "children": [{"id": 10}]}]
        assert result["errors"][0]["card_id"] == 2

    async def test_batch_list_time_logs_sends_filters(self, client, mock_api):
        mock_api.get("/cards/1/time-logs").mock(
            return_value=Response(200, json=[{"id": 50, "time_spent": 10}])
        )
        mock_api.get("/cards/2/time-logs").mock(
            return_value=Response(404, json={"message": "missing"})
        )

        result = await TIME_LOG_TOOLS["kaiten_batch_list_time_logs"]["handler"](
            client,
            {
                "card_ids": [1, 2],
                "for_date": "2026-06-01",
                "personal": True,
                "fields": "id",
            },
        )

        assert result["items"] == [{"card_id": 1, "ok": True, "time_logs": [{"id": 50}]}]
        assert result["errors"][0]["card_id"] == 2


class TestRoleAndGroupParityTools:
    async def test_company_users_defaults_to_members_section(self, client, mock_api):
        route = mock_api.get("/company/users").mock(
            return_value=Response(200, json=[{"id": 7, "full_name": "Alice", "email": "a"}])
        )

        result = await ROLE_TOOLS["kaiten_list_company_users"]["handler"](
            client, {"compact": True, "fields": "id,full_name"}
        )

        url = str(route.calls[0].request.url)
        assert "for_members_section=true" in url.lower()
        assert "offset=0" in url
        assert "limit=100" in url
        assert result == [{"id": 7, "full_name": "Alice"}]

    async def test_group_entity_add_merges_payload(self, client, mock_api):
        route = mock_api.post("/company/groups/g1/entities").mock(
            return_value=Response(200, json={"ok": True})
        )

        await ROLE_TOOLS["kaiten_add_group_entity"]["handler"](
            client,
            {
                "group_uid": "g1",
                "entity_uid": "entity-1",
                "role_ids": ["role-1"],
                "payload": {"inherited": False},
            },
        )

        body = json.loads(route.calls[0].request.content)
        assert body == {"entity_uid": "entity-1", "role_ids": ["role-1"], "inherited": False}


class TestCustomPropertyParityTools:
    async def test_create_catalog_value_merges_payload(self, client, mock_api):
        route = mock_api.post("/company/custom-properties/5/catalog-values").mock(
            return_value=Response(200, json={"id": 10})
        )

        await PROPERTY_TOOLS["kaiten_create_catalog_value"]["handler"](
            client,
            {
                "property_id": 5,
                "name": "Alice",
                "value": {"field-1": "Alice"},
                "payload": {"sort_order": 1},
            },
        )

        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Alice", "value": {"field-1": "Alice"}, "sort_order": 1}


class TestCustomDirectoryParityTools:
    async def test_list_records_json_encodes_filters(self, client, mock_api):
        route = mock_api.get("/company/custom-directories/dir-1/records").mock(
            return_value=Response(200, json=[])
        )

        await DIRECTORY_TOOLS["kaiten_list_custom_directory_records"]["handler"](
            client,
            {
                "directory_id": "dir-1",
                "filters": {"field-1": {"eq": "Alice"}},
                "profile": "summary",
            },
        )

        url = unquote_plus(str(route.calls[0].request.url))
        assert 'filters={"field-1": {"eq": "Alice"}}' in url
        assert "profile=summary" in url
        assert "limit=100" in url

    async def test_create_directory_field_merges_payload(self, client, mock_api):
        route = mock_api.post("/company/custom-directories/dir-1/fields").mock(
            return_value=Response(200, json={"id": "field-1"})
        )

        await DIRECTORY_TOOLS["kaiten_create_custom_directory_field"]["handler"](
            client,
            {
                "directory_id": "dir-1",
                "name": "Email",
                "type": "email",
                "payload": {"settings": {"unique": True}},
            },
        )

        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Email", "type": "email", "settings": {"unique": True}}


class TestDocumentAndScimParityTools:
    async def test_get_document_schema(self, client, mock_api):
        route = mock_api.get("/document-schemas/1").mock(
            return_value=Response(200, json={"id": 1})
        )

        result = await DOCUMENT_TOOLS["kaiten_get_document_schema"]["handler"](
            client, {"schema_id": 1}
        )

        assert route.called
        assert result == {"id": 1}

    async def test_scim_list_uses_root_url_and_start_index_alias(self, client):
        with respx.mock(assert_all_called=False) as router:
            route = router.get("https://test-company.kaiten.ru/scim/v2/Users").mock(
                return_value=Response(200, json={"Resources": []})
            )

            result = await SCIM_TOOLS["kaiten_list_scim_users"]["handler"](
                client, {"start_index": 2, "count": 10, "filter": 'userName eq "a"'}
            )

        url = str(route.calls[0].request.url)
        assert "startIndex=2" in url
        assert "count=10" in url
        assert "filter=userName" in url
        assert result == {"Resources": []}

    async def test_scim_create_sends_payload_as_body(self, client):
        with respx.mock(assert_all_called=False) as router:
            route = router.post("https://test-company.kaiten.ru/scim/v2/Users").mock(
                return_value=Response(200, json={"id": "u1"})
            )

            result = await SCIM_TOOLS["kaiten_create_scim_user"]["handler"](
                client, {"payload": {"userName": "alice@example.com"}}
            )

        body = json.loads(route.calls[0].request.content)
        assert body == {"userName": "alice@example.com"}
        assert result == {"id": "u1"}
