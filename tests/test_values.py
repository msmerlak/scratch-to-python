"""Tests for value coercion and operator helpers."""

import math

from scratch2py.runtime import ops, values


def test_to_number():
    assert values.to_number("10") == 10
    assert values.to_number("3.5") == 3.5
    assert values.to_number("abc") == 0
    assert values.to_number("") == 0
    assert values.to_number(True) == 1


def test_to_string():
    assert values.to_string(10.0) == "10"
    assert values.to_string(3.5) == "3.5"
    assert values.to_string(True) == "true"
    assert values.to_string(None) == ""


def test_equals_numeric_and_string():
    assert values.equals("10", 10)
    assert values.equals("ABC", "abc")
    assert not values.equals("a", "b")


def test_comparisons():
    assert values.less_than("1", "2")
    assert values.greater_than("10", "2")  # numeric, not lexical


def test_to_boolean():
    assert values.to_boolean("true")
    assert values.to_boolean(1)
    assert not values.to_boolean("false")
    assert not values.to_boolean("")
    assert not values.to_boolean(0)


def test_ops_join_and_letter():
    assert ops.join("ab", "cd") == "abcd"
    assert ops.letter_of(1, "world") == "w"
    assert ops.letter_of(99, "world") == ""


def test_ops_mod_and_round():
    assert ops.mod(10, 3) == 1
    assert math.isnan(ops.mod(1, 0))
    assert ops.scratch_round(2.5) == 3
    assert ops.scratch_round(2.4) == 2


def test_ops_div_by_zero():
    assert ops.div(1, 0) == math.inf
    assert ops.div(-1, 0) == -math.inf
    assert math.isnan(ops.div(0, 0))


def test_ops_mathop():
    assert ops.mathop("abs", -5) == 5
    assert ops.mathop("sqrt", 9) == 3
    assert ops.mathop("floor", 2.9) == 2
