---
name: kaiten-heavy-data
description: Handle large Kaiten API responses without overflowing LLM context
version: 1.0.0
---

# Working with Heavy MCP Data from Kaiten

This skill teaches how to efficiently handle bulk Kaiten data (cards, activity, etc.) without overflowing the LLM context window. The key principle: **large content goes to temp files, not through the LLM**.

## Anti-patterns (NEVER DO THIS)

- **NEVER** call bulk card endpoints without `relations="none"` — full card objects are ~20KB each, 100 cards = 2MB+ which overflows context
- **NEVER** pass 2MB+ JSON responses through the LLM — save to file and extract needed fields
- **NEVER** write Python scripts that call the Kaiten REST API directly — use MCP tools with proper parameters
- **NEVER** read saved JSON files entirely into LLM context — parse them with targeted field extraction
- **NEVER** call `kaiten_get_card_location_history` per card — use `kaiten_get_all_space_activity` instead
- **NEVER** use `kaiten_list_cards` for bulk operations — use `kaiten_list_all_cards` which auto-paginates and defaults to `relations="none"`

## Response Size Control Parameters

### `relations` — API-level nested object control

Controls which nested objects the Kaiten API returns with each card.

| Value | Effect | Response size |
|---|---|---|
| *(not set)* | All relations included (members, files, comments, checklists, properties, tags, type) | ~20KB/card |
| `"none"` | All relations excluded | ~2KB/card |
| `"member,type"` | Only listed relations included | varies |

**Default for `kaiten_list_all_cards`**: `"none"` (lightweight by default).
**Default for `kaiten_list_cards`**: all relations (for interactive use).

### `fields` — Client-side field whitelist

Returns only the listed fields per item. Applied after API response.

```
fields="id,title,created,last_moved_to_done_at,state"
```

With `fields`, each card is ~100-300 bytes. 500 cards = ~100KB.

### `compact` — Strip heavy scalar fields

When `compact=true` (default for bulk tools):
- Removes `description` field (up to 32KB per card)
- Simplifies user objects to `{id, full_name}`
- Strips base64 avatar data

### Combined usage (recommended for all bulk operations)

```
kaiten_list_all_cards(
  space_id=X,
  relations="none",
  fields="id,title,type_id,created,state,condition",
  compact=true
)
```

## Decision Tree

```
Need card data?
├── Single card → kaiten_get_card(card_id=X) — full data OK
├── List of cards (interactive) → kaiten_list_cards(space_id=X) — full data OK for small lists
└── Bulk cards (50+)
    ├── Need only counts/metrics? → Use fields parameter with timing fields only
    ├── Need descriptions? → Use relations="none" (keeps descriptions, drops nested objects)
    └── Need everything? → Use relations="none", process in batches

Need activity data?
├── Single space, recent → kaiten_get_space_activity(space_id=X, fields="id,action,card_id,changed")
└── Full history → kaiten_get_all_space_activity(space_id=X, fields="id,action,card_id,column_id,changed")

Need analytics?
└── Use kaiten_chart_* tools — server computes everything, tiny response
```

## File-Based Output

When `KAITEN_MCP_OUTPUT_DIR` is configured, responses exceeding 200KB are automatically saved to files:

```json
{
  "saved_to": "/path/to/kaiten_list_all_cards_20260220_143052.json",
  "total_items": 500,
  "size_bytes": 450000,
  "sample": [{"id": 1, "title": "..."}, {"id": 2, "title": "..."}, {"id": 3, "title": "..."}],
  "tip": "Read the saved file to process data. Use 'fields' parameter to reduce response size."
}
```

### Setup

**Docker**: Add volume mount and env var:
```bash
docker run --rm -i \
  -v ./tmp:/tmp/kaiten-mcp \
  -e KAITEN_MCP_OUTPUT_DIR=/tmp/kaiten-mcp \
  -e KAITEN_DOMAIN -e KAITEN_TOKEN \
  kaiten-mcp
```

**Python venv**: Set env var:
```bash
export KAITEN_MCP_OUTPUT_DIR=./tmp
```

### Processing saved files

When a file is saved, do NOT read the entire file into context. Instead:
1. Read the summary (returned by the tool)
2. Use targeted file processing to extract needed data
3. Pass only extracted data to the LLM

## Response Size Reference

| Configuration | Per card | 100 cards | 500 cards |
|---|---|---|---|
| No optimization | ~20KB | 2MB+ (OVERFLOW) | 10MB+ (OVERFLOW) |
| `relations="none"` | ~2KB | ~200KB | ~1MB |
| `relations="none"` + `compact` | ~500B | ~50KB | ~250KB |
| `relations="none"` + `fields` (metrics) | ~200B | ~20KB | **~100KB** |

## ToolSearch Queries

```
ToolSearch query: "+kaiten list all cards"       --> kaiten_list_all_cards (bulk, auto-paginating)
ToolSearch query: "+kaiten space activity"        --> kaiten_get_all_space_activity (bulk activity)
ToolSearch query: "+kaiten chart"                 --> kaiten_chart_cfd, kaiten_chart_control, etc.
```
