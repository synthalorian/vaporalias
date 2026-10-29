"""Network layer, kept behind a tiny interface so it can be faked or disabled.

The default is DryRunFetcher, which never touches the network. LiveFetcher
uses urllib (stdlib) and is only constructed when the user passes --live.
LiveFetcher never follows HTTP redirects: a 3xx response is reported back as
the result (status + Location) instead of triggering a second request.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional, Protocol

from .meta import NAME, VERSION

REDIRECT_CODES = (301, 302, 303, 307, 308)


@dataclass(frozen=True)
class FetchResult:
    url: str
    status: Optional[int]  # None means "not fetched" (dry run) or transport error
    body: str = ""
    error: str = ""
    location: str = ""  # Location header of a refused redirect, if any


class Fetcher(Protocol):
    live: bool

    def fetch(self, url: str) -> FetchResult: ...


class DryRunFetcher:
    """Never makes a request. Returns an unfetched result for every URL."""

    live = False

    def fetch(self, url: str) -> FetchResult:
        return FetchResult(url=url, status=None)


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Refuses every redirect by raising HTTPError with the 3xx response."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)


def build_opener(*handlers: urllib.request.BaseHandler) -> urllib.request.OpenerDirector:
    """urllib opener with redirects disabled. Extra handlers are for tests."""
    return urllib.request.build_opener(NoRedirectHandler(), *handlers)


class LiveFetcher:
    """Real HTTP GET via urllib. Reads at most max_bytes of the body."""

    live = True

    def __init__(
        self,
        timeout: float = 10.0,
        max_bytes: int = 512_000,
        opener: Optional[urllib.request.OpenerDirector] = None,
    ):
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.opener = build_opener() if opener is None else opener

    def fetch(self, url: str) -> FetchResult:
        req = urllib.request.Request(url, headers={"User-Agent": f"{NAME}/{VERSION} (self-scan)"})
        try:
            with self.opener.open(req, timeout=self.timeout) as resp:
                raw = resp.read(self.max_bytes)
                charset = resp.headers.get_content_charset() or "utf-8"
                return FetchResult(url, resp.status, raw.decode(charset, errors="replace"))
        except urllib.error.HTTPError as exc:
            if getattr(exc, "fp", None) is not None:
                exc.fp.close()
            if exc.code in REDIRECT_CODES:
                location = (exc.headers.get("Location") or "") if exc.headers else ""
                return FetchResult(url, exc.code, error="redirect not followed", location=location)
            return FetchResult(url, exc.code)
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, TimeoutError):
                return FetchResult(url, None, error=f"timed out after {self.timeout:g}s")
            return FetchResult(url, None, error=str(exc.reason))
        except TimeoutError:
            return FetchResult(url, None, error=f"timed out after {self.timeout:g}s")
        except (OSError, ValueError) as exc:
            return FetchResult(url, None, error=str(exc))
