# Kaiten MCP Tools Reference (246 tools)

All tools use prefix `mcp__kaiten__kaiten_`. Load via `ToolSearch` before use.

## Response Optimization

**Default limit**: All list operations default to **50 items**. Use `limit` parameter to override (max 100).

**Compact mode**: Use `compact=true` on list operations to reduce response size by 80-95%:
- Removes base64-encoded `avatar_url` fields (10-50KB each)
- Simplifies user objects to `{id, full_name}`
- Simplifies user lists (members, responsibles) to `[{id, full_name}, ...]`

Supported: `list_cards`, `list_all_cards`, `list_users`, `list_spaces`, `list_boards`, `list_comments`, `list_card_members`, `list_card_subscribers`, `list_column_subscribers`, `list_space_users`, `list_group_users`, `list_project_cards`

---

## Spaces (5 tools)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_spaces` | List all spaces | `compact` |
| `kaiten_get_space` | Get space by ID | **`space_id`** |
| `kaiten_create_space` | Create a new space | **`title`**, `parent_entity_uid`, `access` |
| `kaiten_update_space` | Update a space | **`space_id`**, `title`, `parent_entity_uid` |
| `kaiten_delete_space` | Delete a space | **`space_id`** |

## Boards (5 tools)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_boards` | List boards in a space | **`space_id`**, `compact` |
| `kaiten_get_board` | Get board by ID (with columns and lanes) | **`board_id`** |
| `kaiten_create_board` | Create board in a space | **`space_id`**, **`title`** |
| `kaiten_update_board` | Update a board | **`space_id`**, **`board_id`** |
| `kaiten_delete_board` | Delete a board | **`space_id`**, **`board_id`** |

## Columns (8 tools)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_columns` | List columns on a board (type: 1=queue, 2=in_progress, 3=done) | **`board_id`** |
| `kaiten_create_column` | Create a column | **`board_id`**, **`title`**, **`type`** (1/2/3) |
| `kaiten_update_column` | Update a column | **`board_id`**, **`column_id`** |
| `kaiten_delete_column` | Delete a column | **`board_id`**, **`column_id`** |
| `kaiten_list_subcolumns` | List subcolumns of a column | **`column_id`** |
| `kaiten_create_subcolumn` | Create a subcolumn | **`column_id`**, **`title`** |
| `kaiten_update_subcolumn` | Update a subcolumn | **`column_id`**, **`subcolumn_id`** |
| `kaiten_delete_subcolumn` | Delete a subcolumn | **`column_id`**, **`subcolumn_id`** |

## Lanes (4 tools)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_lanes` | List lanes (swimlanes) on a board | **`board_id`** |
| `kaiten_create_lane` | Create a lane | **`board_id`**, **`title`** |
| `kaiten_update_lane` | Update a lane | **`board_id`**, **`lane_id`** |
| `kaiten_delete_lane` | Delete a lane | **`board_id`**, **`lane_id`** |

## Cards (8 tools)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_cards` | Search/list cards with filtering (default limit=50) | `query`, `board_id`, `space_id`, `compact` |
| `kaiten_get_card` | Get card by ID or key (e.g. PROJ-123) | **`card_id`** |
| `kaiten_create_card` | Create a card (title max 1024, description max 32768) | **`title`**, **`board_id`**, `column_id`, `lane_id` |
| `kaiten_update_card` | Update card fields; use condition=2 to archive | **`card_id`** |
| `kaiten_delete_card` | Soft-delete a card (cards with time logs cannot be deleted) | **`card_id`** |
| `kaiten_archive_card` | Archive a card (sets condition=2) | **`card_id`** |
| `kaiten_move_card` | Move card to different board/column/lane | **`card_id`**, `board_id`, `column_id`, `lane_id` |
| `kaiten_list_all_cards` | Fetch ALL cards with auto-pagination (max 5000) | `board_id`, `space_id`, `compact`, `page_size`, `max_pages` |

## Tags (6 tools)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_tags` | List tags (filterable by query, space, IDs) | `query`, `space_id`, `ids` |
| `kaiten_create_tag` | Create a tag (color assigned randomly) | **`name`** |
| `kaiten_update_tag` | Update tag name/color (company permission) | **`tag_id`**, `name`, `color` |
| `kaiten_delete_tag` | Delete a tag (company permission) | **`tag_id`** |
| `kaiten_add_card_tag` | Add tag to card by name (auto-creates if new) | **`card_id`**, **`name`** |
| `kaiten_remove_card_tag` | Remove tag from card | **`card_id`**, **`tag_id`** |

