# Kaiten MCP Tools Reference

All tools use prefix `mcp__kaiten__kaiten_`. Load via `ToolSearch` before use.

## Spaces
| Tool | Description |
|---|---|
| list_spaces | List all spaces (supports `archived` filter) |
| get_space | Get space by ID |
| create_space | Create space (`title`, optional `parent_id` for nesting) |
| update_space | Update space properties |
| delete_space | Delete a space |

## Boards
| Tool | Description |
|---|---|
| list_boards | List boards (filter by `space_id`) |
| get_board | Get board by ID |
| create_board | Create board in a space |
| update_board | Update board |
| delete_board | Delete board |

## Columns
| Tool | Description |
|---|---|
| list_columns | List columns on a board |
| create_column | Create column (`board_id`, `title`, `type`: 1=queue/2=in_progress/3=done) |
| update_column | Update column |
| delete_column | Delete column |

## Lanes
| Tool | Description |
|---|---|
| list_lanes | List lanes on a board |
| create_lane | Create lane (`board_id`, `title`) |
| update_lane | Update lane |
| delete_lane | Delete lane |

## Cards
| Tool | Description |
|---|---|
| list_cards | List cards (filter: `space_id`, `board_id`, `condition`, `state`) |
| get_card | Get card by ID |
| create_card | Create card (required: `title`, `board_id`, `column_id`) |
| update_card | Update card fields |
| delete_card | Delete card |
| archive_card | Archive a card |
| move_card | Move card to different column/lane/board |

**Key card fields**: `title`, `board_id`, `column_id`, `lane_id`, `type_id`, `owner_id`, `planned_start`, `planned_end`, `size_text`, `due_date`, `asap`, `description`

## Card Relations (Parent/Child)
| Tool | Description |
|---|---|
| list_card_children | List children of a card |
| add_card_child | Add child card (`card_id`, `child_card_id`) |
| remove_card_child | Remove child relationship |
| list_card_parents | List parents of a card |
| add_card_parent | Add parent card |
| remove_card_parent | Remove parent relationship |

## Card Types
| Tool | Description |
|---|---|
| list_card_types | List all card types in company |
| get_card_type | Get type by ID |
| create_card_type | Create new type (`name`, `color`, `letter`) |
| update_card_type | Update type |
| delete_card_type | Delete type |

## Custom Properties
| Tool | Description |
|---|---|
| list_custom_properties | List custom properties |
| get_custom_property | Get property by ID |
| create_custom_property | Create custom property |
| update_custom_property | Update property |
| delete_custom_property | Delete property |
| list_select_values | List values for select-type properties |
| create_select_value | Add value to select property |

## Members & Users
| Tool | Description |
|---|---|
| list_users | List all users in company |
| get_current_user | Get authenticated user info |
| list_card_members | List members of a card |
| add_card_member | Add member to card (`card_id`, `user_id`) |
| remove_card_member | Remove member from card |

## Tags
| Tool | Description |
|---|---|
| list_tags | List all tags |
| create_tag | Create tag |
| delete_tag | Delete tag |
| add_card_tag | Add tag to card |
| remove_card_tag | Remove tag from card |

## Comments
| Tool | Description |
|---|---|
| list_comments | List comments on a card |
| create_comment | Add comment to card |
| update_comment | Update comment |
| delete_comment | Delete comment |

## Checklists
| Tool | Description |
|---|---|
| list_checklists | List checklists on a card |
| create_checklist | Create checklist on card |
| update_checklist | Update checklist |
| delete_checklist | Delete checklist |
| list_checklist_items | List items in checklist |
| create_checklist_item | Add item to checklist |
| update_checklist_item | Update item (toggle complete) |
| delete_checklist_item | Delete item |

## Documents & Groups
| Tool | Description |
|---|---|
| list_documents | List documents |
| create_document | Create document (`title`, `sort_order` REQUIRED) |
| get_document | Get document by UID |
| update_document | Update document (`document_uid`, `data` as ProseMirror JSON) |
| delete_document | Delete document |
| list_document_groups | List document groups (folders) |
| create_document_group | Create group (`title`, `sort_order` REQUIRED) |
| get_document_group | Get group by UID |
| update_document_group | Update group |
| delete_document_group | Delete group |

## Time Logs
| Tool | Description |
|---|---|
| list_card_time_logs | List time logs on a card |
| create_time_log | Log time on card |
| update_time_log | Update time log |
| delete_time_log | Delete time log |

