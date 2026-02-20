"""Root conftest — environment setup and shared fixtures."""

import os

import pytest

os.environ.setdefault("KAITEN_DOMAIN", "test-company")
os.environ.setdefault("KAITEN_TOKEN", "test-token-12345")


@pytest.fixture(scope="session")
def all_tool_modules():
    from kaiten_mcp.server import TOOL_MODULES

    return TOOL_MODULES


@pytest.fixture(scope="session")
def all_tools():
    from kaiten_mcp.server import ALL_TOOLS

    return ALL_TOOLS


@pytest.fixture(scope="session")
def tool_names(all_tools):
    return sorted(all_tools.keys())
