"""Variable and list blocks."""

from __future__ import annotations

from ..util import py_string
from . import expression, statement

EMPTY = "''"


# -- variables ----------------------------------------------------------


@statement("data_setvariableto")
def set_variable(e, s):
    name = py_string(e.field(s, "VARIABLE"))
    e.emit(f"self.set_var({name}, {e.inp(s, 'VALUE', EMPTY)})")


@statement("data_changevariableby")
def change_variable(e, s):
    name = py_string(e.field(s, "VARIABLE"))
    e.emit(f"self.change_var({name}, {e.num(s, 'VALUE')})")


@statement("data_showvariable", "data_hidevariable")
def show_hide_variable(e, s):
    # Variable monitors are not rendered; treat as a no-op.
    e.emit("pass  # variable monitor not supported")


@expression("data_variable")
def variable(e, s):
    return f"self.var({py_string(e.field(s, 'VARIABLE'))})"


# -- lists --------------------------------------------------------------


@statement("data_addtolist")
def add_to_list(e, s):
    name = py_string(e.field(s, "LIST"))
    e.emit(f"self.list_add({name}, {e.inp(s, 'ITEM', EMPTY)})")


@statement("data_deleteoflist")
def delete_of_list(e, s):
    name = py_string(e.field(s, "LIST"))
    e.emit(f"self.list_delete({name}, {e.inp(s, 'INDEX', '1')})")


@statement("data_deletealloflist")
def delete_all_of_list(e, s):
    e.emit(f"self.list_delete_all({py_string(e.field(s, 'LIST'))})")


@statement("data_insertatlist")
def insert_at_list(e, s):
    name = py_string(e.field(s, "LIST"))
    e.emit(f"self.list_insert({name}, {e.inp(s, 'ITEM', EMPTY)}, {e.inp(s, 'INDEX', '1')})")


@statement("data_replaceitemoflist")
def replace_item_of_list(e, s):
    name = py_string(e.field(s, "LIST"))
    e.emit(f"self.list_replace({name}, {e.inp(s, 'INDEX', '1')}, {e.inp(s, 'ITEM', EMPTY)})")


@statement("data_showlist", "data_hidelist")
def show_hide_list(e, s):
    e.emit("pass  # list monitor not supported")


@expression("data_itemoflist")
def item_of_list(e, s):
    name = py_string(e.field(s, "LIST"))
    return f"self.list_item({name}, {e.inp(s, 'INDEX', '1')})"


@expression("data_itemnumoflist")
def item_num_of_list(e, s):
    name = py_string(e.field(s, "LIST"))
    return f"self.list_item_index({name}, {e.inp(s, 'ITEM', EMPTY)})"


@expression("data_lengthoflist")
def length_of_list(e, s):
    return f"self.list_length({py_string(e.field(s, 'LIST'))})"


@expression("data_listcontainsitem")
def list_contains_item(e, s):
    name = py_string(e.field(s, "LIST"))
    return f"self.list_contains({name}, {e.inp(s, 'ITEM', EMPTY)})"
