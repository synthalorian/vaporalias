"""Static data: search engines, profile sites, and removal/opt-out pages.

URLs for third-party opt-out pages change over time; treat them as starting
points and verify on the site itself.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchEngine:
    name: str
    url_template: str  # contains {q}


@dataclass(frozen=True)
class ProfileSite:
    name: str
    url_template: str  # contains {alias}


@dataclass(frozen=True)
class RemovalLink:
    name: str
    url: str
    kind: str  # "search" or "broker"


SEARCH_ENGINES = (
    SearchEngine("Google", "https://www.google.com/search?q={q}"),
    SearchEngine("Bing", "https://www.bing.com/search?q={q}"),
    SearchEngine("DuckDuckGo", "https://duckduckgo.com/html/?q={q}"),
)

PROFILE_SITES = (
    ProfileSite("GitHub", "https://github.com/{alias}"),
    ProfileSite("GitLab", "https://gitlab.com/{alias}"),
    ProfileSite("Reddit", "https://www.reddit.com/user/{alias}"),
    ProfileSite("Keybase", "https://keybase.io/{alias}"),
    ProfileSite("Mastodon (mastodon.social)", "https://mastodon.social/@{alias}"),
    ProfileSite("Twitch", "https://www.twitch.tv/{alias}"),
    ProfileSite("Steam", "https://steamcommunity.com/id/{alias}"),
    ProfileSite("Medium", "https://medium.com/@{alias}"),
    ProfileSite("Dev.to", "https://dev.to/{alias}"),
    ProfileSite("Hacker News", "https://news.ycombinator.com/user?id={alias}"),
    ProfileSite("PyPI", "https://pypi.org/user/{alias}/"),
    ProfileSite("npm", "https://www.npmjs.com/~{alias}"),
)

REMOVAL_LINKS = (
    RemovalLink("Google: Results about you", "https://myactivity.google.com/results-about-you", "search"),
    RemovalLink("Google: Remove outdated content", "https://search.google.com/search-console/remove-outdated-content", "search"),
    RemovalLink("Bing: Content removal", "https://www.bing.com/webmasters/tools/contentremoval", "search"),
    RemovalLink("Spokeo opt-out", "https://www.spokeo.com/optout", "broker"),
    RemovalLink("Whitepages suppression", "https://www.whitepages.com/suppression-requests", "broker"),
    RemovalLink("BeenVerified opt-out", "https://www.beenverified.com/app/optout/search", "broker"),
    RemovalLink("PeopleConnect (Intelius, TruthFinder, etc.)", "https://suppression.peopleconnect.us/login", "broker"),
    RemovalLink("PeopleFinders opt-out", "https://www.peoplefinders.com/opt-out", "broker"),
    RemovalLink("Radaris privacy control", "https://radaris.com/control/privacy", "broker"),
    RemovalLink("FastPeopleSearch removal", "https://www.fastpeoplesearch.com/removal", "broker"),
)
