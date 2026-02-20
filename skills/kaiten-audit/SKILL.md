---
name: kaiten-audit
description: Comprehensive account health audit for Kaiten workspaces
version: 1.0.0
---

# Kaiten Account Health Audit

This skill performs a comprehensive health audit of a Kaiten workspace. It evaluates staleness, public exposure, WIP discipline, activity patterns, file hygiene, document tree health, kanban metrics, and automation health. The audit produces a single structured report with a composite health score (0-100).

## Anti-patterns (NEVER DO THIS)

- **NEVER** fetch cards without `relations="none"` + `fields` -- full card objects are ~20KB each, overflow context
- **NEVER** call `kaiten_get_card_location_history` per card -- use bulk `kaiten_list_all_cards` with timing fields
- **NEVER** skip Phase 0 Discovery -- all subsequent phases depend on it
- **NEVER** audit >5000 cards in one `kaiten_list_all_cards` call -- use `max_pages` safety limit
- **NEVER** call `kaiten_list_card_files` for every card -- sample 30-50 cards from active boards
- **NEVER** write standalone Python scripts -- all data comes from MCP tools

## Scope Controls

The user may specify audit scope:

| Parameter | Values | Default |
|---|---|---|
| scope | `account` / `space` / `board` | `account` (all spaces) |
| staleness_thresholds | custom days for queued/in_progress/done | 60 / 30 / 90 |
| period | lookback window for activity analysis | 30 days |
| space_id | specific space to audit | all spaces |

If scope is `space` or `board`, limit Discovery and all phases to the specified entity.

## Phase 0: Discovery (MANDATORY FIRST)

This phase builds the maps that all subsequent phases reference. Never skip it.

### Tools

```
kaiten_get_company()
kaiten_get_current_user()
kaiten_list_spaces()
kaiten_list_users(include_inactive=true, limit=200)
```

For each space:
```
kaiten_list_boards(space_id=X)
kaiten_list_columns(board_id=Y)  -- for each board
kaiten_get_tree(space_id=X)
```

### Output data structures

Build these maps in memory:

- **space_map**: `{space_id: {name, access, boards: [...]}}`
- **board_map**: `{board_id: {name, space_id, columns: [...]}}`
- **column_map**: `{column_id: {title, type, wip_limit, wip_limit_type, archive_after_days, last_moved_warning_after_days, card_hide_after_days, board_id}}`
- **user_map**: `{user_id: {full_name, last_request_date, activated, role, created}}`
- **entity_tree**: raw tree data per space for Phase 6

### API calls estimate

| Entity | Formula | Example (10 spaces, 5 boards/space) |
|---|---|---|
| Company + User | 2 | 2 |
| Spaces | 1 | 1 |
| Users | 1 | 1 |
| Boards | 1 per space | 10 |
| Columns | 1 per board | 50 |
| Trees | 1 per space | 10 |
| **Total** | | **~74** |

## Phase 1: Staleness

Identify cards that haven't moved or been updated for too long.

### Tool call

```
kaiten_list_all_cards(
  condition=1,
  relations="none",
  fields="id,title,state,board_id,column_id,last_moved_at,column_changed_at,comment_last_added_at,updated_at,created,due_date,owner_id,responsible_id,public,share_id"
)
```

If scope is `space`, add `space_id=X`. If scope is `board`, add `board_id=X`.

### Staleness algorithm

For each card, compute `days_since_move = now - last_moved_at` (fall back to `column_changed_at`, then `updated_at`, then `created`).

| State | Threshold | Severity |
|---|---|---|
| queued (state=1) | >60 days no move | STALE |
| in_progress (state=2) | >30 days no move | STUCK (CRITICAL) |
| done (state=3) + condition=1 | >90 days active | UNARCHIVED ZOMBIE |
| any | >180 days no activity | ABANDONED |

