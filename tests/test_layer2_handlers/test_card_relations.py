"""Layer 2 handler integration tests for tools/card_relations.py."""

import json

from httpx import Response

from kaiten_mcp.tools.card_relations import TOOLS

# ---------------------------------------------------------------------------
# Children
# ---------------------------------------------------------------------------


class TestListCardChildren:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/cards/1/children").mock(
            return_value=Response(200, json=[{"id": 10}])
        )
        result = await TOOLS["kaiten_list_card_children"]["handler"](client, {"card_id": 1})
        assert route.called
        assert result == [{"id": 10}]


class TestAddCardChild:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/cards/1/children").mock(
            return_value=Response(200, json={"id": 10})
        )
        result = await TOOLS["kaiten_add_card_child"]["handler"](
            client, {"card_id": 1, "child_card_id": 10}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"card_id": 10}
        assert result == {"id": 10}


class TestRemoveCardChild:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/cards/1/children/10").mock(return_value=Response(200, json={}))
        result = await TOOLS["kaiten_remove_card_child"]["handler"](
            client, {"card_id": 1, "child_id": 10}
        )
        assert route.called
        assert result == {}


# ---------------------------------------------------------------------------
# Parents
# ---------------------------------------------------------------------------


class TestListCardParents:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/cards/5/parents").mock(return_value=Response(200, json=[{"id": 2}]))
        result = await TOOLS["kaiten_list_card_parents"]["handler"](client, {"card_id": 5})
        assert route.called
        assert result == [{"id": 2}]


class TestAddCardParent:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/cards/5/parents").mock(return_value=Response(200, json={"id": 2}))
        result = await TOOLS["kaiten_add_card_parent"]["handler"](
            client, {"card_id": 5, "parent_card_id": 2}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"card_id": 2}
        assert result == {"id": 2}


class TestRemoveCardParent:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/cards/5/parents/2").mock(return_value=Response(200, json={}))
        result = await TOOLS["kaiten_remove_card_parent"]["handler"](
            client, {"card_id": 5, "parent_id": 2}
        )
        assert route.called
        assert result == {}


# ---------------------------------------------------------------------------
# Planned Relations (Successor cards on Timeline/Gantt)
# ---------------------------------------------------------------------------


class TestAddPlannedRelation:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/cards/100/planned-relation").mock(
            return_value=Response(
                200,
                json={
                    "source_id": 100,
                    "target_id": 200,
                    "type": "end-start",
                },
            )
        )
        result = await TOOLS["kaiten_add_planned_relation"]["handler"](
            client, {"card_id": 100, "target_card_id": 200}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"target_card_id": 200, "type": "end-start"}
        assert result["source_id"] == 100
        assert result["target_id"] == 200

    async def test_explicit_type(self, client, mock_api):
        route = mock_api.post("/cards/100/planned-relation").mock(
            return_value=Response(
                200, json={"source_id": 100, "target_id": 200, "type": "end-start"}
            )
        )
        result = await TOOLS["kaiten_add_planned_relation"]["handler"](
            client, {"card_id": 100, "target_card_id": 200, "type": "end-start"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body["type"] == "end-start"


class TestUpdatePlannedRelation:
    async def test_set_gap(self, client, mock_api):
        route = mock_api.patch("/cards/100/planned-relation/200").mock(
            return_value=Response(
                200,
                json={"source_id": 100, "target_id": 200, "gap": 2, "gap_type": "days"},
            )
        )
        result = await TOOLS["kaiten_update_planned_relation"]["handler"](
            client,
            {"card_id": 100, "target_card_id": 200, "gap": 2, "gap_type": "days"},
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"gap": 2, "gap_type": "days"}
        assert result["gap"] == 2

    async def test_clear_gap(self, client, mock_api):
        route = mock_api.patch("/cards/100/planned-relation/200").mock(
            return_value=Response(
                200,
                json={"source_id": 100, "target_id": 200, "gap": None, "gap_type": None},
            )
        )
        result = await TOOLS["kaiten_update_planned_relation"]["handler"](
            client,
            {"card_id": 100, "target_card_id": 200, "gap": None, "gap_type": None},
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"gap": None, "gap_type": None}


class TestRemovePlannedRelation:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/cards/100/planned-relation/200").mock(
            return_value=Response(
                200,
                json={"card_id": 100, "target_card_id": 200},
            )
        )
        result = await TOOLS["kaiten_remove_planned_relation"]["handler"](
            client, {"card_id": 100, "target_card_id": 200}
        )
        assert route.called
        assert result["card_id"] == 100
