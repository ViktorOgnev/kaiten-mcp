"""Integration tests for documents handler layer."""
import json
import time

import pytest
from httpx import Response

from kaiten_mcp.tools.documents import TOOLS, DEFAULT_LIMIT


# ---------------------------------------------------------------------------
# Default Limit Tests
# ---------------------------------------------------------------------------


class TestDocumentsDefaultLimit:
    """Tests for default limit behavior."""

    async def test_list_documents_default_limit_50(self, client, mock_api):
        """Without explicit limit, should use DEFAULT_LIMIT (50)."""
        route = mock_api.get("/documents").mock(return_value=Response(200, json=[]))
        await TOOLS["kaiten_list_documents"]["handler"](client, {})
        assert route.called
        url = str(route.calls[0].request.url)
        assert "limit=50" in url

    async def test_list_documents_explicit_limit_overrides(self, client, mock_api):
        """Explicit limit should override the default."""
        route = mock_api.get("/documents").mock(return_value=Response(200, json=[]))
        await TOOLS["kaiten_list_documents"]["handler"](client, {"limit": 25})
        url = str(route.calls[0].request.url)
        assert "limit=25" in url
        assert "limit=50" not in url

    async def test_list_document_groups_default_limit_50(self, client, mock_api):
        """Document groups should also use default limit."""
        route = mock_api.get("/document-groups").mock(return_value=Response(200, json=[]))
        await TOOLS["kaiten_list_document_groups"]["handler"](client, {})
        url = str(route.calls[0].request.url)
        assert "limit=50" in url


# ---------------------------------------------------------------------------
# Auto sort_order Tests
# ---------------------------------------------------------------------------


class TestDocumentAutoSortOrder:
    """Tests for auto-generated sort_order."""

    async def test_create_document_auto_sort_order(self, client, mock_api):
        """Without sort_order, should auto-generate based on timestamp."""
        route = mock_api.post("/documents").mock(
            return_value=Response(200, json={"uid": "abc"})
        )
        before = int(time.time())
        await TOOLS["kaiten_create_document"]["handler"](client, {"title": "Doc"})
        after = int(time.time())

        body = json.loads(route.calls[0].request.content)
        assert "sort_order" in body
        # sort_order should be a timestamp
        assert before <= body["sort_order"] <= after

    async def test_create_document_explicit_sort_order(self, client, mock_api):
        """Explicit sort_order should be used as-is."""
        route = mock_api.post("/documents").mock(
            return_value=Response(200, json={"uid": "abc"})
        )
        await TOOLS["kaiten_create_document"]["handler"](
            client, {"title": "Doc", "sort_order": 999}
        )
        body = json.loads(route.calls[0].request.content)
        assert body["sort_order"] == 999

    async def test_create_document_group_auto_sort_order(self, client, mock_api):
        """Document groups should also auto-generate sort_order."""
        route = mock_api.post("/document-groups").mock(
            return_value=Response(200, json={"uid": "g1"})
        )
        before = int(time.time())
        await TOOLS["kaiten_create_document_group"]["handler"](client, {"title": "Grp"})
        after = int(time.time())

        body = json.loads(route.calls[0].request.content)
        assert "sort_order" in body
        assert before <= body["sort_order"] <= after


# ---------------------------------------------------------------------------
# ProseMirror Sanitization Tests
# ---------------------------------------------------------------------------


