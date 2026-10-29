# Verification: How are you boss

## Discovery

<!-- Written by designing: each discovery result, and any slice with its limits. Keep as found. -->

- No input table was profiled at design time, because the intent's inputs do not exist yet: `R-01` authors the four source CSVs in this intent, and until they land there is no relation to read. The sandbox `ephm_testing_new-intent-3a74ac3d.duckdb` and the Domain `demo.duckdb` were both checked for `customers`, `products`, `orders`, `order_items` under schema `src_ecommerce` and found to hold none — this source has never been loaded. Profiling of each landed bronze table, with its Bronze Adequacy verdict, therefore happens in Plan task 3 (after the load) and its results are appended here before verification. — `lakehouse_schema(target=ephemeral, schemaName=src_ecommerce, schemaType=tables)` and the same call with `target=domain`: both returned no relations.
- dlt runtime present: `dlt 1.30.0`; `dlt.sources.filesystem.read_csv` and `filesystem` import and expose the `items`/`pandas_kwargs` and `bucket_url`/`file_glob` arguments the local-files template uses. — `python -c "import dlt, inspect; from dlt.sources.filesystem import read_csv, filesystem; print(dlt.__version__); print(inspect.signature(read_csv))"` → `1.30.0`, signature printed.
