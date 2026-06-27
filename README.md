# Databricks Internals Practice Polygon

Local, offline Docker sandbox for practicing the Databricks-internals half that runs on a laptop: Delta Lake, medallion pipelines, data lineage, and Unity Catalog OSS. This is the **internals lab** — platform surface (notebooks service, clusters, Workflows, proprietary UC lineage graph) is out of scope and practiced separately on Databricks Free Edition.

## Layer map

| Layer | Coverage |
|-------|----------|
| **Layer 1 — Delta core** | The substrate every migrated table lands on: transaction log, ACID, time travel. |
| **Layer 2 — Delta ops** | Write-side verbs used in every migrated pipeline: MERGE, schema enforcement/evolution, OPTIMIZE, ZORDER, VACUUM. |
| **Layer 3 — Medallion** | How to structure migrated pipelines: bronze → silver → gold, idempotent end-to-end. |
| **Layer 4 — Lineage** | "Where did this number come from?" answered automatically with OpenLineage + Marquez. Runs in an isolated Spark 4.0.0 sidecar. |
| **Layer 5 — Unity Catalog OSS** | Three-level namespace + governance model via local OSS UC server. |

## Quickstart

```bash
# Start the Spark/Jupyter+pytest container
make up

# Generate small synthetic insurance dataset
make generate-data

# Run all tests
make test

# Per-layer tests
make test-l1
make test-l2
make test-l3
make test-l4   # needs lineage profile
make test-l5   # needs unity profile
```

### Lineage layer

```bash
make up-lineage   # starts Marquez (API :5000, Web :3000)
make test-l4
```

Open Marquez UI at http://localhost:3000 and trace gold → silver → bronze.

### Unity Catalog layer

```bash
make up-unity     # starts UC server on :8080
make test-l5
```

## Bridges to what you already know

- Transaction log ≈ WAL / commit log.
- Time travel ≈ persisted MVCC snapshots.
- Data skipping via log stats ≈ Postgres statistics + pruning.
- `MERGE` ≈ upsert / SCD.
- `OPTIMIZE` ≈ heap/index compaction.
- Lineage graph ≈ query plan provenance, but persisted and queryable.

## Learning mechanics

Each layer has `tasks.py` with numbered stubs. Implement the stubs, then run the tests. Reference solutions live in `layer*/solution/` and are git-ignored; to verify the test suite itself, run with `POLYGON_USE_SOLUTION=1`.

## Repository hygiene

- `**/solution/` is git-ignored so answers never leak into the public repo.
- Generated data and Spark scratch dirs are git-ignored.
- Agent/prompt files are git-ignored.
