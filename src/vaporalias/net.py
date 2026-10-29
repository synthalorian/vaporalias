"""Network layer, kept behind a tiny interface so it can be faked or disabled.

The default is DryRunFetcher, which never touches the network. LiveFetcher
uses urllib (stdlib) and is only constructed when the user passes --live.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional, Protocol

from .meta import NAME, VERSION


@dataclass(frozen=True)
class FetchResult:
    url: str
    status: Optional[int]  # None means "not fetched" (dry run) or transport error
    body: str = ""
    error: str = ""


class Fetcher(Protocol):
    live: bool

    def fetch(self, url: str) -> FetchResult: ...


class DryRunFetcher:
    """Never makes a request. Returns an unfetched result for every URL."""

    live = False

    def fetch(self, url: str) -> FetchResult:
        return FetchResult(url=url, status=None)


class LiveFetcher:
    """Real HTTP GET via urllib. Reads at most max_bytes of the body."""

    live = True

    def __init__(self, timeout: float = 10.0, max_bytes: int = 512_000):
        self.timeout = timeout
        self.max_bytes = max_bytes

    def fetch(self, url: str) -> FetchResult:  # pragma: no cover - live network
        req = urllib.request.Request(url, headers={"User-Agent": f"{NAME}/{VERSION} (self-scan)"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read(self.max_bytes)
                charset = resp.headers.get_content_charset() or "utf-8"
                return FetchResult(url, resp.status, raw.decode(charset, errors="replace"))
        except urllib.error.HTTPError as exc:
            return FetchResult(url, exc.code)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            return FetchResult(url, None, error=str(exc))
