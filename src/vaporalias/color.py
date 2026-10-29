"""The one and only color helper. Cyan + magenta on black, neon-grid style.

Color is disabled when:
  * the NO_COLOR environment variable is set to a non-empty value
    (per no-color.org; an empty NO_COLOR is ignored), or
  * the target stream is not a TTY.
"""

from __future__ import annotations

import os
import sys
from typing import Optional, TextIO

RESET = "\033[0m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
ON_BLACK = "\033[40m"
BOLD = "\033[1m"
DIM = "\033[2m"


def color_enabled(stream: Optional[TextIO] = None, environ=None) -> bool:
    env = os.environ if environ is None else environ
    if env.get("NO_COLOR", ""):
        return False
    stream = sys.stdout if stream is None else stream
    isatty = getattr(stream, "isatty", None)
    try:
        return bool(isatty and isatty())
    except (ValueError, OSError):
        return False


class Palette:
    """Wraps text in ANSI codes, or passes it through untouched when disabled."""

    def __init__(self, enabled: bool):
        self.enabled = enabled

    @classmethod
    def for_stream(cls, stream: Optional[TextIO] = None, environ=None) -> "Palette":
        return cls(color_enabled(stream, environ))

    def _wrap(self, text: str, *codes: str) -> str:
        if not self.enabled:
            return text
        return "".join(codes) + ON_BLACK + text + RESET

    def cyan(self, text: str) -> str:
        return self._wrap(text, CYAN)

    def magenta(self, text: str) -> str:
        return self._wrap(text, MAGENTA)

    def title(self, text: str) -> str:
        return self._wrap(text, BOLD, MAGENTA)

    def dim(self, text: str) -> str:
        return self._wrap(text, DIM, CYAN)
