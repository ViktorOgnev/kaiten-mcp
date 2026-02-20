"""Tests for compact response utilities."""

from kaiten_mcp.tools.compact import (
    DEFAULT_LIMIT,
    STRIP_FIELDS,
    _is_base64_avatar,
    _simplify_user,
    compact_response,
    select_fields,
)


class TestDefaultLimit:
    """Tests for DEFAULT_LIMIT constant."""

    def test_default_limit_is_50(self):
        """DEFAULT_LIMIT should be 50."""
        assert DEFAULT_LIMIT == 50


class TestIsBase64Avatar:
    """Tests for _is_base64_avatar helper."""

    def test_data_uri_is_base64(self):
        """data: URIs should be detected as base64."""
        assert _is_base64_avatar("data:image/png;base64,iVBORw0KGgo=") is True

    def test_http_url_is_not_base64(self):
        """HTTP URLs should not be detected as base64."""
        assert _is_base64_avatar("https://example.com/avatar.png") is False

    def test_none_is_not_base64(self):
        """None should not be detected as base64."""
        assert _is_base64_avatar(None) is False

    def test_number_is_not_base64(self):
        """Numbers should not be detected as base64."""
        assert _is_base64_avatar(12345) is False


class TestSimplifyUser:
    """Tests for _simplify_user helper."""

    def test_simplify_full_user(self):
        """User with id and full_name should be simplified correctly."""
        user = {
            "id": 123,
            "full_name": "John Doe",
            "email": "john@example.com",
            "avatar_url": "data:image/png;base64,xxx",
        }
        result = _simplify_user(user)
        assert result == {"id": 123, "full_name": "John Doe"}

    def test_simplify_user_with_username(self):
        """User without full_name should use username."""
        user = {
            "id": 456,
            "username": "johndoe",
            "email": "john@example.com",
        }
        result = _simplify_user(user)
        assert result == {"id": 456, "full_name": "johndoe"}

    def test_simplify_user_id_only(self):
        """User with only id should return just id."""
        user = {"id": 789}
        result = _simplify_user(user)
        assert result == {"id": 789}

    def test_non_dict_returns_unchanged(self):
        """Non-dict values should be returned unchanged."""
        assert _simplify_user("not a dict") == "not a dict"
        assert _simplify_user(None) is None


