"""Compact response utilities for reducing payload size."""
from typing import Any

# Default limit for list operations
DEFAULT_LIMIT = 50

# Fields to simplify when compact=True (replace with {id, full_name})
SIMPLIFY_FIELDS = {"owner", "responsible", "author", "user", "created_by", "updated_by"}

# Fields containing user lists to simplify
SIMPLIFY_LIST_FIELDS = {"members", "responsibles", "owners", "subscribers", "participants"}

# Fields to strip entirely in compact mode (heavy text blobs)
STRIP_FIELDS = {"description"}


def _is_base64_avatar(value: Any) -> bool:
    """Check if a value is a base64 data URI (heavy avatar)."""
    return isinstance(value, str) and value.startswith("data:")


def _simplify_user(user: dict) -> dict:
    """Simplify user object to {id, full_name}."""
    if not isinstance(user, dict):
        return user
    result = {}
    if "id" in user:
        result["id"] = user["id"]
    if "full_name" in user:
        result["full_name"] = user["full_name"]
    elif "username" in user:
        result["full_name"] = user["username"]
    return result if result else user


def _compact_dict(data: dict) -> dict:
    """Apply compact transformation to a dictionary."""
    result = {}
    for key, value in data.items():
        # Strip heavy text fields
        if key in STRIP_FIELDS:
            continue
        # Skip base64 avatars
        if key == "avatar_url" and _is_base64_avatar(value):
            continue
        # Skip avatar field entirely if it's base64
        if key == "avatar" and isinstance(value, str) and value.startswith("data:"):
            continue

        # Simplify user objects
        if key in SIMPLIFY_FIELDS and isinstance(value, dict):
            result[key] = _simplify_user(value)
        # Simplify user lists
        elif key in SIMPLIFY_LIST_FIELDS and isinstance(value, list):
            result[key] = [
                _simplify_user(item) if isinstance(item, dict) else item
                for item in value
            ]
        # Recursively compact nested dicts
        elif isinstance(value, dict):
            result[key] = _compact_dict(value)
        # Recursively compact lists
        elif isinstance(value, list):
            result[key] = _compact_list(value)
        else:
            result[key] = value

    return result


def _compact_list(data: list) -> list:
    """Apply compact transformation to a list."""
    result = []
    for item in data:
        if isinstance(item, dict):
            result.append(_compact_dict(item))
        elif isinstance(item, list):
            result.append(_compact_list(item))
        else:
            result.append(item)
    return result


def compact_response(data: Any, compact: bool = False) -> Any:
    """
    Apply compact transformation to API response data.

    When compact=True:
    - Removes avatar_url fields that contain base64 data URIs
    - Simplifies user objects (owner, responsible, author, etc.) to {id, full_name}
    - Simplifies user lists (members, responsibles, etc.) to [{id, full_name}, ...]

    Args:
        data: API response data (dict, list, or primitive)
        compact: Whether to apply compact transformation

    Returns:
        Transformed data if compact=True, original data otherwise
    """
    if not compact:
        return data

    if isinstance(data, dict):
        return _compact_dict(data)
    elif isinstance(data, list):
        return _compact_list(data)
    else:
        return data


def select_fields(data: Any, fields_str: str | None) -> Any:
    """Keep only specified fields from each item in a list.

    Args:
        data: API response (list of dicts, or single dict)
        fields_str: Comma-separated field names, or None (no filtering)

    Returns:
        Filtered data with only requested fields
    """
    if not fields_str:
        return data

    keys = {f.strip() for f in fields_str.split(",")}

    if isinstance(data, list):
        return [{k: v for k, v in item.items() if k in keys} for item in data if isinstance(item, dict)]
    elif isinstance(data, dict):
        return {k: v for k, v in data.items() if k in keys}
    return data
