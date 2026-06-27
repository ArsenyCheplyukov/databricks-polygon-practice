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
    """Delta + OpenLineage listener pointed at Marquez for Layer 4.

    On the primary Spark 4.1.2 container the jars are fetched via
    ``configure_spark_with_delta_pip``. On the Layer 4 Spark 4.0.1 sidecar the
    jars are pre-installed in ``pyspark/jars`` so Delta and OpenLineage share
    the app classloader (required for dataset capture on Spark 4.x).
    """
    builder = SparkSession.builder \
        .appName(app_name) \
        .master("local[*]") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.extraListeners", "io.openlineage.spark.agent.OpenLineageSparkListener") \
        .config("spark.openlineage.transport.type", "http") \
        .config("spark.openlineage.transport.url", os.environ.get("MARQUEZ_API_URL", "http://marquez-api:5000")) \
        .config("spark.openlineage.namespace", namespace) \
        .config("spark.openlineage.facets.columnLineage.enabled", "true")

    if os.environ.get("POLYGON_LINEAGE_SIDECAR") == "1":
        return builder.getOrCreate()

    openlineage_version = os.environ.get("OPENLINEAGE_SPARK_VERSION", "1.50.0")
    return configure_spark_with_delta_pip(
        builder,
        extra_packages=[f"io.openlineage:openlineage-spark_2.13:{openlineage_version}"],
    ).getOrCreate()


def uc_session(app_name: str) -> SparkSession:
    """Delta + Unity Catalog OSS connector for Layer 5.

    The Unity Catalog Spark connector jars are pre-baked into the image
    (see Dockerfile.spark) so Layer 5 can run without runtime network access.
    """
    builder = SparkSession.builder \
        .appName(app_name) \
        .master("local[*]") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.sql.catalog.unity", "io.unitycatalog.spark.UCSingleCatalog") \
        .config("spark.sql.catalog.unity.uri", os.environ.get("UC_SERVER_URL", "http://unity-catalog:8080")) \
        .config("spark.sql.catalog.unity.token", os.environ.get("UC_TOKEN", ""))
    return builder.getOrCreate()
