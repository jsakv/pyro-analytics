"""Camera map publication flow outside dlt ingestion."""

from __future__ import annotations

from pyromap.cells import aggregate_cells
from pyromap.config import Config
from pyromap.geojson import serialize_aggregates
from pyromap.ingestion import CAMERAS_TABLE, build_pipeline, run_cameras_ingestion
from pyromap.publishers import GEOJSON_CONTENT_TYPE, Publisher, S3Publisher
from pyromap.records import load_fixture_records, read_records
from pyromap.schemas import Camera, Result


def _load_cameras(config: Config) -> tuple[Camera, ...]:
    if config.fixture_path is not None:
        return load_fixture_records(config.fixture_path, model=Camera)

    pipeline = build_pipeline(config)
    run_cameras_ingestion(config, pipeline=pipeline)
    return read_records(pipeline, table_name=CAMERAS_TABLE, model=Camera)


def publish(config: Config, *, publisher: Publisher | None = None) -> Result:
    """Ingest, transform, and publish the camera map artifact."""
    selected_publisher = publisher or S3Publisher(config)

    cameras = _load_cameras(config)
    aggregates = aggregate_cells(cameras, config)
    artifact = serialize_aggregates(aggregates)
    result = selected_publisher.publish(artifact, content_type=GEOJSON_CONTENT_TYPE)
    return result.model_copy(update={"camera_count": len(cameras), "cell_count": aggregates.height})
