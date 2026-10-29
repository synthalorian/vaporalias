"""Command-line entry point."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence, TextIO

from .catalog import REMOVAL_LINKS
from .color import Palette
from .meta import NAME, TAGLINE, VERSION
from .net import DryRunFetcher, Fetcher, LiveFetcher
from . import scan

CONFIRM_FLAG = "--i-am-this-person"

VERDICT_STYLE = {
    scan.LINKED: "magenta",
    scan.FOUND: "cyan",
    scan.ERROR: "dim",
    scan.NOT_FOUND: "dim",
    scan.NOT_CHECKED: "dim",
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog=NAME,
        description=f"{NAME}: {TAGLINE}. SELF-SCAN ONLY: scan yourself, nobody else.",
    )
    p.add_argument("--alias", required=True, help="your own online handle, e.g. example_alias")
    p.add_argument("--name", required=True, help='your own real name, e.g. "Jane Placeholder"')
    p.add_argument(
        CONFIRM_FLAG,
        dest="confirmed",
        action="store_true",
        help="required: confirm the alias and name are YOURS",
    )
    p.add_argument(
        "--live",
        action="store_true",
        help=(
            "actually request profile pages; this sends your alias to each site"
            " (default: offline dry run, prints URLs only, nothing leaves your machine)"
        ),
    )
    p.add_argument("--timeout", type=float, default=10.0, help="per-request timeout for --live (s)")
    p.add_argument("--version", action="version", version=f"{NAME} {VERSION}")
    return p


def main(
    argv: Optional[Sequence[str]] = None,
    out: Optional[TextIO] = None,
    fetcher: Optional[Fetcher] = None,
    environ=None,
) -> int:
    out = sys.stdout if out is None else out
    args = build_parser().parse_args(argv)
    c = Palette.for_stream(out, environ)

    def say(line: str = "") -> None:
        print(line, file=out)

    if not args.confirmed:
        say(c.magenta(f"refusing to run: pass {CONFIRM_FLAG} to confirm this is YOUR alias and name."))
        say(f"{NAME} is a self-scan tool only. See ETHICS.md.")
        return 2

    try:
        alias = scan.validate_alias(args.alias)
        real_name = scan.validate_name(args.name)
    except ValueError as exc:
        say(c.magenta(f"error: {exc}"))
        return 2

    if fetcher is None:
        fetcher = LiveFetcher(timeout=args.timeout) if args.live else DryRunFetcher()

    mode = "LIVE" if fetcher.live else "DRY RUN (offline)"
    say(c.title(f">>> {NAME} v{VERSION} // {TAGLINE}"))
    say(c.dim(f"mode: {mode}  alias: {alias}  name: {real_name}"))
    say()

    say(c.title("== search-engine queries =="))
    say(c.dim("open these yourself to see what the grid knows about you"))
    for engine, query, url in scan.build_search_urls(alias, real_name):
        say(f"  {c.cyan(engine.ljust(11))} {query}")
        say(f"    {url}")
    say()

    say(c.title("== profile sites =="))
    findings = scan.check_profiles(alias, real_name, fetcher)
    for f in findings:
        style = getattr(c, VERDICT_STYLE[f.verdict])
        detail = f"  ({f.detail})" if f.detail else ""
        say(f"  {style(f'[{f.verdict}]'.ljust(14))} {f.site.ljust(28)} {f.url}{detail}")
    linked = [f for f in findings if f.verdict == scan.LINKED]
    if fetcher.live:
        say()
        if linked:
            say(c.magenta(f"!! {len(linked)} profile(s) show your alias next to your real name."))
        else:
            say(c.cyan("no profile pages showed your alias next to your real name."))
    say()

    say(c.title("== removal + opt-out links =="))
    for kind, label in (("search", "search engines"), ("broker", "data brokers")):
        say(c.dim(f"  {label}:"))
        for link in REMOVAL_LINKS:
            if link.kind == kind:
                say(f"    {c.cyan(link.name)}: {link.url}")
    say()
    say(c.dim("stay neon, stay private."))
    return 1 if linked else 0
