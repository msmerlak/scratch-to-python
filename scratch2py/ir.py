"""Build an intermediate representation (IR) from a parsed target's block graph.

A Scratch target stores blocks as a flat dict keyed by id. Stacked blocks are
linked via ``next``; reporter blocks are plugged into ``inputs``; C-blocks hold
their bodies in ``SUBSTACK``/``SUBSTACK2`` inputs. This module turns that graph
into:

* :class:`Script` — a hat block plus an ordered list of body statements.
* :class:`Statement` — one stacked command, with nested substacks.
* expression nodes (:class:`Literal`, :class:`VarRef`, :class:`ListRef`,
  :class:`BroadcastLiteral`, :class:`Reporter`) for inputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .model import Block, Target

# Hat opcodes start a script. Mapped to a friendly handler kind in codegen.
HAT_OPCODES = {
    "event_whenflagclicked",
    "event_whenkeypressed",
    "event_whenthisspriteclicked",
    "event_whenstageclicked",
    "event_whenbroadcastreceived",
    "event_whenbackdropswitchesto",
    "event_whengreaterthan",
    "control_start_as_clone",
}


class Node:
    """Base class for all IR nodes."""


@dataclass
class Literal(Node):
    value: Any
    is_number: bool = False


@dataclass
class VarRef(Node):
    name: str


@dataclass
class ListRef(Node):
    name: str


@dataclass
class BroadcastLiteral(Node):
    name: str


@dataclass
class Reporter(Node):
    """A reporter/boolean block used as an expression."""

    opcode: str
    inputs: dict[str, Node] = field(default_factory=dict)
    fields: dict[str, str] = field(default_factory=dict)


@dataclass
class Statement(Node):
    """A stacked command block."""

    opcode: str
    inputs: dict[str, Node] = field(default_factory=dict)
    fields: dict[str, str] = field(default_factory=dict)
    # Bodies for C-blocks: index 0 == SUBSTACK, index 1 == SUBSTACK2.
    substacks: list[list[Statement]] = field(default_factory=list)


@dataclass
class Script(Node):
    hat_opcode: str
    hat_inputs: dict[str, Node]
    hat_fields: dict[str, str]
    body: list[Statement]


# Scratch input/primitive type codes (the first element of a primitive array).
_NUMBER_PRIMS = {4, 5, 6, 7, 8}
_COLOR_PRIM = 9
_STRING_PRIM = 10
_BROADCAST_PRIM = 11
_VAR_PRIM = 12
_LIST_PRIM = 13


class IRBuilder:
    def __init__(self, target: Target) -> None:
        self.target = target
        self.blocks = target.blocks

    # -- public API -----------------------------------------------------

    def build_scripts(self) -> list[Script]:
        """Return one :class:`Script` per hat block in the target."""
        scripts: list[Script] = []
        for block in self.blocks.values():
            if block.top_level and block.opcode in HAT_OPCODES:
                scripts.append(self._build_script(block))
        return scripts

    # -- helpers --------------------------------------------------------

    def _build_script(self, hat: Block) -> Script:
        body = self._build_sequence(hat.next)
        return Script(
            hat_opcode=hat.opcode,
            hat_inputs=self._resolve_inputs(hat),
            hat_fields=self._resolve_fields(hat),
            body=body,
        )

    def _build_sequence(self, start_id: str | None) -> list[Statement]:
        stmts: list[Statement] = []
        current = start_id
        while current is not None:
            block = self.blocks.get(current)
            if block is None:
                break
            stmts.append(self._build_statement(block))
            current = block.next
        return stmts

    def _build_statement(self, block: Block) -> Statement:
        inputs: dict[str, Node] = {}
        substacks: list[list[Statement]] = []

        # SUBSTACK / SUBSTACK2 are bodies, not expressions.
        for substack_name in ("SUBSTACK", "SUBSTACK2"):
            if substack_name in block.inputs:
                first_id = self._input_block_id(block.inputs[substack_name])
                substacks.append(self._build_sequence(first_id))

        for name, raw in block.inputs.items():
            if name in ("SUBSTACK", "SUBSTACK2"):
                continue
            inputs[name] = self._resolve_input(raw)

        return Statement(
            opcode=block.opcode,
            inputs=inputs,
            fields=self._resolve_fields(block),
            substacks=substacks,
        )

    def _resolve_inputs(self, block: Block) -> dict[str, Node]:
        return {name: self._resolve_input(raw) for name, raw in block.inputs.items()}

    @staticmethod
    def _resolve_fields(block: Block) -> dict[str, str]:
        # fields[name] == [value, id]; we keep the visible value.
        return {name: entry[0] for name, entry in block.fields.items()}

    @staticmethod
    def _input_block_id(raw: Any) -> str | None:
        """Return the referenced block id from an input array, if any."""
        if not isinstance(raw, list) or len(raw) < 2:
            return None
        candidate = raw[1]
        return candidate if isinstance(candidate, str) else None

    def _resolve_input(self, raw: Any) -> Node:
        """Resolve an input array into an IR expression node.

        Input arrays take the forms::

            [1, <primitive | blockId>]        # shadow only
            [2, <blockId>]                    # block, no shadow
            [3, <blockId>, <primitive>]       # block obscuring a shadow
        """
        if not isinstance(raw, list) or len(raw) < 2:
            return Literal("")

        value = raw[1]
        # A plugged-in reporter block is referenced by id (a string).
        if isinstance(value, str):
            block = self.blocks.get(value)
            if block is not None:
                return self._build_reporter(block)
            return Literal("")
        # Otherwise it is an inline primitive array.
        if isinstance(value, list):
            return self._resolve_primitive(value)
        return Literal("")

    @staticmethod
    def _resolve_primitive(prim: list[Any]) -> Node:
        prim_type = prim[0]
        if prim_type in _NUMBER_PRIMS:
            return Literal(prim[1], is_number=True)
        if prim_type in (_COLOR_PRIM, _STRING_PRIM):
            return Literal(prim[1])
        if prim_type == _BROADCAST_PRIM:
            return BroadcastLiteral(prim[1])
        if prim_type == _VAR_PRIM:
            return VarRef(prim[1])
        if prim_type == _LIST_PRIM:
            return ListRef(prim[1])
        return Literal("")

    def _build_reporter(self, block: Block) -> Reporter:
        return Reporter(
            opcode=block.opcode,
            inputs=self._resolve_inputs(block),
            fields=self._resolve_fields(block),
        )


def build_scripts(target: Target) -> list[Script]:
    """Convenience wrapper returning the scripts for ``target``."""
    return IRBuilder(target).build_scripts()
