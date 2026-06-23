"""The Stage: backdrops, the coordinate system, and background rendering."""

from __future__ import annotations

import pygame

from . import assets
from .engine import STAGE_HEIGHT, STAGE_WIDTH
from .target import TargetMixin


class Stage(TargetMixin):
    """Base class for the generated Stage target.

    Scratch's stage is 480x360 with the origin at the centre and y pointing up.
    This class owns the conversion to pygame's top-left, y-down pixel space.
    """

    is_stage = True

    def __init__(self, name: str = "Stage") -> None:
        self.engine = None
        self.name = name
        # (name, md5ext) pairs, set by the generated subclass.
        self.backdrops: list[tuple[str, str]] = []
        self.current_backdrop = 0
        self.volume = 100.0
        self.variables: dict = {}
        self.lists: dict = {}
        self._image_cache: dict[str, pygame.Surface] = {}

    # -- coordinate mapping --------------------------------------------

    @staticmethod
    def scratch_to_screen(x: float, y: float) -> tuple[int, int]:
        return int(round(x + STAGE_WIDTH / 2)), int(round(STAGE_HEIGHT / 2 - y))

    @staticmethod
    def screen_to_scratch(px: float, py: float) -> tuple[float, float]:
        return px - STAGE_WIDTH / 2, STAGE_HEIGHT / 2 - py

    # -- backdrops ------------------------------------------------------

    def _backdrop_surface(self) -> pygame.Surface | None:
        if not self.backdrops:
            return None
        name, md5ext = self.backdrops[self.current_backdrop]
        if md5ext not in self._image_cache:
            self._image_cache[md5ext] = assets.load_costume_image(md5ext, name)
        return self._image_cache[md5ext]

    def backdrop_number(self) -> int:
        return self.current_backdrop + 1

    def backdrop_name(self) -> str:
        if not self.backdrops:
            return ""
        return self.backdrops[self.current_backdrop][0]

    def switch_backdrop(self, name) -> None:
        for index, (bname, _md5) in enumerate(self.backdrops):
            if bname == name:
                self.current_backdrop = index
                return
        # Allow switching by number.
        try:
            self.current_backdrop = (int(float(name)) - 1) % len(self.backdrops)
        except (ValueError, ZeroDivisionError):
            pass

    def next_backdrop(self) -> None:
        if self.backdrops:
            self.current_backdrop = (self.current_backdrop + 1) % len(self.backdrops)

    # -- rendering ------------------------------------------------------

    def draw(self, screen: pygame.Surface) -> None:
        surface = self._backdrop_surface()
        if surface is None:
            screen.fill((255, 255, 255))
            return
        scaled = pygame.transform.smoothscale(surface, (STAGE_WIDTH, STAGE_HEIGHT))
        screen.blit(scaled, (0, 0))

    def setup_scripts(self) -> None:  # overridden by generated subclass
        pass
