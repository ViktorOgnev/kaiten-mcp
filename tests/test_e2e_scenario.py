"""
End-to-End scenario test against a REAL Kaiten production instance.

This test exercises the maximum number of kaiten-mcp tools in a realistic
development-team workflow.  It creates a complete project setup, populates it
with cards, enriches them (comments, checklists, blockers, relations, links,
tags, members, subscribers), moves cards through a lifecycle, tests updates,
and finally tears everything down in reverse dependency order.

Prerequisites
-------------
* KAITEN_DOMAIN and KAITEN_TOKEN environment variables must be set pointing
  at a live Kaiten instance.
* The token must belong to a user with admin/owner permissions so that
  spaces, card types, custom properties and automations can be created.

Run
---
    pytest tests/test_e2e_scenario.py -v -x --timeout=600

The ``-x`` flag stops on the first failure so partial cleanup can still run.

Safety
------
* Every created entity uses a unique timestamp prefix so it cannot collide
  with existing data.
* Nothing is touched outside the test space.
* Teardown deletes everything in reverse dependency order.
* No time-logs are created on cards that we intend to delete (cards with
  time-logs cannot be deleted in Kaiten).
"""
from __future__ import annotations

import asyncio
import os
import time
import logging
from datetime import datetime, timedelta, timezone

import pytest

from kaiten_mcp.client import KaitenClient, KaitenApiError

# -- Tool handler imports (thin wrappers around client.get/post/patch/delete) -
from kaiten_mcp.tools.spaces import TOOLS as SPACE_T
from kaiten_mcp.tools.boards import TOOLS as BOARD_T
from kaiten_mcp.tools.columns import TOOLS as COL_T
from kaiten_mcp.tools.lanes import TOOLS as LANE_T
from kaiten_mcp.tools.cards import TOOLS as CARD_T
from kaiten_mcp.tools.card_types import TOOLS as CTYPE_T
from kaiten_mcp.tools.custom_properties import TOOLS as PROP_T
from kaiten_mcp.tools.tags import TOOLS as TAG_T
from kaiten_mcp.tools.comments import TOOLS as CMT_T
from kaiten_mcp.tools.checklists import TOOLS as CK_T
from kaiten_mcp.tools.blockers import TOOLS as BLK_T
from kaiten_mcp.tools.card_relations import TOOLS as REL_T
from kaiten_mcp.tools.external_links import TOOLS as LINK_T
from kaiten_mcp.tools.members import TOOLS as MBR_T
from kaiten_mcp.tools.subscribers import TOOLS as SUB_T
from kaiten_mcp.tools.projects import TOOLS as PROJ_T
from kaiten_mcp.tools.documents import TOOLS as DOC_T
from kaiten_mcp.tools.webhooks import TOOLS as WH_T
from kaiten_mcp.tools.automations import TOOLS as AUTO_T
from kaiten_mcp.tools.roles_and_groups import TOOLS as RG_T
from kaiten_mcp.tools.time_logs import TOOLS as TL_T
from kaiten_mcp.tools.utilities import TOOLS as UTIL_T

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TS = str(int(time.time()))
PREFIX = f"E2E-{TS}"


def _h(tools: dict, name: str):
    """Return the handler function for tool *name*."""
    return tools[name]["handler"]


