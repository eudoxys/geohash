"""Tests for geohash.nearest()"""

import math
from geohash.geohash import geohash, distance, nearest

def test_nearest_uses_great_circle_distance():
    # At 60N a degree of longitude is about half a degree of latitude, so the
    # point 1.5 deg east is nearer (~83 km) than the point 1 deg north (~111 km)
    # even though it is farther in squared degrees (issue #1)
    gh = geohash(60.0, 0.0, 9)
    east = geohash(60.0, 1.5, 9)
    north = geohash(61.0, 0.0, 9)
    assert distance(gh, east) < distance(gh, north)
    assert nearest(gh, [north, east]) == east
    assert nearest(gh, [east, north]) == east

def test_nearest_withdist():
    gh = geohash(60.0, 0.0, 9)
    east = geohash(60.0, 1.5, 9)
    north = geohash(61.0, 0.0, 9)
    best, dist = nearest(gh, [north, east], withdist=True)
    assert best == east
    assert dist == distance(gh, east)

def test_nearest_empty():
    assert nearest("9mtzm4", []) is None
    best, dist = nearest("9mtzm4", [], withdist=True)
    assert best is None and math.isnan(dist)
