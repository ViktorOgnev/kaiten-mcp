"""Layer 2 handler integration tests for columns tools."""

import json

import pytest
from httpx import Response

from kaiten_mcp.tools.columns import TOOLS


class TestListColumns:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/boards/10/columns").mock(
            return_value=Response(200, json=[{"id": 1, "title": "To Do"}])
        )
        result = await TOOLS["kaiten_list_columns"]["handler"](client, {"board_id": 10})
        assert route.called
        assert result == [{"id": 1, "title": "To Do"}]


class TestCreateColumn:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/boards/10/columns").mock(
            return_value=Response(200, json={"id": 5, "title": "Backlog"})
        )
        result = await TOOLS["kaiten_create_column"]["handler"](
            client, {"board_id": 10, "title": "Backlog", "type": 1}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "Backlog", "type": 1}
        assert result == {"id": 5, "title": "Backlog"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/boards/10/columns").mock(
            return_value=Response(200, json={"id": 5})
        )
        result = await TOOLS["kaiten_create_column"]["handler"](
            client,
            {
                "board_id": 10,
                "title": "In Progress",
                "type": 2,
                "wip_limit": 5,
                "wip_limit_type": 1,
                "col_count": 2,
                "sort_order": 2.0,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "title": "In Progress",
            "type": 2,
            "wip_limit": 5,
            "wip_limit_type": 1,
            "col_count": 2,
            "sort_order": 2.0,
        }


class TestUpdateColumn:
    @pytest.mark.parametrize("fields", [{}, {"wip_limit": None}, {"auto_archive_days": 14}])
    async def test_rejects_empty_patch(self, client, mock_api, fields):
        route = mock_api.patch("/boards/10/columns/5").mock(return_value=Response(200, json={}))
        args = {"board_id": 10, "column_id": 5}
        with pytest.raises(ValueError, match="at least one non-null"):
            await TOOLS["kaiten_update_column"]["handler"](client, {**args, **fields})
        assert not route.called
        assert not mock_api.calls

    async def test_all_args(self, client, mock_api):
        route = mock_api.patch("/boards/10/columns/5").mock(
            return_value=Response(200, json={"id": 5})
        )
        result = await TOOLS["kaiten_update_column"]["handler"](
            client,
            {
                "board_id": 10,
                "column_id": 5,
                "title": "Done",
                "type": 3,
                "wip_limit": 10,
                "wip_limit_type": 2,
                "col_count": 2,
                "sort_order": 3.5,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {
            "title": "Done",
            "type": 3,
            "wip_limit": 10,
            "wip_limit_type": 2,
            "col_count": 2,
            "sort_order": 3.5,
        }


class TestDeleteColumn:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/boards/10/columns/5").mock(return_value=Response(204))
        result = await TOOLS["kaiten_delete_column"]["handler"](
            client, {"board_id": 10, "column_id": 5}
        )
        assert route.called


# ---------------------------------------------------------------------------
# Subcolumns
# ---------------------------------------------------------------------------


class TestListSubcolumns:
    async def test_required_only(self, client, mock_api):
        route = mock_api.get("/columns/10/subcolumns").mock(
            return_value=Response(200, json=[{"id": 20, "title": "In Progress"}])
        )
        result = await TOOLS["kaiten_list_subcolumns"]["handler"](client, {"column_id": 10})
        assert route.called
        assert result == [{"id": 20, "title": "In Progress"}]


class TestCreateSubcolumn:
    async def test_required_only(self, client, mock_api):
        route = mock_api.post("/columns/10/subcolumns").mock(
            return_value=Response(200, json={"id": 20, "title": "Done"})
        )
        result = await TOOLS["kaiten_create_subcolumn"]["handler"](
            client, {"column_id": 10, "title": "Done"}
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "Done"}
        assert result == {"id": 20, "title": "Done"}

    async def test_all_args(self, client, mock_api):
        route = mock_api.post("/columns/10/subcolumns").mock(
            return_value=Response(200, json={"id": 20})
        )
        result = await TOOLS["kaiten_create_subcolumn"]["handler"](
            client,
            {"column_id": 10, "title": "Done", "sort_order": 3, "wip_limit": 5, "col_count": 2},
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "Done", "sort_order": 3, "wip_limit": 5, "col_count": 2}


class TestUpdateSubcolumn:
    @pytest.mark.parametrize("fields", [{}, {"wip_limit": None}, {"auto_archive_days": 14}])
    async def test_rejects_empty_patch(self, client, mock_api, fields):
        route = mock_api.patch("/columns/10/subcolumns/20").mock(
            return_value=Response(200, json={})
        )
        args = {"column_id": 10, "subcolumn_id": 20}
        with pytest.raises(ValueError, match="at least one non-null"):
            await TOOLS["kaiten_update_subcolumn"]["handler"](client, {**args, **fields})
        assert not route.called
        assert not mock_api.calls

    async def test_all_args(self, client, mock_api):
        route = mock_api.patch("/columns/10/subcolumns/20").mock(
            return_value=Response(200, json={"id": 20})
        )
        result = await TOOLS["kaiten_update_subcolumn"]["handler"](
            client,
            {
                "column_id": 10,
                "subcolumn_id": 20,
                "title": "Review",
                "sort_order": 1,
                "wip_limit": 3,
                "col_count": 2,
            },
        )
        assert route.called
        body = json.loads(route.calls[0].request.content)
        assert body == {"title": "Review", "sort_order": 1, "wip_limit": 3, "col_count": 2}


class TestDeleteSubcolumn:
    async def test_required_only(self, client, mock_api):
        route = mock_api.delete("/columns/10/subcolumns/20").mock(
            return_value=Response(200, json={})
        )
        result = await TOOLS["kaiten_delete_subcolumn"]["handler"](
            client, {"column_id": 10, "subcolumn_id": 20}
        )
        assert route.called
        assert result == {}


@pytest.mark.parametrize(
    "tool_name, method, path, identifiers, required_body",
    [
        (
            "kaiten_create_column",
            "POST",
            "/boards/10/columns",
            {"board_id": 10},
            {"title": "Done", "type": 3},
        ),
        (
            "kaiten_update_column",
            "PATCH",
            "/boards/10/columns/5",
            {"board_id": 10, "column_id": 5},
            {},
        ),
        (
            "kaiten_create_subcolumn",
            "POST",
            "/columns/10/subcolumns",
            {"column_id": 10},
            {"title": "Done"},
        ),
        (
            "kaiten_update_subcolumn",
            "PATCH",
            "/columns/10/subcolumns/20",
            {"column_id": 10, "subcolumn_id": 20},
            {},
        ),
    ],
)
async def test_zero_is_forwarded_and_none_is_omitted(
    client, mock_api, tool_name, method, path, identifiers, required_body
):
    route = mock_api.request(method, path).mock(return_value=Response(200, json={"id": 5}))
    args = {**identifiers, **required_body, "wip_limit": 0, "sort_order": None}
    original = args.copy()
    await TOOLS[tool_name]["handler"](client, args)
    assert route.call_count == 1
    assert json.loads(route.calls[0].request.content) == {**required_body, "wip_limit": 0}
    assert args == original
