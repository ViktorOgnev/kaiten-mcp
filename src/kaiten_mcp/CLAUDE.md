# Kaiten MCP Server

This is an MCP (Model Context Protocol) server that provides full access to the Kaiten project management API. It exposes 119 tools covering spaces, boards, cards, comments, checklists, projects, documents, automations, service desk, and more.

## Quick Setup

Register this MCP server with Claude Code using ONE of these methods:

### Method 1: Direct Python (recommended for development)
```bash
claude mcp add kaiten -e KAITEN_DOMAIN=YOUR_DOMAIN -e KAITEN_TOKEN=YOUR_TOKEN -- python -m kaiten_mcp.server
```

### Method 2: Docker (recommended for isolation)
```bash
claude mcp add kaiten -e KAITEN_DOMAIN=YOUR_DOMAIN -e KAITEN_TOKEN=YOUR_TOKEN -- docker compose -f /path/to/kaiten-mcp/docker-compose.yml run --rm kaiten-mcp
```

### Method 3: Installed package
```bash
pip install -e /path/to/kaiten-mcp
claude mcp add kaiten -e KAITEN_DOMAIN=YOUR_DOMAIN -e KAITEN_TOKEN=YOUR_TOKEN -- kaiten-mcp
```

Replace `YOUR_DOMAIN` with your Kaiten subdomain (e.g. `mycompany` for `mycompany.kaiten.ru`) and `YOUR_TOKEN` with your API token from Kaiten settings.

### Verify Registration
```bash
claude mcp list
```
You should see `kaiten` in the list. Restart Claude Code session after adding the server.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `KAITEN_DOMAIN` | Yes | Your Kaiten subdomain (e.g. `mycompany`) |
| `KAITEN_TOKEN` | Yes | API token from Kaiten user settings |

## Available Tools (119 total)

### Spaces (5 tools)
| Tool | Description |
|------|-------------|
| `kaiten_list_spaces` | List all spaces |
| `kaiten_get_space` | Get space by ID |
| `kaiten_create_space` | Create a space |
| `kaiten_update_space` | Update a space |
| `kaiten_delete_space` | Delete a space |

### Boards (5 tools)
| Tool | Description |
|------|-------------|
| `kaiten_list_boards` | List boards in a space (requires `space_id`) |
| `kaiten_get_board` | Get board by ID |
| `kaiten_create_board` | Create board in a space |
| `kaiten_update_board` | Update a board |
| `kaiten_delete_board` | Delete a board |

### Columns (4 tools)
| Tool | Description |
|------|-------------|
| `kaiten_list_columns` | List columns on a board |
| `kaiten_create_column` | Create column (`type`: 1=queue, 2=in_progress, 3=done) |
| `kaiten_update_column` | Update a column |
| `kaiten_delete_column` | Delete a column |

### Lanes (4 tools)
| Tool | Description |
|------|-------------|
| `kaiten_list_lanes` | List lanes on a board |
| `kaiten_create_lane` | Create a lane |
| `kaiten_update_lane` | Update a lane |
| `kaiten_delete_lane` | Delete a lane |

### Cards (7 tools)
| Tool | Description |
|------|-------------|
| `kaiten_list_cards` | Search/filter cards |
| `kaiten_get_card` | Get card by ID or key |
| `kaiten_create_card` | Create a card (requires `title`, `board_id`) |
| `kaiten_update_card` | Update a card |
| `kaiten_delete_card` | Soft-delete a card |
| `kaiten_archive_card` | Archive a card |
| `kaiten_move_card` | Move card to different board/column/lane |

### Comments (4 tools)
`kaiten_list_comments`, `kaiten_create_comment`, `kaiten_update_comment`, `kaiten_delete_comment`

### Checklists (8 tools)
`kaiten_list_checklists`, `kaiten_create_checklist`, `kaiten_update_checklist`, `kaiten_delete_checklist`, `kaiten_list_checklist_items`, `kaiten_create_checklist_item`, `kaiten_update_checklist_item`, `kaiten_delete_checklist_item`

