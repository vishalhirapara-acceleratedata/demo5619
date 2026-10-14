---
artifacts: [stg_orders]
---

# stg_orders

The durable design record for the `stg_orders` staging model.

## Grain

One row per order line item — identical to the `orders` seed. One `order_id` may appear on multiple rows (one per product purchased in that order).

## Decisions

- `D-01` Reads `ref('orders')` (the dbt seed). No bronze/dlt landing table exists — the seed is the raw data source for this demo domain. Source: R-01, agent decision.
- `D-02` Casts `order_date` to DATE, `quantity` to INTEGER, `unit_price` to DECIMAL(10,2). All other columns remain VARCHAR. Source: R-02, standard silver typing.
- `D-03` Renames no columns — the seed schema is already clean. Source: R-02, requirement.
- `D-04` No filtering applied — all rows from the seed are surfaced. Source: business decision (population = all orders, no filter).
- `D-05` Materialised as `view` — staging models are views by dbt convention in greenfield projects. Source: medallion guardrails.

## Rejected

- Materialised as `table`: unnecessary for a demo with a small seed; view keeps it light.
- Reading via `source()`: seeds are accessed through `ref()` in dbt, not `source()`.

## Consumers

- `mart_sales` — the gold mart reads `ref('stg_orders')`.

## Evidence

- No upstream bronze data to profile — seed data is agent-created, schema defined in R-01 business decisions.
- No existing models impacted — fresh build.
- No prod manifest — defer unavailable.

## History

- 2026-10-14 — new-intent-87028a1a — initial design — D-01 through D-05
