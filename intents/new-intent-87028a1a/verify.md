# Certification: Sales Data Mart Pipeline

## Certification

`verdict: certified` at `469e2f2`, intent `new-intent-87028a1a`.

All 5 requirements met, all 20 data tests pass, all acceptance checks verified by independent recomputation from the source. No unit tests — not applicable (no unit-test artifacts in this project). `dbt_project_evaluator` not installed — not applicable. Baseline cross-check: not applicable (no `/cache/prod-selection/manifest.json`). No dev artifacts found. Docs descriptions verified — all complete.

## Coverage

| Item | Evidence | Result | At |
| --- | --- | --- | --- |
| `R-01` Seed rows non-zero | `SELECT COUNT(*) FROM orders` (ephemeral) | 25 rows | `469e2f2` |
| `R-02` stg_orders builds, 0 test failures | `dbt build --select stg_orders --target dev` | exit 0, PASS=12 (1 view + 11 tests) | `469e2f2` |
| `R-02` stg_orders row count matches seed | `SELECT COUNT(*) FROM stg_orders` vs `FROM orders` | both 25 | `469e2f2` |
| `R-03` mart_sales one row per order_id | `SELECT COUNT(*), COUNT(DISTINCT order_id) FROM mart_sales` | 20 = 20, grain_check = UNIQUE | `469e2f2` |
| `R-03` mart row count = source distinct orders | `SELECT COUNT(DISTINCT order_id) FROM orders` | 20 = mart_rows 20 | `469e2f2` |
| `R-04` total_revenue formula correct (0 mismatches) | `SELECT ... HAVING mart.total_revenue IS DISTINCT FROM source_recomputed` | 0 rows returned | `469e2f2` |
| `R-04` total_items formula correct (0 mismatches) | `SELECT ... HAVING mart.total_items IS DISTINCT FROM SUM(stg.quantity)` | 0 rows returned | `469e2f2` |
| `R-04` total_revenue, total_items, order_status columns exist with correct types | `DESCRIBE mart_sales` | DECIMAL(10,2), INTEGER, VARCHAR — match contract | `469e2f2` |
| `R-05` YAML docs complete, no placeholders | Python yaml.safe_load walk over all schema.yml files | All descriptions OK | `469e2f2` |
| Seed `orders` | `dbt seed --select orders --target dev` | exit 0, INSERT 25 | `79182fa` |
| Model `stg_orders` (silver view) | `dbt build --select stg_orders --target dev` | exit 0, PASS=12 | `55c7837` |
| Model `mart_sales` (gold table, enforced contract) | `dbt build --select mart_sales --target dev` | exit 0, PASS=10 | `469e2f2` |
| Project config `dbt_project.yml` | `dbt parse --target dev` | exit 0, no deprecations | `79182fa` |
| Docs generation | `dbt docs generate --static --target dev` | exit 0, catalog.json written, published to /data/ephm_dbt_docs | `469e2f2` |

## Gate results

| Gate | Command | Exit | Outcome |
| --- | --- | --- | --- |
| Data tests — impacted closure | `dbt test --select stg_orders mart_sales --target dev` | 0 | PASS=20 |
| Unit tests | (none in project) | n/a | not applicable |
| Dev-artifact scan | Python scan for dev_mode, .add_limit(), hardcoded targets | 0 | CLEAN |
| dbt_project_evaluator | (package not installed) | n/a | not applicable |
| Baseline cross-check | (no /cache/prod-selection/manifest.json) | n/a | not applicable |
| Population closure | stg_rows=25=seed_rows; mart_rows=20=source_distinct_orders | n/a | PASS |
| Grain uniqueness (independent) | COUNT(*) = COUNT(DISTINCT order_id) on mart_sales | n/a | UNIQUE |
| Formula recomputation — total_revenue | 0 mismatches across all 20 orders | n/a | PASS |
| Formula recomputation — total_items | 0 mismatches across all 20 orders | n/a | PASS |
| Docs match data | DESCRIBE mart_sales vs schema.yml + design record D-02–D-08 | n/a | PASS |
| Docs placeholder check | yaml.safe_load walk over all 3 schema.yml files | n/a | PASS |
| Scope check | Only files named in Plan scope rows changed | n/a | PASS |
| Contract promotion | mart_sales: public + enforced + all data_types declared; stg_orders: protected, no contract required | n/a | PASS |
| Currency check | ship_currency.py --rows .agents_tmp/ship-currency-rows.json (post-approval run) | 0 | fresh=true, stale=[] |
| Pull request | gh pr create --base main --head intent/new-intent-87028a1a | 0 | https://github.com/vishalhirapara-acceleratedata/demo5619/pull/1 |
