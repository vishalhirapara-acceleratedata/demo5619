---
artifacts: [fct_order_lines]
---

# fct_order_lines

## Grain

One row per order line: `order_id` + `line_number`, unique together.

## Decisions

- `D-01` Grain key is `order_id` + `line_number`, both taken from the order line itself, not a generated surrogate: they are the source's own identity and the CSV's documented primary key. Source: `R-03`.
- `D-02` Population: only lines whose order has `status = 'completed'`; `pending`, `cancelled` and `refunded` are excluded. An order line whose `order_id` matches no order row is also excluded, since it cannot be shown to belong to a completed order — the requirement's population is defined through the order's status. Source: `R-03`; answer `population = completed`; answer `unmatched = keep` (which the Requirement scopes to customer and product keys).
- `D-03` Net revenue is `quantity * unit_price - discount_amount`, cast to `decimal(18,2)`, and published beside `quantity`, `unit_price`, `discount_amount` and `gross_amount` (`quantity * unit_price`) so any consumer can re-derive it. Currency is USD with no FX. Source: `R-04`; answer `revenue = net`; Requirement decision `currency and rounding`.
- `D-04` Customer and product attributes come from `dim_customers` and `dim_products` by LEFT JOIN on the natural key: an unmatched key keeps the line with NULL dimension columns, and those columns are nullable in the contract. Source: `R-06`; answer `unmatched = keep`.
- `D-05` Materialised as a table in schema `marts` with `contract: {enforced: true}` and explicit column types. Source: medallion guardrails § Gold.
- `D-06` Tests: `unique` on `order_id` + `line_number` (dbt_utils surrogate expression or a two-column unique test), `not_null` on `order_id`, `line_number`, `quantity`, `unit_price`, `discount_amount`, `net_revenue`, `order_date`; `relationships` from `customer_id` to `dim_customers` and `product_id` to `dim_products` with severity `warn`, because `R-06` keeps unmatched keys deliberately rather than treating them as a defect. Source: `R-06`, `R-08`.

## Rejected

- Inner joins to the dimensions — they would silently drop unmatched lines and break `R-06`.
- A surrogate `order_line_id` — `order_id` + `line_number` is already unique and is what a consumer filters on.
- Publishing only `net_revenue` — `R-04` requires the components beside it so the figure can be re-derived.

## Consumers

- `mart_orders`, and the domain owner's own sales questions.

## History

- 2026-10-29 — intent `new-intent-3a74ac3d` — created.
