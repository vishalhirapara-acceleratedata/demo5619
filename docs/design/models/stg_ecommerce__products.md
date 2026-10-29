---
artifacts: [stg_ecommerce__products]
---

# stg_ecommerce__products

## Grain

One row per `product_id` in bronze `src_ecommerce.products`.

## Decisions

- `D-01` Reads only `source('ecommerce', 'products')`; renames to snake_case and casts `list_price` to `decimal(18,2)` and `created_at` to `timestamp`. No filter, no join, no dedupe. Source: medallion guardrails § Silver; `R-01`.
- `D-02` Materialised as a view in schema `staging`. Source: medallion guardrails § Silver.

## Rejected

- Deriving the sale price here — the price actually charged lives on the order line, and staging carries no business rule.

## Consumers

- `dim_products`.

## History

- 2026-10-29 — intent `new-intent-3a74ac3d` — created.
