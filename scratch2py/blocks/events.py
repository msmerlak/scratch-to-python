"""Event blocks (the non-hat command blocks)."""

from __future__ import annotations

from . import statement

EMPTY = "''"


@statement("event_broadcast")
def broadcast(e, s):
    e.emit(f"self.broadcast({e.inp(s, 'BROADCAST_INPUT', EMPTY)})")


@statement("event_broadcastandwait")
def broadcast_and_wait(e, s):
    e.emit(f"yield from self.broadcast_and_wait({e.inp(s, 'BROADCAST_INPUT', EMPTY)})")
