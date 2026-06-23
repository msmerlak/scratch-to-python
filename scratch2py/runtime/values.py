"""Scratch value-coercion semantics.

Scratch is loosely typed: values flow between number and string contexts with
specific rules. Centralizing those rules here keeps generated code readable.
"""

from __future__ import annotations

from typing import Any


def to_number(value: Any) -> float:
    """Coerce a value to a number the way Scratch does (non-numeric -> 0)."""
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if value is None:
        return 0.0
    s = str(value).strip()
    if s == "":
        return 0.0
    try:
        return float(s)
    except ValueError:
        # Scratch treats hex/inf/NaN leniently; for MVP, non-numeric -> 0.
        return 0.0


def to_string(value: Any) -> str:
    """Coerce a value to a string the way Scratch displays it."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        # Render integral floats without a trailing ``.0`` (Scratch style).
        if value.is_integer():
            return str(int(value))
        return repr(value)
    if value is None:
        return ""
    return str(value)


def to_boolean(value: Any) -> bool:
    """Coerce a value to a boolean the way Scratch does."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if value is None:
        return False
    s = str(value).strip().lower()
    return s not in ("", "false", "0")


def is_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    try:
        float(str(value).strip())
        return True
    except (ValueError, AttributeError):
        return False


def equals(a: Any, b: Any) -> bool:
    """Scratch ``=`` : numeric compare when both look numeric, else case-insensitive string."""
    if is_number(a) and is_number(b):
        return to_number(a) == to_number(b)
    return to_string(a).lower() == to_string(b).lower()


def less_than(a: Any, b: Any) -> bool:
    if is_number(a) and is_number(b):
        return to_number(a) < to_number(b)
    return to_string(a).lower() < to_string(b).lower()


def greater_than(a: Any, b: Any) -> bool:
    if is_number(a) and is_number(b):
        return to_number(a) > to_number(b)
    return to_string(a).lower() > to_string(b).lower()
