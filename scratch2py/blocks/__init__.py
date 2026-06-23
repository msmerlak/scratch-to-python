"""Opcode → code-generation handler registry.

Handlers are registered with the :func:`statement` and :func:`expression`
decorators and dispatched by :class:`scratch2py.codegen.Emitter`.

* A *statement* handler has signature ``(emitter, statement) -> None`` and emits
  one or more Python lines via ``emitter.emit`` / ``emitter.emit_substack``.
* An *expression* handler has signature ``(emitter, reporter) -> str`` and
  returns a Python expression string.
"""

from __future__ import annotations

from collections.abc import Callable

STATEMENT_HANDLERS: dict[str, Callable] = {}
EXPRESSION_HANDLERS: dict[str, Callable] = {}


def statement(*opcodes: str):
    def decorator(fn: Callable) -> Callable:
        for opcode in opcodes:
            STATEMENT_HANDLERS[opcode] = fn
        return fn

    return decorator


def expression(*opcodes: str):
    def decorator(fn: Callable) -> Callable:
        for opcode in opcodes:
            EXPRESSION_HANDLERS[opcode] = fn
        return fn

    return decorator


# Import handler modules for their registration side effects.
from . import (  # noqa: E402, F401
    control,
    events,
    looks,
    motion,
    operators,
    sensing,
    sound,
    variables,
)

__all__ = ["STATEMENT_HANDLERS", "EXPRESSION_HANDLERS", "statement", "expression"]
