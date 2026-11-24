---
kinds: [ingestion, transformation]
---

# Requirement: Sample data: user, order, purchase, cart, payment

## Ask

The user built five 100-row fixture CSVs in `seeds/` (users, carts, orders, purchases, payments) and then asked: "now can you go ahead and build the salesforce sales data mart pipeline for thi ??".

Asked which reading of "salesforce sales data mart" they meant, they chose **the sales mart built from the five sample CSVs already in the repo** rather than a live Salesforce connection. Asked which sales numbers the mart must answer, they chose **cart-to-order funnel** and **product performance**. Analysts in the Domain consume the result through the boundary marts and the dbt docs.

## Requirements

- [ ] `R-01` The five fixture CSVs land in the Intent sandbox as bronze tables, one per file, carrying every source column — accept when each of `users`, `carts`, `orders`, `purchases`, `payments` returns `count(*) = 100` in the sandbox and the dlt preview renders all five — source: request, `seeds/*.csv`
- [ ] `R-02` A daily cart-funnel mart publishes one row per calendar day with cart activity — accept when the grain `(activity_date)` is unique and `carts_converted + carts_abandoned + carts_active = carts_created` on every row, and `sum(carts_created)` over all rows is 100 — source: user answer (funnel focus)
- [ ] `R-03` Conversion rate divides the day's converted carts by every cart created that day, `active` carts included — accept when an independent recomputation from `seeds/carts.csv` matches every row and `sum(carts_converted) / sum(carts_created) = 0.85` — source: user answer
- [ ] `R-04` A daily product-performance mart publishes one row per calendar day per product — accept when the grain `(activity_date, product_id)` is unique and `sum(units_sold)` equals the summed `quantity` of `seeds/purchases.csv` — source: user answer (product focus)
- [ ] `R-05` Revenue is gross: completed and refunded orders count at full value, cancelled orders are excluded, and refunds are published as their own measure beside revenue — accept when summed revenue equals an independent recomputation of line amounts over non-cancelled orders and summed refunded revenue equals the line amounts of the refunded orders — source: user answer
- [ ] `R-06` Every model and every source column used downstream is documented and tested — accept when `dbt build` over the selection is green, with unique and not-null tests on every grain key and `relationships` tests on every join key — source: request (a data product is a table with its tests and docs)
- [ ] `R-07` Every write lands only in the Intent sandbox — accept when `assert_destination.py` and `assert_dbt_destination.py` both exit 0 after the load and the build — source: platform contract

## Business decisions

| Decision | Value | Source |
| --- | --- | --- |
| Sources (ingestion) | The five fixture CSVs in `seeds/`, read through one `dlt-builtin` filesystem connection, one landed table per file | user answer (scope) |
| History (ingestion) | Merge on each file's natural key (`user_id`, `cart_id`, `order_id`, `purchase_id`, `payment_id`), keeping history | playbook default |
| Load size (ingestion) | Sample load, 1,000 rows per resource; the fixture holds 100 rows per file, so every row lands | playbook default |
| Cadence (ingestion) | Not applicable: a schedule is the `orchestration` kind, which `kinds:` does not list and the request did not ask for | playbook default |
| Grain of the funnel mart | One row per calendar day | user answer |
| Grain of the product mart | One row per calendar day per product | user answer |
| Edge periods | Not applicable: the source is a fixed two-year fixture that defines its own coverage, so no reporting-window boundary cuts a day short, and the marts publish activity days rather than a calendar spine | derived from the data |
| Revenue population | Gross: completed and refunded orders at full value, cancelled excluded, refunds a separate measure | user answer |
| Conversion definition | Numerator is `carts.status = 'converted'`; denominator is every cart created that day, `active` included | user answer |
| NULLs in aggregates | Not applicable: revenue sums `order_total`, which every non-cancelled order carries, and cancelled orders are excluded from revenue and reported by count instead, so no NULL enters an aggregate | derived from the data |
| Coverage | Publish the count of rows carrying each measure beside the aggregate (orders behind revenue, order lines behind units) | playbook default |
| Empty periods | Open, see `## Open questions`: the user declined to settle it, and both marts publish activity days only | user declined |
| Reuse | No published model exists in this Domain (empty repository; `list_assets` returns 0 assets), so both marts are built fresh on this intent's staging layer | repository |
| Unmatched and null keys | Keep every row: the marts read from `orders` and `carts` rather than dropping unmatched rows, and a future key miss surfaces as a `relationships` test failure rather than a silent drop | playbook default |
| Extended scope | Not applicable: no schedule requested, and the repository declares no `logical-model/`, `ontology/` or contract path | repository |

## Out of scope

- A live Salesforce connection: no Salesforce credential exists in the Domain Secret Store (`list_secret_names` returned none), and the user chose the fixture route.
- Customer lifetime value, repeat-purchase and payment-failure marts: offered in the same question and not selected.
- Any schedule or orchestration item.
- Any change to `seeds/*.csv`; they are the fixed input.

## Open questions

- **Empty periods.** Should a day with no carts, or no product sales, be emitted as a zero row or left out? The user declined to settle it. It moves row count only, never a total: both marts currently publish days with activity. It is asked again only on new evidence.
- **Onboarding.** The repository has no `AGENTS.md` and no `repo-map.json`, so no artifact location or layer role is declared. This intent uses the plugin's documented defaults (`ingestion/`, `transformation/`, `docs/design/`, `intents/<slug>/`); onboarding would pin them.

## Approvals
