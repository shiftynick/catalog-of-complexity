"""HTTP fetcher with User-Agent, politeness rate-limit, and redirect support.

Stdlib-only (urllib). Resolvers inject a fetcher so tests don't touch the
network; this is the default implementation.
"""

from __future__ import annotations

import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from coc.sources.base import FetchError, NotFoundError, PaywallError

DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MIN_INTERVAL_SECONDS = 1.0

_contact_email = os.environ.get("COC_CONTACT_EMAIL", "admin@catalog-of-complexity.local")
_user_agent = f"catalog-of-complexity/0.1 (mailto:{_contact_email})"

# Per-host last-request timestamps for politeness throttling.
_last_request_lock = threading.Lock()
_last_request_at: dict[str, float] = {}


def _throttle(host: str, min_interval: float) -> None:
    now = time.monotonic()
    with _last_request_lock:
        last = _last_request_at.get(host, 0.0)
        wait = min_interval - (now - last)
        if wait > 0:
            time.sleep(wait)
        _last_request_at[host] = time.monotonic()


def http_get(
    url: str,
    headers: dict[str, str] | None = None,
    *,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    min_interval: float = DEFAULT_MIN_INTERVAL_SECONDS,
) -> tuple[int, dict[str, str], bytes]:
    """GET `url` with User-Agent + throttling; return (status, headers, body).

    Raises:
      NotFoundError — 404.
      PaywallError — 401/403 (metadata may be accessible, content isn't).
      FetchError — any other failure (timeout, DNS, 5xx).
    """
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc or "unknown"
    _throttle(host, min_interval)

    req_headers = {"User-Agent": _user_agent, "Accept": "*/*"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            body = resp.read()
            resp_headers = {k.lower(): v for k, v in resp.headers.items()}
            return status, resp_headers, body
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise NotFoundError(f"404 Not Found: {url}") from exc
        if exc.code in (401, 403):
            raise PaywallError(f"{exc.code} {exc.reason}: {url}") from exc
        raise FetchError(f"HTTP {exc.code} {exc.reason}: {url}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise FetchError(f"fetch failed: {url} ({exc})") from exc


def extension_for(content_type: str) -> str:
    """Pick a file extension from a Content-Type header value."""
    ct = content_type.split(";", 1)[0].strip().lower()
    mapping = {
        "application/pdf": "pdf",
        "application/json": "json",
        "application/xml": "xml",
        "text/xml": "xml",
        "application/atom+xml": "xml",
        "text/html": "html",
        "text/plain": "txt",
    }
    return mapping.get(ct, "bin")
