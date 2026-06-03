"""HTTP entrypoint for remote MCP deployment."""

import html
import importlib
import os
import time
from contextlib import asynccontextmanager
from typing import Any, cast
from urllib.parse import urlsplit

import uvicorn
from mcp.server.auth.middleware.auth_context import AuthContextMiddleware
from mcp.server.auth.middleware.bearer_auth import BearerAuthBackend, RequireAuthMiddleware
from pydantic.networks import AnyHttpUrl
from starlette.applications import Starlette
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.routing import Mount, Route

from kaiten_mcp.auth import (
    AUTH_STORE,
    DEFAULT_REQUIRED_SCOPE,
    KaitenSessionTokenVerifier,
    build_redirect_uri,
    parse_scope,
    reject_unsafe_public_url,
    validate_kaiten_credential,
    validate_redirect_uri,
)
from kaiten_mcp.client import KaitenApiError
from kaiten_mcp.runtime import app, close_client


def _load_session_manager_cls() -> type[Any]:
    try:
        module = importlib.import_module("mcp.server.streamable_http_manager")
    except ImportError:  # pragma: no cover - compatibility fallback across SDK versions
        module = importlib.import_module("mcp.server.streamable_http")
    return cast(type[Any], module.StreamableHTTPSessionManager)


DEFAULT_SESSION_MANAGER_CLS = _load_session_manager_cls()


def _auth_mode() -> str:
    configured = os.environ.get("MCP_HTTP_AUTH_MODE", "").strip().lower()
    if configured in {"none", "shared", "oauth"}:
        return configured
    if os.environ.get("MCP_AUTH_TOKEN"):
        return "shared"
    return "none"


def _required_scopes() -> list[str]:
    return parse_scope(os.environ.get("MCP_REQUIRED_SCOPES", DEFAULT_REQUIRED_SCOPE))


def _is_authorized(request: Request, expected: str | None) -> bool:
    if not expected:
        return True
    return request.headers.get("authorization") == f"Bearer {expected}"


def _mcp_path() -> str:
    path = os.environ.get("MCP_HTTP_BASE_PATH", "/mcp")
    return path if path.startswith("/") else f"/{path}"


def _request_origin(request: Request) -> str:
    return f"{request.url.scheme}://{request.url.netloc}"


def _issuer_url(request: Request) -> str:
    value = os.environ.get("MCP_OAUTH_ISSUER_URL")
    if value:
        reject_unsafe_public_url(value)
        return value.rstrip("/")
    return _request_origin(request)


def _resource_url(request: Request) -> str:
    value = os.environ.get("MCP_PUBLIC_URL")
    if value:
        reject_unsafe_public_url(value)
        return value.rstrip("/")
    return f"{_request_origin(request)}{_mcp_path()}"


def _static_resource_metadata_url() -> AnyHttpUrl | None:
    value = os.environ.get("MCP_RESOURCE_METADATA_URL")
    if value:
        reject_unsafe_public_url(value)
        return AnyHttpUrl(value.rstrip("/"))
    public_url = os.environ.get("MCP_PUBLIC_URL")
    if not public_url:
        return None
    reject_unsafe_public_url(public_url)
    parsed = urlsplit(public_url)
    return AnyHttpUrl(f"{parsed.scheme}://{parsed.netloc}/.well-known/oauth-protected-resource")


def _allowed_origin(request: Request) -> bool:
    allowed = [item.strip() for item in os.environ.get("MCP_ALLOWED_ORIGINS", "").split(",")]
    allowed = [item for item in allowed if item]
    origin = request.headers.get("origin")
    return not allowed or not origin or origin in allowed


