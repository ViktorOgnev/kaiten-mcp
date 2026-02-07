# Kaiten Workflow Examples

## Workflow 1: Account overview

```
Progress:
- [ ] Get current user
- [ ] List all spaces
- [ ] List cards (filter by space if needed)
- [ ] Parse and present results
```

1. Load tools: `ToolSearch query: "+kaiten list spaces"` and `select:mcp__kaiten__kaiten_get_current_user`
2. Call `kaiten_get_current_user` → note `id`, `full_name`
3. Call `kaiten_list_spaces` → note space IDs and names
4. Call `kaiten_list_cards` with `space_id` filter for each space of interest
5. If response is too large, save to file and parse with Python script

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
- [ ] List cards in space
- [ ] Parse card data (state, column, owner, dates, tags)
- [ ] Present summary by board/status
```

**Parsing large card lists**: Write a reusable script:

```python
import json, sys

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

text = None
for item in data:
    if item.get('type') == 'text':
        text = item['text']
        break

cards = json.loads(text)
state_map = {1: 'Queue', 2: 'In Progress', 3: 'Done'}

for c in cards:
    state = state_map.get(c.get('state'), '?')
    title = c.get('title', 'No title')
    card_id = c.get('id')
    board = c.get('board', {}).get('title', '?') if c.get('board') else '?'
    column = c.get('column', {}).get('title', '?') if c.get('column') else '?'
    owner = c.get('owner', {}).get('full_name', '-') if c.get('owner') else '-'
    print(f'[{card_id}] {title} | {state} | {column} | {owner}')
```

Save to `/tmp/parse_cards.py`, run: `python3 /tmp/parse_cards.py <response_file>`

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

See [PROSEMIRROR.md](PROSEMIRROR.md) for format details and known limitations.

## Common ToolSearch queries

| Need | Query |
|---|---|
| Spaces | `+kaiten list spaces` |
| Cards | `+kaiten cards` |
| Boards & columns | `+kaiten board column` |
| Documents | `+kaiten document` |
| Card relationships | `+kaiten child parent` |
| Users & members | `+kaiten users members` |
| Card types | `select:mcp__kaiten__kaiten_list_card_types` |
| Current user | `select:mcp__kaiten__kaiten_get_current_user` |
| Tags | `+kaiten tags` |
| Time logs | `+kaiten time log` |
| Projects & sprints | `+kaiten project sprint` |
