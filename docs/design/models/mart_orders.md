---
artifacts: [mart_orders]
---

# mart_orders

## Grain

One row per `order_id` holding at least one completed order line.

## Decisions

- `D-01` Rolls up `fct_order_lines`, the published fact, rather than recomputing from staging: the fact already states this population (`completed` orders) and this measure (`net_revenue`), so the mart inherits both instead of duplicating the rule. Source: `R-05`; transformation playbook § Reuse.
- `D-02` Population is the fact's population, which means an order with no completed line does not appear; every completed order that has at least one line does. Source: `R-05`.
- `D-03` Measures: `line_count`, `total_quantity`, `gross_revenue`, `total_discount`, `net_revenue` — each a sum over the order's lines, `net_revenue` summing the fact's own column so the two agree by construction. `order_date` and `customer_id` are carried for grouping; `customer_id` is the fact's, so it is NULL only when the line's key matched no customer. Source: `R-05`, `R-06`.
- `D-04` Materialised as a table in schema `marts` with `contract: {enforced: true}`. Source: medallion guardrails § Gold.
- `D-05` Tests: `unique` and `not_null` on `order_id`, `not_null` on `net_revenue`, `relationships` from `customer_id` to `dim_customers` with severity `warn` (matching the fact). Source: `R-08`.

## Rejected

- Rebuilding order totals from `stg_ecommerce__order_items` — that would restate the population and the revenue formula in a second place and let the two drift.

## Consumers

- The domain owner's order-level reporting; nothing else in the repository yet.

## History

- 2026-10-29 — intent `new-intent-3a74ac3d` — created.
