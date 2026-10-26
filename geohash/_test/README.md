Testing
-------

From the repository root:

	python3 -m venv .venv
	. .venv/bin/activate
	python3 -m pip install --upgrade pip
	pip install . pytest
	pytest

Use `pip install -e .` instead of `pip install .` while editing the package.
CI uses the non-editable install so that it tests what users get.

All tests are fast and self-contained: no credentials, no network, no
downloaded data, and no environment variables. The whole suite runs in under
a second, so there is only one tier and no `network` marker.

`conftest.py` clears the in-memory memo of decoded codes kept by `geocode()`
before each test, so tests do not depend on the order they run in.

test_roundtrip.py
-----------------

Encode/decode round trips at precisions 1 to 12 for several points; known
reference vectors (`9mtzm4`, `ezs42`, `u4pruydqqvj`); the encoded point lies
inside the decoded cell; cell sizes per precision; code prefixes are the
enclosing cells; uppercase codes; `nearest2()` on an empty list and on entries
with extra fields.

	pytest geohash/_test/test_roundtrip.py

test_conformance.py
-------------------

Conformance to CTA-5009-A, which adopts the Wikipedia "Geohash" technical
description: the alphabet and 5-bit values, longitude/latitude bit
interleaving, interval halving, decoding to the cell center (checked against
an independent bit-level decoder on random codes), the `ezs42` and
`u4pruydqqvj` worked examples, and the cell-size table.

	pytest geohash/_test/test_conformance.py

test_geohash.py
---------------

`geohash()` encoding: valid and edge coordinates, out-of-range, NaN and
infinite coordinates (`ValueError`), wrong argument types (`TypeError`),
precision checks; `nearest()` uses great-circle distance, with and without
`withdist`, and on an empty list.

	pytest geohash/_test/test_geohash.py

test_decode.py
--------------

`geocode()` input handling: uppercase and mixed-case codes, characters outside
the geohash alphabet, empty and non-string codes, and that invalid codes are
not memoized.

	pytest geohash/_test/test_decode.py

test_distance.py
----------------

Distances in km: `haversine_distance()` against known distances, and
`distance()`, `nearest()` and `nearest2()` against `haversine_distance()`.

	pytest geohash/_test/test_distance.py

test_cli.py
-----------

The `geohash` command via `main()`: conversions, options and their forms,
exit codes (0 ok, 1 syntax error, 9 exception), `--debug`, `--warning`,
`--help`, and LAT,LON argument validation.

	pytest geohash/_test/test_cli.py

test_docs.py
------------

Runs the `>>>` examples in the docstrings of `geohash`, `geohash.geohash`
and `geohash.cli` with `doctest`, so the documented output stays real.

	pytest geohash/_test/test_docs.py