Additional flags:
- `owner_id is null` AND `responsible_id is null` = UNOWNED
- `due_date < now` AND `state != 3` = OVERDUE

### Document staleness

```
kaiten_list_documents(limit=200)
```

Flag documents where `updated_at` is older than 180 days as STALE_DOCUMENT.

### Output

- `stale_cards`: list of `{id, title, board, column, state, days_stale, severity}`
- `stale_documents`: list of `{uid, title, days_stale}`
- `staleness_score`: `100 * (1 - stale_count / total_count)`, clamped [0, 100]

## Phase 2: Public Exposure

Identify entities accessible to anyone outside the company.

### Data sources

From Discovery (no additional API calls):
- Spaces where `access == "for_everyone"` = PUBLIC_SPACE
- Documents where `public == true` = PUBLIC_DOCUMENT

From Phase 1 cards:
- Cards where `public == true` or `share_id is not null` = PUBLIC_CARD

### Optional: audit log check

If account has audit log access:
```
kaiten_list_audit_logs(categories="publication", limit=50)
```

### Output

- `public_spaces`: list of `{id, name}`
- `public_cards`: list of `{id, title, board}`
- `public_documents`: list of `{uid, title}`
- `security_score`: `100 - (public_count * 5)`, clamped [0, 100]

## Phase 3: WIP Health

Evaluate Work-In-Progress discipline across boards.

### Data sources

From Discovery:
- `column_map` with `wip_limit` values

From Phase 1 cards:
- Count cards per `column_id` where `state == 2` (in_progress)

### Algorithm

For each column with `type == 2` (in_progress):

1. Count active cards in this column
2. If `wip_limit > 0`: check if count exceeds limit
3. If `wip_limit == 0` or null: flag as NO_WIP_LIMIT

Stuck cards: `state == 2` AND `days_since_move > 14`

### Output

- `wip_violations`: list of `{board, column, limit, actual, overflow}`
- `columns_without_wip`: list of `{board, column}`
- `stuck_cards`: list of `{id, title, board, column, days_stuck}`
- `wip_score`: weighted average of `% columns within WIP` and `% cards not stuck`

## Phase 4: Activity Hotspots

Map where work is happening and where boards are dead.

### Tool call

For each space:
```
kaiten_get_all_space_activity(
  space_id=X,
  actions="card_add,card_move,card_archive,comment_add",
  created_after=<30 days ago ISO>,
  max_pages=10,
  fields="id,action,card_id,board_id,column_id,changed"
)
```

### Algorithm

Count events per board in the last 30 days:

| Events (30d) | Classification |
|---|---|
| >100 | HOTSPOT |
| 20-100 | ACTIVE |
| 1-19 | LOW_ACTIVITY |
| 0 | DEAD_ZONE |

Count events per user (from `changed.user_id` or activity actor):

| Events (30d) | Classification |
|---|---|
| >200 | OVERLOADED |
| 20-200 | NORMAL |
| 1-19 | LOW_ACTIVITY |
| 0 (but `activated=true`) | DORMANT |

Also from user_map: if `last_request_date` is >30 days ago, flag as DORMANT.

Input/output ratio per board:
```
ratio = card_add_count / max(card_archive_count, 1)
```
- ratio > 3.0 = INPUT_HEAVY (cards piling up)
- ratio < 0.3 = OUTPUT_HEAVY (clearing backlog)

### Output

- `board_activity`: list of `{board, space, events_30d, classification}`
- `user_activity`: list of `{user, events_30d, classification}`
- `dead_zones`: boards with 0 events
- `activity_score`: `100 * (active_boards / total_boards)`, clamped [0, 100]

## Phase 5: File Hygiene (Sampling)

Check file attachment health on a sample of cards. This is a sampling-based phase -- do NOT check every card.

### Sampling strategy

1. From Phase 4, pick the top 3 most active boards
2. From Phase 1 cards, pick 10-15 cards per board (newest first)
3. Total sample: 30-50 cards

