"""HTTP entrypoint for remote MCP deployment."""

import importlib
import os
from contextlib import asynccontextmanager
from typing import Any, cast

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from kaiten_mcp.runtime import app, close_client, get_client


def _load_session_manager_cls() -> type[Any]:
    try:
        module = importlib.import_module("mcp.server.streamable_http_manager")
    except ImportError:  # pragma: no cover - compatibility fallback across SDK versions
        module = importlib.import_module("mcp.server.streamable_http")
    return cast(type[Any], module.StreamableHTTPSessionManager)


DEFAULT_SESSION_MANAGER_CLS = _load_session_manager_cls()


def _is_authorized(request: Request, expected: str | None) -> bool:
    if not expected:
        return True
    return request.headers.get("authorization") == f"Bearer {expected}"


async def healthz(_: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


async def readyz(_: Request) -> JSONResponse:
    try:
        get_client()
    except ValueError as exc:
        return JSONResponse({"status": "error", "detail": str(exc)}, status_code=503)
    return JSONResponse({"status": "ready"})


def create_http_app(
    *,
    session_manager_cls: type[Any] = DEFAULT_SESSION_MANAGER_CLS,
) -> Starlette:
    mcp_path = os.environ.get("MCP_HTTP_BASE_PATH", "/mcp")
    auth_token = os.environ.get("MCP_AUTH_TOKEN")
    if not mcp_path.startswith("/"):
        mcp_path = f"/{mcp_path}"

    session_manager = session_manager_cls(
        app=app,
        event_store=None,
        json_response=True,
        stateless=True,
    )

    async def handle_streamable_http(scope, receive, send) -> None:
        request = Request(scope, receive=receive)
        if not _is_authorized(request, auth_token):
            response = JSONResponse({"error": "Unauthorized"}, status_code=401)
            await response(scope, receive, send)
            return
        await session_manager.handle_request(scope, receive, send)

    @asynccontextmanager
    async def lifespan(_: Starlette):
        async with session_manager.run():
            try:
                yield
            finally:
                await close_client()

    return Starlette(
        debug=False,
        lifespan=lifespan,
        routes=[
            Route("/healthz", endpoint=healthz),
            Route("/readyz", endpoint=readyz),
            Mount(mcp_path, app=handle_streamable_http),
        ],
    )


def main() -> None:
    host = os.environ.get("MCP_HTTP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_HTTP_PORT", "8000"))
    uvicorn.run(create_http_app(), host=host, port=port)


__all__ = ["create_http_app", "healthz", "main", "readyz"]
