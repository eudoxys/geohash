"""Tests for geohash.nearest()"""

import math
from geohash._core import geohash, distance, nearest

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

# Input validation (issue #6)

import pytest

@pytest.mark.parametrize("lat,lon",[
    (90,180),(-90,-180),(0,0),(32.225646,-115.43884),(45,10**0),
    ])
def test_geohash_valid_coordinates(lat,lon):
    assert len(geohash(lat,lon)) == 6

def test_geohash_edges():
    assert geohash(90,180) == "zzzzzz"
    assert geohash(-90,-180) == "000000"

@pytest.mark.parametrize("lat,lon",[
    (95,200),(90.0001,0),(-90.0001,0),(0,180.0001),(0,-180.0001),
    (float("nan"),0),(0,float("nan")),(float("inf"),0),(0,float("-inf")),
    ])
def test_geohash_invalid_coordinates(lat,lon):
    with pytest.raises(ValueError,match="outside"):
        geohash(lat,lon)

@pytest.mark.parametrize("lat,lon",[("32.2",0),(0,None),(True,0),(0,[1])])
def test_geohash_coordinate_type(lat,lon):
    with pytest.raises(TypeError):
        geohash(lat,lon)

@pytest.mark.parametrize("precision",[0,-1])
def test_geohash_invalid_precision(precision):
    with pytest.raises(ValueError,match="precision must be positive"):
        geohash(32.2,-115.4,precision)

@pytest.mark.parametrize("precision",[6.0,"6",None,True])
def test_geohash_precision_type(precision):
    with pytest.raises(TypeError):
        geohash(32.2,-115.4,precision)

def test_geohash_precision_one():
    assert geohash(32.225646,-115.43884,1) == "9"
