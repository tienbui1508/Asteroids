"""Best-effort fullscreen support (desktop + pygbag/web).

Browsers require fullscreen to be triggered by a user gesture (tap/click), so this
module should only be called from an input handler.
"""

from __future__ import annotations

import sys

import pygame


def is_web() -> bool:
    return sys.platform == "emscripten"


def toggle_fullscreen() -> None:
    """Toggle fullscreen when possible.

    - Web (pygbag): requests browser fullscreen on the canvas.
    - Desktop: uses pygame's toggle_fullscreen when available.
    """

    if is_web():
        try:
            # pygbag exposes the browser window via the stdlib `platform` module.
            from platform import window  # type: ignore

            doc = window.document
            if getattr(doc, "fullscreenElement", None):
                doc.exitFullscreen()
            else:
                window.canvas.requestFullscreen()
        except Exception:
            # Fullscreen may fail (permissions, missing API, etc.). Ignore safely.
            return
        return

    # Desktop fallback (not all SDL backends support it).
    try:
        pygame.display.toggle_fullscreen()
    except Exception:
        return
