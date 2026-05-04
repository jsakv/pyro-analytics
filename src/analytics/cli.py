"""Compatibility exports for the Pyronear Analytics CLI."""

from __future__ import annotations

from analytics.__main__ import create_app, main

app = create_app()

__all__ = ["app", "create_app", "main"]
