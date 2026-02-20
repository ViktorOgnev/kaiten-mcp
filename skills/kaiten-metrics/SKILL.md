---
name: kaiten-metrics
description: Collect Kanban metrics from Kaiten using MCP tools efficiently
version: 1.0.0
---

# Kanban Metrics Collection via Kaiten MCP Tools

This skill teaches efficient collection of Kanban metrics (Lead Time, Cycle Time, Throughput, WIP, Flow Efficiency) using Kaiten MCP tools. All metrics are computed from data already present on card objects or from server-side chart endpoints, eliminating the need for per-card API calls.

## Anti-patterns (NEVER DO THIS)

- **NEVER** write Python or shell scripts that call the Kaiten REST API directly
- **NEVER** hardcode API tokens in scripts or files
- **NEVER** call `kaiten_get_card_location_history` for each card individually (N+1 problem)
- **NEVER** use `time.sleep()` sequential polling patterns
- **NEVER** create standalone script files for metrics collection
- **NEVER** fetch cards one-by-one when bulk endpoints exist

The anti-pattern approach (per-card history calls) results in 539+ API calls taking 42+ minutes. The correct MCP approach uses 5-15 API calls and completes in under 1 minute.

## Efficient Data Fetching (CRITICAL)

Bulk card endpoints return full card objects (~20KB each). Without optimization, 100 cards = 2MB+ which overflows the LLM context window. **Always** use these parameters:

### Recommended call pattern for metrics

```
kaiten_list_all_cards(
  space_id=X,
  condition=2,
  relations="none",
  fields="id,title,type_id,created,first_moved_to_in_progress_at,last_moved_to_done_at,time_spent_sum,time_blocked_sum,state,condition,due_date,column_id,lane_id,board_id"
)
```

### Parameter guide

| Parameter | Effect | When to use |
|---|---|---|
| `relations="none"` | Excludes members, files, comments, checklists, properties, tags (~90% size reduction) | **Always** for bulk card fetching |
| `fields="id,title,..."` | Returns only listed fields per card (~99% size reduction) | **Always** for metrics — request only timing fields |
| `compact=true` | Strips descriptions, simplifies user objects (default for bulk) | Automatic, no action needed |

### Response sizes

| Configuration | Per card | 500 cards |
|---|---|---|
| No optimization | ~20KB | 10MB+ (OVERFLOW) |
| `relations="none"` | ~2KB | ~1MB |
| `relations="none"` + `compact` | ~500B | ~250KB |
| `relations="none"` + `fields` | ~200B | **~100KB** (optimal) |

### For Space Activity

```
kaiten_get_all_space_activity(
  space_id=X,
  actions="card_add,card_move,card_archive",
  fields="id,action,card_id,board_id,column_id,lane_id,changed"
)
```

## Quick Metrics (from card fields only)

Card objects returned by `kaiten_list_all_cards` already contain all the timing fields needed for standard metrics. No additional API calls are required.

### Step-by-step

```
Step 1: kaiten_list_all_cards(space_id=X, condition=1, relations="none",
          fields="id,title,type_id,state,column_id,lane_id,board_id,time_spent_sum,time_blocked_sum")
        -- active cards (for WIP)

Step 2: kaiten_list_all_cards(space_id=X, condition=2, relations="none",
          fields="id,title,type_id,created,first_moved_to_in_progress_at,last_moved_to_done_at,time_spent_sum,time_blocked_sum,state,condition,due_date,column_id,lane_id,board_id")
        -- archived/done cards (for SLT, Cycle Time, Throughput)

Step 3: Compute metrics from the card fields directly (no further API calls)
```

### Available timing fields on each card

