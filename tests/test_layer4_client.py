"""Tests for KaitenClient – Layer 4 (HTTP transport)."""

import asyncio

import httpx
import pytest
import respx

from kaiten_mcp.client import (
    KaitenApiError,
    KaitenClient,
    MAX_RETRIES,
    RATE_LIMIT_DELAY,
    RETRY_DELAY,
)

DOMAIN = "test-company"
TOKEN = "test-token-12345"
BASE = f"https://{DOMAIN}.kaiten.ru/api/latest"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client():
    """Return a KaitenClient with rate-limit delay neutralised."""
    c = KaitenClient(domain=DOMAIN, token=TOKEN)
    c._last_request_time = 0.0
    return c


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------

class TestConstructor:
    def test_requires_domain(self, monkeypatch):
        monkeypatch.delenv("KAITEN_DOMAIN", raising=False)
        with pytest.raises(ValueError, match="KAITEN_DOMAIN is required"):
            KaitenClient(domain="", token="tok")

    def test_requires_token(self, monkeypatch):
        monkeypatch.delenv("KAITEN_TOKEN", raising=False)
        with pytest.raises(ValueError, match="KAITEN_TOKEN is required"):
            KaitenClient(domain="acme", token="")

    def test_base_url_built_correctly(self, client):
        assert client.base_url == BASE

    def test_lazy_client_init(self, client):
        assert client._client is None


# ---------------------------------------------------------------------------
# HTTP method delegation
# ---------------------------------------------------------------------------

class TestMethodDelegation:
    @respx.mock
    async def test_get_delegates(self, client):
        route = respx.get(f"{BASE}/cards").respond(json={"ok": True})
        result = await client.get("/cards", params={"a": "1"})
        assert result == {"ok": True}
        assert route.called
        assert route.calls.last.request.method == "GET"

    @respx.mock
    async def test_post_delegates(self, client):
        route = respx.post(f"{BASE}/cards").respond(json={"id": 1})
        result = await client.post("/cards", json={"title": "t"})
        assert result == {"id": 1}
        assert route.calls.last.request.method == "POST"

    @respx.mock
    async def test_patch_delegates(self, client):
        route = respx.patch(f"{BASE}/cards/1").respond(json={"id": 1})
        result = await client.patch("/cards/1", json={"title": "u"})
        assert result == {"id": 1}
        assert route.calls.last.request.method == "PATCH"

    @respx.mock
    async def test_delete_delegates(self, client):
        route = respx.delete(f"{BASE}/cards/1").respond(204)
        result = await client.delete("/cards/1")
        assert result is None
        assert route.calls.last.request.method == "DELETE"


# ---------------------------------------------------------------------------
# Authorization header
# ---------------------------------------------------------------------------

class TestHeaders:
    @respx.mock
    async def test_bearer_token_sent(self, client):
        route = respx.get(f"{BASE}/me").respond(json={})
        await client.get("/me")
        auth = route.calls.last.request.headers["authorization"]
        assert auth == f"Bearer {TOKEN}"


# ---------------------------------------------------------------------------
# Params filtering
# ---------------------------------------------------------------------------

class TestParamsFiltering:
    @respx.mock
    async def test_none_values_stripped(self, client):
        route = respx.get(f"{BASE}/cards").respond(json=[])
        await client.get("/cards", params={"a": "1", "b": None, "c": "3"})
        url = str(route.calls.last.request.url)
        assert "a=1" in url
        assert "c=3" in url
        assert "b=" not in url

    @respx.mock
    async def test_empty_params_ok(self, client):
        respx.get(f"{BASE}/cards").respond(json=[])
        result = await client.get("/cards", params={})
        assert result == []

    @respx.mock
    async def test_none_params_ok(self, client):
        respx.get(f"{BASE}/cards").respond(json=[])
        result = await client.get("/cards", params=None)
        assert result == []


# ---------------------------------------------------------------------------
# Response handling
# ---------------------------------------------------------------------------

