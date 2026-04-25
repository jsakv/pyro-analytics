"""S3-compatible artifact publisher adapter."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, cast

import boto3  # type: ignore[import-untyped]
from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-untyped]
from pydantic import SecretStr

from station.config import Config
from station.publishers.base import GEOJSON_CONTENT_TYPE
from station.schemas import Result


class S3Client(Protocol):
    """Subset of the boto3 S3 client used by the publisher."""

    def put_object(self, **kwargs: Any) -> Mapping[str, Any]:
        """Upload one object."""


class S3Publisher:
    """Publish artifact bytes to an S3-compatible bucket."""

    def __init__(self, config: Config, *, client: S3Client | None = None) -> None:
        config.require_upload_settings()
        self.endpoint_url = _required(config.s3_endpoint_url, "STATION_MAP_S3_ENDPOINT_URL")
        self.region = _required(config.s3_region, "STATION_MAP_S3_REGION")
        self.bucket = _required(config.s3_bucket, "STATION_MAP_S3_BUCKET")
        self.object_key = config.s3_object_key
        self.client = client or _build_client(config)

    def publish(self, artifact: bytes, *, content_type: str = GEOJSON_CONTENT_TYPE) -> Result:
        """Upload artifact bytes to the configured bucket/object key."""
        if not artifact:
            msg = "Artifact bytes must be non-empty."
            raise ValueError(msg)

        try:
            response = self.client.put_object(
                Bucket=self.bucket,
                Key=self.object_key,
                Body=artifact,
                ContentType=content_type,
            )
        except ClientError as exc:
            code = str(exc.response.get("Error", {}).get("Code", "unknown"))
            msg = f"S3 upload failed with error code {code}."
            raise ValueError(msg) from exc
        except BotoCoreError as exc:
            msg = f"S3 upload failed: {exc.__class__.__name__}."
            raise ValueError(msg) from exc

        return Result(
            artifact_key=self.object_key,
            published=True,
            bucket=self.bucket,
            endpoint_url=self.endpoint_url,
            etag=_response_etag(response),
        )


def _build_client(config: Config) -> S3Client:
    access_key = _required_secret(config.s3_access_key_id, "STATION_MAP_S3_ACCESS_KEY_ID")
    secret_key = _required_secret(config.s3_secret_access_key, "STATION_MAP_S3_SECRET_ACCESS_KEY")
    return cast(
        S3Client,
        boto3.client(
            "s3",
            endpoint_url=_required(config.s3_endpoint_url, "STATION_MAP_S3_ENDPOINT_URL"),
            region_name=_required(config.s3_region, "STATION_MAP_S3_REGION"),
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        ),
    )


def _required(value: str | None, env_name: str) -> str:
    if value is None:
        msg = f"Missing required upload setting: {env_name}."
        raise ValueError(msg)
    return value


def _required_secret(value: SecretStr | None, env_name: str) -> str:
    if value is None:
        msg = f"Missing required upload setting: {env_name}."
        raise ValueError(msg)
    return value.get_secret_value()


def _response_etag(response: Mapping[str, Any]) -> str | None:
    etag = response.get("ETag")
    if etag is None:
        return None
    return str(etag)
