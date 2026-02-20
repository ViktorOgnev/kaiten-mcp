"""Async HTTP client for Kaiten REST API."""

import asyncio
import contextlib
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

API_VERSION = "latest"
RATE_LIMIT_DELAY = 0.22  # ~4.5 req/s to stay under 5 req/s limit
RETRY_DELAY = 2.0
MAX_RETRIES = 3


class KaitenApiError(Exception):
    """Kaiten API error with status code and message."""

    def __init__(self, status_code: int, message: str, body: Any = None):
        self.status_code = status_code
        self.message = message
        self.body = body
        super().__init__(f"HTTP {status_code}: {message}")


class KaitenClient:
    """Async HTTP client for Kaiten API with rate limiting."""

    def __init__(self, domain: str | None = None, token: str | None = None):
        self.domain = domain or os.environ.get("KAITEN_DOMAIN", "")
        self.token = token or os.environ.get("KAITEN_TOKEN", "")
        if not self.domain:
            raise ValueError("KAITEN_DOMAIN is required")
        if not self.token:
            raise ValueError("KAITEN_TOKEN is required")
        self.base_url = f"https://{self.domain}.kaiten.ru/api/{API_VERSION}"
        self._client: httpx.AsyncClient | None = None
        self._last_request_time = 0.0
        self._rate_lock = asyncio.Lock()

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    async def _rate_limit(self) -> None:
        async with self._rate_lock:
            now = asyncio.get_running_loop().time()
            elapsed = now - self._last_request_time
            if elapsed < RATE_LIMIT_DELAY:
                await asyncio.sleep(RATE_LIMIT_DELAY - elapsed)
            self._last_request_time = asyncio.get_running_loop().time()

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        client = await self._get_client()

        # Filter None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        for attempt in range(MAX_RETRIES):
            await self._rate_limit()
            try:
                response = await client.request(method, path, params=params, json=json)
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        try:
                            delay = float(retry_after)
                        except ValueError:
                            delay = RETRY_DELAY * (attempt + 1)
                    else:
                        delay = RETRY_DELAY * (attempt + 1)
                    logger.warning("Rate limited, retrying after %.1fs", delay)
                    await asyncio.sleep(delay)
                    continue
                if response.status_code >= 400:
                    body = None
                    with contextlib.suppress(Exception):
                        body = response.json()
                    msg: str = ""
                    if isinstance(body, dict):
                        msg = str(body.get("message", body.get("error", "")))
                    if not msg:
                        msg = response.text[:500]
                    raise KaitenApiError(response.status_code, msg, body)
                if response.status_code == 204:
                    return None
                if not response.content:
                    return None
                return response.json()
            except httpx.HTTPError as e:
                if attempt == MAX_RETRIES - 1:
                    raise KaitenApiError(0, f"Connection error: {e}") from e
                await asyncio.sleep(RETRY_DELAY)

        # All retries exhausted (e.g. repeated 429)
        raise KaitenApiError(429, "Rate limit retries exhausted")

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        return await self._request("POST", path, json=json)

    async def patch(self, path: str, json: dict[str, Any] | None = None) -> Any:
        return await self._request("PATCH", path, json=json)

    async def delete(self, path: str, json: dict[str, Any] | None = None) -> Any:
        return await self._request("DELETE", path, json=json)

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
