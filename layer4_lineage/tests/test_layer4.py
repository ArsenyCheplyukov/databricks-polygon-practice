"""Layer 4 tests — Data lineage."""

import csv
import json
import os
import time
import urllib.parse
import uuid
from pathlib import Path

import pytest
import requests

if os.environ.get("POLYGON_USE_SOLUTION") == "1":
    from layer4_lineage.solution import tasks
else:
    from layer4_lineage import tasks

from common.spark_session import lineage_session


MARQUEZ_API_URL = os.environ.get("MARQUEZ_API_URL", "http://marquez-api:5000")


@pytest.fixture(scope="module")
def namespace():
    """Unique OpenLineage namespace per test module so assertions are isolated
    from any stale Marquez state."""
    return f"polygon-test-{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module")
def spark(namespace):
    spark = lineage_session("layer4-tests", namespace)
    yield spark
    # Give OpenLineage async emitter time to flush before stopping the context.
    time.sleep(5)
    spark.stop()


@pytest.fixture
def dirs(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    clients = [
        {"client_id": 1, "name": "A", "state": "CA", "signup_date": "2021-01-15", "segment": "premium"},
        {"client_id": 2, "name": "B", "state": "NY", "signup_date": "2021-03-20", "segment": "basic"},
    ]
    policies = [
        {"policy_id": 1, "client_id": 1, "product": "auto", "premium": 500.0, "start_date": "2021-02-01", "status": "active"},
        {"policy_id": 2, "client_id": 2, "product": "home", "premium": 800.0, "start_date": "2021-04-01", "status": "active"},
    ]
    claims = [
        {"claim_id": 1, "policy_id": 1, "amount": 100.0, "claim_date": "2021-06-01", "status": "approved"},
    ]
    with (raw / "clients.jsonl").open("w") as f:
        for row in clients:
            f.write(json.dumps(row) + "\n")
    with (raw / "policies.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["policy_id", "client_id", "product", "premium", "start_date", "status"])
        writer.writeheader()
        writer.writerows(policies)
    with (raw / "claims.jsonl").open("w") as f:
        for row in claims:
            f.write(json.dumps(row) + "\n")
    return {
        "raw": str(raw),
        "bronze": str(tmp_path / "bronze"),
        "silver": str(tmp_path / "silver"),
        "gold": str(tmp_path / "gold"),
    }


def _poll_for_graph(
    required_prefixes: list[str], max_wait: int = 60
) -> dict:
    """Wait until Marquez has ingested a lineage graph containing all required
    dataset path prefixes."""
    node_id = f"dataset:file:{required_prefixes[0]}"
    for _ in range(max_wait):
        try:
            resp = requests.get(
                f"{MARQUEZ_API_URL}/api/v1/lineage",
                params={"nodeId": node_id, "depth": 5},
                timeout=5,
            )
            if resp.status_code == 200:
                data = resp.json()
                graph = data.get("graph", [])
                node_ids = {n["id"] for n in graph}
                if all(
                    any(prefix in nid for nid in node_ids)
                    for prefix in required_prefixes
                ):
                    return data
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError(f"Marquez did not ingest lineage for {required_prefixes}")


def _dataset_metadata(dataset_name: str, max_wait: int = 60) -> dict:
    """Wait until Marquez has the dataset metadata and return it."""
    encoded = urllib.parse.quote(dataset_name, safe="")
    for _ in range(max_wait):
        try:
            resp = requests.get(
                f"{MARQUEZ_API_URL}/api/v1/namespaces/file/datasets/{encoded}",
                timeout=5,
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError(f"Marquez did not ingest dataset metadata for {dataset_name}")


def _is_dataset(node_id: str) -> bool:
    return node_id.startswith("dataset:")


def _is_job(node_id: str) -> bool:
    return node_id.startswith("job:")


def test_lineage_graph_has_bronze_silver_gold_and_column_edges(spark, namespace, dirs):
    tasks.task_1_emit_lineage(spark, dirs["raw"], dirs["bronze"], dirs["silver"], dirs["gold"])

    graph = _poll_for_graph([dirs["gold"], dirs["silver"], dirs["bronze"]])["graph"]
    node_ids = {n["id"] for n in graph}

    # The current run's bronze, silver, and gold dataset nodes must exist.
    assert any(dirs["gold"] in n for n in node_ids), "gold dataset node missing"
    assert any(dirs["silver"] in n for n in node_ids), "silver dataset node missing"
    assert any(dirs["bronze"] in n for n in node_ids), "bronze dataset node missing"

    # Build adjacency: origin -> [destinations]
    adj = {n["id"]: [] for n in graph}
    for n in graph:
        for e in n.get("outEdges", []):
            adj[e["origin"]].append(e["destination"])

    bronze_nodes = [n for n in node_ids if dirs["bronze"] in n and _is_dataset(n)]
    silver_nodes = [n for n in node_ids if dirs["silver"] in n and _is_dataset(n)]
    gold_nodes = [n for n in node_ids if dirs["gold"] in n and _is_dataset(n)]

    found_bronze_to_silver = False
    found_silver_to_gold = False

    for bn in bronze_nodes:
        for j1 in adj.get(bn, []):
            if _is_job(j1):
                for sn in silver_nodes:
                    if sn in adj.get(j1, []):
                        found_bronze_to_silver = True

    for sn in silver_nodes:
        for j2 in adj.get(sn, []):
            if _is_job(j2):
                for gn in gold_nodes:
                    if gn in adj.get(j2, []):
                        found_silver_to_gold = True

    assert found_bronze_to_silver, "no bronze -> job -> silver path"
    assert found_silver_to_gold, "no silver -> job -> gold path"

    # Column-level lineage: at least one gold column maps back to a silver table.
    gold_meta = _dataset_metadata(dirs["gold"])
    column_lineage = gold_meta.get("columnLineage", [])
    assert any(
        col.get("inputFields")
        for col in column_lineage
    ), "no column-level lineage input fields on gold dataset"