class TestProseMirrorSanitize:
    """Tests for ProseMirror document sanitization."""

    async def test_bullet_list_converted_to_paragraphs(self, client, mock_api):
        """bullet_list should be converted to paragraphs with bullet char."""
        route = mock_api.patch("/documents/abc-uid").mock(
            return_value=Response(200, json={"uid": "abc-uid"})
        )
        doc_data = {
            "type": "doc",
            "content": [
                {
                    "type": "bullet_list",
                    "content": [
                        {
                            "type": "list_item",
                            "content": [
                                {"type": "paragraph", "content": [{"type": "text", "text": "First item"}]}
                            ]
                        },
                        {
                            "type": "list_item",
                            "content": [
                                {"type": "paragraph", "content": [{"type": "text", "text": "Second item"}]}
                            ]
                        }
                    ]
                }
            ]
        }
        await TOOLS["kaiten_update_document"]["handler"](
            client, {"document_uid": "abc-uid", "data": doc_data}
        )
        body = json.loads(route.calls[0].request.content)
        content = body["data"]["content"]
        # Should be converted to paragraphs
        assert len(content) == 2
        assert content[0]["type"] == "paragraph"
        assert content[0]["content"][0]["text"].startswith("\u2022 ")
        assert "First item" in content[0]["content"][0]["text"]
        assert content[1]["type"] == "paragraph"
        assert content[1]["content"][0]["text"].startswith("\u2022 ")
        assert "Second item" in content[1]["content"][0]["text"]

    async def test_ordered_list_converted_to_numbered_paragraphs(self, client, mock_api):
        """ordered_list should be converted to paragraphs with numbers."""
        route = mock_api.patch("/documents/abc-uid").mock(
            return_value=Response(200, json={"uid": "abc-uid"})
        )
        doc_data = {
            "type": "doc",
            "content": [
                {
                    "type": "ordered_list",
                    "content": [
                        {
                            "type": "list_item",
                            "content": [
                                {"type": "paragraph", "content": [{"type": "text", "text": "First"}]}
                            ]
                        },
                        {
                            "type": "list_item",
                            "content": [
                                {"type": "paragraph", "content": [{"type": "text", "text": "Second"}]}
                            ]
                        },
                        {
                            "type": "list_item",
                            "content": [
                                {"type": "paragraph", "content": [{"type": "text", "text": "Third"}]}
                            ]
                        }
                    ]
                }
            ]
        }
        await TOOLS["kaiten_update_document"]["handler"](
            client, {"document_uid": "abc-uid", "data": doc_data}
        )
        body = json.loads(route.calls[0].request.content)
        content = body["data"]["content"]
        assert len(content) == 3
        assert content[0]["content"][0]["text"] == "1. First"
        assert content[1]["content"][0]["text"] == "2. Second"
        assert content[2]["content"][0]["text"] == "3. Third"

    async def test_safe_nodes_unchanged(self, client, mock_api):
        """Safe nodes (heading, paragraph) should not be modified."""
        route = mock_api.patch("/documents/abc-uid").mock(
            return_value=Response(200, json={"uid": "abc-uid"})
        )
        doc_data = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [{"type": "text", "text": "Title"}]
                },
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Regular text."}]
                }
            ]
        }
        await TOOLS["kaiten_update_document"]["handler"](
            client, {"document_uid": "abc-uid", "data": doc_data}
        )
        body = json.loads(route.calls[0].request.content)
        # Should be unchanged
        assert body["data"] == doc_data

    async def test_nested_lists_sanitized(self, client, mock_api):
        """Nested lists should also be sanitized."""
        route = mock_api.patch("/documents/abc-uid").mock(
            return_value=Response(200, json={"uid": "abc-uid"})
        )
        doc_data = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [{"type": "text", "text": "Header"}]
                },
                {
                    "type": "bullet_list",
                    "content": [
                        {
                            "type": "list_item",
                            "content": [
                                {"type": "paragraph", "content": [{"type": "text", "text": "Item"}]}
                            ]
                        }
                    ]
                }
            ]
        }
        await TOOLS["kaiten_update_document"]["handler"](
            client, {"document_uid": "abc-uid", "data": doc_data}
        )
        body = json.loads(route.calls[0].request.content)
        content = body["data"]["content"]
        # First should be heading (unchanged)
        assert content[0]["type"] == "heading"
        # Second should be converted paragraph
        assert content[1]["type"] == "paragraph"
        assert "\u2022 Item" in content[1]["content"][0]["text"]

    async def test_empty_list_produces_empty_paragraph(self, client, mock_api):
        """Empty list should produce an empty paragraph."""
        route = mock_api.patch("/documents/abc-uid").mock(
            return_value=Response(200, json={"uid": "abc-uid"})
        )
        doc_data = {
            "type": "doc",
            "content": [
                {
                    "type": "bullet_list",
                    "content": []
                }
            ]
        }
        await TOOLS["kaiten_update_document"]["handler"](
            client, {"document_uid": "abc-uid", "data": doc_data}
        )
        body = json.loads(route.calls[0].request.content)
        content = body["data"]["content"]
        # Should have at least one paragraph
        assert len(content) >= 1
        assert content[0]["type"] == "paragraph"


class TestProseMirrorSanitizeEdgeCases:
    """Edge case tests for ProseMirror sanitization functions."""

    async def test_non_dict_data_returned_unchanged(self, client, mock_api):
        """Non-dict data should be returned unchanged."""
        route = mock_api.patch("/documents/abc-uid").mock(
            return_value=Response(200, json={"uid": "abc-uid"})
        )
        # This is an unusual case - sending a string as data
        # The sanitizer should handle it gracefully
        await TOOLS["kaiten_update_document"]["handler"](
            client, {"document_uid": "abc-uid", "data": "not a dict"}
        )
        body = json.loads(route.calls[0].request.content)
        # Non-dict data should be unchanged
        assert body["data"] == "not a dict"


class TestExtractTextFromNode:
    """Unit tests for _extract_text_from_node function."""

    def test_non_dict_returns_empty_string(self):
        """Non-dict input should return empty string."""
        from kaiten_mcp.tools.documents import _extract_text_from_node

        assert _extract_text_from_node("not a dict") == ""
        assert _extract_text_from_node(123) == ""
        assert _extract_text_from_node(None) == ""
        assert _extract_text_from_node([]) == ""

    def test_text_node_returns_text(self):
        """Text node should return its text content."""
        from kaiten_mcp.tools.documents import _extract_text_from_node

        assert _extract_text_from_node({"type": "text", "text": "Hello"}) == "Hello"

    def test_paragraph_extracts_nested_text(self):
        """Paragraph with nested content should extract all text."""
        from kaiten_mcp.tools.documents import _extract_text_from_node

        node = {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Hello "},
                {"type": "text", "text": "World"},
            ]
        }
        assert _extract_text_from_node(node) == "Hello World"


class TestSanitizeProseMirrorUnit:
    """Unit tests for _sanitize_prosemirror function."""

    def test_non_dict_returns_unchanged(self):
        """Non-dict input should be returned unchanged."""
        from kaiten_mcp.tools.documents import _sanitize_prosemirror

        assert _sanitize_prosemirror(None) is None
        assert _sanitize_prosemirror("string") == "string"
        assert _sanitize_prosemirror(123) == 123
        assert _sanitize_prosemirror([1, 2, 3]) == [1, 2, 3]

    def test_dict_without_content_returned_unchanged(self):
        """Dict without content key should be returned unchanged."""
        from kaiten_mcp.tools.documents import _sanitize_prosemirror

        node = {"type": "text", "text": "Hello"}
        assert _sanitize_prosemirror(node) == node


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
        # sort_order is now auto-generated
        assert body["title"] == "Doc"
        assert "sort_order" in body  # auto-generated
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
            client, {"title": "Grp"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        # sort_order is now auto-generated
        assert body["title"] == "Grp"
        assert "sort_order" in body  # auto-generated

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
