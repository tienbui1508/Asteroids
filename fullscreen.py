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
            fullscreen_el = getattr(doc, "fullscreenElement", None) or getattr(
                doc, "webkitFullscreenElement", None
            )
            if fullscreen_el:
                exit_fs = getattr(doc, "exitFullscreen", None) or getattr(
                    doc, "webkitExitFullscreen", None
                )
                if callable(exit_fs):
                    exit_fs()
                return

            # Try standard + iOS WebKit fullscreen entry points.
            targets = [
                getattr(window, "canvas", None),
                getattr(doc, "documentElement", None),
                getattr(doc, "body", None),
            ]
            for target in targets:
                if target is None:
                    continue
                req = getattr(target, "requestFullscreen", None) or getattr(
                    target, "webkitRequestFullscreen", None
                )
                if callable(req):
                    req()
                    return
        except Exception:
            # Fullscreen may fail (permissions, missing API, etc.). Ignore safely.
            return
        return

    # Desktop fallback (not all SDL backends support it).
    try:
        pygame.display.toggle_fullscreen()
    except Exception:
        return
