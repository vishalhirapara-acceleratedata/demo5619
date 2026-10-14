# Plan: Sales Data Mart Pipeline

**Goal:** Build a demo sales data mart on DuckDB-local with agent-created CSV seed data, a staging model, and a gold mart at order grain.

**Constraints:**
- Platform: DuckDB-local (`dbt_duckdb_local` profile, sandbox at `VD_EPHM_DUCKDB_LOCAL_PATH`)
- Gold layer: `contract: { enforced: true }`, explicit column list, `unique` + `not_null` on grain key
- No writes to Domain (production) target
- Medallion guardrails: seeds → stg (view) → mart (table)
- All models and seeds must have YAML documentation

## Scope and impact

| Artifact | Kind | Action | Requirements | Design record | Gate |
| --- | --- | --- | --- | --- | --- |
| `orders` | seed | create | R-01 | code is contract | `dbt seed --select orders` — exit 0, non-zero row count |
| `stg_orders` | model | create | R-02 | `docs/design/models/stg_orders.md` | `dbt build --select stg_orders` — exit 0, 0 test failures |
| `mart_sales` | model | create | R-03, R-04 | `docs/design/models/mart_sales.md` | `dbt build --select mart_sales` — exit 0, unique+not_null on order_id pass |
| dbt project config | project-config | create | R-01–R-05 | code is contract | `dbt parse` — exit 0 |
| YAML docs | project-config | create | R-05 | code is contract | `dbt docs generate` — exit 0 |

**Change impact:** No existing artifacts impacted — fresh build. No downstream consumers.

## Tasks

### Task 1: dbt project scaffold + orders seed

**Requirements:** `R-01` · **Design:** code is contract · **Skill:** generating-dbt-model
**Dependencies:** none

- [ ] Initialise the dbt project: `dbt_project.yml`, `profiles.yml` reference, directory structure (`models/staging/`, `models/marts/`, `seeds/`)
- [ ] Create `seeds/orders.csv` with ~20 realistic demo rows (columns: `order_id`, `order_date`, `customer_id`, `customer_name`, `product_id`, `product_name`, `category`, `quantity`, `unit_price`, `order_status`)
- [ ] Create `seeds/schema.yml` with description and column docs for `orders`
- [ ] Run `dbt seed --select orders`; expect exit 0 and a non-zero row count confirmed by `SELECT COUNT(*) FROM orders`
- [ ] Commit and push `dbt_project.yml`, `seeds/orders.csv`, `seeds/schema.yml`

### Task 2: stg_orders staging model

**Requirements:** `R-02` · **Design:** `docs/design/models/stg_orders.md` · **Skill:** generating-dbt-model
**Dependencies:** Task 1

- [ ] Author `models/staging/stg_orders.sql` — reads `ref('orders')`, casts `order_date` to DATE, `quantity` to INT, `unit_price` to DECIMAL(10,2), all other columns VARCHAR
- [ ] Author `models/staging/schema.yml` with description and column docs for `stg_orders`
- [ ] Run `dbt build --select stg_orders`; expect exit 0 and 0 test failures
- [ ] Commit and push `models/staging/stg_orders.sql`, `models/staging/schema.yml`

### Task 3: mart_sales gold mart

**Requirements:** `R-03`, `R-04`, `R-05` · **Design:** `docs/design/models/mart_sales.md` · **Skill:** generating-dbt-model
**Dependencies:** Task 2

- [ ] Author `models/marts/mart_sales.sql` — reads `ref('stg_orders')`, groups by `order_id`, exposes `order_date`, `customer_id`, `customer_name`, `total_revenue` (SUM of quantity × unit_price), `total_items` (SUM of quantity), `order_status` (MIN); materialised as `table` with `contract: { enforced: true }`
- [ ] Author `models/marts/schema.yml` with description and column docs; include `unique` + `not_null` tests on `order_id`
- [ ] Run `dbt build --select mart_sales`; expect exit 0, unique + not_null tests on `order_id` pass
- [ ] Run `dbt docs generate`; expect exit 0
- [ ] Commit and push `models/marts/mart_sales.sql`, `models/marts/schema.yml`

## Execution evidence

- Task 1: `dbt seed --select orders --target dev` — exit 0 — seeds/orders.csv — 25 rows inserted (INSERT 25)
- Task 1: `SELECT COUNT(*) FROM orders` (ephemeral) — 25 rows confirmed
- Task 1: workspace marker — status: created
- Task 2: `dbt build --select stg_orders --target dev` — exit 0 — models/staging/stg_orders.sql — PASS=12 (1 view + 11 tests)
- Task 3: `dbt build --select mart_sales --target dev` — exit 0 — models/marts/mart_sales.sql — PASS=10 (1 table + 9 tests including unique_mart_sales_order_id)
- Task 3: `SELECT COUNT(*) FROM mart_sales` (ephemeral) — 20 rows (matches 20 distinct order_ids)
- Task 3: spot-check ORD-002 total_revenue=534.97 ✓, ORD-005=225.97 ✓, ORD-020=89.97 ✓
- Task 3: `dbt docs generate --static --target dev` — exit 0 — target/catalog.json written; static_index.html published to /data/ephm_dbt_docs
- Task 3: docs placeholder check — All descriptions OK
