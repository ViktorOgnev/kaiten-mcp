"""Tests for HTTP MCP bootstrap and auth wrapper."""

from contextlib import asynccontextmanager
from typing import ClassVar
from unittest.mock import AsyncMock, patch

from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from kaiten_mcp.http_server import create_http_app


class FakeSessionManager:
    """Minimal session manager stub for HTTP app tests."""

    instances: ClassVar[list["FakeSessionManager"]] = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.handle_request = AsyncMock(side_effect=self._handle_request)
        self.run = self._run
        type(self).instances.append(self)

    @asynccontextmanager
    async def _run(self):
        yield

    async def _handle_request(self, scope, receive, send):
        response = JSONResponse({"transport": "http"})
        await response(scope, receive, send)


def test_healthz_returns_ok():
    app = create_http_app(session_manager_cls=FakeSessionManager)

    with TestClient(app) as client:
        response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_returns_ready_with_auth_mode():
    with patch.dict("os.environ", {"MCP_HTTP_AUTH_MODE": "oauth"}, clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "auth_mode": "oauth"}


def test_readyz_does_not_require_kaiten_token_in_oauth_mode():
    with patch.dict("os.environ", {"MCP_HTTP_AUTH_MODE": "oauth"}, clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            response = client.get("/readyz")

    assert response.status_code == 200


def test_http_endpoint_requires_auth_when_token_is_configured():
    with patch.dict("os.environ", {"MCP_AUTH_TOKEN": "secret"}, clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            response = client.get("/mcp")

    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}


def test_http_endpoint_explicit_shared_mode_without_token_allows_requests():
    with patch.dict("os.environ", {"MCP_HTTP_AUTH_MODE": "shared"}, clear=True):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            response = client.get("/mcp")

    assert response.status_code == 200
    assert response.json() == {"transport": "http"}


def test_http_endpoint_passes_authorized_requests_to_session_manager():
    with patch.dict("os.environ", {"MCP_AUTH_TOKEN": "secret"}, clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            response = client.get("/mcp", headers={"Authorization": "Bearer secret"})

    assert response.status_code == 200
    assert response.json() == {"transport": "http"}
    assert FakeSessionManager.instances[-1].handle_request.await_count == 1


def test_http_endpoint_shared_origin_allowlist_blocks_untrusted_origin():
    with patch.dict(
        "os.environ",
        {
            "MCP_HTTP_AUTH_MODE": "shared",
            "MCP_AUTH_TOKEN": "secret",
            "MCP_ALLOWED_ORIGINS": "https://trusted.example.com",
        },
        clear=True,
    ):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            response = client.get(
                "/mcp",
                headers={
                    "Authorization": "Bearer secret",
                    "Origin": "https://evil.example.com",
                },
            )

    assert response.status_code == 403
    assert response.json() == {"error": "Forbidden origin"}


def test_http_endpoint_uses_custom_mount_path():
    with patch.dict("os.environ", {"MCP_HTTP_BASE_PATH": "/rpc"}, clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)

    with TestClient(app) as client:
        response = client.get("/rpc")

    assert response.status_code == 200
    assert response.json() == {"transport": "http"}


def test_http_endpoint_normalizes_mount_path_without_leading_slash():
    with patch.dict("os.environ", {"MCP_HTTP_BASE_PATH": "rpc"}, clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)

    with TestClient(app) as client:
        response = client.get("/rpc")

    assert response.status_code == 200
    assert response.json() == {"transport": "http"}


def test_http_endpoint_default_session_manager_handles_authorized_probe_without_500():
    with patch.dict(
        "os.environ",
        {
            "KAITEN_SUBDOMAIN": "sandbox",
            "KAITEN_TOKEN": "test-token",
            "MCP_AUTH_TOKEN": "secret",
        },
        clear=False,
    ):
        app = create_http_app()
        with TestClient(app) as client:
            response = client.get("/mcp", headers={"Authorization": "Bearer secret"})

    assert response.status_code in {400, 405, 406}
