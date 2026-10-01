"""Helpers for constructing allowlisted Kaiten request bodies."""

from collections.abc import Iterable, Mapping
from typing import Any


def _body_from(args: Mapping[str, Any], keys: Iterable[str]) -> dict[str, Any]:
    """Select supported, non-None values, retaining zero, False and empty values."""
    return {key: args[key] for key in keys if args.get(key) is not None}
