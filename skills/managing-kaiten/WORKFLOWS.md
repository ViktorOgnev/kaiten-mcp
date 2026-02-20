# Kaiten Workflow Examples

## Workflow 1: Account overview

```
Progress:
- [ ] Get current user
- [ ] List all spaces
- [ ] List cards (filter by space if needed)
- [ ] Present summary
```

1. Load tools: `ToolSearch query: "+kaiten list spaces"` and `select:mcp__kaiten__kaiten_get_current_user`
2. Call `kaiten_get_current_user` → note `id`, `full_name`
3. Call `kaiten_list_spaces(compact=true)` → note space IDs and names
4. Call `kaiten_list_cards(space_id=X, compact=true)` for each space of interest

## Workflow 2: Three-level project setup (Epic → Story → Task)

```
Progress:
- [ ] Create/select space
- [ ] Create 3 boards (Epics, Stories, Tasks)
- [ ] Create columns for each board
- [ ] Create lanes for each board
- [ ] Look up card types (Epic, Story, Task)
- [ ] Create Epic cards with timelines
- [ ] Create Story cards with timelines
- [ ] Link Stories to Epics (parent-child)
- [ ] Create Task cards with timelines (use background agent for 10+)
- [ ] Link Tasks to Stories (use background agent for 10+)
```

**Board setup per level**:

| Board | Columns (type) |
|---|---|
| Epics | Backlog (1), Planning (2), In Progress (2), Done (3) |
| Stories | Backlog (1), In Progress (2), Review (2), Done (3) |
| Tasks | To Do (1), In Progress (2), Testing (2), Done (3) |

**Card creation**: Always include `board_id`, `column_id`, `lane_id`, `type_id`, `owner_id`, `planned_start`, `planned_end`, `size_text`.

**Linking**: After ALL cards are created, link them:
- `kaiten_add_card_child(card_id=epic_id, child_card_id=story_id)`
- `kaiten_add_card_child(card_id=story_id, child_card_id=task_id)`

## Workflow 3: Analyze existing work

```
Progress:
- [ ] List spaces to find target
- [ ] List boards in space
- [ ] List cards in space (compact mode)
- [ ] Present summary by board/status
```

1. `kaiten_list_spaces(compact=true)` → find space_id
2. `kaiten_list_boards(space_id=X, compact=true)` → find board_id
3. `kaiten_list_cards(space_id=X, compact=true)` → get cards

Results with `compact=true` contain only essential fields: `id`, `title`, `state`, simplified `owner`, `column` info.

## Workflow 4: Bulk card operations

For creating or modifying 10+ cards, delegate to a background agent:

```
Task agent prompt template:
"Create N cards on board_id X with the following parameters:
[list of {title, column_id, lane_id, type_id, owner_id, planned_start, planned_end, size_text}]
Use mcp__kaiten__kaiten_create_card for each. Report back with all created card IDs."
```

Similarly for bulk linking:
```
"Link parent-child relationships:
Parent A → Children [X, Y, Z]
Parent B → Children [P, Q, R]
Use mcp__kaiten__kaiten_add_card_child for each pair."
```

## Workflow 5: Document with plan

```
Progress:
- [ ] Create document group (folder)
- [ ] Create empty document in group
- [ ] Prepare ProseMirror JSON content
- [ ] Update document with content
```

Note: `sort_order` is auto-generated if not provided. See [PROSEMIRROR.md](PROSEMIRROR.md) for format details. Lists (`bullet_list`, `ordered_list`) are automatically converted to safe paragraphs.

## Common ToolSearch queries

| Need | Query |
|---|---|
| Spaces | `+kaiten list spaces` |
| Cards | `+kaiten cards` |
| Boards & columns | `+kaiten board column` |
| Documents | `+kaiten document` |
| Entity tree | `+kaiten tree children` |
| Card relationships | `+kaiten child parent` |
| Users & members | `+kaiten users members` |
| Card types | `select:mcp__kaiten__kaiten_list_card_types` |
| Current user | `select:mcp__kaiten__kaiten_get_current_user` |
| Tags | `+kaiten tags` |
| Time logs | `+kaiten time log` |
| Projects & sprints | `+kaiten project sprint` |

## Workflow 6: Navigating the entity tree

```
Progress:
- [ ] Load tree tools
- [ ] List root entities or get full tree
- [ ] Explore specific subtree if needed
```

1. Load tools: `ToolSearch query: "+kaiten tree children"` or `select:mcp__kaiten__kaiten_get_tree`
2. See what's at the top level: `kaiten_list_children()` → root entities
3. Explore a specific folder: `kaiten_list_children(parent_entity_uid="group-uid")`
4. Or get the full nested tree: `kaiten_get_tree()` → recursive tree with children arrays
5. For large orgs, limit depth: `kaiten_get_tree(depth=2)` → only 2 levels deep
6. To see subtree of a specific entity: `kaiten_get_tree(root_uid="entity-uid")`

## Workflow 7: Kanban Metrics Collection

```
Progress:
- [ ] Load metrics tools
- [ ] Fetch all cards (active + archived)
- [ ] Compute metrics from card fields
- [ ] (Optional) Fetch server-side charts
```

1. Load tools: `ToolSearch query: "+kaiten list all cards"` and `select:mcp__kaiten__kaiten_get_compute_job`
2. Fetch active cards: `kaiten_list_all_cards(space_id=X, condition=1)`
3. Fetch archived cards: `kaiten_list_all_cards(space_id=X, condition=2)`
4. Compute metrics from card fields: Lead Time (`last_moved_to_done_at - created`), Cycle Time (`last_moved_to_done_at - first_moved_to_in_progress_at`), Throughput (count completed per period), WIP (count where `state=2`)
5. (Optional) Request server-side charts: `kaiten_chart_cfd(space_id=X, date_from=..., date_to=...)`, then poll with `kaiten_get_compute_job(job_id=...)`

For full metric formulas, column-level flow analysis, and performance details, see the [`kaiten-metrics` skill](../kaiten-metrics/SKILL.md).

## Tips for efficiency

1. **Use compact mode** for all list operations: `compact=true` reduces response size by 80-95%
2. **Default limit is 50** — if you need more, specify `limit` explicitly
3. **Batch operations** — for 10+ items, use background agents
4. **Check user first** — always start with `kaiten_get_current_user` to get user_id for assignments