## Card Types (5 tools)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_card_types` | List all card types in company | `query` |
| `kaiten_get_card_type` | Get card type by ID | **`type_id`** |
| `kaiten_create_card_type` | Create card type (color 2-25) | **`name`**, **`letter`**, **`color`** |
| `kaiten_update_card_type` | Update card type | **`type_id`** |
| `kaiten_delete_card_type` | Delete card type | **`type_id`** |

## Custom Properties (10 tools)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_custom_properties` | List company custom properties | `types`, `board_id`, `include_values` |
| `kaiten_get_custom_property` | Get property by ID | **`property_id`** |
| `kaiten_create_custom_property` | Create custom property | **`name`**, **`type`** (string/number/date/select/...) |
| `kaiten_update_custom_property` | Update property | **`property_id`** |
| `kaiten_delete_custom_property` | Soft-delete property | **`property_id`** |
| `kaiten_list_select_values` | List values for select-type property | **`property_id`**, `query` |
| `kaiten_get_select_value` | Get a single select value | **`property_id`**, **`value_id`** |
| `kaiten_create_select_value` | Add value to select property | **`property_id`**, **`value`** |
| `kaiten_update_select_value` | Update select value | **`property_id`**, **`value_id`** |
| `kaiten_delete_select_value` | Soft-delete select value | **`property_id`**, **`value_id`** |

## Comments (4 tools)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_comments` | List comments on a card | **`card_id`**, `compact` |
| `kaiten_create_comment` | Add comment (markdown or html format) | **`card_id`**, **`text`**, `format`, `internal` |
| `kaiten_update_comment` | Update comment (author only) | **`card_id`**, **`comment_id`**, **`text`** |
| `kaiten_delete_comment` | Delete comment (author only) | **`card_id`**, **`comment_id`** |

## Members (5 tools)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_users` | List company users with search/pagination | `query`, `include_inactive`, `compact` |
| `kaiten_get_current_user` | Get authenticated user profile | (none) |
| `kaiten_list_card_members` | List members assigned to a card | **`card_id`**, `compact` |
| `kaiten_add_card_member` | Add member to card | **`card_id`**, **`user_id`** |
| `kaiten_remove_card_member` | Remove member from card | **`card_id`**, **`user_id`** |

## Time Logs (4 tools)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_card_time_logs` | List time logs on a card | **`card_id`**, `for_date`, `personal` |
| `kaiten_create_time_log` | Log time on card (minutes) | **`card_id`**, **`time_spent`**, `role_id`, `for_date` |
| `kaiten_update_time_log` | Update time log (author only) | **`card_id`**, **`time_log_id`** |
| `kaiten_delete_time_log` | Delete time log (author only) | **`card_id`**, **`time_log_id`** |

## Checklists (8 tools)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_checklists` | List checklists on a card | **`card_id`** |
| `kaiten_create_checklist` | Create checklist on card | **`card_id`**, **`name`** |
| `kaiten_update_checklist` | Update checklist | **`card_id`**, **`checklist_id`** |
| `kaiten_delete_checklist` | Delete checklist | **`card_id`**, **`checklist_id`** |
| `kaiten_list_checklist_items` | List items in checklist | **`card_id`**, **`checklist_id`** |
| `kaiten_create_checklist_item` | Create checklist item | **`card_id`**, **`checklist_id`**, **`text`** |
| `kaiten_update_checklist_item` | Update item (toggle checked, text, due_date) | **`card_id`**, **`checklist_id`**, **`item_id`** |
| `kaiten_delete_checklist_item` | Delete checklist item | **`card_id`**, **`checklist_id`**, **`item_id`** |

## Blockers (5 tools)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_card_blockers` | List blockers on a card | **`card_id`** |
| `kaiten_create_card_blocker` | Create blocker (text reason or card link) | **`card_id`**, `reason`, `blocker_card_id` |
| `kaiten_get_card_blocker` | Get specific blocker | **`card_id`**, **`blocker_id`** |
| `kaiten_update_card_blocker` | Update blocker reason | **`card_id`**, **`blocker_id`** |
| `kaiten_delete_card_blocker` | Delete blocker | **`card_id`**, **`blocker_id`** |

