# CLAUDE.md

Guidance for Claude when working in the `eudoxys/geohash` repository.
General Eudoxys package conventions are in the `eudoxys-package` skill; this
file records only what is specific to this package.

## What this is

`geohash` encodes latitude/longitude positions as geohash codes, decodes
codes to the latitude/longitude of their cell centers, and gives great-circle
distances (km) between codes and the nearest code or position in a list. It
is a pure-Python, alpha-stage package for Python >= 3.10 with **no
third-party dependencies**, a `geohash` CLI, and a small Python API.

- Docs site: https://www.eudoxys.com/geohash (pdoc from docstrings)
- Maintainer: David P. Chassin
- CLI entry point: `geohash` -> `geohash.cli:main`
- PyPI's `geohash` is an unrelated package; install from the `git+` URL.

## Where things are

- `MANIFEST.md`: map of every file, a task index, and what not to read.
  Read it first instead of listing folders.
- There is no `DESIGN.md`: the package is small enough that its
  specification lives in the package docstring (`geohash/__init__.py`,
  Description and "What is not promised"). Treat that docstring as the
  contract; change it deliberately, not as a side effect.
- `TODO.md`: roadmap, linked to GitHub issues.

No sibling Eudoxys dependencies; no `cache` package; nothing is downloaded.

## Core conventions

- Latitude and longitude are in degrees (north and east positive);
  distances are in km on a sphere of radius `EARTH_RADIUS_KM` (6371.0,
  mean Earth radius).
- Codes are returned lowercase and accepted in any case; the alphabet is
  `0123456789bcdefghjkmnpqrstuvwxyz`.
- Invalid input raises `ValueError` (bad characters, empty code, coordinates
  out of range or NaN, precision < 1) or `TypeError` (wrong argument type).
  Coordinates are never wrapped or clamped.
- A position on a cell boundary belongs to the cell to its south or west.
- The algorithm is CTA-5009-A's (the Wikipedia "Technical description");
  `_test/test_conformance.py` checks it against an independent bit-level
  decoder. Keep it passing when changing `geohash()` or `_decode()`.
- CLI: an argument containing a comma is `LAT,LON`; anything else is a
  `CODE`. Exit codes are 0 ok, 1 syntax error, 9 exception caught.

## Style

Compact house style: no spaces after commas in many call sites and
signatures (`def nearest(gh,ghlist,withdist=False)`), dashed-underline
docstring sections. Match the surrounding code; don't reformat lines you
aren't changing.

## Build, test, docs

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install --upgrade pip && pip install -e . pytest
pytest
make docs
python .github/check_manifest.py
```

Everything is fast (the whole suite runs in under a second), needs no
network or credentials, and has a single tier with no `network` marker. CI
(`validate.yaml`) runs pylint (informational) and pytest on Python 3.10 and
3.13 from a non-editable install. `test_docs.py` runs the `>>>` docstring
examples, so example output must stay exact.

## Known rough edges (don't "fix" silently; mention or ask)

- `from .geohash import geohash` in `__init__.py` shadows the
  `geohash.geohash` submodule with the function; the module is reached via
  `importlib.import_module("geohash.geohash")` (see `_test/conftest.py`).
  Tracked in #13.
- `distance2()` and `haversine_distance()` are public names but not
  re-exported; `nearest()` and `nearest2()` return different shapes, and
  `nearest2((lat,lon), [])` returns index `0` with `None`. Tracked in #13.
- `geocode()` memoizes every decoded code in the module-level `_cache` dict
  without bound (documented in "What is not promised"). Tracked in #13.
- `geocode()` discards the error margins `_decode()` computes, and the CLI
  prints full float precision by default. Tracked in #14.
- `cli.py` sets argparse's private `_negative_number_matcher` so negative
  `LAT,LON` arguments are positional; check it on new Python versions.
- Dead commented-out formatting code remains in `geocode()`.

## Working rules

- Don't commit `docs/` (pdoc output), `.venv/`, or build artifacts; there is
  no checked-in data.
- When a public signature, return value, or CLI option changes, update the
  module docstring example, the package docstring (Syntax, Description,
  "What is not promised"), and `README.md` in the same PR, and keep the
  doctest output exact.
- Update `MANIFEST.md` when adding, moving, or deleting files, and run
  `python .github/check_manifest.py`.
- Conventional small test case: `9mtzm4` <-> `32.225646,-115.43884`.
