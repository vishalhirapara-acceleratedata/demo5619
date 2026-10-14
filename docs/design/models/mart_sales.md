---
artifacts: [mart_sales]
---

# mart_sales

The durable design record for the `mart_sales` gold mart model.

## Grain

One row per order (`order_id`). Each order aggregates all its line items from `stg_orders`.

## Decisions

- `D-01` Reads `ref('stg_orders')` only — gold layer never reads `source()` or a lower-layer seed directly. Source: medallion guardrails.
- `D-02` Grain is `order_id`; uniqueness enforced by a `unique` + `not_null` dbt test on `order_id`. Source: R-03, user answer.
- `D-03` `total_revenue` = SUM(quantity × unit_price) across all line items for the order. NULL quantity or unit_price rows contribute 0 (COALESCE). Source: R-04, business decision.
- `D-04` `total_items` = SUM(quantity) across all line items for the order. Source: R-04, business decision.
- `D-05` `order_status` is taken as MIN(order_status) — for a demo all line items in an order share one status; MIN is deterministic and reproducible. Source: R-04, agent decision (demo assumption).
- `D-06` Carries dimensional columns at order grain: `order_date`, `customer_id`, `customer_name` — taken as MIN() to collapse duplicate values from multiple line items of the same order. Source: design.
- `D-07` Materialised as `table` with `contract: { enforced: true }` and explicit column types. Source: medallion guardrails (gold layer requires enforced contract).
- `D-08` Explicit column list — no `SELECT *`. Source: medallion guardrails.

## Rejected

- Materialised as `view`: gold marts should be `table` for query performance and enforced contracts.
- Including product-level columns in mart: these belong at line-item grain (out of scope for this intent).

## Consumers

None at the time of this intent — demo domain, no downstream models or BI tools configured.

## Evidence

- Source schema derived from agent-created seed (see R-01 business decisions).
- Row count: `mart_sales` will have one row per distinct `order_id` in the seed.
- No existing models impacted — fresh build.
- No prod manifest — defer unavailable.

## History

- 2026-10-14 — new-intent-87028a1a — initial design — D-01 through D-08
