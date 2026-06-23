"""Looks blocks."""

from __future__ import annotations

from ..util import py_string
from . import expression, statement

EMPTY = "''"


@statement("looks_sayforsecs")
def say_for_secs(e, s):
    e.emit(f"yield from self.say_for_secs({e.inp(s, 'MESSAGE', EMPTY)}, {e.num(s, 'SECS', '2')})")


@statement("looks_say")
def say(e, s):
    e.emit(f"self.say({e.inp(s, 'MESSAGE', EMPTY)})")


@statement("looks_thinkforsecs")
def think_for_secs(e, s):
    e.emit(f"yield from self.think_for_secs({e.inp(s, 'MESSAGE', EMPTY)}, {e.num(s, 'SECS', '2')})")


@statement("looks_think")
def think(e, s):
    e.emit(f"self.think({e.inp(s, 'MESSAGE', EMPTY)})")


@statement("looks_switchcostumeto")
def switch_costume(e, s):
    e.emit(f"self.switch_costume({e.inp(s, 'COSTUME', EMPTY)})")


@statement("looks_nextcostume")
def next_costume(e, s):
    e.emit("self.next_costume()")


@statement("looks_switchbackdropto")
def switch_backdrop(e, s):
    e.emit(f"self.engine.stage.switch_backdrop({e.inp(s, 'BACKDROP', EMPTY)})")


@statement("looks_nextbackdrop")
def next_backdrop(e, s):
    e.emit("self.engine.stage.next_backdrop()")


@statement("looks_changesizeby")
def change_size_by(e, s):
    e.emit(f"self.change_size_by({e.num(s, 'CHANGE')})")


@statement("looks_setsizeto")
def set_size(e, s):
    e.emit(f"self.set_size({e.num(s, 'SIZE', '100')})")


@statement("looks_changeeffectby")
def change_effect(e, s):
    effect = e.field(s, "EFFECT", "ghost")
    e.emit(f"self.change_effect({py_string(effect)}, {e.num(s, 'CHANGE')})")


@statement("looks_seteffectto")
def set_effect(e, s):
    effect = e.field(s, "EFFECT", "ghost")
    e.emit(f"self.set_effect({py_string(effect)}, {e.num(s, 'VALUE')})")


@statement("looks_cleargraphiceffects")
def clear_effects(e, s):
    e.emit("self.clear_effects()")


@statement("looks_show")
def show(e, s):
    e.emit("self.show()")


@statement("looks_hide")
def hide(e, s):
    e.emit("self.hide()")


@statement("looks_gotofrontback")
def go_to_front_back(e, s):
    if e.field(s, "FRONT_BACK", "front") == "front":
        e.emit("self.go_to_front()")
    else:
        e.emit("self.go_to_back()")


@expression("looks_costumenumbername")
def costume_number_name(e, s):
    if e.field(s, "NUMBER_NAME", "number") == "number":
        return "self.costume_number()"
    return "self.costume_name()"


@expression("looks_backdropnumbername")
def backdrop_number_name(e, s):
    if e.field(s, "NUMBER_NAME", "number") == "number":
        return "self.engine.stage.backdrop_number()"
    return "self.engine.stage.backdrop_name()"


@expression("looks_size")
def size(e, s):
    return "self.size_value()"
