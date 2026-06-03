#!/usr/bin/env python3
"""Verify the ChatGPT OAuth/DCR path for the remote MCP endpoint.

The script intentionally avoids printing Kaiten tokens, OAuth codes, or access
tokens. It exercises the same public-client OAuth path ChatGPT can use: metadata,
DCR, authorization code + PKCE, token exchange, initialize, and tools/list.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import os
import re
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_ENV_FILES = (
    Path("/etc/kaiten-mcp/kaiten-mcp.env"),
    Path("/etc/kaiten-mcp/kaiten-mcp-chatgpt.env"),
    Path(".env"),
)
DEFAULT_REDIRECT_URI = "https://chatgpt.com/aip/callback"
DEFAULT_SCOPE = "kaiten:tools"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


NO_REDIRECT_OPENER = urllib.request.build_opener(NoRedirect)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def normalize_mcp_url(value: str) -> str:
    if not value:
        fail("Set MCP_PUBLIC_URL or pass --mcp-url.")
    parsed = urllib.parse.urlsplit(value.strip())
    if parsed.scheme != "https" or not parsed.netloc or parsed.query or parsed.fragment:
        fail("MCP URL must be an HTTPS URL without query or fragment.")
    path = parsed.path.rstrip("/")
    if not path:
        path = "/mcp"
    if not path.endswith("/mcp"):
        fail("MCP URL path must end with /mcp or /mcp/.")
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, f"{path}/", "", ""))


def origin_for(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))


def http_request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    form: dict[str, str] | None = None,
    json_body: dict[str, Any] | None = None,
    no_redirect: bool = False,
) -> tuple[int, dict[str, str], bytes]:
    request_headers = dict(headers or {})
    body: bytes | None = None
    if form is not None:
        body = urllib.parse.urlencode(form).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
    if json_body is not None:
        body = json.dumps(json_body, separators=(",", ":")).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")

    request = urllib.request.Request(url, data=body, headers=request_headers, method=method)
    try:
        if no_redirect:
            response = NO_REDIRECT_OPENER.open(request, timeout=45)
        else:
            response = urllib.request.urlopen(request, timeout=45)
        with response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers), exc.read()


def load_json(body: bytes, context: str) -> dict[str, Any]:
    try:
        value = json.loads(body)
    except json.JSONDecodeError as exc:
        fail(f"{context} did not return JSON: {exc}")
    if not isinstance(value, dict):
        fail(f"{context} returned non-object JSON.")
    return value


def parse_mcp_json(body: bytes, context: str) -> dict[str, Any]:
    text = body.decode("utf-8", errors="replace").strip()
    if text.startswith("event:") or "\ndata:" in text or text.startswith("data:"):
        data_lines = [
            line.removeprefix("data:").strip()
            for line in text.splitlines()
            if line.startswith("data:")
        ]
        text = "\n".join(data_lines).strip()
    return load_json(text.encode("utf-8"), context)


def pkce_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def html_error(body: bytes) -> str:
    text = body.decode("utf-8", errors="replace")
    match = re.search(r'<p class="error">(.*?)</p>', text, flags=re.S)
    if not match:
        return "no HTML error message"
    return html.unescape(re.sub(r"<.*?>", "", match.group(1))).strip()


def require_keys(data: dict[str, Any], keys: tuple[str, ...], context: str) -> None:
    missing = [key for key in keys if not data.get(key)]
    if missing:
        fail(f"{context} response is missing: {', '.join(missing)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp-url", default=os.environ.get("MCP_PUBLIC_URL", ""))
    parser.add_argument("--env-file", action="append", type=Path, default=[])
    parser.add_argument("--redirect-uri", default=os.environ.get("MCP_REDIRECT_URI", DEFAULT_REDIRECT_URI))
    parser.add_argument("--scope", default=os.environ.get("MCP_REQUIRED_SCOPES", DEFAULT_SCOPE))
    args = parser.parse_args()

    for path in (*args.env_file, *DEFAULT_ENV_FILES):
        load_env_file(path)

    mcp_url = normalize_mcp_url(args.mcp_url or os.environ.get("MCP_PUBLIC_URL", ""))
    issuer = origin_for(mcp_url)
    kaiten_subdomain = os.environ.get("KAITEN_SUBDOMAIN", "").strip()
    kaiten_token = os.environ.get("KAITEN_TOKEN", "").strip()
    if not kaiten_subdomain or not kaiten_token:
        fail("Set KAITEN_SUBDOMAIN and KAITEN_TOKEN for the OAuth onboarding smoke.")

    print(f"Verifying MCP URL: {mcp_url}")

    status, _, body = http_request("GET", f"{issuer}/.well-known/oauth-protected-resource")
    if status != 200:
        fail(f"protected-resource metadata returned HTTP {status}.")
    resource_metadata = load_json(body, "protected-resource metadata")
    auth_servers = resource_metadata.get("authorization_servers")
    if not isinstance(auth_servers, list) or not auth_servers:
        fail("protected-resource metadata does not list authorization_servers.")
    resource = str(resource_metadata.get("resource", ""))
    if normalize_mcp_url(resource) != mcp_url:
        fail(f"protected-resource metadata resource does not match MCP URL: {resource}")
    print(f"protected-resource: 200 resource={resource}")

    auth_server = str(auth_servers[0]).rstrip("/")
    status, _, body = http_request("GET", f"{auth_server}/.well-known/oauth-authorization-server")
    if status != 200:
        fail(f"authorization-server metadata returned HTTP {status}.")
    auth_metadata = load_json(body, "authorization-server metadata")
    require_keys(
        auth_metadata,
        ("registration_endpoint", "authorization_endpoint", "token_endpoint"),
        "authorization-server metadata",
    )
    token_methods = auth_metadata.get("token_endpoint_auth_methods_supported", [])
    if "none" not in token_methods:
        fail("authorization-server metadata does not advertise public-client token auth method none.")
    print("authorization-server: 200 DCR=true token_auth=none")

    status, _, body = http_request(
        "POST",
        str(auth_metadata["registration_endpoint"]),
        json_body={"redirect_uris": [args.redirect_uri]},
    )
    if status != 201:
        fail(f"DCR registration returned HTTP {status}.")
    registration = load_json(body, "DCR registration")
    require_keys(registration, ("client_id",), "DCR registration")
    client_id = str(registration["client_id"])
    print("register: 201")

    verifier = secrets.token_urlsafe(48)
    status, headers, body = http_request(
        "POST",
        str(auth_metadata["authorization_endpoint"]),
        form={
            "client_id": client_id,
            "redirect_uri": args.redirect_uri,
            "response_type": "code",
            "code_challenge": pkce_challenge(verifier),
            "code_challenge_method": "S256",
            "resource": mcp_url,
            "scope": args.scope,
            "state": "kaiten-mcp-smoke",
            "kaiten_subdomain": kaiten_subdomain,
            "kaiten_token": kaiten_token,
        },
        no_redirect=True,
    )
    if status != 302:
        fail(f"authorize returned HTTP {status}: {html_error(body)}")
    location = headers.get("Location") or headers.get("location")
    if not location:
        fail("authorize did not return a Location header.")
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(location).query)
    code_values = query.get("code")
    if not code_values:
        fail("authorize redirect did not include an authorization code.")
    print("authorize: 302")

    status, _, body = http_request(
        "POST",
        str(auth_metadata["token_endpoint"]),
        form={
            "grant_type": "authorization_code",
            "code": code_values[0],
            "client_id": client_id,
            "redirect_uri": args.redirect_uri,
            "code_verifier": verifier,
        },
    )
    if status != 200:
        fail(f"token exchange returned HTTP {status}.")
    token = load_json(body, "token exchange")
    require_keys(token, ("access_token", "token_type"), "token exchange")
    if token.get("token_type") != "Bearer":
        fail("token exchange did not return a Bearer token.")
    print(f"token: 200 scope={token.get('scope', '')}")

    headers = {
        "Authorization": f"Bearer {token['access_token']}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    status, _, body = http_request(
        "POST",
        mcp_url,
        headers=headers,
        json_body={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "kaiten-mcp-live-smoke", "version": "0.1"},
            },
        },
    )
    if status != 200:
        fail(f"MCP initialize returned HTTP {status}.")
    initialize = parse_mcp_json(body, "MCP initialize")
    if "result" not in initialize:
        fail(f"MCP initialize returned an error: {initialize.get('error')}")
    print("initialize: 200")

    status, _, _ = http_request(
        "POST",
        mcp_url,
        headers=headers,
        json_body={"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
    )
    if status not in {200, 202}:
        fail(f"MCP initialized notification returned HTTP {status}.")
    print(f"initialized-notification: {status}")

    status, _, body = http_request(
        "POST",
        mcp_url,
        headers=headers,
        json_body={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    )
    if status != 200:
        fail(f"MCP tools/list returned HTTP {status}.")
    tools_result = parse_mcp_json(body, "MCP tools/list")
    tools = ((tools_result.get("result") or {}).get("tools") or [])
    if not isinstance(tools, list) or not tools:
        fail("MCP tools/list returned no tools.")
    first_names = [str(tool.get("name", "")) for tool in tools[:8] if isinstance(tool, dict)]
    print(f"tools/list: 200 tools={len(tools)} first={', '.join(first_names)}")
    print("OAuth DCR MCP smoke passed.")


if __name__ == "__main__":
    main()
