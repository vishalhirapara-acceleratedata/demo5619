---
status: decided
date: 2026-10-14
---

# Treat NULL quantity and unit_price as zero when computing total_revenue

When computing total_revenue (the sum of quantity × unit_price per order), NULL values in either quantity or unit_price are treated as zero via COALESCE rather than being excluded from the sum. This is hard to reverse because downstream consumers will depend on every order producing a non-NULL total_revenue; it is surprising without context because a NULL quantity could reasonably mean "unknown" rather than "none ordered"; and it reflects a real trade-off between excluding ambiguous rows and guaranteeing coverage.

## Considered options

- **COALESCE to zero (chosen)** — every order produces a total_revenue value; partial or unknown quantities contribute nothing rather than making the whole order's revenue unknown. Chosen because the demo seed has no NULL line items and the requirement mandates NOT NULL on total_revenue.
- **Exclude rows with NULL inputs** — would drop line items silently, under-counting revenue for affected orders. Rejected because it changes the population without a user-visible flag.
- **Propagate NULL** — would make total_revenue NULL for any order with a bad line item. Rejected because the enforced contract requires NOT NULL on total_revenue.

## Consequences

- Any dbt model or query reading `mart_sales.total_revenue` can assume it is never NULL.
- A source row where quantity or unit_price is legitimately unknown will contribute zero revenue; a data-quality alert (not in this intent's scope) is needed to surface that.
