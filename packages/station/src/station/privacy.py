"""Location privacy policy helpers."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator

DEFAULT_PUBLISH_RESOLUTION = 5
ALLOWED_PUBLIC_PROPERTIES = frozenset({"cell", "station_count", "station_count_bucket"})
DEFAULT_PUBLIC_PROPERTIES = ("cell", "station_count", "station_count_bucket")


class LocationPolicy(BaseModel):
    """Location precision and public property policy."""

    model_config = ConfigDict(frozen=True)

    resolution: int = DEFAULT_PUBLISH_RESOLUTION
    public_properties: tuple[str, ...] = DEFAULT_PUBLIC_PROPERTIES

    @field_validator("resolution")
    @classmethod
    def validate_resolution(cls, value: int) -> int:
        """Constrain H3 resolution to the valid range."""
        if not 0 <= value <= 15:
            msg = "publish resolution must be between 0 and 15."
            raise ValueError(msg)
        return value

    @field_validator("public_properties")
    @classmethod
    def validate_public_properties(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        """Constrain public properties to the approved allowlist."""
        if not value:
            msg = "public_properties must include at least one property."
            raise ValueError(msg)

        duplicate_properties = {prop for prop in value if value.count(prop) > 1}
        if duplicate_properties:
            joined_properties = ", ".join(sorted(duplicate_properties))
            msg = f"public_properties contains duplicates: {joined_properties}."
            raise ValueError(msg)

        unknown_properties = set(value) - ALLOWED_PUBLIC_PROPERTIES
        if unknown_properties:
            joined_properties = ", ".join(sorted(unknown_properties))
            msg = f"public_properties contains unapproved fields: {joined_properties}."
            raise ValueError(msg)
        return value


DEFAULT_LOCATION_POLICY = LocationPolicy()
