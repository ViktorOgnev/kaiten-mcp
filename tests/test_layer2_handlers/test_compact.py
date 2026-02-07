"""Tests for compact response utilities."""
import pytest

from kaiten_mcp.tools.compact import (
    DEFAULT_LIMIT,
    compact_response,
    _is_base64_avatar,
    _simplify_user,
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
        """compact=True should preserve non-heavy fields."""
        data = {
            "id": 1,
            "title": "My Card",
            "description": "Description text",
            "created_at": "2024-01-01T00:00:00Z",
            "owner": {"id": 10, "full_name": "Owner", "extra": "data"},
        }
        result = compact_response(data, compact=True)
        assert result["id"] == 1
        assert result["title"] == "My Card"
        assert result["description"] == "Description text"
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
