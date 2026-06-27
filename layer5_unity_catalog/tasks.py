"""Layer 5 — Unity Catalog OSS."""

from pyspark.sql import SparkSession


def task_1_create_catalog_schema_table(
    spark: SparkSession, schema_name: str, table_name: str
) -> str:
    """
    Objective: create a schema and an external Delta table in the Unity Catalog
    namespace.

    Acceptance:
    - Use ``uc_session()`` so the ``unity`` catalog points at the UC server.
    - Create ``unity.{schema_name}`` if it does not exist.
    - Create ``unity.{schema_name}.{table_name}`` as an external Delta table.
    - Return the fully-qualified table name.
    """
    raise NotImplementedError


def task_2_write_and_read(spark: SparkSession, table_name: str, num_rows: int = 3) -> int:
    """
    Objective: write a Delta table through the unity namespace and read it back.

    Acceptance:
    - Insert ``num_rows`` rows into ``table_name``.
    - Read the table and return the row count.
    - The returned count equals ``num_rows``.
    """
    raise NotImplementedError


def task_3_describe_and_show(spark: SparkSession, table_name: str) -> dict:
    """
    Objective: run DESCRIBE and SHOW on the UC table and confirm the three-level
    name resolves.

    Acceptance:
    - ``DESCRIBE TABLE EXTENDED`` returns at least the column names.
    - ``SHOW TABLES IN <schema>`` lists ``table_name``.
    - Return a dict with:
        {'describe_columns': list, 'show_tables': list, 'full_name': table_name}
    """
    raise NotImplementedError
