"""Tests for camera artifact publishers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import pytest
from botocore.exceptions import ClientError  # type: ignore[import-untyped]
from pydantic import SecretStr
from pyromap import Config, Result
from pyromap.publishers import GEOJSON_CONTENT_TYPE, LocalPublisher, Publisher, S3Publisher


def secret(value: str) -> SecretStr:
    """Create synthetic secrets for publisher tests."""
    return SecretStr(value)


def make_s3_config() -> Config:
    """Create MinIO-compatible upload config without live credentials."""
    return Config(
        s3_endpoint_url="http://localhost:9000",
        s3_region="us-east-1",
        s3_bucket="pyronear-public-map-local",
        s3_object_key="camera-cells.geojson",
        s3_access_key_id=secret("minio-access"),
        s3_secret_access_key=secret("minio-secret"),
    )


class FakeS3Client:
    """Record S3 put_object calls without network access."""

    def __init__(self, *, response: Mapping[str, object] | None = None, error: BaseException | None = None) -> None:
        self.response = response or {"ETag": '"synthetic-etag"'}
        self.error = error
        self.calls: list[dict[str, object]] = []

    def put_object(self, **kwargs: object) -> Mapping[str, object]:
        """Record one upload call."""
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.response


def test_local_publisher_matches_publisher_protocol(tmp_path: Path) -> None:
    """LocalPublisher should satisfy the publisher contract."""
    publisher: Publisher = LocalPublisher(tmp_path / "camera-cells.geojson")

    result = publisher.publish(b'{"type":"FeatureCollection","features":[]}')

    assert isinstance(result, Result)


def test_local_publisher_writes_artifact_bytes(tmp_path: Path) -> None:
    """Local staging should write exactly the artifact bytes provided."""
    artifact = b'{"type":"FeatureCollection","features":[]}'
    path = tmp_path / "nested" / "camera-cells.geojson"
    publisher = LocalPublisher(path)

    result = publisher.publish(artifact)

    assert path.read_bytes() == artifact
    assert result.published is True
    assert result.artifact_key == str(path)


def test_local_publisher_rejects_empty_artifact(tmp_path: Path) -> None:
    """Publisher inputs should not accept empty artifacts."""
    publisher = LocalPublisher(tmp_path / "camera-cells.geojson")

    with pytest.raises(ValueError, match="non-empty"):
        publisher.publish(b"")


def test_s3_publisher_uploads_to_configured_bucket_and_key() -> None:
    """S3 upload should target exactly the configured bucket and object key."""
    client = FakeS3Client()
    publisher: Publisher = S3Publisher(make_s3_config(), client=client)
    artifact = b'{"type":"FeatureCollection","features":[]}'

    result = publisher.publish(artifact)

    assert client.calls == [
        {
            "Bucket": "pyronear-public-map-local",
            "Key": "camera-cells.geojson",
            "Body": artifact,
            "ContentType": GEOJSON_CONTENT_TYPE,
        }
    ]
    assert result.published is True
    assert result.bucket == "pyronear-public-map-local"
    assert result.artifact_key == "camera-cells.geojson"
    assert result.etag == '"synthetic-etag"'


def test_s3_publisher_supports_minio_endpoint() -> None:
    """Custom endpoint URLs should be preserved for MinIO-compatible uploads."""
    client = FakeS3Client()
    publisher = S3Publisher(make_s3_config(), client=client)

    result = publisher.publish(b'{"type":"FeatureCollection","features":[]}')

    assert result.endpoint_url == "http://localhost:9000"


def test_s3_publisher_sets_geojson_content_type() -> None:
    """GeoJSON artifacts should be uploaded with the public artifact MIME type."""
    client = FakeS3Client()
    publisher = S3Publisher(make_s3_config(), client=client)

    publisher.publish(b"{}", content_type=GEOJSON_CONTENT_TYPE)

    assert client.calls[0]["ContentType"] == "application/geo+json"


def test_s3_publisher_missing_settings_fail_before_upload() -> None:
    """Missing upload config should fail before any S3 client call."""
    client = FakeS3Client()

    with pytest.raises(ValueError, match="CAMERA_MAP_S3_ENDPOINT_URL"):
        S3Publisher(Config(s3_bucket="pyronear-public-map-local"), client=client)

    assert client.calls == []


def test_s3_publisher_rejects_empty_artifact() -> None:
    """S3 publisher should not upload empty artifacts."""
    client = FakeS3Client()
    publisher = S3Publisher(make_s3_config(), client=client)

    with pytest.raises(ValueError, match="non-empty"):
        publisher.publish(b"")

    assert client.calls == []


def test_s3_publisher_failure_is_actionable_without_credentials() -> None:
    """Upload failures should report S3 code without leaking secrets."""
    hidden_message = "do-not-print"
    error = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": hidden_message}},
        "PutObject",
    )
    client = FakeS3Client(error=error)
    publisher = S3Publisher(make_s3_config(), client=client)

    with pytest.raises(ValueError, match="AccessDenied") as exc_info:
        publisher.publish(b'{"type":"FeatureCollection","features":[]}')

    assert hidden_message not in str(exc_info.value)
    assert "minio-secret" not in str(exc_info.value)
