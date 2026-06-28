"""Generate readable Python source from the script IR.

The :class:`Emitter` walks IR statements and expressions, dispatching each
opcode to a handler registered in :mod:`scratch2py.blocks`. It produces:

* one method per script on the generated sprite/stage class, and
* a ``setup_scripts`` method that registers each script's hat with the engine.

Unsupported opcodes become commented no-ops plus an entry in the conversion
report, so generated projects always run.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import blocks
from .ir import (
    BroadcastLiteral,
    ListRef,
    Literal,
    Node,
    Reporter,
    Script,
    Statement,
    VarRef,
)
from .util import py_number, py_string, safe_class_name, safe_identifier

__all__ = [
    "Emitter",
    "ConversionReport",
    "py_string",
    "py_number",
    "safe_identifier",
    "safe_class_name",
    "generate_target_module",
    "generate_main",
    "project_title",
]


@dataclass
class Emitter:
    """Renders IR into Python source lines for a single target."""

    report: ConversionReport
    lines: list[str] = field(default_factory=list)
    indent: int = 0

    # -- output ---------------------------------------------------------

    def emit(self, text: str) -> None:
        self.lines.append("    " * self.indent + text if text else "")

    def emit_substack(self, stmt: Statement, index: int) -> None:
        self.indent += 1
        body = stmt.substacks[index] if index < len(stmt.substacks) else []
        if not body:
            self.emit("pass")
        else:
            for child in body:
                self.emit_statement(child)
        self.indent -= 1

    # -- statements -----------------------------------------------------

    def emit_statement(self, stmt: Statement) -> None:
        handler = blocks.STATEMENT_HANDLERS.get(stmt.opcode)
        if handler is None:
            self.report.unsupported(stmt.opcode)
            self.emit(f"# TODO unsupported block: {stmt.opcode}")
            return
        handler(self, stmt)

    # -- expressions ----------------------------------------------------

    def expr(self, node: Node | None) -> str:
        if node is None:
            return "''"
        if isinstance(node, Literal):
            if node.is_number:
                return py_number(node.value)
            return py_string(node.value)
        if isinstance(node, VarRef):
            return f"self.var({py_string(node.name)})"
        if isinstance(node, ListRef):
            return f"self.list_as_string({py_string(node.name)})"
        if isinstance(node, BroadcastLiteral):
            return py_string(node.name)
        if isinstance(node, Reporter):
            handler = blocks.EXPRESSION_HANDLERS.get(node.opcode)
            if handler is None:
                # Dropdown menu shadows carry their choice in a single field.
                if node.opcode.endswith("menu") and len(node.fields) == 1:
                    return py_string(next(iter(node.fields.values())))
                self.report.unsupported(node.opcode)
                return "''"
            return handler(self, node)
        return "''"

    # -- input/field helpers (used by handlers) -------------------------

    def inp(self, node, name: str, default: str = "0") -> str:
        value = node.inputs.get(name)
        if value is None:
            return default
        return self.expr(value)

    def num(self, node, name: str, default: str = "0") -> str:
        """Render an input wrapped so it is treated as a number."""
        value = node.inputs.get(name)
        if value is None:
            return default
        if isinstance(value, Literal) and value.is_number:
            return py_number(value.value)
        return f"to_number({self.expr(value)})"

    @staticmethod
    def field(node, name: str, default: str = "") -> str:
        return node.fields.get(name, default)


@dataclass
class ConversionReport:
    unsupported_opcodes: dict[str, int] = field(default_factory=dict)

    def unsupported(self, opcode: str) -> None:
        self.unsupported_opcodes[opcode] = self.unsupported_opcodes.get(opcode, 0) + 1

    def summary(self) -> str:
        if not self.unsupported_opcodes:
            return "All blocks converted."
        items = sorted(self.unsupported_opcodes.items(), key=lambda kv: (-kv[1], kv[0]))
        lines = ["Unsupported blocks (emitted as no-ops):"]
        lines += [f"  {op} x{count}" for op, count in items]
        return "\n".join(lines)


# Map a hat opcode to (registration-call template, method base name).
def hat_registration(emitter: Emitter, script: Script, method_name: str) -> str | None:
    """Return the engine registration call for a script's hat, or ``None``."""
    op = script.hat_opcode
    if op == "event_whenflagclicked":
        return f"self.engine.on_flag(self, self.{method_name})"
    if op == "event_whenkeypressed":
        key = script.hat_fields.get("KEY_OPTION", "space")
        return f"self.engine.on_key({py_string(key)}, self, self.{method_name})"
    if op == "event_whenthisspriteclicked":
        return f"self.engine.on_clicked(self, self.{method_name})"
    if op == "event_whenstageclicked":
        return f"self.engine.on_stage_clicked(self, self.{method_name})"
    if op == "event_whenbroadcastreceived":
        msg = script.hat_fields.get("BROADCAST_OPTION", "")
        return f"self.engine.on_broadcast({py_string(msg)}, self, self.{method_name})"
    return None


