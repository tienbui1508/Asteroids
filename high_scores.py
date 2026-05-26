from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from typing import TypedDict

from logger import log_event

from constants import (
    HIGH_SCORES_DISPLAY_ENTRIES,
    HIGH_SCORES_FILE,
    HIGH_SCORES_MAX_ENTRIES,
    SUPABASE_ANON_KEY,
    SUPABASE_HIGH_SCORES_TABLE,
    SUPABASE_URL,
)


class HighScoreEntry(TypedDict):
    name: str
    score: int


@dataclass
class HighScores:
    entries: list[HighScoreEntry]

    def top(self) -> list[HighScoreEntry]:
        return self.entries[:HIGH_SCORES_DISPLAY_ENTRIES]

    def trimmed(self) -> "HighScores":
        self.entries.sort(key=lambda e: (e["score"], e["name"]), reverse=True)
        self.entries = self.entries[:HIGH_SCORES_MAX_ENTRIES]
        return self


def _safe_parse_entries(raw: object) -> list[HighScoreEntry]:
    if not isinstance(raw, list):
        return []

    entries: list[HighScoreEntry] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        score = item.get("score")
        if not isinstance(name, str):
            continue
        if not isinstance(score, int):
            continue
        entries.append({"name": name, "score": score})
    return entries


def _supabase_enabled() -> bool:
    return bool(SUPABASE_URL and SUPABASE_ANON_KEY)


def _supabase_headers() -> dict[str, str]:
    # Supabase REST requires both `apikey` and `Authorization`.
    key = SUPABASE_ANON_KEY or ""
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def _supabase_fetch_top_scores(limit: int) -> HighScores:
    base = (SUPABASE_URL or "").rstrip("/")
    table = SUPABASE_HIGH_SCORES_TABLE
    url = (
        f"{base}/rest/v1/{table}"
        f"?select=name,score"
        f"&order=score.desc"
        f"&order=created_at.desc"
        f"&limit={int(limit)}"
    )

    req = Request(url, headers=_supabase_headers(), method="GET")
    with urlopen(req, timeout=3) as resp:
        raw = resp.read().decode("utf-8")
    data = json.loads(raw)
    return HighScores(entries=_safe_parse_entries(data)).trimmed()


def _supabase_insert_score(*, player_name: str, score: int) -> None:
    base = (SUPABASE_URL or "").rstrip("/")
    table = SUPABASE_HIGH_SCORES_TABLE
    url = f"{base}/rest/v1/{table}"

    payload = json.dumps({"name": player_name, "score": score}).encode("utf-8")
    headers = _supabase_headers()
    # Ask Supabase to return the inserted row (not required, but useful when debugging).
    headers["Prefer"] = "return=minimal"

    req = Request(url, data=payload, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=5):
            pass
    except HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")
        except Exception:
            body = ""
        raise HTTPError(
            e.url,
            e.code,
            f"{e.reason} body={body}",
            e.headers,
            e.fp,
        ) from e


def load_high_scores(path: Path) -> HighScores:
    if _supabase_enabled():
        try:
            return _supabase_fetch_top_scores(HIGH_SCORES_MAX_ENTRIES)
        except Exception as e:
            log_event(
                "high_scores_supabase_load_failed",
                error=f"{type(e).__name__}: {e}",
            )

    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        return HighScores(entries=_safe_parse_entries(data)).trimmed()
    except FileNotFoundError:
        return HighScores(entries=[])
    except Exception as e:  # pragma: no cover - best-effort persistence
        log_event("high_scores_load_failed", error=str(e))
        return HighScores(entries=[])


def record_high_score(path: Path, *, player_name: str, score: int) -> HighScores:
    sanitized_name = player_name.strip() or "Player"
    sanitized_score = max(0, int(score))

    if _supabase_enabled():
        try:
            _supabase_insert_score(player_name=sanitized_name, score=sanitized_score)
            return _supabase_fetch_top_scores(HIGH_SCORES_MAX_ENTRIES)
        except Exception as e:
            log_event(
                "high_scores_supabase_save_failed",
                error=f"{type(e).__name__}: {e}",
            )

    scores = load_high_scores(path)
    scores.entries.append({"name": sanitized_name, "score": sanitized_score})
    scores.trimmed()

    try:
        path.write_text(
            json.dumps(scores.entries, ensure_ascii=True, indent=2),
            encoding="utf-8",
        )
    except Exception as e:  # pragma: no cover - best-effort persistence
        log_event("high_scores_save_failed", error=str(e))

    return scores

