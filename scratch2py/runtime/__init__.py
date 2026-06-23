"""Runtime library vendored into every generated Scratch project.

Generated projects import this package as ``engine`` (a copy is placed at the
project root), so they run without installing ``scratch2py``.
"""

from .engine import Engine
from .sprite import Sprite
from .stage import Stage

__all__ = ["Engine", "Sprite", "Stage"]
