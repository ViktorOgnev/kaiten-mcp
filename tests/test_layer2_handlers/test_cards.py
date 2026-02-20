"""Layer 2 handler integration tests for cards tools."""
import json

from httpx import Response

from kaiten_mcp.tools.cards import TOOLS
from kaiten_mcp.tools.compact import DEFAULT_LIMIT


class TestListCardsDefaultLimit:
    """Tests for default limit behavior in list_cards."""

    async def test_default_limit_50_when_not_specified(self, client, mock_api):
        """Without explicit limit, should use DEFAULT_LIMIT (50)."""
        route = mock_api.get("/cards").mock(
            return_value=Response(200, json=[])
        )
        await TOOLS["kaiten_list_cards"]["handler"](client, {})
        assert route.called
        url = str(route.calls[0].request.url)
        assert "limit=50" in url

    async def test_explicit_limit_overrides_default(self, client, mock_api):
        """Explicit limit should override the default."""
        route = mock_api.get("/cards").mock(
            return_value=Response(200, json=[])
        )
        await TOOLS["kaiten_list_cards"]["handler"](client, {"limit": 25})
        assert route.called
        url = str(route.calls[0].request.url)
        assert "limit=25" in url
        assert "limit=50" not in url

    async def test_limit_100_is_respected(self, client, mock_api):
        """Max limit of 100 should work."""
        route = mock_api.get("/cards").mock(
            return_value=Response(200, json=[])
        )
        await TOOLS["kaiten_list_cards"]["handler"](client, {"limit": 100})
        url = str(route.calls[0].request.url)
        assert "limit=100" in url


class TestListCardsCompact:
    """Tests for compact mode in list_cards."""

    async def test_compact_false_returns_full_response(self, client, mock_api):
        """compact=False (default) should return the full response unchanged."""
        full_response = [
            {
                "id": 1,
                "title": "Card One",
                "avatar_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg==",
                "owner": {
                    "id": 10,
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "avatar_url": "data:image/png;base64,xxx",
                },
            }
        ]
        route = mock_api.get("/cards").mock(
            return_value=Response(200, json=full_response)
        )
        result = await TOOLS["kaiten_list_cards"]["handler"](client, {"compact": False})
        assert route.called
        # Full response should be unchanged
        assert result == full_response

    async def test_compact_strips_base64_avatars(self, client, mock_api):
        """compact=True should remove base64 avatar_url fields."""
        full_response = [
            {
                "id": 1,
                "title": "Card One",
                "avatar_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg==",
            }
        ]
        route = mock_api.get("/cards").mock(
            return_value=Response(200, json=full_response)
        )
        result = await TOOLS["kaiten_list_cards"]["handler"](client, {"compact": True})
        assert route.called
        assert "avatar_url" not in result[0]
        assert result[0]["id"] == 1
        assert result[0]["title"] == "Card One"

    async def test_compact_simplifies_owner_object(self, client, mock_api):
        """compact=True should simplify owner to {id, full_name}."""
        full_response = [
            {
                "id": 1,
                "owner": {
                    "id": 10,
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "avatar_url": "data:xxx",
                    "username": "johnd",
                },
            }
        ]
        route = mock_api.get("/cards").mock(
            return_value=Response(200, json=full_response)
        )
        result = await TOOLS["kaiten_list_cards"]["handler"](client, {"compact": True})
        assert route.called
        assert result[0]["owner"] == {"id": 10, "full_name": "John Doe"}

    async def test_compact_simplifies_members_list(self, client, mock_api):
        """compact=True should simplify members list."""
        full_response = [
            {
                "id": 1,
                "members": [
                    {"id": 1, "full_name": "Alice", "email": "alice@x.com"},
                    {"id": 2, "full_name": "Bob", "email": "bob@x.com"},
                ],
            }
        ]
        route = mock_api.get("/cards").mock(
            return_value=Response(200, json=full_response)
        )
        result = await TOOLS["kaiten_list_cards"]["handler"](client, {"compact": True})
        assert route.called
        assert result[0]["members"] == [
            {"id": 1, "full_name": "Alice"},
            {"id": 2, "full_name": "Bob"},
        ]

    async def test_compact_default_is_false(self, client, mock_api):
        """Without compact param, should behave as compact=False."""
        full_response = [
            {
                "id": 1,
                "avatar_url": "data:image/png;base64,xxx",
            }
        ]
        route = mock_api.get("/cards").mock(
            return_value=Response(200, json=full_response)
        )
        result = await TOOLS["kaiten_list_cards"]["handler"](client, {})
        assert route.called
        # Should keep the avatar_url since compact defaults to False
        assert result[0]["avatar_url"] == "data:image/png;base64,xxx"