| Field | Description |
|---|---|
| `created` | Card creation timestamp |
| `first_moved_to_in_progress_at` | When card first entered an In Progress column |
| `last_moved_to_done_at` | When card last moved to a Done column |
| `time_spent_sum` | Total logged work time (minutes) |
| `time_blocked_sum` | Total blocked time (minutes) |
| `state` | 1 = queued, 2 = inProgress, 3 = done |
| `condition` | 1 = active, 2 = archived |
| `due_date` | Card due date (if set) |
| `column_id` | Current column ID |

### Metric formulas

**System Lead Time (SLT)** -- total time from creation to completion:
```
SLT = last_moved_to_done_at - created
```
Apply to: archived cards where `last_moved_to_done_at` is not null.

**Cycle Time** -- time from start of work to completion:
```
Cycle Time = last_moved_to_done_at - first_moved_to_in_progress_at
```
Apply to: archived cards where both fields are not null.

**Throughput** -- number of cards completed per period:
```
Throughput = count of cards where last_moved_to_done_at falls within [period_start, period_end]
```
Group by week or month as needed.

**Work In Progress (WIP)** -- cards currently being worked on:
```
WIP = count of active cards where state = 2 (inProgress)
```
Group by `column_id` for per-column WIP counts.

**Due Date Performance** -- on-time delivery rate:
```
On-time = last_moved_to_done_at <= due_date
Late    = last_moved_to_done_at > due_date
Rate    = count(on-time) / count(completed cards with due_date)
```
Apply to: completed cards where both `due_date` and `last_moved_to_done_at` are not null.

**Flow Efficiency** -- ratio of active work time to total elapsed time:
```
Flow Efficiency = time_spent_sum / (last_moved_to_done_at - first_moved_to_in_progress_at)
```
Only meaningful when `time_spent_sum` is actively tracked by the team.

## Detailed Flow Analysis (using Space Activity)

When you need column-by-column timing (e.g., how long cards spent in each column), use the Space Activity endpoint instead of per-card history calls.

### Step-by-step

```
Step 1: kaiten_list_boards(space_id=X)
        -- get board structure (board IDs)

Step 2: kaiten_list_columns(board_id=Y)
        -- get column names and IDs for each board

Step 3: kaiten_get_all_space_activity(
          space_id=X,
          actions='card_add,card_move,card_archive,card_join_board,card_revive',
          fields='id,action,card_id,board_id,column_id,lane_id,changed'
        )
        -- returns ALL location events for ALL cards in the space
        -- auto-paginates (~5-10 requests instead of 539 individual calls)
        -- fields parameter keeps only needed data (small response)

Step 4: Group activity records by card_id
        -- reconstruct per-card column transition timeline

Step 5: Compute time-in-column
        -- for each card, diff consecutive card_move timestamps
        -- map column_id to column name from Step 2
```

This approach replaces N individual `kaiten_get_card_location_history` calls with a single paginated bulk fetch.

## Pre-computed Analytics (using Charts)

Kaiten provides server-side chart computation for standard analytics. These return pre-aggregated data with no client-side calculation needed.

### Available chart tools

| Tool | What it computes |
|---|---|
| `kaiten_chart_cfd` | Cumulative Flow Diagram -- cards in each state over time |
| `kaiten_chart_control` | Control Chart -- cycle time per individual card |
| `kaiten_chart_cycle_time` | Cycle Time chart -- distribution and trends |
| `kaiten_chart_lead_time` | Lead Time chart -- distribution and trends |
| `kaiten_chart_throughput_capacity` | Throughput (capacity) -- completed cards over time |
| `kaiten_chart_throughput_demand` | Throughput (demand) -- created cards over time |

### Usage pattern

```
Step 1: kaiten_chart_cfd(space_id=X, date_from="2025-01-01", date_to="2025-12-31")
        -- returns a job_id

Step 2: kaiten_get_compute_job(job_id=<returned_id>)
        -- poll until status is "done"
        -- result contains the computed chart data
```

All chart tools follow this async pattern: submit job, then poll for results.

## Metric Definitions Reference