class TestCompactResponse:
    """Tests for compact_response function."""

    def test_compact_false_returns_unchanged(self):
        """compact=False should return data unchanged."""
        data = {
            "id": 1,
            "avatar_url": "data:image/png;base64,xxx",
            "owner": {"id": 2, "full_name": "Owner", "email": "owner@x.com"},
        }
        result = compact_response(data, compact=False)
        assert result == data

    def test_compact_strips_base64_avatar(self):
        """compact=True should strip base64 avatar_url."""
        data = {
            "id": 1,
            "title": "Card",
            "avatar_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg==",
        }
        result = compact_response(data, compact=True)
        assert "avatar_url" not in result
        assert result["id"] == 1
        assert result["title"] == "Card"

    def test_compact_keeps_http_avatar(self):
        """compact=True should keep HTTP avatar URLs."""
        data = {
            "id": 1,
            "avatar_url": "https://example.com/avatar.png",
        }
        result = compact_response(data, compact=True)
        assert result["avatar_url"] == "https://example.com/avatar.png"

    def test_compact_strips_base64_avatar_field(self):
        """compact=True should strip avatar field if it's base64."""
        data = {
            "id": 1,
            "avatar": "data:image/png;base64,xxx",
        }
        result = compact_response(data, compact=True)
        assert "avatar" not in result

    def test_compact_simplifies_owner(self):
        """compact=True should simplify owner object."""
        data = {
            "id": 1,
            "owner": {
                "id": 10,
                "full_name": "John Doe",
                "email": "john@example.com",
                "avatar_url": "data:xxx",
            },
        }
        result = compact_response(data, compact=True)
        assert result["owner"] == {"id": 10, "full_name": "John Doe"}

    def test_compact_simplifies_responsible(self):
        """compact=True should simplify responsible object."""
        data = {
            "id": 1,
            "responsible": {
                "id": 20,
                "full_name": "Jane Doe",
                "email": "jane@example.com",
            },
        }
        result = compact_response(data, compact=True)
        assert result["responsible"] == {"id": 20, "full_name": "Jane Doe"}

    def test_compact_simplifies_members_list(self):
        """compact=True should simplify members list."""
        data = {
            "id": 1,
            "members": [
                {"id": 1, "full_name": "User One", "email": "one@x.com"},
                {"id": 2, "full_name": "User Two", "email": "two@x.com"},
            ],
        }
        result = compact_response(data, compact=True)
        assert result["members"] == [
            {"id": 1, "full_name": "User One"},
            {"id": 2, "full_name": "User Two"},
        ]

    def test_compact_handles_nested_objects(self):
        """compact=True should handle nested objects."""
        data = {
            "id": 1,
            "card": {
                "owner": {
                    "id": 5,
                    "full_name": "Nested Owner",
                    "email": "nested@x.com",
                },
                "avatar_url": "data:xxx",
            },
        }
        result = compact_response(data, compact=True)
        assert result["card"]["owner"] == {"id": 5, "full_name": "Nested Owner"}
        assert "avatar_url" not in result["card"]

    def test_compact_handles_list_of_dicts(self):
        """compact=True should handle lists of dicts."""
        data = [
            {
                "id": 1,
                "avatar_url": "data:xxx",
                "owner": {"id": 10, "full_name": "Owner1", "email": "o1@x.com"},
            },
            {
                "id": 2,
                "avatar_url": "data:yyy",
                "owner": {"id": 20, "full_name": "Owner2", "email": "o2@x.com"},
            },
        ]
        result = compact_response(data, compact=True)
        assert len(result) == 2
        assert "avatar_url" not in result[0]
        assert "avatar_url" not in result[1]
        assert result[0]["owner"] == {"id": 10, "full_name": "Owner1"}
        assert result[1]["owner"] == {"id": 20, "full_name": "Owner2"}

    def test_compact_handles_primitives(self):
        """compact_response should handle primitive types."""
        assert compact_response("string", compact=True) == "string"
        assert compact_response(123, compact=True) == 123
        assert compact_response(None, compact=True) is None

    def test_compact_preserves_other_fields(self):
        """compact=True should preserve non-heavy, non-stripped fields."""
        data = {
            "id": 1,
            "title": "My Card",
            "created_at": "2024-01-01T00:00:00Z",
            "owner": {"id": 10, "full_name": "Owner", "extra": "data"},
        }
        result = compact_response(data, compact=True)
        assert result["id"] == 1
        assert result["title"] == "My Card"
        assert result["created_at"] == "2024-01-01T00:00:00Z"

    def test_compact_handles_nested_lists_in_dict(self):
        """compact=True should handle dicts containing lists with primitives."""
        data = {
            "id": 1,
            "tags": ["urgent", "bug", "priority"],  # List of primitives
            "nested": [
                [1, 2, 3],  # Nested list of primitives
                ["a", "b", "c"],
            ],
        }
        result = compact_response(data, compact=True)
        assert result["id"] == 1
        assert result["tags"] == ["urgent", "bug", "priority"]
        assert result["nested"] == [[1, 2, 3], ["a", "b", "c"]]

    def test_compact_handles_deeply_nested_lists(self):
        """compact=True should handle deeply nested structures."""
        data = {
            "id": 1,
            "items": [
                [
                    {"id": 10, "avatar_url": "data:xxx"},
                    [1, 2, {"nested": "value"}],
                ]
            ],
        }
        result = compact_response(data, compact=True)
        assert result["id"] == 1
        # Should strip avatar from nested dict
        assert result["items"][0][0] == {"id": 10}
        # Should preserve nested list with primitives and dicts
        assert result["items"][0][1] == [1, 2, {"nested": "value"}]

    def test_compact_handles_list_with_mixed_types(self):
        """compact=True should handle lists with mixed types."""
        data = [
            1,
            "string",
            {"id": 1, "avatar_url": "data:xxx"},
            [1, 2, 3],
            None,
        ]
        result = compact_response(data, compact=True)
        assert result[0] == 1
        assert result[1] == "string"
        assert result[2] == {"id": 1}  # avatar stripped
        assert result[3] == [1, 2, 3]
        assert result[4] is None


