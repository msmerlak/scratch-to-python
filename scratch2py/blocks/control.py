"""Control blocks (loops, conditionals, waits, stop)."""

from __future__ import annotations

from . import statement


def _emit_loop_body(e, s, index: int) -> None:
    """Emit a C-block body followed by a frame ``yield`` (one per iteration)."""
    e.indent += 1
    body = s.substacks[index] if index < len(s.substacks) else []
    for child in body:
        e.emit_statement(child)
    e.emit("yield")
    e.indent -= 1


@statement("control_wait")
def wait(e, s):
    e.emit(f"yield from self.wait_seconds({e.num(s, 'DURATION', '1')})")


@statement("control_wait_until")
def wait_until(e, s):
    cond = e.inp(s, "CONDITION", "False")
    e.emit(f"yield from self.wait_until(lambda: to_boolean({cond}))")


@statement("control_repeat")
def repeat(e, s):
    e.emit(f"for _ in range(max(0, int(round(to_number({e.num(s, 'TIMES', '10')}))))):")
    _emit_loop_body(e, s, 0)


@statement("control_forever")
def forever(e, s):
    e.emit("while True:")
    _emit_loop_body(e, s, 0)


@statement("control_repeat_until")
def repeat_until(e, s):
    cond = e.inp(s, "CONDITION", "False")
    e.emit(f"while not to_boolean({cond}):")
    _emit_loop_body(e, s, 0)


@statement("control_if")
def if_(e, s):
    cond = e.inp(s, "CONDITION", "False")
    e.emit(f"if to_boolean({cond}):")
    e.emit_substack(s, 0)


@statement("control_if_else")
def if_else(e, s):
    cond = e.inp(s, "CONDITION", "False")
    e.emit(f"if to_boolean({cond}):")
    e.emit_substack(s, 0)
    e.emit("else:")
    e.emit_substack(s, 1)


@statement("control_stop")
def stop(e, s):
    option = e.field(s, "STOP_OPTION", "all")
    if option == "all":
        e.emit("self.engine.running = False")
        e.emit("return")
    elif option == "this script":
        e.emit("return")
    else:
        # "other scripts in sprite" is not modelled; treat as a no-op.
        e.emit("pass  # stop: 'other scripts' not supported")
