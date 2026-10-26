"""Tests for geohash.geocode() input validation (issue #5)"""

import pytest
from geohash.geohash import geocode, geohash, distance

def test_geocode_uppercase():
    assert geocode("9MTZM4") == geocode("9mtzm4")

def test_geocode_mixed_case():
    assert geocode("9mTzM4") == geocode("9mtzm4")

def test_geocode_uppercase_roundtrip():
    lat, lon = geocode("9MTZM4")
    assert geohash(lat, lon, 6) == "9mtzm4"

def test_distance_uppercase():
    assert distance("9MTZM4", "9mtzm4") == 0.0

@pytest.mark.parametrize("bad",["a","i","l","o","-",".", " "])
def test_geocode_invalid_character(bad):
    code = "9mtz" + bad + "4"
    with pytest.raises(ValueError, match=f"invalid geohash character {bad!r} at position 4"):
        geocode(code)

@pytest.mark.parametrize("bad",["A","I","L","O"])
def test_geocode_invalid_uppercase_character_named_as_given(bad):
    with pytest.raises(ValueError, match=f"invalid geohash character {bad!r}"):
        geocode("9mtz" + bad)

def test_geocode_empty():
    with pytest.raises(ValueError, match="empty"):
        geocode("")

def test_geocode_not_a_string():
    with pytest.raises(TypeError):
        geocode(None)

def test_invalid_code_not_cached():
    with pytest.raises(ValueError):
        geocode("9mtzma")
    with pytest.raises(ValueError):
        geocode("9mtzma")
