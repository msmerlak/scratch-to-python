"""Shared variable and list operations for targets (Sprite and Stage).

Generated code addresses variables and lists by name. A name is resolved
against the target's own table first, then the Stage's (global) table. This
mirrors Scratch's local-then-global scoping for the common case.
"""

from __future__ import annotations

from typing import Any

from .values import equals, to_number, to_string


class TargetMixin:
    # These are defined on the concrete Sprite/Stage classes.
    variables: dict
    lists: dict
    engine: Any

    # -- variables ------------------------------------------------------

    def _var_table(self, name: str) -> dict:
        if name in self.variables:
            return self.variables
        stage = getattr(self.engine, "stage", None)
        if stage is not None and name in stage.variables:
            return stage.variables
        # Default new variables to the local table.
        return self.variables

    def var(self, name: str) -> Any:
        return self._var_table(name).get(name, 0)

    def set_var(self, name: str, value: Any) -> None:
        self._var_table(name)[name] = value

    def change_var(self, name: str, amount: Any) -> None:
        table = self._var_table(name)
        table[name] = to_number(table.get(name, 0)) + to_number(amount)

    # -- lists ----------------------------------------------------------

    def _list_table(self, name: str) -> list:
        if name in self.lists:
            return self.lists[name]
        stage = getattr(self.engine, "stage", None)
        if stage is not None and name in stage.lists:
            return stage.lists[name]
        self.lists[name] = []
        return self.lists[name]

    def list_add(self, name: str, value: Any) -> None:
        self._list_table(name).append(value)

    def list_delete(self, name: str, index: Any) -> None:
        lst = self._list_table(name)
        i = self._list_index(index, len(lst), allow_special=True)
        if i is not None and 0 <= i < len(lst):
            del lst[i]

    def list_delete_all(self, name: str) -> None:
        self._list_table(name).clear()

    def list_insert(self, name: str, value: Any, index: Any) -> None:
        lst = self._list_table(name)
        i = self._list_index(index, len(lst) + 1)
        if i is not None:
            lst.insert(i, value)

    def list_replace(self, name: str, index: Any, value: Any) -> None:
        lst = self._list_table(name)
        i = self._list_index(index, len(lst))
        if i is not None and 0 <= i < len(lst):
            lst[i] = value

    def list_item(self, name: str, index: Any) -> Any:
        lst = self._list_table(name)
        i = self._list_index(index, len(lst))
        if i is not None and 0 <= i < len(lst):
            return lst[i]
        return ""

    def list_item_index(self, name: str, value: Any) -> int:
        lst = self._list_table(name)
        for i, item in enumerate(lst):
            if equals(item, value):
                return i + 1
        return 0

    def list_length(self, name: str) -> int:
        return len(self._list_table(name))

    def list_contains(self, name: str, value: Any) -> bool:
        return any(equals(item, value) for item in self._list_table(name))

    def list_as_string(self, name: str) -> str:
        items = [to_string(x) for x in self._list_table(name)]
        # Scratch joins with no separator when all items are single chars.
        sep = "" if all(len(s) == 1 for s in items) else " "
        return sep.join(items)

    @staticmethod
    def _list_index(index: Any, length: int, allow_special: bool = True) -> int | None:
        if allow_special and isinstance(index, str):
            low = index.lower()
            if low == "last":
                return length - 1
            if low == "all":
                return None
            if low == "random":
                import random

                return random.randint(0, length - 1) if length else None
        try:
            return int(to_number(index)) - 1
        except (ValueError, TypeError):
            return None
