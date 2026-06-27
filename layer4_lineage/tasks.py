"""Layer 4 — Data lineage with OpenLineage + Marquez."""

from pyspark.sql import SparkSession


def task_1_emit_lineage(spark: SparkSession, raw_dir: str, bronze_dir: str, silver_dir: str, gold_dir: str) -> list:
    """
    Objective: run the medallion pipeline with the OpenLineage listener active.

    Acceptance:
    - Use a lineage-enabled Spark session.
    - Run bronze → silver → gold.
    - Return a list of dataset names (or paths) that the job produced/consumed.
    """
    raise NotImplementedError


def task_2_query_marquez(namespace: str, dataset_name: str, marquez_api_url: str) -> dict:
    """
    Objective: query the Marquez API for the lineage graph of a gold dataset.

    Acceptance:
    - GET the lineage for `dataset_name` in `namespace`.
    - Return the JSON response as a Python dict.
    """
    raise NotImplementedError