### Tags (5 tools)
`kaiten_list_tags`, `kaiten_create_tag`, `kaiten_delete_tag`, `kaiten_add_card_tag`, `kaiten_remove_card_tag`

### Card Members & Users (5 tools)
`kaiten_list_card_members`, `kaiten_add_card_member`, `kaiten_remove_card_member`, `kaiten_list_users`, `kaiten_get_current_user`

### Time Logs (4 tools)
`kaiten_list_card_time_logs`, `kaiten_create_time_log`, `kaiten_update_time_log`, `kaiten_delete_time_log`

### Blockers (5 tools)
`kaiten_list_card_blockers`, `kaiten_create_card_blocker`, `kaiten_get_card_blocker`, `kaiten_update_card_blocker`, `kaiten_delete_card_blocker`

### Card Relations (6 tools)
`kaiten_list_card_children`, `kaiten_add_card_child`, `kaiten_remove_card_child`, `kaiten_list_card_parents`, `kaiten_add_card_parent`, `kaiten_remove_card_parent`

### External Links (4 tools)
`kaiten_list_external_links`, `kaiten_create_external_link`, `kaiten_update_external_link`, `kaiten_delete_external_link`

### Subscribers & Subcolumns (10 tools)
`kaiten_list_card_subscribers`, `kaiten_add_card_subscriber`, `kaiten_remove_card_subscriber`, `kaiten_list_column_subscribers`, `kaiten_add_column_subscriber`, `kaiten_remove_column_subscriber`, `kaiten_list_subcolumns`, `kaiten_create_subcolumn`, `kaiten_update_subcolumn`, `kaiten_delete_subcolumn`

### Documents (10 tools)
`kaiten_list_documents`, `kaiten_create_document`, `kaiten_get_document`, `kaiten_update_document`, `kaiten_delete_document`, `kaiten_list_document_groups`, `kaiten_create_document_group`, `kaiten_get_document_group`, `kaiten_update_document_group`, `kaiten_delete_document_group`

### Webhooks (5 tools)
`kaiten_list_webhooks`, `kaiten_create_webhook`, `kaiten_get_webhook`, `kaiten_update_webhook`, `kaiten_delete_webhook`

### Automations & Workflows (10 tools)
`kaiten_list_automations`, `kaiten_create_automation`, `kaiten_get_automation`, `kaiten_update_automation`, `kaiten_delete_automation`, `kaiten_list_workflows`, `kaiten_create_workflow`, `kaiten_get_workflow`, `kaiten_update_workflow`, `kaiten_delete_workflow`

### Projects & Sprints (12 tools)
`kaiten_list_projects`, `kaiten_create_project`, `kaiten_get_project`, `kaiten_update_project`, `kaiten_delete_project`, `kaiten_list_project_cards`, `kaiten_add_project_card`, `kaiten_remove_project_card`, `kaiten_list_sprints`, `kaiten_create_sprint`, `kaiten_get_sprint`, `kaiten_update_sprint`, `kaiten_delete_sprint`

### Roles & Groups (14 tools)
`kaiten_list_space_users`, `kaiten_add_space_user`, `kaiten_update_space_user`, `kaiten_remove_space_user`, `kaiten_list_company_groups`, `kaiten_create_company_group`, `kaiten_get_company_group`, `kaiten_update_company_group`, `kaiten_delete_company_group`, `kaiten_list_group_users`, `kaiten_add_group_user`, `kaiten_remove_group_user`, `kaiten_list_roles`, `kaiten_get_role`

### Audit & Analytics (10 tools)
`kaiten_list_audit_logs`, `kaiten_get_card_activity`, `kaiten_get_space_activity`, `kaiten_get_company_activity`, `kaiten_get_card_location_history`, `kaiten_list_saved_filters`, `kaiten_create_saved_filter`, `kaiten_get_saved_filter`, `kaiten_update_saved_filter`, `kaiten_delete_saved_filter`

