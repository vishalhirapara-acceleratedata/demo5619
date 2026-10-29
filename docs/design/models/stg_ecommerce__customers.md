---
artifacts: [stg_ecommerce__customers]
---

# stg_ecommerce__customers

## Grain

One row per `customer_id` in bronze `src_ecommerce.customers`.

## Decisions

- `D-01` Reads only `source('ecommerce', 'customers')`; renames to snake_case and casts `signup_date` to `date`. No filter, no join, no dedupe: bronze holds exactly the CSV's rows. Source: medallion guardrails § Silver; `R-01`.
- `D-02` Materialised as a view in schema `staging`: staging is a thin 1:1 projection and needs no storage. Source: medallion guardrails § Silver.

## Rejected

- Casting inside the dimension instead — the cast belongs at the lowest layer that owns the type, so every consumer inherits it.

## Consumers

- `dim_customers`.

## History

- 2026-10-29 — intent `new-intent-3a74ac3d` — created.