### Tool call

For each sampled card:
```
kaiten_list_card_files(card_id=X)
```

### Flags

| Condition | Flag |
|---|---|
| file_count > 20 | TOO_MANY_FILES |
| filename matches `^[a-f0-9]{8,}` | HASH_NAME |
| filename matches UUID pattern | UUID_NAME |
| filename is generic (image.png, file.pdf, download.zip) | GENERIC_NAME |
| filename has no extension | NO_EXTENSION |

### Output

- `file_issues`: list of `{card_id, card_title, issue, files}`
- `hygiene_file_score`: `100 * (1 - issue_cards / sampled_cards)`

## Phase 6: Document Tree Health

Evaluate the organization of the document/entity tree.

### Data sources

From Discovery: `entity_tree` per space (from `kaiten_get_tree`).

### Algorithm

Traverse the tree recursively:

| Condition | Flag |
|---|---|
| depth > 4 | DEEP_NESTING |
| group has 0 children | EMPTY_GROUP |
| document `updated_at` > 180 days | STALE_DOCUMENT |
| document `parent_entity_uid` not found in tree | ORPHAN |

### Output

- `tree_issues`: list of `{space, path, issue, entity}`
- `hygiene_tree_score`: `100 * (1 - issue_count / total_entities)`
- Combined `hygiene_score`: average of `hygiene_file_score` and `hygiene_tree_score`

## Phase 7: Kanban Metrics (Delegation)

Delegate to the `kaiten-metrics` skill for quantitative flow metrics.

### Approach

For each space (or scoped space), collect:
- SLT median (System Lead Time)
- Cycle Time median
- Throughput per month
- WIP count
- Flow Efficiency (if time tracking is used)

Use the same `kaiten_list_all_cards` call pattern as described in the `kaiten-metrics` skill:

```
kaiten_list_all_cards(
  space_id=X,
  condition=2,
  relations="none",
  fields="id,title,type_id,created,first_moved_to_in_progress_at,last_moved_to_done_at,time_spent_sum,time_blocked_sum,state,condition,due_date,column_id,lane_id,board_id"
)
```

### Output

- `metrics_per_space`: `{space_id: {slt_median, cycle_time_median, throughput_month, wip_count}}`
- Include in report as summary table

## Phase 8: Automation Health

Check automation and webhook configurations.

### Tool calls

For each space:
```
kaiten_list_automations(space_id=X)
kaiten_list_webhooks(space_id=X)
kaiten_list_incoming_webhooks(space_id=X)
```

### Flags

| Condition | Flag |
|---|---|
| automation `enabled == false` | DISABLED_AUTOMATION |
| webhook `enabled == false` | DISABLED_WEBHOOK |
| incoming webhook pointing to non-existent board/column | BROKEN_INCOMING_WEBHOOK |
| space has 0 automations | NO_AUTOMATIONS |

### Output

- `automation_issues`: list of `{space, type, name, issue}`
- Include in report as summary table

## Phase 9: Entity Tree Visualization

Build an annotated ASCII tree of the workspace hierarchy.

### Data sources

All from previous phases -- no additional API calls.

### Annotation rules

Annotate entities in the tree with findings from earlier phases:

| Finding | Annotation |
|---|---|
| Board with 0 activity (Phase 4) | `[DEAD]` |
| Column with WIP violation (Phase 3) | `[!WIP 8/5]` |
| Public space/document (Phase 2) | `[PUBLIC]` |
| Stale document (Phase 6) | `[STALE 8mo]` |
| Empty group (Phase 6) | `[EMPTY]` |
| Hotspot board (Phase 4) | `[HOT]` |

### Example output

```
Space: Engineering [PUBLIC]
  Board: Sprint Board [HOT]
    Queue (wip: -)
    In Progress [!WIP 12/8]
    Review (wip: 3)
    Done
  Board: Legacy Backlog [DEAD]
    Backlog
    In Progress
    Done
  Docs:
    Architecture [STALE 14mo]
    API Reference
    Empty Folder [EMPTY]
```

