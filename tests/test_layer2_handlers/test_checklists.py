"""Layer 2 handler integration tests for tools/checklists.py."""

import json

from httpx import Response

from kaiten_mcp.tools.checklists import TOOLS

# ---------------------------------------------------------------------------
# Checklists
# ---------------------------------------------------------------------------


class TestListChecklists:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/cards/1/checklists").mock(
            return_value=Response(200, json=[{"id": 5, "name": "TODO"}])
        )
        result = await TOOLS["kaiten_list_checklists"]["handler"](client, {"card_id": 1})
        assert route.called
        assert result == [{"id": 5, "name": "TODO"}]


class TestCreateChecklist:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/cards/1/checklists").mock(
            return_value=Response(200, json={"id": 5, "name": "TODO"})
        )
        result = await TOOLS["kaiten_create_checklist"]["handler"](
            client, {"card_id": 1, "name": "TODO"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "TODO"}
        assert result == {"id": 5, "name": "TODO"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/cards/1/checklists").mock(
            return_value=Response(200, json={"id": 5, "name": "TODO", "sort_order": 10})
        )
        result = await TOOLS["kaiten_create_checklist"]["handler"](
            client, {"card_id": 1, "name": "TODO", "sort_order": 10}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "TODO", "sort_order": 10}


class TestUpdateChecklist:
    async def test_required_only(self, client, mock_api):
        route = mock_api.patch("/cards/1/checklists/5").mock(
            return_value=Response(200, json={"id": 5, "name": "TODO"})
        )
        result = await TOOLS["kaiten_update_checklist"]["handler"](
            client, {"card_id": 1, "checklist_id": 5}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_all_args(self, client, mock_api):
        route = mock_api.patch("/cards/1/checklists/5").mock(
            return_value=Response(200, json={"id": 5, "name": "Done", "sort_order": 2})
        )
        result = await TOOLS["kaiten_update_checklist"]["handler"](
            client, {"card_id": 1, "checklist_id": 5, "name": "Done", "sort_order": 2}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"name": "Done", "sort_order": 2}


class TestDeleteChecklist:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/cards/1/checklists/5").mock(return_value=Response(200, json={}))
        result = await TOOLS["kaiten_delete_checklist"]["handler"](
            client, {"card_id": 1, "checklist_id": 5}
        )
        assert route.called
        assert result == {}


# ---------------------------------------------------------------------------
# Checklist Items
# ---------------------------------------------------------------------------


class TestListChecklistItems:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/cards/1/checklists/5/items").mock(
            return_value=Response(200, json=[{"id": 20, "text": "Step 1"}])
        )
        result = await TOOLS["kaiten_list_checklist_items"]["handler"](
            client, {"card_id": 1, "checklist_id": 5}
        )
        assert route.called
        assert result == [{"id": 20, "text": "Step 1"}]


class TestCreateChecklistItem:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/cards/1/checklists/5/items").mock(
            return_value=Response(200, json={"id": 20, "text": "Step 1"})
        )
        result = await TOOLS["kaiten_create_checklist_item"]["handler"](
            client, {"card_id": 1, "checklist_id": 5, "text": "Step 1"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"text": "Step 1"}
        assert result == {"id": 20, "text": "Step 1"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/cards/1/checklists/5/items").mock(
            return_value=Response(200, json={"id": 20})
        )
        args = {
            "card_id": 1,
            "checklist_id": 5,
            "text": "Step 1",
            "checked": True,
            "sort_order": 3,
            "user_id": 42,
            "due_date": "2025-12-31",
        }
        result = await TOOLS["kaiten_create_checklist_item"]["handler"](client, args)
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "text": "Step 1",
            "checked": True,
            "sort_order": 3,
            "user_id": 42,
            "due_date": "2025-12-31",
        }


class TestUpdateChecklistItem:
    async def test_required_only(self, client, mock_api):
        route = mock_api.patch("/cards/1/checklists/5/items/20").mock(
            return_value=Response(200, json={"id": 20})
        )
        result = await TOOLS["kaiten_update_checklist_item"]["handler"](
            client, {"card_id": 1, "checklist_id": 5, "item_id": 20}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {}

    async def test_all_args(self, client, mock_api):
        route = mock_api.patch("/cards/1/checklists/5/items/20").mock(
            return_value=Response(200, json={"id": 20})
        )
        args = {
            "card_id": 1,
            "checklist_id": 5,
            "item_id": 20,
            "text": "Updated step",
            "checked": False,
            "sort_order": 1,
            "user_id": 99,
            "due_date": "2025-06-01",
        }
        result = await TOOLS["kaiten_update_checklist_item"]["handler"](client, args)
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "text": "Updated step",
            "checked": False,
            "sort_order": 1,
            "user_id": 99,
            "due_date": "2025-06-01",
        }


class TestDeleteChecklistItem:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/cards/1/checklists/5/items/20").mock(
            return_value=Response(200, json={})
        )
        result = await TOOLS["kaiten_delete_checklist_item"]["handler"](
            client, {"card_id": 1, "checklist_id": 5, "item_id": 20}
        )
        assert route.called
        assert result == {}