## Card Relations (9 tools)

### Parent/Child

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_card_children` | List child cards | **`card_id`** |
| `kaiten_add_card_child` | Add child card | **`card_id`**, **`child_card_id`** |
| `kaiten_remove_card_child` | Remove child relationship | **`card_id`**, **`child_id`** |
| `kaiten_list_card_parents` | List parent cards | **`card_id`** |
| `kaiten_add_card_parent` | Add parent card | **`card_id`**, **`parent_card_id`** |
| `kaiten_remove_card_parent` | Remove parent relationship | **`card_id`**, **`parent_id`** |

### Planned Relations (Timeline/Gantt)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_add_planned_relation` | Create successor link between cards (finish-to-start) | **`card_id`**, **`target_card_id`**, `type` |
| `kaiten_update_planned_relation` | Update gap/lag of a planned relation | **`card_id`**, **`target_card_id`**, **`gap`**, **`gap_type`** |
| `kaiten_remove_planned_relation` | Remove planned relation | **`card_id`**, **`target_card_id`** |

## External Links (4 tools)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_external_links` | List external links on card | **`card_id`** |
| `kaiten_create_external_link` | Add link to card | **`card_id`**, **`url`** |
| `kaiten_update_external_link` | Update link | **`card_id`**, **`link_id`** |
| `kaiten_delete_external_link` | Delete link | **`card_id`**, **`link_id`** |

## Files (4 tools)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_card_files` | List file attachments on a card | **`card_id`** |
| `kaiten_create_card_file` | Create file attachment by URL (type: 1=attachment, 2=googleDrive, ...) | **`card_id`**, **`url`**, **`name`** |
| `kaiten_update_card_file` | Update file attachment | **`card_id`**, **`file_id`** |
| `kaiten_delete_card_file` | Delete file attachment | **`card_id`**, **`file_id`** |

## Documents (10 tools)

### Documents

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_documents` | List documents | `query`, `limit` |
| `kaiten_create_document` | Create document (`text` for markdown, `data` for ProseMirror) | **`title`**, `text`, `data`, `parent_entity_uid` |
| `kaiten_get_document` | Get document by UID | **`document_uid`** |
| `kaiten_update_document` | Update document content/title | **`document_uid`**, `text`, `data` |
| `kaiten_delete_document` | Delete document | **`document_uid`** |

### Document Groups

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_document_groups` | List document groups (folders) | `query`, `limit` |
| `kaiten_create_document_group` | Create group | **`title`**, `parent_entity_uid` |
| `kaiten_get_document_group` | Get group by UID | **`group_uid`** |
| `kaiten_update_document_group` | Update group | **`group_uid`** |
| `kaiten_delete_document_group` | Delete group | **`group_uid`** |

## Webhooks (9 tools)

### External Webhooks (outbound event notifications)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_webhooks` | List external webhooks for a space (1 per space) | **`space_id`** |
| `kaiten_create_webhook` | Create external webhook (paid feature) | **`space_id`**, **`url`** |
| `kaiten_get_webhook` | Get external webhook by ID | **`space_id`**, **`webhook_id`** |
| `kaiten_update_webhook` | Update external webhook (URL, enabled) | **`space_id`**, **`webhook_id`** |
| `kaiten_delete_webhook` | Delete external webhook | **`space_id`**, **`webhook_id`** |

### Incoming Webhooks (card-creation)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_incoming_webhooks` | List incoming webhooks for a space | **`space_id`** |
| `kaiten_create_incoming_webhook` | Create incoming webhook (paid feature) | **`space_id`**, **`board_id`**, **`column_id`**, **`lane_id`**, **`owner_id`** |
| `kaiten_update_incoming_webhook` | Update incoming webhook | **`space_id`**, **`webhook_id`** |
| `kaiten_delete_incoming_webhook` | Delete incoming webhook | **`space_id`**, **`webhook_id`** |

## Automations (11 tools)

