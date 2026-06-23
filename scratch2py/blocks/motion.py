"""Motion blocks."""

from __future__ import annotations

from ..util import py_string
from . import expression, statement

EMPTY = "''"


@statement("motion_movesteps")
def move_steps(e, s):
    e.emit(f"self.move({e.num(s, 'STEPS')})")


@statement("motion_turnright")
def turn_right(e, s):
    e.emit(f"self.turn_right({e.num(s, 'DEGREES')})")


@statement("motion_turnleft")
def turn_left(e, s):
    e.emit(f"self.turn_left({e.num(s, 'DEGREES')})")


@statement("motion_pointindirection")
def point_in_direction(e, s):
    e.emit(f"self.point_in_direction({e.num(s, 'DIRECTION', '90')})")


@statement("motion_pointtowards")
def point_towards(e, s):
    e.emit(f"self.point_towards({e.inp(s, 'TOWARDS', EMPTY)})")


@statement("motion_gotoxy")
def goto_xy(e, s):
    e.emit(f"self.go_to_xy({e.num(s, 'X')}, {e.num(s, 'Y')})")


@statement("motion_goto")
def goto(e, s):
    e.emit(f"self.go_to({e.inp(s, 'TO', EMPTY)})")


@statement("motion_glidesecstoxy")
def glide_secs_to_xy(e, s):
    e.emit(
        f"yield from self.glide_to_xy({e.num(s, 'SECS', '1')}, "
        f"{e.num(s, 'X')}, {e.num(s, 'Y')})"
    )


@statement("motion_changexby")
def change_x_by(e, s):
    e.emit(f"self.change_x_by({e.num(s, 'DX')})")


@statement("motion_setx")
def set_x(e, s):
    e.emit(f"self.set_x({e.num(s, 'X')})")


@statement("motion_changeyby")
def change_y_by(e, s):
    e.emit(f"self.change_y_by({e.num(s, 'DY')})")


@statement("motion_sety")
def set_y(e, s):
    e.emit(f"self.set_y({e.num(s, 'Y')})")


@statement("motion_ifonedgebounce")
def if_on_edge_bounce(e, s):
    e.emit("self.if_on_edge_bounce()")


@statement("motion_setrotationstyle")
def set_rotation_style(e, s):
    style = e.field(s, "STYLE", "all around")
    e.emit(f"self.set_rotation_style({py_string(style)})")


@expression("motion_xposition")
def x_position(e, s):
    return "self.x_position()"


@expression("motion_yposition")
def y_position(e, s):
    return "self.y_position()"


@expression("motion_direction")
def direction(e, s):
    return "self.direction_value()"
