"""Tests for server.py compact JSON and file-based output (Phase 8)."""
import json
import os
import tempfile

import pytest
from unittest.mock import AsyncMock, patch

from mcp.types import CallToolResult, TextContent

from kaiten_mcp.server import call_tool, ALL_TOOLS


def _text(result: CallToolResult) -> str:
    """Extract the text string from a CallToolResult."""
    assert len(result.content) == 1
    item = result.content[0]
    assert isinstance(item, TextContent)
    return item.text


@pytest.fixture(autouse=True)
def _inject_client():
    """Inject a mock client so get_client() does not create a real one."""
    with patch("kaiten_mcp.server._client", object()):
        yield


class TestCompactJsonSerialization:
    """Test that large responses use compact JSON (no indent)."""

    async def test_small_response_uses_indent(self):
        """Small responses should be pretty-printed with indentation."""
        handler = AsyncMock(return_value={"id": 1})
        with patch.dict(ALL_TOOLS, {
            "test_tool": {"handler": handler, "description": "t", "inputSchema": {"type": "object", "properties": {}}},
        }):
            result = await call_tool("test_tool", {})
        text = _text(result)
        # Pretty-printed JSON has newlines
        assert "\n" in text

    async def test_large_response_uses_compact_json(self):
        """Responses exceeding threshold should use compact JSON."""
        from kaiten_mcp.server import COMPACT_JSON_THRESHOLD
        # Create data that produces indented JSON larger than the threshold
        item_count = (COMPACT_JSON_THRESHOLD // 20) + 50
        large_data = [{"id": i, "data": "x" * 10} for i in range(item_count)]
        handler = AsyncMock(return_value=large_data)
        with patch.dict(ALL_TOOLS, {
            "test_tool": {"handler": handler, "description": "t", "inputSchema": {"type": "object", "properties": {}}},
        }):
            result = await call_tool("test_tool", {})
        text = _text(result)
        # Compact JSON: no space after colon in keys
        assert '"id":' in text

    async def test_compact_json_is_valid(self):
        """Compact JSON output should be valid parseable JSON."""
        from kaiten_mcp.server import COMPACT_JSON_THRESHOLD
        item_count = (COMPACT_JSON_THRESHOLD // 20) + 50
        large_data = [{"id": i, "val": "test"} for i in range(item_count)]
        handler = AsyncMock(return_value=large_data)
        with patch.dict(ALL_TOOLS, {
            "test_tool": {"handler": handler, "description": "t", "inputSchema": {"type": "object", "properties": {}}},
        }):
            result = await call_tool("test_tool", {})
        text = _text(result)
        parsed = json.loads(text)
        assert isinstance(parsed, list)
        assert len(parsed) == item_count


class TestFileBasedOutput:
    """Test file-based output for oversized responses."""

    async def test_file_output_when_configured(self):
        """When KAITEN_MCP_OUTPUT_DIR is set, oversized responses save to file."""
        from kaiten_mcp.server import FILE_OUTPUT_THRESHOLD
        # Create data large enough to exceed FILE_OUTPUT_THRESHOLD
        item_count = (FILE_OUTPUT_THRESHOLD // 30) + 100
        large_data = [{"id": i, "data": "x" * 20} for i in range(item_count)]
        handler = AsyncMock(return_value=large_data)
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(ALL_TOOLS, {
                "test_tool": {"handler": handler, "description": "t", "inputSchema": {"type": "object", "properties": {}}},
            }), patch.dict(os.environ, {"KAITEN_MCP_OUTPUT_DIR": tmpdir}):
                result = await call_tool("test_tool", {})
            text = _text(result)
            summary = json.loads(text)
            assert "saved_to" in summary
            assert summary["total_items"] == item_count
            assert os.path.exists(summary["saved_to"])
            # Verify saved file contains correct data
            with open(summary["saved_to"], "r") as f:
                saved_data = json.loads(f.read())
            assert len(saved_data) == item_count

    async def test_no_file_output_without_env(self):
        """Without KAITEN_MCP_OUTPUT_DIR, oversized responses are returned inline."""
        from kaiten_mcp.server import FILE_OUTPUT_THRESHOLD
        item_count = (FILE_OUTPUT_THRESHOLD // 30) + 100
        large_data = [{"id": i, "data": "x" * 20} for i in range(item_count)]
        handler = AsyncMock(return_value=large_data)
        env = os.environ.copy()
        env.pop("KAITEN_MCP_OUTPUT_DIR", None)
        with patch.dict(ALL_TOOLS, {
            "test_tool": {"handler": handler, "description": "t", "inputSchema": {"type": "object", "properties": {}}},
        }), patch.dict(os.environ, env, clear=True):
            result = await call_tool("test_tool", {})
        text = _text(result)
        # Should return the full data inline (compact JSON), not a file summary
        parsed = json.loads(text)
        assert isinstance(parsed, list)
        assert len(parsed) == item_count

    async def test_file_output_not_triggered_for_small_response(self):
        """Small responses should not trigger file output even with env set."""
        small_data = [{"id": 1}]
        handler = AsyncMock(return_value=small_data)
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(ALL_TOOLS, {
                "test_tool": {"handler": handler, "description": "t", "inputSchema": {"type": "object", "properties": {}}},
            }), patch.dict(os.environ, {"KAITEN_MCP_OUTPUT_DIR": tmpdir}):
                result = await call_tool("test_tool", {})
            text = _text(result)
            parsed = json.loads(text)
            # Small result should be returned directly, not as file summary
            assert isinstance(parsed, list)
            assert parsed == [{"id": 1}]
