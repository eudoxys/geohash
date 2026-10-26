# MANIFEST

Map of the `eudoxys/geohash` repository. Every tracked file is covered by
one row or glob below; check with `python .github/check_manifest.py`.
Update this file in the same PR that adds, moves, or deletes a file.

## Start here

1. `CLAUDE.md` — conventions, rough edges, and working rules
2. `geohash/__init__.py` — package docs (the specification) and public API
3. `geohash/geohash.py` — encoding, decoding, and distances
4. `geohash/cli.py` — the `geohash` command

## Task index

- Change encoding/decoding or distances: `geohash/geohash.py`; tests in `geohash/_test/test_roundtrip.py`, `test_geohash.py`, `test_decode.py`, `test_distance.py`
- Add or change a public function: `geohash/geohash.py` (docstring with example output); re-export in `geohash/__init__.py`; update the package docstring and `README.md`
- Add a CLI option: `geohash/cli.py`, `geohash/__init__.py` Syntax section, `README.md`; test in `geohash/_test/test_cli.py`
- Fix a docstring example: `geohash/_test/test_docs.py` runs them; output must match exactly
- Update docs: `make docs` (output in `docs/`, not committed)
- Release: `pyproject.toml` version; see the eudoxys-package skill checklist and the release issue

## Package

| Path | Purpose | Notes |
|---|---|---|
| `geohash/__init__.py` | package docs, re-exports, `__version__` | pdoc landing page; doctested by `_test/test_docs.py` |
| `geohash/geohash.py` | `geohash()`, `geocode()`, `distance()`, `distance2()`, `haversine_distance()`, `nearest()`, `nearest2()` | tested by `test_roundtrip.py`, `test_geohash.py`, `test_decode.py`, `test_distance.py` |
| `geohash/cli.py` | CLI `main()` | entry point `geohash`; tested by `_test/test_cli.py` |

## Tests

| Path | Purpose | Notes |
|---|---|---|
| `geohash/_test/README.md` | how to run tests, what each file checks | |
| `geohash/_test/conftest.py` | clears the `geocode()` memo before each test | no cache dir; nothing downloaded |
| `geohash/_test/test_*.py` | tests | all fast; no `network` marker |

## Repository

| Path | Purpose | Notes |
|---|---|---|
| `README.md` | user overview | examples must match real output |
| `CLAUDE.md` | assistant guidance | |
| `MANIFEST.md` | this file | |
| `CONTRIBUTING.md` | contributor guide | approved-issue rule |
| `TODO.md` | roadmap | links to issues |
| `COPYRIGHT.md` | copyright notice | |
| `LICENSE` | MIT | |
| `pyproject.toml` | packaging, pytest settings | version here |
| `requirements.txt` | dependencies | none (comment only) |
| `Makefile` | `make docs`, `make test` | |
| `.gitignore` | GitHub Python ignores + `docs/` | |
| `.gitattributes` | line-ending normalization | |
| `.github/workflows/validate.yaml` | CI: pylint + pytest on 3.10 and 3.13 | |
| `.github/workflows/deploy-pages.yaml` | CI: pdoc → GitHub Pages | |
| `.github/workflows/approved-issue.yaml` | closes new contributors' PRs without an approved issue | matches template |
| `.github/workflows/assign-issues.yaml` | assigns unassigned issues to the owner | matches template |
| `.github/check_manifest.py` | checks this file against `git ls-files` | |

## Don't read

`docs/` (generated), `.venv/`, `build/`, `*.egg-info/`, `.pytest_cache/`.
