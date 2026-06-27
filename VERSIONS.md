# Resolved versions

| Component | Resolved version | Verification status |
|-----------|------------------|---------------------|
| Python | 3.13 | TBD |
| JDK | Temurin 21 | TBD |
| PySpark | 4.1.2 | TBD |
| Delta Lake | 4.1.0 | TBD |
| OpenLineage Spark | 1.50.0 | TBD |
| OpenLineage namespace | insurance-polygon | TBD |
| Marquez API/Web | 0.51.1 | TBD |
| Marquez DB | postgres:15 | TBD |
| Unity Catalog server | main-2f2e32d | TBD |
| Unity Catalog Spark connector | 0.4.0 (target) | TBD |

## Per-layer status

| Layer | Status | Notes |
|-------|--------|-------|
| Layer 1 — Delta core | TBD | |
| Layer 2 — Delta ops | TBD | |
| Layer 3 — Medallion | TBD | |
| Layer 4 — Lineage | TBD | Primary: Spark 4.1.2; fallback Spark 4.0.1 if needed |
| Layer 5 — Unity Catalog OSS | TBD | Scaffold + timebox; SKIP if not clean |
