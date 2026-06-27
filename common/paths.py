"""Repo-relative paths used by layers and data generator."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
GENERATED_DIR = DATA_DIR / "generated"
RAW_DIR = GENERATED_DIR / "raw"
TABLES_DIR = REPO_ROOT / "spark-warehouse" / "polygon"


def generated_raw_path(name: str) -> Path:
    return RAW_DIR / name


def generated_manifest_path() -> Path:
    return GENERATED_DIR / "manifest.json"


def layer_table_dir(layer: str, table: str) -> Path:
    return TABLES_DIR / layer / table
