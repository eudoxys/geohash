"""Tests for distance units and the Earth radius (issue #7)"""

import math

import pytest

from geohash._core import (haversine_distance, distance, geocode,
    nearest, nearest_latlon, EARTH_RADIUS_KM)

def test_radius_is_mean_earth_radius_km():
    assert EARTH_RADIUS_KM == 6371.0

def test_haversine_known_distance_km():
    # Rosetta Code haversine reference: BNA (36.12, -86.67) to
    # LAX (33.94, -118.40) is 2887.25995 km on a sphere of radius 6372.8 km
    d = haversine_distance(36.12, -86.67, 33.94, -118.40)
    assert d * 6372.8 / EARTH_RADIUS_KM == pytest.approx(2887.25995, abs=1e-4)

def test_haversine_quarter_meridian_km():
    # equator to pole is a quarter great circle: pi/2 * R, about 10008 km
    d = haversine_distance(0.0, 0.0, 90.0, 0.0)
    assert d == pytest.approx(math.pi / 2 * EARTH_RADIUS_KM)
    assert d == pytest.approx(10007.54, abs=0.01)

def test_haversine_one_degree_km():
    # one degree of arc along the equator is about 111.195 km
    assert haversine_distance(0.0, 0.0, 0.0, 1.0) == pytest.approx(111.195, abs=1e-3)

def test_distance_matches_haversine_km():
    # San Francisco to New York, about 4130 km
    a, b = "9q8yyk", "dr5reg"
    d = distance(a, b)
    assert d == pytest.approx(haversine_distance(*geocode(a), *geocode(b)))
    assert 4100 < d < 4160

def test_nearest_withdist_km():
    best, dist = nearest("9q8yyk", ["dr5reg", "9q8yyk"], withdist=True)
    assert best == "9q8yyk" and dist == 0.0
    _, dist = nearest("9q8yyk", ["dr5reg"], withdist=True)
    assert 4100 < dist < 4160

def test_nearest_latlon_km():
    ix, ll, dist = nearest_latlon((0.0, 0.0), [(0.0, 2.0), (0.0, 1.0)])
    assert ix == 1 and ll == (0.0, 1.0)
    assert dist == pytest.approx(111.195, abs=1e-3)
