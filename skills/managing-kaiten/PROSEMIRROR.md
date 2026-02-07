# ProseMirror Document Format for Kaiten

Kaiten documents use ProseMirror JSON format in the `data` field of `kaiten_update_document`.

## Working node types

These are confirmed to work without errors:

```json
{
  "type": "doc",
  "content": [
    {
      "type": "heading",
      "attrs": {"level": 1},
      "content": [{"type": "text", "text": "Title"}]
    },
    {
      "type": "heading",
      "attrs": {"level": 2},
      "content": [{"type": "text", "text": "Section"}]
    },
    {
      "type": "heading",
      "attrs": {"level": 3},
      "content": [{"type": "text", "text": "Subsection"}]
    },
    {
      "type": "paragraph",
      "content": [{"type": "text", "text": "Regular text."}]
    },
    {
      "type": "paragraph",
      "content": [
        {"type": "text", "marks": [{"type": "bold"}], "text": "Bold text"},
        {"type": "text", "text": " and "},
        {"type": "text", "marks": [{"type": "italic"}], "text": "italic text"}
      ]
    }
  ]
}
```

## Nodes that cause HTTP 500 errors

Do NOT use these — they crash the Kaiten API:

- `bullet_list` with `list_item` children
- `ordered_list` with `list_item` children
- `horizontal_rule`

**Workaround for lists**: Use paragraph nodes with bullet characters:

```json
{
  "type": "paragraph",
  "content": [{"type": "text", "text": "\u2022 First item"}]
}
```

## Size limits

Large documents (30+ nodes) in a single update may cause HTTP 500. Keep documents under ~20 content nodes per update. If more content is needed, make the text denser rather than adding more nodes.

## Two-step creation

1. `kaiten_create_document` — creates empty document, returns `uid`
2. `kaiten_update_document` — sets content via `data` parameter (ProseMirror JSON object, NOT a string)

The `data` parameter must be a JSON **object**, not a JSON string. The MCP server handles serialization.

## Associating documents with spaces

Kaiten documents live in document groups (folders), not directly in spaces. To associate a document with a space conceptually:

1. Create a document group with a matching name (e.g., "IT Department")
2. Create the document with `parent_entity_uid` set to the group's UID
3. Both require `sort_order` (integer) — this field is mandatory despite the schema

## Example: Complete document creation

```
Step 1: kaiten_create_document_group
  title: "Project Documentation"
  sort_order: 1
  → returns uid: "abc-123"

Step 2: kaiten_create_document
  title: "Project Plan"
  parent_entity_uid: "abc-123"
  sort_order: 1
  → returns uid: "def-456"

Step 3: kaiten_update_document
  document_uid: "def-456"
  data: {
    "type": "doc",
    "content": [
      {"type": "heading", "attrs": {"level": 1}, "content": [{"type": "text", "text": "Project Plan"}]},
      {"type": "paragraph", "content": [{"type": "text", "text": "Overview of the project..."}]}
    ]
  }
```
