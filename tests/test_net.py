"""LiveFetcher tests. The opener is fed by a fake handler: zero real network."""

import email.message
import io
import socket
import urllib.error
import urllib.request
import urllib.response

from vaporalias import net, scan

URL = "https://example.invalid/example_alias"


class FakeHTTPHandler(urllib.request.BaseHandler):
    """Answers http(s) requests from a script instead of the network."""

    handler_order = 100  # ahead of the stock HTTP(S)Handler

    def __init__(self, responses):
        self.responses = dict(responses)  # url -> (status, headers, body) or exception
        self.requests = []

    def _open(self, req):
        self.requests.append(req)
        answer = self.responses[req.full_url]
        if isinstance(answer, BaseException):
            raise answer
        status, headers, body = answer
        msg = email.message.Message()
        for k, v in headers.items():
            msg[k] = v
        resp = urllib.response.addinfourl(io.BytesIO(body), msg, req.full_url, status)
        resp.msg = "scripted"
        return resp

    http_open = _open
    https_open = _open


def fetcher(responses, **kw):
    handler = FakeHTTPHandler(responses)
    return net.LiveFetcher(opener=net.build_opener(handler), **kw), handler


def test_success_returns_decoded_body():
    f, h = fetcher({URL: (200, {"Content-Type": "text/html; charset=latin-1"}, "Jos\xe9".encode("latin-1"))})
    res = f.fetch(URL)
    assert res.status == 200
    assert res.body == "Jos\xe9"
    assert res.error == ""
    assert h.requests[0].get_header("User-agent").endswith("(self-scan)")


def test_success_body_capped_at_max_bytes():
    f, _ = fetcher({URL: (200, {}, b"x" * 100)}, max_bytes=10)
    assert f.fetch(URL).body == "x" * 10


def test_redirect_is_refused_and_reported():
    target = "https://example.invalid/login?next=/example_alias"
    f, h = fetcher({URL: (302, {"Location": target}, b"")})
    res = f.fetch(URL)
    assert res.status == 302
    assert res.location == target
    assert res.error == "redirect not followed"
    assert [r.full_url for r in h.requests] == [URL]  # target was never requested


def test_every_redirect_code_is_refused():
    for code in net.REDIRECT_CODES:
        f, h = fetcher({URL: (code, {"Location": "/elsewhere"}, b"")})
        res = f.fetch(URL)
        assert (res.status, res.location) == (code, "/elsewhere")
        assert len(h.requests) == 1


def test_redirect_verdict_in_scan():
    class OneSite:
        name = "Example"
        url_template = URL.rsplit("/", 1)[0] + "/{alias}"

    f, _ = fetcher({URL: (301, {"Location": "https://example.invalid/"}, b"")})
    [finding] = scan.check_profiles("example_alias", "Jane Placeholder", f, sites=[OneSite])
    assert finding.verdict == scan.ERROR
    assert "301 redirect not followed -> https://example.invalid/" in finding.detail


def test_default_opener_disables_redirects():
    handlers = net.LiveFetcher().opener.handlers
    redirect = [x for x in handlers if isinstance(x, urllib.request.HTTPRedirectHandler)]
    assert len(redirect) == 1 and isinstance(redirect[0], net.NoRedirectHandler)


def test_http_error_status():
    f, _ = fetcher({URL: (404, {}, b"gone")})
    res = f.fetch(URL)
    assert res.status == 404
    assert res.body == "" and res.location == ""


def test_http_server_error_status():
    f, _ = fetcher({URL: (503, {}, b"")})
    assert f.fetch(URL).status == 503


def test_timeout_raw():
    f, _ = fetcher({URL: socket.timeout("timed out")}, timeout=2.5)
    res = f.fetch(URL)
    assert res.status is None
    assert res.error == "timed out after 2.5s"


def test_timeout_wrapped_in_urlerror():
    f, _ = fetcher({URL: urllib.error.URLError(TimeoutError("timed out"))}, timeout=3)
    res = f.fetch(URL)
    assert res.status is None
    assert res.error == "timed out after 3s"


def test_connection_error():
    f, _ = fetcher({URL: urllib.error.URLError(ConnectionRefusedError("refused"))})
    res = f.fetch(URL)
    assert res.status is None
    assert "refused" in res.error


def test_live_fetcher_via_patched_urllib_opener(monkeypatch):
    """Patching urllib's opener factory also keeps LiveFetcher off the network."""
    handler = FakeHTTPHandler({URL: (200, {}, b"hello")})
    real_build = urllib.request.build_opener
    monkeypatch.setattr(urllib.request, "build_opener", lambda *hs: real_build(*hs, handler))
    assert net.LiveFetcher().fetch(URL).body == "hello"