### Space Automations

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_automations` | List automations for a space | **`space_id`** |
| `kaiten_create_automation` | Create automation (trigger + actions) | **`space_id`**, **`name`**, **`trigger`**, **`actions`** |
| `kaiten_get_automation` | Get automation by ID | **`space_id`**, **`automation_id`** |
| `kaiten_update_automation` | Update automation | **`space_id`**, **`automation_id`** |
| `kaiten_delete_automation` | Delete automation | **`space_id`**, **`automation_id`** |
| `kaiten_copy_automation` | Copy automation to another space | **`space_id`**, **`automation_id`**, **`target_space_id`** |

### Company Workflows

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_workflows` | List company workflows | `limit`, `offset` |
| `kaiten_create_workflow` | Create workflow (min 2 stages, 1 transition) | **`name`**, **`stages`**, **`transitions`** |
| `kaiten_get_workflow` | Get workflow by ID | **`workflow_id`** |
| `kaiten_update_workflow` | Update workflow | **`workflow_id`** |
| `kaiten_delete_workflow` | Delete workflow | **`workflow_id`** |

## Projects (13 tools)

### Projects

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_projects` | List all projects | (none) |
| `kaiten_create_project` | Create project | **`title`** |
| `kaiten_get_project` | Get project by UUID | **`project_id`**, `with_cards_data` |
| `kaiten_update_project` | Update project | **`project_id`** |
| `kaiten_delete_project` | Delete project | **`project_id`** |
| `kaiten_list_project_cards` | List cards in project | **`project_id`**, `compact` |
| `kaiten_add_project_card` | Add card to project | **`project_id`**, **`card_id`** |
| `kaiten_remove_project_card` | Remove card from project | **`project_id`**, **`card_id`** |

### Sprints

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_sprints` | List sprints | `active`, `limit` |
| `kaiten_create_sprint` | Create sprint | **`title`**, **`board_id`**, `start_date`, `finish_date` |
| `kaiten_get_sprint` | Get sprint by ID (with card summary) | **`sprint_id`** |
| `kaiten_update_sprint` | Update sprint (set active=false to finish) | **`sprint_id`** |
| `kaiten_delete_sprint` | Delete sprint (may return 405) | **`sprint_id`** |

## Roles & Groups (14 tools)

### Roles

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_roles` | List available roles | `query`, `limit` |
| `kaiten_get_role` | Get role by ID | **`role_id`** |

### Company Groups

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_company_groups` | List company groups | `query`, `limit` |
| `kaiten_create_company_group` | Create group | **`name`** |
| `kaiten_get_company_group` | Get group by UID | **`group_uid`** |
| `kaiten_update_company_group` | Update group | **`group_uid`** |
| `kaiten_delete_company_group` | Delete group | **`group_uid`** |
| `kaiten_list_group_users` | List users in group | **`group_uid`**, `compact` |
| `kaiten_add_group_user` | Add user to group | **`group_uid`**, **`user_id`** |
| `kaiten_remove_group_user` | Remove user from group | **`group_uid`**, **`user_id`** |

### Space Users

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_space_users` | List space users | **`space_id`**, `compact` |
| `kaiten_add_space_user` | Add user to space | **`space_id`**, **`user_id`**, `role_id` |
| `kaiten_update_space_user` | Update user role in space | **`space_id`**, **`user_id`** |
| `kaiten_remove_space_user` | Remove user from space | **`space_id`**, **`user_id`** |

## Audit & Analytics (11 tools)

### Audit Logs & Activity

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_audit_logs` | List company audit logs | `categories`, `actions`, `from`, `to` |
| `kaiten_get_card_activity` | Get card activity feed | **`card_id`** |
| `kaiten_get_space_activity` | Get space activity feed (filter by actions, dates) | **`space_id`**, `actions`, `created_after` |
| `kaiten_get_company_activity` | Get company-wide activity (cursor pagination) | `actions`, `cursor_created`, `cursor_id` |
| `kaiten_get_card_location_history` | Get card movement history (column/lane moves) | **`card_id`** |
| `kaiten_get_all_space_activity` | Fetch ALL space activity with auto-pagination (max 5000) | **`space_id`**, `actions`, `page_size`, `max_pages` |

### Saved Filters

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_saved_filters` | List saved filters | `limit` |
| `kaiten_create_saved_filter` | Create saved filter | **`name`**, **`filter`** |
| `kaiten_get_saved_filter` | Get filter by ID | **`filter_id`** |
| `kaiten_update_saved_filter` | Update filter | **`filter_id`** |
| `kaiten_delete_saved_filter` | Delete filter | **`filter_id`** |

## Subscribers (6 tools)

### Card Subscribers

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_card_subscribers` | List card subscribers (watchers) | **`card_id`**, `compact` |
| `kaiten_add_card_subscriber` | Subscribe user to card | **`card_id`**, **`user_id`** |
| `kaiten_remove_card_subscriber` | Unsubscribe user from card | **`card_id`**, **`user_id`** |

