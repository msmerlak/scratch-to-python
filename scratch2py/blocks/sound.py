"""Sound blocks."""

from __future__ import annotations

from . import expression, statement

EMPTY = "''"


@statement("sound_play")
def play(e, s):
    e.emit(f"self.play_sound({e.inp(s, 'SOUND_MENU', EMPTY)})")


@statement("sound_playuntildone")
def play_until_done(e, s):
    e.emit(f"yield from self.play_sound_until_done({e.inp(s, 'SOUND_MENU', EMPTY)})")


@statement("sound_stopallsounds")
def stop_all(e, s):
    e.emit("self.stop_all_sounds()")


@statement("sound_setvolumeto")
def set_volume(e, s):
    e.emit(f"self.set_volume({e.num(s, 'VOLUME', '100')})")


@statement("sound_changevolumeby")
def change_volume(e, s):
    e.emit(f"self.change_volume({e.num(s, 'VOLUME')})")


@expression("sound_volume")
def volume(e, s):
    return "self.volume_value()"