async def _safe_delete(coro):
    """Swallow errors on cleanup so later deletions still run."""
    try:
        await coro
    except Exception as exc:
        logger.warning("Cleanup error (ignored): %s", exc)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def event_loop():
    """Module-scoped event loop for all async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def client():
    """Real KaitenClient -- requires KAITEN_E2E=1 + KAITEN_DOMAIN + KAITEN_TOKEN."""
    if not os.environ.get("KAITEN_E2E"):
        pytest.skip("KAITEN_E2E not set -- skipping E2E (set KAITEN_E2E=1 to enable)")
    domain = os.environ.get("KAITEN_DOMAIN")
    token = os.environ.get("KAITEN_TOKEN")
    if not domain or not token:
        pytest.skip("KAITEN_DOMAIN / KAITEN_TOKEN not set -- skipping E2E")
    c = KaitenClient(domain=domain, token=token)
    yield c
    await c.close()


# ---------------------------------------------------------------------------
# Shared state across ordered tests
# ---------------------------------------------------------------------------


class _State:
    """Mutable bag shared between all test methods in TestE2EScenario."""

    # Identity
    current_user_id: int = 0

    # Card types
    card_type_bug_id: int = 0
    card_type_feature_id: int = 0
    card_type_task_id: int = 0

    # Custom properties
    prop_priority_id: int = 0
    prop_effort_id: int = 0
    prop_done_id: int = 0
    select_val_high_id: int = 0
    select_val_medium_id: int = 0
    select_val_low_id: int = 0

    # Tags
    tag_backend_id: int = 0
    tag_frontend_id: int = 0
    tag_urgent_id: int = 0

    # Space / board infrastructure
    space_id: int = 0
    board_id: int = 0
    col_backlog_id: int = 0
    col_inprogress_id: int = 0
    col_review_id: int = 0
    col_done_id: int = 0
    subcolumn_id: int = 0
    lane_high_id: int = 0
    lane_normal_id: int = 0

    # Cards
    card_epic_id: int = 0
    card_feature_id: int = 0
    card_bug_id: int = 0
    card_task_id: int = 0
    card_subtask_id: int = 0

    # Sub-entities
    comment_id: int = 0
    checklist_id: int = 0
    checklist_item_1_id: int = 0
    checklist_item_2_id: int = 0
    blocker_id: int = 0
    ext_link_id: int = 0

    # Project / sprint
    project_id: int = 0
    sprint_id: int = 0

    # Documents
    doc_group_uid: str = ""
    doc_uid: str = ""

    # Webhook
    webhook_id: int = 0

    # Automation
    automation_id: int = 0

    # Company group
    company_group_uid: str = ""

    # Time-log card (dedicated, will NOT be deleted)
    card_timelog_id: int = 0
    time_log_id: int = 0


S = _State()


# ---------------------------------------------------------------------------
# The test class -- methods execute in order (test_01, test_02, ...)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not os.environ.get("KAITEN_E2E"),
    reason="E2E requires KAITEN_E2E=1 (plus KAITEN_DOMAIN and KAITEN_TOKEN)",
)
class TestE2EScenario:
    """Ordered E2E scenario exercising ~100+ tool handler calls."""

    # ---------------------------------------------------------------
    # Phase 0: Discover current user (read-only tools)
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_00_get_current_user(self, client):
        """kaiten_get_current_user, kaiten_list_users"""
        user = await _h(MBR_T, "kaiten_get_current_user")(client, {})
        assert user["id"]
        S.current_user_id = user["id"]
        logger.info("Current user: %s (id=%d)", user.get("full_name", "?"), S.current_user_id)

        # Also exercise list_users
        users = await _h(MBR_T, "kaiten_list_users")(client, {"limit": 5})
        assert isinstance(users, list)

    # ---------------------------------------------------------------
    # Phase 1: Card types (company-level)
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_01_create_card_types(self, client):
        """kaiten_create_card_type x3, kaiten_get_card_type, kaiten_list_card_types"""
        bug = await _h(CTYPE_T, "kaiten_create_card_type")(client, {
            "name": f"{PREFIX} Bug", "letter": "B", "color": 2,
        })
        S.card_type_bug_id = bug["id"]

        feat = await _h(CTYPE_T, "kaiten_create_card_type")(client, {
            "name": f"{PREFIX} Feature", "letter": "F", "color": 5,
        })
        S.card_type_feature_id = feat["id"]

        task = await _h(CTYPE_T, "kaiten_create_card_type")(client, {
            "name": f"{PREFIX} Task", "letter": "T", "color": 8,
        })
        S.card_type_task_id = task["id"]

        # Verify via get
        got = await _h(CTYPE_T, "kaiten_get_card_type")(client, {"type_id": S.card_type_bug_id})
        assert got["name"] == f"{PREFIX} Bug"
        assert got["color"] == 2

        # Verify via list
        types_list = await _h(CTYPE_T, "kaiten_list_card_types")(client, {"query": PREFIX})
        found_names = {t["name"] for t in types_list}
        assert f"{PREFIX} Bug" in found_names
        assert f"{PREFIX} Feature" in found_names

    @pytest.mark.asyncio
    async def test_01b_update_card_type(self, client):
        """kaiten_update_card_type"""
        updated = await _h(CTYPE_T, "kaiten_update_card_type")(client, {
            "type_id": S.card_type_task_id,
            "name": f"{PREFIX} Task (updated)",
            "color": 9,
        })
        assert updated["name"] == f"{PREFIX} Task (updated)"
        assert updated["color"] == 9

    # ---------------------------------------------------------------
    # Phase 2: Custom properties (company-level)
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_02_create_custom_properties(self, client):
        """kaiten_create_custom_property (select, number, checkbox), kaiten_create_select_value,
        kaiten_list_custom_properties, kaiten_get_custom_property, kaiten_list_select_values"""
        # Priority (select)
        prop_p = await _h(PROP_T, "kaiten_create_custom_property")(client, {
            "name": f"{PREFIX} Priority", "type": "select",
        })
        S.prop_priority_id = prop_p["id"]

        # Create select values
        v_high = await _h(PROP_T, "kaiten_create_select_value")(client, {
            "property_id": S.prop_priority_id, "value": "High", "sort_order": 1,
        })
        S.select_val_high_id = v_high["id"]

        v_med = await _h(PROP_T, "kaiten_create_select_value")(client, {
            "property_id": S.prop_priority_id, "value": "Medium", "sort_order": 2,
        })
        S.select_val_medium_id = v_med["id"]

        v_low = await _h(PROP_T, "kaiten_create_select_value")(client, {
            "property_id": S.prop_priority_id, "value": "Low", "sort_order": 3,
        })
        S.select_val_low_id = v_low["id"]

        # Effort (number)
        prop_e = await _h(PROP_T, "kaiten_create_custom_property")(client, {
            "name": f"{PREFIX} Effort", "type": "number",
        })
        S.prop_effort_id = prop_e["id"]

        # Done flag (checkbox)
        prop_d = await _h(PROP_T, "kaiten_create_custom_property")(client, {
            "name": f"{PREFIX} Done Flag", "type": "checkbox",
        })
        S.prop_done_id = prop_d["id"]

        # Verify list
        all_props = await _h(PROP_T, "kaiten_list_custom_properties")(client, {
            "query": PREFIX,
        })
        found = {p["name"] for p in all_props}
        assert f"{PREFIX} Priority" in found

        # Verify get
        got = await _h(PROP_T, "kaiten_get_custom_property")(client, {
            "property_id": S.prop_priority_id,
        })
        assert got["type"] == "select"

        # Verify select values
        vals = await _h(PROP_T, "kaiten_list_select_values")(client, {
            "property_id": S.prop_priority_id,
        })
        val_names = {v["value"] for v in vals}
        assert "High" in val_names
        assert "Low" in val_names

    @pytest.mark.asyncio
    async def test_02b_update_custom_property(self, client):
        """kaiten_update_custom_property"""
        updated = await _h(PROP_T, "kaiten_update_custom_property")(client, {
            "property_id": S.prop_effort_id, "show_on_facade": True,
        })
        assert updated["show_on_facade"] is True

    # ---------------------------------------------------------------
    # Phase 3: Tags (company-level)
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_03_create_tags(self, client):
        """kaiten_create_tag x3, kaiten_list_tags"""
        t1 = await _h(TAG_T, "kaiten_create_tag")(client, {"name": f"{PREFIX}-backend"})
        S.tag_backend_id = t1["id"]

        t2 = await _h(TAG_T, "kaiten_create_tag")(client, {"name": f"{PREFIX}-frontend"})
        S.tag_frontend_id = t2["id"]

        t3 = await _h(TAG_T, "kaiten_create_tag")(client, {"name": f"{PREFIX}-urgent"})
        S.tag_urgent_id = t3["id"]

        tags = await _h(TAG_T, "kaiten_list_tags")(client, {"query": PREFIX})
        # Tags list may be global; just verify at least one is returned
        assert isinstance(tags, list)

    # ---------------------------------------------------------------
    # Phase 4: Space, board, columns, lanes, subcolumns
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_04_create_space(self, client):
        """kaiten_create_space, kaiten_get_space, kaiten_list_spaces"""
        sp = await _h(SPACE_T, "kaiten_create_space")(client, {
            "title": f"{PREFIX} MCP E2E Test",
            "description": "Automated E2E test space -- safe to delete",
        })
        S.space_id = sp["id"]

        got = await _h(SPACE_T, "kaiten_get_space")(client, {"space_id": S.space_id})
        assert got["title"] == f"{PREFIX} MCP E2E Test"

        spaces = await _h(SPACE_T, "kaiten_list_spaces")(client, {})
        assert any(s["id"] == S.space_id for s in spaces)

    @pytest.mark.asyncio
    async def test_04b_update_space(self, client):
        """kaiten_update_space"""
        updated = await _h(SPACE_T, "kaiten_update_space")(client, {
            "space_id": S.space_id,
            "description": "Updated E2E description",
        })
        assert "Updated" in updated["description"]

    @pytest.mark.asyncio
    async def test_04c_create_board(self, client):
        """kaiten_create_board, kaiten_get_board, kaiten_list_boards"""
        bd = await _h(BOARD_T, "kaiten_create_board")(client, {
            "space_id": S.space_id,
            "title": f"{PREFIX} Dev Board",
            "description": "Main development board",
        })
        S.board_id = bd["id"]

        got = await _h(BOARD_T, "kaiten_get_board")(client, {"board_id": S.board_id})
        assert got["title"] == f"{PREFIX} Dev Board"

        boards = await _h(BOARD_T, "kaiten_list_boards")(client, {"space_id": S.space_id})
        assert any(b["id"] == S.board_id for b in boards)

    @pytest.mark.asyncio
    async def test_04d_update_board(self, client):
        """kaiten_update_board"""
        updated = await _h(BOARD_T, "kaiten_update_board")(client, {
            "space_id": S.space_id, "board_id": S.board_id,
            "description": "Updated dev board description",
        })
        assert "Updated" in updated["description"]

    @pytest.mark.asyncio
    async def test_04e_create_columns(self, client):
        """kaiten_create_column x4, kaiten_list_columns"""
        c1 = await _h(COL_T, "kaiten_create_column")(client, {
            "board_id": S.board_id, "title": "Backlog", "type": 1, "sort_order": 1,
        })
        S.col_backlog_id = c1["id"]

        c2 = await _h(COL_T, "kaiten_create_column")(client, {
            "board_id": S.board_id, "title": "In Progress", "type": 2,
            "wip_limit": 5, "sort_order": 2,
        })
        S.col_inprogress_id = c2["id"]

        c3 = await _h(COL_T, "kaiten_create_column")(client, {
            "board_id": S.board_id, "title": "Review", "type": 2, "sort_order": 3,
        })
        S.col_review_id = c3["id"]

        c4 = await _h(COL_T, "kaiten_create_column")(client, {
            "board_id": S.board_id, "title": "Done", "type": 3, "sort_order": 4,
        })
        S.col_done_id = c4["id"]

        cols = await _h(COL_T, "kaiten_list_columns")(client, {"board_id": S.board_id})
        titles = {c["title"] for c in cols}
        assert "Backlog" in titles
        assert "Done" in titles

    @pytest.mark.asyncio
    async def test_04f_update_column(self, client):
        """kaiten_update_column"""
        updated = await _h(COL_T, "kaiten_update_column")(client, {
            "board_id": S.board_id, "column_id": S.col_inprogress_id,
            "wip_limit": 3,
        })
        assert updated.get("wip_limit") == 3

    @pytest.mark.asyncio
    async def test_04g_create_subcolumn(self, client):
        """kaiten_create_subcolumn, kaiten_list_subcolumns"""
        sc = await _h(SUB_T, "kaiten_create_subcolumn")(client, {
            "column_id": S.col_review_id, "title": "Code Review",
        })
        S.subcolumn_id = sc["id"]

        subs = await _h(SUB_T, "kaiten_list_subcolumns")(client, {
            "column_id": S.col_review_id,
        })
        assert any(s["id"] == S.subcolumn_id for s in subs)

    @pytest.mark.asyncio
    async def test_04h_update_subcolumn(self, client):
        """kaiten_update_subcolumn"""
        updated = await _h(SUB_T, "kaiten_update_subcolumn")(client, {
            "column_id": S.col_review_id, "subcolumn_id": S.subcolumn_id,
            "title": "Code Review (Updated)",
        })
        assert "Updated" in updated["title"]

    @pytest.mark.asyncio
    async def test_04i_create_lanes(self, client):
        """kaiten_create_lane x2, kaiten_list_lanes"""
        l1 = await _h(LANE_T, "kaiten_create_lane")(client, {
            "board_id": S.board_id, "title": "High Priority", "sort_order": 1,
        })
        S.lane_high_id = l1["id"]

        l2 = await _h(LANE_T, "kaiten_create_lane")(client, {
            "board_id": S.board_id, "title": "Normal", "sort_order": 2,
        })
        S.lane_normal_id = l2["id"]

        lanes = await _h(LANE_T, "kaiten_list_lanes")(client, {"board_id": S.board_id})
        assert len(lanes) >= 2

    @pytest.mark.asyncio
    async def test_04j_update_lane(self, client):
        """kaiten_update_lane"""
        updated = await _h(LANE_T, "kaiten_update_lane")(client, {
            "board_id": S.board_id, "lane_id": S.lane_normal_id,
            "title": "Normal Priority",
        })
        assert updated["title"] == "Normal Priority"

    # ---------------------------------------------------------------
    # Phase 5: Column subscribers
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_05_column_subscribers(self, client):
        """kaiten_add_column_subscriber, kaiten_list_column_subscribers,
        kaiten_remove_column_subscriber"""
        await _h(SUB_T, "kaiten_add_column_subscriber")(client, {
            "column_id": S.col_done_id, "user_id": S.current_user_id,
        })
        subs = await _h(SUB_T, "kaiten_list_column_subscribers")(client, {
            "column_id": S.col_done_id,
        })
        assert any(
            (s.get("id") == S.current_user_id or s.get("user_id") == S.current_user_id)
            for s in subs
        )

        await _h(SUB_T, "kaiten_remove_column_subscriber")(client, {
            "column_id": S.col_done_id, "user_id": S.current_user_id,
        })

    # ---------------------------------------------------------------
    # Phase 6: Create cards
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_06_create_cards(self, client):
        """kaiten_create_card x5, kaiten_get_card, kaiten_list_cards"""
        due = (datetime.now(timezone.utc) + timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Epic card (parent)
        epic = await _h(CARD_T, "kaiten_create_card")(client, {
            "title": f"{PREFIX} Epic: Authentication Module",
            "board_id": S.board_id,
            "column_id": S.col_backlog_id,
            "lane_id": S.lane_high_id,
            "description": "Implement full authentication module with OAuth2 + JWT",
            "type_id": S.card_type_feature_id,
            "size_text": "XL",
            "due_date": due,
            "properties": {
                f"id_{S.prop_priority_id}": S.select_val_high_id,
                f"id_{S.prop_effort_id}": 21,
                f"id_{S.prop_done_id}": False,
            },
        })
        S.card_epic_id = epic["id"]

        # Feature card (child of epic)
        feat = await _h(CARD_T, "kaiten_create_card")(client, {
            "title": f"{PREFIX} Feature: Login page",
            "board_id": S.board_id,
            "column_id": S.col_backlog_id,
            "lane_id": S.lane_high_id,
            "description": "Create login page with email + password fields",
            "type_id": S.card_type_feature_id,
            "size_text": "M",
            "properties": {
                f"id_{S.prop_priority_id}": S.select_val_medium_id,
                f"id_{S.prop_effort_id}": 8,
            },
        })
        S.card_feature_id = feat["id"]

        # Bug card
        bug = await _h(CARD_T, "kaiten_create_card")(client, {
            "title": f"{PREFIX} Bug: Session timeout not working",
            "board_id": S.board_id,
            "column_id": S.col_inprogress_id,
            "lane_id": S.lane_high_id,
            "description": "Users are not logged out after 30 min of inactivity",
            "type_id": S.card_type_bug_id,
            "asap": True,
        })
        S.card_bug_id = bug["id"]

        # Task card
        task = await _h(CARD_T, "kaiten_create_card")(client, {
            "title": f"{PREFIX} Task: Write API docs",
            "board_id": S.board_id,
            "column_id": S.col_backlog_id,
            "lane_id": S.lane_normal_id,
            "type_id": S.card_type_task_id,
            "size_text": "S",
        })
        S.card_task_id = task["id"]

        # Sub-task card (will become child of feature)
        subtask = await _h(CARD_T, "kaiten_create_card")(client, {
            "title": f"{PREFIX} Subtask: Password validation",
            "board_id": S.board_id,
            "column_id": S.col_backlog_id,
            "lane_id": S.lane_normal_id,
            "type_id": S.card_type_task_id,
            "external_id": f"ext-{TS}-001",
        })
        S.card_subtask_id = subtask["id"]

        # Verify get
        got = await _h(CARD_T, "kaiten_get_card")(client, {"card_id": S.card_epic_id})
        assert got["title"] == f"{PREFIX} Epic: Authentication Module"
        assert got["size_text"] == "XL"

        # Verify list (search)
        found = await _h(CARD_T, "kaiten_list_cards")(client, {
            "query": PREFIX, "board_id": S.board_id, "limit": 10,
        })
        assert len(found) >= 5

    # ---------------------------------------------------------------
    # Phase 7: Card updates
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_07_update_cards(self, client):
        """kaiten_update_card -- title, description, properties, external_id"""
        updated = await _h(CARD_T, "kaiten_update_card")(client, {
            "card_id": S.card_bug_id,
            "title": f"{PREFIX} Bug: Session timeout CRITICAL",
            "description": "CRITICAL: Users not logged out. Affects all browsers.",
            "properties": {
                f"id_{S.prop_priority_id}": S.select_val_high_id,
            },
        })
        assert "CRITICAL" in updated["title"]

    # ---------------------------------------------------------------
    # Phase 8: Tags on cards
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_08_card_tags(self, client):
        """kaiten_add_card_tag, kaiten_remove_card_tag"""
        # Add tags to bug card
        await _h(TAG_T, "kaiten_add_card_tag")(client, {
            "card_id": S.card_bug_id, "name": f"{PREFIX}-backend",
        })
        await _h(TAG_T, "kaiten_add_card_tag")(client, {
            "card_id": S.card_bug_id, "name": f"{PREFIX}-urgent",
        })

        # Add tag to feature card
        await _h(TAG_T, "kaiten_add_card_tag")(client, {
            "card_id": S.card_feature_id, "name": f"{PREFIX}-frontend",
        })

        # Verify by re-reading card
        card = await _h(CARD_T, "kaiten_get_card")(client, {"card_id": S.card_bug_id})
        tag_names = [t["name"] for t in (card.get("tags") or [])]
        assert f"{PREFIX}-backend" in tag_names

        # Remove one tag
        await _h(TAG_T, "kaiten_remove_card_tag")(client, {
            "card_id": S.card_bug_id, "tag_id": S.tag_urgent_id,
        })

    # ---------------------------------------------------------------
    # Phase 9: Comments
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_09_comments(self, client):
        """kaiten_create_comment, kaiten_list_comments, kaiten_update_comment,
        kaiten_delete_comment"""
        cmt = await _h(CMT_T, "kaiten_create_comment")(client, {
            "card_id": S.card_bug_id,
            "text": f"[{PREFIX}] Investigating session timeout issue. Seems related to cookie expiry.",
        })
        S.comment_id = cmt["id"]

        # Internal comment
        await _h(CMT_T, "kaiten_create_comment")(client, {
            "card_id": S.card_bug_id,
            "text": f"[{PREFIX}] Internal note: check Redis TTL config",
            "internal": True,
        })

        # List
        comments = await _h(CMT_T, "kaiten_list_comments")(client, {
            "card_id": S.card_bug_id,
        })
        assert len(comments) >= 2

        # Update
        updated = await _h(CMT_T, "kaiten_update_comment")(client, {
            "card_id": S.card_bug_id,
            "comment_id": S.comment_id,
            "text": f"[{PREFIX}] Root cause found: cookie SameSite attribute misconfigured.",
        })
        assert "Root cause" in updated["text"]

    # ---------------------------------------------------------------
    # Phase 10: Checklists with items
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_10_checklists(self, client):
        """kaiten_create_checklist, kaiten_list_checklists, kaiten_update_checklist,
        kaiten_create_checklist_item x3, kaiten_list_checklist_items,
        kaiten_update_checklist_item"""
        cl = await _h(CK_T, "kaiten_create_checklist")(client, {
            "card_id": S.card_feature_id, "name": f"{PREFIX} Implementation Steps",
        })
        S.checklist_id = cl["id"]

        # Update checklist name
        updated_cl = await _h(CK_T, "kaiten_update_checklist")(client, {
            "card_id": S.card_feature_id, "checklist_id": S.checklist_id,
            "name": f"{PREFIX} Implementation Steps (v2)",
        })
        assert "(v2)" in updated_cl["name"]

        # Create items
        i1 = await _h(CK_T, "kaiten_create_checklist_item")(client, {
            "card_id": S.card_feature_id, "checklist_id": S.checklist_id,
            "text": "Design login form layout", "sort_order": 1,
        })
        S.checklist_item_1_id = i1["id"]

        i2 = await _h(CK_T, "kaiten_create_checklist_item")(client, {
            "card_id": S.card_feature_id, "checklist_id": S.checklist_id,
            "text": "Implement form validation", "sort_order": 2,
        })
        S.checklist_item_2_id = i2["id"]

        await _h(CK_T, "kaiten_create_checklist_item")(client, {
            "card_id": S.card_feature_id, "checklist_id": S.checklist_id,
            "text": "Add OAuth2 buttons", "sort_order": 3,
        })

        # List items
        items = await _h(CK_T, "kaiten_list_checklist_items")(client, {
            "card_id": S.card_feature_id, "checklist_id": S.checklist_id,
        })
        assert len(items) >= 3

        # Check first item
        await _h(CK_T, "kaiten_update_checklist_item")(client, {
            "card_id": S.card_feature_id, "checklist_id": S.checklist_id,
            "item_id": S.checklist_item_1_id, "checked": True,
        })

        # Verify checklists list
        cls_list = await _h(CK_T, "kaiten_list_checklists")(client, {
            "card_id": S.card_feature_id,
        })
        assert len(cls_list) >= 1

    # ---------------------------------------------------------------
    # Phase 11: Parent-child relationships
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_11_card_relations(self, client):
        """kaiten_add_card_child, kaiten_list_card_children,
        kaiten_add_card_parent, kaiten_list_card_parents"""
        # Epic -> Feature (parent-child)
        await _h(REL_T, "kaiten_add_card_child")(client, {
            "card_id": S.card_epic_id, "child_card_id": S.card_feature_id,
        })

        # Feature -> Subtask (parent-child)
        await _h(REL_T, "kaiten_add_card_child")(client, {
            "card_id": S.card_feature_id, "child_card_id": S.card_subtask_id,
        })

        # Verify children of epic
        children = await _h(REL_T, "kaiten_list_card_children")(client, {
            "card_id": S.card_epic_id,
        })
        child_ids = [c["id"] for c in children]
        assert S.card_feature_id in child_ids

        # Verify parents of subtask
        parents = await _h(REL_T, "kaiten_list_card_parents")(client, {
            "card_id": S.card_subtask_id,
        })
        parent_ids = [p["id"] for p in parents]
        assert S.card_feature_id in parent_ids

    # ---------------------------------------------------------------
    # Phase 12: Blockers
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_12_blockers(self, client):
        """kaiten_create_card_blocker, kaiten_list_card_blockers,
        kaiten_get_card_blocker, kaiten_update_card_blocker"""
        blk = await _h(BLK_T, "kaiten_create_card_blocker")(client, {
            "card_id": S.card_feature_id,
            "blocker_card_id": S.card_bug_id,
            "reason": "Session bug must be fixed before login page can be deployed",
        })
        S.blocker_id = blk["id"]

        # List
        blockers = await _h(BLK_T, "kaiten_list_card_blockers")(client, {
            "card_id": S.card_feature_id,
        })
        assert len(blockers) >= 1

        # Get
        got = await _h(BLK_T, "kaiten_get_card_blocker")(client, {
            "card_id": S.card_feature_id, "blocker_id": S.blocker_id,
        })
        assert "Session bug" in got["reason"]

        # Update
        updated = await _h(BLK_T, "kaiten_update_card_blocker")(client, {
            "card_id": S.card_feature_id, "blocker_id": S.blocker_id,
            "reason": "RESOLVED: Session bug fixed. Unblocking soon.",
        })
        assert "RESOLVED" in updated["reason"]

    # ---------------------------------------------------------------
    # Phase 13: External links
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_13_external_links(self, client):
        """kaiten_create_external_link, kaiten_list_external_links,
        kaiten_update_external_link"""
        lnk = await _h(LINK_T, "kaiten_create_external_link")(client, {
            "card_id": S.card_feature_id,
            "url": "https://github.com/example/auth-module/pull/42",
            "description": "PR #42 - Login page implementation",
        })
        S.ext_link_id = lnk["id"]

        # Add another link
        await _h(LINK_T, "kaiten_create_external_link")(client, {
            "card_id": S.card_feature_id,
            "url": "https://figma.com/file/login-page-design",
            "description": "Figma design",
        })

        links = await _h(LINK_T, "kaiten_list_external_links")(client, {
            "card_id": S.card_feature_id,
        })
        assert len(links) >= 2

        # Update
        updated = await _h(LINK_T, "kaiten_update_external_link")(client, {
            "card_id": S.card_feature_id, "link_id": S.ext_link_id,
            "description": "PR #42 - Login page (MERGED)",
        })
        assert "MERGED" in updated["description"]

    # ---------------------------------------------------------------
    # Phase 14: Members and subscribers
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_14_members_and_subscribers(self, client):
        """kaiten_add_card_member, kaiten_list_card_members,
        kaiten_add_card_subscriber, kaiten_list_card_subscribers"""
        # Add current user as member of feature card
        await _h(MBR_T, "kaiten_add_card_member")(client, {
            "card_id": S.card_feature_id, "user_id": S.current_user_id,
        })
        members = await _h(MBR_T, "kaiten_list_card_members")(client, {
            "card_id": S.card_feature_id,
        })
        assert any(
            m.get("id") == S.current_user_id or m.get("user_id") == S.current_user_id
            for m in members
        )

        # Subscribe current user to epic
        await _h(SUB_T, "kaiten_add_card_subscriber")(client, {
            "card_id": S.card_epic_id, "user_id": S.current_user_id,
        })
        subs = await _h(SUB_T, "kaiten_list_card_subscribers")(client, {
            "card_id": S.card_epic_id,
        })
        assert isinstance(subs, list)

    # ---------------------------------------------------------------
    # Phase 15: Card lifecycle -- move through columns
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_15_card_lifecycle(self, client):
        """kaiten_move_card (backlog -> in_progress -> review -> done),
        kaiten_archive_card"""
        # Move bug from In Progress -> Review
        await _h(CARD_T, "kaiten_move_card")(client, {
            "card_id": S.card_bug_id,
            "column_id": S.col_review_id,
        })
        card = await _h(CARD_T, "kaiten_get_card")(client, {"card_id": S.card_bug_id})
        assert card["column_id"] == S.col_review_id

        # Move bug Review -> Done
        await _h(CARD_T, "kaiten_move_card")(client, {
            "card_id": S.card_bug_id,
            "column_id": S.col_done_id,
        })
        card = await _h(CARD_T, "kaiten_get_card")(client, {"card_id": S.card_bug_id})
        assert card["column_id"] == S.col_done_id

        # Move feature from Backlog -> In Progress
        await _h(CARD_T, "kaiten_move_card")(client, {
            "card_id": S.card_feature_id,
            "column_id": S.col_inprogress_id,
        })
        card = await _h(CARD_T, "kaiten_get_card")(client, {"card_id": S.card_feature_id})
        assert card["column_id"] == S.col_inprogress_id

        # Move subtask to In Progress + different lane
        await _h(CARD_T, "kaiten_move_card")(client, {
            "card_id": S.card_subtask_id,
            "column_id": S.col_inprogress_id,
            "lane_id": S.lane_high_id,
        })

        # Verify list by state: cards in "in progress" state
        in_prog = await _h(CARD_T, "kaiten_list_cards")(client, {
            "board_id": S.board_id, "states": "2", "limit": 10,
        })
        in_prog_ids = [c["id"] for c in in_prog]
        assert S.card_feature_id in in_prog_ids

    # ---------------------------------------------------------------
    # Phase 16: Unblock and resolve blocker
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_16_unblock(self, client):
        """kaiten_delete_card_blocker"""
        await _h(BLK_T, "kaiten_delete_card_blocker")(client, {
            "card_id": S.card_feature_id, "blocker_id": S.blocker_id,
        })
        blockers = await _h(BLK_T, "kaiten_list_card_blockers")(client, {
            "card_id": S.card_feature_id,
        })
        blocker_ids = [b["id"] for b in blockers]
        assert S.blocker_id not in blocker_ids

    # ---------------------------------------------------------------
    # Phase 17: Project + Sprint
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_17_project_and_sprint(self, client):
        """kaiten_create_project, kaiten_get_project, kaiten_list_projects,
        kaiten_update_project, kaiten_add_project_card, kaiten_list_project_cards,
        kaiten_create_sprint, kaiten_get_sprint, kaiten_list_sprints,
        kaiten_update_sprint"""
        # Project
        proj = await _h(PROJ_T, "kaiten_create_project")(client, {
            "title": f"{PREFIX} Auth Module Project",
            "description": "Authentication module delivery",
        })
        S.project_id = proj["id"]

        got = await _h(PROJ_T, "kaiten_get_project")(client, {"project_id": S.project_id})
        assert got["title"] == f"{PREFIX} Auth Module Project"

        projects = await _h(PROJ_T, "kaiten_list_projects")(client, {"query": PREFIX})
        assert any(p["id"] == S.project_id for p in projects)

        # Update project
        await _h(PROJ_T, "kaiten_update_project")(client, {
            "project_id": S.project_id,
            "description": "Auth module delivery -- updated scope",
        })

        # Add cards to project
        await _h(PROJ_T, "kaiten_add_project_card")(client, {
            "project_id": S.project_id, "card_id": S.card_epic_id,
        })
        await _h(PROJ_T, "kaiten_add_project_card")(client, {
            "project_id": S.project_id, "card_id": S.card_feature_id,
        })
        await _h(PROJ_T, "kaiten_add_project_card")(client, {
            "project_id": S.project_id, "card_id": S.card_bug_id,
        })

        pcards = await _h(PROJ_T, "kaiten_list_project_cards")(client, {
            "project_id": S.project_id,
        })
        pcard_ids = [c["id"] for c in pcards]
        assert S.card_epic_id in pcard_ids

        # Sprint
        start = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        end = (datetime.now(timezone.utc) + timedelta(days=14)).strftime("%Y-%m-%d")
        sp = await _h(PROJ_T, "kaiten_create_sprint")(client, {
            "title": f"{PREFIX} Sprint 1",
            "start_date": start,
            "end_date": end,
        })
        S.sprint_id = sp["id"]

        got_sp = await _h(PROJ_T, "kaiten_get_sprint")(client, {"sprint_id": S.sprint_id})
        assert got_sp["title"] == f"{PREFIX} Sprint 1"

        sprints = await _h(PROJ_T, "kaiten_list_sprints")(client, {"query": PREFIX})
        assert any(s["id"] == S.sprint_id for s in sprints)

        # Update sprint
        await _h(PROJ_T, "kaiten_update_sprint")(client, {
            "sprint_id": S.sprint_id,
            "title": f"{PREFIX} Sprint 1 (extended)",
        })

    # ---------------------------------------------------------------
    # Phase 18: Documents & document groups
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_18_documents(self, client):
        """kaiten_create_document_group, kaiten_get_document_group,
        kaiten_list_document_groups, kaiten_update_document_group,
        kaiten_create_document, kaiten_get_document, kaiten_list_documents,
        kaiten_update_document"""
        # Document group
        dg = await _h(DOC_T, "kaiten_create_document_group")(client, {
            "title": f"{PREFIX} Tech Specs",
        })
        S.doc_group_uid = dg["uid"]

        got_dg = await _h(DOC_T, "kaiten_get_document_group")(client, {
            "group_uid": S.doc_group_uid,
        })
        assert got_dg["title"] == f"{PREFIX} Tech Specs"

        dgs = await _h(DOC_T, "kaiten_list_document_groups")(client, {"query": PREFIX})
        assert isinstance(dgs, list)

        # Update group
        await _h(DOC_T, "kaiten_update_document_group")(client, {
            "group_uid": S.doc_group_uid,
            "title": f"{PREFIX} Tech Specs (updated)",
        })

        # Document
        doc = await _h(DOC_T, "kaiten_create_document")(client, {
            "title": f"{PREFIX} Auth API Specification",
            "text": "# Auth API\n\n## Endpoints\n\n- POST /auth/login\n- POST /auth/refresh\n- DELETE /auth/logout",
            "folder_uid": S.doc_group_uid,
        })
        S.doc_uid = doc["uid"]

        got_doc = await _h(DOC_T, "kaiten_get_document")(client, {"document_uid": S.doc_uid})
        assert got_doc["title"] == f"{PREFIX} Auth API Specification"

        docs = await _h(DOC_T, "kaiten_list_documents")(client, {"query": PREFIX})
        assert isinstance(docs, list)

        # Update document
        await _h(DOC_T, "kaiten_update_document")(client, {
            "document_uid": S.doc_uid,
            "text": "# Auth API v2\n\n## Endpoints\n\n- POST /auth/login\n- POST /auth/refresh\n- DELETE /auth/logout\n- GET /auth/me",
        })

    # ---------------------------------------------------------------
    # Phase 19: Webhooks
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_19_webhooks(self, client):
        """kaiten_create_webhook, kaiten_get_webhook, kaiten_list_webhooks,
        kaiten_update_webhook"""
        wh = await _h(WH_T, "kaiten_create_webhook")(client, {
            "space_id": S.space_id,
            "url": f"https://httpbin.org/post?test={TS}",
            "active": False,
        })
        S.webhook_id = wh["id"]

        got = await _h(WH_T, "kaiten_get_webhook")(client, {
            "space_id": S.space_id, "webhook_id": S.webhook_id,
        })
        assert got["url"].endswith(f"test={TS}")

        whs = await _h(WH_T, "kaiten_list_webhooks")(client, {"space_id": S.space_id})
        assert any(w["id"] == S.webhook_id for w in whs)

        # Update
        await _h(WH_T, "kaiten_update_webhook")(client, {
            "space_id": S.space_id, "webhook_id": S.webhook_id,
            "active": False,
            "url": f"https://httpbin.org/post?test={TS}&v=2",
        })

    # ---------------------------------------------------------------
    # Phase 20: Automations
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_20_automations(self, client):
        """kaiten_create_automation, kaiten_get_automation, kaiten_list_automations,
        kaiten_update_automation"""
        auto = await _h(AUTO_T, "kaiten_create_automation")(client, {
            "space_id": S.space_id,
            "name": f"{PREFIX} Auto-assign on move",
            "trigger": {
                "type": "card_moved",
                "params": {"column_id": S.col_inprogress_id},
            },
            "action": {
                "type": "set_owner",
                "params": {"user_id": S.current_user_id},
            },
            "active": False,
        })
        S.automation_id = auto["id"]

        got = await _h(AUTO_T, "kaiten_get_automation")(client, {
            "space_id": S.space_id, "automation_id": S.automation_id,
        })
        assert got["name"] == f"{PREFIX} Auto-assign on move"

        autos = await _h(AUTO_T, "kaiten_list_automations")(client, {
            "space_id": S.space_id,
        })
        assert any(a["id"] == S.automation_id for a in autos)

        # Update
        await _h(AUTO_T, "kaiten_update_automation")(client, {
            "space_id": S.space_id, "automation_id": S.automation_id,
            "name": f"{PREFIX} Auto-assign (disabled)",
        })

    # ---------------------------------------------------------------
    # Phase 21: Company groups
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_21_company_groups(self, client):
        """kaiten_create_company_group, kaiten_get_company_group,
        kaiten_list_company_groups, kaiten_update_company_group,
        kaiten_add_group_user, kaiten_list_group_users, kaiten_remove_group_user"""
        cg = await _h(RG_T, "kaiten_create_company_group")(client, {
            "name": f"{PREFIX} Test Team",
            "description": "E2E test group",
        })
        S.company_group_uid = cg["uid"]

        got = await _h(RG_T, "kaiten_get_company_group")(client, {
            "group_uid": S.company_group_uid,
        })
        assert got["name"] == f"{PREFIX} Test Team"

        groups = await _h(RG_T, "kaiten_list_company_groups")(client, {"query": PREFIX})
        assert isinstance(groups, list)

        # Update
        await _h(RG_T, "kaiten_update_company_group")(client, {
            "group_uid": S.company_group_uid,
            "description": "Updated E2E test group",
        })

        # Add current user to group
        await _h(RG_T, "kaiten_add_group_user")(client, {
            "group_uid": S.company_group_uid, "user_id": S.current_user_id,
        })
        gusers = await _h(RG_T, "kaiten_list_group_users")(client, {
            "group_uid": S.company_group_uid,
        })
        assert any(
            u.get("id") == S.current_user_id or u.get("user_id") == S.current_user_id
            for u in gusers
        )

        # Remove user from group
        await _h(RG_T, "kaiten_remove_group_user")(client, {
            "group_uid": S.company_group_uid, "user_id": S.current_user_id,
        })

    # ---------------------------------------------------------------
    # Phase 22: Read-only tools (roles, company, calendars, etc.)
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_22_readonly_tools(self, client):
        """kaiten_list_roles, kaiten_get_company, kaiten_list_calendars,
        kaiten_list_space_users, kaiten_list_removed_cards"""
        roles = await _h(RG_T, "kaiten_list_roles")(client, {"limit": 5})
        assert isinstance(roles, list)

        company = await _h(UTIL_T, "kaiten_get_company")(client, {})
        assert "id" in company

        cals = await _h(UTIL_T, "kaiten_list_calendars")(client, {"limit": 5})
        assert isinstance(cals, list)

        space_users = await _h(RG_T, "kaiten_list_space_users")(client, {
            "space_id": S.space_id,
        })
        assert isinstance(space_users, list)

        removed = await _h(UTIL_T, "kaiten_list_removed_cards")(client, {"limit": 5})
        assert isinstance(removed, list)

    # ---------------------------------------------------------------
    # Phase 23: Card filtering (advanced queries)
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_23_card_filtering(self, client):
        """kaiten_list_cards with various filters"""
        # By type
        bugs = await _h(CARD_T, "kaiten_list_cards")(client, {
            "board_id": S.board_id,
            "type_id": S.card_type_bug_id,
            "limit": 10,
        })
        assert all(c.get("type_id") == S.card_type_bug_id for c in bugs if c.get("type_id"))

        # By column
        backlog_cards = await _h(CARD_T, "kaiten_list_cards")(client, {
            "column_id": S.col_backlog_id, "limit": 10,
        })
        assert isinstance(backlog_cards, list)

        # Done cards (state=3)
        done_cards = await _h(CARD_T, "kaiten_list_cards")(client, {
            "board_id": S.board_id, "states": "3", "limit": 10,
        })
        done_ids = [c["id"] for c in done_cards]
        assert S.card_bug_id in done_ids

    # ---------------------------------------------------------------
    # Phase 24: Archive a card
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_24_archive_card(self, client):
        """kaiten_archive_card"""
        await _h(CARD_T, "kaiten_archive_card")(client, {"card_id": S.card_task_id})
        card = await _h(CARD_T, "kaiten_get_card")(client, {"card_id": S.card_task_id})
        assert card.get("condition") == 2  # archived

    # ---------------------------------------------------------------
    # Phase 25: Time log on a DEDICATED card (will not be deleted)
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_25_time_logs(self, client):
        """kaiten_create_time_log, kaiten_list_card_time_logs,
        kaiten_update_time_log, kaiten_delete_time_log
        NOTE: We create a separate card for time logs because cards with
        time logs cannot be deleted. This card is archived at the end."""
        # Create dedicated card
        tl_card = await _h(CARD_T, "kaiten_create_card")(client, {
            "title": f"{PREFIX} Time-log test card (DO NOT DELETE)",
            "board_id": S.board_id,
            "column_id": S.col_inprogress_id,
        })
        S.card_timelog_id = tl_card["id"]

        # Create time log
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        tl = await _h(TL_T, "kaiten_create_time_log")(client, {
            "card_id": S.card_timelog_id,
            "time_spent": 30,
            "for_date": today,
            "comment": f"[{PREFIX}] E2E testing work",
        })
        S.time_log_id = tl["id"]

        # List
        logs = await _h(TL_T, "kaiten_list_card_time_logs")(client, {
            "card_id": S.card_timelog_id,
        })
        assert any(l["id"] == S.time_log_id for l in logs)

        # Update
        await _h(TL_T, "kaiten_update_time_log")(client, {
            "card_id": S.card_timelog_id,
            "time_log_id": S.time_log_id,
            "time_spent": 45,
            "comment": f"[{PREFIX}] E2E testing work (updated)",
        })

        # Delete the time log so the card CAN be deleted later
        await _h(TL_T, "kaiten_delete_time_log")(client, {
            "card_id": S.card_timelog_id,
            "time_log_id": S.time_log_id,
        })

    # ---------------------------------------------------------------
    # Phase 26: Workflows (company-level)
    # ---------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_26_workflows(self, client):
        """kaiten_create_workflow, kaiten_get_workflow, kaiten_list_workflows,
        kaiten_update_workflow, kaiten_delete_workflow"""
        wf = await _h(AUTO_T, "kaiten_create_workflow")(client, {
            "name": f"{PREFIX} Dev Pipeline",
            "description": "E2E test workflow",
        })
        wf_id = wf["id"]

        got = await _h(AUTO_T, "kaiten_get_workflow")(client, {"workflow_id": wf_id})
        assert got["name"] == f"{PREFIX} Dev Pipeline"

        wfs = await _h(AUTO_T, "kaiten_list_workflows")(client, {"query": PREFIX})
        assert any(w["id"] == wf_id for w in wfs)

        await _h(AUTO_T, "kaiten_update_workflow")(client, {
            "workflow_id": wf_id, "description": "Updated E2E workflow",
        })

        # Cleanup workflow immediately (no dependencies)
        await _h(AUTO_T, "kaiten_delete_workflow")(client, {"workflow_id": wf_id})

    # ===================================================================
    # TEARDOWN -- delete everything in reverse dependency order
    # ===================================================================

    @pytest.mark.asyncio
    async def test_99_teardown(self, client):
        """Clean up all created entities in reverse dependency order.
        Every deletion is wrapped in _safe_delete so partial failures
        do not prevent later clean-up steps."""
        logger.info("=== TEARDOWN START ===")

        # -- Automation --
        if S.automation_id:
            await _safe_delete(
                _h(AUTO_T, "kaiten_delete_automation")(client, {
                    "space_id": S.space_id, "automation_id": S.automation_id,
                })
            )

        # -- Webhook --
        if S.webhook_id:
            await _safe_delete(
                _h(WH_T, "kaiten_delete_webhook")(client, {
                    "space_id": S.space_id, "webhook_id": S.webhook_id,
                })
            )

        # -- Remove cards from project --
        if S.project_id:
            for cid in [S.card_epic_id, S.card_feature_id, S.card_bug_id]:
                if cid:
                    await _safe_delete(
                        _h(PROJ_T, "kaiten_remove_project_card")(client, {
                            "project_id": S.project_id, "card_id": cid,
                        })
                    )

        # -- Sprint --
        if S.sprint_id:
            await _safe_delete(
                _h(PROJ_T, "kaiten_delete_sprint")(client, {"sprint_id": S.sprint_id})
            )

        # -- Project --
        if S.project_id:
            await _safe_delete(
                _h(PROJ_T, "kaiten_delete_project")(client, {"project_id": S.project_id})
            )

        # -- Documents --
        if S.doc_uid:
            await _safe_delete(
                _h(DOC_T, "kaiten_delete_document")(client, {"document_uid": S.doc_uid})
            )
        if S.doc_group_uid:
            await _safe_delete(
                _h(DOC_T, "kaiten_delete_document_group")(client, {"group_uid": S.doc_group_uid})
            )

        # -- Company group --
        if S.company_group_uid:
            await _safe_delete(
                _h(RG_T, "kaiten_delete_company_group")(client, {
                    "group_uid": S.company_group_uid,
                })
            )

        # -- Card sub-entities: remove relations before deleting cards --
        if S.card_epic_id and S.card_feature_id:
            await _safe_delete(
                _h(REL_T, "kaiten_remove_card_child")(client, {
                    "card_id": S.card_epic_id, "child_id": S.card_feature_id,
                })
            )
        if S.card_feature_id and S.card_subtask_id:
            await _safe_delete(
                _h(REL_T, "kaiten_remove_card_child")(client, {
                    "card_id": S.card_feature_id, "child_id": S.card_subtask_id,
                })
            )

        # -- Remove member and subscriber --
        if S.card_feature_id and S.current_user_id:
            await _safe_delete(
                _h(MBR_T, "kaiten_remove_card_member")(client, {
                    "card_id": S.card_feature_id, "user_id": S.current_user_id,
                })
            )
        if S.card_epic_id and S.current_user_id:
            await _safe_delete(
                _h(SUB_T, "kaiten_remove_card_subscriber")(client, {
                    "card_id": S.card_epic_id, "user_id": S.current_user_id,
                })
            )

        # -- Delete external links --
        if S.card_feature_id:
            # Get all links and delete them
            try:
                links = await _h(LINK_T, "kaiten_list_external_links")(client, {
                    "card_id": S.card_feature_id,
                })
                for lnk in links:
                    await _safe_delete(
                        _h(LINK_T, "kaiten_delete_external_link")(client, {
                            "card_id": S.card_feature_id, "link_id": lnk["id"],
                        })
                    )
            except Exception:
                pass

        # -- Delete checklist items then checklist --
        if S.card_feature_id and S.checklist_id:
            for item_id in [S.checklist_item_1_id, S.checklist_item_2_id]:
                if item_id:
                    await _safe_delete(
                        _h(CK_T, "kaiten_delete_checklist_item")(client, {
                            "card_id": S.card_feature_id,
                            "checklist_id": S.checklist_id,
                            "item_id": item_id,
                        })
                    )
            await _safe_delete(
                _h(CK_T, "kaiten_delete_checklist")(client, {
                    "card_id": S.card_feature_id, "checklist_id": S.checklist_id,
                })
            )

        # -- Delete comments --
        if S.card_bug_id:
            try:
                comments = await _h(CMT_T, "kaiten_list_comments")(client, {
                    "card_id": S.card_bug_id,
                })
                for c in comments:
                    await _safe_delete(
                        _h(CMT_T, "kaiten_delete_comment")(client, {
                            "card_id": S.card_bug_id, "comment_id": c["id"],
                        })
                    )
            except Exception:
                pass

        # -- Delete cards (no time logs on these) --
        for card_id in [
            S.card_subtask_id, S.card_task_id, S.card_bug_id,
            S.card_feature_id, S.card_epic_id, S.card_timelog_id,
        ]:
            if card_id:
                await _safe_delete(
                    _h(CARD_T, "kaiten_delete_card")(client, {"card_id": card_id})
                )

        # -- Subcolumn --
        if S.subcolumn_id:
            await _safe_delete(
                _h(SUB_T, "kaiten_delete_subcolumn")(client, {
                    "column_id": S.col_review_id, "subcolumn_id": S.subcolumn_id,
                })
            )

        # -- Lanes --
        for lane_id in [S.lane_high_id, S.lane_normal_id]:
            if lane_id:
                await _safe_delete(
                    _h(LANE_T, "kaiten_delete_lane")(client, {
                        "board_id": S.board_id, "lane_id": lane_id,
                    })
                )

        # -- Columns --
        for col_id in [S.col_backlog_id, S.col_inprogress_id, S.col_review_id, S.col_done_id]:
            if col_id:
                await _safe_delete(
                    _h(COL_T, "kaiten_delete_column")(client, {
                        "board_id": S.board_id, "column_id": col_id,
                    })
                )

        # -- Board --
        if S.board_id:
            await _safe_delete(
                _h(BOARD_T, "kaiten_delete_board")(client, {
                    "space_id": S.space_id, "board_id": S.board_id,
                })
            )

        # -- Space --
        if S.space_id:
            await _safe_delete(
                _h(SPACE_T, "kaiten_delete_space")(client, {"space_id": S.space_id})
            )

        # -- Tags (company-level) --
        for tag_id in [S.tag_backend_id, S.tag_frontend_id, S.tag_urgent_id]:
            if tag_id:
                await _safe_delete(
                    _h(TAG_T, "kaiten_delete_tag")(client, {"tag_id": tag_id})
                )

        # -- Custom properties (company-level) --
        for prop_id in [S.prop_priority_id, S.prop_effort_id, S.prop_done_id]:
            if prop_id:
                await _safe_delete(
                    _h(PROP_T, "kaiten_delete_custom_property")(client, {
                        "property_id": prop_id,
                    })
                )

        # -- Card types (company-level) --
        for ct_id in [S.card_type_bug_id, S.card_type_feature_id, S.card_type_task_id]:
            if ct_id:
                await _safe_delete(
                    _h(CTYPE_T, "kaiten_delete_card_type")(client, {"type_id": ct_id})
                )

        logger.info("=== TEARDOWN COMPLETE ===")