### Column Subscribers

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_column_subscribers` | List column subscribers | **`column_id`**, `compact` |
| `kaiten_add_column_subscriber` | Subscribe user to column | **`column_id`**, **`user_id`**, `type` |
| `kaiten_remove_column_subscriber` | Unsubscribe user from column | **`column_id`**, **`user_id`** |

## Service Desk (47 tools)

### Requests

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_sd_requests` | List SD requests | `query`, `limit` |
| `kaiten_create_sd_request` | Create SD request | **`title`**, **`service_id`** |
| `kaiten_get_sd_request` | Get request by ID | **`request_id`** |
| `kaiten_update_sd_request` | Update request | **`request_id`** |
| `kaiten_delete_sd_request` | Delete request | **`request_id`** |

### Services

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_sd_services` | List SD services | `query`, `include_archived` |
| `kaiten_get_sd_service` | Get service by ID | **`service_id`** |
| `kaiten_create_sd_service` | Create SD service | **`name`**, **`board_id`**, **`position`** |
| `kaiten_update_sd_service` | Update SD service | **`service_id`** |
| `kaiten_delete_sd_service` | Archive SD service | **`service_id`** |

### Organizations

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_sd_organizations` | List SD organizations | `query`, `includeUsers` |
| `kaiten_create_sd_organization` | Create organization | **`name`** |
| `kaiten_get_sd_organization` | Get organization by ID | **`organization_id`** |
| `kaiten_update_sd_organization` | Update organization | **`organization_id`** |
| `kaiten_delete_sd_organization` | Delete organization | **`organization_id`** |

### SLA Policies

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_sd_sla` | List SLA policies | `limit` |
| `kaiten_get_sd_sla` | Get SLA policy by ID | **`sla_id`** |
| `kaiten_create_sd_sla` | Create SLA policy | **`name`**, **`rules`** |
| `kaiten_update_sd_sla` | Update SLA policy | **`sla_id`** |
| `kaiten_delete_sd_sla` | Delete SLA policy | **`sla_id`** |

### Template Answers

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_sd_template_answers` | List template answers | (none) |
| `kaiten_get_sd_template_answer` | Get template answer by ID | **`template_answer_id`** |
| `kaiten_create_sd_template_answer` | Create template answer | **`name`**, **`text`** |
| `kaiten_update_sd_template_answer` | Update template answer | **`template_answer_id`** |
| `kaiten_delete_sd_template_answer` | Delete template answer | **`template_answer_id`** |

### SLA Rules

| Tool | Description | Key params |
|---|---|---|
| `kaiten_create_sla_rule` | Create rule within SLA policy | **`sla_id`**, `type`, `estimated_time` |
| `kaiten_update_sla_rule` | Update SLA rule | **`sla_id`**, **`rule_id`** |
| `kaiten_delete_sla_rule` | Delete SLA rule | **`sla_id`**, **`rule_id`** |

### SLA Recalculate

| Tool | Description | Key params |
|---|---|---|
| `kaiten_recalculate_sla` | Trigger async SLA measurement recalculation | **`sla_id`** |

