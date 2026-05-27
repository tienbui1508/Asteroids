"""Global games-played counter (Supabase + local fallback)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.request import Request

from constants import (
    GAME_STATS_FILE,
    GAME_STATS_ROW_ID,
    SUPABASE_ANON_KEY,
    SUPABASE_STATS_TABLE,
    SUPABASE_URL,
)
from logger import log_event
from http_transport import request_json


def _supabase_enabled() -> bool:
    return bool(SUPABASE_URL and SUPABASE_ANON_KEY)


def _supabase_headers() -> dict[str, str]:
    # `apikey` is sufficient for anon access and avoids extra auth-header quirks in browser WASM.
    key = SUPABASE_ANON_KEY or ""
    return {
        "apikey": key,
        "Content-Type": "application/json",
    }


def _stats_table_url() -> str:
    base = (SUPABASE_URL or "").rstrip("/")
    return f"{base}/rest/v1/{SUPABASE_STATS_TABLE}"


def _supabase_fetch_games_played() -> int:
    url = (
        f"{_stats_table_url()}"
        f"?select=games_played"
        f"&id=eq.{GAME_STATS_ROW_ID}"
        f"&limit=1"
    )
    data = request_json(method="GET", url=url, headers=_supabase_headers())
    if not isinstance(data, list) or not data:
        return 0
    row = data[0]
    if not isinstance(row, dict):
        return 0
    count = row.get("games_played")
    if isinstance(count, int):
        return max(0, count)
    return 0


def _supabase_write_games_played(count: int) -> None:
    url = f"{_stats_table_url()}?on_conflict=id"
    headers = _supabase_headers()
    headers["Prefer"] = "resolution=merge-duplicates,return=minimal"
    request_json(
        method="POST",
        url=url,
        headers=headers,
        payload={"id": GAME_STATS_ROW_ID, "games_played": max(0, int(count))},
    )


def _load_local(path: Path) -> int:
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, dict):
            count = data.get("games_played")
            if isinstance(count, int):
                return max(0, count)
    except FileNotFoundError:
        return 0
    except Exception as e:
        log_event("game_stats_load_failed", error=str(e))
    return 0


def _save_local(path: Path, count: int) -> None:
    try:
        path.write_text(
            json.dumps({"games_played": max(0, int(count))}, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        log_event("game_stats_save_failed", error=str(e))


def load_games_played(path: Path) -> int:
    if _supabase_enabled():
        try:
            count = _supabase_fetch_games_played()
            log_event(
                "game_stats_supabase_load_ok",
                games_played=count,
                platform=sys.platform,
            )
            return count
        except Exception as e:
            log_event(
                "game_stats_supabase_load_failed",
                error=f"{type(e).__name__}: {e}",
                platform=sys.platform,
            )
    else:
        log_event("game_stats_supabase_disabled", platform=sys.platform)
    return _load_local(path)


def record_game_played(path: Path) -> int:
    count = load_games_played(path) + 1

    if _supabase_enabled():
        try:
            _supabase_write_games_played(count)
            log_event(
                "game_stats_supabase_save_ok",
                games_played=count,
                platform=sys.platform,
            )
            return count
        except Exception as e:
            log_event(
                "game_stats_supabase_save_failed",
                error=f"{type(e).__name__}: {e}",
                platform=sys.platform,
            )
    else:
        log_event("game_stats_supabase_disabled", games_played=count, platform=sys.platform)

    _save_local(path, count)
    return count
