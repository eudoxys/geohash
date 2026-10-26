# Correctness

- [x] `nearest()` uses great-circle distance (#1, #16; see `geohash.nearest`)
- [x] Invalid and uppercase geohash characters handled (#5, #20; see `geohash.geocode`)
- [x] Latitude, longitude, and precision validated (#6, #21; see `geohash.geohash`)
- [x] Distances in km with the mean Earth radius (#7, #22; see `geohash.EARTH_RADIUS_KM`)

- [x] Cite CTA-5009-A and test conformance (#12; see `geohash/_test/test_conformance.py`)

# API

- [x] Clean up the public API and module internals (#13; see `geohash.__all__` and `geohash/_test/test_api.py`)
- [ ] Expose cell bounds / decode error, and let the CLI format to the code's precision (#14)

# CLI

- [x] argparse CLI with `-p 8` / `-f FMT` forms and negative `LAT,LON` (#4, #19; see `geohash.cli`)
- [x] `--debug` works and the installed CLI handles exceptions (#3, #18; see `geohash.cli.main`)

# Packaging, tests, docs

- [x] README install URL and `epm install` (#2, #17; see `README.md`)
- [x] `pyproject.toml` meets Eudoxys packaging requirements (#8, #23)
- [x] pytest suite and `validate.yaml` CI (#9, #24; see `geohash/_test/`)
- [x] pdoc docs, `Makefile`, and `deploy-pages.yaml` (#10, #25)
- [x] `CLAUDE.md`, `MANIFEST.md` (+ `.github/check_manifest.py`), and `TODO.md` (#11)

# Release

- [ ] Release 26.10.0 per the eudoxys-package checklist (#15)
