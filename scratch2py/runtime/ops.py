"""Operator helper functions used by generated expression code."""

from __future__ import annotations

import math
import random as _random

from .values import to_number, to_string


def pick_random(a, b):
    lo, hi = to_number(a), to_number(b)
    if lo > hi:
        lo, hi = hi, lo
    # If both bounds are integers, Scratch returns an integer.
    if float(lo).is_integer() and float(hi).is_integer():
        return _random.randint(int(lo), int(hi))
    return _random.uniform(lo, hi)


def div(a, b):
    divisor = to_number(b)
    numerator = to_number(a)
    if divisor == 0:
        if numerator == 0:
            return float("nan")
        return math.inf if numerator > 0 else -math.inf
    return numerator / divisor


def mod(a, b):
    divisor = to_number(b)
    if divisor == 0:
        return float("nan")
    return to_number(a) % divisor


def scratch_round(x):
    # Scratch rounds halves up (unlike Python's banker's rounding).
    return math.floor(to_number(x) + 0.5)


def join(a, b):
    return to_string(a) + to_string(b)


def letter_of(index, string):
    s = to_string(string)
    i = int(to_number(index))
    if 1 <= i <= len(s):
        return s[i - 1]
    return ""


def length_of(string):
    return len(to_string(string))


def contains(haystack, needle):
    return to_string(needle).lower() in to_string(haystack).lower()


def mathop(operator: str, x):
    n = to_number(x)
    op = operator.lower()
    if op == "abs":
        return abs(n)
    if op == "floor":
        return math.floor(n)
    if op == "ceiling":
        return math.ceil(n)
    if op == "sqrt":
        return math.sqrt(n) if n >= 0 else float("nan")
    if op == "sin":
        return round(math.sin(math.radians(n)), 10)
    if op == "cos":
        return round(math.cos(math.radians(n)), 10)
    if op == "tan":
        return round(math.tan(math.radians(n)), 10)
    if op == "asin":
        return math.degrees(math.asin(n))
    if op == "acos":
        return math.degrees(math.acos(n))
    if op == "atan":
        return math.degrees(math.atan(n))
    if op == "ln":
        return math.log(n) if n > 0 else float("nan")
    if op == "log":
        return math.log10(n) if n > 0 else float("nan")
    if op in ("e ^", "e^"):
        return math.exp(n)
    if op in ("10 ^", "10^"):
        return 10 ** n
    return n


def days_since_2000():
    import datetime

    epoch = datetime.datetime(2000, 1, 1)
    delta = datetime.datetime.now() - epoch
    return delta.total_seconds() / 86400.0


def current(unit: str):
    import datetime

    now = datetime.datetime.now()
    unit = unit.lower()
    if unit == "year":
        return now.year
    if unit == "month":
        return now.month
    if unit == "date":
        return now.day
    if unit == "dayofweek":
        return now.isoweekday() % 7 + 1
    if unit == "hour":
        return now.hour
    if unit == "minute":
        return now.minute
    if unit == "second":
        return now.second
    return 0
