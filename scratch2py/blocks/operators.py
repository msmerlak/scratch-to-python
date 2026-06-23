"""Operator blocks (all reporters/booleans)."""

from __future__ import annotations

from ..util import py_string
from . import expression

EMPTY = "''"


@expression("operator_add")
def add(e, s):
    return f"({e.num(s, 'NUM1')} + {e.num(s, 'NUM2')})"


@expression("operator_subtract")
def subtract(e, s):
    return f"({e.num(s, 'NUM1')} - {e.num(s, 'NUM2')})"


@expression("operator_multiply")
def multiply(e, s):
    return f"({e.num(s, 'NUM1')} * {e.num(s, 'NUM2')})"


@expression("operator_divide")
def divide(e, s):
    return f"ops.div({e.num(s, 'NUM1')}, {e.num(s, 'NUM2')})"


@expression("operator_random")
def random(e, s):
    return f"ops.pick_random({e.inp(s, 'FROM', '0')}, {e.inp(s, 'TO', '10')})"


@expression("operator_lt")
def lt(e, s):
    return f"less_than({e.inp(s, 'OPERAND1', EMPTY)}, {e.inp(s, 'OPERAND2', EMPTY)})"


@expression("operator_gt")
def gt(e, s):
    return f"greater_than({e.inp(s, 'OPERAND1', EMPTY)}, {e.inp(s, 'OPERAND2', EMPTY)})"


@expression("operator_equals")
def equals_op(e, s):
    return f"equals({e.inp(s, 'OPERAND1', EMPTY)}, {e.inp(s, 'OPERAND2', EMPTY)})"


@expression("operator_and")
def and_op(e, s):
    a = e.inp(s, "OPERAND1", "False")
    b = e.inp(s, "OPERAND2", "False")
    return f"(to_boolean({a}) and to_boolean({b}))"


@expression("operator_or")
def or_op(e, s):
    a = e.inp(s, "OPERAND1", "False")
    b = e.inp(s, "OPERAND2", "False")
    return f"(to_boolean({a}) or to_boolean({b}))"


@expression("operator_not")
def not_op(e, s):
    return f"(not to_boolean({e.inp(s, 'OPERAND', 'False')}))"


@expression("operator_join")
def join(e, s):
    return f"ops.join({e.inp(s, 'STRING1', EMPTY)}, {e.inp(s, 'STRING2', EMPTY)})"


@expression("operator_letter_of")
def letter_of(e, s):
    return f"ops.letter_of({e.inp(s, 'LETTER', '1')}, {e.inp(s, 'STRING', EMPTY)})"


@expression("operator_length")
def length(e, s):
    return f"ops.length_of({e.inp(s, 'STRING', EMPTY)})"


@expression("operator_contains")
def contains(e, s):
    return f"ops.contains({e.inp(s, 'STRING1', EMPTY)}, {e.inp(s, 'STRING2', EMPTY)})"


@expression("operator_mod")
def mod(e, s):
    return f"ops.mod({e.inp(s, 'NUM1', '0')}, {e.inp(s, 'NUM2', '0')})"


@expression("operator_round")
def round_op(e, s):
    return f"ops.scratch_round({e.num(s, 'NUM')})"


@expression("operator_mathop")
def mathop(e, s):
    operator = e.field(s, "OPERATOR", "abs")
    return f"ops.mathop({py_string(operator)}, {e.num(s, 'NUM')})"