## Blockers
| Tool | Description |
|---|---|
| list_card_blockers | List blockers on a card |
| create_card_blocker | Create blocker |
| get_card_blocker | Get blocker by ID |
| update_card_blocker | Update blocker |
| delete_card_blocker | Delete blocker |

## External Links
| Tool | Description |
|---|---|
| list_external_links | List external links on card |
| create_external_link | Add link to card |
| update_external_link | Update link |
| delete_external_link | Delete link |

## Projects & Sprints
| Tool | Description |
|---|---|
| list_projects | List projects |
| create_project | Create project |
| get_project | Get project by ID |
| update_project | Update project |
| delete_project | Delete project |
| list_project_cards | List cards in project |
| add_project_card | Add card to project |
| remove_project_card | Remove card from project |
| list_sprints | List sprints |
| create_sprint | Create sprint |
| get_sprint | Get sprint by ID |
| update_sprint | Update sprint |
| delete_sprint | Delete sprint |

## Automations & Workflows
| Tool | Description |
|---|---|
| list_automations | List automations |
| create_automation | Create automation |
| get_automation | Get automation by ID |
| update_automation | Update automation |
| delete_automation | Delete automation |
| list_workflows | List workflows |
| create_workflow | Create workflow |
| get_workflow | Get workflow by ID |
| update_workflow | Update workflow |
| delete_workflow | Delete workflow |

## Subscribers & Subcolumns
| Tool | Description |
|---|---|
| list_card_subscribers | List card subscribers |
| add_card_subscriber | Subscribe user to card |
| remove_card_subscriber | Unsubscribe from card |
| list_column_subscribers | List column subscribers |
| add_column_subscriber | Subscribe to column |
| remove_column_subscriber | Unsubscribe from column |
| list_subcolumns | List subcolumns |
| create_subcolumn | Create subcolumn |
| update_subcolumn | Update subcolumn |
| delete_subcolumn | Delete subcolumn |

## Audit & Analytics
| Tool | Description |
|---|---|
| list_audit_logs | List audit logs |
| get_card_activity | Get card activity history |
| get_space_activity | Get space activity |
| get_company_activity | Get company activity |
| get_card_location_history | Card movement history |
| list_saved_filters | List saved filters |
| create_saved_filter | Create filter |
| get_saved_filter | Get filter |
| update_saved_filter | Update filter |
| delete_saved_filter | Delete filter |

## Roles & Groups
| Tool | Description |
|---|---|
| list_roles | List roles |
| get_role | Get role by ID |
| list_company_groups | List groups |
| create_company_group | Create group |
| get_company_group | Get group |
| update_company_group | Update group |
| delete_company_group | Delete group |
| list_group_users | List users in group |
| add_group_user | Add user to group |
| remove_group_user | Remove user from group |
| list_space_users | List space users |
| add_space_user | Add user to space |
| update_space_user | Update space user role |
| remove_space_user | Remove user from space |

## Service Desk
| Tool | Description |
|---|---|
| list_sd_requests | List service desk requests |
| create_sd_request | Create request |
| get_sd_request | Get request |
| update_sd_request | Update request |
| delete_sd_request | Delete request |
| list_sd_services | List services |
| get_sd_service | Get service |
| list_sd_organizations | List organizations |
| create_sd_organization | Create organization |
| get_sd_organization | Get organization |
| update_sd_organization | Update organization |
| delete_sd_organization | Delete organization |
| list_sd_sla | List SLA policies |
| get_sd_sla | Get SLA policy |

## Utilities
| Tool | Description |
|---|---|
| list_api_keys | List API keys |
| create_api_key | Create API key |
| delete_api_key | Delete API key |
| list_user_timers | List active timers |
| create_user_timer | Start timer |
| get_user_timer | Get timer |
| update_user_timer | Update timer |
| delete_user_timer | Stop/delete timer |
| list_removed_cards | List deleted cards |
| list_removed_boards | List deleted boards |
| list_calendars | List calendars |
| get_calendar | Get calendar |
| get_company | Get company info |
| update_company | Update company settings |

## Webhooks
| Tool | Description |
|---|---|
| list_webhooks | List webhooks |
| create_webhook | Create webhook |
| get_webhook | Get webhook |
| update_webhook | Update webhook |
| delete_webhook | Delete webhook |
