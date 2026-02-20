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

**Board hierarchy**: Company → Space → Board → Column/Lane → Card

**Sidebar tree**: Spaces, documents, and document groups form a unified tree via `parent_entity_uid`. Any entity can nest under another (cross-nesting allowed). Use `kaiten_list_children` and `kaiten_get_tree` to navigate.

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

Use the `text` parameter for one-step creation with markdown content, or `data` for raw ProseMirror JSON. See [PROSEMIRROR.md](PROSEMIRROR.md) for advanced format details.

**One-step (recommended)**:
```
kaiten_create_document: title, text="## Heading\n\nContent with **bold**"
```

**Two-step (for complex content)**:
1. Create document group (optional folder):
   ```
   kaiten_create_document_group: title
   ```

2. Create document:
   ```
   kaiten_create_document: title, parent_entity_uid
   ```

3. Update with content:
   ```
   kaiten_update_document: document_uid, data (ProseMirror JSON object)
   ```

Notes:
- `sort_order` is auto-generated if not provided
- `bullet_list` and `ordered_list` nodes are automatically converted to safe paragraphs
- `text` param supports: `# headings`, `**bold**`, `*italic*`, `~~strike~~`, `` `code` ``, `> quotes`, `---` rules

### Navigating the entity tree

Use tree tools to discover what's nested where in the sidebar:

```
kaiten_list_children                         → root-level entities
kaiten_list_children: parent_entity_uid=X    → children of entity X
kaiten_get_tree                              → full nested tree
kaiten_get_tree: root_uid=X, depth=2         → subtree with depth limit
```

## Handling large responses

Use `compact=true` parameter for list operations to reduce response size:

```
kaiten_list_cards: board_id=123, compact=true
kaiten_list_users: compact=true
kaiten_list_spaces: compact=true
```

**What compact mode does:**
- Removes base64-encoded `avatar_url` fields (can be 10-50KB each)
- Simplifies user objects (`owner`, `responsible`, `author`) to `{id, full_name}`
- Simplifies user lists (`members`, `responsibles`) to `[{id, full_name}, ...]`

**Default limit:** All list operations default to 50 items when `limit` is not specified. Use `limit` parameter to override.

## Bulk operations

For creating 10+ cards or links, use background agents to avoid context bloat. Pass the agent a flat list of parameters and let it call tools sequentially.

## Gotchas

- `kaiten_list_cards` accepts `space_id` to filter by space
- Rate limit: 4.5 req/s. The MCP server handles retries automatically
- Card `state` is derived from column type, not set directly
- Default limit is 50 for all list operations

## Kanban metrics

For Kanban metrics collection (Lead Time, Cycle Time, Throughput, WIP, Flow Efficiency), see the [`kaiten-metrics`](../kaiten-metrics/SKILL.md) skill. It covers efficient bulk data fetching, server-side chart computation, and all metric formulas using card fields directly.

## Reference

**Full tool list by category**: See [TOOLS_REFERENCE.md](TOOLS_REFERENCE.md)
**ProseMirror document format**: See [PROSEMIRROR.md](PROSEMIRROR.md)
**Complex workflow examples**: See [WORKFLOWS.md](WORKFLOWS.md)
**Kanban metrics collection**: See [`kaiten-metrics` skill](../kaiten-metrics/SKILL.md)
