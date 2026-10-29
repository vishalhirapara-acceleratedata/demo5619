# Plan: How are you boss

**Goal:** Author four ecommerce CSVs, land them in the sandbox through a dlt pipeline, and model a sales fact at order-line grain plus an order-level mart on top of dbt staging and dimension models.

**Requirement:** `docs/requirements/2026-10-29-how-are-you-boss-3a74ac3d.md`

**Constraints:**
- Platform is `duckdb_local`: every write goes to the sandbox file; the Domain database is read-only and never opened for writing.
- dbt's only target is `dev`; no `--defer`, nothing under `/cache`, and no profile is authored or edited.
- Contracts are enforced on marts with explicit types; DuckDB does not coerce an expression, so every output is cast to its declared type.
- Bronze tables land only in `src_ecommerce`; dbt models publish to `staging` and `marts`.
- No archive, schedule or orchestration item is created (Requirement § Out of scope).
- dlt artifacts sit at their canonical paths (`ingestion/`, `ingestion/docs/<connection>.yml`); the dbt project is `transformation/`.

## Scope and impact

| Artifact | Kind | Action | Requirements | Design record | Gate |
| --- | --- | --- | --- | --- | --- |
| `landing/ecommerce/customers.csv`, `products.csv`, `orders.csv`, `order_items.csv` | seed (plain CSV input) | create | `R-01` | `docs/design/pipelines/ecommerce_pipeline.md` | `python -c` header/row assertion over the four files |
| `ingestion/.dlt/config.toml` (four `[sources.*]` sections) | project-config | create | `R-02` | `docs/design/pipelines/ecommerce_pipeline.md` | `add-or-update-source` local-files route: section values read back |
| `ingestion/ecommerce_pipeline.py`, `ingestion/docs/*.yml`, `ingestion/requirements.txt` | pipeline | create | `R-02` | `docs/design/pipelines/ecommerce_pipeline.md` | `assert_destination.py` + `run_bronze_tier1_tests.py --audit` + preview |
| dbt project (`transformation/dbt_project.yml`, `profiles` untouched) | project-config | create | `R-08` | `code is contract` | `dbt parse` |
| `stg_ecommerce__customers`, `stg_ecommerce__products`, `stg_ecommerce__orders`, `stg_ecommerce__order_items` | model | create | `R-01` | `docs/design/models/stg_ecommerce__*.md` | `dbt build --select <model>` |
| `dim_customers`, `dim_products` | model | create | `R-07`, `R-08` | `docs/design/models/dim_customers.md`, `dim_products.md` | `dbt build --select <model>` |
| `fct_order_lines` | model | create | `R-03`, `R-04`, `R-06`, `R-08` | `docs/design/models/fct_order_lines.md` | `dbt build --select fct_order_lines` |
| `mart_orders` | model | create | `R-05`, `R-08` | `docs/design/models/mart_orders.md` | `dbt build --select mart_orders` |

**Change impact:** none downstream. The repository held no models, sources or marts before this intent (`lakehouse_schema` on both `ephemeral` and `domain` returned zero relations), so nothing existing is read differently or broken.

## Tasks

### Task 1: the four sample CSVs

**Requirements:** `R-01` · **Design:** `docs/design/pipelines/ecommerce_pipeline.md` · **Skill:** none (plain data files, no authoring skill owns them) · **Depends on:** none

