---
kinds: [transformation]
---

# Requirement: Sales Data Mart Pipeline

## Ask

Build a sales data mart on DuckDB-local. The user asked to "build salesdata mart pipeline" using CSV as the source, with one row per order as the mart grain. Sample CSV data will be created by the agent as demo data. The mart will support sales analysis by order, customer, product and date.

## Requirements

- [ ] `R-01` Sample sales CSV seed data exists in the dbt project with realistic order records — accept when `dbt seed` completes without error and the seed table is queryable with a non-zero row count — source: user answer (demo data created by agent)
- [ ] `R-02` A staging model `stg_orders` cleans and types the raw seed data — accept when `dbt build --select stg_orders` passes with no test failures and the model is queryable — source: request
- [ ] `R-03` A mart model `mart_sales` delivers one row per order at order grain — accept when the model builds without error, a uniqueness test on `order_id` passes, and a row count matches the seed source — source: user answer (grain = one row per order)
- [ ] `R-04` `mart_sales` exposes key sales measures: `total_revenue` (quantity × unit_price), `total_items` (sum of line quantities), and `order_status` — accept when the columns exist with correct data types and a spot-check formula recomputation matches — source: agent-designed demo schema
- [ ] `R-05` All models and seeds have dbt YAML documentation (description + column descriptions) — accept when `dbt docs generate` completes without error — source: build standards

## Business decisions

| Decision | Value | Source |
| --- | --- | --- |
| Grain of `mart_sales` | One row per order (`order_id`) | User answer |
| Ingestion mechanism | dbt seeds (agent-created sample CSV) — no dlt pipeline for demo scenario | Agent decision; user asked agent to create sample data |
| Sample data schema | `order_id`, `order_date`, `customer_id`, `customer_name`, `product_id`, `product_name`, `category`, `quantity`, `unit_price`, `order_status` | Agent-designed demo schema |
| Population | All orders in the seed — no date or status filter | Playbook default (no filter stated) |
| Unmatched / null keys | Keep all rows | Playbook default (express) |
| Measures in mart | `total_revenue` = SUM(quantity × unit_price), `total_items` = SUM(quantity), `order_status` = order-level status | Agent-designed; user accepted demo scope |
| Consumers / freshness | Not applicable — demo domain | Not named by user or repository |
| Orchestration | Out of scope — not requested | Request |
| Semantic model | Out of scope — not requested | Request |

## Out of scope

- dlt ingestion pipeline (data is agent-created CSV seeds, not a live source)
- Orchestration / scheduling
- Semantic / BI layer
- Published models not named in this intent (none exist in the domain)
- Any production data writes — sandbox only

## Open questions

None — all material branches resolved.

## Approvals

- 2026-10-14T04:33Z — requirement approved — "approve_continue" — dcfd79d
