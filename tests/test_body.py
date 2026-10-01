"""Request body selection preserves falsy values and excludes routing metadata."""

import pytest

from kaiten_mcp.tools._body import _body_from


@pytest.mark.parametrize("value", [0, -1, False, "", [], {}])
def test_body_preserves_values_and_does_not_modify_arguments(value):
    args = {"setting": value, "optional": None, "board_id": 10, "unknown": "ignored"}
    original = args.copy()
    assert _body_from(args, ("setting", "optional", "absent")) == {"setting": value}
    assert args == original


def test_body_without_supported_values_is_empty():
    assert _body_from({"setting": None, "unknown": 1}, ("setting", "absent")) == {}
