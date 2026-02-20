"""Integration tests for tree navigation tools."""

import pytest
from httpx import Response

from kaiten_mcp.tools.tree import TOOLS, _fetch_all_entities, _sort_entities

# ---------------------------------------------------------------------------
# Test data helpers
# ---------------------------------------------------------------------------

SPACE_A = {"id": 1, "uid": "space-a", "title": "Alpha Space", "parent_entity_uid": None}
SPACE_B = {"id": 2, "uid": "space-b", "title": "Beta Space", "parent_entity_uid": "group-1"}
DOC_1 = {"uid": "doc-1", "title": "Design Doc", "parent_entity_uid": None}
DOC_2 = {"uid": "doc-2", "title": "API Spec", "parent_entity_uid": "group-1"}
DOC_3 = {"uid": "doc-3", "title": "Notes", "parent_entity_uid": "space-a"}
GROUP_1 = {"uid": "group-1", "title": "Engineering", "parent_entity_uid": None}
GROUP_2 = {"uid": "group-2", "title": "Archive", "parent_entity_uid": "group-1"}


def _mock_all_routes(mock_api, spaces=None, docs=None, groups=None):
    """Set up mocks for all three API routes."""
    mock_api.get("/spaces").mock(return_value=Response(200, json=spaces or []))
    mock_api.get("/documents").mock(return_value=Response(200, json=docs or []))
    mock_api.get("/document-groups").mock(return_value=Response(200, json=groups or []))


# ---------------------------------------------------------------------------
# _fetch_all_entities
# ---------------------------------------------------------------------------


class TestFetchAllEntities:
    """Unit tests for entity normalization."""

    async def test_normalizes_spaces(self, client, mock_api):
        _mock_all_routes(mock_api, spaces=[SPACE_A])
        entities = await _fetch_all_entities(client)
        assert len(entities) == 1
        assert entities[0] == {
            "type": "space",
            "uid": "space-a",
            "id": 1,
            "title": "Alpha Space",
            "parent_entity_uid": None,
        }

    async def test_normalizes_documents(self, client, mock_api):
        _mock_all_routes(mock_api, docs=[DOC_1])
        entities = await _fetch_all_entities(client)
        assert len(entities) == 1
        assert entities[0]["type"] == "document"
        assert entities[0]["uid"] == "doc-1"
        assert entities[0]["id"] is None

    async def test_normalizes_document_groups(self, client, mock_api):
        _mock_all_routes(mock_api, groups=[GROUP_1])
        entities = await _fetch_all_entities(client)
        assert len(entities) == 1
        assert entities[0]["type"] == "document_group"
        assert entities[0]["uid"] == "group-1"
        assert entities[0]["id"] is None

    async def test_all_entity_types_combined(self, client, mock_api):
        _mock_all_routes(
            mock_api,
            spaces=[SPACE_A],
            docs=[DOC_1],
            groups=[GROUP_1],
        )
        entities = await _fetch_all_entities(client)
        assert len(entities) == 3
        types = {e["type"] for e in entities}
        assert types == {"space", "document", "document_group"}

    async def test_skips_spaces_without_uid(self, client, mock_api):
        _mock_all_routes(mock_api, spaces=[{"id": 99, "title": "No UID"}])
        entities = await _fetch_all_entities(client)
        assert len(entities) == 0

    async def test_handles_non_list_responses(self, client, mock_api):
        """Non-list API responses should be treated as empty."""
        mock_api.get("/spaces").mock(return_value=Response(200, json={"error": "bad"}))
        mock_api.get("/documents").mock(return_value=Response(200, json="not a list"))
        mock_api.get("/document-groups").mock(return_value=Response(200, json=None))
        entities = await _fetch_all_entities(client)
        assert entities == []


# ---------------------------------------------------------------------------
# kaiten_list_children
# ---------------------------------------------------------------------------


