"""Shared test assertion helpers."""

import json

from httpx import Request


def get_request_json(request: Request) -> dict:
    """Extract JSON body from an httpx Request."""
    return json.loads(request.content)


def get_request_params(request: Request) -> dict[str, str]:
    """Extract query parameters as a dict."""
    return dict(request.url.params)