| Metric | Formula | MCP Tools | API Calls | Time |
|---|---|---|---|---|
| System Lead Time | `last_moved_to_done_at - created` | `kaiten_list_all_cards` | 2-10 (paginated) | <30s |
| Cycle Time | `last_moved_to_done_at - first_moved_to_in_progress_at` | `kaiten_list_all_cards` | 2-10 (paginated) | <30s |
| Throughput | Count completed cards per period | `kaiten_list_all_cards` | 2-10 (paginated) | <30s |
| WIP | Count active cards with `state=2` | `kaiten_list_all_cards` | 1-5 (paginated) | <15s |
| Due Date Performance | `last_moved_to_done_at` vs `due_date` | `kaiten_list_all_cards` | 2-10 (paginated) | <30s |
| Flow Efficiency | `time_spent_sum / elapsed` | `kaiten_list_all_cards` | 2-10 (paginated) | <30s |
| Time in Column | Activity event diffs | `kaiten_get_all_space_activity` + `kaiten_list_columns` | 5-15 | <60s |
| CFD | Server-computed | `kaiten_chart_cfd` + `kaiten_get_compute_job` | 2 | <30s |
| Control Chart | Server-computed | `kaiten_chart_control` + `kaiten_get_compute_job` | 2 | <30s |
| Cycle Time Chart | Server-computed | `kaiten_chart_cycle_time` + `kaiten_get_compute_job` | 2 | <30s |
| Lead Time Chart | Server-computed | `kaiten_chart_lead_time` + `kaiten_get_compute_job` | 2 | <30s |
| Throughput (capacity) | Server-computed | `kaiten_chart_throughput_capacity` + `kaiten_get_compute_job` | 2 | <30s |
| Throughput (demand) | Server-computed | `kaiten_chart_throughput_demand` + `kaiten_get_compute_job` | 2 | <30s |

## Performance Expectations

| Scenario | Old approach (scripts) | New approach (MCP tools) |
|---|---|---|
| 539 cards full metrics | 42 min, 539+ API calls | <1 min, ~15 API calls |
| WIP snapshot | Manual script, N calls | 1 bulk call (`kaiten_list_all_cards`) |
| CFD chart | Complex script with calculations | 2 API calls (chart + poll) |
| Cycle time distribution | Per-card history fetches | 2 API calls (chart + poll) |
| Column-level flow analysis | N per-card history calls | ~10 paginated activity calls |

## ToolSearch Queries

Load the required MCP tools before use:

```
ToolSearch query: "+kaiten list all cards"       --> kaiten_list_all_cards
ToolSearch query: "+kaiten space activity"        --> kaiten_get_space_activity, kaiten_get_all_space_activity
ToolSearch query: "+kaiten chart"                 --> kaiten_chart_cfd, kaiten_chart_control, etc.
ToolSearch query: "select:mcp__kaiten__kaiten_get_compute_job"  --> kaiten_get_compute_job
ToolSearch query: "+kaiten board column"          --> kaiten_list_boards, kaiten_list_columns
```

## Tips

1. **Always use `relations="none"` and `fields`** -- without these, 100 cards = 2MB+ which overflows the LLM context. With them, 500 cards = ~100KB.
2. **Start with Quick Metrics** -- card fields cover 80% of metrics needs with zero extra API calls beyond the bulk fetch.
3. **Use `condition` filtering** -- pass `condition=1` for active cards, `condition=2` for archived. This avoids fetching unnecessary data.
4. **Prefer charts for presentation** -- if you need a chart image or pre-aggregated data, use the `kaiten_chart_*` tools. They compute everything server-side.
5. **Space Activity is the bulk alternative** -- when you need per-column timing, `kaiten_get_all_space_activity` replaces hundreds of individual history calls.
6. **Auto-pagination is built in** -- `kaiten_list_all_cards` handles pagination automatically (up to 5000 cards). No manual offset management needed.
7. **Never read full JSON into LLM** -- if a file was saved to disk due to size, extract only the needed fields before processing.
