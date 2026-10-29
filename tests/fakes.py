"""Test doubles. No test in this suite touches the network."""

from vaporalias.net import FetchResult


class FakeFetcher:
    live = True

    def __init__(self, pages=None, default_status=404):
        self.pages = pages or {}  # url -> (status, body)
        self.default_status = default_status
        self.calls = []

    def fetch(self, url):
        self.calls.append(url)
        status, body = self.pages.get(url, (self.default_status, ""))
        if status is None:
            return FetchResult(url, None, error="boom")
        return FetchResult(url, status, body)


class TTYBuffer:
    """StringIO-alike that claims (or denies) being a terminal."""

    def __init__(self, tty):
        self._tty = tty
        self.parts = []

    def write(self, s):
        self.parts.append(s)
        return len(s)

    def flush(self):
        pass

    def isatty(self):
        return self._tty

    def getvalue(self):
        return "".join(self.parts)