- [ ] Author `landing/ecommerce/customers.csv` with header `customer_id,first_name,last_name,email,country_code,signup_date`; at least 10 data rows; `customer_id` unique integers.
- [ ] Author `landing/ecommerce/products.csv` with header `product_id,product_name,category,list_price,created_at`; at least 10 data rows; `product_id` unique integers; `list_price` a positive decimal.
- [ ] Author `landing/ecommerce/orders.csv` with header `order_id,customer_id,order_date,status`; at least 15 data rows; every `status` drawn from `completed`, `pending`, `cancelled`, `refunded`, with at least one row of each so the population rule has something to exclude.
- [ ] Author `landing/ecommerce/order_items.csv` with header `order_id,line_number,product_id,quantity,unit_price,discount_amount`; at least 40 data rows; `(order_id, line_number)` unique; every `discount_amount` in `[0, quantity*unit_price]`.
- [ ] Include in `order_items.csv` at least one line whose `customer_id` (via its order) has no `customers` row and at least one line whose `product_id` has no `products` row, so `R-06` has a real case to prove; note both in the task evidence.
- [ ] Run `python -c "import csv;spec={'customers':['customer_id','first_name','last_name','email','country_code','signup_date'],'products':['product_id','product_name','category','list_price','created_at'],'orders':['order_id','customer_id','order_date','status'],'order_items':['order_id','line_number','product_id','quantity','unit_price','discount_amount']};import io;
[(_ for _ in ()).throw(AssertionError(n+' header '+str(next(csv.reader(open('landing/ecommerce/'+n+'.csv'))))+' != '+str(h))) for n,h in spec.items() if next(csv.reader(open('landing/ecommerce/'+n+'.csv')))!=h];print('CSV_HEADERS_OK')"`; expect `CSV_HEADERS_OK`.
- [ ] Run `python -c "import csv;[print(n, sum(1 for _ in open('landing/ecommerce/'+n+'.csv'))-1) for n in ['customers','products','orders','order_items']]"`; expect four non-zero row counts.
- [ ] Commit the four CSVs.

### Task 2: dlt destination and the four local-files connections

**Requirements:** `R-02` · **Design:** `docs/design/pipelines/ecommerce_pipeline.md` · **Skill:** `configuring-dlt-destination` then `add-or-update-source` · **Depends on:** Task 1

- [ ] Run `configuring-dlt-destination`: confirm `[destination.duckdb]` needs nothing in `ingestion/.dlt/config.toml` for this platform and record it as a check.
- [ ] Run `add-or-update-source` in the local-files route for each of `ecommerce_customers`, `ecommerce_products`, `ecommerce_orders`, `ecommerce_order_items`: `connector = "filesystem"`, `connector_source = "dlt-builtin"`, `entry_point = "filesystem"`, `bucket_url = "file:///workspace/landing/ecommerce"`, `file_glob` naming that connection's one file, `schema = "src_ecommerce"`.
- [ ] Read the four sections back from `ingestion/.dlt/config.toml` without reading any secret; expect all four present with those values and no secret invented (the route is credential-free).
- [ ] Commit `ingestion/.dlt/config.toml`.

### Task 3: the dlt pipeline, its load and its documentation

**Requirements:** `R-02` · **Design:** `docs/design/pipelines/ecommerce_pipeline.md` · **Skill:** `generating-dlt-pipeline` · **Depends on:** Task 2

- [ ] Author `ingestion/ecommerce_pipeline.py` from `_shared/platforms/duckdb_local/templates/dlt-pipeline-local-files.py`: four resources `customers`, `products`, `orders`, `order_items`, each `(filesystem(bucket_url=dlt.config['sources.<connection>.bucket_url'], file_glob=dlt.config['sources.<connection>.file_glob']) | read_csv()).with_name('<resource>')`, `write_disposition="replace"`, `schema_contract` default, `# why:` above the non-default write disposition.
- [ ] Author `ingestion/docs/ecommerce_customers.yml`, `ecommerce_products.yml`, `ecommerce_orders.yml`, `ecommerce_order_items.yml`, documenting every emitted field including `_dlt_id` and `_dlt_load_id`; author `ingestion/requirements.txt` bare-pinned.
- [ ] Run `python "$SKILL_DIR/../../scripts/validate_schema_contract.py" ingestion/ecommerce_pipeline.py`; expect `SCHEMA_CONTRACT_OK`.
- [ ] Run the safety run, then the load `Load: full` (all rows of all four CSVs), then `python "$SKILL_DIR/../../scripts/assert_destination.py" --pipeline ecommerce_pipeline` and `python "$SKILL_DIR/../../scripts/run_bronze_tier1_tests.py" --dataset src_ecommerce --audit`; expect `DESTINATION_OK` and four `PASS` lines.
- [ ] Run `bash "$SKILL_DIR/../../scripts/vd-dlt-preview.sh" --dataset src_ecommerce`; expect `[vd-dlt-preview] wrote`.
- [ ] Run the pipeline audit rules and record one finding per rule; expect `failed_critical: 0`.
- [ ] Run the acceptance condition of `R-02`: compare each landed table's row count with its CSV's data-row count; expect equality for all four.
- [ ] Append the Bronze Adequacy profiling result for all four landed tables to `docs/verifications/2026-10-29-how-are-you-boss-3a74ac3d.md` § Discovery.
- [ ] Commit the pipeline, the four docs YAMLs and `requirements.txt`.

