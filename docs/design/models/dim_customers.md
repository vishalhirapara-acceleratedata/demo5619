---
artifacts: [dim_customers]
---

# dim_customers

## Grain

One row per `customer_id`, the natural key of `stg_ecommerce__customers`.

## Decisions

- `D-01` Materialised as a table in schema `marts`, `contract: {enforced: true}`, with explicit columns and types; `customer_id` the primary key. Source: medallion guardrails § Gold; `R-07`.
- `D-02` Columns: `customer_id`, `first_name`, `last_name`, `email`, `country_code`, `signup_date` — exactly the staging columns, no derived attributes: the request names no customer attribute beyond the source's own. Source: `R-07`.
- `D-03` Tests: `unique` and `not_null` on `customer_id`, `not_null` on `email`. Source: `R-08`.

## Rejected

- Surrogate keys — the source id is already a stable integer identity and nothing here versions a customer.

## Consumers

- `fct_order_lines` joins it for `customer_id` validation; no consumer reads attributes yet.

## History

- 2026-10-29 — intent `new-intent-3a74ac3d` — created.