class TestStripFields:
    """Test STRIP_FIELDS behavior in compact mode."""

    def test_strip_fields_contains_description(self):
        """STRIP_FIELDS should contain 'description'."""
        assert "description" in STRIP_FIELDS

    def test_description_stripped_in_compact_mode(self):
        """compact=True should strip description field."""
        data = {"id": 1, "title": "Test", "description": "Long text..."}
        result = compact_response(data, compact=True)
        assert "description" not in result
        assert result["id"] == 1
        assert result["title"] == "Test"

    def test_description_kept_when_not_compact(self):
        """compact=False should keep description field."""
        data = {"id": 1, "description": "Long text..."}
        result = compact_response(data, compact=False)
        assert result["description"] == "Long text..."

    def test_description_stripped_in_list(self):
        """compact=True should strip description from each item in a list."""
        data = [
            {"id": 1, "description": "Desc 1"},
            {"id": 2, "description": "Desc 2"},
        ]
        result = compact_response(data, compact=True)
        assert len(result) == 2
        assert "description" not in result[0]
        assert "description" not in result[1]

    def test_nested_description_stripped(self):
        """compact=True should strip description from nested objects."""
        data = {"id": 1, "nested": {"description": "Nested desc"}}
        result = compact_response(data, compact=True)
        assert "description" not in result["nested"]


class TestSelectFields:
    """Test select_fields() whitelist filtering."""

    def test_select_fields_from_list(self):
        """select_fields should pick only named keys from list items."""
        data = [
            {"id": 1, "title": "A", "description": "D", "state": 3},
            {"id": 2, "title": "B", "description": "E", "state": 1},
        ]
        result = select_fields(data, "id,title")
        assert result == [{"id": 1, "title": "A"}, {"id": 2, "title": "B"}]

    def test_select_fields_from_dict(self):
        """select_fields should pick only named keys from a single dict."""
        data = {"id": 1, "title": "A", "extra": "X"}
        result = select_fields(data, "id,title")
        assert result == {"id": 1, "title": "A"}

    def test_select_fields_none_returns_original(self):
        """select_fields with None should return data unchanged."""
        data = [{"id": 1, "extra": "X"}]
        result = select_fields(data, None)
        assert result == data

    def test_select_fields_empty_string_returns_original(self):
        """select_fields with empty string should return data unchanged."""
        data = [{"id": 1}]
        result = select_fields(data, "")
        assert result == data

    def test_select_fields_with_spaces(self):
        """select_fields should handle spaces around field names."""
        data = [{"id": 1, "title": "A", "state": 3}]
        result = select_fields(data, "id, title, state")
        assert result == [{"id": 1, "title": "A", "state": 3}]

    def test_select_fields_missing_keys_ignored(self):
        """select_fields should ignore requested keys that are absent."""
        data = [{"id": 1, "title": "A"}]
        result = select_fields(data, "id,title,nonexistent")
        assert result == [{"id": 1, "title": "A"}]

    def test_select_fields_non_dict_items_skipped(self):
        """select_fields should skip non-dict items in a list."""
        data = [{"id": 1}, "not a dict", {"id": 2}]
        result = select_fields(data, "id")
        assert result == [{"id": 1}, {"id": 2}]

    def test_select_fields_primitive_passthrough(self):
        """select_fields should pass through primitive values unchanged."""
        assert select_fields("hello", "id") == "hello"
        assert select_fields(42, "id") == 42