### Task 4: the dbt project

**Requirements:** `R-08` · **Design:** `code is contract` · **Skill:** `generating-dbt-model` · **Depends on:** Task 3

- [ ] Author `transformation/dbt_project.yml` with `profile: "{{ env_var('DBT_PROFILE_NAME', 'default') }}"`, `model-paths: [models]`, `test-paths: [tests]`, and schemas `staging` (views) and `marts` (tables).
- [ ] Run `python "$SKILL_DIR/../../scripts/ensure_gitignore.py" --capability dbt` from the skill directory; expect `updated` or `unchanged`, and stage `.gitignore` when it reports `updated`.
- [ ] Run `dbt parse`; expect exit 0.
- [ ] Commit `transformation/dbt_project.yml` and `.gitignore` if it changed.

### Task 5: dbt sources and the four staging models

**Requirements:** `R-01`, `R-08` · **Design:** `docs/design/models/stg_ecommerce__customers.md`, `stg_ecommerce__products.md`, `stg_ecommerce__orders.md`, `stg_ecommerce__order_items.md` · **Skill:** `generating-dbt-model` · **Depends on:** Task 4

- [ ] Register the four landed tables as a dbt source `ecommerce` with `schema: src_ecommerce` in `transformation/models/staging/ecommerce/_ecommerce__sources.yml`, bare table rows only.
- [ ] Author `stg_ecommerce__customers.sql` + `.yml`, `stg_ecommerce__products.sql` + `.yml`, `stg_ecommerce__orders.sql` + `.yml`, `stg_ecommerce__order_items.sql` + `.yml`, each reading only `source('ecommerce', '<table>')`, renaming and casting per the design record.
- [ ] Author tests: `not_null` on each staging key (`customer_id`, `product_id`, `order_id`, and `order_id` + `line_number`), plus `accepted_values` on `orders.status` over `completed`, `pending`, `cancelled`, `refunded`.
- [ ] Author dbt unit tests per staging model covering the cast of each typed column and the `status` pass-through, with fixtures that would fail a model that dropped or filtered a row.
- [ ] Run `dbt show --inline "select count(*) as n from {{ source('ecommerce','customers') }}" --limit 1` (and the same for `products`, `orders`, `order_items`); expect non-zero counts, proving each source resolves.
- [ ] Run `dbt build --select stg_ecommerce__customers stg_ecommerce__products stg_ecommerce__orders stg_ecommerce__order_items --exclude test_type:unit` then `dbt test --select stg_ecommerce__customers+ ... ,test_type:unit`; expect zero failures.
- [ ] Run the acceptance condition of `R-01`: each staging row count equals its CSV data-row count.
- [ ] Commit the sources file and the eight model files.

### Task 6: the customer and product dimensions

**Requirements:** `R-07`, `R-08` · **Design:** `docs/design/models/dim_customers.md`, `dim_products.md` · **Skill:** `generating-dbt-model` · **Depends on:** Task 5

