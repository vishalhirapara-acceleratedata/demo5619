---
artifacts: [stg_ecommerce__orders]
---

# stg_ecommerce__orders

## Grain

One row per `order_id` in bronze `src_ecommerce.orders`.

## Decisions

- `D-01` Reads only `source('ecommerce', 'orders')`; renames to snake_case and casts `order_date` to `date`. Status is passed through unmodified as text — no filtering in silver, because the sales population is a gold-layer rule. Source: medallion guardrails § Silver; `R-03`.
- `D-02` Materialised as a view in schema `staging`. Source: medallion guardrails § Silver.

## Rejected

- Filtering `status = 'completed'` here — the population rule belongs to the fact that the requirement names, and staging must stay a 1:1 projection any other consumer can read.

## Consumers

- `fct_order_lines`.

## History

- 2026-10-29 — intent `new-intent-3a74ac3d` — created.
