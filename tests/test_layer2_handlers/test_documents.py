"""Integration tests for documents handler layer."""
import json

import pytest
from httpx import Response

from kaiten_mcp.tools.documents import TOOLS


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------


class TestListDocuments:
    async def test_list_documents_required_only(self, client, mock_api):
        route = mock_api.get("/documents").mock(return_value=Response(200, json=[]))
        result = await TOOLS["kaiten_list_documents"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_documents_all_args(self, client, mock_api):
        route = mock_api.get("/documents").mock(
            return_value=Response(200, json=[{"uid": "abc"}])
        )
        result = await TOOLS["kaiten_list_documents"]["handler"](
            client, {"query": "spec", "limit": 10, "offset": 5}
        )
        assert route.called
        url = str(route.calls[0].request.url)
        assert "query=spec" in url
        assert "limit=10" in url
        assert "offset=5" in url


class TestCreateDocument:
    async def test_create_document_required_only(self, client, mock_api):
        route = mock_api.post("/documents").mock(
            return_value=Response(200, json={"uid": "abc", "title": "Doc"})
        )
        result = await TOOLS["kaiten_create_document"]["handler"](
            client, {"title": "Doc"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "Doc"}
        assert result["title"] == "Doc"

    async def test_create_document_all_args(self, client, mock_api):
        route = mock_api.post("/documents").mock(
            return_value=Response(200, json={"uid": "abc"})
        )
        await TOOLS["kaiten_create_document"]["handler"](
            client,
            {
                "title": "Doc",
                "parent_entity_uid": "folder-123",
                "sort_order": 1,
                "key": "doc-key",
            },
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "title": "Doc",
            "parent_entity_uid": "folder-123",
            "sort_order": 1,
            "key": "doc-key",
        }


class TestGetDocument:
    async def test_get_document_required_only(self, client, mock_api):
        route = mock_api.get("/documents/abc-uid").mock(
            return_value=Response(200, json={"uid": "abc-uid", "title": "Doc"})
        )
        result = await TOOLS["kaiten_get_document"]["handler"](
            client, {"document_uid": "abc-uid"}
        )
        assert route.called
        assert result["uid"] == "abc-uid"


class TestUpdateDocument:
    async def test_update_document_required_only(self, client, mock_api):
        route = mock_api.patch("/documents/abc-uid").mock(
            return_value=Response(200, json={"uid": "abc-uid"})
        )
        result = await TOOLS["kaiten_update_document"]["handler"](
            client, {"document_uid": "abc-uid"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_document_all_args(self, client, mock_api):
        route = mock_api.patch("/documents/abc-uid").mock(
            return_value=Response(200, json={"uid": "abc-uid"})
        )
        await TOOLS["kaiten_update_document"]["handler"](
            client,
            {"document_uid": "abc-uid", "title": "New Title", "data": {"type": "doc", "content": []}},
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "New Title", "data": {"type": "doc", "content": []}}


class TestDeleteDocument:
    async def test_delete_document_required_only(self, client, mock_api):
        route = mock_api.delete("/documents/abc-uid").mock(
            return_value=Response(204)
        )
        await TOOLS["kaiten_delete_document"]["handler"](
            client, {"document_uid": "abc-uid"}
        )
        assert route.called


# ---------------------------------------------------------------------------
# Document Groups
# ---------------------------------------------------------------------------


class TestListDocumentGroups:
    async def test_list_document_groups_required_only(self, client, mock_api):
        route = mock_api.get("/document-groups").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_document_groups"]["handler"](client, {})
        assert route.called
        assert result == []

    async def test_list_document_groups_all_args(self, client, mock_api):
        route = mock_api.get("/document-groups").mock(
            return_value=Response(200, json=[{"uid": "g1"}])
        )
        await TOOLS["kaiten_list_document_groups"]["handler"](
            client, {"query": "eng", "limit": 10, "offset": 0}
        )
        url = str(route.calls[0].request.url)
        assert "query=eng" in url
        assert "limit=10" in url
        assert "offset=0" in url


class TestCreateDocumentGroup:
    async def test_create_document_group_required_only(self, client, mock_api):
        route = mock_api.post("/document-groups").mock(
            return_value=Response(200, json={"uid": "g1", "title": "Grp"})
        )
        result = await TOOLS["kaiten_create_document_group"]["handler"](
            client, {"title": "Grp", "sort_order": 1}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "Grp", "sort_order": 1}

    async def test_create_document_group_all_args(self, client, mock_api):
        route = mock_api.post("/document-groups").mock(
            return_value=Response(200, json={"uid": "g1"})
        )
        await TOOLS["kaiten_create_document_group"]["handler"](
            client, {"title": "Grp", "parent_entity_uid": "parent-1", "sort_order": 2}
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "Grp", "parent_entity_uid": "parent-1", "sort_order": 2}


class TestGetDocumentGroup:
    async def test_get_document_group_required_only(self, client, mock_api):
        route = mock_api.get("/document-groups/g1").mock(
            return_value=Response(200, json={"uid": "g1"})
        )
        result = await TOOLS["kaiten_get_document_group"]["handler"](
            client, {"group_uid": "g1"}
        )
        assert route.called
        assert result["uid"] == "g1"


class TestUpdateDocumentGroup:
    async def test_update_document_group_required_only(self, client, mock_api):
        route = mock_api.patch("/document-groups/g1").mock(
            return_value=Response(200, json={"uid": "g1"})
        )
        result = await TOOLS["kaiten_update_document_group"]["handler"](
            client, {"group_uid": "g1"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_update_document_group_all_args(self, client, mock_api):
        route = mock_api.patch("/document-groups/g1").mock(
            return_value=Response(200, json={"uid": "g1"})
        )
        await TOOLS["kaiten_update_document_group"]["handler"](
            client, {"group_uid": "g1", "title": "Renamed"}
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "Renamed"}


class TestDeleteDocumentGroup:
    async def test_delete_document_group_required_only(self, client, mock_api):
        route = mock_api.delete("/document-groups/g1").mock(
            return_value=Response(204)
        )
        await TOOLS["kaiten_delete_document_group"]["handler"](
            client, {"group_uid": "g1"}
        )
        assert route.called
