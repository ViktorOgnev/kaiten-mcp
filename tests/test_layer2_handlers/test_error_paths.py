"""Layer 2: Error-path and edge-case tests for handlers.

Covers:
- API error propagation through handlers (400, 404, 500)
- Boolean false vs absent (is not None semantics)
- Empty string arguments
- Update card null-pass-through (key in args semantics)
"""
import json

import httpx
import pytest
import respx

from kaiten_mcp.client import KaitenApiError
from kaiten_mcp.tools.cards import TOOLS as CARD_TOOLS
from kaiten_mcp.tools.spaces import TOOLS as SPACE_TOOLS
from kaiten_mcp.tools.comments import TOOLS as COMMENT_TOOLS

BASE_URL = "https://test-company.kaiten.ru/api/latest"


@pytest.fixture
def mock_api():
    with respx.mock(base_url=BASE_URL, assert_all_called=False) as router:
        yield router


@pytest.fixture
async def client():
    from kaiten_mcp.client import KaitenClient
    c = KaitenClient(domain="test-company", token="test-token-12345")
    c._last_request_time = 0.0
    yield c
    if c._client and not c._client.is_closed:
        await c._client.aclose()


# ── API error propagation ──────────────────────────────────────────────────


class TestHandlerErrorPropagation:
    """Errors from the API should propagate as KaitenApiError."""

    async def test_get_card_404(self, client, mock_api):
        mock_api.get("/cards/999").respond(
            404, json={"error": "Card not found"}
        )
        with pytest.raises(KaitenApiError) as exc:
            await CARD_TOOLS["kaiten_get_card"]["handler"](client, {"card_id": 999})
        assert exc.value.status_code == 404
        assert "Card not found" in exc.value.message

    async def test_create_card_400(self, client, mock_api):
        mock_api.post("/cards").respond(
            400, json={"message": "Title is required"}
        )
        with pytest.raises(KaitenApiError) as exc:
            await CARD_TOOLS["kaiten_create_card"]["handler"](
                client, {"title": "", "board_id": 1}
            )
        assert exc.value.status_code == 400
        assert "Title is required" in exc.value.message

    async def test_delete_space_500(self, client, mock_api):
        mock_api.delete("/spaces/1").respond(
            500, json={"message": "Internal Server Error"}
        )
        with pytest.raises(KaitenApiError) as exc:
            await SPACE_TOOLS["kaiten_delete_space"]["handler"](
                client, {"space_id": 1}
            )
        assert exc.value.status_code == 500

    async def test_list_spaces_non_json_error(self, client, mock_api):
        mock_api.get("/spaces").respond(
            502, content=b"Bad Gateway", headers={"content-type": "text/plain"}
        )
        with pytest.raises(KaitenApiError) as exc:
            await SPACE_TOOLS["kaiten_list_spaces"]["handler"](client, {})
        assert exc.value.status_code == 502
        assert "Bad Gateway" in exc.value.message

    async def test_update_space_403(self, client, mock_api):
        mock_api.patch("/spaces/1").respond(
            403, json={"error": "Forbidden"}
        )
        with pytest.raises(KaitenApiError) as exc:
            await SPACE_TOOLS["kaiten_update_space"]["handler"](
                client, {"space_id": 1, "title": "New"}
            )
        assert exc.value.status_code == 403

    async def test_create_comment_422(self, client, mock_api):
        mock_api.post("/cards/1/comments").respond(
            422, json={"message": "Invalid text format"}
        )
        with pytest.raises(KaitenApiError) as exc:
            await COMMENT_TOOLS["kaiten_create_comment"]["handler"](
                client, {"card_id": 1, "text": "hi"}
            )
        assert exc.value.status_code == 422


# ── Boolean false vs absent ────────────────────────────────────────────────


