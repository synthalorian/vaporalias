# Renaming the project

The project is named **Vaporalias** (display name in prose) with the lowercase
`vaporalias` as the package, import path and CLI command. All runtime output
(CLI `prog`, banner, `--version`, HTTP User-Agent) reads it from **one constant**:

- `src/vaporalias/meta.py`: `NAME = "vaporalias"`

Python packaging, import paths and prose can't import a constant, so they
also contain the name. Here is every place, checked with
`grep -rni vaporalias --exclude-dir=.git .` and `find . -iname '*vaporalias*'`:

## Code / config

| Where | What |
| --- | --- |
| `src/vaporalias/` | package **directory** name (`git mv src/vaporalias src/<newname>`) |
| `src/vaporalias/meta.py` | `NAME = "vaporalias"`: the single runtime constant |
| `pyproject.toml` | `[project] name = "vaporalias"` |
| `pyproject.toml` | `[project.scripts] vaporalias = "vaporalias.cli:main"` (command name **and** module path) |
| `.github/workflows/ci.yml` | smoke-test step: `python -m vaporalias ...` |
| `tests/fakes.py` | `from vaporalias.net import ...` |
| `tests/test_cli.py` | `from vaporalias import cli`, `from vaporalias.meta import NAME` |
| `tests/test_color.py` | `from vaporalias.cli ...`, `from vaporalias.color ...` |
| `tests/test_scan.py` | `from vaporalias import scan`, `from vaporalias.catalog ...`, `from vaporalias.net ...` |

## Docs

| Where | What |
| --- | --- |
| `README.md` | title, ASCII banner, pitch paragraph, SELF-SCAN notice (display name `Vaporalias`), usage commands (`python3 -m vaporalias`), install note, layout tree (`src/vaporalias/`) |
| `ETHICS.md` | first paragraph (display name `Vaporalias`) |
| `RENAME.md` | this file |

## Not affected

`LICENSE`, `conftest.py`, `.gitignore`, and the other modules
(`cli.py`, `scan.py`, `catalog.py`, `net.py`, `color.py`, `__init__.py`,
`__main__.py`) don't contain the name. They use relative imports or `NAME`.

## One-shot rename (GNU sed)

```sh
NEW=newname          # lowercase: package / command
DISPLAY=Newname      # capitalized: prose
git mv src/vaporalias "src/$NEW"
grep -rl Vaporalias --exclude-dir=.git . | xargs sed -i "s/Vaporalias/$DISPLAY/g"
grep -rl vaporalias --exclude-dir=.git . | xargs sed -i "s/vaporalias/$NEW/g"
python3 -m pytest -q
grep -rni vaporalias --exclude-dir=.git .   # should print nothing
```
