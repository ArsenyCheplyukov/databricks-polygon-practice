# Resolved versions

| Component | Resolved version | Verification status |
|-----------|------------------|---------------------|
| Python | 3.13 | Verified (primary + lineage sidecar containers) |
| JDK | Temurin 21 | Verified |
| PySpark (Layers 1–3, 5) | 4.1.2 | Verified |
| Delta Lake (Layers 1–3, 5) | 4.1.0 | Verified |
| PySpark (Layer 4 sidecar) | 4.0.0 | Verified |
| Delta Lake (Layer 4 sidecar) | 4.0.0 | Verified |
| OpenLineage Spark | 1.50.0 | Verified on Spark 4.0.0 sidecar |
| OpenLineage namespace | insurance-polygon (default) | Verified; tests use unique namespaces |
| Marquez API/Web | 0.51.1 | Verified |
| Marquez DB | postgres:15 | Verified |
| Unity Catalog server | main-2f2e32d | Verified |
| Unity Catalog Spark connector | 0.4.0 | Verified; uses external tables because managed tables are experimental in OSS UC |

## Per-layer status

| Layer | Status | Notes |
|-------|--------|-------|
| Layer 1 — Delta core | Verified | `make test-l1` green on Spark 4.1.2 |
| Layer 2 — Delta ops | Verified | `make test-l2` green on Spark 4.1.2 |
| Layer 3 — Medallion | Verified | `make test-l3` green on Spark 4.1.2 |
| Layer 4 — Lineage | Verified | `make up-lineage && make test-l4` green on Spark 4.0.0 sidecar; requires `--add-opens=java.base/java.security=ALL-UNNAMED` on JDK 21 |
| Layer 5 — Unity Catalog OSS | Verified | `make up-unity && POLYGON_USE_SOLUTION=1 make test-l5` green on Spark 4.1.2; uses external Delta tables |

## Layer 4 isolation note

OpenLineage 1.50.0 on Spark 4.1.2 emits job runs but fails to capture Delta dataset
I/O (`Query execution is null` + `InaccessibleObjectException` on JDK 21). The same
errors appear with Spark 4.0.1. Spark 4.0.0 + Delta 4.0.0 captures the medallion
bronze→silver→gold graph and column-level lineage correctly, so Layer 4 runs in an
isolated `spark-lineage` sidecar using those pins.