## Scoring Model

Composite health score from 5 dimensions:

| Dimension | Weight | Source Phase | Formula |
|---|---|---|---|
| Staleness | 25% | Phase 1 | `100 * (1 - stale_count / total_cards)` |
| Flow/WIP | 20% | Phase 3 | avg of `% columns within WIP` and `% cards not stuck` |
| Activity | 20% | Phase 4 | `100 * (active_boards / total_boards)` |
| Security | 20% | Phase 2 | `100 - (public_entity_count * 5)` clamped [0, 100] |
| Hygiene | 15% | Phase 5+6 | avg of file hygiene and document tree scores |

```
composite = staleness * 0.25 + flow * 0.20 + activity * 0.20 + security * 0.20 + hygiene * 0.15
```

| Score | Status | Color |
|---|---|---|
| >= 75 | HEALTHY | GREEN |
| >= 50 | NEEDS ATTENTION | YELLOW |
| < 50 | AT RISK | RED |

## Report Template

```markdown
# Kaiten Account Health Audit

**Company**: {company_name} | **Date**: {date} | **Scope**: {N} spaces, {M} boards, {K} cards

## Health Score: {score}/100 ({status})

| Dimension | Score | Status | Key Finding |
|---|---|---|---|
| Staleness | {s1}/100 | {status1} | {top_finding_1} |
| Flow/WIP | {s2}/100 | {status2} | {top_finding_2} |
| Activity | {s3}/100 | {status3} | {top_finding_3} |
| Security | {s4}/100 | {status4} | {top_finding_4} |
| Hygiene | {s5}/100 | {status5} | {top_finding_5} |

## Top 3 Actions (Quick Wins)

1. {action_1} -- expected impact: {impact_1}
2. {action_2} -- expected impact: {impact_2}
3. {action_3} -- expected impact: {impact_3}

## 1. Staleness

{stale_count} stale cards out of {total_cards} ({pct}%).
{stuck_count} STUCK cards in progress (CRITICAL).

| Card | Board | Column | State | Days Stale | Severity |
|---|---|---|---|---|---|
(max 15 rows, sorted by severity then days_stale desc)

## 2. Public Exposure

{public_count} publicly accessible entities found.

- Public spaces: {list}
- Public cards: {count} (top 5 listed)
- Public documents: {count}

## 3. WIP Health

{violation_count} WIP limit violations across {board_count} boards.

| Board | Column | WIP Limit | Actual | Overflow |
|---|---|---|---|---|
(all violations)

{no_wip_count} in-progress columns have no WIP limit set.

## 4. Activity

| Board | Space | Events (30d) | Status |
|---|---|---|---|
(sorted: hotspots first, dead zones last, max 20 rows)

Dead zones: {dead_zone_list}
Dormant users: {dormant_user_list}

## 5. File Hygiene

Sampled {sample_count} cards across {board_count} boards.
{issue_count} cards with file naming issues.

## 6. Document Tree

{tree_issue_count} issues found in document tree structure.
- Deep nesting (>4 levels): {count}
- Empty groups: {count}
- Stale documents (>6 months): {count}

## 7. Kanban Metrics Summary

| Space | SLT Median | Cycle Time Median | Throughput/mo | WIP |
|---|---|---|---|---|
(one row per space)

## 8. Automation Health

| Space | Automations | Disabled | Webhooks | Issues |
|---|---|---|---|---|
(one row per space with automations)

## 9. Entity Tree (Annotated)

(ASCII tree from Phase 9)

## Recommendations

### Quick Wins (this week)
- {recommendation_1}
- {recommendation_2}

### Planned Work (this month)
- {recommendation_3}
- {recommendation_4}

### Strategic (this quarter)
- {recommendation_5}

## Methodology

- Staleness thresholds: queued={t1}d, in_progress={t2}d, done_unarchived={t3}d
- Activity window: {period} days
- File hygiene: sampled {n} cards from top {m} active boards
- Data sources: {tool_count} MCP tool calls, {total_calls} API requests
```

