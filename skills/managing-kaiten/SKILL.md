---
name: managing-kaiten
description: Manages projects, boards, cards, documents, and workflows in Kaiten via the Kaiten MCP server. Use when the user asks about Kaiten tasks, boards, spaces, cards, timelines, Gantt charts, project management, or any Kaiten-related operations. Supports full CRUD on spaces, boards, columns, lanes, cards, documents, tags, checklists, sprints, automations, and more.
---

# Managing Kaiten via MCP Server

## Quick start

All Kaiten tools are deferred. Load them before use:

```
ToolSearch query: "+kaiten list spaces"
ToolSearch query: "select:mcp__kaiten__kaiten_get_current_user"
```

Tool naming pattern: `mcp__kaiten__kaiten_<action>` (e.g., `mcp__kaiten__kaiten_list_cards`).

Always begin a session with `kaiten_get_current_user` to get the user's ID, name, and permissions.

## Core concepts

**Hierarchy**: Company → Space → Board → Column/Lane → Card

**Card types**: Epic, Story, Task (or custom). Set via `type_id`.

**Card states**: 1 = Queue, 2 = In Progress, 3 = Done

**Column types**: 1 = Queue, 2 = In Progress, 3 = Done

**Card conditions**: 1 = Active, 2 = Archived, 3 = Deleted

**Timeline/Gantt**: Use `planned_start` and `planned_end` fields (ISO 8601) on cards.

**Size estimation**: `size_text` field accepts S, M, L, XL.

## Essential workflows

### Creating a full board structure

1. Create or select a space (`kaiten_create_space` or `kaiten_list_spaces`)
2. Create board in space (`kaiten_create_board` with `space_id`)
3. Create columns (`kaiten_create_column` with `board_id`, `type` 1/2/3)
4. Create at least one lane (`kaiten_create_lane` with `board_id`)
5. Now cards can be placed on the board

### Creating cards with timeline

```
kaiten_create_card:
  title, board_id, column_id, lane_id, type_id, owner_id,
  planned_start: "2026-03-01T00:00:00.000Z",
  planned_end: "2026-03-31T00:00:00.000Z",
  size_text: "L"
```

### Parent-child relationships (decomposition)

Parent-child links are NOT set during card creation. Use a separate call:

```
kaiten_add_card_child:
  card_id: <parent_card_id>
  child_card_id: <child_card_id>
```

For three-level decomposition (Epic → Story → Task):
- Link each Story as child of its Epic
- Link each Task as child of its Story

### Creating documents

Two-step process. See [PROSEMIRROR.md](PROSEMIRROR.md) for content format.

1. Create document group (optional folder):
   ```
   kaiten_create_document_group: title, sort_order (REQUIRED)
   ```
2. Create document:
   ```
   kaiten_create_document: title, parent_entity_uid, sort_order (REQUIRED)
   ```
3. Update with content:
   ```
   kaiten_update_document: document_uid, data (ProseMirror JSON object)
   ```

## Handling large responses

List operations (cards, users, spaces) return verbose JSON with base64 avatars. When responses exceed context limits, they are saved to disk files.

**Strategy**: Write a Python parsing script to `/tmp/` and run it on the saved file:

```python
import json, sys
with open(sys.argv[1], 'r') as f:
    data = json.load(f)
# Find the text content in MCP response
text = None
for item in data:
    if item.get('type') == 'text':
        text = item['text']
        break
items = json.loads(text)
for item in items:
    print(f"[{item['id']}] {item.get('title', '?')}")
```

## Bulk operations

For creating 10+ cards or links, use background agents to avoid context bloat. Pass the agent a flat list of parameters and let it call tools sequentially.

## Gotchas

- `sort_order` is required for documents and document groups (schema says optional, API says otherwise)
- ProseMirror `bullet_list`/`list_item` nodes cause HTTP 500. Use `paragraph` with bullet characters instead
- `kaiten_list_cards` accepts `space_id` to filter by space
- Rate limit: 4.5 req/s. The MCP server handles retries automatically
- Card `state` is derived from column type, not set directly

## Reference

**Full tool list by category**: See [TOOLS_REFERENCE.md](TOOLS_REFERENCE.md)
**ProseMirror document format**: See [PROSEMIRROR.md](PROSEMIRROR.md)
**Complex workflow examples**: See [WORKFLOWS.md](WORKFLOWS.md)
