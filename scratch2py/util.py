"""Small, dependency-free helpers shared by codegen and block handlers."""

from __future__ import annotations

import keyword
import re


def py_string(value) -> str:
    """Return a Python string literal for ``value``."""
    return repr(str(value))


def py_number(text) -> str:
    """Return a Python numeric literal for a Scratch number string, if possible."""
    s = str(text).strip()
    if re.fullmatch(r"[-+]?\d+", s):
        return s
    if re.fullmatch(r"[-+]?(\d+\.\d*|\.\d+|\d+)([eE][-+]?\d+)?", s):
        return s
    return py_string(text)


def safe_identifier(name: str, prefix: str = "m") -> str:
    """Turn an arbitrary Scratch name into a safe Python identifier fragment."""
    ident = re.sub(r"\W+", "_", name).strip("_").lower()
    if not ident:
        ident = prefix
    if ident[0].isdigit() or keyword.iskeyword(ident):
        ident = f"{prefix}_{ident}"
    return ident


def safe_class_name(name: str) -> str:
    cleaned = re.sub(r"\W+", " ", name).title().replace(" ", "")
    if not cleaned or cleaned[0].isdigit():
        cleaned = "T" + cleaned
    if keyword.iskeyword(cleaned):
        cleaned += "Target"
    return cleaned
