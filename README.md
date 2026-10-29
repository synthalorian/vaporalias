<p align="center"><img src=".github/assets/vaporalias-banner.png" alt="vaporalias banner" width="100%"></p>

# Vaporalias

> **Jack into the grid. See what it knows about you. Pull the plug on the leaks.**

```
  ░▒▓ Vaporalias ▓▒░   privacy self-scanner // cyan + magenta, 1986 forever
```

You've got a handle. You've got a real name. Somewhere out there in the neon
sprawl, a forgotten profile page or a data broker is quietly wiring the two
together. **Vaporalias** runs a sweep on *you*. It builds the search-engine
queries an adversary would try, checks the profile sites where your alias
might sit next to your name, and hands you the opt-out links to go dark.

**SELF-SCAN ONLY.** Vaporalias is for checking your *own* exposure. It won't run
without `--i-am-this-person`. Read [ETHICS.md](ETHICS.md) before you ride.

## Features

- 🔎 **Query builder**: quoted alias + name searches for Google, Bing and DuckDuckGo, printed as ready-to-click URLs.
- 🕹️ **Profile sweep**: GitHub, GitLab, Reddit, Keybase, Mastodon, Twitch, Steam, Medium, Dev.to, Hacker News, PyPI, npm.
- 🧲 **Link detection**: in `--live` mode, flags any profile page that shows your real name next to your alias. Redirects are never followed.
- 🚪 **Exit ramps**: removal links for search engines and data brokers.
- 🌃 **Offline by default**: the default dry-run mode sends no packets. `--live` does send requests (see below).
- 📼 **Stdlib only**: Python ≥ 3.10, zero runtime deps.

## Usage

```sh
# Dry run (default): no network, prints every URL for you to check yourself
python3 -m vaporalias --alias example_alias --name "Jane Placeholder" --i-am-this-person

# Live: actually requests each profile page for your alias
python3 -m vaporalias --alias example_alias --name "Jane Placeholder" --i-am-this-person --live
```

Run it from a source checkout with `PYTHONPATH=src python3 -m vaporalias ...`, or
`pip install .` to get the `vaporalias` command.

| Flag | What it does |
| --- | --- |
| `--alias` | Your handle (letters, digits, `.`, `_`, `-`; max 64). |
| `--name` | Your real name. |
| `--i-am-this-person` | **Required.** Confirms both are yours. |
| `--live` | Make real HTTP requests to profile sites (otherwise dry run). Your alias leaves your machine in these requests. |
| `--timeout SECONDS` | Per-request timeout in live mode (default 10). |
| `--version` | Print the version. |

**Profile verdicts:** `not-checked` (dry run), `not-found` (404/410),
`found` (profile exists, name not seen), `found+name` (**your alias and real
name are on the same page**), `error` (network error, timeout, a refused
redirect, or any other HTTP status). Live mode never follows redirects: a
3xx is reported as `error` with the status and its `Location` target, so you
can open it yourself if you want to.

**Exit codes:** `0` clean / dry run, `1` at least one `found+name`,
`2` usage error or missing confirmation.

**Color:** cyan/magenta on black when stdout is a TTY. Set `NO_COLOR` to any
non-empty value (per [no-color.org](https://no-color.org); an empty `NO_COLOR`
is ignored) or pipe the output to get plain text.

> Removal URLs come from each provider's public opt-out flow, and those flows
> change. If a link 404s, search the provider's site for "opt out".

## Development

```sh
python3 -m pytest -q          # works from repo root, no install needed
```

Layout:

```
src/vaporalias/
  meta.py      # NAME / VERSION: the single source of the project name
  cli.py       # argparse entry point
  scan.py      # query building, profile checks, name matching
  catalog.py   # search engines, profile sites, removal links
  net.py       # Fetcher interface: DryRunFetcher (default), LiveFetcher (urllib, no redirects)
  color.py     # the only place ANSI colors live; honors NO_COLOR and TTY detection
tests/         # pytest; fakes + a socket guard, never touches the network
```

To add a profile site, add a `ProfileSite` to `catalog.py`. To change how the
network works (proxy, rate limit, caching), implement the `Fetcher` protocol in
`net.py` and pass it to `cli.main(fetcher=...)`.

Renaming the project? See [RENAME.md](RENAME.md).

## License

MIT. See [LICENSE](LICENSE). Stay neon, stay private. 🌆
