"""Spark session builders for the polygon."""

import os

from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession


def _delta_conf(builder: SparkSession.Builder) -> SparkSession.Builder:
    return builder \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")


def delta_session(app_name: str) -> SparkSession:
    """Plain local Delta session for Layers 1-3."""
    builder = _delta_conf(SparkSession.builder.appName(app_name).master("local[*]"))
    return configure_spark_with_delta_pip(builder).getOrCreate()


def lineage_session(app_name: str, namespace: str) -> SparkSession:
    """Delta + OpenLineage listener pointed at Marquez for Layer 4."""
    openlineage_version = os.environ.get("OPENLINEAGE_SPARK_VERSION", "1.50.0")
    packages = (
        "io.delta:delta-spark_4.1_2.13:4.1.0,"
        f"io.openlineage:openlineage-spark_2.13:{openlineage_version}"
    )
    builder = SparkSession.builder \
        .appName(app_name) \
        .master("local[*]") \
        .config("spark.jars.packages", packages) \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.extraListeners", "io.openlineage.spark.agent.OpenLineageSparkListener") \
        .config("spark.openlineage.transport.type", "http") \
        .config("spark.openlineage.transport.url", os.environ.get("MARQUEZ_API_URL", "http://marquez-api:5000")) \
        .config("spark.openlineage.namespace", namespace) \
        .config("spark.openlineage.facets.columnLineage.enabled", "true")
    return builder.getOrCreate()


def uc_session(app_name: str) -> SparkSession:
    """Delta + Unity Catalog OSS connector for Layer 5."""
    packages = (
        "io.delta:delta-spark_4.1_2.13:4.1.0,"
        "io.unitycatalog:unitycatalog-spark_2.13:0.4.0"
    )
    builder = SparkSession.builder \
        .appName(app_name) \
        .master("local[*]") \
        .config("spark.jars.packages", packages) \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.sql.catalog.unity", "io.unitycatalog.spark.UCSingleCatalog") \
        .config("spark.sql.catalog.unity.uri", os.environ.get("UC_SERVER_URL", "http://unity-catalog:8080")) \
        .config("spark.sql.catalog.unity.token", os.environ.get("UC_TOKEN", ""))
    return builder.getOrCreate()
