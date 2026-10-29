---
artifacts: [dim_products]
---

# dim_products

## Grain

One row per `product_id`, the natural key of `stg_ecommerce__products`.

## Decisions

- `D-01` Materialised as a table in schema `marts`, `contract: {enforced: true}`, with `product_id` the primary key. Source: medallion guardrails § Gold; `R-07`.
- `D-02` Columns: `product_id`, `product_name`, `category`, `list_price` — the staging columns as-is; `list_price` is the catalogue price, never the price charged, which lives on the order line. Source: `R-07`.
- `D-03` Tests: `unique` and `not_null` on `product_id`. Source: `R-08`.

## Rejected

- Surrogate keys — the source id is a stable integer identity.

## Consumers

- `fct_order_lines` joins it for `product_id` validation; no consumer reads attributes yet.

## History

- 2026-10-29 — intent `new-intent-3a74ac3d` — created.
