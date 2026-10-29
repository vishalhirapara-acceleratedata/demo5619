---
kinds: [ingestion, transformation]
---

# Requirement: How are you boss

## Ask

Create a set of sample CSV files modelling an ecommerce platform, and build a sales pipeline over them: land the files in the sandbox, then model sales. The user (the domain owner) consumes the resulting marts; nothing else downstream is known today.

The repository is new — no `AGENTS.md`, `repo-map.json`, `CONTEXT.md` or `docs/` layout existed at the start of this intent — so the artifact locations below were chosen by the user rather than read from the repository.

## Requirements

- [ ] `R-01` Four sample source files exist in the repository — `customers`, `products`, `orders`, `order_items` — as CSV with a header row and a stable column set. — accept when each file parses as CSV, its header matches the documented column list, and each holds at least one data row — source: request; answer `four`
- [ ] `R-02` The four files land in the Intent's sandbox as four bronze tables through a committed dlt pipeline. — accept when each of the four tables exists in the sandbox with a row count equal to its CSV's data-row count — source: request
- [ ] `R-03` A sales fact exists at the grain of one order line, holding only completed orders. — accept when the fact's row count equals the count of `order_items` rows joined to an order with status `completed`, and its grain key is unique — source: answers `grain = both`, `population = completed`
- [ ] `R-04` Net revenue is published per order line as `quantity * unit_price - discount_amount`, together with its components. — accept when an independent recomputation of net revenue from the bronze tables matches the fact's total to the cent, and the per-line formula holds for every row — source: answer `revenue = net`
- [ ] `R-05` An order-level mart exists at the grain of one order, reconciling to the line fact. — accept when its order key is unique and the sum of its net revenue equals the line fact's net revenue for the same population — source: answer `grain = both`
- [ ] `R-06` An order line whose customer or product does not match a dimension row is kept, with the unmatched dimension columns NULL. — accept when the fact's row count equals the population count of `R-03` even when a fixture supplies an unmatched key, and the unmatched columns are NULL rather than dropped — source: answer `unmatched = keep`
- [ ] `R-07` Customer and product dimensions exist, one row per source id. — accept when each dimension's key is unique and its row count equals the count of distinct ids in its bronze table — source: answer `sources = four` (dimensions are what the facts join to)
- [ ] `R-08` Every built model is covered by tests — generic tests on grain, keys and relations, and dbt unit tests on each modelled branch — and builds green in the sandbox. — accept when `dbt build` over the project returns no failures and every model carries at least its grain test — source: project convention (a data product is finished only with its tests)

## Business decisions

| Decision | Value | Source |
| --- | --- | --- |
| Source objects in scope | `customers`, `products`, `orders`, `order_items` as CSV files committed to this repository | user answer `four` |
| Source file size | a fixed hand-authored sample (small enough to review by eye); the pipeline loads every row of each file | playbook default (sample load); the files are themselves the sample |
| Bronze write disposition | replace, no history: the CSVs carry no stable change-feed identity and each load is a full extract | playbook default (full extract with no identity replaces) |
| Grain of the sales fact | one row per order line | user answer `grain = both` |
| Grain of the order mart | one row per order | user answer `grain = both` |
| Net revenue definition | `quantity * unit_price - discount_amount`, published alongside its components | user answer `revenue = net` |
| Sales population | only orders whose status is `completed`; `pending`, `cancelled` and `refunded` are excluded | user answer `population = completed` |
| Unmatched dimension keys in the fact | keep the line, leave the unmatched dimension columns NULL | user answer `unmatched = keep` |
| Dimension grain | one row per source id (`customer_id`, `product_id`) | derived from `R-07` |
| Currency and rounding | net revenue in USD, `decimal(18,2)`; no FX conversion | playbook default — the request names no currency |
| Intent artifact locations | `docs/requirements/`, `docs/design/`, `docs/plans/`, `docs/verifications/` | user answer `artifact_location = docs` |

## Out of scope

- Any schedule, cron or orchestration item: not requested. Adding one later is the `orchestration` kind.
- Returns and refunds as a source object (not chosen), and any net-of-refund revenue definition.
- The canonical semantic model (`logical-model/`) and the ontology (`ontology/`): neither exists in this repository today.
- Data contracts: no `repo-map.json` declares a contract boundary, so no relation is on one.
- No published model exists in this repository, so nothing can be broken by this change.

## Open questions

- None blocking. Currency is unstated and defaulted to USD; say so now if the platform should be multi-currency, since a currency column on the source is much cheaper to add before the files exist than after.

## Approvals
- 2026-10-29T10:19:35Z — requirement approved — "approve" — 1bd9f80
- 2026-10-29T10:30:36Z — design approved — "approve" — f7c23cc
