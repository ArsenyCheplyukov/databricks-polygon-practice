"""Layer 5 tests — Unity Catalog OSS."""

import os
import uuid

import pytest

if os.environ.get("POLYGON_USE_SOLUTION") == "1":
    from layer5_unity_catalog.solution import tasks
else:
    from layer5_unity_catalog import tasks

from common.spark_session import uc_session


@pytest.fixture(scope="module")
def spark():
    spark = uc_session("layer5-tests")
    yield spark
    spark.stop()


@pytest.fixture
def unique_schema():
    return f"l5_{uuid.uuid4().hex[:8]}"


def test_task_1_creates_table(spark, unique_schema):
    full_name = tasks.task_1_create_catalog_schema_table(spark, unique_schema, "demo")
    assert full_name == f"unity.{unique_schema}.demo"
    rows = spark.sql(f"SHOW TABLES IN unity.{unique_schema}").collect()
    assert any(r.tableName == "demo" for r in rows)


def test_task_2_round_trip(spark, unique_schema):
    table = tasks.task_1_create_catalog_schema_table(spark, unique_schema, "rt")
    count = tasks.task_2_write_and_read(spark, table, num_rows=5)
    assert count == 5


def test_task_3_describe_and_show(spark, unique_schema):
    table = tasks.task_1_create_catalog_schema_table(spark, unique_schema, "meta")
    result = tasks.task_3_describe_and_show(spark, table)
    assert result["full_name"] == table
    assert "id" in result["describe_columns"]
    assert "value" in result["describe_columns"]
    assert "meta" in result["show_tables"]
