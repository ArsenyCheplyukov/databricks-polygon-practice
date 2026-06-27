"""Layer 3 — Medallion pipeline."""

from pyspark.sql import DataFrame, SparkSession


def task_1_bronze(spark: SparkSession, raw_dir: str, bronze_dir: str) -> dict:
    """
    Objective: ingest raw messy JSON/CSV into bronze append-only tables.

    Acceptance:
    - Read raw/clients.jsonl, raw/policies.csv, raw/claims.jsonl from `raw_dir`.
    - Append them to bronze tables under `bronze_dir`.
    - Add metadata columns `_source_file` and `_loaded_at`.
    - Return a dict of bronze DataFrames keyed by 'clients', 'policies', 'claims'.
    """
    raise NotImplementedError


def task_2_silver(spark: SparkSession, bronze_dir: str, silver_dir: str) -> dict:
    """
    Objective: clean, dedupe, and conform bronze data into silver tables.

    Acceptance:
    - Read bronze clients/policies/claims.
    - Parse dates, enforce types, dedupe by business key.
    - Use MERGE upsert to write silver tables under `silver_dir`.
    - Return a dict of silver DataFrames keyed by 'clients', 'policies', 'claims'.
    """
    raise NotImplementedError


def task_3_gold(spark: SparkSession, silver_dir: str, gold_dir: str) -> DataFrame:
    """
    Objective: compute business aggregates for the gold layer.

    Acceptance:
    - Join silver policies → clients and claims → policies.
    - Aggregate premiums and claim amounts by state, product, and segment.
    - Write the gold table under `gold_dir` and return it.
    """
    raise NotImplementedError


def task_4_idempotent(spark: SparkSession, raw_dir: str, bronze_dir: str, silver_dir: str, gold_dir: str) -> bool:
    """
    Objective: prove the full pipeline is idempotent.

    Acceptance:
    - Run bronze → silver → gold once.
    - Capture gold row count/hash.
    - Run the full pipeline again on the same raw inputs.
    - Return True if the gold output is unchanged, False otherwise.
    """
    raise NotImplementedError
