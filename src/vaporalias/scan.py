"""Core logic: build queries, probe profile sites, decide what might leak."""

from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .catalog import PROFILE_SITES, SEARCH_ENGINES, ProfileSite, SearchEngine
from .net import Fetcher

ALIAS_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def validate_alias(alias: str) -> str:
    alias = alias.strip()
    if not ALIAS_RE.match(alias):
        raise ValueError("alias must be 1-64 chars of letters, digits, '.', '_' or '-'")
    return alias


def validate_name(name: str) -> str:
    name = " ".join(name.split())
    if not name:
        raise ValueError("real name must not be empty")
    return name


def build_query_strings(alias: str, real_name: str) -> List[str]:
    """Search phrasings that tend to surface alias <-> name links."""
    return [
        f'"{alias}" "{real_name}"',
        f'"{alias}"',
        f'"{real_name}" "{alias}" profile',
    ]


def build_search_urls(
    alias: str, real_name: str, engines: Sequence[SearchEngine] = SEARCH_ENGINES
) -> List[tuple]:
    out = []
    for q in build_query_strings(alias, real_name):
        for eng in engines:
            out.append((eng.name, q, eng.url_template.format(q=urllib.parse.quote_plus(q))))
    return out


def profile_urls(alias: str, sites: Sequence[ProfileSite] = PROFILE_SITES) -> List[tuple]:
    safe = urllib.parse.quote(alias, safe="")
    return [(s.name, s.url_template.format(alias=safe)) for s in sites]


def name_tokens(real_name: str) -> List[str]:
    return [t.lower() for t in real_name.split() if len(t) >= 2]


def mentions_name(body: str, real_name: str) -> bool:
    """True if the full name, or every name token, appears in the body."""
    low = body.lower()
    if real_name.lower() in low:
        return True
    tokens = name_tokens(real_name)
    return bool(tokens) and all(re.search(rf"\b{re.escape(t)}\b", low) for t in tokens)


# Verdicts for a profile probe.
NOT_CHECKED = "not-checked"
NOT_FOUND = "not-found"
FOUND = "found"
LINKED = "found+name"
ERROR = "error"


@dataclass(frozen=True)
class ProfileFinding:
    site: str
    url: str
    verdict: str
    detail: str = ""


def check_profiles(
    alias: str, real_name: str, fetcher: Fetcher, sites: Iterable[ProfileSite] = PROFILE_SITES
) -> List[ProfileFinding]:
    findings = []
    for site, url in profile_urls(alias, tuple(sites)):
        res = fetcher.fetch(url)
        if not fetcher.live:
            findings.append(ProfileFinding(site, url, NOT_CHECKED))
        elif res.status is None:
            findings.append(ProfileFinding(site, url, ERROR, res.error))
        elif res.status == 200:
            if mentions_name(res.body, real_name):
                findings.append(ProfileFinding(site, url, LINKED, "real name appears on page"))
            else:
                findings.append(ProfileFinding(site, url, FOUND, "profile exists"))
        elif res.status in (404, 410):
            findings.append(ProfileFinding(site, url, NOT_FOUND))
        else:
            findings.append(ProfileFinding(site, url, ERROR, f"HTTP {res.status}"))
    return findings