## API Call Budget

| Phase | Calls (10 spaces, 5 boards/space) | Time (~4.5 req/s) |
|---|---|---|
| 0. Discovery | ~74 | ~17s |
| 1. Staleness (cards) | ~10-24 | ~5-10s |
| 1. Staleness (docs) | ~1 | ~0.2s |
| 2. Public Exposure | 0 (from discovery + phase 1) | 0s |
| 3. WIP Health | 0 (from discovery + phase 1) | 0s |
| 4. Activity | ~100 | ~22s |
| 5. File Hygiene | ~30-50 (sampled) | ~7-11s |
| 6. Document Tree | 0 (from discovery) | 0s |
| 7. Kanban Metrics | ~20-60 | ~5-13s |
| 8. Automations | ~30-60 | ~7-13s |
| 9. Visualization | 0 (computed) | 0s |
| **Total** | **~265-370** | **~63-87s** |

## Execution Order

Phases MUST execute in order because later phases depend on earlier data:

1. **Phase 0** (Discovery) -- prerequisite for all
2. **Phase 1** (Staleness) -- produces card data for Phases 2, 3, 5
3. **Phase 2** (Public Exposure) -- uses Phase 0 + Phase 1 data
4. **Phase 3** (WIP Health) -- uses Phase 0 + Phase 1 data
5. **Phase 4** (Activity) -- independent of Phase 1, but needs Phase 0
6. **Phase 5** (File Hygiene) -- needs Phase 1 cards + Phase 4 top boards
7. **Phase 6** (Document Tree) -- uses Phase 0 tree data
8. **Phase 7** (Kanban Metrics) -- independent, uses same card fetching pattern
9. **Phase 8** (Automations) -- independent, uses Phase 0 space list
10. **Phase 9** (Visualization) -- aggregates all findings

Note: Phases 4, 7, 8 are independent of each other and can run after Phase 1.

## ToolSearch Queries

Load MCP tools before use. Run these ToolSearch queries at the start:

```
ToolSearch query: "+kaiten list all cards"
ToolSearch query: "+kaiten space activity"
ToolSearch query: "+kaiten list spaces"
ToolSearch query: "+kaiten list boards"
ToolSearch query: "+kaiten list columns"
ToolSearch query: "+kaiten tree"
ToolSearch query: "+kaiten list users"
ToolSearch query: "+kaiten company"
ToolSearch query: "+kaiten list documents"
ToolSearch query: "+kaiten list card files"
ToolSearch query: "+kaiten automations"
ToolSearch query: "+kaiten webhooks"
ToolSearch query: "+kaiten audit log"
```

## Tips

1. **Reuse card data** -- Phase 1 fetches all active cards once. Phases 2, 3, and 5 all use this same dataset. Never re-fetch.
2. **Respect rate limits** -- at 4.5 req/s, 350 calls takes ~80 seconds. Be patient.
3. **Progressive reporting** -- output section-by-section as each phase completes, rather than waiting for all phases to finish.
4. **Skip phases if scoped** -- if scope is a single board, skip Phase 4 (activity) and Phase 8 (automations) as they add limited value.
5. **Cap table rows** -- staleness table: max 15 rows. Activity table: max 20 rows. Always sort by severity.
6. **File hygiene is sampled** -- explicitly state the sample size and boards in the report. Don't claim comprehensive file analysis.
7. **Handle missing data gracefully** -- some fields (last_moved_at, comment_last_added_at) may be null. Fall back to `updated_at`, then `created`.
8. **Delegate metrics** -- for detailed kanban metrics, refer to the `kaiten-metrics` skill. The audit provides summary numbers only.