### SD Users

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_sd_users` | List SD users | `query`, `include_paid_users` |
| `kaiten_update_sd_user` | Update SD user profile | **`user_id`**, `full_name`, `lng` |
| `kaiten_set_sd_user_temp_password` | Generate temporary password for SD user | **`user_id`** |

### Organization Users

| Tool | Description | Key params |
|---|---|---|
| `kaiten_add_sd_org_user` | Add user to SD organization | **`organization_id`**, **`user_id`** |
| `kaiten_update_sd_org_user` | Update user permissions in organization | **`organization_id`**, **`user_id`** |
| `kaiten_remove_sd_org_user` | Remove user from organization | **`organization_id`**, **`user_id`** |
| `kaiten_batch_add_sd_org_users` | Batch add users to organization | **`organization_id`**, **`user_ids`** |
| `kaiten_batch_remove_sd_org_users` | Batch remove users from organization | **`organization_id`**, **`user_ids`** |

### SD Settings

| Tool | Description | Key params |
|---|---|---|
| `kaiten_get_sd_settings` | Get current SD settings | (none) |
| `kaiten_update_sd_settings` | Update SD settings | **`service_desk_settings`** |

### SD Statistics

| Tool | Description | Key params |
|---|---|---|
| `kaiten_get_sd_stats` | Get SD statistics | `date_from`, `date_to`, `service_id` |
| `kaiten_get_sd_sla_stats` | Get SD SLA statistics (async, returns compute_job_id) | `date_from`, `date_to`, `sla_id` |

### Vote Properties

| Tool | Description | Key params |
|---|---|---|
| `kaiten_add_service_vote_property` | Add vote property to SD service | **`service_id`**, **`id`** |
| `kaiten_remove_service_vote_property` | Remove vote property from SD service | **`service_id`**, **`property_id`** |

### Card SLAs

| Tool | Description | Key params |
|---|---|---|
| `kaiten_attach_card_sla` | Attach SLA policy to card | **`card_id`**, **`sla_id`** |
| `kaiten_detach_card_sla` | Detach SLA policy from card | **`card_id`**, **`sla_id`** |

### SLA Measurements

| Tool | Description | Key params |
|---|---|---|
| `kaiten_get_card_sla_measurements` | Get SLA measurements for a card | **`card_id`** |
| `kaiten_get_space_sla_measurements` | Get SLA measurements for all cards in space | **`space_id`** |

## Utilities (14 tools)

### API Keys

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_api_keys` | List API keys for current user | (none) |
| `kaiten_create_api_key` | Create new API key | **`name`** |
| `kaiten_delete_api_key` | Delete API key (NEVER delete active token!) | **`key_id`** |

### User Timers

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_user_timers` | List all active user timers | (none) |
| `kaiten_create_user_timer` | Start timer for a card | **`card_id`** |
| `kaiten_get_user_timer` | Get timer by ID | **`timer_id`** |
| `kaiten_update_user_timer` | Update timer (pause/resume) | **`timer_id`**, `paused` |
| `kaiten_delete_user_timer` | Stop/delete timer | **`timer_id`** |

### Recycle Bin

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_removed_cards` | List deleted cards (may return 405) | `limit` |
| `kaiten_list_removed_boards` | List deleted boards (may return 405) | `limit` |

### Calendars

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_calendars` | List calendars | `limit` |
| `kaiten_get_calendar` | Get calendar by UUID | **`calendar_id`** |

### Company

| Tool | Description | Key params |
|---|---|---|
| `kaiten_get_company` | Get current company info | (none) |
| `kaiten_update_company` | Update company name | `name` |

## Tree (2 tools)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_list_children` | List direct children of an entity (omit `parent_entity_uid` for roots) | `parent_entity_uid` |
| `kaiten_get_tree` | Build nested entity tree (spaces, docs, groups) | `root_uid`, `depth` |

## Charts (15 tools)

### Synchronous Charts

| Tool | Description | Key params |
|---|---|---|
| `kaiten_get_chart_boards` | Get board structure for chart configuration | **`space_id`** |
| `kaiten_chart_summary` | Get done-card summary for date range | **`space_id`**, **`date_from`**, **`date_to`**, **`done_columns`** |
| `kaiten_chart_block_resolution` | Get blocker resolution time data | **`space_id`**, `category_ids` |
| `kaiten_chart_due_dates` | Get due dates analysis (cards + checklist items) | **`space_id`**, **`card_date_from`**, **`card_date_to`**, **`checklist_item_date_from`**, **`checklist_item_date_to`** |

### Asynchronous Charts (return compute_job_id)