### Service Desk (14 tools)
`kaiten_list_sd_requests`, `kaiten_create_sd_request`, `kaiten_get_sd_request`, `kaiten_update_sd_request`, `kaiten_delete_sd_request`, `kaiten_list_sd_services`, `kaiten_get_sd_service`, `kaiten_list_sd_organizations`, `kaiten_create_sd_organization`, `kaiten_get_sd_organization`, `kaiten_update_sd_organization`, `kaiten_delete_sd_organization`, `kaiten_list_sd_sla`, `kaiten_get_sd_sla`

### Card Types & Custom Properties (7 tools)
`kaiten_list_card_types`, `kaiten_get_card_type`, `kaiten_create_card_type`, `kaiten_update_card_type`, `kaiten_delete_card_type`, `kaiten_list_custom_properties`, `kaiten_get_custom_property`, `kaiten_create_custom_property`, `kaiten_update_custom_property`, `kaiten_delete_custom_property`, `kaiten_list_select_values`, `kaiten_create_select_value`

### Utilities (14 tools)
`kaiten_list_api_keys`, `kaiten_create_api_key`, `kaiten_delete_api_key`, `kaiten_list_user_timers`, `kaiten_create_user_timer`, `kaiten_get_user_timer`, `kaiten_update_user_timer`, `kaiten_delete_user_timer`, `kaiten_list_removed_cards`, `kaiten_list_removed_boards`, `kaiten_list_calendars`, `kaiten_get_calendar`, `kaiten_get_company`, `kaiten_update_company`

## Usage Examples

Once registered, use the MCP tools directly. Here are common workflows:

### Get account overview
```
1. kaiten_get_current_user → who am I
2. kaiten_get_company → company info
3. kaiten_list_spaces → all spaces
4. For each space: kaiten_list_boards → boards
```

### Create a card
```
1. kaiten_list_spaces → find space_id
2. kaiten_list_boards(space_id) → find board_id
3. kaiten_list_columns(board_id) → find column_id for the right column
4. kaiten_create_card(title="My task", board_id=X, column_id=Y)
```

### Full project audit
```
1. kaiten_list_projects → all projects
2. kaiten_list_project_cards(project_id) → cards per project
3. kaiten_list_sprints → active sprints
4. kaiten_get_company_activity → recent company activity
5. kaiten_list_audit_logs → audit trail
```

### Manage card workflow
```
1. kaiten_get_card(card_id) → current state
2. kaiten_list_card_blockers(card_id) → check blockers
3. kaiten_list_card_children(card_id) → subtasks
4. kaiten_list_comments(card_id) → discussion
5. kaiten_move_card(card_id, column_id=NEW_COL) → advance card
```

## Important Notes

- **Rate limiting**: The server enforces ~4.5 req/s with automatic retry on 429 responses.
- **API key safety**: Never use `kaiten_delete_api_key` on your active token -- it will invalidate your session.
- **Some endpoints return 405**: Certain operations (get single webhook, delete sprint, list removed items) may not be available on all Kaiten plans. The tool descriptions note this.
- **ID types**: Most entities use numeric IDs. Documents, document groups, automations, and projects use UUID strings.

## Development

### Run tests (Docker only)
```bash
# Unit tests (100% coverage)
docker compose -f tests/docker-compose.test.yml up --build test-overseer

# E2E tests (requires KAITEN_DOMAIN and KAITEN_TOKEN in .env)
docker compose -f tests/docker-compose.test.yml up --build test-e2e-expanded
```

### Project structure
```
src/kaiten_mcp/
  server.py          # MCP server entry point
  client.py          # Async HTTP client with rate limiting
  models.py          # Enums and data models
  tools/             # 25 tool modules (119 tools total)
    spaces.py, boards.py, columns.py, lanes.py, cards.py,
    comments.py, checklists.py, blockers.py, card_relations.py,
    external_links.py, members.py, time_logs.py, tags.py,
    subscribers.py, webhooks.py, automations.py, projects.py,
    roles_and_groups.py, documents.py, audit_and_analytics.py,
    service_desk.py, utilities.py, custom_properties.py,
    card_types.py
```
