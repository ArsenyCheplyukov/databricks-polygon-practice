"""Layer 3 tests — Medallion pipeline."""

import csv
import json
import os
from pathlib import Path

import pytest

if os.environ.get("POLYGON_USE_SOLUTION") == "1":
    from layer3_medallion.solution import tasks
else:
    from layer3_medallion import tasks

from common.spark_session import delta_session


@pytest.fixture(scope="module")
def spark():
    spark = delta_session("layer3-tests")
    yield spark
    spark.stop()


@pytest.fixture
def raw_dir(tmp_path):
    d = tmp_path / "raw"
    d.mkdir()
    clients = [
        {"client_id": 1, "name": "A", "state": "CA", "signup_date": "2021-01-15", "segment": "premium"},
        {"client_id": 1, "name": "A", "state": "CA", "signup_date": "01/15/2021", "segment": "premium"},
        {"client_id": 2, "name": "B", "state": "NY", "signup_date": "2021-03-20", "segment": "basic"},
    ]
    policies = [
        {"policy_id": 1, "client_id": 1, "product": "auto", "premium": 500.0, "start_date": "2021-02-01", "status": "active"},
        {"policy_id": 2, "client_id": 2, "product": "home", "premium": 800.0, "start_date": "02/01/2021", "status": "active"},
        {"policy_id": 1, "client_id": 1, "product": "auto", "premium": 500.0, "start_date": "2021-02-01", "status": "active"},
    ]
    claims = [
        {"claim_id": 1, "policy_id": 1, "amount": 100.0, "claim_date": "2021-06-01", "status": "approved"},
        {"claim_id": 2, "policy_id": 2, "amount": 200.0, "claim_date": "01-06-2021", "status": "approved"},
    ]
    with (d / "clients.jsonl").open("w") as f:
        for row in clients:
            f.write(json.dumps(row) + "\n")
    with (d / "policies.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["policy_id", "client_id", "product", "premium", "start_date", "status"])
        writer.writeheader()
        writer.writerows(policies)
    with (d / "claims.jsonl").open("w") as f:
        for row in claims:
            f.write(json.dumps(row) + "\n")
    return str(d)


@pytest.fixture
def dirs(raw_dir, tmp_path):
    return {
        "raw": raw_dir,
        "bronze": str(tmp_path / "bronze"),
        "silver": str(tmp_path / "silver"),
        "gold": str(tmp_path / "gold"),
    }


def test_task_1_bronze_counts_match_raw(spark, dirs):
    bronze = tasks.task_1_bronze(spark, dirs["raw"], dirs["bronze"])
    assert set(bronze.keys()) == {"clients", "policies", "claims"}
    assert bronze["clients"].count() == 3
    assert bronze["policies"].count() == 3
    assert bronze["claims"].count() == 2
    for df in bronze.values():
        assert "_source_file" in df.columns
        assert "_loaded_at" in df.columns


def test_task_2_silver_deduped_and_typed(spark, dirs):
    tasks.task_1_bronze(spark, dirs["raw"], dirs["bronze"])
    silver = tasks.task_2_silver(spark, dirs["bronze"], dirs["silver"])
    assert silver["clients"].count() == 2
    assert silver["policies"].count() == 2
    assert silver["claims"].count() == 2
    # Dates should be parsed to DateType
    from pyspark.sql.types import DateType
    assert isinstance(silver["clients"].schema["signup_date"].dataType, DateType)
    assert isinstance(silver["policies"].schema["start_date"].dataType, DateType)


def test_task_3_gold_aggregates(spark, dirs):
    tasks.task_1_bronze(spark, dirs["raw"], dirs["bronze"])
    tasks.task_2_silver(spark, dirs["bronze"], dirs["silver"])
    gold = tasks.task_3_gold(spark, dirs["silver"], dirs["gold"])
    rows = {r.state: r for r in gold.collect()}
    assert "CA" in rows and "NY" in rows
    ca = rows["CA"]
    assert ca.total_premium == 500.0
    assert ca.total_claims == 100.0


def test_task_4_idempotent(spark, dirs):
    assert tasks.task_4_idempotent(spark, dirs["raw"], dirs["bronze"], dirs["silver"], dirs["gold"]) is True
