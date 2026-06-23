"""Unpack a Scratch ``.sb3`` archive.

An ``.sb3`` file is a ZIP archive containing a ``project.json`` plus asset files
named by their md5 hash and extension (e.g. ``a1b2....svg``, ``c3d4....wav``).
"""

from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class UnpackedProject:
    """Raw contents of an unpacked ``.sb3`` archive."""

    project_json: dict[str, Any]
    # md5ext (filename) -> bytes
    assets: dict[str, bytes]


def unpack(sb3_path: str | Path) -> UnpackedProject:
    """Read a ``.sb3`` file and return its ``project.json`` and asset blobs."""
    sb3_path = Path(sb3_path)
    if not sb3_path.exists():
        raise FileNotFoundError(f"No such .sb3 file: {sb3_path}")

    with zipfile.ZipFile(sb3_path) as zf:
        names = set(zf.namelist())
        if "project.json" not in names:
            raise ValueError(f"{sb3_path} is not a valid .sb3 (missing project.json)")

        with zf.open("project.json") as fh:
            project_json = json.load(fh)

        assets: dict[str, bytes] = {}
        for name in names:
            if name == "project.json":
                continue
            # Skip directory entries.
            if name.endswith("/"):
                continue
            assets[name] = zf.read(name)

    return UnpackedProject(project_json=project_json, assets=assets)
