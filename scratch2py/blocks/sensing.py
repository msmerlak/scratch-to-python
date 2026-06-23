"""Sensing blocks (basic subset)."""

from __future__ import annotations

from ..util import py_string
from . import expression, statement

EMPTY = "''"


@statement("sensing_resettimer")
def reset_timer(e, s):
    e.emit("self.reset_timer()")


@expression("sensing_touchingobject")
def touching_object(e, s):
    return f"self.touching({e.inp(s, 'TOUCHINGOBJECTMENU', EMPTY)})"


@expression("sensing_keypressed")
def key_pressed(e, s):
    return f"self.key_pressed({e.inp(s, 'KEY_OPTION', EMPTY)})"


@expression("sensing_mousedown")
def mouse_down(e, s):
    return "self.mouse_down()"


@expression("sensing_mousex")
def mouse_x(e, s):
    return "self.mouse_x()"


@expression("sensing_mousey")
def mouse_y(e, s):
    return "self.mouse_y()"


@expression("sensing_distanceto")
def distance_to(e, s):
    return f"self.distance_to({e.inp(s, 'DISTANCETOMENU', EMPTY)})"


@expression("sensing_timer")
def timer(e, s):
    return "self.timer()"


@expression("sensing_dayssince2000")
def days_since_2000(e, s):
    return "ops.days_since_2000()"


@expression("sensing_current")
def current(e, s):
    unit = e.field(s, "CURRENTMENU", "year")
    return f"ops.current({py_string(unit)})"
