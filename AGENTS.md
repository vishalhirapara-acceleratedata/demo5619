# demo5619 — Agent Conventions

A first cut of this domain's own dbt/dlt conventions. Edit this file directly as the project's needs diverge from the starting defaults below — it belongs to the domain, not to any template.

## Medallion Layers

- **Bronze** — raw, untransformed data as ingested by dlt. One dlt resource per source table; no renaming, casting, or business logic.
- **Silver** — dbt `staging` and `intermediate` models. Staging renames and casts 1:1 with a bronze table; intermediate applies business logic and joins between staging models, with no grain commitment of its own.
- **Gold** — dbt `marts` models: grain-committed facts and conformed dimensions, ready for consumption.

## Model Naming

| Prefix | Layer | Responsibility |
| --- | --- | --- |
| `stg_` | Staging | 1:1 with a source table. Rename, cast, light cleanup. No business logic. |
| `int_` | Intermediate | Business logic and joins between staging models. No grain commitment. |
| `fct_` | Fact | Grain-committed measurable events. |
| `dim_` | Dimension | Descriptive entities, conformed across facts. |

Staging models follow `stg_<source>__<entity>` (double underscore separates source from entity, e.g. `stg_salesforce__accounts`). Intermediate and mart models name the entity directly (`int_account_segments`, `fct_opportunity`, `dim_account`). No `_fact`/`_dimension` suffixes — the prefix already carries that.

## File Organization

- `models/staging/<source>/` — one directory per source system.
- `models/intermediate/`
- `models/marts/<area>/` — grouped by business area, not by source.

Each model ships with a colocated schema YAML carrying its column tests and description — never a bare `.sql` file with no tests.

## Testing

Every primary key gets `unique` and `not_null`. Foreign keys to a conformed dimension get `relationships`. Add a source freshness check where the source is expected to land on a schedule.

## SQL Style

Lowercase keywords, `snake_case` identifiers, explicit `join`/`on` (never implicit joins in the `where` clause), one clause per line for anything beyond a trivial select.
