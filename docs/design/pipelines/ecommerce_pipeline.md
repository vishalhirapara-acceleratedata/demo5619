---
artifacts: [ecommerce_pipeline]
---

# ecommerce_pipeline

## Grain

One landed bronze table per source CSV (`customers`, `products`, `orders`, `order_items`), each holding one row per row of that CSV.

## Decisions

- `D-01` The source is the four CSV files this intent authors under `landing/ecommerce/`, read through dlt's built-in `dlt.sources.filesystem` + `read_csv` (the local-files route), not a mounted connector: the data is authored in this repository and no external system holds it. Source: `R-01`, `R-02`, `add-or-update-source` § Local-files route.
- `D-02` Four connections — `ecommerce_customers`, `ecommerce_products`, `ecommerce_orders`, `ecommerce_order_items` — each with its own `[sources.<connection>]` section, `bucket_url=file:///workspace/landing/ecommerce` and a `file_glob` naming its one file: the local-files route carries exactly one glob per connection, so a feed per connection keeps every config key canonical rather than inventing per-resource keys. Source: `add-or-update-source` § Local-files route.
- `D-03` One pipeline, `ingestion/ecommerce_pipeline.py`, with four resources — `customers`, `products`, `orders`, `order_items` — each reading its own connection's section, landing into the single dataset `src_ecommerce`: one pipeline keeps one state directory and one run for a single coherent source. Source: `R-02`; `ingestion-artifact-paths.md`.
- `D-04` Write disposition is `replace` for all four resources, with no primary key, no cursor and no history: each CSV is a full snapshot of its table and carries no change-feed identity, so a reload must replace rather than accumulate. Source: Requirement decision `bronze write disposition = replace`.
- `D-05` Schema contract is `columns: freeze`, `tables: evolve`, `data_type: freeze` — the default in the platform template, inherited rather than overridden. Source: platform `dlt.md` § Authoring.
- `D-06` All four resources load in full (`Load: full` in the plan): the committed CSVs are themselves the sample, and `R-02` compares each landed row count to its CSV's row count. Source: `R-02`; Requirement decision `source file size`.
- `D-07` `DLT_INGEST_LIMIT` stays in the pipeline as the template's safety knob and is unset for the load; no `dev_mode`, no hard-coded `.add_limit()`. Source: platform `dlt.md` § Authoring; `generating-dlt-pipeline` § Audit rules.

## Rejected

- One connection with per-resource globs under invented config keys — the canonical section keys are `bucket_url` and `file_glob`, so this would put non-standard keys in a file only `add-or-update-source` writes.
- Four separate pipelines, one per file — needless duplicate state directories, four runs and four datasets for one source.
- `merge` with a primary key — the CSVs carry no update timestamp and every load replaces them wholesale, so merge would add state without changing an outcome.

## Consumers

- `stg_ecommerce__customers`, `stg_ecommerce__products`, `stg_ecommerce__orders`, `stg_ecommerce__order_items` read these tables as dbt sources.

## History

- 2026-10-29 — intent `new-intent-3a74ac3d` — created the pipeline design. terms: repository has no `CONTEXT.md` or glossary rules, so no terms recorded (repository needs onboarding).
