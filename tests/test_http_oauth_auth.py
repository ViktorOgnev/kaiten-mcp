"""Tests for shared HTTP MCP OAuth onboarding and per-user Kaiten credentials."""

import base64
import hashlib
from contextlib import asynccontextmanager
from dataclasses import replace
from typing import ClassVar
from unittest.mock import AsyncMock, patch
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
import respx
from mcp.server.auth.middleware.auth_context import auth_context_var
from mcp.server.auth.middleware.bearer_auth import AuthenticatedUser
from mcp.server.auth.provider import AccessToken
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from kaiten_mcp.auth import (
    AUTH_STORE,
    DEFAULT_REQUIRED_SCOPE,
    current_kaiten_credential,
    reject_unsafe_public_url,
    validate_redirect_uri,
)
from kaiten_mcp.http_server import create_http_app
from kaiten_mcp.server import ALL_TOOLS, call_tool


class FakeSessionManager:
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


@pytest.fixture(autouse=True)
def _reset_auth_store():
    AUTH_STORE.reset()
    yield
    AUTH_STORE.reset()


def _pkce(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def _oauth_env() -> dict[str, str]:
    return {
        "MCP_HTTP_AUTH_MODE": "oauth",
        "MCP_PUBLIC_URL": "https://mcp.example.com/mcp",
        "MCP_OAUTH_ISSUER_URL": "https://mcp.example.com",
        "MCP_RESOURCE_METADATA_URL": "https://mcp.example.com/.well-known/oauth-protected-resource",
    }


def test_oauth_metadata_endpoints_describe_resource_and_auth_server():
    with patch.dict("os.environ", _oauth_env(), clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            resource = client.get("/.well-known/oauth-protected-resource")
            auth_server = client.get("/.well-known/oauth-authorization-server")

    assert resource.json()["resource"] == "https://mcp.example.com/mcp"
    assert resource.json()["authorization_servers"] == ["https://mcp.example.com"]
    assert auth_server.json()["authorization_endpoint"] == "https://mcp.example.com/authorize"
    assert auth_server.json()["token_endpoint"] == "https://mcp.example.com/token"
    assert auth_server.json()["registration_endpoint"] == "https://mcp.example.com/register"


def test_oauth_metadata_preserves_public_resource_trailing_slash():
    env = {**_oauth_env(), "MCP_PUBLIC_URL": "https://mcp.example.com/mcp/"}
    with patch.dict("os.environ", env, clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            resource = client.get("/.well-known/oauth-protected-resource")

    assert resource.json()["resource"] == "https://mcp.example.com/mcp/"


def test_oauth_metadata_defaults_to_request_origin_and_custom_scopes():
    env = {"MCP_HTTP_AUTH_MODE": "oauth", "MCP_REQUIRED_SCOPES": "kaiten:read kaiten:write"}
    with patch.dict("os.environ", env, clear=True):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            resource = client.get("/.well-known/oauth-protected-resource")
            auth_server = client.get("/.well-known/oauth-authorization-server")

    assert resource.json()["resource"] == "http://testserver/mcp"
    assert resource.json()["authorization_servers"] == ["http://testserver"]
    assert resource.json()["scopes_supported"] == ["kaiten:read", "kaiten:write"]
    assert auth_server.json()["issuer"] == "http://testserver"


def test_oauth_mcp_endpoint_rejects_missing_bearer_with_metadata_header():
    with patch.dict("os.environ", _oauth_env(), clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            response = client.get("/mcp")

    assert response.status_code == 401
    assert response.json()["error"] == "invalid_token"
    assert "resource_metadata" in response.headers["www-authenticate"]


def test_oauth_mcp_metadata_header_can_be_derived_from_public_url():
    env = {"MCP_HTTP_AUTH_MODE": "oauth", "MCP_PUBLIC_URL": "https://mcp.example.com/mcp"}
    with patch.dict("os.environ", env, clear=True):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            response = client.get("/mcp")

    assert response.status_code == 401
    assert (
        "https://mcp.example.com/.well-known/oauth-protected-resource"
        in response.headers["www-authenticate"]
    )


def test_oauth_register_rejects_invalid_redirect_uri_payloads():
    with patch.dict("os.environ", _oauth_env(), clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            missing = client.post("/register", json={})
            empty = client.post("/register", json={"redirect_uris": []})

    assert missing.status_code == 400
    assert missing.json() == {"error": "invalid_redirect_uris"}
    assert empty.status_code == 400
    assert empty.json() == {"error": "invalid_redirect_uris"}


def test_oauth_authorize_get_renders_form_with_hidden_oauth_fields():
    with patch.dict("os.environ", _oauth_env(), clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            response = client.get(
                "/authorize",
                params={
                    "client_id": "client-1",
                    "redirect_uri": "https://llm.example.com/callback",
                    "state": "state-1",
                },
            )

    assert response.status_code == 200
    assert 'name="client_id" value="client-1"' in response.text
    assert 'name="state" value="state-1"' in response.text


def test_oauth_authorize_rejects_invalid_client_request():
    with patch.dict("os.environ", _oauth_env(), clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            response = client.post(
                "/authorize",
                data={
                    "client_id": "unknown-client",
                    "redirect_uri": "https://llm.example.com/callback",
                    "kaiten_subdomain": "acme",
                    "kaiten_token": "kaiten-user-token",
                },
            )

    assert response.status_code == 200
    assert "Invalid OAuth client request" in response.text


def test_oauth_authorize_rejects_unregistered_redirect_uri():
    client_registration = AUTH_STORE.register_client(["https://llm.example.com/callback"])
    with patch.dict("os.environ", _oauth_env(), clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            response = client.post(
                "/authorize",
                data={
                    "client_id": client_registration.client_id,
                    "redirect_uri": "https://evil.example.com/callback",
                    "response_type": "code",
                    "code_challenge": _pkce("verifier"),
                    "code_challenge_method": "S256",
                    "scope": DEFAULT_REQUIRED_SCOPE,
                    "kaiten_subdomain": "acme",
                    "kaiten_token": "kaiten-user-token",
                },
            )

    assert response.status_code == 200
    assert "Could not validate Kaiten credentials" in response.text


def test_oauth_register_authorize_token_and_call_mcp():
    with patch.dict("os.environ", _oauth_env(), clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)

        verifier = "correct-horse-battery-staple"
        redirect_uri = "https://llm.example.com/oauth/callback"
        with TestClient(app) as client:
            registration = client.post("/register", json={"redirect_uris": [redirect_uri]})
            client_id = registration.json()["client_id"]

            with respx.mock:
                respx.get("https://acme.kaiten.ru/api/latest/users/current").mock(
                    return_value=httpx.Response(200, json={"id": 42, "full_name": "Alice"})
                )
                authorization = client.post(
                    "/authorize",
                    data={
                        "client_id": client_id,
                        "redirect_uri": redirect_uri,
                        "response_type": "code",
                        "code_challenge": _pkce(verifier),
                        "code_challenge_method": "S256",
                        "resource": "https://mcp.example.com/mcp",
                        "scope": DEFAULT_REQUIRED_SCOPE,
                        "state": "state-1",
                        "kaiten_subdomain": "acme",
                        "kaiten_token": "kaiten-user-token",
                    },
                    follow_redirects=False,
                )
            location = authorization.headers["location"]
            query = parse_qs(urlsplit(location).query)
            assert query["state"] == ["state-1"]

            token = client.post(
                "/token",
                data={
                    "grant_type": "authorization_code",
                    "code": query["code"][0],
                    "client_id": client_id,
                    "redirect_uri": redirect_uri,
                    "code_verifier": verifier,
                },
            )
            access_token = token.json()["access_token"]
            response = client.get(
                "/mcp",
                headers={"Authorization": f"Bearer {access_token}"},
            )

    assert registration.status_code == 201
    assert authorization.status_code == 302
    assert token.status_code == 200
    assert token.json()["token_type"] == "Bearer"
    assert response.status_code == 200
    assert response.json() == {"transport": "http"}
    assert FakeSessionManager.instances[-1].handle_request.await_count == 1


def test_oauth_token_rejects_unsupported_grant_and_invalid_code():
    with patch.dict("os.environ", _oauth_env(), clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            unsupported = client.post("/token", data={"grant_type": "client_credentials"})
            invalid = client.post(
                "/token",
                data={
                    "grant_type": "authorization_code",
                    "code": "missing-code",
                    "client_id": "client-1",
                    "redirect_uri": "https://llm.example.com/callback",
                    "code_verifier": "verifier",
                },
            )

    assert unsupported.status_code == 400
    assert unsupported.json() == {"error": "unsupported_grant_type"}
    assert invalid.status_code == 400
    assert invalid.json() == {"error": "invalid_grant"}


def test_oauth_authorize_requires_explicit_kaiten_credentials_without_env_fallback():
    with patch.dict(
        "os.environ",
        {**_oauth_env(), "KAITEN_SUBDOMAIN": "env-company", "KAITEN_TOKEN": "env-token"},
        clear=False,
    ):
        app = create_http_app(session_manager_cls=FakeSessionManager)

        verifier = "correct-horse-battery-staple"
        redirect_uri = "https://llm.example.com/oauth/callback"
        with TestClient(app) as client:
            registration = client.post("/register", json={"redirect_uris": [redirect_uri]})
            with respx.mock(assert_all_called=False) as mock_router:
                route = mock_router.get("https://env-company.kaiten.ru/api/latest/users/current")
                response = client.post(
                    "/authorize",
                    data={
                        "client_id": registration.json()["client_id"],
                        "redirect_uri": redirect_uri,
                        "response_type": "code",
                        "code_challenge": _pkce(verifier),
                        "code_challenge_method": "S256",
                        "resource": "https://mcp.example.com/mcp",
                        "scope": DEFAULT_REQUIRED_SCOPE,
                        "kaiten_subdomain": "",
                        "kaiten_token": "",
                    },
                )

    assert response.status_code == 200
    assert "Kaiten domain and API key are required" in response.text
    assert route.called is False


def test_oauth_mcp_endpoint_rejects_insufficient_scope():
    credential = AUTH_STORE.store_credential(
        token="kaiten-user-token",
        subdomain="acme",
        base_domain=None,
        base_url=None,
        user={"id": 42, "full_name": "Alice"},
    )
    client_registration = AUTH_STORE.register_client(["https://llm.example.com/callback"])
    access_token = AccessToken(
        token="mcp-token",
        client_id=client_registration.client_id,
        scopes=["wrong:scope"],
        expires_at=credential.expires_at,
        resource="https://mcp.example.com/mcp",
        subject="kaiten:42",
        claims={"kaiten_credential_id": credential.id},
    )
    AUTH_STORE.access_tokens[access_token.token] = access_token

    with patch.dict("os.environ", _oauth_env(), clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            response = client.get("/mcp", headers={"Authorization": "Bearer mcp-token"})

    assert response.status_code == 403
    assert response.json()["error"] == "insufficient_scope"


def test_oauth_origin_allowlist_blocks_untrusted_browser_origins():
    credential = AUTH_STORE.store_credential(
        token="kaiten-user-token",
        subdomain="acme",
        base_domain=None,
        base_url=None,
        user={"id": 42, "full_name": "Alice"},
    )
    client_registration = AUTH_STORE.register_client(["https://llm.example.com/callback"])
    access_token = AccessToken(
        token="mcp-token",
        client_id=client_registration.client_id,
        scopes=[DEFAULT_REQUIRED_SCOPE],
        expires_at=credential.expires_at,
        resource="https://mcp.example.com/mcp",
        subject="kaiten:42",
        claims={"kaiten_credential_id": credential.id},
    )
    AUTH_STORE.access_tokens[access_token.token] = access_token

    env = {**_oauth_env(), "MCP_ALLOWED_ORIGINS": "https://trusted.example.com"}
    with patch.dict("os.environ", env, clear=False):
        app = create_http_app(session_manager_cls=FakeSessionManager)
        with TestClient(app) as client:
            response = client.get(
                "/mcp",
                headers={
                    "Authorization": "Bearer mcp-token",
                    "Origin": "https://evil.example.com",
                },
            )

    assert response.status_code == 403
    assert response.json() == {"error": "Forbidden origin"}


def test_auth_store_rejects_invalid_authorization_code_exchanges():
    with pytest.raises(ValueError, match="redirect_uris"):
        AUTH_STORE.register_client([])

    credential = AUTH_STORE.store_credential(
        token="kaiten-user-token",
        subdomain="acme",
        base_domain=None,
        base_url=None,
        user={"id": 42, "full_name": "Alice"},
    )
    client_registration = AUTH_STORE.register_client(["https://llm.example.com/callback"])

    assert (
        AUTH_STORE.exchange_authorization_code(
            code="missing-code",
            client_id=client_registration.client_id,
            redirect_uri="https://llm.example.com/callback",
            code_verifier="verifier",
        )
        is None
    )

    expired = AUTH_STORE.create_authorization_code(
        client_id=client_registration.client_id,
        redirect_uri="https://llm.example.com/callback",
        code_challenge=_pkce("verifier"),
        subject="kaiten:42",
        credential_id=credential.id,
        resource="https://mcp.example.com/mcp",
        scopes=[DEFAULT_REQUIRED_SCOPE],
    )
    AUTH_STORE.authorization_codes[expired.code] = replace(expired, expires_at=0)
    assert (
        AUTH_STORE.exchange_authorization_code(
            code=expired.code,
            client_id=client_registration.client_id,
            redirect_uri="https://llm.example.com/callback",
            code_verifier="verifier",
        )
        is None
    )

    wrong_client = AUTH_STORE.create_authorization_code(
        client_id=client_registration.client_id,
        redirect_uri="https://llm.example.com/callback",
        code_challenge=_pkce("verifier"),
        subject="kaiten:42",
        credential_id=credential.id,
        resource="https://mcp.example.com/mcp",
        scopes=[DEFAULT_REQUIRED_SCOPE],
    )
    assert (
        AUTH_STORE.exchange_authorization_code(
            code=wrong_client.code,
            client_id="other-client",
            redirect_uri="https://llm.example.com/callback",
            code_verifier="verifier",
        )
        is None
    )

    wrong_redirect = AUTH_STORE.create_authorization_code(
        client_id=client_registration.client_id,
        redirect_uri="https://llm.example.com/callback",
        code_challenge=_pkce("verifier"),
        subject="kaiten:42",
        credential_id=credential.id,
        resource="https://mcp.example.com/mcp",
        scopes=[DEFAULT_REQUIRED_SCOPE],
    )
    assert (
        AUTH_STORE.exchange_authorization_code(
            code=wrong_redirect.code,
            client_id=client_registration.client_id,
            redirect_uri="https://llm.example.com/other",
            code_verifier="verifier",
        )
        is None
    )

    wrong_verifier = AUTH_STORE.create_authorization_code(
        client_id=client_registration.client_id,
        redirect_uri="https://llm.example.com/callback",
        code_challenge=_pkce("verifier"),
        subject="kaiten:42",
        credential_id=credential.id,
        resource="https://mcp.example.com/mcp",
        scopes=[DEFAULT_REQUIRED_SCOPE],
    )
    assert (
        AUTH_STORE.exchange_authorization_code(
            code=wrong_verifier.code,
            client_id=client_registration.client_id,
            redirect_uri="https://llm.example.com/callback",
            code_verifier="wrong-verifier",
        )
        is None
    )

    missing_credential = AUTH_STORE.create_authorization_code(
        client_id=client_registration.client_id,
        redirect_uri="https://llm.example.com/callback",
        code_challenge=_pkce("verifier"),
        subject="kaiten:42",
        credential_id=credential.id,
        resource="https://mcp.example.com/mcp",
        scopes=[DEFAULT_REQUIRED_SCOPE],
    )
    AUTH_STORE.credentials.pop(credential.id)
    assert (
        AUTH_STORE.exchange_authorization_code(
            code=missing_credential.code,
            client_id=client_registration.client_id,
            redirect_uri="https://llm.example.com/callback",
            code_verifier="verifier",
        )
        is None
    )


def test_auth_store_rejects_expired_or_unlinked_access_tokens_and_credentials():
    credential = AUTH_STORE.store_credential(
        token="kaiten-user-token",
        subdomain="acme",
        base_domain=None,
        base_url=None,
        user={"email": "alice@example.com"},
    )
    expired_token = AccessToken(
        token="expired-token",
        client_id="client-1",
        scopes=[DEFAULT_REQUIRED_SCOPE],
        expires_at=0,
        resource="https://mcp.example.com/mcp",
        subject="kaiten:alice@example.com",
        claims={"kaiten_credential_id": credential.id},
    )
    AUTH_STORE.access_tokens[expired_token.token] = expired_token
    assert AUTH_STORE.verify_access_token("expired-token") is None

    unlinked_token = AccessToken(
        token="unlinked-token",
        client_id="client-1",
        scopes=[DEFAULT_REQUIRED_SCOPE],
        expires_at=credential.expires_at,
        resource="https://mcp.example.com/mcp",
        subject="kaiten:alice@example.com",
        claims={"kaiten_credential_id": "missing"},
    )
    AUTH_STORE.access_tokens[unlinked_token.token] = unlinked_token
    assert AUTH_STORE.verify_access_token("unlinked-token") is None
    assert AUTH_STORE.get_credential("missing") is None

    context_token = auth_context_var.set(AuthenticatedUser(unlinked_token))
    try:
        with pytest.raises(ValueError, match="session expired"):
            current_kaiten_credential()
    finally:
        auth_context_var.reset(context_token)


def test_auth_helpers_reject_invalid_redirect_and_public_urls():
    client_registration = AUTH_STORE.register_client(["https://llm.example.com/callback"])
    with pytest.raises(ValueError, match="redirect_uri"):
        validate_redirect_uri(client_registration, "https://llm.example.com/other")
    with pytest.raises(ValueError, match="public URL"):
        reject_unsafe_public_url("https://mcp.example.com/mcp?token=secret")


async def test_call_tool_uses_request_scoped_kaiten_credential():
    credential = AUTH_STORE.store_credential(
        token="kaiten-user-token",
        subdomain="acme",
        base_domain=None,
        base_url=None,
        user={"id": 42, "full_name": "Alice"},
    )
    access_token = AccessToken(
        token="mcp-token",
        client_id="client-1",
        scopes=[DEFAULT_REQUIRED_SCOPE],
        expires_at=credential.expires_at,
        resource="https://mcp.example.com/mcp",
        subject="kaiten:42",
        claims={"kaiten_credential_id": credential.id},
    )
    context_token = auth_context_var.set(AuthenticatedUser(access_token))
    handler = AsyncMock(return_value={"ok": True})
    try:
        with patch.dict(
            ALL_TOOLS,
            {
                "test_tool": {
                    "handler": handler,
                    "description": "t",
                    "inputSchema": {"type": "object", "properties": {}},
                },
            },
        ):
            result = await call_tool("test_tool", {})
    finally:
        auth_context_var.reset(context_token)

    used_client = handler.await_args.args[0]
    assert used_client.token == "kaiten-user-token"
    assert used_client.base_url == "https://acme.kaiten.ru/api/latest"
    assert result.isError is False
