"""Tests for the public API and module internals (issue #13)"""

import importlib.util
import inspect
import math

import geohash
from geohash import _core

PUBLIC = ["geohash", "geocode", "distance", "haversine_distance", "nearest",
    "nearest_latlon", "EARTH_RADIUS_KM", "GEOCODE_CACHE_SIZE", "main"]

def test_all_is_public_api():
    assert sorted(geohash.__all__) == sorted(PUBLIC)

def test_public_names_exported():
    for name in PUBLIC:
        assert hasattr(geohash, name), name

def test_geohash_attribute_is_function():
    # the package attribute is the function, and no submodule shares its name
    assert inspect.isfunction(geohash.geohash)
    assert geohash.geohash is _core.geohash
    assert importlib.util.find_spec("geohash.geohash") is None

def test_removed_names():
    for name in ("nearest2", "distance2"):
        assert not hasattr(geohash, name), name
        assert not hasattr(_core, name), name

def test_no_unbounded_memo():
    assert not hasattr(_core, "_cache")
    assert _core._geocode.cache_info().maxsize == geohash.GEOCODE_CACHE_SIZE # pylint: disable=protected-access

def test_geocode_memo_bounded():
    info = _core._geocode.cache_info # pylint: disable=protected-access
    for lat in range(-89, 90):
        for lon in range(-179, 180, 4):
            geohash.geocode(geohash.geohash(lat, lon, 8))
    assert info().currsize <= geohash.GEOCODE_CACHE_SIZE

def test_geocode_memo_normalizes_case():
    geohash.geocode("9mtzm4")
    geohash.geocode("9MTZM4")
    assert _core._geocode.cache_info().hits == 1 # pylint: disable=protected-access

def test_decodemap_is_module_constant():
    assert _core._DECODEMAP == {c:i for i,c in enumerate(_core._BASE32)} # pylint: disable=protected-access

def test_nearest_shapes():
    # nearest() returns a code; nearest_latlon() returns (index, entry, km)
    assert geohash.nearest("9q8yyk", ["dr5reg", "9q5ctr"]) == "9q5ctr"
    ix, entry, dist = geohash.nearest_latlon((0.0, 0.0), [(0.0, 2.0), (0.0, 1.0)])
    assert (ix, entry) == (1, (0.0, 1.0))
    assert dist == geohash.haversine_distance(0.0, 0.0, 0.0, 1.0)

def test_nearest_empty_shapes():
    assert geohash.nearest("9q8yyk", []) is None
    best, dist = geohash.nearest("9q8yyk", [], withdist=True)
    assert best is None and math.isnan(dist)
    ix, entry, dist = geohash.nearest_latlon((0.0, 0.0), [])
    assert ix is None and entry is None and math.isnan(dist)

def test_public_functions_annotated():
    for name in PUBLIC:
        obj = getattr(geohash, name)
        if inspect.isfunction(obj) and obj is not geohash.main:
            sig = inspect.signature(obj)
            assert sig.return_annotation is not inspect.Signature.empty, name
            for param in sig.parameters.values():
                assert param.annotation is not inspect.Parameter.empty, (name, param.name)
