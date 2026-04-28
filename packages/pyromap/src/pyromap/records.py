"""Typed record readers for local fixtures and dlt datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError as exc:
        msg = f"Fixture source file does not exist: {path}."
        raise ValueError(msg) from exc
    except json.JSONDecodeError as exc:
        msg = f"Fixture source {path} is not valid JSON."
        raise ValueError(msg) from exc


def _select_model_fields[ModelT: BaseModel](record: dict[str, object], model: type[ModelT]) -> dict[str, object]:
    model_fields = set(model.model_fields)
    return {key: value for key, value in record.items() if key in model_fields}


def _model_from_record[ModelT: BaseModel](
    record: object,
    *,
    model: type[ModelT],
    context: str,
    strip_metadata: bool = False,
) -> ModelT:
    if not isinstance(record, dict):
        msg = f"{context} must be an object."
        raise TypeError(msg)

    payload = _select_model_fields(record, model) if strip_metadata else record
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        msg = f"{context} is invalid."
        raise ValueError(msg) from exc


def load_fixture_records[ModelT: BaseModel](path: Path | str, *, model: type[ModelT]) -> tuple[ModelT, ...]:
    """Read and normalize local fixture records into typed models."""
    fixture_path = Path(path)
    payload = _load_json(fixture_path)
    if not isinstance(payload, list):
        msg = f"Fixture source {fixture_path} must contain a JSON array."
        raise TypeError(msg)

    return tuple(
        _model_from_record(record, model=model, context=f"Fixture source {fixture_path} record {index}")
        for index, record in enumerate(payload)
    )


def read_records[ModelT: BaseModel](
    pipeline: Any,
    *,
    table_name: str,
    model: type[ModelT],
    strip_metadata: bool = True,
) -> tuple[ModelT, ...]:
    """Read normalized records from a dlt destination table."""
    records = pipeline.dataset()[table_name].df().to_dict(orient="records")
    return tuple(
        _model_from_record(
            record,
            model=model,
            context=f"dlt table {table_name} record {index}",
            strip_metadata=strip_metadata,
        )
        for index, record in enumerate(records)
    )
