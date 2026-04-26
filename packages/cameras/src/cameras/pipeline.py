"""Camera map publishing pipeline orchestration."""

from __future__ import annotations

from cameras.cells import aggregate_cells
from cameras.config import Config
from cameras.publishers import GEOJSON_CONTENT_TYPE, Publisher, S3Publisher
from cameras.schemas import Result
from cameras.serialization import serialize_aggregates
from cameras.sources import ApiSource, FixtureSource, Source


def publish(config: Config, *, source: Source | None = None, publisher: Publisher | None = None) -> Result:
    """Run the camera publication pipeline."""
    selected_source = source or _select_source(config)
    selected_publisher = publisher or S3Publisher(config)

    cameras = selected_source.fetch()
    aggregates = aggregate_cells(cameras, config)
    artifact = serialize_aggregates(aggregates)
    result = selected_publisher.publish(artifact, content_type=GEOJSON_CONTENT_TYPE)
    return result.model_copy(update={"camera_count": len(cameras), "cell_count": aggregates.height})


def _select_source(config: Config) -> Source:
    if config.fixture_path is not None:
        return FixtureSource(config.fixture_path)
    return ApiSource(config)
