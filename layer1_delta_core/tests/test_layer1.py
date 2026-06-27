"""Layer 1 tests — Delta core & transaction log."""

import os
from pathlib import Path

import pytest

if os.environ.get("POLYGON_USE_SOLUTION") == "1":
    from layer1_delta_core.solution import tasks
else:
    from layer1_delta_core import tasks

from common.spark_session import delta_session


@pytest.fixture(scope="module")
def spark():
    spark = delta_session("layer1-tests")
    yield spark
    spark.stop()


@pytest.fixture
def policies_path(tmp_path):
    return str(tmp_path / "policies")


@pytest.fixture
def base_path(tmp_path):
    return str(tmp_path / "atomicity")


def test_task_1_creates_multiple_versions(spark, policies_path):
    tasks.task_1_write_and_operate(spark, policies_path)

    history = spark.sql(f"DESCRIBE HISTORY delta.`{policies_path}`").collect()
    operations = [row.operation for row in history]
    assert len(history) == 5, f"expected 5 versions, got {len(history)}: {operations}"
    assert "WRITE" in operations or "CREATE TABLE" in operations or "APPEND" in operations


def test_task_2_log_has_expected_actions(spark, policies_path):
    actions = tasks.task_2_inspect_log(spark, policies_path)
    assert isinstance(actions, dict)
    assert len(actions) >= 5

    version_actions = {v: set(names) for v, names in actions.items()}
    assert any("metaData" in names for names in version_actions.values())
    assert any("protocol" in names for names in version_actions.values())
    assert any("add" in names for names in version_actions.values())
    assert any("remove" in names for names in version_actions.values())


def test_task_3_time_travel_returns_pre_change_state(spark, policies_path):
    result = tasks.task_3_time_travel(spark, policies_path)
    assert isinstance(result, dict)
    assert result["before_overwrite_count"] != result["after_overwrite_count"]
    assert result["timestamp_as_of_count"] == result["before_overwrite_count"]


def test_task_4_describe_history_lists_all_versions(spark, policies_path):
    history = tasks.task_4_describe_history(spark, policies_path)
    assert isinstance(history, list)
    assert len(history) == 5
    for entry in history:
        assert "version" in entry
        assert "operation" in entry
        assert "operationParameters" in entry
        assert "readVersion" in entry


def test_task_5_delta_atomic_parquet_not_atomic(spark, base_path):
    result = tasks.task_5_parquet_vs_delta(spark, base_path)
    assert isinstance(result, dict)
    assert result["delta_consistent"] is True
    assert result["parquet_consistent"] is False
