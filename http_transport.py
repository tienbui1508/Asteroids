from __future__ import annotations

import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _request_timeout_seconds() -> float:
    # Browser/WASM startup networking can be slower than native Python.
    return 15.0 if sys.platform == "emscripten" else 5.0


def _raise_with_http_body(e: HTTPError) -> None:
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


def _xhr_request(
    *,
    method: str,
    url: str,
    headers: dict[str, str],
    payload: str | None = None,
) -> str:
    from platform import window  # type: ignore

    xhr_ctor = getattr(window, "XMLHttpRequest", None)
    if xhr_ctor is None:
        raise RuntimeError("XMLHttpRequest is unavailable")

    xhr = None
    ctor_new = getattr(xhr_ctor, "new", None)
    if callable(ctor_new):
        try:
            xhr = ctor_new()
        except Exception:
            xhr = None
    if xhr is None:
        eval_fn = getattr(window, "eval", None)
        if callable(eval_fn):
            xhr = eval_fn("new XMLHttpRequest()")
    if xhr is None:
        raise RuntimeError("Failed to construct XMLHttpRequest")

    open_fn = getattr(xhr, "open", None)
    if not callable(open_fn):
        raise RuntimeError("XMLHttpRequest.open is unavailable")
    open_fn(method, url, False)

    set_header = getattr(xhr, "setRequestHeader", None)
    if not callable(set_header):
        raise RuntimeError("XMLHttpRequest.setRequestHeader is unavailable")
    for key, value in headers.items():
        set_header(key, value)

    send_fn = getattr(xhr, "send", None)
    if not callable(send_fn):
        raise RuntimeError("XMLHttpRequest.send is unavailable")
    if payload is None:
        send_fn()
    else:
        send_fn(payload)

    status = int(xhr.status)
    body = str(xhr.responseText or "")
    if status < 200 or status >= 300:
        raise RuntimeError(f"HTTP {status} body={body}")
    return body


def request_json(
    *,
    method: str,
    url: str,
    headers: dict[str, str],
    payload: object | None = None,
    retries: int = 3,
) -> object:
    """Make an HTTP request and parse the JSON response.

    - On desktop/native: uses urllib.
    - On pygbag/web (emscripten): uses browser XMLHttpRequest.
    """

    payload_text: str | None = None
    data: bytes | None = None
    if payload is not None:
        payload_text = json.dumps(payload)
        data = payload_text.encode("utf-8")

    if sys.platform == "emscripten":
        raw = _xhr_request(method=method, url=url, headers=headers, payload=payload_text)
        if raw == "":
            return []
        return json.loads(raw)

    req = Request(url, data=data, headers=headers, method=method)
    last_error: Exception | None = None
    for attempt in range(max(1, int(retries))):
        try:
            with urlopen(req, timeout=_request_timeout_seconds()) as resp:
                raw = resp.read().decode("utf-8")
            if raw == "":
                return []
            return json.loads(raw)
        except HTTPError as e:
            _raise_with_http_body(e)
        except URLError as e:
            last_error = e
            if attempt == retries - 1:
                raise
            time.sleep(0.25 * (attempt + 1))

    if last_error is not None:
        raise last_error
    raise RuntimeError("unreachable")

