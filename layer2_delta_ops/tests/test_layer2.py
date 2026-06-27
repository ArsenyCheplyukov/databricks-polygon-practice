"""Layer 2 tests — Delta operations."""

import os

import pytest
from pyspark.sql.functions import col

if os.environ.get("POLYGON_USE_SOLUTION") == "1":
    from layer2_delta_ops.solution import tasks
else:
    from layer2_delta_ops import tasks

from common.spark_session import delta_session


@pytest.fixture(scope="module")
def spark():
    spark = delta_session("layer2-tests")
    yield spark
    spark.stop()


@pytest.fixture
def table_path(tmp_path):
    return str(tmp_path / "table")


def test_task_1_merge_upsert(spark, table_path):
    target = spark.createDataFrame(
        [(1, "a", 10), (2, "b", 20), (3, "c", 30)],
        ["id", "name", "value"],
    )
    target.write.format("delta").save(table_path)

    source = spark.createDataFrame(
        [(2, "b-updated", 200), (4, "d", 40), (5, "e", 50)],
        ["id", "name", "value"],
    )

    result = tasks.task_1_merge_upsert(spark, table_path, source)
    rows = result.orderBy("id").collect()
    ids = [r.id for r in rows]
    assert len(ids) == len(set(ids))
    assert sorted(ids) == [1, 2, 3, 4, 5]
    updated = [r for r in rows if r.id == 2][0]
    assert updated.value == 200


def test_task_2_update_delete(spark, table_path):
    result = tasks.task_2_update_delete(spark, table_path)
    assert isinstance(result, dict)
    assert result["update_files_added"] > 0
    assert result["delete_files_added"] > 0


def test_task_3_schema_enforcement_and_evolution(spark, table_path):
    result = tasks.task_3_schema_enforcement_and_evolution(spark, table_path)
    assert result["bad_schema_raised"] is True
    assert result["new_column_present"] is True


def test_task_4_optimize_reduces_file_count(spark, table_path):
    result = tasks.task_4_optimize(spark, table_path)
    assert result["after_files"] < result["before_files"]


def test_task_5_zorder_reduces_files_scanned(spark, table_path):
    result = tasks.task_5_zorder(spark, table_path)
    assert result["files_after"] <= result["files_before"]


def test_task_6_vacuum_removes_old_files(spark, table_path):
    result = tasks.task_6_vacuum(spark, table_path)
    assert result["old_files_remaining"] == 0
