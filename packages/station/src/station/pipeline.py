"""Station map publishing pipeline orchestration."""

from __future__ import annotations

from station.cells import aggregate_cells
from station.config import Config
from station.publishers import GEOJSON_CONTENT_TYPE, Publisher, S3Publisher
from station.schemas import Result
from station.serialization import serialize_aggregates
from station.sources import ApiSource, FixtureSource, Source


def publish(config: Config, *, source: Source | None = None, publisher: Publisher | None = None) -> Result:
    """Run the station publication pipeline."""
    selected_source = source or _select_source(config)
    selected_publisher = publisher or S3Publisher(config)

    stations = selected_source.fetch()
    aggregates = aggregate_cells(stations, config)
    artifact = serialize_aggregates(aggregates)
    result = selected_publisher.publish(artifact, content_type=GEOJSON_CONTENT_TYPE)
    return result.model_copy(update={"station_count": len(stations), "cell_count": aggregates.height})


def _select_source(config: Config) -> Source:
    if config.fixture_path is not None:
        return FixtureSource(config.fixture_path)
    return ApiSource(config)