def hat_method_base(script: Script) -> str:
    op = script.hat_opcode
    if op == "event_whenflagclicked":
        return "flag"
    if op == "event_whenkeypressed":
        return "key_" + safe_identifier(script.hat_fields.get("KEY_OPTION", "space"))
    if op == "event_whenthisspriteclicked":
        return "clicked"
    if op == "event_whenstageclicked":
        return "stage_clicked"
    if op == "event_whenbroadcastreceived":
        return "broadcast_" + safe_identifier(script.hat_fields.get("BROADCAST_OPTION", "msg"))
    if op == "event_whenbackdropswitchesto":
        return "backdrop_switch"
    if op == "control_start_as_clone":
        return "clone_start"
    return "script"


# ---------------------------------------------------------------------------
# Module / file generation
# ---------------------------------------------------------------------------

_MODULE_HEADER = '''"""Auto-generated by scratch2py from Scratch target {name!r}. Do not edit."""

from engine import {base} as {base}Base
from engine import ops  # noqa: F401
from engine.values import (  # noqa: F401
    equals,
    greater_than,
    less_than,
    to_boolean,
    to_number,
    to_string,
)
'''


def _py_literal(value) -> str:
    if isinstance(value, bool):
        return repr(value)
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, list):
        return "[" + ", ".join(_py_literal(x) for x in value) + "]"
    return py_string(value)


def generate_target_module(report, target, scripts) -> str:
    """Render a full Python module (a Sprite or Stage subclass) for ``target``."""
    base = "Stage" if target.is_stage else "Sprite"
    class_name = safe_class_name(target.name)
    lines: list[str] = [_MODULE_HEADER.format(name=target.name, base=base), ""]
    lines.append(f"class {class_name}({base}Base):")

    # __init__
    lines.append("    def __init__(self):")
    lines.append(f"        super().__init__({py_string(target.name)})")
    if not target.is_stage:
        lines.append(f"        self.x = {float(target.x)!r}")
        lines.append(f"        self.y = {float(target.y)!r}")
        lines.append(f"        self.direction = {float(target.direction)!r}")
        lines.append(f"        self.size = {float(target.size)!r}")
        lines.append(f"        self.visible = {bool(target.visible)!r}")
        lines.append(f"        self.rotation_style = {py_string(target.rotation_style)}")
    lines.append(f"        self.volume = {float(target.volume)!r}")

    costumes = [(c.name, c.md5ext) for c in target.costumes]
    if target.is_stage:
        lines.append(f"        self.current_backdrop = {int(target.current_costume)}")
        lines.append(f"        self.backdrops = {costumes!r}")
    else:
        lines.append(f"        self.current_costume = {int(target.current_costume)}")
        lines.append(f"        self.costumes = {costumes!r}")
    sounds = [(s.name, s.md5ext) for s in target.sounds]
    lines.append(f"        self.sounds = {sounds!r}")

    var_items = {v.name: v.value for v in target.variables.values()}
    list_items = {lst.name: list(lst.value) for lst in target.lists.values()}
    lines.append(f"        self.variables = {_dict_literal(var_items)}")
    lines.append(f"        self.lists = {_dict_literal(list_items)}")
    lines.append("")

    # Assign deterministic method names.
    named: list[tuple[str, Script]] = []
    counts: dict[str, int] = {}
    for script in scripts:
        base_name = hat_method_base(script)
        counts[base_name] = counts.get(base_name, 0) + 1
        named.append((f"{base_name}_{counts[base_name]}", script))

    # setup_scripts
    lines.append("    def setup_scripts(self):")
    registrations = []
    for method_name, script in named:
        reg = hat_registration(Emitter(report=report), script, method_name)
        if reg is not None:
            registrations.append(f"        {reg}")
    if registrations:
        lines.extend(registrations)
    else:
        lines.append("        pass")
    lines.append("")

    # script methods
    for method_name, script in named:
        lines.append(f"    def {method_name}(self):")
        emitter = Emitter(report=report, indent=2)
        if not script.body:
            emitter.emit("pass")
        else:
            for stmt in script.body:
                emitter.emit_statement(stmt)
        lines.extend(emitter.lines)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _dict_literal(mapping: dict) -> str:
    if not mapping:
        return "{}"
    parts = [f"{py_string(k)}: {_py_literal(v)}" for k, v in mapping.items()]
    return "{" + ", ".join(parts) + "}"


def generate_main(project, modules) -> str:
    """Render the ``main.py`` entry point that wires targets into the engine.

    ``modules`` is a list of ``(module_name, class_name, is_stage)`` tuples in
    drawing order (Stage first).
    """
    lines = ['"""Auto-generated by scratch2py. Run with: python main.py"""', ""]
    lines.append("from engine import Engine")
    for module_name, class_name, _is_stage in modules:
        lines.append(f"from sprites.{module_name} import {class_name}")
    lines.append("")
    lines.append("")
    lines.append("def main():")
    lines.append(f"    engine = Engine({py_string(project_title(project))})")
    for _module_name, class_name, _is_stage in modules:
        lines.append(f"    engine.add_target({class_name}())")
    lines.append("    engine.run()")
    lines.append("")
    lines.append("")
    lines.append('if __name__ == "__main__":')
    lines.append("    main()")
    return "\n".join(lines) + "\n"


def project_title(project) -> str:
    return (project.meta or {}).get("title") or "Scratch Project"