async def healthz(_: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


async def readyz(_: Request) -> JSONResponse:
    return JSONResponse({"status": "ready", "auth_mode": _auth_mode()})


async def protected_resource_metadata(request: Request) -> JSONResponse:
    return JSONResponse(
        {
            "resource": _resource_url(request),
            "authorization_servers": [_issuer_url(request)],
            "scopes_supported": _required_scopes(),
        }
    )


async def authorization_server_metadata(request: Request) -> JSONResponse:
    issuer = _issuer_url(request)
    return JSONResponse(
        {
            "issuer": issuer,
            "authorization_endpoint": f"{issuer}/authorize",
            "token_endpoint": f"{issuer}/token",
            "registration_endpoint": f"{issuer}/register",
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code"],
            "code_challenge_methods_supported": ["S256"],
            "token_endpoint_auth_methods_supported": ["none"],
            "scopes_supported": _required_scopes(),
        }
    )


async def register_client(request: Request) -> JSONResponse:
    payload = await request.json()
    redirect_uris = payload.get("redirect_uris") if isinstance(payload, dict) else None
    if not isinstance(redirect_uris, list):
        return JSONResponse({"error": "invalid_redirect_uris"}, status_code=400)
    try:
        client = AUTH_STORE.register_client(redirect_uris)
    except ValueError:
        return JSONResponse({"error": "invalid_redirect_uris"}, status_code=400)
    return JSONResponse(
        {
            "client_id": client.client_id,
            "client_id_issued_at": client.issued_at,
            "redirect_uris": list(client.redirect_uris),
            "token_endpoint_auth_method": "none",
        },
        status_code=201,
    )


def _authorize_form(
    request: Request,
    error: str | None = None,
    params: dict[str, str] | None = None,
) -> HTMLResponse:
    values = params if params is not None else dict(request.query_params)
    hidden_fields = "\n".join(
        f'<input type="hidden" name="{html.escape(key, quote=True)}" '
        f'value="{html.escape(value, quote=True)}">'
        for key, value in values.items()
    )
    error_html = f'<p class="error">{html.escape(error)}</p>' if error else ""
    return HTMLResponse(
        f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Connect Kaiten MCP</title>
  <style>
    body {{ font-family: sans-serif; max-width: 560px; margin: 48px auto; }}
    label {{ display: block; margin: 16px 0 6px; }}
    input {{ box-sizing: border-box; width: 100%; padding: 10px; }}
    button {{ margin-top: 20px; padding: 10px 16px; }}
    .error {{ color: #b00020; }}
  </style>
</head>
<body>
  <h1>Connect Kaiten</h1>
  <p>Enter your Kaiten company domain and personal API key. The key is kept only for this MCP session.</p>
  {error_html}
  <form method="post" action="/authorize" autocomplete="off">
    {hidden_fields}
    <label for="kaiten_subdomain">Kaiten company domain</label>
    <input id="kaiten_subdomain" name="kaiten_subdomain" placeholder="yourcompany" required>
    <label for="kaiten_token">Kaiten API key</label>
    <input id="kaiten_token" name="kaiten_token" type="password" required>
    <button type="submit">Connect</button>
  </form>
</body>
</html>"""
    )


async def authorize_get(request: Request) -> HTMLResponse:
    return _authorize_form(request)


async def authorize_post(request: Request) -> HTMLResponse | RedirectResponse:
    form = await request.form()
    oauth_fields = {
        "client_id": str(form.get("client_id", "")),
        "redirect_uri": str(form.get("redirect_uri", "")),
        "response_type": str(form.get("response_type", "code")),
        "code_challenge": str(form.get("code_challenge", "")),
        "code_challenge_method": str(form.get("code_challenge_method", "S256")),
        "resource": str(form.get("resource", "")),
        "scope": str(form.get("scope", "")),
        "state": str(form.get("state", "")),
    }
    client_id = str(form.get("client_id", ""))
    redirect_uri = str(form.get("redirect_uri", ""))
    code_challenge = str(form.get("code_challenge", ""))
    resource = str(form.get("resource") or _resource_url(request))
    scopes = parse_scope(str(form.get("scope", "")))
    kaiten_token = str(form.get("kaiten_token", "")).strip()
    kaiten_subdomain = str(form.get("kaiten_subdomain", "")).strip()
    client = AUTH_STORE.get_client(client_id)
    if client is None or not code_challenge:
        return _authorize_form(request, "Invalid OAuth client request", oauth_fields)
    if not kaiten_token or not kaiten_subdomain:
        return _authorize_form(request, "Kaiten domain and API key are required", oauth_fields)
    try:
        validate_redirect_uri(client, redirect_uri)
        credential, _ = await validate_kaiten_credential(
            token=kaiten_token,
            subdomain=kaiten_subdomain,
            base_domain=None,
            base_url=None,
        )
    except (KaitenApiError, ValueError):
        return _authorize_form(request, "Could not validate Kaiten credentials", oauth_fields)

    code = AUTH_STORE.create_authorization_code(
        client_id=client_id,
        redirect_uri=redirect_uri,
        code_challenge=code_challenge,
        subject=f"kaiten:{credential.user_id}",
        credential_id=credential.id,
        resource=resource,
        scopes=scopes,
    )
    params = {"code": code.code}
    if form.get("state"):
        params["state"] = str(form["state"])
    return RedirectResponse(build_redirect_uri(redirect_uri, params), status_code=302)


async def token_post(request: Request) -> JSONResponse:
    form = await request.form()
    if form.get("grant_type") != "authorization_code":
        return JSONResponse({"error": "unsupported_grant_type"}, status_code=400)
    access_token = AUTH_STORE.exchange_authorization_code(
        code=str(form.get("code", "")),
        client_id=str(form.get("client_id", "")),
        redirect_uri=str(form.get("redirect_uri", "")),
        code_verifier=str(form.get("code_verifier", "")),
    )
    if access_token is None or access_token.expires_at is None:
        return JSONResponse({"error": "invalid_grant"}, status_code=400)
    return JSONResponse(
        {
            "access_token": access_token.token,
            "token_type": "Bearer",
            "expires_in": max(0, access_token.expires_at - int(time.time())),
            "scope": " ".join(access_token.scopes),
        }
    )


def _shared_auth_app(app_to_wrap):
    async def wrapped(scope, receive, send) -> None:
        request = Request(scope, receive=receive)
        if not _allowed_origin(request):
            response = JSONResponse({"error": "Forbidden origin"}, status_code=403)
            await response(scope, receive, send)
            return
        if not _is_authorized(request, os.environ.get("MCP_AUTH_TOKEN")):
            response = JSONResponse({"error": "Unauthorized"}, status_code=401)
            await response(scope, receive, send)
            return
        await app_to_wrap(scope, receive, send)

    return wrapped


def _oauth_app(app_to_wrap, resource_metadata_url: AnyHttpUrl | None):
    async def origin_checked(scope, receive, send) -> None:
        request = Request(scope, receive=receive)
        if not _allowed_origin(request):
            response = JSONResponse({"error": "Forbidden origin"}, status_code=403)
            await response(scope, receive, send)
            return
        await app_to_wrap(scope, receive, send)

    protected = RequireAuthMiddleware(
        origin_checked,
        required_scopes=_required_scopes(),
        resource_metadata_url=resource_metadata_url,
    )
    with_context = AuthContextMiddleware(protected)
    return AuthenticationMiddleware(
        with_context,
        backend=BearerAuthBackend(KaitenSessionTokenVerifier()),
    )


def create_http_app(
    *,
    session_manager_cls: type[Any] = DEFAULT_SESSION_MANAGER_CLS,
) -> Starlette:
    mcp_path = _mcp_path()
    auth_mode = _auth_mode()

    session_manager = session_manager_cls(
        app=app,
        event_store=None,
        json_response=True,
        stateless=True,
    )

    async def handle_streamable_http(scope, receive, send) -> None:
        await session_manager.handle_request(scope, receive, send)

    mounted_app = handle_streamable_http
    if auth_mode == "shared":
        mounted_app = _shared_auth_app(mounted_app)
    elif auth_mode == "oauth":
        mounted_app = _oauth_app(mounted_app, _static_resource_metadata_url())

    @asynccontextmanager
    async def lifespan(_: Starlette):
        async with session_manager.run():
            try:
                yield
            finally:
                await close_client()

    routes = [
        Route("/healthz", endpoint=healthz),
        Route("/readyz", endpoint=readyz),
        Route("/.well-known/oauth-protected-resource", endpoint=protected_resource_metadata),
        Route(
            "/.well-known/oauth-protected-resource/{path:path}",
            endpoint=protected_resource_metadata,
        ),
        Route("/.well-known/oauth-authorization-server", endpoint=authorization_server_metadata),
        Route("/.well-known/openid-configuration", endpoint=authorization_server_metadata),
        Route("/register", endpoint=register_client, methods=["POST"]),
        Route("/authorize", endpoint=authorize_get, methods=["GET"]),
        Route("/authorize", endpoint=authorize_post, methods=["POST"]),
        Route("/token", endpoint=token_post, methods=["POST"]),
        Mount(mcp_path, app=mounted_app),
    ]

    return Starlette(
        debug=False,
        lifespan=lifespan,
        routes=routes,
    )


def main() -> None:
    host = os.environ.get("MCP_HTTP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_HTTP_PORT", "8000"))
    uvicorn.run(create_http_app(), host=host, port=port)


__all__ = ["create_http_app", "healthz", "main", "readyz"]
