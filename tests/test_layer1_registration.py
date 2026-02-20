"""Layer 1 – Tool Registration & Discovery.

Verify that ALL 178 MCP tools are properly registered and discoverable.
"""
import asyncio
import inspect

import pytest

from kaiten_mcp.server import TOOL_MODULES, ALL_TOOLS, list_tools


class TestToolRegistration:
    """Verify structural correctness of the tool registry."""

    def test_all_modules_have_tools_dict(self):
        for mod in TOOL_MODULES:
            assert hasattr(mod, "TOOLS"), f"{mod.__name__} missing TOOLS"
            assert isinstance(mod.TOOLS, dict)

    def test_total_tool_count(self):
        assert len(ALL_TOOLS) == 222

    def test_no_duplicate_tool_names(self):
        names = []
        for mod in TOOL_MODULES:
            names.extend(mod.TOOLS.keys())
        assert len(names) == len(set(names)), (
            f"Duplicates: {[n for n in names if names.count(n) > 1]}"
        )

    def test_all_tool_names_prefixed_kaiten(self):
        for name in ALL_TOOLS:
            assert name.startswith("kaiten_"), f"{name} missing kaiten_ prefix"

    def test_all_tools_have_required_keys(self):
        for name, defn in ALL_TOOLS.items():
            assert "description" in defn, f"{name}: missing description"
            assert "inputSchema" in defn, f"{name}: missing inputSchema"
            assert "handler" in defn, f"{name}: missing handler"

    def test_all_descriptions_non_empty(self):
        for name, defn in ALL_TOOLS.items():
            assert defn["description"], f"{name}: empty description"

    def test_all_schemas_are_objects(self):
        for name, defn in ALL_TOOLS.items():
            schema = defn["inputSchema"]
            assert schema.get("type") == "object", (
                f"{name}: schema type is not object"
            )
            assert "properties" in schema, f"{name}: schema missing properties"

    def test_required_fields_exist_in_properties(self):
        for name, defn in ALL_TOOLS.items():
            schema = defn["inputSchema"]
            required = schema.get("required", [])
            props = schema.get("properties", {})
            for field in required:
                assert field in props, (
                    f"{name}: required field '{field}' not in properties"
                )

    def test_all_handlers_are_coroutines(self):
        for name, defn in ALL_TOOLS.items():
            assert asyncio.iscoroutinefunction(defn["handler"]), (
                f"{name}: handler is not async"
            )

    def test_all_handlers_have_two_params(self):
        for name, defn in ALL_TOOLS.items():
            sig = inspect.signature(defn["handler"])
            params = list(sig.parameters.keys())
            assert len(params) == 2, (
                f"{name}: expected 2 params, got {params}"
            )

    def test_property_types_are_valid(self):
        valid_types = {
            "string", "integer", "number", "boolean",
            "object", "array", "null",
        }
        for name, defn in ALL_TOOLS.items():
            for prop_name, prop in defn["inputSchema"].get("properties", {}).items():
                if "type" in prop:
                    t = prop["type"]
                    types = t if isinstance(t, list) else [t]
                    for tt in types:
                        assert tt in valid_types, (
                            f"{name}.{prop_name}: invalid type '{tt}'"
                        )

    def test_no_handler_shared_across_tools(self):
        handler_ids = [id(defn["handler"]) for defn in ALL_TOOLS.values()]
        assert len(handler_ids) == len(set(handler_ids)), (
            "Some tools share the same handler function"
        )

    async def test_list_tools_returns_all(self):
        tools = await list_tools()
        assert len(tools) == len(ALL_TOOLS)

    async def test_list_tools_tool_structure(self):
        tools = await list_tools()
        for tool in tools:
            assert tool.name
            assert tool.description
            assert tool.inputSchema

    def test_modules_count(self):
        assert len(TOOL_MODULES) == 27
