"""Helpers to build synthetic Scratch projects for tests."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32">'
    '<rect width="32" height="32" fill="orange"/></svg>'
)


def smoke_project_json() -> dict:
    """A small but representative project: a stage and one scripted sprite."""
    return {
        "targets": [
            {
                "isStage": True,
                "name": "Stage",
                "variables": {"gid": ["score", 0]},
                "lists": {},
                "broadcasts": {"bid1": "go"},
                "blocks": {},
                "costumes": [
                    {"name": "backdrop1", "assetId": "bd1", "md5ext": "bd1.svg",
                     "dataFormat": "svg"}
                ],
                "sounds": [],
                "currentCostume": 0,
                "volume": 100,
                "layerOrder": 0,
            },
            {
                "isStage": False,
                "name": "Cat",
                "variables": {"lv": ["steps", 0]},
                "lists": {"ll": ["trail", []]},
                "broadcasts": {},
                "blocks": {
                    "hat": {
                        "opcode": "event_whenflagclicked", "next": "b1", "parent": None,
                        "inputs": {}, "fields": {}, "shadow": False, "topLevel": True,
                        "x": 0, "y": 0,
                    },
                    "b1": {
                        "opcode": "motion_gotoxy", "next": "b2", "parent": "hat",
                        "inputs": {"X": [1, [4, "0"]], "Y": [1, [4, "0"]]},
                        "fields": {}, "shadow": False, "topLevel": False,
                    },
                    "b2": {
                        "opcode": "control_repeat", "next": "b5", "parent": "b1",
                        "inputs": {"TIMES": [1, [7, "5"]], "SUBSTACK": [2, "b3"]},
                        "fields": {}, "shadow": False, "topLevel": False,
                    },
                    "b3": {
                        "opcode": "motion_movesteps", "next": "b4", "parent": "b2",
                        "inputs": {"STEPS": [1, [4, "10"]]},
                        "fields": {}, "shadow": False, "topLevel": False,
                    },
                    "b4": {
                        "opcode": "data_changevariableby", "next": None, "parent": "b3",
                        "inputs": {"VALUE": [1, [4, "1"]]},
                        "fields": {"VARIABLE": ["steps", "lv"]},
                        "shadow": False, "topLevel": False,
                    },
                    "b5": {
                        "opcode": "looks_say", "next": None, "parent": "b2",
                        "inputs": {"MESSAGE": [1, [10, "done"]]},
                        "fields": {}, "shadow": False, "topLevel": False,
                    },
                },
                "costumes": [
                    {"name": "costume1", "assetId": "c1", "md5ext": "c1.svg",
                     "dataFormat": "svg"}
                ],
                "sounds": [],
                "currentCostume": 0, "volume": 100, "layerOrder": 1,
                "visible": True, "x": 0, "y": 0, "size": 100, "direction": 90,
                "draggable": False, "rotationStyle": "all around",
            },
        ],
        "monitors": [],
        "extensions": [],
        "meta": {"semver": "3.0.0", "title": "Smoke Test"},
    }


def write_smoke_sb3(path: Path) -> Path:
    project = smoke_project_json()
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("project.json", json.dumps(project))
        zf.writestr("c1.svg", _SVG)
        zf.writestr("bd1.svg", _SVG)
    return path
