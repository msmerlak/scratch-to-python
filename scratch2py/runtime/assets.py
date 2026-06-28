"""Asset loading for generated projects: costumes (images) and sounds.

Costumes may be SVG or bitmap. SVGs are rasterized with ``cairosvg`` when it is
available; otherwise a labelled placeholder surface is used so the project still
runs. Sounds are loaded lazily through pygame's mixer.
"""

from __future__ import annotations

import io
import os

import pygame

try:  # Optional dependency: SVG rasterization.
    import cairosvg  # type: ignore

    _HAVE_CAIROSVG = True
except Exception:  # pragma: no cover - depends on system libs
    _HAVE_CAIROSVG = False


ASSETS_DIRNAME = "assets"


def _assets_dir() -> str:
    # Generated layout places assets next to engine/ at the project root.
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(here, ASSETS_DIRNAME)


def _placeholder(name: str) -> pygame.Surface:
    surf = pygame.Surface((64, 64), pygame.SRCALPHA)
    surf.fill((200, 200, 200, 255))
    pygame.draw.rect(surf, (120, 120, 120), surf.get_rect(), 2)
    return surf


def load_costume_image(md5ext: str, name: str = "") -> pygame.Surface:
    """Load a costume image by its ``md5ext`` filename, returning a Surface."""
    path = os.path.join(_assets_dir(), md5ext)
    if not os.path.exists(path):
        return _placeholder(name)

    if md5ext.lower().endswith(".svg"):
        return _load_svg(path, name)

    try:
        return pygame.image.load(path).convert_alpha()
    except Exception:
        return _placeholder(name)


def _load_svg(path: str, name: str) -> pygame.Surface:
    # Prefer cairosvg when available: it rasterizes Scratch SVGs faithfully.
    if _HAVE_CAIROSVG:
        try:
            png_bytes = cairosvg.svg2png(url=path)
            return pygame.image.load(io.BytesIO(png_bytes)).convert_alpha()
        except Exception:
            pass
    # Fall back to pygame's bundled SDL_image, which can load SVGs directly.
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception:
        return _placeholder(name)


def load_sound(md5ext: str) -> pygame.mixer.Sound | None:
    """Load a sound by its ``md5ext`` filename, or ``None`` if unavailable."""
    path = os.path.join(_assets_dir(), md5ext)
    if not os.path.exists(path):
        return None
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None
