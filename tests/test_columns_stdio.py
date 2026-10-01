"""Black-box stdio tests: run unchanged against Python and baked Docker."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from tests.columns_stdio import column_session


@pytest.fixture
def http_api():
    requests = []

    class API(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def respond(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            requests.append((self.command, self.path, body))
            payload = json.dumps({"id": 5, **body}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        do_POST = respond
        do_PATCH = respond

    server = ThreadingHTTPServer(("127.0.0.1", 0), API)
    worker = threading.Thread(target=lambda: server.serve_forever(poll_interval=0.01), daemon=True)
    worker.start()
    try:
        yield (
            {
                "KAITEN_BASE_URL": f"http://127.0.0.1:{server.server_port}",
                "KAITEN_TOKEN": "local-test-only",
            },
            requests,
        )
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)
        assert not worker.is_alive()


@pytest.mark.parametrize(
    "tool, ids",
    [
        ("kaiten_update_column", {"board_id": 10, "column_id": 5}),
        ("kaiten_update_subcolumn", {"column_id": 10, "subcolumn_id": 20}),
    ],
)
@pytest.mark.parametrize(
    "fields, error",
    [
        ({}, "at least one non-null"),
        ({"auto_archive_days": 14}, "Additional properties"),
        ({"title": "Must not change", "auto_archive_days": 14}, "Additional properties"),
        ({"wip_limit": None}, "not of type"),
        ({"wip_limit": "0"}, "not of type"),
        ({"wip_limit": False}, "not of type"),
    ],
)
async def test_stdio_rejects_invalid_update_without_http(http_api, tool, ids, fields, error):
    env, requests = http_api
    async with column_session(env) as session:
        definitions = {t.name: t for t in (await session.list_tools()).tools}
        assert definitions[tool].inputSchema["additionalProperties"] is False
        result = await session.call_tool(tool, {**ids, **fields})
    assert result.isError
    assert error in " ".join(c.text for c in result.content if c.type == "text")
    assert requests == []


@pytest.mark.parametrize("variant", ["minimal", "zero", "all_fields"])
@pytest.mark.parametrize(
    "tool, ids, required, optional, method, path",
    [
        (
            "kaiten_create_column",
            {"board_id": 10},
            {"title": "Queue", "type": 1},
            {"wip_limit": 5, "wip_limit_type": 2, "col_count": 2, "sort_order": 1.5},
            "POST",
            "/boards/10/columns",
        ),
        (
            "kaiten_update_column",
            {"board_id": 10, "column_id": 5},
            {},
            {
                "title": "Done",
                "type": 3,
                "wip_limit": 5,
                "wip_limit_type": 2,
                "col_count": 2,
                "sort_order": 1.5,
            },
            "PATCH",
            "/boards/10/columns/5",
        ),
        (
            "kaiten_create_subcolumn",
            {"column_id": 10},
            {"title": "Review"},
            {"wip_limit": 5, "col_count": 2, "sort_order": 1.5},
            "POST",
            "/columns/10/subcolumns",
        ),
        (
            "kaiten_update_subcolumn",
            {"column_id": 10, "subcolumn_id": 20},
            {},
            {"title": "Ready", "wip_limit": 5, "col_count": 2, "sort_order": 1.5},
            "PATCH",
            "/columns/10/subcolumns/20",
        ),
    ],
)
async def test_stdio_sends_exact_body(
    http_api, variant, tool, ids, required, optional, method, path
):
    env, requests = http_api
    if variant == "all_fields":
        body = {**required, **optional}
    elif variant == "zero":
        body = {**required, "wip_limit": 0, "sort_order": 0}
    else:
        body = required or {"title": "Renamed"}
    async with column_session(env) as session:
        result = await session.call_tool(tool, {**ids, **body})
    assert not result.isError
    assert requests == [(method, "/api/latest" + path, body)]
