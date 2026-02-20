# ProseMirror Document Format for Kaiten

**Preferred**: Use the `text` parameter on `kaiten_create_document` / `kaiten_update_document` to pass markdown content. It auto-converts to ProseMirror. Supports: `# headings`, `**bold**`, `*italic*`, `~~strike~~`, `` `code` ``, `> quotes`, `---` rules.

**Advanced**: For full control, use the `data` field with raw ProseMirror JSON (described below).

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

## Lists (bullet_list / ordered_list)

The MCP server **automatically converts** `bullet_list` and `ordered_list` nodes to safe paragraph equivalents before sending to the API. You can use standard ProseMirror list syntax:

```json
{
  "type": "bullet_list",
  "content": [
    {"type": "list_item", "content": [{"type": "text", "text": "First item"}]},
    {"type": "list_item", "content": [{"type": "text", "text": "Second item"}]}
  ]
}
```

This will be automatically transformed to:
```json
{
  "type": "paragraph",
  "content": [{"type": "text", "text": "• First item"}]
},
{
  "type": "paragraph",
  "content": [{"type": "text", "text": "• Second item"}]
}
```

Ordered lists are converted with numbered prefixes (1., 2., 3., etc.).

## Size limits

Large documents (30+ nodes) in a single update may cause HTTP 500. Keep documents under ~20 content nodes per update. If more content is needed, make the text denser rather than adding more nodes.

## Creating documents with content

**One-step (recommended):**
```
kaiten_create_document: title="My Doc", text="## Hello\n\nContent here"
```

**Two-step (for raw ProseMirror JSON):**
1. `kaiten_create_document` — creates document, returns `uid`
   - `sort_order` is auto-generated if not provided
2. `kaiten_update_document` — sets content via `data` parameter (ProseMirror JSON object, NOT a string)

The `data` parameter must be a JSON **object**, not a JSON string. The MCP server handles serialization.

## Associating documents with spaces

Kaiten documents live in document groups (folders), not directly in spaces. To associate a document with a space conceptually:

1. Create a document group with a matching name (e.g., "IT Department")
2. Create the document with `parent_entity_uid` set to the group's UID
3. `sort_order` is auto-generated if not provided

## Example: Complete document creation

```
Step 1: kaiten_create_document_group
  title: "Project Documentation"
  → returns uid: "abc-123"

Step 2: kaiten_create_document
  title: "Project Plan"
  parent_entity_uid: "abc-123"
  → returns uid: "def-456"

Step 3: kaiten_update_document
  document_uid: "def-456"
  data: {
    "type": "doc",
    "content": [
      {"type": "heading", "attrs": {"level": 1}, "content": [{"type": "text", "text": "Project Plan"}]},
      {"type": "paragraph", "content": [{"type": "text", "text": "Overview of the project..."}]},
      {"type": "bullet_list", "content": [
        {"type": "list_item", "content": [{"type": "text", "text": "Goal 1"}]},
        {"type": "list_item", "content": [{"type": "text", "text": "Goal 2"}]}
      ]}
    ]
  }
```

The bullet_list will be automatically converted to safe paragraphs.
