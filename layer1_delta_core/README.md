# Layer 1 — Delta core & the transaction log

**Coverage:** the substrate every migrated table lands on + where lineage/ACID begin.

## Objectives

1. Write a Delta table, then append, overwrite, update, and delete — each as a separate commit.
2. Inspect `_delta_log` to see which actions each operation produced.
3. Read earlier table states with `versionAsOf` and `timestampAsOf`.
4. Use `DESCRIBE HISTORY` to summarize what changed per version.
5. Contrast Parquet and Delta behavior under a half-written overwrite.

## How to run

```bash
make test-l1
```

## What to observe

- Each write operation creates a new commit version.
- `_delta_log/*.json` contains `add`, `remove`, `metaData`, `protocol`, and `commitInfo` actions.
- Time travel returns the exact row set from an earlier version.
- A failed/half-written Parquet overwrite can leave mixed data, while Delta stays atomic.

## Self-check

Tests pass when:

- version count matches the number of operations.
- time-travel row counts match the pre-change state.
- overwrite commit contains both `remove` and `add` actions.
- `metaData` schema matches the table schema.