class TestListChildren:
    """Tests for kaiten_list_children tool."""

    async def test_root_level_entities(self, client, mock_api):
        """Without parent_entity_uid, returns entities with null parent."""
        _mock_all_routes(
            mock_api,
            spaces=[SPACE_A, SPACE_B],
            docs=[DOC_1, DOC_2],
            groups=[GROUP_1],
        )
        result = await TOOLS["kaiten_list_children"]["handler"](client, {})
        # Root entities: SPACE_A (parent=None), DOC_1 (parent=None), GROUP_1 (parent=None)
        assert len(result) == 3
        uids = [e["uid"] for e in result]
        assert "space-a" in uids
        assert "doc-1" in uids
        assert "group-1" in uids
        # Non-root should be excluded
        assert "space-b" not in uids
        assert "doc-2" not in uids

    async def test_children_of_specific_parent(self, client, mock_api):
        """With parent_entity_uid, returns direct children."""
        _mock_all_routes(
            mock_api,
            spaces=[SPACE_A, SPACE_B],
            docs=[DOC_1, DOC_2],
            groups=[GROUP_1, GROUP_2],
        )
        result = await TOOLS["kaiten_list_children"]["handler"](
            client, {"parent_entity_uid": "group-1"}
        )
        # Children of group-1: SPACE_B, DOC_2, GROUP_2
        assert len(result) == 3
        uids = [e["uid"] for e in result]
        assert "space-b" in uids
        assert "doc-2" in uids
        assert "group-2" in uids

    async def test_empty_result(self, client, mock_api):
        """Parent with no children returns empty list."""
        _mock_all_routes(mock_api, spaces=[SPACE_A])
        result = await TOOLS["kaiten_list_children"]["handler"](
            client, {"parent_entity_uid": "nonexistent"}
        )
        assert result == []

    async def test_mixed_types_as_children(self, client, mock_api):
        """Different entity types can be children of the same parent."""
        _mock_all_routes(
            mock_api,
            spaces=[SPACE_B],
            docs=[DOC_3],
            groups=[GROUP_2],
        )
        # SPACE_B -> parent group-1, DOC_3 -> parent space-a, GROUP_2 -> parent group-1
        result = await TOOLS["kaiten_list_children"]["handler"](
            client, {"parent_entity_uid": "group-1"}
        )
        types = {e["type"] for e in result}
        assert "space" in types
        assert "document_group" in types

    async def test_sorted_by_type_then_title(self, client, mock_api):
        """Results should be sorted by (type, title)."""
        _mock_all_routes(
            mock_api,
            spaces=[SPACE_A],
            docs=[DOC_1],
            groups=[GROUP_1],
        )
        result = await TOOLS["kaiten_list_children"]["handler"](client, {})
        # Order: document_group first, then space, then document
        types = [e["type"] for e in result]
        assert types == ["document_group", "space", "document"]

    async def test_id_omitted_for_non_spaces(self, client, mock_api):
        """Documents and groups should not have 'id' key in output."""
        _mock_all_routes(mock_api, docs=[DOC_1], groups=[GROUP_1])
        result = await TOOLS["kaiten_list_children"]["handler"](client, {})
        for entity in result:
            if entity["type"] != "space":
                assert "id" not in entity

    async def test_id_present_for_spaces(self, client, mock_api):
        """Spaces should include 'id' field."""
        _mock_all_routes(mock_api, spaces=[SPACE_A])
        result = await TOOLS["kaiten_list_children"]["handler"](client, {})
        assert result[0]["id"] == 1


# ---------------------------------------------------------------------------
# kaiten_get_tree
# ---------------------------------------------------------------------------


class TestGetTree:
    """Tests for kaiten_get_tree tool."""

    async def test_full_tree(self, client, mock_api):
        """Full tree from roots builds nested structure."""
        _mock_all_routes(
            mock_api,
            spaces=[SPACE_A, SPACE_B],
            docs=[DOC_1, DOC_2, DOC_3],
            groups=[GROUP_1, GROUP_2],
        )
        result = await TOOLS["kaiten_get_tree"]["handler"](client, {})
        # Root: GROUP_1, SPACE_A, DOC_1 (sorted by type, title)
        assert len(result) == 3
        uids = [n["uid"] for n in result]
        assert "group-1" in uids
        assert "space-a" in uids
        assert "doc-1" in uids

        # GROUP_1 should have children: GROUP_2, SPACE_B, DOC_2
        group_node = next(n for n in result if n["uid"] == "group-1")
        assert len(group_node["children"]) == 3

        # SPACE_A should have child: DOC_3
        space_node = next(n for n in result if n["uid"] == "space-a")
        assert len(space_node["children"]) == 1
        assert space_node["children"][0]["uid"] == "doc-3"

    async def test_subtree_from_root_uid(self, client, mock_api):
        """Starting from specific root_uid returns subtree."""
        _mock_all_routes(
            mock_api,
            spaces=[SPACE_A, SPACE_B],
            docs=[DOC_2, DOC_3],
            groups=[GROUP_1, GROUP_2],
        )
        result = await TOOLS["kaiten_get_tree"]["handler"](client, {"root_uid": "group-1"})
        # Children of group-1: GROUP_2, SPACE_B, DOC_2
        assert len(result) == 3
        uids = [n["uid"] for n in result]
        assert "group-2" in uids
        assert "space-b" in uids
        assert "doc-2" in uids

    async def test_depth_limit(self, client, mock_api):
        """Depth limit prevents deep recursion."""
        _mock_all_routes(
            mock_api,
            spaces=[SPACE_B],
            docs=[DOC_2],
            groups=[GROUP_1, GROUP_2],
        )
        result = await TOOLS["kaiten_get_tree"]["handler"](client, {"depth": 1})
        # Root: GROUP_1. At depth 1, children are listed but not recursed
        group_node = next(n for n in result if n["uid"] == "group-1")
        assert len(group_node["children"]) > 0
        # Children at depth 1 should have empty children arrays
        for child in group_node["children"]:
            assert child["children"] == []

    async def test_unknown_root_uid_raises(self, client, mock_api):
        """Unknown root_uid raises ValueError."""
        _mock_all_routes(mock_api)
        with pytest.raises(ValueError, match="not found"):
            await TOOLS["kaiten_get_tree"]["handler"](client, {"root_uid": "nonexistent"})

    async def test_tree_nodes_have_no_parent_entity_uid(self, client, mock_api):
        """Tree nodes should not include parent_entity_uid (it's implied by nesting)."""
        _mock_all_routes(mock_api, groups=[GROUP_1])
        result = await TOOLS["kaiten_get_tree"]["handler"](client, {})
        assert "parent_entity_uid" not in result[0]


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------


