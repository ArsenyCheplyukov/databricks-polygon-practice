# Layer 4 — Data lineage

**Coverage:** "where did this number come from?" answered automatically.

## Objectives

1. Run the Layer 3 medallion pipeline through the OpenLineage-instrumented Spark session.
2. Emit lineage events to Marquez.
3. Query the Marquez API to fetch the lineage graph for a gold table.

## How to run

Layer 4 runs in an isolated Spark 4.0.0 sidecar because OpenLineage 1.50.0 does not
capture Delta dataset I/O on Spark 4.1.2.

```bash
make up-lineage
make test-l4
```

Open Marquez UI at http://localhost:3000 and trace gold → silver → bronze.

## What to observe

- Each pipeline step emits a `RUN` event to Marquez.
- The lineage graph contains dataset nodes for bronze, silver, and gold tables.
- Column-level lineage edges connect corresponding columns across layers.

## Self-check

Tests pass when:

- lineage events are emitted for each job.
- the Marquez API returns a graph with bronze → silver → gold edges for the current run.
- the gold dataset has at least one column-level lineage input field.

## Isolation

Layer 4 uses a dedicated `spark-lineage` service (Spark 4.0.0 + Delta 4.0.0 +
OpenLineage 1.50.0). Layers 1–3 and Layer 5 remain on the primary Spark 4.1.2
container. See `VERSIONS.md` for the full version table.
