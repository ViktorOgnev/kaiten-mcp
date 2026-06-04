"""Tests for direct entity tool helpers."""

import pytest

from kaiten_mcp.tools.entity_helpers import make_direct_handler


class DummyClient:
    def __init__(self):
        self.calls = []

    async def get(self, path, params=None):
        self.calls.append(("GET", path, params, None, False))
        return [{"id": 1, "title": "A", "owner": {"id": 2, "full_name": "Owner", "email": "x"}}]

    async def post(self, path, json=None):
        self.calls.append(("POST", path, None, json, False))
        return {"ok": True}

    async def patch(self, path, json=None):
        self.calls.append(("PATCH", path, None, json, False))
        return {"ok": True}

    async def delete(self, path, json=None):
        self.calls.append(("DELETE", path, None, json, False))
        return None

    async def get_root(self, path, params=None):
        self.calls.append(("GET", path, params, None, True))
        return {"root": True}

    async def post_root(self, path, json=None):
        self.calls.append(("POST", path, None, json, True))
        return {"root": True}

    async def patch_root(self, path, json=None):
        self.calls.append(("PATCH", path, None, json, True))
        return {"root": True}

    async def delete_root(self, path, json=None):
        self.calls.append(("DELETE", path, None, json, True))
        return None


async def test_direct_get_shapes_query_and_response():
    client = DummyClient()
    handler = make_direct_handler(
        method="GET",
        path_template="/items/{item_id}",
        path_fields=("item_id",),
        query_fields=("start_index", "filters"),
        query_aliases={"start_index": "startIndex"},
        encode_json_query_fields=("filters",),
        compact_supported=True,
        fields_supported=True,
    )

    result = await handler(
        client,
        {
            "item_id": 10,
            "start_index": 2,
            "filters": {"name": "A"},
            "compact": True,
            "fields": "id,owner",
        },
    )

    assert client.calls == [
        ("GET", "/items/10", {"filters": '{"name": "A"}', "startIndex": 2}, None, False)
    ]
    assert result == [{"id": 1, "owner": {"id": 2, "full_name": "Owner"}}]


@pytest.mark.parametrize("method", ["POST", "PATCH", "DELETE"])
async def test_direct_body_methods_merge_payload(method):
    client = DummyClient()
    handler = make_direct_handler(
        method=method,
        path_template="/items",
        body_fields=("name",),
        include_payload=True,
    )

    await handler(client, {"name": "A", "payload": {"extra": True}})

    assert client.calls == [(method, "/items", None, {"name": "A", "extra": True}, False)]


@pytest.mark.parametrize("method", ["GET", "POST", "PATCH", "DELETE"])
async def test_root_api_methods(method):
    client = DummyClient()
    handler = make_direct_handler(
        method=method,
        path_template="/root",
        query_fields=("q",),
        body_fields=("name",),
        root_api=True,
    )

    await handler(client, {"q": "x", "name": "A"})

    if method == "GET":
        assert client.calls == [("GET", "/root", {"q": "x"}, None, True)]
    elif method == "DELETE":
        assert client.calls == [("DELETE", "/root", None, {"name": "A"}, True)]
    else:
        assert client.calls == [(method, "/root", None, {"name": "A"}, True)]


async def test_unsupported_methods_raise():
    client = DummyClient()
    handler = make_direct_handler(method="PUT", path_template="/items")
    with pytest.raises(ValueError, match="Unsupported method"):
        await handler(client, {})

    root_handler = make_direct_handler(method="PUT", path_template="/items", root_api=True)
    with pytest.raises(ValueError, match="Unsupported root method"):
        await root_handler(client, {})
