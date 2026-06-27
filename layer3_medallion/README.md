# Layer 3 — Medallion pipeline

**Coverage:** how to structure the pipelines you migrate.

## Objectives

1. **Bronze:** ingest raw messy JSON/CSV append-only, minimal transformation, add ingestion metadata.
2. **Silver:** clean, dedupe, conform types/dates, apply business keys; use MERGE for idempotent upserts.
3. **Gold:** business aggregates (premium & claims by state/product/segment).
4. **Idempotency:** re-running the whole pipeline must not change gold.

## How to run

```bash
make test-l3
```

## What to observe

- Bronze row counts match raw plus metadata columns.
- Silver deduplicates messy/duped inputs and has correct types.
- Gold aggregates tie out to an independent calculation.
- Re-running the pipeline produces identical gold output.

## Self-check

Tests pass when:

- bronze row counts equal raw counts.
- silver has no duplicates by business key and dates are parsed.
- gold aggregates match expected values.
- a second full pipeline run leaves gold unchanged.
