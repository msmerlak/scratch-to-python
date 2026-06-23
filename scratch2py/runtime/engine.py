"""The pygame-based runtime engine for generated Scratch projects.

Scratch scripts are cooperative green-threads. Here, each running script is a
Python generator (a :class:`Thread`); the engine steps every thread once per
frame. Scripts relinquish control by ``yield``-ing (loops yield once per
iteration; waits yield until satisfied). Non-yielding scripts run to completion
the frame they start.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator

import pygame

STAGE_WIDTH = 480
STAGE_HEIGHT = 360
FPS = 30

# Map pygame key constants to Scratch key names for "when key pressed" hats.
_SPECIAL_KEYS = {
    pygame.K_SPACE: "space",
    pygame.K_UP: "up arrow",
    pygame.K_DOWN: "down arrow",
    pygame.K_LEFT: "left arrow",
    pygame.K_RIGHT: "right arrow",
    pygame.K_RETURN: "enter",
}


def key_name_from_event(event: pygame.event.Event) -> str | None:
    if event.key in _SPECIAL_KEYS:
        return _SPECIAL_KEYS[event.key]
    if event.unicode and event.unicode.isprintable() and event.unicode.strip():
        return event.unicode.lower()
    return None


class Thread:
    """A single running script, backed by a generator (or a finished no-op)."""

    def __init__(self, gen: Iterator | None) -> None:
        self.gen = gen
        self.done = gen is None

    def step(self) -> None:
        if self.done:
            return
        try:
            next(self.gen)  # type: ignore[arg-type]
        except StopIteration:
            self.done = True


class Engine:
    def __init__(self, title: str = "Scratch Project") -> None:
        self.title = title
        self.stage = None  # set by generated main
        self.sprites: list = []
        self.threads: list[Thread] = []

        # Hat registries: each maps a key to a list of (sprite, method).
        self._flag_hats: list[tuple[object, Callable]] = []
        self._key_hats: dict[str, list[tuple[object, Callable]]] = {}
        self._any_key_hats: list[tuple[object, Callable]] = []
        self._clicked_hats: list[tuple[object, Callable]] = []
        self._stage_clicked_hats: list[tuple[object, Callable]] = []
        self._broadcast_hats: dict[str, list[tuple[object, Callable]]] = {}

        self._start_time = time.monotonic()
        self._mouse_down = False
        self._mouse_pos = (0, 0)
        self.running = False

    # -- registration (called from generated sprite setup) --------------

    def add_target(self, target) -> None:
        target.engine = self
        if getattr(target, "is_stage", False):
            self.stage = target
        else:
            self.sprites.append(target)

    def on_flag(self, sprite, method) -> None:
        self._flag_hats.append((sprite, method))

    def on_key(self, key: str, sprite, method) -> None:
        if key == "any":
            self._any_key_hats.append((sprite, method))
        else:
            self._key_hats.setdefault(key, []).append((sprite, method))

    def on_clicked(self, sprite, method) -> None:
        self._clicked_hats.append((sprite, method))

    def on_stage_clicked(self, sprite, method) -> None:
        self._stage_clicked_hats.append((sprite, method))

    def on_broadcast(self, message: str, sprite, method) -> None:
        self._broadcast_hats.setdefault(message.lower(), []).append((sprite, method))

    # -- spawning -------------------------------------------------------

    def spawn(self, method) -> Thread:
        """Run a script method, returning a :class:`Thread` tracking it."""
        result = method()
        if hasattr(result, "__next__"):
            thread = Thread(result)
        else:
            thread = Thread(None)
        self.threads.append(thread)
        return thread

    def broadcast(self, message: str) -> list[Thread]:
        handlers = self._broadcast_hats.get(message.lower(), [])
        return [self.spawn(method) for _sprite, method in handlers]

    # -- timing / input accessors (used by sprites) ---------------------

    def timer(self) -> float:
        return time.monotonic() - self._start_time

    def reset_timer(self) -> None:
        self._start_time = time.monotonic()

    def mouse_down(self) -> bool:
        return self._mouse_down

    def mouse_position(self) -> tuple[float, float]:
        return self._mouse_pos

    def key_pressed(self, key: str) -> bool:
        pressed = pygame.key.get_pressed()
        if key == "space":
            return pressed[pygame.K_SPACE]
        if key == "up arrow":
            return pressed[pygame.K_UP]
        if key == "down arrow":
            return pressed[pygame.K_DOWN]
        if key == "left arrow":
            return pressed[pygame.K_LEFT]
        if key == "right arrow":
            return pressed[pygame.K_RIGHT]
        if key == "enter":
            return pressed[pygame.K_RETURN]
        if len(key) == 1:
            code = pygame.key.key_code(key) if key.isprintable() else None
            return bool(code and pressed[code])
        return False

    # -- main loop ------------------------------------------------------

    def run(self) -> None:
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception:  # pragma: no cover - headless/audio-less envs
            pass
        screen = pygame.display.set_mode((STAGE_WIDTH, STAGE_HEIGHT))
        pygame.display.set_caption(self.title)
        clock = pygame.time.Clock()

        # Let targets register their scripts now that the engine exists.
        for target in self._all_targets():
            if hasattr(target, "setup_scripts"):
                target.setup_scripts()

        self.running = True
        self._start_time = time.monotonic()
        for _sprite, method in self._flag_hats:
            self.spawn(method)

        while self.running:
            self._handle_events()
            self._step_threads()
            self._render(screen)
            clock.tick(FPS)

        pygame.quit()

    def _all_targets(self) -> list:
        targets: list = []
        if self.stage is not None:
            targets.append(self.stage)
        targets.extend(self.sprites)
        return targets

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                name = key_name_from_event(event)
                if name is not None:
                    for _sprite, method in self._key_hats.get(name, []):
                        self.spawn(method)
                for _sprite, method in self._any_key_hats:
                    self.spawn(method)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._mouse_down = True
                self._dispatch_click(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                self._mouse_down = False
            elif event.type == pygame.MOUSEMOTION:
                if self.stage is not None:
                    self._mouse_pos = self.stage.screen_to_scratch(*event.pos)

    def _dispatch_click(self, pos: tuple[int, int]) -> None:
        hit_sprite = False
        # Topmost sprite first.
        for sprite in reversed(self.sprites):
            if sprite.visible and sprite.contains_point(pos):
                for s, method in self._clicked_hats:
                    if s is sprite:
                        self.spawn(method)
                hit_sprite = True
                break
        if not hit_sprite:
            for _s, method in self._stage_clicked_hats:
                self.spawn(method)

    def _step_threads(self) -> None:
        for thread in list(self.threads):
            thread.step()
        self.threads = [t for t in self.threads if not t.done]

    def _render(self, screen: pygame.Surface) -> None:
        if self.stage is not None:
            self.stage.draw(screen)
        else:
            screen.fill((255, 255, 255))
        for sprite in self.sprites:
            sprite.draw(screen)
        pygame.display.flip()