| Tool | Description | Key params |
|---|---|---|
| `kaiten_chart_cfd` | Cumulative Flow Diagram | **`space_id`**, **`date_from`**, **`date_to`** |
| `kaiten_chart_control` | Control Chart (cycle time per card) | **`space_id`**, **`date_from`**, **`date_to`**, **`start_columns`**, **`end_columns`**, **`start_column_lanes`**, **`end_column_lanes`** |
| `kaiten_chart_spectral` | Spectral Chart (cycle time distribution) | **`space_id`**, **`date_from`**, **`date_to`**, **`start_columns`**, **`end_columns`**, **`start_column_lanes`**, **`end_column_lanes`** |
| `kaiten_chart_lead_time` | Lead Time Chart | **`space_id`**, **`date_from`**, **`date_to`**, **`start_columns`**, **`end_columns`**, **`start_column_lanes`**, **`end_column_lanes`** |
| `kaiten_chart_throughput_capacity` | Throughput Capacity Chart | **`space_id`**, **`date_from`**, **`end_column`** |
| `kaiten_chart_throughput_demand` | Throughput Demand Chart | **`space_id`**, **`date_from`**, **`start_column`** |
| `kaiten_chart_task_distribution` | Task Distribution Chart | **`space_id`** |
| `kaiten_chart_cycle_time` | Cycle Time Chart | **`space_id`**, **`date_from`**, **`date_to`**, **`start_column`**, **`end_column`** |
| `kaiten_chart_sales_funnel` | Sales Funnel Chart | **`space_id`**, **`date_from`**, **`date_to`**, **`board_configs`** |

### Compute Jobs

| Tool | Description | Key params |
|---|---|---|
| `kaiten_get_compute_job` | Poll async chart job status/result (queued/processing/done/failed) | **`job_id`** |
| `kaiten_cancel_compute_job` | Cancel running/queued compute job | **`job_id`** |

---

## Quick Reference (all 246 tools, alphabetical)

