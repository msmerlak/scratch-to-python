"""The Sprite base class: motion, looks, sound, and sensing behaviours.

Generated per-sprite modules subclass :class:`Sprite`, populate costume/sound
tables, and define script methods that call these helpers. Methods that take
time (waits, glides, "for N seconds" blocks) are generators and are driven by
the engine's cooperative scheduler.
"""

from __future__ import annotations

import math
import time
from collections.abc import Iterator

import pygame

from . import assets
from .target import TargetMixin
from .values import to_number, to_string


class Sprite(TargetMixin):
    is_stage = False

    def __init__(self, name: str = "Sprite") -> None:
        self.engine = None
        self.name = name

        # State (overridden by generated subclass __init__).
        self.x = 0.0
        self.y = 0.0
        self.direction = 90.0
        self.size = 100.0
        self.visible = True
        self.rotation_style = "all around"
        self.volume = 100.0

        # Costumes/sounds as (name, md5ext) pairs.
        self.costumes: list[tuple[str, str]] = []
        self.current_costume = 0
        self.sounds: list[tuple[str, str]] = []

        # Graphic effects (only "ghost" is rendered, as alpha).
        self.effects: dict[str, float] = {}

        # Speech bubble: (text, kind) or None.
        self._bubble: tuple[str, str] | None = None

        self.variables: dict = {}
        self.lists: dict = {}

        self._image_cache: dict[str, pygame.Surface] = {}
        self._sound_cache: dict[str, object] = {}

    # -- registration hook ---------------------------------------------

    def setup_scripts(self) -> None:  # overridden by generated subclass
        pass

    # -- motion ---------------------------------------------------------

    def move(self, steps) -> None:
        rad = math.radians(self.direction)
        self.x += to_number(steps) * math.sin(rad)
        self.y += to_number(steps) * math.cos(rad)

    def turn_right(self, degrees) -> None:
        self.direction = self._wrap_direction(self.direction + to_number(degrees))

    def turn_left(self, degrees) -> None:
        self.direction = self._wrap_direction(self.direction - to_number(degrees))

    def point_in_direction(self, direction) -> None:
        self.direction = self._wrap_direction(to_number(direction))

    def point_towards_xy(self, x, y) -> None:
        dx = to_number(x) - self.x
        dy = to_number(y) - self.y
        self.direction = self._wrap_direction(90 - math.degrees(math.atan2(dy, dx)))

    def point_towards(self, target: str) -> None:
        tx, ty = self._target_xy(target)
        self.point_towards_xy(tx, ty)

    def go_to_xy(self, x, y) -> None:
        self.x = to_number(x)
        self.y = to_number(y)

    def go_to(self, target: str) -> None:
        tx, ty = self._target_xy(target)
        self.x, self.y = tx, ty

    def change_x_by(self, dx) -> None:
        self.x += to_number(dx)

    def set_x(self, x) -> None:
        self.x = to_number(x)

    def change_y_by(self, dy) -> None:
        self.y += to_number(dy)

    def set_y(self, y) -> None:
        self.y = to_number(y)

    def if_on_edge_bounce(self) -> None:
        half_w, half_h = 240, 180
        if self.x > half_w:
            self.x = half_w
            self.direction = self._wrap_direction(-self.direction)
        elif self.x < -half_w:
            self.x = -half_w
            self.direction = self._wrap_direction(-self.direction)
        if self.y > half_h:
            self.y = half_h
            self.direction = self._wrap_direction(180 - self.direction)
        elif self.y < -half_h:
            self.y = -half_h
            self.direction = self._wrap_direction(180 - self.direction)

    def set_rotation_style(self, style: str) -> None:
        self.rotation_style = style

    def glide_to_xy(self, secs, x, y) -> Iterator:
        duration = to_number(secs)
        start_x, start_y = self.x, self.y
        end_x, end_y = to_number(x), to_number(y)
        if duration <= 0:
            self.x, self.y = end_x, end_y
            return
        start_t = time.monotonic()
        while True:
            t = (time.monotonic() - start_t) / duration
            if t >= 1:
                break
            self.x = start_x + (end_x - start_x) * t
            self.y = start_y + (end_y - start_y) * t
            yield
        self.x, self.y = end_x, end_y

    def x_position(self) -> float:
        return self.x

    def y_position(self) -> float:
        return self.y

    def direction_value(self) -> float:
        return self.direction

    # -- looks ----------------------------------------------------------

    def say(self, message) -> None:
        text = to_string(message)
        self._bubble = (text, "say") if text else None

    def think(self, message) -> None:
        text = to_string(message)
        self._bubble = (text, "think") if text else None

    def say_for_secs(self, message, secs) -> Iterator:
        self.say(message)
        yield from self.wait_seconds(secs)
        self._bubble = None

    def think_for_secs(self, message, secs) -> Iterator:
        self.think(message)
        yield from self.wait_seconds(secs)
        self._bubble = None

    def switch_costume(self, name) -> None:
        for index, (cname, _md5) in enumerate(self.costumes):
            if cname == name:
                self.current_costume = index
                return
        try:
            self.current_costume = (int(to_number(name)) - 1) % len(self.costumes)
        except (ValueError, ZeroDivisionError):
            pass

    def next_costume(self) -> None:
        if self.costumes:
            self.current_costume = (self.current_costume + 1) % len(self.costumes)

    def costume_number(self) -> int:
        return self.current_costume + 1

    def costume_name(self) -> str:
        if not self.costumes:
            return ""
        return self.costumes[self.current_costume][0]

    def change_size_by(self, amount) -> None:
        self.size += to_number(amount)

    def set_size(self, percent) -> None:
        self.size = to_number(percent)

    def set_effect(self, effect: str, value) -> None:
        self.effects[effect.lower()] = to_number(value)

    def change_effect(self, effect: str, value) -> None:
        key = effect.lower()
        self.effects[key] = self.effects.get(key, 0.0) + to_number(value)

    def clear_effects(self) -> None:
        self.effects.clear()

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    def go_to_front(self) -> None:
        if self.engine and self in self.engine.sprites:
            self.engine.sprites.remove(self)
            self.engine.sprites.append(self)

    def go_to_back(self) -> None:
        if self.engine and self in self.engine.sprites:
            self.engine.sprites.remove(self)
            self.engine.sprites.insert(0, self)

    def size_value(self) -> float:
        return self.size

    # -- sound ----------------------------------------------------------

    def _get_sound(self, name):
        for sname, md5ext in self.sounds:
            if sname == name:
                if md5ext not in self._sound_cache:
                    self._sound_cache[md5ext] = assets.load_sound(md5ext)
                return self._sound_cache[md5ext]
        return None

    def play_sound(self, name) -> None:
        sound = self._get_sound(name)
        if sound is not None:
            sound.set_volume(max(0.0, min(1.0, self.volume / 100.0)))
            sound.play()

    def play_sound_until_done(self, name) -> Iterator:
        sound = self._get_sound(name)
        if sound is None:
            return
        sound.set_volume(max(0.0, min(1.0, self.volume / 100.0)))
        channel = sound.play()
        if channel is None:
            return
        while channel.get_busy():
            yield

    def stop_all_sounds(self) -> None:
        try:
            pygame.mixer.stop()
        except Exception:
            pass

    def set_volume(self, percent) -> None:
        self.volume = max(0.0, min(100.0, to_number(percent)))

    def change_volume(self, amount) -> None:
        self.set_volume(self.volume + to_number(amount))

    def volume_value(self) -> float:
        return self.volume

    # -- control (timing) ----------------------------------------------

    def wait_seconds(self, secs) -> Iterator:
        duration = to_number(secs)
        start = time.monotonic()
        while time.monotonic() - start < duration:
            yield

    def wait_until(self, predicate) -> Iterator:
        while not predicate():
            yield

    # -- events ---------------------------------------------------------

    def broadcast(self, message) -> None:
        if self.engine:
            self.engine.broadcast(to_string(message))

    def broadcast_and_wait(self, message) -> Iterator:
        if not self.engine:
            return
        threads = self.engine.broadcast(to_string(message))
        while any(not t.done for t in threads):
            yield

    # -- sensing --------------------------------------------------------

    def touching(self, target: str) -> bool:
        if target == "_edge_":
            return (
                abs(self.x) >= 240 or abs(self.y) >= 180
            )
        if target == "_mouse_":
            return self.contains_point(self._screen_mouse())
        other = self._find_sprite(target)
        if other is None or not other.visible:
            return False
        return self._rect().colliderect(other._rect())

    def key_pressed(self, key: str) -> bool:
        return bool(self.engine and self.engine.key_pressed(key))

    def mouse_down(self) -> bool:
        return bool(self.engine and self.engine.mouse_down())

    def mouse_x(self) -> float:
        if self.engine:
            return self.engine.mouse_position()[0]
        return 0.0

    def mouse_y(self) -> float:
        if self.engine:
            return self.engine.mouse_position()[1]
        return 0.0

    def distance_to(self, target: str) -> float:
        tx, ty = self._target_xy(target)
        return math.hypot(tx - self.x, ty - self.y)

    def timer(self) -> float:
        return self.engine.timer() if self.engine else 0.0

    def reset_timer(self) -> None:
        if self.engine:
            self.engine.reset_timer()

    # -- rendering helpers ----------------------------------------------

    def _costume_surface(self) -> pygame.Surface | None:
        if not self.costumes:
            return None
        name, md5ext = self.costumes[self.current_costume]
        if md5ext not in self._image_cache:
            self._image_cache[md5ext] = assets.load_costume_image(md5ext, name)
        return self._image_cache[md5ext]

    def _rendered_surface(self) -> pygame.Surface | None:
        surface = self._costume_surface()
        if surface is None:
            return None
        scale = max(0.0, self.size / 100.0)
        if scale != 1.0:
            w = max(1, int(surface.get_width() * scale))
            h = max(1, int(surface.get_height() * scale))
            surface = pygame.transform.smoothscale(surface, (w, h))

        if self.rotation_style == "all around":
            surface = pygame.transform.rotate(surface, 90 - self.direction)
        elif self.rotation_style == "left-right":
            if 180 < self.direction <= 360 or self.direction < 0:
                surface = pygame.transform.flip(surface, True, False)

        ghost = self.effects.get("ghost", 0.0)
        if ghost:
            alpha = int(max(0.0, min(1.0, 1 - ghost / 100.0)) * 255)
            surface = surface.copy()
            surface.set_alpha(alpha)
        return surface

    def draw(self, screen: pygame.Surface) -> None:
        if not self.visible:
            return
        surface = self._rendered_surface()
        if surface is None:
            return
        from .stage import Stage

        cx, cy = Stage.scratch_to_screen(self.x, self.y)
        rect = surface.get_rect(center=(cx, cy))
        screen.blit(surface, rect)
        if self._bubble is not None:
            self._draw_bubble(screen, rect)

    def _draw_bubble(self, screen: pygame.Surface, sprite_rect: pygame.Rect) -> None:
        text, _kind = self._bubble
        font = pygame.font.Font(None, 22)
        label = font.render(text, True, (0, 0, 0))
        padding = 6
        box = pygame.Rect(0, 0, label.get_width() + 2 * padding, label.get_height() + 2 * padding)
        box.bottomleft = (sprite_rect.right, sprite_rect.top)
        box.clamp_ip(screen.get_rect())
        pygame.draw.rect(screen, (255, 255, 255), box, border_radius=8)
        pygame.draw.rect(screen, (160, 160, 160), box, 1, border_radius=8)
        screen.blit(label, (box.x + padding, box.y + padding))

    def _rect(self) -> pygame.Rect:
        surface = self._rendered_surface()
        from .stage import Stage

        cx, cy = Stage.scratch_to_screen(self.x, self.y)
        if surface is None:
            return pygame.Rect(cx - 1, cy - 1, 2, 2)
        return surface.get_rect(center=(cx, cy))

    def contains_point(self, screen_pos: tuple[int, int]) -> bool:
        return self._rect().collidepoint(screen_pos)

    # -- internal lookups ----------------------------------------------

    def _wrap_direction(self, d: float) -> float:
        # Scratch keeps direction in (-180, 180].
        d = (d + 180) % 360 - 180
        return 180.0 if d == -180 else d

    def _find_sprite(self, name: str):
        if not self.engine:
            return None
        for sprite in self.engine.sprites:
            if sprite.name == name:
                return sprite
        return None

    def _screen_mouse(self) -> tuple[int, int]:
        from .stage import Stage

        if self.engine:
            mx, my = self.engine.mouse_position()
            return Stage.scratch_to_screen(mx, my)
        return (0, 0)

    def _target_xy(self, target: str) -> tuple[float, float]:
        if target == "_mouse_":
            if self.engine:
                return self.engine.mouse_position()
            return (0.0, 0.0)
        if target == "_random_":
            import random

            return (random.uniform(-240, 240), random.uniform(-180, 180))
        other = self._find_sprite(target)
        if other is not None:
            return (other.x, other.y)
        return (self.x, self.y)
