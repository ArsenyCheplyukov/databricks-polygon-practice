# Layer 5 — Unity Catalog OSS

**Coverage:** the three-level namespace + governance model you'll meet on the platform.

## Objectives

1. Connect to the Unity Catalog server via `uc_session()` and create a schema + external Delta table under the `unity` catalog.
2. Write to the table through the `catalog.schema.table` namespace and read it back.
3. Run `DESCRIBE` and `SHOW TABLES` and confirm the three-level name resolves.

## How to run

```bash
make up-unity     # starts the UC server on :8080
make test-l5
```

## What to observe

- `unity` is the catalog registered in `common/spark_session.py` via `UCSingleCatalog`.
- Tables are created as **external** Delta tables because managed tables are an experimental OSS UC feature.
- `DESCRIBE TABLE EXTENDED` shows the full `unity.schema.table` name and `EXTERNAL` type.

## What OSS UC does NOT give you

The proprietary automatic lineage graph and UI are part of Databricks Free Edition / platform — not this local OSS server.

## Self-check

Tests pass when:

- `task_1` returns a fully-qualified `unity.schema.table` name that appears in `SHOW TABLES`.
- `task_2` writes N rows and reports N back.
- `task_3` finds the columns and table name via `DESCRIBE` / `SHOW`.
