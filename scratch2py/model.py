"""Data model for a parsed Scratch project.

These dataclasses are a thin, typed view over the structures found in a Scratch
``project.json``. They intentionally stay close to the raw format so the parser
stays simple; higher-level structure (scripts, expressions) is built in :mod:`ir`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Variable:
    id: str
    name: str
    value: Any


@dataclass
class ScratchList:
    id: str
    name: str
    value: list[Any]


@dataclass
class Broadcast:
    id: str
    name: str


@dataclass
class Costume:
    name: str
    asset_id: str
    md5ext: str
    data_format: str
    rotation_center_x: float = 0.0
    rotation_center_y: float = 0.0
    bitmap_resolution: int = 1


@dataclass
class Sound:
    name: str
    asset_id: str
    md5ext: str
    data_format: str
    rate: int | None = None
    sample_count: int | None = None


@dataclass
class Block:
    id: str
    opcode: str
    next: str | None = None
    parent: str | None = None
    # input name -> raw input array, e.g. [1, [4, "10"]] or [2, "blockId"]
    inputs: dict[str, Any] = field(default_factory=dict)
    # field name -> [value, id]
    fields: dict[str, Any] = field(default_factory=dict)
    shadow: bool = False
    top_level: bool = False
    x: float | None = None
    y: float | None = None
    # Present for shadow primitives that are encoded inline as a list rather than
    # a block reference (handled in the IR layer); kept generic here.
    mutation: dict[str, Any] | None = None


@dataclass
class Target:
    """A Scratch target: either the Stage or a Sprite."""

    name: str
    is_stage: bool
    variables: dict[str, Variable] = field(default_factory=dict)
    lists: dict[str, ScratchList] = field(default_factory=dict)
    broadcasts: dict[str, Broadcast] = field(default_factory=dict)
    blocks: dict[str, Block] = field(default_factory=dict)
    costumes: list[Costume] = field(default_factory=list)
    sounds: list[Sound] = field(default_factory=list)
    current_costume: int = 0
    volume: float = 100.0
    layer_order: int = 0

    # Sprite-only attributes (defaults are harmless for the Stage).
    visible: bool = True
    x: float = 0.0
    y: float = 0.0
    size: float = 100.0
    direction: float = 90.0
    draggable: bool = False
    rotation_style: str = "all around"


@dataclass
class Project:
    targets: list[Target] = field(default_factory=list)
    monitors: list[dict[str, Any]] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def stage(self) -> Target | None:
        for t in self.targets:
            if t.is_stage:
                return t
        return None

    @property
    def sprites(self) -> list[Target]:
        return [t for t in self.targets if not t.is_stage]