class TestBooleanFalseHandling:
    """Boolean `false` must be included in the body (is not None)."""

    async def test_create_card_asap_false_included(self, client, mock_api):
        route = mock_api.post("/cards").respond(
            json={"id": 1, "asap": False}
        )
        await CARD_TOOLS["kaiten_create_card"]["handler"](
            client, {"title": "T", "board_id": 1, "asap": False}
        )
        body = json.loads(route.calls[0].request.content)
        assert "asap" in body
        assert body["asap"] is False

    async def test_list_cards_overdue_false_included(self, client, mock_api):
        route = mock_api.get("/cards").respond(json=[])
        await CARD_TOOLS["kaiten_list_cards"]["handler"](
            client, {"overdue": False}
        )
        url = str(route.calls[0].request.url)
        assert "overdue=false" in url.lower() or "overdue=False" in url

    async def test_list_spaces_archived_false_included(self, client, mock_api):
        route = mock_api.get("/spaces").respond(json=[])
        await SPACE_TOOLS["kaiten_list_spaces"]["handler"](
            client, {"archived": False}
        )
        url = str(route.calls[0].request.url)
        assert "archived" in url


# ── Empty string handling ──────────────────────────────────────────────────


class TestEmptyStringHandling:
    """Empty strings are not None, so they should be included."""

    async def test_create_space_empty_description(self, client, mock_api):
        route = mock_api.post("/spaces").respond(json={"id": 1, "title": "T"})
        await SPACE_TOOLS["kaiten_create_space"]["handler"](
            client, {"title": "T", "description": ""}
        )
        body = json.loads(route.calls[0].request.content)
        assert body["description"] == ""

    async def test_create_card_empty_description(self, client, mock_api):
        route = mock_api.post("/cards").respond(json={"id": 1})
        await CARD_TOOLS["kaiten_create_card"]["handler"](
            client, {"title": "T", "board_id": 1, "description": ""}
        )
        body = json.loads(route.calls[0].request.content)
        assert body["description"] == ""


# ── Update card: null pass-through (key in args) ──────────────────────────


class TestUpdateCardNullSemantics:
    """Update card uses `key in args` to allow explicit null for clearing fields."""

    async def test_update_card_null_due_date_included(self, client, mock_api):
        route = mock_api.patch("/cards/1").respond(json={"id": 1})
        await CARD_TOOLS["kaiten_update_card"]["handler"](
            client, {"card_id": 1, "due_date": None}
        )
        body = json.loads(route.calls[0].request.content)
        assert "due_date" in body
        assert body["due_date"] is None

    async def test_update_card_null_description_included(self, client, mock_api):
        route = mock_api.patch("/cards/1").respond(json={"id": 1})
        await CARD_TOOLS["kaiten_update_card"]["handler"](
            client, {"card_id": 1, "description": None}
        )
        body = json.loads(route.calls[0].request.content)
        assert "description" in body
        assert body["description"] is None

    async def test_update_card_absent_keys_excluded(self, client, mock_api):
        route = mock_api.patch("/cards/1").respond(json={"id": 1})
        await CARD_TOOLS["kaiten_update_card"]["handler"](
            client, {"card_id": 1, "title": "Updated"}
        )
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "Updated"}
        assert "due_date" not in body
        assert "description" not in body

    async def test_update_card_card_id_excluded_from_body(self, client, mock_api):
        route = mock_api.patch("/cards/1").respond(json={"id": 1})
        await CARD_TOOLS["kaiten_update_card"]["handler"](
            client, {"card_id": 1, "title": "X"}
        )
        body = json.loads(route.calls[0].request.content)
        assert "card_id" not in body


# ── Integer zero handling ──────────────────────────────────────────────────


class TestZeroValueHandling:
    """Integer 0 is not None and should be included."""

    async def test_create_card_sort_order_zero(self, client, mock_api):
        route = mock_api.post("/cards").respond(json={"id": 1})
        await CARD_TOOLS["kaiten_create_card"]["handler"](
            client, {"title": "T", "board_id": 1, "sort_order": 0}
        )
        body = json.loads(route.calls[0].request.content)
        assert body["sort_order"] == 0

    async def test_list_cards_offset_zero(self, client, mock_api):
        route = mock_api.get("/cards").respond(json=[])
        await CARD_TOOLS["kaiten_list_cards"]["handler"](
            client, {"offset": 0}
        )
        url = str(route.calls[0].request.url)
        assert "offset=0" in url
