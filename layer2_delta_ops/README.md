# Layer 2 — Delta operations

**Coverage:** the write-side verbs you'll use in every migrated pipeline.

## Objectives

1. `MERGE` upsert — apply inserts + updates to a target with no duplicates.
2. `UPDATE`/`DELETE` and observe copy-on-write file rewrites.
3. Schema enforcement (bad-schema write rejected) and schema evolution (`mergeSchema`).
4. `OPTIMIZE` file compaction on a small-files table.
5. `ZORDER BY` a high-selectivity column and measure data skipping.
6. `VACUUM` and the time-travel trade-off.

## How to run

```bash
make test-l2
```

## What to observe

- `MERGE` resolves conflicts without duplicates.
- A schema-violating write raises; `mergeSchema=True` adds columns.
- `OPTIMIZE` reduces the number of files.
- `ZORDER` reduces files read for a selective filter.
- `VACUUM` physically deletes files no longer referenced by active versions.

## Self-check

Tests pass when:

- merge final rows are correct and unique.
- bad-schema write raises an error.
- `OPTIMIZE` reduces file count.
- `ZORDER` reduces input files for a selective query.
- `VACUUM` removes old files.