class TestGetTreeEdgeCases:
    """Edge case tests for tree building."""

    async def test_empty_org(self, client, mock_api):
        """Empty org returns empty tree."""
        _mock_all_routes(mock_api)
        result = await TOOLS["kaiten_get_tree"]["handler"](client, {})
        assert result == []

    async def test_depth_limit_prevents_infinite_recursion(self, client, mock_api):
        """Circular references are safely limited by depth."""
        # Simulate circular: A -> B -> A (both point to each other)
        circular_groups = [
            {"uid": "a", "title": "A", "parent_entity_uid": "b"},
            {"uid": "b", "title": "B", "parent_entity_uid": "a"},
        ]
        _mock_all_routes(mock_api, groups=circular_groups)
        # With depth limit, should not infinite loop
        result = await TOOLS["kaiten_get_tree"]["handler"](client, {"depth": 3})
        # Neither is root (both have parents), so result is empty
        assert result == []

    async def test_leaf_nodes_have_empty_children(self, client, mock_api):
        """Leaf nodes should have children: []."""
        _mock_all_routes(mock_api, docs=[DOC_1])
        result = await TOOLS["kaiten_get_tree"]["handler"](client, {})
        assert result[0]["children"] == []

    async def test_id_present_for_spaces_in_tree(self, client, mock_api):
        """Spaces in tree should include 'id' field."""
        _mock_all_routes(mock_api, spaces=[SPACE_A])
        result = await TOOLS["kaiten_get_tree"]["handler"](client, {})
        assert result[0]["id"] == 1

    async def test_id_omitted_for_non_spaces_in_tree(self, client, mock_api):
        """Documents/groups in tree should not have 'id' key."""
        _mock_all_routes(mock_api, docs=[DOC_1])
        result = await TOOLS["kaiten_get_tree"]["handler"](client, {})
        assert "id" not in result[0]

    async def test_depth_zero_means_unlimited(self, client, mock_api):
        """depth=0 should recurse fully."""
        _mock_all_routes(
            mock_api,
            groups=[GROUP_1, GROUP_2],
            docs=[{"uid": "deep-doc", "title": "Deep", "parent_entity_uid": "group-2"}],
        )
        result = await TOOLS["kaiten_get_tree"]["handler"](client, {"depth": 0})
        # GROUP_1 -> GROUP_2 -> deep-doc
        group1 = result[0]
        assert group1["uid"] == "group-1"
        group2 = group1["children"][0]
        assert group2["uid"] == "group-2"
        deep = group2["children"][0]
        assert deep["uid"] == "deep-doc"


class TestSortEntities:
    """Unit tests for _sort_entities."""

    def test_sorts_by_type_then_title(self):
        entities = [
            {"type": "document", "uid": "d1", "title": "Zebra"},
            {"type": "space", "uid": "s1", "title": "Alpha"},
            {"type": "document_group", "uid": "g1", "title": "Beta"},
            {"type": "document", "uid": "d2", "title": "Alpha"},
        ]
        result = _sort_entities(entities)
        assert [e["uid"] for e in result] == ["g1", "s1", "d2", "d1"]

    def test_empty_list(self):
        assert _sort_entities([]) == []
