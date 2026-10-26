"""Shared test setup

`geohash` downloads nothing and does not use the `cache` package, so there is
no `GEOHASH_CACHEDIR` setting. The only shared state is the bounded
in-memory memo of decoded codes kept by `geocode()`; it is cleared before
each test so tests do not depend on the order they run in.
"""

import pytest

from geohash import _core

@pytest.fixture(autouse=True)
def _clear_geocode_memo():
    _core._geocode.cache_clear() # pylint: disable=protected-access
    yield
