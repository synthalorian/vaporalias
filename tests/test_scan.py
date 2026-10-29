import pytest

from vaporalias import scan
from vaporalias.catalog import ProfileSite
from vaporalias.net import DryRunFetcher

from fakes import FakeFetcher

ALIAS = "example_alias"
NAME = "Jane Placeholder"


def test_validate_alias_rejects_junk():
    with pytest.raises(ValueError):
        scan.validate_alias("bad alias/../x")
    with pytest.raises(ValueError):
        scan.validate_alias("")
    assert scan.validate_alias("  example_alias ") == "example_alias"


def test_validate_name_normalizes_whitespace():
    assert scan.validate_name("  Jane   Placeholder ") == NAME
    with pytest.raises(ValueError):
        scan.validate_name("   ")


def test_search_urls_are_encoded_and_cover_engines():
    urls = scan.build_search_urls(ALIAS, NAME)
    engines = {e for e, _, _ in urls}
    assert {"Google", "Bing", "DuckDuckGo"} <= engines
    first = urls[0][2]
    assert "%22example_alias%22" in first
    assert "Jane+Placeholder" in first
    assert " " not in first


def test_mentions_name():
    assert scan.mentions_name("<h1>Jane Placeholder</h1>", NAME)
    assert scan.mentions_name("placeholder, jane", NAME)
    assert not scan.mentions_name("Jane Doeish only", NAME)


def test_dry_run_checks_nothing():
    findings = scan.check_profiles(ALIAS, NAME, DryRunFetcher())
    assert findings
    assert all(f.verdict == scan.NOT_CHECKED for f in findings)


def test_fake_fetcher_verdicts():
    sites = (
        ProfileSite("A", "https://a.invalid/{alias}"),
        ProfileSite("B", "https://b.invalid/{alias}"),
        ProfileSite("C", "https://c.invalid/{alias}"),
        ProfileSite("D", "https://d.invalid/{alias}"),
        ProfileSite("E", "https://e.invalid/{alias}"),
    )
    fake = FakeFetcher(
        {
            "https://a.invalid/example_alias": (200, "hello I am Jane Placeholder"),
            "https://b.invalid/example_alias": (200, "just a handle"),
            "https://c.invalid/example_alias": (404, ""),
            "https://d.invalid/example_alias": (None, ""),
            "https://e.invalid/example_alias": (429, ""),
        }
    )
    verdicts = [f.verdict for f in scan.check_profiles(ALIAS, NAME, fake, sites)]
    assert verdicts == [scan.LINKED, scan.FOUND, scan.NOT_FOUND, scan.ERROR, scan.ERROR]
    assert len(fake.calls) == 5