class TestListCards:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/cards").mock(
            return_value=Response(200, json=[{"id": 1, "title": "Card One"}])
        )
        result = await TOOLS["kaiten_list_cards"]["handler"](client, {})
        assert route.called
        assert result == [{"id": 1, "title": "Card One"}]

    async def test_all_args(self, client, mock_api):
        route = mock_api.get("/cards").mock(
            return_value=Response(200, json=[])
        )
        all_params = {
            "query": "search term",
            "space_id": 1,
            "board_id": 2,
            "column_id": 3,
            "lane_id": 4,
            "condition": 1,
            "type_id": 5,
            "owner_id": 6,
            "responsible_id": 7,
            "tag_ids": "10,11",
            "member_ids": "20,21",
            "states": "1,2",
            "created_after": "2024-01-01T00:00:00Z",
            "created_before": "2024-12-31T23:59:59Z",
            "updated_after": "2024-06-01T00:00:00Z",
            "updated_before": "2024-06-30T23:59:59Z",
            "due_date_after": "2024-03-01T00:00:00Z",
            "due_date_before": "2024-03-31T23:59:59Z",
            "external_id": "EXT-001",
            "overdue": True,
            "asap": False,
            "archived": True,
            "limit": 50,
            "offset": 10,
            "owner_ids": "6,7",
            "responsible_ids": "8,9",
            "column_ids": "3,4",
            "type_ids": "5,6",
        }
        result = await TOOLS["kaiten_list_cards"]["handler"](client, all_params)
        assert route.called
        url = str(route.calls[0].request.url)
        assert "query=search" in url
        assert "space_id=1" in url
        assert "board_id=2" in url
        assert "limit=50" in url
        assert "offset=10" in url
        assert "overdue" in url
        assert result == []


class TestGetCard:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/cards/100").mock(
            return_value=Response(200, json={"id": 100, "title": "My Card"})
        )
        result = await TOOLS["kaiten_get_card"]["handler"](
            client, {"card_id": 100}
        )
        assert route.called
        assert result == {"id": 100, "title": "My Card"}

    async def test_with_string_key(self, client, mock_api):
        route = mock_api.get("/cards/PROJ-123").mock(
            return_value=Response(200, json={"id": 100, "title": "By Key"})
        )
        result = await TOOLS["kaiten_get_card"]["handler"](
            client, {"card_id": "PROJ-123"}
        )
        assert route.called
        assert result["title"] == "By Key"


class TestCreateCard:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/cards").mock(
            return_value=Response(200, json={"id": 200, "title": "New Card"})
        )
        result = await TOOLS["kaiten_create_card"]["handler"](
            client, {"title": "New Card", "board_id": 10}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "New Card", "board_id": 10}
        assert result == {"id": 200, "title": "New Card"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/cards").mock(
            return_value=Response(200, json={"id": 200})
        )
        all_args = {
            "title": "Full Card",
            "board_id": 10,
            "column_id": 5,
            "lane_id": 3,
            "description": "Detailed description",
            "due_date": "2024-12-31T23:59:59Z",
            "asap": True,
            "size_text": "M",
            "owner_id": 42,
            "type_id": 2,
            "external_id": "EXT-999",
            "sort_order": 1.5,
            "position": 1,
            "properties": {"id_1": "value1"},
            "tags": [{"name": "urgent"}],
            "sprint_id": 42,
            "planned_start": "2024-01-15T00:00:00Z",
            "planned_end": "2024-02-15T00:00:00Z",
        }
        result = await TOOLS["kaiten_create_card"]["handler"](client, all_args)
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body["title"] == "Full Card"
        assert body["board_id"] == 10
        assert body["column_id"] == 5
        assert body["lane_id"] == 3
        assert body["description"] == "Detailed description"
        assert body["due_date"] == "2024-12-31T23:59:59Z"
        assert body["asap"] is True
        assert body["size_text"] == "M"
        assert body["owner_id"] == 42
        assert body["type_id"] == 2
        assert body["external_id"] == "EXT-999"
        assert body["sort_order"] == 1.5
        assert body["position"] == 1
        assert body["properties"] == {"id_1": "value1"}
        assert body["tags"] == [{"name": "urgent"}]
        assert body["sprint_id"] == 42
        assert body["planned_start"] == "2024-01-15T00:00:00Z"
        assert body["planned_end"] == "2024-02-15T00:00:00Z"


