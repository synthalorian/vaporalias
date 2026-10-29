import io

import pytest

from vaporalias import cli
from vaporalias.meta import NAME

from fakes import FakeFetcher

BASE = ["--alias", "example_alias", "--name", "Jane Placeholder"]


def run(argv, fetcher=None):
    buf = io.StringIO()
    code = cli.main(argv, out=buf, fetcher=fetcher, environ={})
    return code, buf.getvalue()


def test_refuses_without_confirmation():
    code, out = run(BASE)
    assert code == 2
    assert "--i-am-this-person" in out
    assert "https://" not in out


def test_default_is_offline_dry_run(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network used in dry run")

    monkeypatch.setattr("urllib.request.urlopen", boom)
    code, out = run(BASE + ["--i-am-this-person"])
    assert code == 0
    assert "DRY RUN" in out
    assert "https://www.google.com/search?q=" in out
    assert "https://github.com/example_alias" in out
    assert "not-checked" in out
    assert "opt-out" in out.lower()


def test_live_path_with_fake_reports_link():
    fake = FakeFetcher({"https://github.com/example_alias": (200, "Jane Placeholder")})
    code, out = run(BASE + ["--i-am-this-person", "--live"], fetcher=fake)
    assert code == 1
    assert "found+name" in out
    assert "1 profile(s)" in out


def test_live_path_with_fake_clean():
    code, out = run(BASE + ["--i-am-this-person", "--live"], fetcher=FakeFetcher())
    assert code == 0
    assert "not-found" in out


def test_bad_alias_rejected():
    code, out = run(["--alias", "a b", "--name", "Jane Placeholder", "--i-am-this-person"])
    assert code == 2
    assert "error" in out


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        cli.main(["--version"])
    assert exc.value.code == 0
    assert NAME in capsys.readouterr().out