```
kaiten_add_card_child
kaiten_add_card_member
kaiten_add_card_parent
kaiten_add_card_subscriber
kaiten_add_card_tag
kaiten_add_column_subscriber
kaiten_add_group_user
kaiten_add_planned_relation
kaiten_add_project_card
kaiten_add_sd_org_user
kaiten_add_service_vote_property
kaiten_add_space_user
kaiten_archive_card
kaiten_attach_card_sla
kaiten_batch_add_sd_org_users
kaiten_batch_remove_sd_org_users
kaiten_cancel_compute_job
kaiten_chart_block_resolution
kaiten_chart_cfd
kaiten_chart_control
kaiten_chart_cycle_time
kaiten_chart_due_dates
kaiten_chart_lead_time
kaiten_chart_sales_funnel
kaiten_chart_spectral
kaiten_chart_summary
kaiten_chart_task_distribution
kaiten_chart_throughput_capacity
kaiten_chart_throughput_demand
kaiten_copy_automation
kaiten_create_api_key
kaiten_create_automation
kaiten_create_board
kaiten_create_card
kaiten_create_card_blocker
kaiten_create_card_file
kaiten_create_card_type
kaiten_create_checklist
kaiten_create_checklist_item
kaiten_create_column
kaiten_create_comment
kaiten_create_company_group
kaiten_create_custom_property
kaiten_create_document
kaiten_create_document_group
kaiten_create_external_link
kaiten_create_incoming_webhook
kaiten_create_lane
kaiten_create_project
kaiten_create_saved_filter
kaiten_create_sd_organization
kaiten_create_sd_request
kaiten_create_sd_service
kaiten_create_sd_sla
kaiten_create_sd_template_answer
kaiten_create_select_value
kaiten_create_sla_rule
kaiten_create_space
kaiten_create_sprint
kaiten_create_subcolumn
kaiten_create_tag
kaiten_create_time_log
kaiten_create_user_timer
kaiten_create_webhook
kaiten_create_workflow
kaiten_delete_api_key
kaiten_delete_automation
kaiten_delete_board
kaiten_delete_card
kaiten_delete_card_blocker
kaiten_delete_card_file
kaiten_delete_card_type
kaiten_delete_checklist
kaiten_delete_checklist_item
kaiten_delete_column
kaiten_delete_comment
kaiten_delete_company_group
kaiten_delete_custom_property
kaiten_delete_document
kaiten_delete_document_group
kaiten_delete_external_link
kaiten_delete_incoming_webhook
kaiten_delete_lane
kaiten_delete_project
kaiten_delete_saved_filter
kaiten_delete_sd_organization
kaiten_delete_sd_request
kaiten_delete_sd_service
kaiten_delete_sd_sla
kaiten_delete_sd_template_answer
kaiten_delete_select_value
kaiten_delete_sla_rule
kaiten_delete_space
kaiten_delete_sprint
kaiten_delete_subcolumn
kaiten_delete_tag
kaiten_delete_time_log
kaiten_delete_user_timer
kaiten_delete_webhook
kaiten_delete_workflow
kaiten_detach_card_sla
kaiten_get_all_space_activity
kaiten_get_automation
kaiten_get_board
kaiten_get_calendar
kaiten_get_card
kaiten_get_card_activity
kaiten_get_card_blocker
kaiten_get_card_location_history
kaiten_get_card_sla_measurements
kaiten_get_card_type
kaiten_get_chart_boards
kaiten_get_company
kaiten_get_company_activity
kaiten_get_company_group
kaiten_get_compute_job
kaiten_get_current_user
kaiten_get_custom_property
kaiten_get_document
kaiten_get_document_group
kaiten_get_project
kaiten_get_role
kaiten_get_saved_filter
kaiten_get_sd_organization
kaiten_get_sd_request
kaiten_get_sd_service
kaiten_get_sd_settings
kaiten_get_sd_sla
kaiten_get_sd_sla_stats
kaiten_get_sd_stats
kaiten_get_sd_template_answer
kaiten_get_select_value
kaiten_get_space
kaiten_get_space_activity
kaiten_get_space_sla_measurements
kaiten_get_sprint
kaiten_get_tree
kaiten_get_user_timer
kaiten_get_webhook
kaiten_get_workflow
kaiten_list_all_cards
kaiten_list_api_keys
kaiten_list_audit_logs
kaiten_list_automations
kaiten_list_boards
kaiten_list_calendars
kaiten_list_card_blockers
kaiten_list_card_children
kaiten_list_card_files
kaiten_list_card_members
kaiten_list_card_parents
kaiten_list_card_subscribers
kaiten_list_card_time_logs
kaiten_list_card_types
kaiten_list_cards
kaiten_list_checklist_items
kaiten_list_checklists
kaiten_list_children
kaiten_list_column_subscribers
kaiten_list_columns
kaiten_list_comments
kaiten_list_company_groups
kaiten_list_custom_properties
kaiten_list_document_groups
kaiten_list_documents
kaiten_list_external_links
kaiten_list_group_users
kaiten_list_incoming_webhooks
kaiten_list_lanes
kaiten_list_projects
kaiten_list_project_cards
kaiten_list_removed_boards
kaiten_list_removed_cards
kaiten_list_roles
kaiten_list_saved_filters
kaiten_list_sd_organizations
kaiten_list_sd_requests
kaiten_list_sd_services
kaiten_list_sd_sla
kaiten_list_sd_template_answers
kaiten_list_sd_users
kaiten_list_select_values
kaiten_list_space_users
kaiten_list_spaces
kaiten_list_sprints
kaiten_list_subcolumns
kaiten_list_tags
kaiten_list_user_timers
kaiten_list_users
kaiten_list_webhooks
kaiten_list_workflows
kaiten_move_card
kaiten_recalculate_sla
kaiten_remove_card_child
kaiten_remove_card_member
kaiten_remove_card_parent
kaiten_remove_card_subscriber
kaiten_remove_card_tag
kaiten_remove_column_subscriber
kaiten_remove_group_user
kaiten_remove_planned_relation
kaiten_remove_project_card
kaiten_remove_sd_org_user
kaiten_remove_service_vote_property
kaiten_remove_space_user
kaiten_set_sd_user_temp_password
kaiten_update_automation
kaiten_update_board
kaiten_update_card
kaiten_update_card_blocker
kaiten_update_card_file
kaiten_update_card_type
kaiten_update_checklist
kaiten_update_checklist_item
kaiten_update_column
kaiten_update_comment
kaiten_update_company
kaiten_update_company_group
kaiten_update_custom_property
kaiten_update_document
kaiten_update_document_group
kaiten_update_external_link
kaiten_update_incoming_webhook
kaiten_update_lane
kaiten_update_planned_relation
kaiten_update_project
kaiten_update_saved_filter
kaiten_update_sd_org_user
kaiten_update_sd_organization
kaiten_update_sd_request
kaiten_update_sd_service
kaiten_update_sd_settings
kaiten_update_sd_sla
kaiten_update_sd_template_answer
kaiten_update_sd_user
kaiten_update_select_value
kaiten_update_sla_rule
kaiten_update_space
kaiten_update_space_user
kaiten_update_sprint
kaiten_update_subcolumn
kaiten_update_tag
kaiten_update_time_log
kaiten_update_user_timer
kaiten_update_webhook
kaiten_update_workflow
```