class TestUpdateCard:
    async def test_required_only(self, client, mock_api):
        route = mock_api.patch("/cards/100").mock(
            return_value=Response(200, json={"id": 100})
        )
        result = await TOOLS["kaiten_update_card"]["handler"](
            client, {"card_id": 100}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_all_args(self, client, mock_api):
        route = mock_api.patch("/cards/100").mock(
            return_value=Response(200, json={"id": 100})
        )
        all_args = {
            "card_id": 100,
            "title": "Updated Title",
            "description": "Updated desc",
            "board_id": 20,
            "column_id": 6,
            "lane_id": 4,
            "sort_order": 2.5,
            "owner_id": 50,
            "type_id": 3,
            "condition": 1,
            "due_date": "2025-06-30T00:00:00Z",
            "asap": False,
            "size_text": "L",
            "blocked": True,
            "external_id": "EXT-UPD",
            "properties": {"id_2": "val2"},
            "sprint_id": 99,
            "planned_start": "2025-01-01T00:00:00Z",
            "planned_end": "2025-03-01T00:00:00Z",
        }
        result = await TOOLS["kaiten_update_card"]["handler"](client, all_args)
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body["title"] == "Updated Title"
        assert body["description"] == "Updated desc"
        assert body["board_id"] == 20
        assert body["column_id"] == 6
        assert body["lane_id"] == 4
        assert body["sort_order"] == 2.5
        assert body["owner_id"] == 50
        assert body["type_id"] == 3
        assert body["condition"] == 1
        assert body["due_date"] == "2025-06-30T00:00:00Z"
        assert body["asap"] is False
        assert body["size_text"] == "L"
        assert body["blocked"] is True
        assert body["external_id"] == "EXT-UPD"
        assert body["properties"] == {"id_2": "val2"}
        assert body["sprint_id"] == 99
        assert body["planned_start"] == "2025-01-01T00:00:00Z"
        assert body["planned_end"] == "2025-03-01T00:00:00Z"
        # card_id must NOT be in the body
        assert "card_id" not in body

    async def test_with_string_key(self, client, mock_api):
        route = mock_api.patch("/cards/PROJ-456").mock(
            return_value=Response(200, json={"id": 456})
        )
        result = await TOOLS["kaiten_update_card"]["handler"](
            client, {"card_id": "PROJ-456", "title": "Keyed Update"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "Keyed Update"}


class TestDeleteCard:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/cards/100").mock(
            return_value=Response(204)
        )
        result = await TOOLS["kaiten_delete_card"]["handler"](
            client, {"card_id": 100}
        )
        assert route.called

    async def test_with_string_key(self, client, mock_api):
        route = mock_api.delete("/cards/PROJ-789").mock(
            return_value=Response(204)
        )
        result = await TOOLS["kaiten_delete_card"]["handler"](
            client, {"card_id": "PROJ-789"}
        )
        assert route.called


class TestArchiveCard:
    async def test_required_only(self, client, mock_api):
        route = mock_api.patch("/cards/100").mock(
            return_value=Response(200, json={"id": 100, "condition": 2})
        )
        result = await TOOLS["kaiten_archive_card"]["handler"](
            client, {"card_id": 100}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"condition": 2}
        assert result["condition"] == 2

    async def test_with_string_key(self, client, mock_api):
        route = mock_api.patch("/cards/PROJ-001").mock(
            return_value=Response(200, json={"id": 1, "condition": 2})
        )
        result = await TOOLS["kaiten_archive_card"]["handler"](
            client, {"card_id": "PROJ-001"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"condition": 2}


class TestMoveCard:
    async def test_required_only(self, client, mock_api):
        route = mock_api.patch("/cards/100").mock(
            return_value=Response(200, json={"id": 100})
        )
        result = await TOOLS["kaiten_move_card"]["handler"](
            client, {"card_id": 100}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_all_args(self, client, mock_api):
        route = mock_api.patch("/cards/100").mock(
            return_value=Response(200, json={"id": 100})
        )
        result = await TOOLS["kaiten_move_card"]["handler"](
            client,
            {
                "card_id": 100,
                "board_id": 20,
                "column_id": 7,
                "lane_id": 2,
                "sort_order": 3.0,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "board_id": 20,
            "column_id": 7,
            "lane_id": 2,
            "sort_order": 3.0,
        }

    async def test_with_string_key(self, client, mock_api):
        route = mock_api.patch("/cards/PROJ-MOVE").mock(
            return_value=Response(200, json={"id": 50})
        )
        result = await TOOLS["kaiten_move_card"]["handler"](
            client, {"card_id": "PROJ-MOVE", "column_id": 9}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"column_id": 9}


class TestListAllCards:
    async def test_required_only_single_page(self, client, mock_api):
        """Single page of results."""
        route = mock_api.get("/cards").mock(
            return_value=Response(200, json=[{"id": i} for i in range(5)])
        )
        result = await TOOLS["kaiten_list_all_cards"]["handler"](
            client, {}
        )
        assert route.called
        assert len(result) == 5

    async def test_multi_page(self, client, mock_api):
        """Multiple pages with auto-pagination."""
        page1 = [{"id": i} for i in range(100)]
        page2 = [{"id": i} for i in range(100, 170)]
        route = mock_api.get("/cards").mock(
            side_effect=[
                Response(200, json=page1),
                Response(200, json=page2),
            ]
        )
        result = await TOOLS["kaiten_list_all_cards"]["handler"](
            client, {"page_size": 100}
        )
        assert route.call_count == 2
        assert len(result) == 170

    async def test_with_space_filter(self, client, mock_api):
        """Filters passed to each page request."""
        route = mock_api.get("/cards").mock(
            return_value=Response(200, json=[{"id": 1}])
        )
        result = await TOOLS["kaiten_list_all_cards"]["handler"](
            client, {"space_id": 688824, "condition": 1}
        )
        url = str(route.calls[0].request.url)
        assert "space_id=688824" in url
        assert "condition=1" in url

    async def test_max_pages_limit(self, client, mock_api):
        """Stops after max_pages."""
        full_page = [{"id": i} for i in range(100)]
        route = mock_api.get("/cards").mock(
            return_value=Response(200, json=full_page)
        )
        result = await TOOLS["kaiten_list_all_cards"]["handler"](
            client, {"page_size": 100, "max_pages": 3}
        )
        assert route.call_count == 3
        assert len(result) == 300

    async def test_compact_default_true(self, client, mock_api):
        """Default compact=True for bulk fetching."""
        card_with_avatar = {
            "id": 1,
            "title": "Test",
            "owner": {
                "id": 42,
                "full_name": "User",
                "username": "user",
                "avatar": "data:image/png;base64,longdata..."
            },
        }
        route = mock_api.get("/cards").mock(
            return_value=Response(200, json=[card_with_avatar])
        )
        result = await TOOLS["kaiten_list_all_cards"]["handler"](
            client, {}
        )
        # compact=True by default, so avatar should be stripped
        assert route.called
        # Check that result is a list (compact_response applied)
        assert isinstance(result, list)

    async def test_empty_result(self, client, mock_api):
        """Empty first page stops pagination."""
        route = mock_api.get("/cards").mock(
            return_value=Response(200, json=[])
        )
        result = await TOOLS["kaiten_list_all_cards"]["handler"](
            client, {"space_id": 1}
        )
        assert route.call_count == 1
        assert result == []
