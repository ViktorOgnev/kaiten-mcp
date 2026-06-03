"""OAuth-style session credentials for shared HTTP MCP deployments."""

import base64
import hashlib
import secrets
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode, urlsplit

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken

from kaiten_mcp.client import KaitenClient

DEFAULT_REQUIRED_SCOPE = "kaiten:tools"


@dataclass(frozen=True)
class KaitenCredential:
    id: str
    token: str
    subdomain: str
    base_domain: str | None
    base_url: str | None
    user_id: str
    user_label: str
    expires_at: int


@dataclass(frozen=True)
class OAuthClient:
    client_id: str
    redirect_uris: tuple[str, ...]
    issued_at: int


@dataclass(frozen=True)
class AuthorizationCode:
    code: str
    client_id: str
    redirect_uri: str
    code_challenge: str
    subject: str
    credential_id: str
    resource: str
    scopes: tuple[str, ...]
    expires_at: int


class EphemeralAuthStore:
    """In-memory OAuth code/access-token store with Kaiten credentials."""

    def __init__(self, *, credential_ttl_seconds: int = 8 * 60 * 60):
        self.credential_ttl_seconds = credential_ttl_seconds
        self.clients: dict[str, OAuthClient] = {}
        self.credentials: dict[str, KaitenCredential] = {}
        self.authorization_codes: dict[str, AuthorizationCode] = {}
        self.access_tokens: dict[str, AccessToken] = {}

    def register_client(self, redirect_uris: list[str] | tuple[str, ...]) -> OAuthClient:
        if not redirect_uris:
            raise ValueError("redirect_uris is required")
        client = OAuthClient(
            client_id=f"mcp_client_{secrets.token_urlsafe(24)}",
            redirect_uris=tuple(str(uri) for uri in redirect_uris),
            issued_at=int(time.time()),
        )
        self.clients[client.client_id] = client
        return client

    def get_client(self, client_id: str) -> OAuthClient | None:
        return self.clients.get(client_id)

    def store_credential(
        self,
        *,
        token: str,
        subdomain: str,
        base_domain: str | None,
        base_url: str | None,
        user: dict[str, Any],
    ) -> KaitenCredential:
        now = int(time.time())
        user_id = str(user.get("id") or user.get("uid") or user.get("email") or "unknown")
        user_label = str(user.get("full_name") or user.get("email") or user_id)
        credential = KaitenCredential(
            id=f"kcred_{secrets.token_urlsafe(24)}",
            token=token,
            subdomain=subdomain,
            base_domain=base_domain,
            base_url=base_url,
            user_id=user_id,
            user_label=user_label,
            expires_at=now + self.credential_ttl_seconds,
        )
        self.credentials[credential.id] = credential
        return credential

    def create_authorization_code(
        self,
        *,
        client_id: str,
        redirect_uri: str,
        code_challenge: str,
        subject: str,
        credential_id: str,
        resource: str,
        scopes: list[str],
    ) -> AuthorizationCode:
        now = int(time.time())
        code = AuthorizationCode(
            code=f"mcp_code_{secrets.token_urlsafe(24)}",
            client_id=client_id,
            redirect_uri=redirect_uri,
            code_challenge=code_challenge,
            subject=subject,
            credential_id=credential_id,
            resource=resource,
            scopes=tuple(scopes),
            expires_at=now + 5 * 60,
        )
        self.authorization_codes[code.code] = code
        return code

    def exchange_authorization_code(
        self,
        *,
        code: str,
        client_id: str,
        redirect_uri: str,
        code_verifier: str,
    ) -> AccessToken | None:
        authorization_code = self.authorization_codes.pop(code, None)
        if authorization_code is None:
            return None
        if authorization_code.expires_at < int(time.time()):
            return None
        if authorization_code.client_id != client_id:
            return None
        if authorization_code.redirect_uri != redirect_uri:
            return None
        if _pkce_s256(code_verifier) != authorization_code.code_challenge:
            return None
        credential = self.credentials.get(authorization_code.credential_id)
        if credential is None or credential.expires_at < int(time.time()):
            return None

        token = f"mcp_at_{secrets.token_urlsafe(32)}"
        access_token = AccessToken(
            token=token,
            client_id=client_id,
            scopes=list(authorization_code.scopes),
            expires_at=credential.expires_at,
            resource=authorization_code.resource,
            subject=authorization_code.subject,
            claims={"kaiten_credential_id": authorization_code.credential_id},
        )
        self.access_tokens[token] = access_token
        return access_token

    def verify_access_token(self, token: str) -> AccessToken | None:
        access_token = self.access_tokens.get(token)
        if access_token is None or (
            access_token.expires_at is not None and access_token.expires_at < int(time.time())
        ):
            return None
        credential_id = str((access_token.claims or {}).get("kaiten_credential_id", ""))
        credential = self.credentials.get(credential_id)
        if credential is None or credential.expires_at < int(time.time()):
            return None
        return access_token

    def get_credential(self, credential_id: str) -> KaitenCredential | None:
        credential = self.credentials.get(credential_id)
        if credential is None or credential.expires_at < int(time.time()):
            return None
        return credential

    def reset(self) -> None:
        self.clients.clear()
        self.credentials.clear()
        self.authorization_codes.clear()
        self.access_tokens.clear()


AUTH_STORE = EphemeralAuthStore()


class KaitenSessionTokenVerifier:
    async def verify_token(self, token: str) -> AccessToken | None:
        return AUTH_STORE.verify_access_token(token)


def _pkce_s256(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def parse_scope(value: str | None) -> list[str]:
    scopes = [scope for scope in (value or DEFAULT_REQUIRED_SCOPE).split() if scope]
    return scopes or [DEFAULT_REQUIRED_SCOPE]


def current_kaiten_credential() -> KaitenCredential | None:
    access_token = get_access_token()
    if access_token is None:
        return None
    credential_id = str((access_token.claims or {}).get("kaiten_credential_id", ""))
    credential = AUTH_STORE.get_credential(credential_id)
    if credential is None:
        raise ValueError("Kaiten credential session expired; reconnect the MCP server")
    return credential


async def validate_kaiten_credential(
    *,
    token: str,
    subdomain: str,
    base_domain: str | None,
    base_url: str | None,
) -> tuple[KaitenCredential, dict[str, Any]]:
    client = KaitenClient(
        domain=subdomain or None,
        token=token,
        base_domain=base_domain,
        base_url=base_url,
    )
    try:
        user = await client.get("/users/current")
    finally:
        await client.close()
    credential = AUTH_STORE.store_credential(
        token=token,
        subdomain=subdomain,
        base_domain=base_domain,
        base_url=base_url,
        user=user if isinstance(user, dict) else {},
    )
    return credential, user if isinstance(user, dict) else {}


def validate_redirect_uri(client: OAuthClient, redirect_uri: str) -> None:
    if redirect_uri not in client.redirect_uris:
        raise ValueError("redirect_uri is not registered for this client")


def build_redirect_uri(redirect_uri: str, params: dict[str, str]) -> str:
    delimiter = "&" if "?" in redirect_uri else "?"
    return f"{redirect_uri}{delimiter}{urlencode(params)}"


def reject_unsafe_public_url(url: str) -> None:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError("public URL must be an HTTPS URL without query or fragment")
