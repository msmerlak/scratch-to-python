"""Parse a Scratch ``project.json`` dict into the typed :mod:`model`."""

from __future__ import annotations

from typing import Any

from .model import (
    Block,
    Broadcast,
    Costume,
    Project,
    ScratchList,
    Sound,
    Target,
    Variable,
)


def _parse_variables(raw: dict[str, Any]) -> dict[str, Variable]:
    out: dict[str, Variable] = {}
    for var_id, entry in (raw or {}).items():
        # entry is [name, value] (cloud vars add a trailing flag we ignore).
        name, value = entry[0], entry[1]
        out[var_id] = Variable(id=var_id, name=name, value=value)
    return out


def _parse_lists(raw: dict[str, Any]) -> dict[str, ScratchList]:
    out: dict[str, ScratchList] = {}
    for list_id, entry in (raw or {}).items():
        name, values = entry[0], entry[1]
        out[list_id] = ScratchList(id=list_id, name=name, value=list(values))
    return out


def _parse_broadcasts(raw: dict[str, Any]) -> dict[str, Broadcast]:
    return {
        bid: Broadcast(id=bid, name=name) for bid, name in (raw or {}).items()
    }


def _parse_costumes(raw: list[dict[str, Any]]) -> list[Costume]:
    costumes: list[Costume] = []
    for c in raw or []:
        costumes.append(
            Costume(
                name=c.get("name", ""),
                asset_id=c.get("assetId", ""),
                md5ext=c.get("md5ext") or f"{c.get('assetId', '')}.{c.get('dataFormat', '')}",
                data_format=c.get("dataFormat", ""),
                rotation_center_x=c.get("rotationCenterX", 0.0),
                rotation_center_y=c.get("rotationCenterY", 0.0),
                bitmap_resolution=c.get("bitmapResolution", 1),
            )
        )
    return costumes


def _parse_sounds(raw: list[dict[str, Any]]) -> list[Sound]:
    sounds: list[Sound] = []
    for s in raw or []:
        sounds.append(
            Sound(
                name=s.get("name", ""),
                asset_id=s.get("assetId", ""),
                md5ext=s.get("md5ext") or f"{s.get('assetId', '')}.{s.get('dataFormat', '')}",
                data_format=s.get("dataFormat", ""),
                rate=s.get("rate"),
                sample_count=s.get("sampleCount"),
            )
        )
    return sounds


def _parse_blocks(raw: dict[str, Any]) -> dict[str, Block]:
    blocks: dict[str, Block] = {}
    for block_id, b in (raw or {}).items():
        # Some entries are "compressed" top-level primitives encoded as lists
        # (e.g. a free-floating variable reporter). Skip them here; the IR layer
        # decodes inline primitives directly from inputs.
        if isinstance(b, list):
            continue
        blocks[block_id] = Block(
            id=block_id,
            opcode=b.get("opcode", ""),
            next=b.get("next"),
            parent=b.get("parent"),
            inputs=b.get("inputs", {}) or {},
            fields=b.get("fields", {}) or {},
            shadow=bool(b.get("shadow", False)),
            top_level=bool(b.get("topLevel", False)),
            x=b.get("x"),
            y=b.get("y"),
            mutation=b.get("mutation"),
        )
    return blocks


def _parse_target(raw: dict[str, Any]) -> Target:
    is_stage = bool(raw.get("isStage", False))
    return Target(
        name=raw.get("name", ""),
        is_stage=is_stage,
        variables=_parse_variables(raw.get("variables", {})),
        lists=_parse_lists(raw.get("lists", {})),
        broadcasts=_parse_broadcasts(raw.get("broadcasts", {})),
        blocks=_parse_blocks(raw.get("blocks", {})),
        costumes=_parse_costumes(raw.get("costumes", [])),
        sounds=_parse_sounds(raw.get("sounds", [])),
        current_costume=raw.get("currentCostume", 0),
        volume=raw.get("volume", 100.0),
        layer_order=raw.get("layerOrder", 0),
        visible=raw.get("visible", True),
        x=raw.get("x", 0.0),
        y=raw.get("y", 0.0),
        size=raw.get("size", 100.0),
        direction=raw.get("direction", 90.0),
        draggable=raw.get("draggable", False),
        rotation_style=raw.get("rotationStyle", "all around"),
    )


def parse_project(project_json: dict[str, Any]) -> Project:
    """Convert a raw ``project.json`` dict into a :class:`Project`.

    Targets are ordered with the Stage first, then sprites sorted by their
    ``layerOrder`` so generated drawing order matches Scratch.
    """
    targets = [_parse_target(t) for t in project_json.get("targets", [])]
    targets.sort(key=lambda t: (not t.is_stage, t.layer_order))

    return Project(
        targets=targets,
        monitors=project_json.get("monitors", []),
        extensions=project_json.get("extensions", []),
        meta=project_json.get("meta", {}),
    )
