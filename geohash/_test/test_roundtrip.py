"""Tests for encode/decode round trips and reference vectors (issue #9)"""

import math

import pytest

from geohash.geohash import geohash, geocode, nearest2, _decode

# (code, latitude, longitude) of known cells; the point is inside the cell
REFERENCE = [
    ("9mtzm4", 32.225646, -115.43884), # README example
    ("ezs42", 42.6, -5.6), # Wikipedia "Geohash" article
    ("u4pruydqqvj", 57.64911, 10.40744), # Wikipedia "Geohash" article
    ]

POINTS = [
    (32.225646, -115.43884), (42.6, -5.6), (57.64911, 10.40744),
    (0.0, 0.0), (-33.8688, 151.2093), (64.1466, -21.9426), (-54.8019, -68.3030),
    ]

@pytest.mark.parametrize("code,lat,lon",REFERENCE)
def test_reference_encode(code,lat,lon):
    assert geohash(lat,lon,len(code)) == code

@pytest.mark.parametrize("code,lat,lon",REFERENCE)
def test_reference_decode(code,lat,lon):
    clat,clon,lat_err,lon_err = _decode(code)
    assert abs(clat - lat) <= lat_err
    assert abs(clon - lon) <= lon_err

def test_reference_decode_exact():
    assert geocode("9mtzm4") == (32.22564697265625, -115.4388427734375)

@pytest.mark.parametrize("precision",[1,3,6,9,12])
@pytest.mark.parametrize("lat,lon",POINTS)
def test_roundtrip_code(lat,lon,precision):
    # decoding a code and re-encoding its center gives the same code
    code = geohash(lat,lon,precision)
    assert len(code) == precision
    assert geohash(*geocode(code),precision) == code

@pytest.mark.parametrize("precision",[1,3,6,9,12])
@pytest.mark.parametrize("lat,lon",POINTS)
def test_point_inside_cell(lat,lon,precision):
    # the encoded point lies inside the decoded cell
    clat,clon,lat_err,lon_err = _decode(geohash(lat,lon,precision))
    assert abs(clat - lat) <= lat_err
    assert abs(clon - lon) <= lon_err

@pytest.mark.parametrize("precision",[1,2,5,6,11])
def test_cell_size(precision):
    # each character adds 5 bits, alternating longitude first
    _,_,lat_err,lon_err = _decode("9"*precision)
    bits = 5 * precision
    assert lat_err == 90 / 2**(bits // 2)
    assert lon_err == 180 / 2**((bits + 1) // 2)

def test_prefix_contains_longer_code():
    # truncating a code gives the enclosing cell
    code = geohash(32.225646,-115.43884,12)
    for n in range(1,12):
        assert geohash(32.225646,-115.43884,n) == code[:n]

def test_uppercase_roundtrip():
    code = geohash(42.6,-5.6,5)
    assert geocode(code.upper()) == geocode(code)

def test_nearest2_empty():
    ix,ll,dist = nearest2((0.0,0.0),[])
    assert (ix,ll) == (0,None) and math.isinf(dist)

def test_nearest2_extra_fields():
    # entries may carry fields beyond lat,lon; the whole entry is returned
    entries = [(10.0,10.0,"far"),(0.0,0.5,"near")]
    assert nearest2((0.0,0.0),entries)[:2] == (1,(0.0,0.5,"near"))
