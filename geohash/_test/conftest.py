"""Shared test setup

`geohash` downloads nothing and does not use the `cache` package, so there is
no `GEOHASH_CACHEDIR` setting. The only shared state is the in-memory
memo of decoded codes kept by `geocode()`; it is cleared before each test so
tests do not depend on the order they run in.
"""

import importlib

import pytest

# `geohash.geohash` is shadowed by the re-exported `geohash()` function, so
# fetch the module itself
_module = importlib.import_module("geohash.geohash")

@pytest.fixture(autouse=True)
def _clear_geocode_memo():
    _module._cache.clear() # pylint: disable=protected-access
    yield