class TestResponseHandling:
    @respx.mock
    async def test_204_returns_none(self, client):
        respx.delete(f"{BASE}/cards/1").respond(204)
        assert await client.delete("/cards/1") is None

    @respx.mock
    async def test_200_returns_json(self, client):
        respx.get(f"{BASE}/cards").respond(json={"id": 42})
        assert await client.get("/cards") == {"id": 42}


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrorHandling:
    @respx.mock
    async def test_400_raises_with_message_field(self, client):
        respx.post(f"{BASE}/cards").respond(
            400, json={"message": "Bad request"}
        )
        with pytest.raises(KaitenApiError) as exc_info:
            await client.post("/cards", json={})
        assert exc_info.value.status_code == 400
        assert exc_info.value.message == "Bad request"

    @respx.mock
    async def test_404_raises_with_error_field(self, client):
        respx.get(f"{BASE}/cards/999").respond(
            404, json={"error": "Not found"}
        )
        with pytest.raises(KaitenApiError) as exc_info:
            await client.get("/cards/999")
        assert exc_info.value.status_code == 404
        assert exc_info.value.message == "Not found"

    @respx.mock
    async def test_500_raises(self, client):
        respx.get(f"{BASE}/me").respond(500, json={"message": "Boom"})
        with pytest.raises(KaitenApiError) as exc_info:
            await client.get("/me")
        assert exc_info.value.status_code == 500

    @respx.mock
    async def test_non_json_error_body_falls_back_to_text(self, client):
        respx.get(f"{BASE}/me").respond(
            502, content=b"Bad Gateway", headers={"content-type": "text/plain"}
        )
        with pytest.raises(KaitenApiError) as exc_info:
            await client.get("/me")
        assert "Bad Gateway" in exc_info.value.message

    @respx.mock
    async def test_error_body_stored(self, client):
        body = {"message": "nope", "details": "extra"}
        respx.post(f"{BASE}/cards").respond(400, json=body)
        with pytest.raises(KaitenApiError) as exc_info:
            await client.post("/cards", json={})
        assert exc_info.value.body == body


# ---------------------------------------------------------------------------
# 429 retry with exponential backoff
# ---------------------------------------------------------------------------

class TestRetry429:
    @respx.mock
    async def test_429_then_success(self, client):
        route = respx.get(f"{BASE}/cards")
        route.side_effect = [
            httpx.Response(429, text="rate limited"),
            httpx.Response(200, json={"ok": True}),
        ]
        result = await client.get("/cards")
        assert result == {"ok": True}
        assert route.call_count == 2

    @respx.mock
    async def test_429_exhausts_retries(self, client):
        respx.get(f"{BASE}/cards").respond(429, text="rate limited")
        # After MAX_RETRIES 429s the last one falls through to >=400 handling
        # which raises KaitenApiError (status_code=429).
        with pytest.raises(KaitenApiError) as exc_info:
            await client.get("/cards")
        assert exc_info.value.status_code == 429


# ---------------------------------------------------------------------------
# Connection errors (httpx.HTTPError)
# ---------------------------------------------------------------------------

class TestConnectionErrors:
    @respx.mock
    async def test_connection_error_on_last_attempt(self, client):
        respx.get(f"{BASE}/me").mock(
            side_effect=httpx.ConnectError("refused")
        )
        with pytest.raises(KaitenApiError) as exc_info:
            await client.get("/me")
        assert exc_info.value.status_code == 0
        assert "Connection error" in exc_info.value.message

    @respx.mock
    async def test_connection_error_retries_then_succeeds(self, client):
        route = respx.get(f"{BASE}/me")
        route.side_effect = [
            httpx.ConnectError("refused"),
            httpx.Response(200, json={"id": 1}),
        ]
        result = await client.get("/me")
        assert result == {"id": 1}
        assert route.call_count == 2


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

class TestRateLimit:
    @respx.mock
    async def test_rate_limit_enforced_between_requests(self, client):
        respx.get(f"{BASE}/me").respond(json={})
        # First request sets _last_request_time
        await client.get("/me")
        t1 = client._last_request_time
        assert t1 > 0

        # Second request should update _last_request_time again
        await client.get("/me")
        t2 = client._last_request_time
        assert t2 >= t1

    @respx.mock
    async def test_rate_limit_delays_rapid_requests(self, client):
        respx.get(f"{BASE}/me").respond(json={})
        # Make the first request to set a recent _last_request_time
        await client.get("/me")
        # Set _last_request_time to "now" so next request must wait
        loop = asyncio.get_event_loop()
        client._last_request_time = loop.time()

        start = loop.time()
        await client.get("/me")
        elapsed = loop.time() - start
        # Should have waited approximately RATE_LIMIT_DELAY
        assert elapsed >= RATE_LIMIT_DELAY * 0.8


# ---------------------------------------------------------------------------
# Client lifecycle
# ---------------------------------------------------------------------------

class TestLifecycle:
    @respx.mock
    async def test_close_closes_underlying_client(self, client):
        respx.get(f"{BASE}/me").respond(json={})
        await client.get("/me")  # triggers lazy init
        assert client._client is not None
        await client.close()
        assert client._client.is_closed

    async def test_close_noop_when_no_client(self, client):
        # Should not raise when _client is None
        await client.close()

    @respx.mock
    async def test_client_recreated_after_close(self, client):
        respx.get(f"{BASE}/me").respond(json={})
        await client.get("/me")
        first = client._client
        await client.close()

        # Next request should create a new internal client
        await client.get("/me")
        assert client._client is not first
        assert not client._client.is_closed
