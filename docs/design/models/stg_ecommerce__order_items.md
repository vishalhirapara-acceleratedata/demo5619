---
artifacts: [stg_ecommerce__order_items]
---

# stg_ecommerce__order_items

## Grain

One row per `order_id` + `line_number` in bronze `src_ecommerce.order_items`.

## Decisions

- `D-01` Reads only `source('ecommerce', 'order_items')`; renames to snake_case and casts `quantity` to `integer`, `unit_price` and `discount_amount` to `decimal(18,2)`. No filter and no join. Source: medallion guardrails § Silver; `R-01`.
- `D-02` Materialised as a view in schema `staging`. Source: medallion guardrails § Silver.

## Rejected

- Computing net revenue here — a measure belongs on the fact that states its grain, not on the 1:1 staging projection.

## Consumers

- `fct_order_lines`.

## History

- 2026-10-29 — intent `new-intent-3a74ac3d` — created.
