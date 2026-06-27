"""Layer 2 — Delta operations."""

from pyspark.sql import DataFrame, SparkSession


def task_1_merge_upsert(spark: SparkSession, target_path: str, source_df: DataFrame) -> DataFrame:
    """
    Objective: apply a batch of inserts and updates to a target Delta table
    using MERGE.

    Acceptance:
    - Create a Delta table at `target_path` if it does not exist.
    - MERGE `source_df` into the target on the business key.
    - Matched rows are updated; unmatched rows are inserted.
    - Return the final DataFrame with no duplicate business keys.
    """
    raise NotImplementedError


def task_2_update_delete(spark: SparkSession, table_path: str) -> dict:
    """
    Objective: run UPDATE and DELETE and observe copy-on-write file rewrites.

    Acceptance:
    - Create/update a Delta table at `table_path`.
    - Run UPDATE and DELETE as separate commits.
    - Return a dict with:
        'update_files_added': number of 'add' actions in the UPDATE commit.
        'delete_files_added': number of 'add' actions in the DELETE commit.
    """
    raise NotImplementedError


def task_3_schema_enforcement_and_evolution(spark: SparkSession, table_path: str) -> dict:
    """
    Objective: enforce schema on writes and opt-in to schema evolution.

    Acceptance:
    - Create a Delta table with a known schema.
    - Attempt to write a DataFrame with an extra column without mergeSchema;
      this must raise an error.
    - Write the same DataFrame with mergeSchema=True; this must succeed and
      the table schema must include the new column.
    - Return a dict {'bad_schema_raised': bool, 'new_column_present': bool}.
    """
    raise NotImplementedError


def task_4_optimize(spark: SparkSession, table_path: str) -> dict:
    """
    Objective: compact small files with OPTIMIZE.

    Acceptance:
    - Create a Delta table with many small files.
    - Run `OPTIMIZE`.
    - Return {'before_files': int, 'after_files': int} where after_files < before_files.
    """
    raise NotImplementedError


def task_5_zorder(spark: SparkSession, table_path: str) -> dict:
    """
    Objective: ZORDER a high-selectivity column and measure data skipping.

    Acceptance:
    - Create a Delta table with multiple files.
    - Run `OPTIMIZE ... ZORDER BY (selective_column)`.
    - Return {'files_before': int, 'files_after': int} where files_after is the
      number of files Spark reads for a selective filter after ZORDER.
    """
    raise NotImplementedError


def task_6_vacuum(spark: SparkSession, table_path: str) -> dict:
    """
    Objective: remove unreferenced old files with VACUUM.

    Acceptance:
    - Create a Delta table, then overwrite it so old files are no longer
      referenced by the latest version.
    - Run `VACUUM ... RETAIN 0 HOURS`.
    - Return {'old_files_remaining': int} equal to 0.
    """
    raise NotImplementedError
