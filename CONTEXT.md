# Review demo — Context

The ubiquitous language of this domain: business terms, entities, abbreviations, source-system quirks, and naming conventions. Platform and agent-family terms are defined elsewhere and never repeated here.

**This file is the language layer, nothing else.**

| Belongs here | Belongs in the catalog (Unity Catalog, Purview, dbt metadata) |
| --- | --- |
| What the business means by a word | Column names, data types, table schemas |
| An abbreviation only this org uses | Row counts, freshness, lineage |
| A source-system quirk worth knowing | Anything a catalog query already answers |

No design decisions (those are ADRs), no implementation detail (that is the artifact's design record), no example values.

## Language

**Order**: A customer purchase transaction. One order (identified by `order_id`) may contain multiple line items — one per product purchased — but represents a single commercial event.

**Order grain**: The level of aggregation at which sales metrics are reported: one row per unique `order_id`. Multi-line-item orders are collapsed to this grain before analysis.

**Total revenue**: A sales measure: the sum of (quantity × unit_price) across all line items belonging to an order, denominated in USD.
_Not_: gross revenue or gross merchandise value — those terms are not used in this domain.

**Total items**: The count of units ordered across all line items in an order. Distinct from the number of line items (products).

**Order status**: The fulfilment state of an order at the time of reporting. Valid values are: `completed`, `shipped`, `processing`, `cancelled`.
