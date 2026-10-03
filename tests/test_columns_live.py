"""Opt-in real Kaiten checks; each case owns and removes its test board."""

import os
import uuid
from contextlib import asynccontextmanager

import pytest

from kaiten_mcp.client import KaitenClient
from tests.columns_stdio import HOST_KEYS, call_json, column_session

WIP_KINDS = [
    "column",
    pytest.param(
        "subcolumn",
        marks=pytest.mark.xfail(
            strict=True,
            raises=AssertionError,
            reason="Kaiten subcolumn API ignores WIP on POST and rejects WIP-only PATCH; also reproduced without MCP",
        ),
    ),
]


@pytest.fixture
def live_board(record_property):
    if os.environ.get("KAITEN_COLUMNS_E2E") != "1":
        pytest.skip("Set KAITEN_COLUMNS_E2E=1 and KAITEN_COLUMNS_TEST_SPACE_ID to opt in")
    space_id = int(os.environ["KAITEN_COLUMNS_TEST_SPACE_ID"])
    env = {key: os.environ[key] for key in HOST_KEYS if os.environ.get(key)}
    assert env.get("KAITEN_TOKEN") not in (None, "test-token-12345")

    @asynccontextmanager
    async def connect():
        prefix = f"MCP-column-AT-{uuid.uuid4().hex[:12]}"
        async with column_session(env) as session:
            spaces = await call_json(session, "kaiten_list_spaces", {"compact": True})
            assert any(s["id"] == space_id and not s.get("archived") for s in spaces)
            board = await call_json(
                session, "kaiten_create_board", {"space_id": space_id, "title": prefix}
            )
            board_id = board["id"]
            record_property("board_id", board_id)
            record_property("space_id", space_id)
            try:
                yield session, board_id
            finally:
                # The delete-board tool has no force argument. Use the API only for
                # fixture cleanup, asserting ownership before deleting this exact ID.
                client = KaitenClient()
                try:
                    current = await client.get(f"/boards/{board_id}")
                    assert current["title"] == prefix
                    await client.delete(
                        f"/spaces/{space_id}/boards/{board_id}", json={"force": True}
                    )
                    remaining = await client.get(f"/spaces/{space_id}/boards")
                    assert all(b["id"] != board_id for b in remaining), "Cleanup failed"
                    record_property("cleanup_verified", True)
                finally:
                    await client.close()

    return connect


async def create_target(session, board_id, kind, **fields):
    column = await call_json(
        session,
        "kaiten_create_column",
        {
            "board_id": board_id,
            "title": "Column",
            "type": 1,
            **(fields if kind == "column" else {}),
        },
    )
    if kind == "column":
        return {"board_id": board_id, "column_id": column["id"]}
    subcolumn = await call_json(
        session,
        "kaiten_create_subcolumn",
        {"column_id": column["id"], "title": "Subcolumn", **fields},
    )
    return {"column_id": column["id"], "subcolumn_id": subcolumn["id"]}


async def read_target(session, kind, ids):
    if kind == "column":
        items = await call_json(session, "kaiten_list_columns", {"board_id": ids["board_id"]})
    else:
        items = await call_json(session, "kaiten_list_subcolumns", {"column_id": ids["column_id"]})
    return next(item for item in items if item["id"] == ids[kind + "_id"])


@pytest.mark.parametrize("kind", ["column", "subcolumn"])
async def test_live_validation_and_rename(live_board, kind):
    async with live_board() as (session, board_id):
        ids = await create_target(session, board_id, kind)
        current = await read_target(session, kind, ids)
        assert current["title"] == kind.capitalize()
        for fields, error in [
            ({}, "at least one non-null"),
            ({"auto_archive_days": 14}, "Additional properties"),
            ({"title": "MUST NOT CHANGE", "auto_archive_days": 14}, "Additional properties"),
            ({"wip_limit": None}, "not of type"),
        ]:
            result = await session.call_tool("kaiten_update_" + kind, {**ids, **fields})
            assert result.isError
            assert error in " ".join(c.text for c in result.content if c.type == "text")
            assert await read_target(session, kind, ids) == current
        await call_json(session, "kaiten_update_" + kind, {**ids, "title": "Renamed"})
        updated = await read_target(session, kind, ids)
        assert updated["title"] == "Renamed"
        assert updated["wip_limit"] == current["wip_limit"]


@pytest.mark.parametrize("kind", WIP_KINDS)
@pytest.mark.parametrize("wip", [0, 5])
async def test_live_create_wip(live_board, kind, wip):
    async with live_board() as (session, board_id):
        ids = await create_target(session, board_id, kind, wip_limit=wip)
        current = await read_target(session, kind, ids)
    # Assert outside the session so xfail cannot hide a cleanup/transport failure.
    assert current["wip_limit"] == wip


@pytest.mark.parametrize("kind", WIP_KINDS)
async def test_live_update_wip(live_board, kind):
    observations = []
    async with live_board() as (session, board_id):
        ids = await create_target(session, board_id, kind)
        for wip in (5, 0):
            result = await session.call_tool("kaiten_update_" + kind, {**ids, "wip_limit": wip})
            current = await read_target(session, kind, ids)
            observations.append((wip, result.isError, current["wip_limit"], current["title"]))
    assert observations == [(5, False, 5, kind.capitalize()), (0, False, 0, kind.capitalize())]


@pytest.mark.parametrize("initial", [-1, 0])
async def test_live_archive_after_days(live_board, initial):
    async with live_board() as (session, board_id):
        # This fixture owns an empty board: no existing cards can be archived.
        column = await call_json(
            session,
            "kaiten_create_column",
            {"board_id": board_id, "title": "Done", "type": 3, "archive_after_days": initial},
        )
        ids = {"board_id": board_id, "column_id": column["id"]}
        assert (await read_target(session, "column", ids))["archive_after_days"] == initial
        before = await call_json(session, "kaiten_list_columns", {"board_id": board_id})
        for tool, args in [
            ("kaiten_create_column", {"board_id": board_id, "title": "Invalid", "type": 3}),
            ("kaiten_update_column", ids),
        ]:
            result = await session.call_tool(tool, {**args, "archive_after_days": -2})
            assert result.isError
            assert "minimum" in " ".join(c.text for c in result.content if c.type == "text")
            assert (
                await call_json(session, "kaiten_list_columns", {"board_id": board_id}) == before
            )
        for value in (14, 0, -1):
            await call_json(session, "kaiten_update_column", {**ids, "archive_after_days": value})
            current = await read_target(session, "column", ids)
            assert current["archive_after_days"] == value
            assert current["title"] == "Done"
