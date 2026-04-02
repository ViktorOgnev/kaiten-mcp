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


def test_readyz_returns_ready_when_client_config_is_valid():
    app = create_http_app(session_manager_cls=FakeSessionManager)

    with (
        patch("kaiten_mcp.http_server.get_client", return_value=object()),
        TestClient(app) as client,
    ):
        response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readyz_returns_503_when_client_config_is_invalid():
    app = create_http_app(session_manager_cls=FakeSessionManager)

    with (
        patch(
            "kaiten_mcp.http_server.get_client",
            side_effect=ValueError("KAITEN_TOKEN is required"),
        ),
        TestClient(app) as client,
    ):
        response = client.get("/readyz")

    assert response.status_code == 503
    assert response.json() == {"status": "error", "detail": "KAITEN_TOKEN is required"}


def test_http_endpoint_requires_auth_when_token_is_configured():
    with patch.dict("os.environ", {"MCP_AUTH_TOKEN": "secret"}, clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)

    with TestClient(app) as client:
        response = client.get("/mcp")

    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}


def test_http_endpoint_passes_authorized_requests_to_session_manager():
    with patch.dict("os.environ", {"MCP_AUTH_TOKEN": "secret"}, clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)

    with TestClient(app) as client:
        response = client.get("/mcp", headers={"Authorization": "Bearer secret"})

    assert response.status_code == 200
    assert response.json() == {"transport": "http"}
    assert FakeSessionManager.instances[-1].handle_request.await_count == 1


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
            "KAITEN_DOMAIN": "sandbox",
            "KAITEN_TOKEN": "test-token",
            "MCP_AUTH_TOKEN": "secret",
        },
        clear=False,
    ):
        app = create_http_app()

    with TestClient(app) as client:
        response = client.get("/mcp", headers={"Authorization": "Bearer secret"})

    assert response.status_code in {400, 405, 406}
