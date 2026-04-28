"""dlt ingestion entrypoints for Pyromap camera data."""

from __future__ import annotations

from typing import Any

import dlt
from sources.backend import backend_source

from pyromap.config import Config

CAMERAS_TABLE = "cameras"


def build_pipeline(config: Config) -> Any:
    """Build the dlt ingestion pipeline for Pyromap camera records."""
    return dlt.pipeline(
        pipeline_name=config.ingestion_pipeline_name,
        pipelines_dir=str(config.ingestion_pipelines_dir),
        destination=config.ingestion_destination,
        dataset_name=config.ingestion_dataset_name,
    )


def run_cameras_ingestion(config: Config, *, pipeline: Any | None = None) -> object:
    """Run backend camera ingestion with dlt."""
    selected_pipeline = pipeline or build_pipeline(config)
    selected_source = backend_source()
    return selected_pipeline.run(selected_source.with_resources(CAMERAS_TABLE))