- [ ] Author `dim_customers.sql` + `.yml` and `dim_products.sql` + `.yml` in `transformation/models/marts/`, tables with `contract: {enforced: true}`, explicit casts, `access: public`.
- [ ] Author tests: `unique` and `not_null` on `customer_id` and `product_id`, `not_null` on `dim_customers.email`.
- [ ] Author dbt unit tests per dimension covering the full column projection and a row with a NULL optional attribute.
- [ ] Run `dbt build --select dim_customers dim_products --exclude test_type:unit` then `dbt test --select dim_customers dim_products,test_type:unit`; expect zero failures.
- [ ] Run the acceptance condition of `R-07`: each dimension's row count equals the distinct id count in its bronze table.
- [ ] Commit both models and their YAMLs.

### Task 7: the order-line fact

**Requirements:** `R-03`, `R-04`, `R-06`, `R-08` · **Design:** `docs/design/models/fct_order_lines.md` · **Skill:** `generating-dbt-model` · **Depends on:** Task 6

- [ ] Author `fct_order_lines.sql` + `.yml` in `transformation/models/marts/`: order lines LEFT JOINed to completed orders, LEFT JOINed to both dimensions, publishing `order_id`, `line_number`, `order_date`, `customer_id`, `customer_country_code`, `product_id`, `product_category`, `quantity`, `unit_price`, `discount_amount`, `gross_amount`, `net_revenue` — every measure cast to its declared type.
- [ ] Author `transformation/tests/assert_fct_order_lines_grain_unique.sql` asserting `(order_id, line_number)` has no duplicate.
- [ ] Author tests: `not_null` on `order_id`, `line_number`, `quantity`, `unit_price`, `discount_amount`, `gross_amount`, `net_revenue`, `order_date`; `relationships` from `customer_id` to `dim_customers` and `product_id` to `dim_products`, each with `severity: warn`.
- [ ] Author dbt unit tests covering: a completed order line kept; a pending, a cancelled and a refunded order line each excluded; an unmatched `customer_id` kept with NULL customer columns; an unmatched `product_id` kept with NULL product columns; a zero-discount line whose `net_revenue` equals `gross_amount`; a full-discount line whose `net_revenue` is 0.
- [ ] Run `dbt build --select fct_order_lines --exclude test_type:unit` then `dbt test --select fct_order_lines,test_type:unit`; expect zero failures and zero warnings beyond the two `relationships` warnings each documented by the fixtures.
- [ ] Run the acceptance conditions: `R-03` row count equals `order_items` joined to `completed` orders and the grain test passes; `R-04` an independent recomputation of `sum(quantity*unit_price - discount_amount)` from bronze equals the fact's `sum(net_revenue)` exactly; `R-06` the fact row count equals the completed-order-line count even with the unmatched fixture rows landed.
- [ ] Commit the model, its YAML and the singular test.

### Task 8: the order-level mart

**Requirements:** `R-05`, `R-08` · **Design:** `docs/design/models/mart_orders.md` · **Skill:** `generating-dbt-model` · **Depends on:** Task 7

- [ ] Author `mart_orders.sql` + `.yml` in `transformation/models/marts/`, rolling up `fct_order_lines` by `order_id`: `order_date`, `customer_id`, `line_count`, `total_quantity`, `gross_revenue`, `total_discount`, `net_revenue`, each cast to its declared type, `contract: {enforced: true}`, `access: public`.
- [ ] Author tests: `unique` and `not_null` on `order_id`, `not_null` on `net_revenue`, `relationships` from `customer_id` to `dim_customers` with `severity: warn`.
- [ ] Author dbt unit tests covering a single-line order and a multi-line order, proving `line_count` and every sum.
- [ ] Run `dbt build --select mart_orders --exclude test_type:unit` then `dbt test --select mart_orders,test_type:unit`; expect zero failures.
- [ ] Run the acceptance condition of `R-05`: `mart_orders` order key unique, and `sum(net_revenue)` over `mart_orders` equals `sum(net_revenue)` over `fct_order_lines`.
- [ ] Commit the model and its YAML.

## Execution evidence
